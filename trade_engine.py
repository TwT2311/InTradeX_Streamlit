# -*- coding: utf-8 -*-
"""
ThinkSpices Trade Intelligence & Sourcing Engine
Defines all dataset tables, HS codes, standard packing configurations,
domestic port costs, and international duty grids for Indonesian Spices.
"""

import math
import datetime

# Master configurations for packaging specifications per crop type
PACKAGING_MASTER = {
    "Cinnamon Cassia Whole": {
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.20, "type": "Bag"},
        "PP Woven Bag 50 Kg": {"weight": 50.0, "price_per_unit": 12000, "tare_weight": 0.35, "type": "Bag"}
    },
    "Cinnamon Ceylon Whole": {
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.20, "type": "Bag"},
        "PP Woven Bag 50 Kg": {"weight": 50.0, "price_per_unit": 12000, "tare_weight": 0.35, "type": "Bag"}
    },
    "Banda Nutmeg Whole": {
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.30, "type": "Bag"},
        "PP Woven Bag 50 Kg": {"weight": 50.0, "price_per_unit": 12000, "tare_weight": 0.35, "type": "Bag"}
    },
    "Papua Nutmeg Whole": {
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.30, "type": "Bag"},
        "PP Woven Bag 50 Kg": {"weight": 50.0, "price_per_unit": 12000, "tare_weight": 0.35, "type": "Bag"}
    },
    "Mace": {
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.30, "type": "Bag"},
        "Carton Box 10 Kg": {"weight": 10.0, "price_per_unit": 15000, "tare_weight": 0.50, "type": "Carton"}
    },
    "Arabica Coffee (Green Beans)": {
        "Jute Bag 60 Kg": {"weight": 60.0, "price_per_unit": 18000, "tare_weight": 1.00, "type": "Bag"},
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.25, "type": "Bag"}
    },
    "Robusta Coffee (Green Beans)": {
        "Jute Bag 60 Kg": {"weight": 60.0, "price_per_unit": 18000, "tare_weight": 1.00, "type": "Bag"},
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.25, "type": "Bag"}
    },
    "Black Pepper": {
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.30, "type": "Bag"}
    },
    "White Pepper": {
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.30, "type": "Bag"}
    },
    "Clove": {
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.30, "type": "Bag"},
        "PP Woven Bag 50 Kg": {"weight": 50.0, "price_per_unit": 12000, "tare_weight": 0.35, "type": "Bag"}
    },
    "Red Ginger": {
        "PP Woven Bag 25 Kg": {"weight": 25.0, "price_per_unit": 7500, "tare_weight": 0.20, "type": "Bag"},
        "PP Woven Bag 50 Kg": {"weight": 50.0, "price_per_unit": 12000, "tare_weight": 0.35, "type": "Bag"}
    },
    "Vanilla": {
        "Vacuum Bag + Carton 5 Kg": {"weight": 5.0, "price_per_unit": 25000, "tare_weight": 0.50, "type": "Carton"},
        "Vacuum Bag + Carton 10 Kg": {"weight": 10.0, "price_per_unit": 35000, "tare_weight": 0.80, "type": "Carton"}
    },
    "Patchouli Oil": {
        "HDPE Drum 25 Kg": {"weight": 25.0, "price_per_unit": 85000, "tare_weight": 1.80, "type": "Drum"},
        "Steel Drum 180 Kg": {"weight": 180.0, "price_per_unit": 350000, "tare_weight": 18.00, "type": "Drum"}
    }
}

# Commodity Domestic Sourcing Buy Prices (IDR per Kg)
COMMODITY_BUY_PRICES = {
    "Cinnamon Cassia Whole": 36000,
    "Cinnamon Ceylon Whole": 240000,
    "Banda Nutmeg Whole": 140000,
    "Papua Nutmeg Whole": 110000,
    "Mace": 220000,
    "Arabica Coffee (Green Beans)": 95000,
    "Robusta Coffee (Green Beans)": 68000,
    "Black Pepper": 68000,
    "White Pepper": 110000,
    "Clove": 95000,
    "Red Ginger": 28000,
    "Vanilla": 750000,
    "Patchouli Oil": 850000,
}

