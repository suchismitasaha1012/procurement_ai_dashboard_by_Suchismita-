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
    st.markdown(
        """
        <div class="task-header">
            <div class="pill">TASK 2 · CONTRACT SELECTION</div>
            <h2 style="margin-top:0.3rem;margin-bottom:0.1rem;font-size:1.3rem;font-weight:800;">
                GenAI-Supported Contract Type Recommendation
            </h2>
            <p style="margin:0.2rem 0;color:#475569;font-size:0.9rem;">
                Select one or more Dell procurement items. The tool evaluates cost predictability,
                market volatility, and duration / volume requirements, and then recommends the most
                suitable supply chain contract type for each item.
                <br/>
                <span style="font-size:0.84rem;color:#64748b;">
                Contract universe is restricted to: Buy-back, Revenue-Sharing, Wholesale Price,
                Quantity Flexibility, Option, VMI, and Cost-Sharing / Incentive Contracts.
                </span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Input card ----
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">DELL PROCUREMENT ITEMS</div>', unsafe_allow_html=True)
    selected_products = st.multiselect(
        "Select products/services",
        options=task2_products,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    analyze_btn = st.button("📑 Analyze Contract Options", use_container_width=True)

    # ---- Call LLM when button is pressed ----
    if analyze_btn:
        if not selected_products:
            st.warning("Please select at least one procurement item.")
        else:
            items_csv = ", ".join(selected_products)

            with st.spinner("Calling GenAI for contract analysis…"):
                prompt2 = f"""
You are a supply-chain contract expert for Dell Technologies.

Your ONLY allowed contract types are:
1. "Buy-back Contract"
2. "Revenue-Sharing Contract"
3. "Wholesale Price Contract"
4. "Quantity Flexibility Contract"
5. "Option Contract"
6. "VMI (Vendor Managed Inventory)"
7. "Cost-Sharing or Incentive Contracts"

Do NOT invent any new contract names. Always use one of the exact names above.

Evaluate the most suitable contract types for the following Dell procurement items:
{items_csv}.

For each item you must:
1. Assess:
   - costPredictability: level ("High" / "Medium" / "Low") + 1–2 line explanation
   - marketVolatility: level ("High" / "Medium" / "Low") + explanation
   - durationAndVolume: profile ("Short / Medium / Long term; Low / Medium / High volume") + explanation

2. Compare the RELEVANT contract types (from the 7 allowed types) for this item.
   For each compared contract type give:
   - suitability: "High" / "Medium" / "Low"
   - pros: 2–3 bullet points
   - cons: 1–2 bullet points

3. Select:
   - recommendedContract: ONE best contract type from the list
   - alternativeContract: ONE second-best contract type
   - finalDecision: 2–3 sentence justification referring explicitly to cost predictability,
     market volatility, and duration/volume fit.

Finally, provide a short generic summary for each contract type explaining:
- whenToUse: typical use case (1–2 sentences)
- keyRisks: main risks/pitfalls (1–2 sentences)

Return ONLY valid JSON (no markdown, no commentary) with EXACTLY this structure:

{{
  "analysisDate": "{date.today().isoformat()}",
  "items": [
    {{
      "name": "Item name exactly as in input",
      "assessment": {{
        "costPredictability": {{
          "level": "High",
          "explanation": "text"
        }},
        "marketVolatility": {{
          "level": "Medium",
          "explanation": "text"
        }},
        "durationAndVolume": {{
          "profile": "Long term; High volume",
          "explanation": "text"
        }}
      }},
      "contractComparison": [
        {{
          "type": "Wholesale Price Contract",
          "suitability": "High",
          "pros": ["point 1","point 2"],
          "cons": ["point 1"]
        }}
      ],
      "recommendedContract": "Wholesale Price Contract",
      "alternativeContract": "Quantity Flexibility Contract",
      "finalDecision": "2-3 sentence justification"
    }}
  ],
  "contractTypeSummary": {{
    "Buy-back Contract": {{
      "whenToUse": "short text",
      "keyRisks": "short text"
    }},
    "Revenue-Sharing Contract": {{
      "whenToUse": "short text",
      "keyRisks": "short text"
    }},
    "Wholesale Price Contract": {{
      "whenToUse": "short text",
      "keyRisks": "short text"
    }},
    "Quantity Flexibility Contract": {{
      "whenToUse": "short text",
      "keyRisks": "short text"
    }},
    "Option Contract": {{
      "whenToUse": "short text",
      "keyRisks": "short text"
    }},
    "VMI (Vendor Managed Inventory)": {{
      "whenToUse": "short text",
      "keyRisks": "short text"
    }},
    "Cost-Sharing or Incentive Contracts": {{
      "whenToUse": "short text",
      "keyRisks": "short text"
    }}
  }}
}}
                """.strip()

                raw2 = call_llm(prompt2)

                try:
                    contract_data = parse_json_from_text(raw2)
                    st.session_state.contract_data = contract_data
                except Exception as e:
                    st.error(f"Could not parse model output as JSON: {e}")
                    st.caption(raw2)

    # ---- Display results ----
    contract_data = st.session_state.contract_data
    if contract_data:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📌 Contract Recommendations</div>', unsafe_allow_html=True)
        st.caption(f"Analysis date: {contract_data.get('analysisDate','')}")

        # Per-item analysis
        for item in contract_data.get("items", []):
            name = item.get("name", "Item")
            assess = item.get("assessment", {})
            cp = assess.get("costPredictability", {}) or {}
            mv = assess.get("marketVolatility", {}) or {}
            dv = assess.get("durationAndVolume", {}) or {}

            st.markdown(f"### 🔹 {name}")

            # Assessment
            st.markdown("**1. Demand & risk assessment**")
            st.markdown(
                f"- **Cost predictability:** {cp.get('level','')} – {cp.get('explanation','')}\n"
                f"- **Market volatility:** {mv.get('level','')} – {mv.get('explanation','')}\n"
                f"- **Duration & volume:** {dv.get('profile','')} – {dv.get('explanation','')}"
            )

            # Comparison of contract types
            st.markdown("**2. Comparison of relevant contract types**")
            for cc in item.get("contractComparison", []):
                ctype = cc.get("type", "")
                suitability = cc.get("suitability", "")
                pros = cc.get("pros", []) or []
                cons = cc.get("cons", []) or []
                st.markdown(f"- **{ctype}** (suitability: {suitability})")
                if pros:
                    st.markdown("  - Pros: " + "; ".join(pros))
                if cons:
                    st.markdown("  - Cons: " + "; ".join(cons))

            # Final decision
            st.markdown("**3. Final contract selection**")
            st.markdown(
                f"- ✅ **Recommended contract:** {item.get('recommendedContract','')}\n"
                f"- 🔁 **Alternative contract:** {item.get('alternativeContract','')}\n\n"
                f"{item.get('finalDecision','')}"
            )

            st.markdown("---")

        st.markdown("</div>", unsafe_allow_html=True)

        # ---- Overall contract type summary ----
        summary = contract_data.get("contractTypeSummary", {})
        if summary:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📘 Contract Type Summary (Cheat Sheet)</div>', unsafe_allow_html=True)
            for ctype, info in summary.items():
                when = (info or {}).get("whenToUse", "")
                risks = (info or {}).get("keyRisks", "")
                st.markdown(f"**{ctype}**")
                if when:
                    st.markdown(f"- _When to use_: {when}")
                if risks:
                    st.markdown(f"- _Key risks_: {risks}")
                st.markdown("")
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
                Based on Task&nbsp;1 suppliers, build an initial weighted scorecard and then
                a refined scorecard with KPIs.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Need Task 1 results first
    market_data = st.session_state.market_data
    if not market_data or not market_data.get("topSuppliers"):
        st.info("Run **Task 1 – Supplier Market Intelligence** first to identify suppliers.")
        st.stop()

    suppliers = [s["name"] for s in market_data["topSuppliers"]]
    category = market_data.get("category", "Selected category")

    # Context card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">CONTEXT</div>', unsafe_allow_html=True)
    st.write(f"**Category:** {category}")
    st.write("**Suppliers to evaluate:** " + ", ".join(suppliers))
    st.markdown("</div>", unsafe_allow_html=True)

    score_btn = st.button("🏅 Generate Scorecards", use_container_width=True)

    # ------------------- Generate scorecards via LLM ------------------- #

    if score_btn:
        # ---------- INITIAL SCORECARD ----------
        with st.spinner("Generating initial scorecard…"):
            prompt_score_initial = f"""
You are designing a **supplier evaluation scorecard** for Dell Technologies.

Suppliers: {", ".join(suppliers)}
Category: {category}

Create an initial scorecard with **5 evaluation dimensions**:
- Technical Capability (weight 25%)
- Quality Performance (weight 20%)
- Financial Health (weight 20%)
- ESG Compliance (weight 20%)
- Innovation Capability (weight 15%)

For each supplier, assign 0–10 scores on each dimension, and compute a numeric
`weightedTotal` (0–10) using the weights above. Also assign a textual `rating`
("Excellent", "Good", "Average", "Poor").

Return **ONLY valid JSON**, no prose, with this structure:

{{
  "evaluationTitle": "Initial Scorecard",
  "category": "{category}",
  "evaluationDate": "{date.today().isoformat()}",
  "dimensions": [
    {{"name":"Technical Capability","weight":25,"description":"1 sentence"}},
    {{"name":"Quality Performance","weight":20,"description":"1 sentence"}},
    {{"name":"Financial Health","weight":20,"description":"1 sentence"}},
    {{"name":"ESG Compliance","weight":20,"description":"1 sentence"}},
    {{"name":"Innovation Capability","weight":15,"description":"1 sentence"}}
  ],
  "supplierScores": [
    {{
      "supplierName": "Supplier name",
      "scores": {{
        "Technical Capability": 9.2,
        "Quality Performance": 8.8,
        "Financial Health": 9.0,
        "ESG Compliance": 8.7,
        "Innovation Capability": 8.9
      }},
      "weightedTotal": 8.9,
      "rating": "Excellent",
      "strengths": ["strength1","strength2"],
      "weaknesses": ["weak1"]
    }}
  ],
  "bestSupplier": {{
    "name": "Supplier name",
    "score": 9.1,
    "reasoning": "2-3 sentence explanation"
  }},
  "conclusion": "2-3 sentence recommendation for Dell"
}}
            """.strip()

            raw_initial = call_llm(prompt_score_initial)
            try:
                score_initial = parse_json_from_text(raw_initial)
                score_initial = ensure_weighted_totals_and_ratings(score_initial)
                st.session_state.score_initial = score_initial
            except Exception as e:
                st.error(f"Could not parse initial scorecard JSON: {e}")
                st.caption(raw_initial)
                st.stop()

        # ---------- REFINED SCORECARD ----------
        with st.spinner("Refining scorecard with KPIs…"):
            prompt_score_refined = f"""
Refine the following supplier evaluation scorecard for Dell:

{json.dumps(st.session_state.score_initial)}

Adjust the weights to:
- Technical Capability 30%
- Quality Performance 25%
- ESG Compliance 25%
- Financial Health 15%
- Innovation Capability 5%

For each dimension, add 2-3 concrete KPIs under a new `kpis` field:
"kpis":[{{"name":"KPI name","description":"what it measures","importance":"why it matters for Dell"}}]

Recalculate `weightedTotal` scores based on the new weights.

Return **ONLY valid JSON** with the same top-level structure as before,
plus the `kpis` field inside each dimension.
Do not include any explanation text or markdown.
            """.strip()

            raw_refined = call_llm(prompt_score_refined)
            try:
                score_refined = parse_json_from_text(raw_refined)
                score_refined = ensure_weighted_totals_and_ratings(score_refined)
                st.session_state.score_refined = score_refined
            except Exception as e:
                st.error(f"Could not parse refined scorecard JSON: {e}")
                st.caption(raw_refined)

    # ------------------------ DISPLAY SECTION -------------------------- #

    score_initial = st.session_state.score_initial
    score_refined = st.session_state.score_refined

    # ---------- Initial Scorecard table & summary ---------- #
    if score_initial:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🟢 Initial Scorecard", unsafe_allow_html=True)
        st.caption(f"{category} • {score_initial.get('evaluationDate', '')}")

        initial_rows = []
        for s in score_initial.get("supplierScores", []):
            row = {"Supplier": s.get("supplierName", "")}
            for dim in score_initial.get("dimensions", []):
                dname = dim.get("name")
                if dname:
                    row[dname] = s.get("scores", {}).get(dname)
            row["Weighted Total"] = s.get("weightedTotal")
            row["Rating"] = s.get("rating")
            initial_rows.append(row)

        if initial_rows:
            df_initial = (
                pd.DataFrame(initial_rows)
                .sort_values("Weighted Total", ascending=False)
                .reset_index(drop=True)
            )
            st.dataframe(df_initial, use_container_width=True, height=260)

        if score_initial.get("bestSupplier"):
            best = score_initial["bestSupplier"]
            st.markdown("#### 🏆 Best Supplier (Initial Scorecard)")
            st.markdown(
                f"**{best.get('name', '')}** — overall score **{best.get('score', '')}**"
            )
            if best.get("reasoning"):
                st.write(best["reasoning"])
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- Refined Scorecard table, best supplier & KPIs ---------- #
    if score_refined:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔵 Refined Scorecard (with KPIs)", unsafe_allow_html=True)
        st.caption(f"{category} • {score_refined.get('evaluationDate', '')}")

        refined_rows = []
        for s in score_refined.get("supplierScores", []):
            row = {"Supplier": s.get("supplierName", "")}
            for dim in score_refined.get("dimensions", []):
                dname = dim.get("name")
                if dname:
                    row[dname] = s.get("scores", {}).get(dname)
            row["Weighted Total"] = s.get("weightedTotal")
            row["Rating"] = s.get("rating")
            refined_rows.append(row)

        if refined_rows:
            df_refined = (
                pd.DataFrame(refined_rows)
                .sort_values("Weighted Total", ascending=False)
                .reset_index(drop=True)
            )
            st.dataframe(df_refined, use_container_width=True, height=260)

        if score_refined.get("bestSupplier"):
            best2 = score_refined["bestSupplier"]
            st.markdown("#### 🥇 Best Supplier (Refined Scorecard)")
            st.markdown(
                f"**{best2.get('name', '')}** — overall score **{best2.get('score', '')}**"
            )
            if best2.get("reasoning"):
                st.write(best2["reasoning"])

        # Dimension KPIs – robust handling
        with st.expander("📊 Dimension KPIs used in refined scorecard", expanded=False):
            for dim in score_refined.get("dimensions", []):
                dname = dim.get("name", "Dimension")
                st.markdown(f"**{dname}**")
                kpis = dim.get("kpis", [])
                if not kpis:
                    st.caption("No KPIs returned by the model.")
                    continue

                if not isinstance(kpis, list):
                    kpis = [kpis]

                for kpi in kpis:
                    if isinstance(kpi, dict):
                        name = kpi.get("name", "KPI")
                        desc = kpi.get("description", "")
                        imp = kpi.get("importance", "")
                        line = f"- **{name}** – {desc}"
                        if imp:
                            line += f"  \n  _Why it matters_: {imp}"
                        st.markdown(line)
                    else:
                        # Fallback if the model just returned a string
                        st.markdown(f"- {kpi}")

        st.markdown("</div>", unsafe_allow_html=True)
