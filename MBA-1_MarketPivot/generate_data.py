"""
Generate reference data for MBA-1: MarketPivot
Strategic Repositioning in the Age of AI Disruption — MediCore Health
"""

import numpy as np
import json
import csv
import os
from datetime import datetime, timedelta

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


# ── 1. Company Financials ────────────────────────────────────────────────────
def gen_company_financials():
    print("1. Generating company financials...")
    d = os.path.join(BASE_DIR, "company")
    ensure_dir(d)

    years = [2020, 2021, 2022, 2023, 2024]
    revenues = [2400, 2350, 2250, 2100, 2000]  # $M, declining
    ehr_pcts = [0.58, 0.59, 0.60, 0.60, 0.60]
    billing_pcts = [0.27, 0.26, 0.25, 0.25, 0.25]

    pnl = []
    for i, yr in enumerate(years):
        rev = revenues[i]
        ehr = rev * ehr_pcts[i]
        billing = rev * billing_pcts[i]
        telehealth = rev - ehr - billing
        cogs = rev * (0.38 + 0.005 * i)  # margin pressure
        gross = rev - cogs
        rd = rev * (0.07 + 0.002 * i)
        sm = rev * (0.18 - 0.005 * i)
        ga = rev * 0.12
        opex = rd + sm + ga
        ebitda = gross - opex
        da = rev * 0.04
        ebit = ebitda - da
        interest = 40 + 2 * i  # rising interest
        ebt = ebit - interest
        tax = max(ebt * 0.22, 0)
        net_income = ebt - tax

        pnl.append({
            "year": yr,
            "revenue": round(rev, 1),
            "revenue_ehr": round(ehr, 1),
            "revenue_billing": round(billing, 1),
            "revenue_telehealth": round(telehealth, 1),
            "cogs": round(cogs, 1),
            "gross_profit": round(gross, 1),
            "gross_margin_pct": round(gross / rev * 100, 1),
            "rd_expense": round(rd, 1),
            "sm_expense": round(sm, 1),
            "ga_expense": round(ga, 1),
            "total_opex": round(opex, 1),
            "ebitda": round(ebitda, 1),
            "ebitda_margin_pct": round(ebitda / rev * 100, 1),
            "depreciation_amortization": round(da, 1),
            "ebit": round(ebit, 1),
            "interest_expense": round(interest, 1),
            "ebt": round(ebt, 1),
            "tax": round(tax, 1),
            "net_income": round(net_income, 1),
        })

    balance_sheet = {
        "as_of": "2024-12-31",
        "cash_and_equivalents": 500,
        "accounts_receivable": 340,
        "total_current_assets": 950,
        "pp_and_e_net": 420,
        "intangible_assets": 1200,
        "goodwill": 800,
        "total_assets": 3370,
        "accounts_payable": 180,
        "current_debt": 150,
        "total_current_liabilities": 480,
        "long_term_debt": 650,
        "total_debt": 800,
        "total_liabilities": 1580,
        "shareholders_equity": 1790,
        "total_liabilities_and_equity": 3370,
    }

    cash_flow = {
        "year": 2024,
        "operating_cash_flow": 310,
        "capex": -120,
        "free_cash_flow": 190,
        "acquisitions": -50,
        "debt_repayment": -80,
        "dividends": 0,
        "share_repurchases": -60,
        "net_change_in_cash": 0,
    }

    key_metrics = {
        "employees": 8200,
        "customer_count": 1850,
        "hospital_customers": 1200,
        "clinic_customers": 650,
        "churn_rate_pct": 15.0,
        "churn_rate_prior_year_pct": 10.0,
        "churn_rate_2_years_ago_pct": 5.0,
        "nps_score": 12,
        "nps_prior_year": 28,
        "nps_2_years_ago": 45,
        "arr": 1950,
        "avg_contract_value_k": 1054,
        "customer_lifetime_months": 72,
        "rd_as_pct_of_revenue": 8.0,
    }

    write_json(os.path.join(d, "financials.json"), {
        "company": "MediCore Health",
        "currency": "USD millions",
        "income_statement": pnl,
        "balance_sheet": balance_sheet,
        "cash_flow": cash_flow,
        "key_metrics": key_metrics,
    })


