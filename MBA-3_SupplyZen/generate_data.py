"""
Generate reference data for MBA-3: SupplyZen
Supply Chain Resilience Optimization — ElectraTech ($10B consumer electronics)
"""

import numpy as np
import json
import csv
import os

SEED = 42
np.random.seed(SEED)

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


COUNTRIES = {
    "Taiwan": "APAC", "South Korea": "APAC", "China": "APAC",
    "Japan": "APAC", "Vietnam": "APAC", "India": "APAC",
    "Malaysia": "APAC", "Thailand": "APAC", "Philippines": "APAC",
    "Indonesia": "APAC", "Germany": "Europe", "Netherlands": "Europe",
    "France": "Europe", "Poland": "Europe", "Czech Republic": "Europe",
    "USA": "Americas", "Mexico": "Americas", "Brazil": "Americas",
    "Canada": "Americas", "Israel": "MENA",
}

CATEGORIES = [
    "semiconductor", "display", "battery", "memory", "PCB",
    "connector", "sensor", "camera_module", "antenna", "passive_component",
    "mechanical_housing", "thermal_management", "audio", "haptic",
    "power_management", "storage", "wireless_module", "cable_assembly",
]

PRODUCTS = ["smartphone", "tablet", "laptop"]


# ── 1. Suppliers ──────────────────────────────────────────────────────────────
def gen_suppliers():
    print("1. Generating 500 suppliers...")
    d = BASE_DIR
    ensure_dir(d)

    prefixes = [
        "Uni", "Neo", "Pro", "Tech", "Core", "Max", "Star", "Digi",
        "Flex", "Sure", "First", "Prime", "Alpha", "Beta", "Sigma",
        "Delta", "Omni", "Micro", "Nano", "Macro", "Global", "Inter",
    ]
    suffixes = [
        "Chip", "Semi", "Tron", "Link", "Wave", "Tek", "Com", "Corp",
        "Parts", "Elect", "Sys", "Sol", "Fab", "Works", "Ind", "Mfg",
    ]

    countries = list(COUNTRIES.keys())
    country_weights = np.array([
        12, 8, 15, 10, 6, 5, 4, 3, 2, 2,
        5, 3, 3, 2, 2, 7, 4, 2, 3, 2,
    ], dtype=float)
    country_weights /= country_weights.sum()

    rows = []
    used_names = set()
    for i in range(500):
        while True:
            name = f"{np.random.choice(prefixes)}{np.random.choice(suffixes)}"
            if i > 50:
                name += f"-{np.random.randint(1, 999):03d}"
            if name not in used_names:
                used_names.add(name)
                break

        country = np.random.choice(countries, p=country_weights)
        region = COUNTRIES[country]
        tier = int(np.random.choice([1, 2, 3], p=[0.20, 0.40, 0.40]))
        cat = np.random.choice(CATEGORIES)

        reliability = round(np.clip(np.random.normal(0.92, 0.06), 0.70, 0.99), 3)
        lead = int(np.clip(np.random.gamma(3, 10), 5, 120))
        if region == "APAC":
            lead = int(lead * 1.2)

        moq = int(np.random.choice([100, 500, 1000, 5000, 10000]))
        unit_cost = round(np.random.lognormal(1.5, 1.2), 2)
        capacity = int(np.random.choice([5000, 10000, 50000, 100000, 500000, 1000000]))
        defect = round(np.clip(np.random.exponential(0.05), 0.001, 0.5), 4)
        fin_health = round(np.clip(np.random.normal(7, 1.5), 2, 10), 1)
        iso = bool(np.random.random() < (0.9 if tier == 1 else 0.7 if tier == 2 else 0.5))
        dual = bool(np.random.random() < 0.55)

        rows.append({
            "supplier_id": f"S{i+1:04d}",
            "name": name,
            "country": country,
            "region": region,
            "tier": tier,
            "category": cat,
            "reliability_score": reliability,
            "lead_time_days": lead,
            "moq": moq,
            "unit_cost": unit_cost,
            "capacity_per_month": capacity,
            "quality_defect_rate": defect,
            "financial_health_score": fin_health,
            "iso_certified": iso,
            "dual_source_available": dual,
        })

    write_csv(os.path.join(d, "suppliers.csv"), rows, list(rows[0].keys()))
    return rows


