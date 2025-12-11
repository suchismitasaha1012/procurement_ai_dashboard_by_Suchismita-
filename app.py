import json
from datetime import date

import pandas as pd
import streamlit as st
from openai import OpenAI

# ------------------------- BASIC PAGE CONFIG ------------------------- #

st.set_page_config(
    page_title="AI-Enabled Procurement Decision Support – Dell",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------- LIGHT THEME CSS --------------------------- #

st.markdown(
    """
    <style>
    body {
        background: linear-gradient(180deg, #f5f7fb 0%, #ffffff 40%, #e6f2ff 100%);
        color: #0f172a;
    }
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px;
    }
    .card {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 16px 30px rgba(15,23,42,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.1rem;
    }
    .task-header {
        background: linear-gradient(90deg, #eef4ff 0%, #f0fff4 100%);
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        border: 1px solid #d4e4ff;
        margin-bottom: 1.2rem;
    }
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        border: 1px solid rgba(148,163,184,0.5);
        background-color: #ffffff;
        color: #1d4ed8;
    }
    .section-title {
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 0.45rem;
        color: #0f172a;
    }
    .tiny-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.25rem;
    }
    .stButton>button {
        border-radius: 9999px !important;
        font-weight: 700 !important;
        padding-top: 0.55rem !important;
        padding-bottom: 0.55rem !important;
        padding-left: 1.3rem !important;
        padding-right: 1.3rem !important;
        font-size: 0.92rem !important;
    }
    thead tr th {
        background-color: #0f766e !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------- OPENAI CLIENT ------------------------------ #

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("Missing OPENAI_API_KEY in secrets.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------- HELPERS ------------------------------------ #

def call_llm(prompt: str, max_tokens: int = 3500) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=max_tokens,
    )
    text = response.output_text or ""
    return text.strip()

def parse_json_from_text(raw: str):
    first = raw.find("{")
    last = raw.rfind("}")
    if first == -1 or last == -1 or last <= first:
        raise ValueError("Model did not return valid JSON.")
    return json.loads(raw[first:last+1])

# ------------------------- DATA DEFINITIONS --------------------------- #

task1_categories = [
    "Electronics & Semiconductors",
    "Packaging Materials",
    "Logistics & Transportation",
    "Chemicals & Materials",
    "IT Services & Software",
    "Hardware Components (ODM)",
    "Cloud Computing Services",
    "Network Equipment",
    "Data Storage Solutions",
    "Manufacturing Equipment",
    "Office Supplies",
    "Energy & Utilities",
    "Laptop Components (Displays, Batteries)",
    "Server Processors (CPUs)",
    "Semiconductor & Microchips",
    "Standard Cables & Connectors",
    "Cooling Systems & Thermal Solutions",
    "Power Supply Units",
    "Networking Equipment (Switches/Routers)",
    "Data Storage Devices (SSDs)",
]

task2_products = [
    "Laptop Components (Displays, Batteries, Keyboards)",
    "Server Components (Processors, Memory, Storage)",
    "Semiconductor & Microchips",
    "Printed Circuit Boards (PCBs)",
    "Standard Cables & Connectors",
    "Cooling Systems & Thermal Solutions",
    "Power Supply Units",
    "Networking Equipment",
    "Data Storage Devices (SSDs)",
    "Graphics Processing Units (GPUs)",
    "Packaging Materials",
    "Logistics & Freight Services",
    "Green/Sustainable Materials",
    "Cloud Infrastructure Services",
    "IT Support & Consulting",
    "Security & Compliance Solutions",
    "Manufacturing Equipment & Tools",
    "Testing & Quality Assurance Equipment",
    "Raw Materials (Plastics, Metals, Composites)",
]

# Session state initialization
for key in ["market_data", "contract_data", "score_initial", "score_refined"]:
    st.session_state.setdefault(key, None)

# ------------------------- HEADER ------------------------------------- #

st.markdown(
    """
    <div class="card" style="display:flex;flex-direction:column;gap:0.35rem;">
        <div class="pill">DELL TECHNOLOGIES · PROCUREMENT · GENAI</div>
        <h1 style="margin:0;font-size:1.9rem;font-weight:800;">
            AI-Enabled Procurement Decision Support
        </h1>
        <p style="margin:0.2rem 0 0.1rem;color:#475569;font-size:0.95rem;max-width:820px;">
            Use GenAI to generate global supplier intelligence, recommend supply-chain contract types,
            and build supplier evaluation scorecards for Dell Technologies.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "🔍 1 · Supplier Market Intelligence",
    "📑 2 · Contract Type Recommendation",
    "🏅 3 · Supplier Evaluation Scorecard",
])