# ── 2. Customer Base ──────────────────────────────────────────────────────────
def gen_customers():
    print("2. Generating customer base...")
    d = os.path.join(BASE_DIR, "company")
    ensure_dir(d)

    hospital_prefixes = [
        "Mercy", "St. Luke's", "Memorial", "Regional", "University",
        "Providence", "Good Samaritan", "Sacred Heart", "Valley",
        "Mount Sinai", "Presbyterian", "Baptist", "Methodist", "Trinity",
        "Sunrise", "Lakewood", "Riverside", "Cedar", "Northside", "Southgate",
    ]
    hospital_suffixes = [
        "Hospital", "Medical Center", "Health System", "Clinic",
        "Healthcare", "Medical Group",
    ]
    types = ["academic", "community", "rural", "specialty", "integrated_system"]
    type_weights = [0.15, 0.40, 0.20, 0.10, 0.15]
    regions = ["Northeast", "Southeast", "Midwest", "Southwest", "West", "Northwest"]
    products = ["EHR", "Billing", "Telehealth"]

    rows = []
    used_names = set()
    for i in range(200):
        while True:
            name = f"{np.random.choice(hospital_prefixes)} {np.random.choice(hospital_suffixes)}"
            if i > 0:
                name += f" {np.random.choice(['of', 'at', '-'])} {np.random.choice(['Springfield','Riverside','Oakland','Fairview','Lakewood','Summit','Valley','Metro','Central','North'])}"
            if name not in used_names:
                used_names.add(name)
                break

        htype = np.random.choice(types, p=type_weights)
        beds = int(np.random.choice([50, 100, 150, 250, 400, 600, 800, 1200]) + np.random.randint(-20, 20))
        beds = max(25, beds)

        n_products = np.random.choice([1, 2, 3], p=[0.25, 0.45, 0.30])
        chosen = list(np.random.choice(products, size=n_products, replace=False))

        base_acv = beds * np.random.uniform(0.5, 1.5) * 1000
        acv = round(base_acv + len(chosen) * 50000, -3)

        start_yr = np.random.randint(2010, 2023)
        renewal_month = np.random.randint(1, 13)
        renewal = f"2025-{renewal_month:02d}-01"

        sat = round(np.clip(np.random.normal(6.5, 1.8), 1, 10), 1)
        if sat < 5:
            risk = "high"
        elif sat < 7:
            risk = "medium"
        else:
            risk = "low"

        rows.append({
            "hospital_name": name,
            "type": htype,
            "beds": beds,
            "annual_contract_value": int(acv),
            "contract_start_year": start_yr,
            "renewal_date": renewal,
            "products_used": "|".join(chosen),
            "satisfaction_score": sat,
            "churn_risk": risk,
            "region": np.random.choice(regions),
        })

    write_csv(os.path.join(d, "customers.csv"), rows, list(rows[0].keys()))


# ── 3. Competitor Landscape ───────────────────────────────────────────────────
def gen_competitors():
    print("3. Generating competitor landscape...")
    d = os.path.join(BASE_DIR, "market")
    ensure_dir(d)

    comps = [
        ("NovaCare AI", "AI-native startup", 25, 180, 120, "AI-powered EHR", 9.2, 0.5, "usage-based", 2021),
        ("HealthBot Labs", "AI-native startup", 15, 220, 85, "Voice documentation", 8.8, 0.3, "subscription", 2020),
        ("ClinicalMind", "AI-native startup", 40, 150, 200, "Clinical decision support", 9.0, 0.8, "per-provider", 2019),
        ("MedScribe AI", "AI-native startup", 10, 300, 50, "Ambient listening", 8.5, 0.2, "per-encounter", 2022),
        ("AutoCode Health", "AI-native startup", 30, 160, 150, "Automated coding/billing", 8.7, 0.6, "per-claim", 2020),
        ("Google Health", "tech giant", 500, 40, 0, "Care Studio / FHIR platform", 9.5, 3.0, "platform fee", 2018),
        ("Microsoft Nuance", "tech giant", 1800, 15, 0, "DAX Copilot", 9.3, 8.0, "per-provider", 2016),
        ("Amazon Clinic", "tech giant", 200, 80, 0, "Virtual care + AWS Health", 8.0, 1.5, "transaction", 2022),
        ("Oracle Health (Cerner)", "traditional", 5800, 3, 0, "Millennium EHR", 6.0, 22.0, "license+maintenance", 2005),
        ("Epic Systems", "traditional", 4200, 8, 0, "Epic EHR suite", 7.5, 30.0, "license", 1998),
        ("Veeva Systems", "traditional", 2400, 12, 0, "Veeva CRM + Vault", 6.5, 5.0, "subscription", 2007),
        ("Athenahealth", "traditional", 1600, 6, 0, "Cloud-based EHR", 7.0, 6.0, "per-encounter", 2004),
        ("NextGen Healthcare", "traditional", 600, 2, 0, "Ambulatory EHR", 5.5, 2.5, "subscription", 2001),
        ("DrFirst", "niche", 150, 25, 80, "e-Prescribing + AI", 7.5, 1.0, "subscription", 2000),
        ("Innovaccer", "AI-native startup", 120, 90, 400, "Health data platform", 8.2, 1.5, "platform", 2014),
    ]

    fields = [
        "company_name", "type", "revenue_m", "growth_rate_pct",
        "funding_m", "key_product", "ai_capability_score",
        "market_share_pct", "pricing_model", "year_founded",
    ]
    rows = []
    for c in comps:
        rows.append(dict(zip(fields, c)))

    write_csv(os.path.join(d, "competitors.csv"), rows, fields)