# ── 2. Components ─────────────────────────────────────────────────────────────
def gen_components(suppliers):
    print("2. Generating 2000 components...")
    d = BASE_DIR
    ensure_dir(d)

    supplier_by_cat = {}
    for s in suppliers:
        supplier_by_cat.setdefault(s["category"], []).append(s["supplier_id"])

    rows = []
    for i in range(2000):
        cat = np.random.choice(CATEGORIES)
        avail = supplier_by_cat.get(cat, [s["supplier_id"] for s in suppliers[:50]])

        primary = np.random.choice(avail)
        alt = None
        if len(avail) > 1 and np.random.random() < 0.55:
            others = [s for s in avail if s != primary]
            if others:
                alt = np.random.choice(others)

        criticality = np.random.choice(
            ["critical", "important", "standard"], p=[0.15, 0.35, 0.50]
        )
        unit_cost = round(np.random.lognormal(1, 1.3), 2)
        lead = int(np.clip(np.random.gamma(3, 8), 3, 90))
        demand = int(np.random.choice([50000, 100000, 500000, 1000000, 5000000, 10000000]))
        safety = round(np.random.choice([1, 2, 3, 4, 6, 8]), 0)

        used_in = np.random.choice(
            ["smartphone", "tablet", "laptop", "smartphone|tablet",
             "smartphone|laptop", "tablet|laptop", "smartphone|tablet|laptop"],
            p=[0.25, 0.15, 0.15, 0.15, 0.10, 0.05, 0.15],
        )

        rows.append({
            "component_id": f"C{i+1:05d}",
            "name": f"{cat.replace('_', ' ').title()} Part {i+1}",
            "category": cat,
            "primary_supplier_id": primary,
            "alt_supplier_id": alt if alt else "",
            "unit_cost": unit_cost,
            "criticality": criticality,
            "lead_time_days": lead,
            "annual_demand": demand,
            "safety_stock_weeks": int(safety),
            "used_in": used_in,
            "single_source": alt is None,
        })

    write_csv(os.path.join(d, "components.csv"), rows, list(rows[0].keys()))
    return rows


# ── 3. Bill of Materials ──────────────────────────────────────────────────────
def gen_bom(components):
    print("3. Generating bill of materials...")
    d = BASE_DIR
    ensure_dir(d)

    volumes = {"smartphone": 60000000, "tablet": 20000000, "laptop": 20000000}
    rows = []
    for comp in components:
        prods = comp["used_in"].split("|")
        for prod in prods:
            qty = int(np.random.choice([1, 1, 1, 2, 2, 3, 4]))
            rows.append({
                "product": prod,
                "component_id": comp["component_id"],
                "quantity_per_unit": qty,
                "annual_volume": volumes.get(prod, 20000000),
            })

    write_csv(os.path.join(d, "bom.csv"), rows, list(rows[0].keys()))


# ── 4. Logistics Routes ──────────────────────────────────────────────────────
def gen_logistics():
    print("4. Generating logistics routes...")
    d = BASE_DIR
    ensure_dir(d)

    origins = list(COUNTRIES.keys())
    destinations = ["USA", "Germany", "Japan", "Brazil", "India", "China"]
    modes = ["sea", "air", "rail", "truck"]
    mode_params = {
        "sea": (30, 0.05, 0.90),
        "air": (5, 0.80, 0.97),
        "rail": (18, 0.12, 0.93),
        "truck": (7, 0.25, 0.95),
    }

    rows = []
    for i in range(100):
        origin = np.random.choice(origins)
        dest = np.random.choice(destinations)
        mode = np.random.choice(modes, p=[0.45, 0.25, 0.15, 0.15])
        base_transit, base_cost, base_rel = mode_params[mode]

        transit = int(base_transit * np.random.uniform(0.7, 1.5))
        cost = round(base_cost * np.random.uniform(0.6, 2.0), 3)
        reliability = round(np.clip(base_rel + np.random.normal(0, 0.03), 0.70, 0.99), 3)
        capacity = int(np.random.choice([1000, 5000, 10000, 50000, 100000]))

        disrupted = bool(np.random.random() < 0.12)
        mult = round(np.random.uniform(1.5, 4.0), 1) if disrupted else 1.0

        rows.append({
            "route_id": f"R{i+1:03d}",
            "origin_country": origin,
            "destination_country": dest,
            "mode": mode,
            "transit_days": transit,
            "cost_per_kg": cost,
            "reliability_pct": round(reliability * 100, 1),
            "capacity_per_month": capacity,
            "current_disruption": disrupted,
            "disruption_cost_multiplier": mult,
        })

    write_csv(os.path.join(d, "logistics.csv"), rows, list(rows[0].keys()))


