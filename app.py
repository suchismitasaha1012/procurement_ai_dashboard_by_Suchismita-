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

# =========================================================
# TASK 1
# =========================================================
with tabs[0]:
    st.markdown(
        """
        <div class="task-header">
            <div class="pill">TASK 1 · MARKET INTELLIGENCE</div>
            <h2>Supplier Market Intelligence using GenAI</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([3,1])

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

    st.markdown("</div>", unsafe_allow_html=True)

    if gen_btn:
        if selected_cat == "-- Select Category --":
            st.warning("Please select a category.")
        else:
            prompt1 = f"""
You are a procurement market-intelligence analyst for Dell.

Category: {selected_cat}

Identify:
1. Top 5 global suppliers  
2. 3–4 key sourcing-country risks  

Return ONLY JSON (no explanation).
"""
            raw = call_llm(prompt1)
            try:
                st.session_state.market_data = parse_json_from_text(raw)
            except Exception as e:
                st.error("Invalid LLM JSON.")
                st.caption(raw)

    market_data = st.session_state.market_data
    if market_data:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("### 🌍 Market Overview")
        st.write(market_data.get("marketOverview",""))
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# TASK 2 — CONTRACT SELECTION
# =========================================================
with tabs[1]:
    st.markdown(
        """
        <div class="task-header">
            <div class="pill">TASK 2 · CONTRACT SELECTION</div>
            <h2>GenAI-Supported Contract Type Recommendation</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">DELL PROCUREMENT ITEMS</div>', unsafe_allow_html=True)

    selected_items = st.multiselect(
        "Select products/services",
        task2_products,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    analyze_btn = st.button("📑 Analyze Contract Options", use_container_width=True)

    if analyze_btn:
        if not selected_items:
            st.warning("Please select at least one item.")
        else:
            items_csv = ", ".join(selected_items)
            prompt2 = f"""
You are a supply-chain contract expert at Dell.

Evaluate contract types for: {items_csv}

Return ONLY JSON with:
- assessment
- recommended contract
- alternative contract
- comparison summary
- final decision summary
"""
            raw2 = call_llm(prompt2)
            try:
                st.session_state.contract_data = parse_json_from_text(raw2)
            except:
                st.error("Invalid JSON returned.")
                st.caption(raw2)

    contract_data = st.session_state.contract_data
    if contract_data:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("### 📌 Contract Recommendations")

        for cat in contract_data.get("categories", []):
            st.write(f"#### {cat.get('name','')}")
            st.write("**Recommended:**", cat.get("recommendedContract",""))
            st.write("**Confidence:**", cat.get("confidence",""))
            st.write("**Justification:**")
            st.write(cat.get("justification",""))
            st.write("---")

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