# ── 4. Industry Benchmarks ───────────────────────────────────────────────────
def gen_benchmarks():
    print("4. Generating industry benchmarks...")
    d = os.path.join(BASE_DIR, "market")
    ensure_dir(d)

    benchmarks = {
        "healthcare_it_market": {
            "total_market_size_b": 340,
            "growth_rate_pct": 13.4,
            "ai_in_healthcare_market_b": 21,
            "ai_healthcare_cagr_pct": 38.0,
        },
        "margin_profiles": {
            "ehr_gross_margin_pct": {"low": 55, "median": 62, "high": 72},
            "ehr_ebitda_margin_pct": {"low": 12, "median": 20, "high": 30},
            "saas_gross_margin_pct": {"low": 65, "median": 75, "high": 85},
            "saas_ebitda_margin_pct": {"low": -10, "median": 15, "high": 35},
        },
        "rd_spend": {
            "traditional_healthit_pct": 8,
            "ai_native_startup_pct": 35,
            "tech_giant_healthit_pct": 15,
            "industry_recommended_pct": 15,
        },
        "customer_metrics": {
            "nps_top_quartile": 50,
            "nps_median": 30,
            "nps_bottom_quartile": 10,
            "churn_rate_top_quartile_pct": 3,
            "churn_rate_median_pct": 8,
            "churn_rate_bottom_quartile_pct": 15,
        },
        "valuation_multiples": {
            "ev_revenue_traditional": {"low": 3, "median": 5, "high": 8},
            "ev_revenue_ai_native": {"low": 10, "median": 20, "high": 40},
            "ev_ebitda_traditional": {"low": 12, "median": 18, "high": 25},
        },
        "digital_health_funding_b": {
            "2020": 14.7,
            "2021": 29.1,
            "2022": 15.3,
            "2023": 10.7,
            "2024": 12.2,
        },
        "ai_adoption_in_hospitals_pct": {
            "2020": 12,
            "2021": 18,
            "2022": 28,
            "2023": 38,
            "2024": 50,
        },
    }

    write_json(os.path.join(d, "industry_benchmarks.json"), benchmarks)


# ── 5. Market Sizing ─────────────────────────────────────────────────────────
def gen_market_sizing():
    print("5. Generating market sizing data...")
    d = os.path.join(BASE_DIR, "market")
    ensure_dir(d)

    segments = [
        ("Electronic Health Records", 38.0, 50.5, 9.9, 0.62),
        ("Medical Billing / RCM", 22.0, 30.0, 10.8, 0.55),
        ("Telehealth Platforms", 12.0, 25.0, 27.8, 0.35),
        ("Clinical Decision Support (AI)", 3.5, 12.0, 50.8, 0.15),
        ("AI Medical Coding", 1.2, 5.5, 66.0, 0.08),
        ("Voice / Ambient Documentation", 0.8, 4.5, 78.0, 0.05),
        ("Interoperability / FHIR", 4.0, 9.0, 30.8, 0.20),
        ("Patient Engagement", 8.0, 14.0, 20.5, 0.40),
        ("Population Health Management", 6.5, 12.0, 22.7, 0.30),
        ("Healthcare Data Analytics", 15.0, 30.0, 26.0, 0.25),
    ]

    fields = ["segment", "tam_2024_b", "tam_2027_projected_b", "cagr_pct", "penetration_rate"]
    rows = [dict(zip(fields, s)) for s in segments]
    write_csv(os.path.join(d, "market_sizing.csv"), rows, fields)