# ── 5. Disruptions ───────────────────────────────────────────────────────────
def gen_disruptions(suppliers):
    print("5. Generating disruption scenarios...")
    d = BASE_DIR
    ensure_dir(d)

    # Pick supplier IDs by country/category for realistic disruptions
    taiwan_semis = [s["supplier_id"] for s in suppliers
                    if s["country"] == "Taiwan" and s["category"] == "semiconductor"][:30]
    china_suppliers = [s["supplier_id"] for s in suppliers if s["country"] == "China"][:50]
    sea_route_countries = ["China", "Vietnam", "India", "Malaysia", "Thailand"]
    sea_affected = [s["supplier_id"] for s in suppliers if s["country"] in sea_route_countries][:80]
    critical_single = [s["supplier_id"] for s in suppliers if s["tier"] == 1][:5]

    disruptions = {
        "active_disruptions": [
            {
                "id": "D001",
                "name": "Semiconductor Shortage",
                "type": "supply_constraint",
                "status": "ongoing",
                "start_date": "2024-03-01",
                "expected_resolution": "2025-06-30",
                "probability": 1.0,
                "affected_supplier_ids": taiwan_semis[:20],
                "components_affected_pct": 40,
                "cost_impact_annual_m": 850,
                "revenue_at_risk_m": 2000,
                "lead_time_increase_days": 45,
            },
            {
                "id": "D002",
                "name": "Red Sea Shipping Disruption",
                "type": "logistics",
                "status": "ongoing",
                "start_date": "2024-01-15",
                "expected_resolution": "2025-03-31",
                "probability": 1.0,
                "affected_supplier_ids": sea_affected[:40],
                "components_affected_pct": 25,
                "cost_impact_annual_m": 320,
                "revenue_at_risk_m": 500,
                "shipping_cost_increase_pct": 300,
                "transit_time_increase_pct": 40,
            },
            {
                "id": "D003",
                "name": "Critical Supplier Factory Fire",
                "type": "catastrophic",
                "status": "recovery",
                "start_date": "2024-08-10",
                "expected_resolution": "2025-02-10",
                "probability": 1.0,
                "affected_supplier_ids": critical_single[:2],
                "components_affected_pct": 5,
                "cost_impact_annual_m": 180,
                "revenue_at_risk_m": 400,
                "recovery_months": 6,
            },
            {
                "id": "D004",
                "name": "Tariff Uncertainty (Country X)",
                "type": "geopolitical",
                "status": "pending",
                "probability": 0.50,
                "affected_supplier_ids": china_suppliers[:40],
                "components_affected_pct": 30,
                "tariff_rate_pct": 25,
                "cost_impact_annual_m": 600,
                "revenue_at_risk_m": 0,
            },
        ],
        "scenario_disruptions": [
            {
                "id": "S001",
                "name": "Major Earthquake (Taiwan)",
                "type": "natural_disaster",
                "probability": 0.08,
                "affected_supplier_ids": taiwan_semis,
                "cost_impact_annual_m": 1500,
                "recovery_months": 9,
            },
            {
                "id": "S002",
                "name": "Pandemic Resurgence",
                "type": "pandemic",
                "probability": 0.15,
                "affected_regions": ["APAC"],
                "cost_impact_annual_m": 1200,
                "recovery_months": 12,
            },
            {
                "id": "S003",
                "name": "Cyber Attack on Logistics",
                "type": "cyber",
                "probability": 0.20,
                "cost_impact_annual_m": 400,
                "recovery_months": 2,
            },
            {
                "id": "S004",
                "name": "US-China Trade War Escalation",
                "type": "geopolitical",
                "probability": 0.30,
                "affected_supplier_ids": china_suppliers,
                "tariff_rate_pct": 50,
                "cost_impact_annual_m": 1800,
            },
            {
                "id": "S005",
                "name": "Key Raw Material Shortage (Lithium)",
                "type": "commodity",
                "probability": 0.25,
                "cost_impact_annual_m": 500,
                "recovery_months": 18,
            },
            {
                "id": "S006",
                "name": "Port Congestion (LA/Long Beach)",
                "type": "logistics",
                "probability": 0.20,
                "cost_impact_annual_m": 350,
                "recovery_months": 4,
            },
        ],
    }

    write_json(os.path.join(d, "disruptions.json"), disruptions)