# Harmonized System (HS) Code Database
HS_CODE_DATABASE = {
    "Cinnamon Cassia Whole": {"code": "0906.11", "description": "Cinnamon (Cinnamomum zeylanicum), whole cassia", "chapter": "09", "unit": "Kg"},
    "Cinnamon Ceylon Whole": {"code": "0906.11", "description": "Cinnamon (Cinnamomum zeylanicum), whole ceylon", "chapter": "09", "unit": "Kg"},
    "Banda Nutmeg Whole": {"code": "0908.11", "description": "Nutmeg (whole Banda variety)", "chapter": "09", "unit": "Kg"},
    "Papua Nutmeg Whole": {"code": "0908.11", "description": "Nutmeg (whole Papua variety)", "chapter": "09", "unit": "Kg"},
    "Mace": {"code": "0908.21", "description": "Mace, neither crushed nor ground", "chapter": "09", "unit": "Kg"},
    "Arabica Coffee (Green Beans)": {"code": "0901.11", "description": "Arabica coffee, not roasted, not decaffeinated", "chapter": "09", "unit": "Kg"},
    "Robusta Coffee (Green Beans)": {"code": "0901.11", "description": "Robusta coffee, not roasted, not decaffeinated", "chapter": "09", "unit": "Kg"},
    "Black Pepper": {"code": "0904.11", "description": "Black Pepper, neither crushed nor ground", "chapter": "09", "unit": "Kg"},
    "White Pepper": {"code": "0904.12", "description": "White Pepper, neither crushed nor ground", "chapter": "09", "unit": "Kg"},
    "Clove": {"code": "0907.10", "description": "Cloves (whole fruit, cloves and stems)", "chapter": "09", "unit": "Kg"},
    "Red Ginger": {"code": "0910.11", "description": "Ginger, neither crushed nor ground (Red Ginger variety)", "chapter": "09", "unit": "Kg"},
    "Vanilla": {"code": "0905.10", "description": "Vanilla beans (unprocessed)", "chapter": "09", "unit": "Kg"},
    "Patchouli Oil": {"code": "3301.29", "description": "Essential oils: patchouli oil", "chapter": "33", "unit": "Kg"},
}

# Domestic Sourcing inland Freight Trucking Charges (in IDR)
DOMESTIC_FREIGHT_COST_IDR = {
    "Tanjung Priok, Jakarta": 2500000,
    "Tanjung Perak, Surabaya": 3000000,
    "Belawan, Medan": 4000000,
    "Soekarno-Hatta, Makassar": 3500000,
    "Tanjung Emas, Semarang": 2800000
}

# Destination port maritime freight approximations (in USD per Net Kg)
DESTINATION_PORT_PRESETS = {
    "Hamburg, Germany":         {"region": "Europe",        "base_freight_usd_per_kg": 0.18},
    "Rotterdam, Netherlands":   {"region": "Europe",        "base_freight_usd_per_kg": 0.17},
    "Antwerp, Belgium":         {"region": "Europe",        "base_freight_usd_per_kg": 0.17},
    "Felixstowe, UK":           {"region": "Europe",        "base_freight_usd_per_kg": 0.19},
    "New York, USA":            {"region": "North America", "base_freight_usd_per_kg": 0.20},
    "Los Angeles, USA":         {"region": "North America", "base_freight_usd_per_kg": 0.16},
    "Houston, USA":             {"region": "North America", "base_freight_usd_per_kg": 0.21},
    "Jebel Ali, UAE":           {"region": "Middle East",   "base_freight_usd_per_kg": 0.10},
    "Dammam, Saudi Arabia":     {"region": "Middle East",   "base_freight_usd_per_kg": 0.11},
    "Tokyo, Japan":             {"region": "Asia Pacific",  "base_freight_usd_per_kg": 0.09},
    "Busan, South Korea":       {"region": "Asia Pacific",  "base_freight_usd_per_kg": 0.08},
    "Sydney, Australia":        {"region": "Asia Pacific",  "base_freight_usd_per_kg": 0.12},
    "Auckland, New Zealand":    {"region": "Oceania",       "base_freight_usd_per_kg": 0.14},
    "Singapore":                {"region": "Asia Pacific",  "base_freight_usd_per_kg": 0.06},
    "Shanghai, China":          {"region": "Asia Pacific",  "base_freight_usd_per_kg": 0.07},
    "Mumbai, India":            {"region": "South Asia",    "base_freight_usd_per_kg": 0.08},
    "Colombo, Sri Lanka":       {"region": "South Asia",    "base_freight_usd_per_kg": 0.07},
    "Custom / Other":           {"region": "Custom",        "base_freight_usd_per_kg": 0.00},
}

