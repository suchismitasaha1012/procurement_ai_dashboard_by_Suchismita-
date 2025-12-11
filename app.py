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
    # Header
    st.markdown(
        """
        <div class="task-header">
            <div class="pill">TASK 3 · SUPPLIER SCORECARD</div>
            <h2 style="margin-top:0.3rem;margin-bottom:0.1rem;font-size:1.3rem;font-weight:800;">
                Supplier Evaluation Scorecard
            </h2>
            <p style="margin:0.2rem 0;color:#475569;font-size:0.9rem;">
                Based on Task&nbsp;1 suppliers, build an initial weighted scorecard and then
                a refined scorecard with KPIs.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Need Task 1 data
    market_data = st.session_state.market_data
    if not market_data or not market_data.get("topSuppliers"):
        st.info("Run **Task 1 – Supplier Market Intelligence** first to identify suppliers.")
        st.stop()

    suppliers = [
        s.get("name", f"Supplier {i+1}")
        for i, s in enumerate(market_data.get("topSuppliers", []))
    ]
    category = market_data.get("category", "Selected category")

    # Context card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">CONTEXT</div>', unsafe_allow_html=True)
    st.write(f"**Category:** {category}")
    st.write("**Suppliers to evaluate:** " + ", ".join(suppliers))
    st.markdown("</div>", unsafe_allow_html=True)

    score_btn = st.button("🏅 Generate Scorecards", use_container_width=True)

    # --------------------- LLM CALLS --------------------- #

    if score_btn:
        # ---------- Initial scorecard ----------
        with st.spinner("Generating initial scorecard…"):
            prompt_score_initial = f"""
Return ONLY valid JSON, no markdown, no explanations.

Create a supplier evaluation scorecard for Dell Technologies.

Suppliers: {", ".join(suppliers)}
Category: {category}

Use EXACTLY 5 dimensions:
- Technical Capability (weight 25)
- Quality Performance (weight 20)
- Financial Health (weight 20)
- ESG Compliance (weight 20)
- Innovation Capability (weight 15)

For each supplier:
- Give 0–100 scores on each dimension
- Compute `weightedTotal` (0–100) using the weights
- Give a text `rating` ("Excellent", "Good", "Average", "Poor")
- Include `strengths` and `weaknesses` lists

JSON structure (keys must match):

{{
  "evaluationTitle": "Initial Scorecard",
  "category": "{category}",
  "evaluationDate": "{date.today().isoformat()}",
  "dimensions": [
    {{"name":"Technical Capability","weight":25,"description":"text"}},
    {{"name":"Quality Performance","weight":20,"description":"text"}},
    {{"name":"Financial Health","weight":20,"description":"text"}},
    {{"name":"ESG Compliance","weight":20,"description":"text"}},
    {{"name":"Innovation Capability","weight":15,"description":"text"}}
  ],
  "supplierScores": [
    {{
      "supplierName": "Supplier name",
      "scores": {{
        "Technical Capability": 85,
        "Quality Performance": 80,
        "Financial Health": 90,
        "ESG Compliance": 75,
        "Innovation Capability": 82
      }},
      "weightedTotal": 83.5,
      "rating": "Excellent",
      "strengths": ["strength1","strength2"],
      "weaknesses": ["weak1"]
    }}
  ],
  "bestSupplier": {{
    "name": "Supplier name",
    "score": 88.4,
    "reasoning": "2-3 sentence explanation"
  }},
  "conclusion": "2-3 sentence recommendation for Dell"
}}
"""
            raw_initial = call_llm(prompt_score_initial)
            try:
                score_initial = parse_json_from_text(raw_initial)
                st.session_state.score_initial = score_initial
            except Exception as e:
                st.error(f"Could not parse initial scorecard JSON: {e}")
                st.caption(raw_initial)
                st.stop()

        # ---------- Refined scorecard ----------
        with st.spinner("Refining scorecard with KPIs…"):
            prompt_score_refined = f"""
Refine the following supplier scorecard JSON for Dell:

{json.dumps(st.session_state.score_initial)}

Change the weights to:
- Technical Capability 30
- Quality Performance 25
- ESG Compliance 25
- Financial Health 15
- Innovation Capability 5

For each dimension add `kpis`:
"kpis":[{{"name":"KPI name","description":"what it measures","importance":"why it matters for Dell"}}]

Recalculate `weightedTotal` for each supplier using the new weights.

Return ONLY valid JSON with the SAME top-level structure, plus the `kpis`
field inside each dimension.
"""
            raw_refined = call_llm(prompt_score_refined)
            try:
                score_refined = parse_json_from_text(raw_refined)
                st.session_state.score_refined = score_refined
            except Exception as e:
                st.error(f"Could not parse refined scorecard JSON: {e}")
                st.caption(raw_refined)

    # --------------------- DISPLAY --------------------- #

    score_initial = st.session_state.get("score_initial")
    score_refined = st.session_state.get("score_refined")

    # ---------- INITIAL SCORECARD ----------
    if score_initial:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🟢 Initial Scorecard", unsafe_allow_html=True)
        st.caption(f"{category} • {score_initial.get('evaluationDate', '')}")

        # Make table
        dim_names = [d.get("name") for d in score_initial.get("dimensions", []) if d.get("name")]
        rows = []
        for s in score_initial.get("supplierScores", []):
            row = {}
            row["Supplier"] = s.get("supplierName", "")
            scores_dict = s.get("scores", {}) or {}
            for dn in dim_names:
                row[dn] = scores_dict.get(dn)
            # use .get to avoid KeyError
            row["Weighted Total"] = (
                s.get("weightedTotal")
                or s.get("weighted_total")
                or s.get("weightedScore")
            )
            row["Rating"] = s.get("rating", "")
            rows.append(row)

        if rows:
            df_initial = (
                pd.DataFrame(rows)
                .sort_values("Weighted Total", ascending=False, na_position="last")
                .reset_index(drop=True)
            )
            st.dataframe(df_initial, use_container_width=True, height=260)
        else:
            st.warning("No supplier scores returned in initial scorecard.")

        # Best supplier call-out
        best = score_initial.get("bestSupplier")
        if best:
            st.markdown("#### 🏆 Best Supplier (Initial Scorecard)")
            st.markdown(
                f"**{best.get('name','')}** — overall score **{best.get('score','')}**"
            )
            if best.get("reasoning"):
                st.write(best["reasoning"])

        if score_initial.get("conclusion"):
            st.markdown("**Conclusion:**")
            st.write(score_initial.get("conclusion"))

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- REFINED SCORECARD ----------
    if score_refined:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔵 Refined Scorecard (with KPIs)", unsafe_allow_html=True)
        st.caption(f"{category} • {score_refined.get('evaluationDate', '')}")

        dim_names_ref = [d.get("name") for d in score_refined.get("dimensions", []) if d.get("name")]
        rows_ref = []
        for s in score_refined.get("supplierScores", []):
            row = {}
            row["Supplier"] = s.get("supplierName", "")
            scores_dict = s.get("scores", {}) or {}
            for dn in dim_names_ref:
                row[dn] = scores_dict.get(dn)
            row["Weighted Total"] = (
                s.get("weightedTotal")
                or s.get("weighted_total")
                or s.get("weightedScore")
            )
            row["Rating"] = s.get("rating", "")
            rows_ref.append(row)

        if rows_ref:
            df_ref = (
                pd.DataFrame(rows_ref)
                .sort_values("Weighted Total", ascending=False, na_position="last")
                .reset_index(drop=True)
            )
            st.dataframe(df_ref, use_container_width=True, height=260)
        else:
            st.warning("No supplier scores returned in refined scorecard.")

        # Optional: best supplier in refined view
        best2 = score_refined.get("bestSupplier")
        if best2:
            st.markdown("#### 🥇 Best Supplier (Refined Scorecard)")
            st.markdown(
                f"**{best2.get('name','')}** — overall score **{best2.get('score','')}**"
            )
            if best2.get("reasoning"):
                st.write(best2["reasoning"])

        # Show KPIs per dimension in an expander
        if score_refined.get("dimensions"):
            with st.expander("📊 Dimension KPIs used in refined scorecard"):
                for d in score_refined.get("dimensions", []):
                    st.markdown(f"**{d.get('name','Dimension')}**  (Weight: {d.get('weight','?')}%)")
                    st.write(d.get("description", ""))
                    for kpi in d.get("kpis", []):
                        st.markdown(
                            f"- **{kpi.get('name','KPI')}** – {kpi.get('description','')} "
                            f"*(Importance: {kpi.get('importance','')})*"
                        )
                    st.markdown("---")

        st.markdown("</div>", unsafe_allow_html=True)