# ── 6. Manufacturing Facilities ───────────────────────────────────────────────
def gen_manufacturing():
    print("6. Generating manufacturing facilities...")
    d = BASE_DIR
    ensure_dir(d)

    facilities = [
        ("F01", "ShenZhen Assembly", "China", "smartphone|tablet", 5000000, 32, 0.97, 14, 0.35),
        ("F02", "DongGuan Electronics", "China", "smartphone|laptop", 4000000, 35, 0.96, 16, 0.38),
        ("F03", "Ho Chi Minh Plant", "Vietnam", "smartphone|tablet", 3000000, 30, 0.94, 18, 0.42),
        ("F04", "Penang Facility", "Malaysia", "tablet|laptop", 2000000, 38, 0.95, 20, 0.50),
        ("F05", "Chennai Works", "India", "smartphone", 2500000, 28, 0.93, 22, 0.45),
        ("F06", "Guadalajara Plant", "Mexico", "laptop", 1500000, 45, 0.96, 10, 0.65),
        ("F07", "Wroclaw Assembly", "Poland", "laptop", 1000000, 50, 0.97, 8, 0.80),
        ("F08", "Austin Facility", "USA", "laptop", 800000, 55, 0.98, 5, 1.00),
    ]

    fields = [
        "facility_id", "name", "country", "products",
        "capacity_per_month", "cost_per_unit", "quality_score",
        "lead_time_days", "labor_cost_index",
    ]
    rows = [dict(zip(fields, f)) for f in facilities]
    write_csv(os.path.join(d, "manufacturing.csv"), rows, fields)