# ===================================================================== #
#                               TASK 1                                  #
# ===================================================================== #

with tabs[0]:

    st.markdown(
        """
        <div class="task-header">
            <div class="pill">TASK 1 · MARKET INTELLIGENCE</div>
            <h2 style="margin-top:0.3rem;margin-bottom:0.1rem;font-size:1.3rem;font-weight:800;">
                Supplier Market Intelligence using GenAI
            </h2>
            <p style="margin:0.2rem 0;color:#475569;font-size:0.9rem;">
                Select a procurement category for Dell and generate top suppliers plus country-level risks.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="tiny-label">PROCUREMENT CATEGORY</div>', unsafe_allow_html=True)
        selected_cat = st.selectbox(
            "Select category",
            ["-- Select Category --"] + task1_categories,
            index=0,
            label_visibility="collapsed",
        )

    with col2:
        gen_btn = st.button("🔍 Generate Intelligence", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if gen_btn:
        if selected_cat == "-- Select Category --":
            st.warning("Select a valid category.")
        else:
            with st.spinner("Calling GenAI…"):
                prompt = f"""
You are a procurement market-intelligence analyst for Dell.
For the category "{selected_cat}", return JSON:

{{
  "category": "{selected_cat}",
  "marketOverview": "2–3 sentence overview",
  "topSuppliers": [
    {{
      "rank": 1,
      "name": "Supplier",
      "headquarters": "City, Country",
      "marketShare": "~X%",
      "keyCapabilities": ["a","b","c"],
      "differentiators": "text",
      "dellRelevance": "text"
    }}
  ],
  "countryRisks": [
    {{
      "country": "Country",
      "supplierConcentration": "High/Medium/Low",
      "politicalRisk": {{"score":5,"assessment":"text","keyFactors":["a","b"]}},
      "logisticsRisk": {{"score":5,"assessment":"text","keyFactors":["a","b"]}},
      "complianceRisk": {{"score":5,"assessment":"text","keyFactors":["a","b"]}},
      "esgRisk": {{"score":5,"assessment":"text","keyFactors":["a","b"]}},
      "overallRiskLevel": "High/Medium/Low",
      "mitigation": "text"
    }}
  ]
}}
"""

                raw = call_llm(prompt)
                try:
                    st.session_state.market_data = parse_json_from_text(raw)
                except Exception:
                    st.error("Invalid JSON returned.")
                    st.caption(raw)

    md = st.session_state.market_data
    if md:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🌍 Market Overview</div>', unsafe_allow_html=True)
        st.write(md["marketOverview"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏭 Top Suppliers</div>', unsafe_allow_html=True)
        for s in md["topSuppliers"]:
            st.write(f"### {s['rank']}. {s['name']}  — *{s['headquarters']}*")
            st.write(f"**Market share:** {s['marketShare']}")
            st.write("**Key capabilities:** " + ", ".join(s["keyCapabilities"]))
            st.write("**Differentiators:** " + s["differentiators"])
            st.write("**Dell relevance:** " + s["dellRelevance"])
            st.markdown("---")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚠ Country Risk Snapshot</div>', unsafe_allow_html=True)
        for r in md["countryRisks"]:
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.write(f"### {r['country']}")
                st.write(f"Supplier concentration: {r['supplierConcentration']}")
                st.write("Mitigation: " + r["mitigation"])
            with col_r:
                st.metric("Overall Risk", r["overallRiskLevel"])
                st.caption(
                    f"P:{r['politicalRisk']['score']} · "
                    f"L:{r['logisticsRisk']['score']} · "
                    f"C:{r['complianceRisk']['score']} · "
                    f"E:{r['esgRisk']['score']}"
                )
            st.markdown("---")
        st.markdown('</div>', unsafe_allow_html=True)

# ===================================================================== #
#                               TASK 2                                  #
# ===================================================================== #

with tabs[1]:

    st.markdown(
        """
        <div class="task-header">
            <div class="pill">TASK 2 · CONTRACT SELECTION</div>
            <h2 style="margin-top:0.3rem;margin-bottom:0.1rem;font-size:1.3rem;font-weight:800;">
                GenAI-Supported Contract Selection
            </h2>
            <p style="margin:0.2rem 0;color:#475569;font-size:0.9rem;">
                Select items, and GenAI will evaluate risk drivers and recommend contract types.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">DELL PROCUREMENT ITEMS</div>', unsafe_allow_html=True)

    selected_items = st.multiselect("Select items", task2_products, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("📑 Analyze Contract Options"):
        if not selected_items:
            st.warning("Select at least one item.")
        else:
            items_csv = ", ".join(selected_items)

            prompt = f"""
You are a contract expert for Dell. Evaluate contract types for: {items_csv}.
Return ONLY JSON in this format:

{{
 "analysisDate": "{date.today()}",
 "categories": [
   {{
     "name": "Item name",
     "assessment": {{
        "costPredictability": {{"level":"High","explanation":"text"}},
        "marketVolatility": {{"level":"Medium","explanation":"text"}},
        "durationAndVolume": {{"profile":"Long; High volume","explanation":"text"}},
        "riskProfile": "text"
     }},
     "recommendedContract": "Contract",
     "confidence": "High",
     "justification": "text",
     "alternativeContract": "Contract",
     "comparisonSummary": "text"
   }}
 ],
 "contractComparison": {{
    "Wholesale Price Contract": {{
        "description": "text",
        "bestFor": "text",
        "advantages": ["a","b"],
        "disadvantages": ["c"]
    }},
    "Quantity Flexibility Contract": {{
        "description": "text",
        "bestFor": "text",
        "advantages": ["a","b"],
        "disadvantages": ["c"]
    }},
    "Vendor-Managed Inventory (VMI)": {{
        "description": "text",
        "bestFor": "text",
        "advantages": ["a","b"],
        "disadvantages": ["c"]
    }}
 }},
 "finalDecisionSummary": "text"
}}
"""

            raw = call_llm(prompt)
            try:
                st.session_state.contract_data = parse_json_from_text(raw)
            except Exception:
                st.error("Invalid JSON returned.")
                st.caption(raw)

    cd = st.session_state.contract_data
    if cd:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📌 Contract Recommendations</div>', unsafe_allow_html=True)

        for cat in cd["categories"]:
            st.markdown(f"## {cat['name']}")
            colA, colB = st.columns(2)

            with colA:
                st.write("**Recommended contract:**", cat["recommendedContract"])
                st.write("**Confidence:**", cat["confidence"])

                assess = cat["assessment"]
                cp = assess["costPredictability"]
                mv = assess["marketVolatility"]
                dv = assess["durationAndVolume"]

                st.markdown("**Contract Fit Assessment**")
                st.write(f"- Cost predictability: {cp['level']} – {cp['explanation']}")
                st.write(f"- Market volatility: {mv['level']} – {mv['explanation']}")
                st.write(f"- Duration & volume: {dv['profile']} – {dv['explanation']}")

                st.markdown("**Why this works for Dell**")
                st.write(cat["justification"])

            with colB:
                st.write("**Alternative contract:**", cat["alternativeContract"])
                st.write("**Comparison:**")
                st.write(cat["comparisonSummary"])

            st.markdown("---")

        st.write("### Final Decision Summary")
        st.write(cd["finalDecisionSummary"])
        st.markdown('</div>', unsafe_allow_html=True)

# ===================================================================== #
#                               TASK 3                                  #
# ===================================================================== #

with tabs[2]:

    st.markdown(
        """
        <div class="task-header">
            <div class="pill">TASK 3 · SUPPLIER SCORECARD</div>
            <h2 style="margin-top:0.3rem;margin-bottom:0.1rem;font-size:1.3rem;font-weight:800;">
                Supplier Evaluation Scorecard
            </h2>
            <p style="margin:0.2rem 0;color:#475569;font-size:0.9rem;">
                Generate initial and refined supplier scorecards based on Task 1 suppliers.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    md = st.session_state.market_data
    if not md:
        st.info("Run Task 1 first.")
        st.stop()

    suppliers = [s["name"] for s in md["topSuppliers"]]
    category = md["category"]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">CONTEXT</div>', unsafe_allow_html=True)
    st.write(f"**Category:** {category}")
    st.write("**Suppliers:** " + ", ".join(suppliers))
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🏅 Generate Scorecards"):
        prompt_initial = f"""
Return JSON only. Build an initial supplier scorecard for: {", ".join(suppliers)}.
{{
 "evaluationTitle": "Initial Scorecard",
 "category": "{category}",
 "evaluationDate": "{date.today()}",
 "dimensions": [
   {{"name":"Technical Capability","weight":25,"description":"text"}},
   {{"name":"Quality Performance","weight":20,"description":"text"}},
   {{"name":"Financial Health","weight":20,"description":"text"}},
   {{"name":"ESG Compliance","weight":20,"description":"text"}},
   {{"name":"Innovation Capability","weight":15,"description":"text"}}
 ],
 "supplierScores":[
   {{
     "supplierName":"Supplier",
     "scores":{{"Technical Capability":80,"Quality Performance":75,"Financial Health":70,"ESG Compliance":85,"Innovation Capability":60}},
     "weightedTotal":78,
     "rating":"Good",
     "strengths":["a","b"],
     "weaknesses":["c"]
   }}
 ],
 "bestSupplier":{{"name":"Supplier","score":90,"reasoning":"text"}},
 "conclusion":"text"
}}
"""
        raw_i = call_llm(prompt_initial)
        try:
            st.session_state.score_initial = parse_json_from_text(raw_i)
        except:
            st.error("Invalid JSON.")
            st.caption(raw_i)
            st.stop()

        prompt_refined = f"""
Refine this scorecard. Add KPIs and adjust weights (30,25,25,15,5). Return JSON only.
{json.dumps(st.session_state.score_initial)}
"""
        raw_r = call_llm(prompt_refined)
        try:
            st.session_state.score_refined = parse_json_from_text(raw_r)
        except:
            st.error("Invalid refined JSON.")
            st.caption(raw_r)

    si = st.session_state.score_initial
    sr = st.session_state.score_refined

    if si:
        st.markdown("### 🟢 Initial Scorecard")
        st.caption(f"{category} · {si['evaluationDate']}")

        rows = []
        for s in si["supplierScores"]:
            row = {"Supplier": s["supplierName"]}
            for d in si["dimensions"]:
                row[d["name"]] = s["scores"].get(d["name"])
            row["Weighted total"] = s["weightedTotal"]
            row["Rating"] = s["rating"]
            rows.append(row)

        df = pd.DataFrame(rows).sort_values("Weighted total", ascending=False)
        st.dataframe(df, use_container_width=True)

        best = si["bestSupplier"]
        st.write(f"### 🏆 Best Supplier: {best['name']} (Score {best['score']})")
        st.write(best["reasoning"])

    if sr:
        st.markdown("### 🔵 Refined Scorecard (with KPIs)")
        st.caption(f"{category} · {sr['evaluationDate']}")

        rows = []
        for s in sr["supplierScores"]:
            row = {"Supplier": s["supplierName"]}
            for d in sr["dimensions"]:
                row[d["name"]] = s["scores"].get(d["name"])
            row["Weighted total"] = s["weightedTotal"]
            row["Rating"] = s["rating"]
            rows.append(row)

        df2 = pd.DataFrame(rows).sort_values("Weighted total", ascending=False)
        st.dataframe(df2, use_container_width=True)

        best2 = sr["bestSupplier"]
        st.write(f"### 🥇 Best Supplier (Refined): {best2['name']} ({best2['score']})")
        st.write(best2["reasoning"])
