import json
from datetime import date

import pandas as pd
import streamlit as st
from openai import OpenAI

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI-Enabled Procurement Decision Support – Dell",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# LIGHT THEME CSS
# ---------------------------------------------------------
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
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# OPENAI CLIENT
# ---------------------------------------------------------
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY missing in Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def call_llm(prompt: str, max_tokens: int = 3500) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=max_tokens,
    )
    return (response.output_text or "").strip()


def parse_json_from_text(raw: str):
    first = raw.find("{")
    last = raw.rfind("}")
    if first == -1 or last == -1:
        raise ValueError("LLM did not return valid JSON.")
    return json.loads(raw[first:last+1])


# ---------------------------------------------------------
# STATIC DATA
# ---------------------------------------------------------
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

for key in ["market_data", "contract_data", "score_initial", "score_refined"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="card">
        <div class="pill">DELL TECHNOLOGIES · PROCUREMENT · GENAI</div>
        <h1 style="margin:0;font-size:1.9rem;font-weight:800;">AI-Enabled Procurement Decision Support</h1>
        <p style="color:#475569;font-size:0.95rem;">
            Use GenAI to generate supplier intelligence, contract recommendations,
            and weighted supplier evaluation scorecards.
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
    st.markdown("""
        <div class="task-header">
            <div class="pill">TASK 1 · MARKET INTELLIGENCE</div>
            <h2 style="margin-top:0.3rem;margin-bottom:0.1rem;font-size:1.3rem;font-weight:800;">
                Supplier Market Intelligence using GenAI
            </h2>
            <p style="margin:0.2rem 0;color:#475569;font-size:0.9rem;">
                Generate supplier insights & risk intelligence for Dell categories.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="tiny-label">PROCUREMENT CATEGORY</div>', unsafe_allow_html=True)
        selected_cat = st.selectbox(
            "Select category",
            options=["-- Select Category --"] + task1_categories,
            index=0,
            label_visibility="collapsed",
        )

    with col2:
        st.write("")
        gen_btn = st.button("🔍 Generate Intelligence", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- RUN GENAI ---------------- #

    if gen_btn:
        if selected_cat == "-- Select Category --":
            st.warning("Please select a valid procurement category.")
        else:
            with st.spinner("Calling GenAI…"):
                prompt1 = f"""
Return ONLY valid JSON. No explanations.

JSON MUST contain these keys:
- "marketOverview"
- "topSuppliers" (list of 5)
- "countryRisks" (list of 3–4)

If uncertain, provide placeholder text instead of removing a field.

Structure:
{{
  "category": "{selected_cat}",
  "marketOverview": "2-3 sentence overview.",
  "topSuppliers": [
    {{
      "rank": 1,
      "name": "Company",
      "headquarters": "City, Country",
      "marketShare": "~25%",
      "keyCapabilities": ["cap1", "cap2", "cap3"],
      "differentiators": "text",
      "dellRelevance": "text"
    }}
  ],
  "countryRisks": [
    {{
      "country": "Country",
      "supplierConcentration": "High/Medium/Low",
      "politicalRisk": {{"score": 5, "assessment": "text", "keyFactors": ["f1","f2"]}},
      "logisticsRisk":  {{"score": 6, "assessment": "text", "keyFactors": ["f1","f2"]}},
      "complianceRisk": {{"score": 7, "assessment": "text", "keyFactors": ["f1","f2"]}},
      "esgRisk":        {{"score": 8, "assessment": "text", "keyFactors": ["f1","f2"]}},
      "overallRiskLevel": "High/Medium/Low",
      "mitigation": "text"
    }}
  ]
}}
"""

                raw = call_llm(prompt1)

                try:
                    market_data = parse_json_from_text(raw)
                    st.session_state.market_data = market_data
                except:
                    st.error("❌ LLM returned invalid JSON. Please try again.")
                    st.caption(raw)
                    st.stop()

    # ------------- DISPLAY OUTPUT ------------- #

    data = st.session_state.market_data

    if data:
        marketOverview = data.get("marketOverview", "No overview provided.")
        topSuppliers = data.get("topSuppliers", [])
        countryRisks = data.get("countryRisks", [])

        # --- MARKET OVERVIEW ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🌍 Market Overview</div>", unsafe_allow_html=True)
        st.write(marketOverview)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- SUPPLIERS ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🏭 Top 5 Global Suppliers</div>", unsafe_allow_html=True)

        if not topSuppliers:
            st.warning("⚠️ No supplier info returned by GenAI.")
        else:
            for s in topSuppliers:
                st.markdown(f"""
                **{s.get('rank','?')}. {s.get('name','Unknown Supplier')}**  
                *{s.get('headquarters','N/A')}*  

                **Market Share:** {s.get('marketShare','N/A')}  
                **Capabilities:** {", ".join(s.get("keyCapabilities", []))}  
                **Differentiators:** {s.get("differentiators","N/A")}  
                **Dell Relevance:** {s.get("dellRelevance","N/A")}
                """)
                st.markdown("---")

        st.markdown("</div>", unsafe_allow_html=True)

        # --- COUNTRY RISKS ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<div class='section-title'>⚠️ Country Risk Snapshot</div>", unsafe_allow_html=True)

        if not countryRisks:
            st.warning("⚠️ No risk data returned.")
        else:
            for r in countryRisks:
                st.subheader(r.get("country", "Unknown Country"))
                st.write(f"Supplier Concentration: **{r.get('supplierConcentration','N/A')}**")
                st.write(r.get("mitigation", ""))

                st.caption(
                    f"Political: {r.get('politicalRisk',{}).get('score','?')} · "
                    f"Logistics: {r.get('logisticsRisk',{}).get('score','?')} · "
                    f"Compliance: {r.get('complianceRisk',{}).get('score','?')} · "
                    f"ESG: {r.get('esgRisk',{}).get('score','?')}"
                )
                st.markdown("---")

        st.markdown("</div>", unsafe_allow_html=True)

# ===================================================================== #
#                               TASK 2                                  #
# ===================================================================== #

with tabs[1]:
    st.markdown("""
        <div class="task-header">
            <div class="pill">TASK 2 · CONTRACT SELECTION</div>
            <h2 style="margin-top:0.3rem;margin-bottom:0.1rem;font-size:1.3rem;font-weight:800;">
                GenAI-Supported Contract Type Recommendation
            </h2>
            <p style="margin:0.2rem 0;color:#475569;font-size:0.9rem;">
                Recommend optimal supply-chain contract types for Dell items.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">DELL PROCUREMENT ITEMS</div>', unsafe_allow_html=True)

    selected_products = st.multiselect(
        "Select items",
        task2_products,
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    analyze_btn = st.button("📑 Analyze Contract Options", use_container_width=True)

    if analyze_btn:
        if not selected_products:
            st.warning("Please select at least one item.")
        else:
            products_csv = ", ".join(selected_products)

            with st.spinner("Generating contract recommendations…"):

                prompt2 = f"""
Return ONLY valid JSON.

Structure:
{{
  "analysisDate": "{date.today()}",
  "categories": [
    {{
      "name": "Item",
      "assessment": {{
        "costPredictability": {{"level":"High","explanation":"text"}},
        "marketVolatility":   {{"level":"Low","explanation":"text"}},
        "durationAndVolume":  {{"profile":"Long; High","explanation":"text"}},
        "riskProfile": "text"
      }},
      "recommendedContract": "Type",
      "confidence": "High/Medium/Low",
      "justification": "text",
      "alternativeContract": "Type",
      "comparisonSummary": "text"
    }}
  ],
  "finalDecisionSummary": "text"
}}
"""

                raw = call_llm(prompt2)

                try:
                    contract_data = parse_json_from_text(raw)
                    st.session_state.contract_data = contract_data
                except:
                    st.error("❌ LLM returned invalid JSON.")
                    st.caption(raw)

    # ------------- DISPLAY OUTPUT ------------- #

    contract_data = st.session_state.contract_data

    if contract_data:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📌 Contract Recommendations</div>", unsafe_allow_html=True)

        for c in contract_data.get("categories", []):
            st.subheader(c.get("name", "Item"))

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Recommended Contract**")
                st.write(c.get("recommendedContract", "N/A"))
                st.write("**Confidence:** " + c.get("confidence", "N/A"))
                st.write("**Why this works:**")
                st.write(c.get("justification", ""))

            with col2:
                st.markdown("**Alternative Contract**")
                st.write(c.get("alternativeContract", "N/A"))
                st.write("**Comparison Summary:**")
                st.write(c.get("comparisonSummary", ""))

            st.markdown("---")

        st.subheader("🏁 Final Recommendation Summary")
        st.write(contract_data.get("finalDecisionSummary", ""))

        st.markdown("</div>", unsafe_allow_html=True)

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
                Based on Task 1 suppliers, build an initial weighted scorecard and a refined scorecard with KPIs.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------- Ensure Task 1 Data Exists --------------------
    market_data = st.session_state.get("market_data", None)

    if not market_data or "topSuppliers" not in market_data:
        st.info("⚠️ Please run Task 1 (Market Intelligence) before generating scorecards.")
        st.stop()

    suppliers = [s["name"] for s in market_data["topSuppliers"]]
    category = market_data.get("category", "Selected Category")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">CONTEXT</div>', unsafe_allow_html=True)
    st.write(f"**Category:** {category}")
    st.write("**Suppliers:** " + ", ".join(suppliers))
    st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------- Generate Button -------------------------
    score_btn = st.button("🏅 Generate Scorecards", use_container_width=True)

    if score_btn:

        # ---------------- Initial Scorecard -----------------
        with st.spinner("Generating initial scorecard…"):
            prompt_initial = f"""
You are designing a supplier evaluation scorecard for Dell.

Suppliers: {", ".join(suppliers)}
Category: {category}

Create an initial scorecard using weights:
- Technical Capability: 25
- Quality Performance: 20
- Financial Health: 20
- ESG Compliance: 20
- Innovation Capability: 15

Return ONLY JSON structured as:
{{
 "evaluationTitle": "Initial Scorecard",
 "evaluationDate": "{date.today().isoformat()}",
 "category": "{category}",
 "dimensions": [...],
 "supplierScores": [...],
 "bestSupplier": {{
     "name": "",
     "score": 0,
     "reasoning": ""
 }},
 "conclusion": ""
}}
"""
            raw_initial = call_llm(prompt_initial)
            score_initial = parse_json_from_text(raw_initial)
            st.session_state.score_initial = score_initial

        # ---------------- Refined Scorecard -----------------
        with st.spinner("Refining scorecard with KPIs…"):
            prompt_refined = f"""
Refine the following Dell supplier scorecard. Add KPIs to each dimension and update weights.

{json.dumps(score_initial)}

Return ONLY JSON with same structure, but each dimension must include "kpis".
"""
            raw_refined = call_llm(prompt_refined)
            score_refined = parse_json_from_text(raw_refined)
            st.session_state.score_refined = score_refined

    # ---------------------- DISPLAY RESULTS -------------------------

    score_initial = st.session_state.get("score_initial", None)
    score_refined = st.session_state.get("score_refined", None)

    if score_initial:
        st.markdown("### 🟢 Initial Scorecard")
        st.caption(f"{category} • {score_initial['evaluationDate']}")

        # Convert to DataFrame
        rows = []
        for s in score_initial["supplierScores"]:
            row = {"Supplier": s["supplierName"], "Weighted Total": s["weightedTotal"], "Rating": s["rating"]}
            for d in score_initial["dimensions"]:
                row[d["name"]] = s["scores"][d["name"]]
            rows.append(row)

        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        best = score_initial["bestSupplier"]
        st.markdown(f"#### 🏆 Best Supplier: **{best['name']}** — {best['score']}")
        st.write(best["reasoning"])

    if score_refined:
        st.markdown("### 🔵 Refined Scorecard (with KPIs)")
        st.caption(f"{category} • {score_refined['evaluationDate']}")

        rows = []
        for s in score_refined["supplierScores"]:
            row = {"Supplier": s["supplierName"], "Weighted Total": s["weightedTotal"], "Rating": s["rating"]}
            for d in score_refined["dimensions"]:
                row[d["name"]] = s["scores"][d["name"]]
            rows.append(row)

        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        best = score_refined["bestSupplier"]
        st.markdown(f"#### 🥇 Best Supplier (Refined): **{best['name']}** — {best['score']}")
        st.write(best["reasoning"])