# ── 7. Distribution Centers ──────────────────────────────────────────────────
def gen_distribution():
    print("7. Generating 50 distribution centers...")
    d = BASE_DIR
    ensure_dir(d)

    cities = [
        ("Los Angeles", "USA", "Americas"), ("Dallas", "USA", "Americas"),
        ("Chicago", "USA", "Americas"), ("New York", "USA", "Americas"),
        ("Atlanta", "USA", "Americas"), ("Miami", "USA", "Americas"),
        ("Seattle", "USA", "Americas"), ("Toronto", "Canada", "Americas"),
        ("Sao Paulo", "Brazil", "Americas"), ("Mexico City", "Mexico", "Americas"),
        ("London", "UK", "Europe"), ("Amsterdam", "Netherlands", "Europe"),
        ("Frankfurt", "Germany", "Europe"), ("Paris", "France", "Europe"),
        ("Milan", "Italy", "Europe"), ("Madrid", "Spain", "Europe"),
        ("Warsaw", "Poland", "Europe"), ("Stockholm", "Sweden", "Europe"),
        ("Dublin", "Ireland", "Europe"), ("Prague", "Czech Republic", "Europe"),
        ("Shanghai", "China", "APAC"), ("Shenzhen", "China", "APAC"),
        ("Beijing", "China", "APAC"), ("Tokyo", "Japan", "APAC"),
        ("Osaka", "Japan", "APAC"), ("Seoul", "South Korea", "APAC"),
        ("Taipei", "Taiwan", "APAC"), ("Singapore", "Singapore", "APAC"),
        ("Hong Kong", "Hong Kong", "APAC"), ("Mumbai", "India", "APAC"),
        ("Delhi", "India", "APAC"), ("Bangkok", "Thailand", "APAC"),
        ("Jakarta", "Indonesia", "APAC"), ("Sydney", "Australia", "APAC"),
        ("Melbourne", "Australia", "APAC"), ("Auckland", "New Zealand", "APAC"),
        ("Dubai", "UAE", "MENA"), ("Riyadh", "Saudi Arabia", "MENA"),
        ("Istanbul", "Turkey", "MENA"), ("Cairo", "Egypt", "MENA"),
        ("Johannesburg", "South Africa", "Africa"),
        ("Lagos", "Nigeria", "Africa"),
        ("Nairobi", "Kenya", "Africa"),
        ("Lima", "Peru", "Americas"),
        ("Bogota", "Colombia", "Americas"),
        ("Santiago", "Chile", "Americas"),
        ("Buenos Aires", "Argentina", "Americas"),
        ("Helsinki", "Finland", "Europe"),
        ("Bucharest", "Romania", "Europe"),
        ("Lisbon", "Portugal", "Europe"),
    ]

    rows = []
    for i, (city, country, region) in enumerate(cities):
        capacity = int(np.random.choice([50000, 100000, 250000, 500000, 1000000]))
        util = round(np.random.uniform(0.55, 0.95), 2)
        cost = round(np.random.uniform(1.5, 8.0), 2)

        rows.append({
            "dc_id": f"DC{i+1:03d}",
            "city": city,
            "country": country,
            "region": region,
            "capacity_units": capacity,
            "current_utilization_pct": round(util * 100, 1),
            "cost_per_unit": cost,
            "covers_markets": region,
        })

    write_csv(os.path.join(d, "distribution.csv"), rows, list(rows[0].keys()))


# ── 8. Demand Forecast ────────────────────────────────────────────────────────
def gen_demand_forecast():
    print("8. Generating 24-month demand forecast...")
    d = BASE_DIR
    ensure_dir(d)

    base_monthly = {"smartphone": 5000000, "tablet": 1666667, "laptop": 1666667}
    regions = ["Americas", "Europe", "APAC", "MENA", "Africa"]
    region_share = {"Americas": 0.30, "Europe": 0.25, "APAC": 0.35, "MENA": 0.07, "Africa": 0.03}

    rows = []
    for month_offset in range(24):
        month_str = f"2025-{(month_offset % 12) + 1:02d}"
        # Seasonality: boost in Q4 (months 10-12)
        m = (month_offset % 12) + 1
        seasonal = 1.0 + 0.15 * (m >= 10) + 0.05 * (m >= 7) - 0.10 * (m <= 2)
        # Slight growth trend
        trend = 1.0 + 0.005 * month_offset

        for prod, base in base_monthly.items():
            for reg, share in region_share.items():
                forecast = int(base * share * seasonal * trend)
                low = int(forecast * np.random.uniform(0.85, 0.92))
                high = int(forecast * np.random.uniform(1.08, 1.18))
                rows.append({
                    "month": month_str,
                    "product": prod,
                    "region": reg,
                    "forecast_units": forecast,
                    "confidence_low": low,
                    "confidence_high": high,
                })

    write_csv(os.path.join(d, "demand_forecast.csv"), rows, list(rows[0].keys()))