# ── 6. Acquisition Targets ───────────────────────────────────────────────────
def gen_acquisition_targets():
    print("6. Generating acquisition targets...")
    d = os.path.join(BASE_DIR, "acquisitions")
    ensure_dir(d)

    targets = [
        ("NovaCare AI", "AI-powered EHR", 25, 180, 120, 120, 500, "LLM clinical copilot", 45, 20),
        ("HealthBot Labs", "Voice documentation", 15, 220, 80, 85, 300, "Ambient listening AI", 30, 25),
        ("MedScribe AI", "Ambient scribe", 10, 300, 55, 50, 200, "Real-time transcription", 25, 30),
        ("AutoCode Health", "AI medical coding", 30, 160, 150, 150, 350, "NLP coding engine", 60, 18),
        ("CareGraph", "Knowledge graph", 8, 120, 60, 45, 180, "Clinical knowledge graph", 20, 22),
        ("PredictHealth", "Predictive analytics", 18, 100, 90, 80, 250, "ML risk prediction", 40, 15),
        ("DataBridge Health", "Interoperability", 22, 80, 100, 70, 220, "FHIR middleware", 55, 12),
        ("VirtualMD", "AI triage", 12, 140, 65, 60, 180, "Symptom checker AI", 35, 20),
        ("RxIntel", "Drug interaction AI", 5, 90, 35, 25, 100, "Pharmacogenomics", 15, 18),
        ("PopHealthAI", "Population health", 20, 70, 95, 90, 280, "Risk stratification ML", 50, 14),
    ]

    fields = [
        "company_name", "product_focus", "revenue_m", "growth_rate_pct",
        "employees", "funding_raised_m", "last_valuation_m",
        "key_technology", "customer_count", "asking_price_revenue_multiple",
    ]
    rows = [dict(zip(fields, t)) for t in targets]
    write_csv(os.path.join(d, "targets.csv"), rows, fields)


# ── 7. Precedent Deals ───────────────────────────────────────────────────────
def gen_precedent_deals():
    print("7. Generating precedent M&A deals...")
    d = os.path.join(BASE_DIR, "acquisitions")
    ensure_dir(d)

    deals = [
        ("Microsoft", "Nuance Communications", "2022-03-04", 19700, 1800, 10.9, 65.0, "cash", "AI clinical documentation"),
        ("Oracle", "Cerner", "2022-06-08", 28300, 5800, 4.9, 22.0, "cash", "EHR market entry"),
        ("UnitedHealth", "Change Healthcare", "2022-10-03", 13000, 3400, 3.8, 18.5, "cash", "Claims processing + data"),
        ("Amazon", "One Medical", "2023-02-22", 3900, 600, 6.5, 0, "cash", "Primary care platform"),
        ("Google/Alphabet", "Fitbit", "2021-01-14", 2100, 1400, 1.5, 0, "cash", "Health wearables data"),
        ("Veeva Systems", "Crossix", "2021-06-01", 430, 80, 5.4, 28.0, "cash", "Healthcare data analytics"),
        ("IQVIA", "E-Clinical Works (stake)", "2023-09-15", 800, 550, 1.5, 8.0, "mixed", "Ambulatory EHR data"),
        ("Thoma Bravo", "Athenahealth", "2022-01-06", 17000, 1600, 10.6, 55.0, "LBO", "Cloud EHR consolidation"),
    ]

    fields = [
        "acquirer", "target", "date", "deal_value_m",
        "target_revenue_m", "revenue_multiple", "ebitda_multiple",
        "deal_type", "strategic_rationale",
    ]
    rows = [dict(zip(fields, d_)) for d_ in deals]
    write_csv(os.path.join(d, "precedent_deals.csv"), rows, fields)


# ── 8. Debt Schedule ─────────────────────────────────────────────────────────
def gen_debt_schedule():
    print("8. Generating debt schedule...")
    d = os.path.join(BASE_DIR, "financial")
    ensure_dir(d)

    tranches = [
        ("Term Loan A", 300, 5.25, "2026-06-30", "term_loan"),
        ("Term Loan B", 200, 6.00, "2027-03-31", "term_loan"),
        ("Senior Notes 2027", 150, 4.75, "2027-09-15", "bonds"),
        ("Revolving Credit", 100, 5.50, "2026-12-31", "revolver"),
        ("Convertible Notes", 50, 3.50, "2028-06-30", "convertible"),
    ]

    fields = ["tranche", "principal_m", "interest_rate_pct", "maturity_date", "type"]
    rows = [dict(zip(fields, t)) for t in tranches]
    write_csv(os.path.join(d, "debt_schedule.csv"), rows, fields)