# Country Custom Tariffs and VAT standard indices
COUNTRY_DUTY_PRESETS = {
    "Germany":           {"duty_rate_pct": 0.0, "vat_rate_pct": 19.0, "note": "EU MFN — most spices 0%"},
    "Netherlands":       {"duty_rate_pct": 0.0, "vat_rate_pct": 21.0, "note": "EU MFN — most spices 0%"},
    "Belgium":           {"duty_rate_pct": 0.0, "vat_rate_pct": 21.0, "note": "EU MFN — most spices 0%"},
    "France":            {"duty_rate_pct": 0.0, "vat_rate_pct": 20.0, "note": "EU MFN — most spices 0%"},
    "United Kingdom":    {"duty_rate_pct": 0.0, "vat_rate_pct": 0.0,  "note": "UK GSP — Indonesian spices 0% duty, food VAT 0%"},
    "United States":     {"duty_rate_pct": 0.0, "vat_rate_pct": 0.0,  "note": "US — most spices 0% MFN; no federal VAT"},
    "United Arab Emirates": {"duty_rate_pct": 5.0, "vat_rate_pct": 5.0, "note": "GCC CET 5% + VAT 5%"},
    "Saudi Arabia":      {"duty_rate_pct": 5.0, "vat_rate_pct": 15.0, "note": "GCC CET 5% + VAT 15%"},
    "Japan":             {"duty_rate_pct": 3.0, "vat_rate_pct": 10.0, "note": "Japan MFN ~3% avg + consumption tax 10%"},
    "South Korea":       {"duty_rate_pct": 5.0, "vat_rate_pct": 10.0, "note": "Korea MFN ~5% spices + VAT 10%"},
    "Australia":         {"duty_rate_pct": 0.0, "vat_rate_pct": 10.0, "note": "Australia IA-CEPA — spices 0% + GST 10%"},
    "New Zealand":       {"duty_rate_pct": 0.0, "vat_rate_pct": 15.0, "note": "NZ FTA — most spices 0% duty + GST 15%"},
    "Custom / Other":    {"duty_rate_pct": 0.0, "vat_rate_pct": 0.0,  "note": "Enter rates manually below"},
}

