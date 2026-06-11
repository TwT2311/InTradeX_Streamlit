# -*- coding: utf-8 -*-
"""
InTradeX - Strategic Sourcing & Export Intelligence Platform
Rewritten entirely in Python/Streamlit as a modular full-stack application.
"""

import os
import datetime
import requests
import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

# Import separate business logics
from trade_engine import (
    PACKAGING_MASTER,
    COMMODITY_BUY_PRICES,
    HS_CODE_DATABASE,
    DOMESTIC_FREIGHT_COST_IDR,
    DESTINATION_PORT_PRESETS,
    COUNTRY_DUTY_PRESETS,
    MARKET_ADVISOR_BENCHMARKS,
    calculate_packaging,
    calculate_fob,
    calculate_cif,
    calculate_ddp,
    generate_price_trend_data
)

from document_generator import (
    generate_pdf_bytes,
    generate_docx_bytes,
    format_usd
)

# ── 1. PAGE INITIALIZATIONS & CONFIGS ──
st.set_page_config(
    page_title="InTradeX - Sourcing & Export Intelligence",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global custom CSS inject for Clean Minimalism styling & branding
st.markdown("""
<style>
    /* Styling adjustments */
    .stApp {
        background-color: #f8fafc;
    }
    .brand-title {
        color: #0c0a09;
        font-weight: 850;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
    }
    .brand-sub {
        font-size: 10px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: -5px;
        margin-bottom: 25px;
        font-weight: 650;
    }
    .metric-container {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        flex: 1;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .card-label {
        font-size: 10px;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .card-val {
        font-size: 24px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 4px;
        line-height: 1;
    }
    .blue-card {
        border-top: 3px solid #FF4B4B;
    }
    .amber-card {
        border-top: 3px solid #94a3b8;
    }
    .neutral-card {
        border-top: 3px solid #0f172a;
    }
    .emerald-card {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #e2e8f0 !important;
        border-left: 4px solid #FF4B4B !important;
        border-radius: 8px !important;
        padding: 20px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .compliance-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #FF4B4B;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    /* Clean stream tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        background-color: transparent;
        font-weight: 500;
        color: #64748b;
        border-radius: 4px;
    }
    .stTabs [aria-selected="true"] {
        color: #FF4B4B !important;
        font-weight: 600;
    }
    /* Simple A4 container outline styling */
    .a4-paper {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        padding: 32px;
        font-family: inherit;
        font-size: 11px;
        color: #1e293b;
        line-height: 1.4;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        max-width: 600px;
        margin: 0 auto;
    }
    .a4-header {
        background-color: #0f172a;
        color: #ffffff;
        padding: 16px;
        border-radius: 4px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# ── 2. EXCHANGE RATE INDICATIVE UPDATER ──
@st.cache_data(ttl=3600)
def fetch_indicative_exchange_rate():
    """Reads live exchange rates dynamically using open-api fallback"""
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD")
        if response.status_code == 200:
            data = response.json()
            if data and "rates" in data and "IDR" in data["rates"]:
                return int(round(data["rates"]["IDR"])), datetime.datetime.now()
    except Exception:
        pass
    return 16250, datetime.datetime.now()

live_rate, last_checked = fetch_indicative_exchange_rate()

# Initialize session state variables
if "is_unlocked" not in st.session_state:
    st.session_state["is_unlocked"] = False

if "sync_vol" not in st.session_state:
    st.session_state["sync_vol"] = 1000
if "sync_commodity" not in st.session_state:
    st.session_state["sync_commodity"] = "Cinnamon Cassia Whole"
if "sync_packaging" not in st.session_state:
    st.session_state["sync_packaging"] = "PP Woven Bag 25 Kg"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ── 3. SIDEBAR AND LANGUAGES ──
with st.sidebar:
    st.markdown('<h1 class="brand-title">InTrade<span style="color:#FF4B4B">X</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="brand-sub">EXPORT MANAGEMENT DESK</p>', unsafe_allow_html=True)
    
    # Language Matrix Selection
    selected_lang = st.selectbox("🌐 Language", ["English", "Bahasa Indonesia", "Deutsch", "Nederlands", "日本語", "한국어", "العربية"])
    
    st.write("---")
    
    # Premium Passcode Cryptography Unlock Box
    if not st.session_state["is_unlocked"]:
        st.markdown("**🔓 Premium Passcode**")
        st.info("Input private exporter passcode to activate professional CIF/DDP indices and formal document generation sheets.")
        passcode = st.text_input("Enter code", type="password", key="sidebar_passcode")
        if st.button("Authenticate Premium Key"):
            if passcode == "TwT2311_":
                st.session_state["is_unlocked"] = True
                st.success("Access Unlocked! Exporter Premium Granted.")
                st.rerun()
            else:
                st.error("Invalid passcode. Please verify.")
    else:
        st.markdown("🟢 **PREMIUM UNLOCKED**")
        st.success("Exporter level initialized.")
        if st.button("Lock Premium Content"):
            st.session_state["is_unlocked"] = False
            st.rerun()
            
    st.write("---")
    
    # Live indicatives box
    st.markdown(f"""
    <div style="background-color:#ffffff; color:#0f172a; border:1px solid #e2e8f0; padding:16px; border-radius:8px; font-family:monospace; font-size:11px; margin-top:10px;">
        <span style="font-weight:600; color:#64748b; font-family:sans-serif;">Live USD/IDR Exchange:</span><br/>
        <span style="font-size:18px; font-weight:800; color:#FF4B4B; display:inline-block; margin-top:4px; margin-bottom:4px;">IDR {live_rate:,.0f}</span><br/>
        <span style="font-size:9px; color:#94a3b8; font-family:sans-serif;">Checked: {last_checked.strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)


# ── 4. MAIN INTERACTIVE LAYOUT ──
# Dynamic Column split: Main calculators on Left, Persistent AI Advisor on Right
col_workspace, col_advisor = st.columns([2, 1], gap="medium")

with col_workspace:
    # Set main content tabs equivalent to tab-sourcing, tab-incoterms, tab-documents, tab-intelligence
    tab_sourcing, tab_incoterms, tab_docs, tab_intel = st.tabs([
        "📦 Sourcing & Packaging",
        "🚢 Incoterms",
        "📄 Documents",
        "🌐 Compliance & Tariffs"
    ])
    
    # ── TAB 1: SOURCING & PACKAGING ──
    with tab_sourcing:
        st.subheader("📦 Sourcing & Package Parameter Estimator")
        st.caption("Perform complete net weight assessments, unit requirements, and purchasing benchmark indexing.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            commodity_option = st.selectbox("Select Commodity", list(PACKAGING_MASTER.keys()), index=0)
        with c2:
            volume_kg = st.number_input("Target Net Weight Volume (Kg)", min_value=100.0, max_value=500000.0, value=100.0, step=100.0)
        with c3:
            pack_options = list(PACKAGING_MASTER[commodity_option].keys())
            packaging_option = st.selectbox("Packaging Specification Model", pack_options, index=0)
            
        # Packaging calculations output
        pack_res = calculate_packaging(commodity_option, volume_kg, packaging_option, live_rate)
        
        if "error" in pack_res:
            st.error(pack_res["error"])
        else:
            # Sourcing Metric Display
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-card blue-card">
                    <div class="card-label">Total Packages Needed</div>
                    <div class="card-val">{pack_res['totalUnitsNeeded']:,} <span style="font-size:12px; color:#FF4B4B;">{pack_res['packagingType']}s</span></div>
                    <div style="font-size:9.5px; color:#64748b; margin-top:4px;">At {pack_res['weightPerUnitKg']:.1f} Kg per unit loading</div>
                </div>
                <div class="metric-card neutral-card">
                    <div class="card-label">Net Sourced Cargo</div>
                    <div class="card-val">{pack_res['netWeightKg']:,} <span style="font-size:12px; color:#0f172a;">Kg</span></div>
                    <div style="font-size:9.5px; color:#64748b; margin-top:4px;">Target net payload booking</div>
                </div>
                <div class="metric-card amber-card">
                    <div class="card-label">Taksiran Berat Kotor (Gross)</div>
                    <div class="card-val">{pack_res['grossWeightKg']:,} <span style="font-size:12px; color:#94a3b8;">Kg</span></div>
                    <div style="font-size:9.5px; color:#94a3b8; margin-top:4px;">Includes {pack_res['grossWeightKg'] - pack_res['netWeightKg']:.1f} Kg overall tare</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Local Sourcing Cost breakdown vs indicative global FOB Index
            st.write("---")
            b_col_local, b_col_global = st.columns(2)
            
            with b_col_local:
                local_buy = COMMODITY_BUY_PRICES.get(commodity_option, 35000)
                local_buy_usd = local_buy / live_rate
                st.markdown(f"""
                <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #0f172a; padding: 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(15,23,42,0.05);">
                    <span style="font-size:10px; font-weight:bold; color:#64748b; text-transform:uppercase; letter-spacing:0.5px;">Indonesian Domestic Purchasing reference</span>
                    <h3 style="margin: 6px 0px; color:#0f172a; font-weight:800; font-size:20px;">IDR {local_buy:,.0f} / Kg</h3>
                    <p style="font-size:11px; color:#64748b; line-height:1.4; margin:0;">Equivalent to <b style="color:#0f172a;">{format_usd(local_buy_usd)}</b> / Kg at live rate. Sourced directly from local cooperative farming portals.</p>
                </div>
                """, unsafe_allow_html=True)
                
            with b_col_global:
                benchmark = MARKET_ADVISOR_BENCHMARKS.get(commodity_option, {"low": 2.0, "high": 4.0})
                st.markdown(f"""
                <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #FF4B4B; padding: 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(15,23,42,0.05);">
                    <span style="font-size:10px; font-weight:bold; color:#FF4B4B; text-transform:uppercase; letter-spacing:0.5px;">Indicative FOB Global Benchmark corridor</span>
                    <h3 style="margin: 6px 0px; color:#0f172a; font-weight:800; font-size:20px;">{format_usd(benchmark['low'])} - {format_usd(benchmark['high'])} / Kg</h3>
                    <p style="font-size:11px; color:#64748b; line-height:1.4; margin:0;">Trade reference prices based on actual shipping logs curated by <b style="color:#0f172a;">{benchmark['source']}</b>.</p>
                </div>
                """, unsafe_allow_html=True)
                
            # Line Chart Visualization of prices using generated trend lines
            st.markdown("<p style='font-size:12px; font-weight:bold; color:#334155; margin-top:14px;'>30-Day Crop Pricing Analytics & Spread Deviation (USD/Kg)</p>", unsafe_allow_html=True)
            chart_raw = generate_price_trend_data(commodity_option, live_rate)
            df_chart = pd.DataFrame(chart_raw).set_index("Date")
            st.area_chart(df_chart)
            
            # Button synchronization triggers session state updates to make workflow smooth
            if st.button("🚀 Sync Sourcing specifications into FOB Incoterm"):
                st.session_state["sync_vol"] = volume_kg
                st.session_state["sync_commodity"] = commodity_option
                st.session_state["sync_packaging"] = packaging_option
                st.toast("Settings synchronized matching Incoterms input options.")
                
                
    # ── TAB 2: INCOTERMS CALCULATOR ──
    with tab_incoterms:
        st.subheader("🚢 Multi-Level Incoterms Price Appraiser")
        st.caption("Calculate exact pricing across FOB (Indonesian port), CIF (Ocean destination), and DDP (Delivery cleared to Warehouse).")
        
        # Load inputs synced from Tab 1
        st.markdown("<p style='font-size:10px; font-weight:bold; color:#475569;'>CURRENT ACTIVE INPUTS:</p>", unsafe_allow_html=True)
        active_inco_commodity = st.selectbox("Active Commodity Crop", list(PACKAGING_MASTER.keys()), key="inco_crop", index=list(PACKAGING_MASTER.keys()).index(st.session_state["sync_commodity"]))
        
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            active_inco_vol = st.number_input("Cargo Weight Volume (Kg)", min_value=1.0, value=float(st.session_state["sync_vol"]), step=50.0, key="inco_vol")
        with col_in2:
            pack_model_opts = list(PACKAGING_MASTER[active_inco_commodity].keys())
            try:
                p_idx = pack_model_opts.index(st.session_state["sync_packaging"])
            except ValueError:
                p_idx = 0
            active_inco_pack = st.selectbox("Current Pack Solution", pack_model_opts, index=p_idx, key="inco_pack")
            
        inco_opt_tab = st.radio("Incoterm Step Selection", ["1. FOB (Free On Board)", "2. CIF (Cost, Insurance & Freight)", "3. DDP (Delivered Duty Paid)", "📊 Comparative Port Matrix"], horizontal=True)
        
        # Immediate FOB calculation foundation
        f_port = st.selectbox("Port of Loading Hub", list(DOMESTIC_FREIGHT_COST_IDR.keys()), index=0)
        e_margin = st.slider("Target Profit Margin % (for standard FOB Exporter)", min_value=5, max_value=40, value=15, step=1)
        
        fob_result = calculate_fob(active_inco_commodity, active_inco_vol, active_inco_pack, f_port, live_rate, e_margin)
        
        # 🟢 FOB DETAILS
        if "1. FOB" in inco_opt_tab:
            st.markdown("##### ⚓ FOB Sourcing & Port Handling charges")
            
            # Unit Pricing displays
            u1, u2 = st.columns(2)
            with u1:
                st.markdown(f"""
                <div class="emerald-card">
                    <span style="font-size:11px; text-transform:uppercase; color:#FF4B4B; font-weight:700;">Calculated FOB Price Per Kg</span><br/>
                    <span style="font-size:26px; font-weight:900; color:#0f172a;">{format_usd(fob_result['fob_price_per_kg'])}</span> <span style="font-size:11px; color:#64748b;">USD / Kg</span><br/>
                    <span style="font-size:10px; color:#64748b; margin-top:5px; display:inline-block;">Contract FOB Aggregate: <b style="color:#0f172a;">{format_usd(fob_result['fob_total_usd'])}</b></span>
                </div>
                """, unsafe_allow_html=True)
            with u2:
                st.markdown(f"""
                <div style="background-color:#ffffff; border-radius:8px; padding:20px; border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(15,23,42,0.05); color:#0f172a;">
                    <span style="font-size:11px; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Base Sourcing & Margin Yield</span><br/>
                    <span style="font-size:18px; font-weight:800; color:#0f172a; display:inline-block; margin-top:6px;">Exporter Profit: {format_usd(fob_result['profit_usd'])}</span><br/>
                    <span style="font-size:11px; color:#64748b; margin-top:4px; display:inline-block;">Raw sourcing costs: {format_usd(fob_result['total_cost_usd'])} total</span>
                </div>
                """, unsafe_allow_html=True)
                
            # Table costs display
            st.write("---")
            st.markdown("**Detail Poin Pengeluaran (Skema IDR-Rupiah)**")
            bk_total = fob_result["breakdown_total"]
            df_bk = pd.DataFrame([
                {"Logistics Component": "Indonesian Cooperatives buying purchase", "Value in IDR": f"IDR {bk_total['purchasing_cost_idr']:,}"},
                {"Logistics Component": "Primary Woven & Container Package", "Value in IDR": f"IDR {bk_total['packaging_cost_idr']:,}"},
                {"Logistics Component": "Inland land route tracking to hub", "Value in IDR": f"IDR {bk_total['inland_trucking_idr']:,}"},
                {"Logistics Component": "Customs clearance & processing", "Value in IDR": f"IDR {bk_total['export_declaration_customs_idr']:,}"},
                {"Logistics Component": "Karantina Surveyor inspection fees", "Value in IDR": f"IDR {bk_total['loading_handling_surveyor_idr']:,}"},
                {"Logistics Component": "Port Terminal Handling Charge (THC)", "Value in IDR": f"IDR {bk_total['port_thc_charge_idr']:,}"},
            ])
            st.table(df_bk)
            
        # 🔒 PREMIUM LOCKED BLOCKS CHECK
        elif ("2. CIF" in inco_opt_tab or "3. DDP" in inco_opt_tab or "Comparative" in inco_opt_tab) and not st.session_state["is_unlocked"]:
            st.markdown("""
            <div style="background-color:#ffffff; border:1px solid #e2e8f0; border-left:4px solid #FF4B4B; border-radius:8px; padding:32px; text-align:center; margin: 20px 0; box-shadow:0 1px 3px rgba(15,23,42,0.05);">
                <span style="font-size:32px;">🔒</span>
                <h4 style="margin-top:10px; color:#0f172a; font-weight:700;">Premium Cryptography Authorization Needed</h4>
                <p style="font-size:12px; color:#64748b; max-width:480px; margin: 0 auto 15px auto;">This CIF ocean tracking module and subsequent customized import duty calculators are private. Input target passcode to unlock fully.</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # Render premium parts if unlocked
            # 🟢 CIF SEGMENTS
            if "2. CIF" in inco_opt_tab:
                st.markdown("##### ⚓ CIF International Marine Shipment calculations")
                c_dp = st.selectbox("Ocean Destination Port", list(DESTINATION_PORT_PRESETS.keys()), index=0)
                
                # Preset autofills
                preset_freight = DESTINATION_PORT_PRESETS[c_dp]["base_freight_usd_per_kg"]
                c_freight = st.number_input("Ocean Freight Rate cargo cost (USD / Kg)", min_value=0.0, value=preset_freight, step=0.01)
                c_ins = st.number_input("Ad Valorem Insurance rate % (ICC Minimum Standard A)", min_value=0.0, max_value=5.0, value=0.3, step=0.05)
                
                cif_result = calculate_cif(fob_result, c_dp, c_freight, c_ins)
                
                ui_1, ui_2 = st.columns(2)
                with ui_1:
                    st.markdown(f"""
                    <div style="background-color:#ffffff; color:#0f172a; border:1px solid #e2e8f0; border-left:4px solid #3b82f6; border-radius:8px; padding:20px; box-shadow:0 1px 3px rgba(15, 23, 42, 0.05);">
                        <span style="font-size:11px; text-transform:uppercase; color:#3b82f6; font-weight:700;">Calculated CIF Price per Kg</span><br/>
                        <span style="font-size:26px; font-weight:950; color:#0f172a;">{format_usd(cif_result['cif_price_per_kg'])}</span> <span style="font-size:11px; color:#64748b;">USD / Kg</span><br/>
                        <span style="font-size:10px; color:#64748b; margin-top:5px; display:inline-block;">Contract CIF Invoice sum: <b style="color:#0f172a;">{format_usd(cif_result['cif_total_usd'])}</b></span>
                    </div>
                    """, unsafe_allow_html=True)
                with ui_2:
                    st.markdown(f"""
                    <div style="background-color:#ffffff; border-radius:8px; padding:20px; border:1px solid #e2e8f0; font-size:12px; box-shadow:0 1px 3px rgba(15, 23, 42, 0.05); color:#0f172a;">
                        <span style="font-weight:700; color:#3b82f6; font-size:13px;">CIF Cost Breakdowns</span><br/>
                        <div style="margin-top:8px; line-height:1.5; color:#475569;">
                        • Base FOB value: <b style="color:#0f172a;">{format_usd(cif_result['fob_total_usd'])}</b><br/>
                        • Ocean maritime freight: <b style="color:#0f172a;">{format_usd(cif_result['ocean_freight_usd'])}</b><br/>
                        • Transport insurance: <b style="color:#0f172a;">{format_usd(cif_result['insurance_usd'])}</b> ({cif_result['insurance_rate_pct']}% rate)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            # 🟢 DDP SEGMENTS
            elif "3. DDP" in inco_opt_tab:
                st.markdown("##### ⚓ Destination Country custom entry & port cleared taxes")
                
                c_country = st.selectbox("Import Destination Country", list(COUNTRY_DUTY_PRESETS.keys()), index=0)
                preset_duty = COUNTRY_DUTY_PRESETS[c_country]["duty_rate_pct"]
                preset_vat = COUNTRY_DUTY_PRESETS[c_country]["vat_rate_pct"]
                
                d1, d2 = st.columns(2)
                with d1:
                    import_duty = st.number_input("Customs General Tariff Import Duty %", min_value=0.0, value=preset_duty, step=0.5)
                with d2:
                    import_vat = st.number_input("Local Taxes / VAT Value %", min_value=0.0, value=preset_vat, step=0.5)
                    
                i1, i2 = st.columns(2)
                with i1:
                    local_inland = st.number_input("Secondary Inland truck deliveries (USD Flat)", min_value=0.0, value=150.0, step=10.0)
                with i2:
                    customs_handling = st.number_input("Brokerage & port terminal clearances (USD Flat)", min_value=0.0, value=75.0, step=5.0)
                    
                # CIF needed as foundation
                c_dp = st.selectbox("Default base delivery port", list(DESTINATION_PORT_PRESETS.keys()), index=0)
                preset_freight = DESTINATION_PORT_PRESETS[c_dp]["base_freight_usd_per_kg"]
                cif_result_ddp = calculate_cif(fob_result, c_dp, preset_freight, 0.3)
                
                ddp_result = calculate_ddp(cif_result_ddp, import_duty, import_vat, local_inland, customs_handling)
                
                st.write("---")
                ud_1, ud_2 = st.columns(2)
                with ud_1:
                    st.markdown(f"""
                    <div style="background-color:#ffffff; color:#0f172a; border:1px solid #e2e8f0; border-left:4px solid #FF4B4B; border-radius:8px; padding:20px; box-shadow:0 1px 3px rgba(15, 23, 42, 0.05);">
                        <span style="font-size:11px; text-transform:uppercase; color:#FF4B4B; font-weight:700;">Calculated DDP Price per Kg</span><br/>
                        <span style="font-size:26px; font-weight:950; color:#0f172a;">{format_usd(ddp_result['ddp_price_per_kg'])}</span> <span style="font-size:11px; color:#64748b;">USD / Kg</span><br/>
                        <span style="font-size:10px; color:#64748b; margin-top:5px; display:inline-block;">Contract total cleared: <b style="color:#0f172a;">{format_usd(ddp_result['ddp_total_usd'])}</b></span>
                    </div>
                    """, unsafe_allow_html=True)
                with ud_2:
                    st.markdown(f"""
                    <div style="background-color:#ffffff; border-radius:8px; padding:20px; border:1px solid #e2e8f0; font-size:12px; box-shadow:0 1px 3px rgba(15, 23, 42, 0.05); color:#0f172a;">
                        <span style="font-weight:700; color:#FF4B4B; font-size:13px;">DDP Cost breakdown (USD)</span><br/>
                       <div style="margin-top:8px; line-height:1.5; color:#475569;">
                        • Base CIF value: <b style="color:#0f172a;">{format_usd(ddp_result['cif_total_usd'])}</b><br/>
                        • Custom Duty tax paid: <b style="color:#0f172a;">{format_usd(ddp_result['import_duty_usd'])}</b> ({ddp_result['duty_rate_pct']}% rate)<br/>
                        • VAT / GST value: <b style="color:#0f172a;">{format_usd(ddp_result['vat_usd'])}</b> ({ddp_result['vat_rate_pct']}% rate)<br/>
                        • Local inland tracking flat: <b style="color:#0f172a;">{format_usd(ddp_result['inland_freight_usd'] + ddp_result['customs_handling_usd'])}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            # 🟢 COMPARATIVE MATRIX SEGMENTS
            elif "Comparative" in inco_opt_tab:
                st.markdown("##### ⚓ Comprehensive Global Port freight pricing metrics")
                st.caption("Side-by-side shipping comparisons from Indonesia loaded with standard spices.")
                
                compare_data = []
                for p_name, p_val in DESTINATION_PORT_PRESETS.items():
                    if p_name == "Custom / Other":
                        continue
                    freight_rate_val = p_val["base_freight_usd_per_kg"]
                    cif_calc = calculate_cif(fob_result, p_name, freight_rate_val, 0.3)
                    ddp_calc = calculate_ddp(cif_calc, 3.5, 12, 150.0, 75.0)
                    
                    compare_data.append({
                        "Destination Port": p_name,
                        "Region": p_val["region"],
                        "Ocean Freight/Kg": format_usd(freight_rate_val),
                        "Total CIF Invoice Value": format_usd(cif_calc["cif_total_usd"]),
                        "Total DDP Cleared Value": format_usd(ddp_calc["ddp_total_usd"])
                    })
                df_compare = pd.DataFrame(compare_data)
                df_compare.index+=1
                
                st.dataframe(
                    df_compare,
                    use_container_width=True
                )


    # ── TAB 3: EXPORT DOCUMENTS GENERATOR ──
    with tab_docs:
        st.subheader("📄 Formal Export Documents Desk")
        st.caption("Fill dynamic consignee party fields and print customized formal export invoices, packing list manifests or quotes.")
        
        # Sourcing checks
        if not fob_result:
            st.warning("Please complete an active calculation foundation first under Sourcing tab.")
        else:
            # Multi Document option selector
            doc_option = st.selectbox(
                "Select Export Document Type",
                ["Commercial Quotation", "Proforma Invoice (PI)", "Commercial Invoice (CI)", "Packing List (PL)", "Shipping Instruction (SI)"]
            )
            
            # Map type option name to short type code
            doc_type_mapping = {
                "Commercial Quotation": "quote",
                "Proforma Invoice (PI)": "pi",
                "Commercial Invoice (CI)": "ci",
                "Packing List (PL)": "pl",
                "Shipping Instruction (SI)": "si"
            }
            doc_type_code = doc_type_mapping[doc_option]
            
            # 🔐 Standard validation check for premium documents CI, PL, SI
            if doc_type_code in ["ci", "pl", "si"] and not st.session_state["is_unlocked"]:
                 st.markdown("""
                 <div style="background-color:#ffffff; border:1px solid #e2e8f0; border-left:4px solid #FF4B4B; border-radius:8px; padding:32px; text-align:center; margin: 20px 0; box-shadow:0 1px 3px rgba(15,23,42,0.05);">
                     <span style="font-size:32px;">🔒</span>
                     <h4 style="color:#0f172a; margin-top:10px; font-weight:700;">Premium Document Framework Access Locked</h4>
                     <p style="font-size:12px; color:#64748b; max-width:480px; margin: 0 auto 15px auto;">Commercial Invoices, formal packing manifests, and SI shipping instructions are cryptographically locked. Insert export passcode in sidebar.</p>
                 </div>
                 """, unsafe_allow_html=True)
                
            else:
                st.write("---")
                
                # Two-column document form inputs
                form_col, prev_col = st.columns([1, 1])
                
                with form_col:
                    st.markdown("**1. Contracting Corporate Parties**")
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        seller_name = st.text_input("Exporter (Seller Name)", "PT Magastu Indoprime Group")
                        seller_addr = st.text_area("Exporter Address", "Grand Slipi Tower 38th Floor, S. Parman 22, Jakarta Pin 11480", height=80)
                        seller_phone = st.text_input("Seller Tel", "+62 21 2902 2231")
                        seller_email = st.text_input("Seller Email", "trade@magastu.com")
                    with col_p2:
                        buyer_name = st.text_input("Importer (Buyer Name)", "Global Spice Importers AG")
                        buyer_addr = st.text_area("Importer Address", "Speicherstrasse 12, Hamburg Port City, 20457 Hamburg", height=80)
                        buyer_phone = st.text_input("Buyer Tel", "+49 40 3119 4455")
                        buyer_email = st.text_input("Buyer Email", "import@globalspicetrade.de")
                        
                    st.write("---")
                    st.markdown("**2. Sheet Reference Metadata**")
                    col_ref1, col_ref2 = st.columns(2)
                    with col_ref1:
                        doc_ref_no = st.text_input("Document Identification No", f"MSG/{doc_type_code.upper()}/2026/184")
                    with col_ref2:
                        doc_issue_date = st.date_input("Date of Issue", datetime.date.today())
                        
                    # Document specific additional parameters
                    custom_meta = {}
                    if doc_type_code in ["quote", "pi"]:
                        p_val_days = st.number_input("Price Validity Duration Days", min_value=5, value=14, step=1)
                        custom_meta["validityDays"] = p_val_days
                    elif doc_type_code == "ci":
                        custom_bl = st.text_input("Bill of Lading No reference", "MSK-99023114-ID")
                        custom_meta["additionalFieldLabel"] = "Bill of Lading No"
                        custom_meta["additionalFieldValue"] = custom_bl
                    elif doc_type_code == "pl":
                        custom_marks = st.text_input("Shipping Transit Marks & Labels", "MIG/SPICE/ROT-01")
                        custom_meta["additionalFieldLabel"] = "Shipping Marks"
                        custom_meta["additionalFieldValue"] = custom_marks
                    elif doc_type_code == "si":
                        carrier_name = st.text_input("Transit Ocean Shipping Carrier Line", "MAERSK LINE INDONESIA")
                        custom_meta["additionalFieldLabel"] = "Transit Ocean carrier"
                        custom_meta["additionalFieldValue"] = carrier_name
                        
                    pay_terms = "30% T/T Advance Deposit, 70% against B/L Copy"
                    bank_inst = "Bank BCA, Cabang Harmoni Jakarta\nAccount No: 887-0311-2311-9\nBeneficiary: PT Magastu Indoprime Group\nSWIFT Code: CENAIDJA"
                    
                    if doc_type_code in ["quote", "pi", "ci"]:
                        st.write("---")
                        st.markdown("**3. Financial Clauses**")
                        pay_terms = st.text_input("Agreement Payment Clauses", "30% T/T Advance Deposit, 70% against B/L Copy")
                        bank_inst = st.text_area("Remittance Bank Details guidelines", "Bank BCA, Cabang Harmoni Jakarta\nAccount No: 887-0311-2311-9\nBeneficiary: PT Magastu Indoprime Group\nSWIFT Code: CENAIDJA", height=100)
                        
                    st.write("---")
                    st.markdown("**4. Additional QA Guidelines Notes**")
                    qa_notes = st.text_area("Fumigation and Phytosanitary declarations", "1. Wooden outer pallets must comply with ISPM-15 fumigation standards.\n2. Phytosanitary Health Certificate and COA supplied free of charge once vessel loads.", height=100)
                    
                # ── Live HTML Paper Preview ──
                with prev_col:
                    st.markdown("**Live A4 Print Sheet Preview**")
                    st.caption("Symmetrical replica of final generated print paper document.")
                    
                    parties_dict = {
                        "sellerName": seller_name,
                        "sellerAddress": seller_addr,
                        "sellerCountry": "Indonesia",
                        "sellerPhone": seller_phone,
                        "sellerEmail": seller_email,
                        "buyerName": buyer_name,
                        "buyerAddress": buyer_addr,
                        "buyerCountry": "Worldwide",
                        "buyerPhone": buyer_phone,
                        "buyerEmail": buyer_email
                    }
                    
                    meta_vals = {
                        "docNumber": doc_ref_no,
                        "issueDate": doc_issue_date.strftime("%Y-%m-%d"),
                        "paymentTerms": pay_terms,
                        "bankDetails": bank_inst,
                        "notes": qa_notes,
                        **custom_meta
                    }
                    
                    # Layout HTML Replica construction
                    html_preview = f"""
                    <div class="a4-paper">
                        <div class="a4-header">
                            <div>
                                <span style="font-weight:900; font-size:12px; letter-spacing:0.5px;">{doc_option.upper()}</span><br/>
                                <span style="font-size:7.5px; opacity:0.8;">InTradeX Export Intelligence Desk</span>
                            </div>
                            <span style="font-size:7px; font-weight:bold; opacity:0.9;">PT Magastu Indoprime</span>
                        </div>
                        
                        <div style="background-color:#f8fafc; border:1px solid #e2e8f0; padding:8px; font-size:8.5px; margin-bottom:12px; border-radius:4px;">
                            <b>Document No:</b> {doc_ref_no} &nbsp;|&nbsp; <b>Issue Date:</b> {doc_issue_date.strftime('%Y-%m-%d')}<br/>
                            <b>Incoterms Base:</b> FOB {fob_result.get('loading_port', '—')} Loading
                        </div>
                        
                        <div style="display:flex; justify-content:space-between; gap:10px; margin-bottom:12px;">
                            <div style="flex:1; border:1px solid #e2e8f0; padding:8px; border-radius:3px;">
                                <b style="color:#0f172a; font-size:8px; display:block; margin-bottom:2px;">EXPORTER (SELLER)</b>
                                <b>{seller_name}</b><br/>{seller_addr}
                            </div>
                            <div style="flex:1; border:1px solid #e2e8f0; padding:8px; border-radius:3px;">
                                <b style="color:#0f172a; font-size:8px; display:block; margin-bottom:2px;">CONSIGNEE (BUYER)</b>
                                <b>{buyer_name}</b><br/>{buyer_addr}
                            </div>
                        </div>
                        
                        <div style="border:1px solid #e2e8f0; margin-bottom:12px; border-radius:3px; overflow:hidden;">
                            <table style="width:100%; font-size:8px; border-collapse:collapse; text-align:left;">
                                <tr style="background-color:#0f172a; color:white; font-weight:bold;">
                                    <th style="padding:4px 6px;">Description of Cargo</th>
                                    <th style="padding:4px 6px;">HS Code</th>
                                    <th style="padding:4px 6px;">Net Weight</th>
                                    <th style="padding:4px 6px; text-align:right;">Total Amount</th>
                                </tr>
                                <tr>
                                    <td style="padding:6px; font-weight:bold;">{fob_result['commodity']}</td>
                                    <td style="padding:6px; font-family:monospace;">{fob_result['hs_code']}</td>
                                    <td style="padding:6px;">{fob_result['volume_kg']:,} Kg</td>
                                    <td style="padding:6px; text-align:right; font-weight:bold;">{format_usd(fob_result['fob_total_usd'])}</td>
                                </tr>
                                <tr style="background-color:#f8fafc; color:#0f172a; font-weight:black; border-top:1px solid #e2e8f0;">
                                    <td colspan="3" style="padding:6px; font-weight:bold;">TOTAL INVOICE FOB BASE VALUE:</td>
                                    <td style="padding:6px; text-align:right; font-weight:bold;">{format_usd(fob_result['fob_total_usd'])}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div style="font-size:7.5px; opacity:0.8; margin-top:20px; text-align:center; border-top:1px dashed #e2e8f0; padding-top:10px;">
                            Generated via InTradeX Premium Trade Desk.
                        </div>
                    </div>
                    """
                    st.markdown(html_preview, unsafe_allow_html=True)
                    
                    # Direct Binary Download buttons from ReportLab & Docx generators
                    st.write("---")
                    st.markdown("**5. Retrieve & Download Print Manifest File**")
                    
                    pdf_bytes_data = generate_pdf_bytes(doc_type_code, fob_result, parties_dict, meta_vals)
                    docx_bytes_data = generate_docx_bytes(doc_type_code, fob_result, parties_dict, meta_vals)
                    
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        st.download_button(
                            label=f"📥 Download formal PDF Document",
                            data=pdf_bytes_data,
                            file_name=f"{doc_type_code}_{doc_ref_no.replace('/', '_')}.pdf",
                            mime="application/pdf"
                        )
                    with col_dl2:
                        st.download_button(
                            label="📥 Download Word DOCX Document",
                            data=docx_bytes_data,
                            file_name=f"{doc_type_code}_{doc_ref_no.replace('/', '_')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )


    # ── TAB 4: COMPLIANCE & TARIFF BIODATA ──
    with tab_intel:
        st.subheader("🌐 Indonesian Spice Regulatory compliance benchmarks")
        st.caption("Explore quality compliance thresholds, maximum residue parameters, and customs SKA certificates requirements.")
        
        st.markdown("""
        <div class="compliance-card">
            <h4>🛂 Mandatory Export Document Checklist for Spices:</h4>
            <ol>
                <li><b>Phytosanitary Certificate:</b> Issued by Indonesian Badan Karantina Pertanian confirming compliance with target boundary insect & hazard fumigations.</li>
                <li><b>Certificate of Origin (SKA / Form A):</b> Declares the agricultural product is authentic Indonesian crop under FTA agreements.</li>
                <li><b>Certificate of Analysis (COA):</b> Curated testing verifying exact moisture (standard <12% for Cinnamon/Nutmeg) and mold aflatoxin levels under food regulatory bounds.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.markdown("**Quality Moisture Index Guidelines for Exporters**")
        st.info("Ensure spice grains sit below the 12% moisture thresholds to eliminate aflatoxin hazard alerts before booking international freight voyages.")


# ── 5. PERSISTENT SMART TRADE INTELLIGENCE AI ADVISOR ──
with col_advisor:
    st.markdown("""
    <div style="background-color:#ffffff; border-radius:8px; padding:14px; margin-bottom:15px; border:1px solid #e2e8f0; border-left:4px solid #FF4B4B; text-align:center; box-shadow:0 1px 3px rgba(15,23,42,0.05);">
        <span style="font-weight:800; color:#0f172a; font-size:12px; letter-spacing:0.5px; text-transform:uppercase;">InTradeX AI Advisor</span><br/>
        <span style="font-size:10px; color:#64748b; font-weight:500;">Corporate Compliance Logistics Helpdesk</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Render native Streamlit chats
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Handle user prompts
    if advisor_prompt := st.chat_input("Ask about duties, pesticides, RASFF alerts, or compliance rules..."):
        # Display User Input
        with st.chat_message("user"):
            st.markdown(advisor_prompt)
        st.session_state["chat_history"].append({"role": "user", "content": advisor_prompt})
        
        # Build comprehensive context prompts injecting calculated matrix points
        system_instructions = f"""You are InTradeX, an advanced AI-powered Export Intelligence Consultant for Magastu Indoprime Group.
Current language user is talking in is {selected_lang}. Please reply exclusively in this language.
Active client sourcing context:
- Commodity: {commodity_option}
- Target Volume: {active_inco_vol} Kg
- Packaging: {active_inco_pack}
- Estimated FOB Port Price: {format_usd(fob_result['fob_price_per_kg']) if fob_result else 'Not calculated'} / Kg
- Loaded Port Hub: {f_port}

Rules:
1. Speak with professional, highly knowledgeable Indonesian spice logistics authority.
2. Provide real compliance benchmarks (e.g. RASFF pesticide alerts, EU maximum residue limits - MRLs, FDA registration, Saudi FDA rules).
3. Do not assume or mention environment variables or platform details. Remain strictly business-oriented.
4. IMPORTANT: Never output double asterisks (**) or single asterisks (*) anywhere in the text. Do not use markdown style headers or symbols. Instead, use CAPITALIZED inline text and normal, clean paragraphs or numbered lists (1., 2.) for structuring lists.
"""

        with st.chat_message("assistant"):
            st.write("Analysing compliance checkpoints...")
            
            # Request Gemini generative response
            # Let's import on flight to protect memory usage footprint
            from google import genai
            from google.genai import types
            
            # API Key declaration from env
            api_key = os.environ.get("GEMINI_API_KEY", "")
            
            if not api_key:
                st.error("Error: GEMINI_API_KEY environment variable is missing on server configs.")
                response_text = "API credentials not configured on the host workspace."
            else:
                try:
                    client = genai.Client(api_key=api_key)
                    config = types.GenerateContentConfig(
                        system_instruction=system_instructions,
                        temperature=0.4
                    )
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=advisor_prompt,
                        config=config
                    )
                    response_text = response.text
                except Exception as e:
                    # Alternative model fallback
                    try:
                        client = genai.Client(api_key=api_key)
                        config = types.GenerateContentConfig(
                            system_instruction=system_instructions,
                            temperature=0.4
                        )
                        response = client.models.generate_content(
                            model='gemini-2.0-flash',
                            contents=advisor_prompt,
                            config=config
                        )
                        response_text = response.text
                    except Exception as e2:
                        response_text = f"An issue occurred compiling compliance guidelines: {str(e2)}"
            
            st.write(response_text)
            st.session_state["chat_history"].append({"role": "model", "content": response_text})