# ── 9. Scenario Assumptions ──────────────────────────────────────────────────
def gen_scenario_assumptions():
    print("9. Generating scenario assumptions...")
    d = os.path.join(BASE_DIR, "financial")
    ensure_dir(d)

    scenarios = {
        "bear": {
            "description": "AI disruption accelerates, customer churn worsens",
            "revenue_growth_pct": {"year1": -8, "year2": -12, "year3": -15},
            "ebitda_margin_pct": {"year1": 15, "year2": 10, "year3": 5},
            "churn_rate_pct": {"year1": 18, "year2": 22, "year3": 25},
            "rd_spend_pct": 8,
            "ai_investment_m": 50,
            "capex_m": 100,
            "customer_acquisition_m": 30,
            "probability_pct": 25,
        },
        "base": {
            "description": "Moderate AI pivot, stabilize churn, gradual recovery",
            "revenue_growth_pct": {"year1": -3, "year2": 2, "year3": 8},
            "ebitda_margin_pct": {"year1": 16, "year2": 18, "year3": 22},
            "churn_rate_pct": {"year1": 12, "year2": 9, "year3": 7},
            "rd_spend_pct": 14,
            "ai_investment_m": 150,
            "capex_m": 120,
            "customer_acquisition_m": 80,
            "probability_pct": 50,
        },
        "bull": {
            "description": "Successful AI transformation, become platform leader",
            "revenue_growth_pct": {"year1": 0, "year2": 10, "year3": 20},
            "ebitda_margin_pct": {"year1": 14, "year2": 20, "year3": 28},
            "churn_rate_pct": {"year1": 10, "year2": 6, "year3": 4},
            "rd_spend_pct": 18,
            "ai_investment_m": 250,
            "capex_m": 150,
            "customer_acquisition_m": 120,
            "probability_pct": 25,
        },
        "common_assumptions": {
            "tax_rate_pct": 22,
            "wacc_pct": 10,
            "terminal_growth_pct": 3,
            "depreciation_pct_of_revenue": 4,
            "working_capital_pct_of_revenue": 10,
        },
    }

    write_json(os.path.join(d, "scenario_assumptions.json"), scenarios)


# ── 10. Talent Market Rates ──────────────────────────────────────────────────
def gen_talent_data():
    print("10. Generating talent market rates...")
    d = os.path.join(BASE_DIR, "talent")
    ensure_dir(d)

    roles = [
        ("AI/ML Engineer", "junior", 130000, 9.2, 3.5, 3),
        ("AI/ML Engineer", "mid", 180000, 9.5, 2.8, 4),
        ("AI/ML Engineer", "senior", 250000, 9.8, 2.0, 5),
        ("Data Scientist", "junior", 110000, 8.0, 4.5, 2),
        ("Data Scientist", "mid", 155000, 8.5, 3.5, 3),
        ("Data Scientist", "senior", 210000, 9.0, 2.5, 4),
        ("Clinical AI Specialist", "mid", 200000, 9.5, 1.5, 6),
        ("Clinical AI Specialist", "senior", 280000, 9.8, 1.0, 8),
        ("NLP Engineer", "mid", 170000, 9.0, 3.0, 4),
        ("NLP Engineer", "senior", 240000, 9.5, 2.2, 5),
        ("MLOps Engineer", "mid", 165000, 8.5, 3.2, 3),
        ("MLOps Engineer", "senior", 220000, 9.0, 2.5, 4),
        ("Healthcare Data Architect", "senior", 195000, 8.0, 3.0, 4),
        ("VP of AI", "executive", 350000, 9.8, 0.8, 6),
        ("Chief AI Officer", "executive", 450000, 9.9, 0.5, 8),
        ("Product Manager (AI)", "mid", 160000, 8.5, 4.0, 3),
        ("Product Manager (AI)", "senior", 220000, 9.0, 3.0, 4),
        ("FHIR/Interop Engineer", "mid", 150000, 7.5, 4.0, 3),
        ("Cloud Architect", "senior", 230000, 8.5, 2.8, 4),
        ("DevOps/SRE", "mid", 155000, 7.5, 4.5, 2),
    ]

    fields = [
        "role", "experience_level", "annual_salary",
        "demand_index", "supply_index", "time_to_hire_months",
    ]
    rows = [dict(zip(fields, r)) for r in roles]
    write_csv(os.path.join(d, "market_rates.csv"), rows, fields)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Generating MarketPivot reference data...")
    print("=" * 50)

    gen_company_financials()
    gen_customers()
    gen_competitors()
    gen_benchmarks()
    gen_market_sizing()
    gen_acquisition_targets()
    gen_precedent_deals()
    gen_debt_schedule()
    gen_scenario_assumptions()
    gen_talent_data()

    print(f"\nData generated in: {BASE_DIR}")
    print("  - company/: financials.json, customers.csv")
    print("  - market/: competitors.csv, industry_benchmarks.json, market_sizing.csv")
    print("  - acquisitions/: targets.csv, precedent_deals.csv")
    print("  - financial/: debt_schedule.csv, scenario_assumptions.json")
    print("  - talent/: market_rates.csv")
    print("\nDone!")


if __name__ == "__main__":
    main()