# Historical and current FOB price range guides (FOB / Kg)
MARKET_ADVISOR_BENCHMARKS = {
    "Cinnamon Cassia Whole": {"low": 2.20,  "high": 4.50,  "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
    "Cinnamon Ceylon Whole": {"low": 15.00, "high": 30.00, "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
    "Banda Nutmeg Whole":    {"low": 8.50,  "high": 14.00, "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
    "Papua Nutmeg Whole":    {"low": 6.50,  "high": 11.00, "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
    "Mace":                  {"low": 14.00, "high": 24.00, "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
    "Arabica Coffee (Green Beans)": {"low": 4.50,  "high": 8.00,  "unit": "USD/kg", "source": "ICO Index (est.)"},
    "Robusta Coffee (Green Beans)": {"low": 3.50,  "high": 5.50,  "unit": "USD/kg", "source": "ICO Index (est.)"},
    "Black Pepper":   {"low": 3.80,  "high": 6.50,  "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
    "White Pepper":   {"low": 6.00,  "high": 9.50,  "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
    "Clove":          {"low": 5.50,  "high": 9.00,  "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
    "Red Ginger":     {"low": 1.80,  "high": 3.50,  "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
    "Vanilla":        {"low": 40.00, "high": 80.00, "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
    "Patchouli Oil":  {"low": 48.00, "high": 70.00, "unit": "USD/kg", "source": "ITC Trade Map (est.)"},
}


def calculate_packaging(commodity, target_weight_kg, packaging_name, exchange_rate=16200):
    """
    Kalkulasi kuantitas kemasan dan taksiran berat kotor ekspor.
    """
    comm_pack_options = PACKAGING_MASTER.get(commodity)
    if not comm_pack_options:
        return {"error": f"Commodity '{commodity}' not found."}

    pack_info = comm_pack_options.get(packaging_name)
    if not pack_info:
        return {"error": f"Packaging '{packaging_name}' not found for {commodity}."}

    weight_per_unit = pack_info["weight"]
    price_per_unit_idr = pack_info["price_per_unit"]
    tare_weight = pack_info["tare_weight"]

    total_units_needed = math.ceil(target_weight_kg / weight_per_unit)
    total_packaging_cost_idr = total_units_needed * price_per_unit_idr
    total_packaging_cost_usd = total_packaging_cost_idr / exchange_rate
    packaging_cost_per_kg_usd = total_packaging_cost_usd / target_weight_kg if target_weight_kg > 0 else 0.0

    total_tare_weight = total_units_needed * tare_weight
    gross_weight_estimate = target_weight_kg + total_tare_weight

    return {
        "commodity": commodity,
        "selectedPackaging": packaging_name,
        "packagingType": pack_info["type"],
        "weightPerUnitKg": weight_per_unit,
        "pricePerUnitIdr": price_per_unit_idr,
        "totalUnitsNeeded": total_units_needed,
        "totalPackagingCostUsd": total_packaging_cost_usd,
        "packagingCostPerKgUsd": packaging_cost_per_kg_usd,
        "netWeightKg": target_weight_kg,
        "grossWeightKg": round(gross_weight_estimate, 2),
        "exchangeRate": exchange_rate
    }


def calculate_fob(commodity, volume_kg, packaging_name, loading_port, exchange_rate=16200, profit_margin_percent=15):
    """
    Kalkulasi taksiran harga ekspor FOB (Free On Board).
    """
    pack_res = calculate_packaging(commodity, volume_kg, packaging_name, exchange_rate)
    if "error" in pack_res:
        return pack_res

    buy_price_idr_per_kg = COMMODITY_BUY_PRICES.get(commodity, 35000)
    total_purchase_cost_idr = buy_price_idr_per_kg * volume_kg

    inland_trucking_idr = DOMESTIC_FREIGHT_COST_IDR.get(loading_port, 2500000)
    customs_export_clearance_idr = 1500000
    handling_surveyor_idr = 3500000
    port_handling_thc_idr = 1800000

    total_local_costs_idr = (
        inland_trucking_idr +
        customs_export_clearance_idr +
        handling_surveyor_idr +
        port_handling_thc_idr
    )

    total_packaging_cost_idr = pack_res["totalUnitsNeeded"] * pack_res["pricePerUnitIdr"]

    total_fob_cost_idr = total_purchase_cost_idr + total_packaging_cost_idr + total_local_costs_idr
    total_fob_cost_usd = total_fob_cost_idr / exchange_rate

    margin_fraction = profit_margin_percent / 100
    if margin_fraction >= 1.0:
        margin_fraction = 0.99 # prevent division by zero

    fob_total_price_usd = total_fob_cost_usd / (1.0 - margin_fraction)
    fob_price_per_kg_usd = fob_total_price_usd / volume_kg if volume_kg > 0 else 0.0

    profit_usd = fob_total_price_usd - total_fob_cost_usd

    breakdown_idr = {
        "purchasing_cost_idr": total_purchase_cost_idr,
        "packaging_cost_idr": total_packaging_cost_idr,
        "inland_trucking_idr": inland_trucking_idr,
        "export_declaration_customs_idr": customs_export_clearance_idr,
        "loading_handling_surveyor_idr": handling_surveyor_idr,
        "port_thc_charge_idr": port_handling_thc_idr,
    }

    hs_code = HS_CODE_DATABASE.get(commodity, {}).get("code", "0900.00")

    return {
        "commodity": commodity,
        "hs_code": hs_code,
        "origin": "Indonesia",
        "loading_port": loading_port,
        "volume_kg": volume_kg,
        "net_weight_kg": volume_kg,
        "gross_weight_kg": pack_res["grossWeightKg"],
        "total_units_needed": pack_res["totalUnitsNeeded"],
        "exchange_rate": exchange_rate,
        "fob_price_per_kg": fob_price_per_kg_usd,
        "fob_total_usd": fob_total_price_usd,
        "total_cost_usd": total_fob_cost_usd,
        "profit_usd": profit_usd,
        "margin_percent": profit_margin_percent,
        "breakdown_total": breakdown_idr
    }


def calculate_cif(fob_result, destination_port, freight_usd_per_kg, insurance_rate_pct=0.3):
    """
    Kalkulasi taksiran harga ekspor CIF (Cost, Insurance, and Freight).
    """
    volume_kg = fob_result["volume_kg"]
    fob_total_usd = fob_result["fob_total_usd"]

    ocean_freight_usd = freight_usd_per_kg * volume_kg
    insurance_rate = insurance_rate_pct / 100

    if insurance_rate >= 1.0:
        insurance_rate = 0.99

    cif_total_usd = (fob_total_usd + ocean_freight_usd) / (1.0 - insurance_rate)
    insurance_usd = cif_total_usd * insurance_rate
    cif_price_per_kg = cif_total_usd / volume_kg if volume_kg > 0 else 0.0

    return {
        "commodity": fob_result["commodity"],
        "hs_code": fob_result["hs_code"],
        "origin": fob_result["origin"],
        "loading_port": fob_result["loading_port"],
        "destination_port": destination_port,
        "volume_kg": volume_kg,
        "net_weight_kg": fob_result["net_weight_kg"],
        "gross_weight_kg": fob_result["gross_weight_kg"],
        "total_units_needed": fob_result["total_units_needed"],
        "exchange_rate": fob_result["exchange_rate"],
        "fob_total_usd": fob_result["fob_total_usd"],
        "fob_price_per_kg": fob_result["fob_price_per_kg"],
        "freight_usd_per_kg": freight_usd_per_kg,
        "ocean_freight_usd": ocean_freight_usd,
        "insurance_rate_pct": insurance_rate_pct,
        "insurance_usd": insurance_usd,
        "cif_total_usd": cif_total_usd,
        "cif_price_per_kg": cif_price_per_kg
    }


def calculate_ddp(cif_result, duty_rate_pct, vat_rate_pct, inland_freight_usd, customs_handling_usd):
    """
    Kalkulasi taksiran harga ekspor DDP (Delivered Duty Paid).
    """
    volume_kg = cif_result["volume_kg"]
    cif_total_usd = cif_result["cif_total_usd"]

    import_duty_usd = cif_total_usd * (duty_rate_pct / 100)
    vat_base_usd = cif_total_usd + import_duty_usd
    vat_usd = vat_base_usd * (vat_rate_pct / 100)

    ddp_total_usd = cif_total_usd + import_duty_usd + vat_usd + inland_freight_usd + customs_handling_usd
    ddp_price_per_kg = ddp_total_usd / volume_kg if volume_kg > 0 else 0.0

    return {
        "commodity": cif_result["commodity"],
        "hs_code": cif_result["hs_code"],
        "origin": cif_result["origin"],
        "loading_port": cif_result["loading_port"],
        "destination_port": cif_result["destination_port"],
        "volume_kg": volume_kg,
        "net_weight_kg": cif_result["net_weight_kg"],
        "gross_weight_kg": cif_result["gross_weight_kg"],
        "total_units_needed": cif_result["total_units_needed"],
        "exchange_rate": cif_result["exchange_rate"],
        "fob_total_usd": cif_result["fob_total_usd"],
        "fob_price_per_kg": cif_result["fob_price_per_kg"],
        "ocean_freight_usd": cif_result["ocean_freight_usd"],
        "insurance_usd": cif_result["insurance_usd"],
        "cif_total_usd": cif_total_usd,
        "cif_price_per_kg": cif_result["cif_price_per_kg"],
        "duty_rate_pct": duty_rate_pct,
        "import_duty_usd": import_duty_usd,
        "vat_rate_pct": vat_rate_pct,
        "vat_usd": vat_usd,
        "inland_freight_usd": inland_freight_usd,
        "customs_handling_usd": customs_handling_usd,
        "ddp_total_usd": ddp_total_usd,
        "ddp_price_per_kg": ddp_price_per_kg
    }


def generate_price_trend_data(commodity, exchange_rate=16200):
    """
    Menghasilkan data rentang historis 30 hari untuk visualisasi Streamlit Line Chart.
    """
    benchmark = MARKET_ADVISOR_BENCHMARKS.get(commodity, {"low": 2.20, "high": 4.50})
    buy_price_local_idr = COMMODITY_BUY_PRICES.get(commodity, 35000)
    buy_price_usd = buy_price_local_idr / exchange_rate

    low = benchmark["low"]
    high = benchmark["high"]
    avg = (low + high) / 2

    def seed_string(s):
        h = 0
        for char in s:
            h = ord(char) + ((h << 5) - h)
        return abs(h)

    seed = seed_string(commodity)
    data = []
    today = datetime.date.today()

    for i in range(29, -1, -1):
        date = today - datetime.timedelta(days=i)
        date_str = date.strftime("%b %d")
        t = 29 - i

        # Symmetrical wave fluctuation
        wave = math.sin((t + seed) * 0.35) * 0.3 + math.cos((t + seed) * 0.15) * 0.15
        noise = math.sin(t * 1.8) * 0.04

        global_price = round(avg + (high - low) * 0.3 * wave + noise, 2)
        local_spread = math.cos((t + seed * 1.5) * 0.25) * 0.08
        local_price = round(buy_price_usd + local_spread, 2)

        data.append({
            "Date": date_str,
            "Global FOB Benchmark": max(0.1, global_price),
            "Local Reference Price": max(0.1, local_price)
        })
    return data