# ── 9. Cost Structure ─────────────────────────────────────────────────────────
def gen_cost_structure():
    print("9. Generating cost structure...")
    d = BASE_DIR
    ensure_dir(d)

    cost_structure = {
        "currency": "USD",
        "procurement_costs": {
            "semiconductor_pct_of_bom": 35,
            "display_pct_of_bom": 20,
            "battery_pct_of_bom": 10,
            "memory_pct_of_bom": 12,
            "other_pct_of_bom": 23,
            "total_procurement_b": 5.2,
        },
        "manufacturing_costs": {
            "direct_labor_pct": 15,
            "overhead_pct": 8,
            "quality_control_pct": 3,
            "total_manufacturing_b": 1.8,
        },
        "logistics_costs": {
            "inbound_freight_b": 0.4,
            "outbound_freight_b": 0.3,
            "warehousing_b": 0.25,
            "customs_duties_b": 0.15,
            "total_logistics_b": 1.1,
        },
        "inventory_holding": {
            "cost_of_capital_pct": 8,
            "storage_pct": 3,
            "insurance_pct": 1,
            "obsolescence_pct": 2,
            "total_holding_cost_pct": 14,
        },
        "tariff_rates_by_country": {
            "China": 7.5,
            "Taiwan": 3.0,
            "South Korea": 2.5,
            "Vietnam": 5.0,
            "India": 10.0,
            "Mexico": 0,
            "USA": 0,
        },
        "targets": {
            "service_level_pct": 95,
            "max_lead_time_weeks": 4,
            "max_defect_rate_pct": 0.1,
            "target_inventory_weeks": 8,
            "current_inventory_weeks": 3,
        },
        "unit_cost_by_product": {
            "smartphone": {"bom": 180, "manufacturing": 22, "logistics": 8, "total": 210},
            "tablet": {"bom": 220, "manufacturing": 25, "logistics": 10, "total": 255},
            "laptop": {"bom": 380, "manufacturing": 35, "logistics": 15, "total": 430},
        },
    }

    write_json(os.path.join(d, "cost_structure.json"), cost_structure)


# ── 10. Historical Financial Impact ───────────────────────────────────────────
def gen_financial_impact():
    print("10. Generating historical disruption financial impact...")
    d = BASE_DIR
    ensure_dir(d)

    quarters = []
    for year in [2022, 2023, 2024]:
        for q in range(1, 5):
            if year == 2024 and q > 3:
                break
            disruption_types = ["semiconductor_shortage", "logistics_delay",
                                "supplier_quality", "demand_spike", "tariff_change", "none"]
            dtype = np.random.choice(disruption_types, p=[0.25, 0.20, 0.10, 0.10, 0.10, 0.25])
            if dtype == "none":
                rev_impact = 0
                cost_impact = 0
            else:
                rev_impact = -round(np.random.uniform(20, 300), 1)
                cost_impact = round(np.random.uniform(10, 150), 1)

            quarters.append({
                "quarter": f"{year}-Q{q}",
                "disruption_type": dtype,
                "revenue_impact_m": rev_impact,
                "cost_impact_m": cost_impact,
                "margin_impact_bps": int((rev_impact - cost_impact) / 100 * -1),
                "units_delayed": int(abs(rev_impact) * 10000) if dtype != "none" else 0,
            })

    write_csv(os.path.join(d, "financial_impact.csv"), quarters, list(quarters[0].keys()))


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Generating SupplyZen reference data...")
    print("=" * 50)

    suppliers = gen_suppliers()
    components = gen_components(suppliers)
    gen_bom(components)
    gen_logistics()
    gen_disruptions(suppliers)
    gen_manufacturing()
    gen_distribution()
    gen_demand_forecast()
    gen_cost_structure()
    gen_financial_impact()

    print(f"\nData generated in: {BASE_DIR}")
    print("  - suppliers.csv: 500 suppliers across 20 countries")
    print("  - components.csv: 2000 components")
    print("  - bom.csv: Bill of materials (3 products)")
    print("  - logistics.csv: 100 shipping routes")
    print("  - disruptions.json: 4 active + 6 scenario disruptions")
    print("  - manufacturing.csv: 8 contract manufacturers")
    print("  - distribution.csv: 50 distribution centers")
    print("  - demand_forecast.csv: 24-month forecast")
    print("  - cost_structure.json: Detailed cost breakdown")
    print("  - financial_impact.csv: Historical disruption impact")
    print("\nDone!")


if __name__ == "__main__":
    main()
