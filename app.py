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
    /* Light background */
    body {
        background: linear-gradient(180deg, #f5f7fb 0%, #ffffff 40%, #e6f2ff 100%);
        color: #0f172a;
    }
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px;
    }

    /* Generic card */
    .card {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 16px 30px rgba(15,23,42,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.1rem;
    }

    /* Task header card with gradient */
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

    /* Buttons */
    .stButton>button {
        border-radius: 9999px !important;
        font-weight: 700 !important;
        padding-top: 0.55rem !important;
        padding-bottom: 0.55rem !important;
        padding-left: 1.3rem !important;
        padding-right: 1.3rem !important;
        font-size: 0.92rem !important;
    }

    /* Scorecard table tweaks */
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
    st.error(
        "OPENAI_API_KEY missing from Streamlit secrets. "
        "Go to *Manage app → Settings → Secrets* and add it."
    )
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------- HELPERS ------------------------------------ #


def call_llm(prompt: str, max_tokens: int = 3500) -> str:
    """
    Call OpenAI Responses API and return plain text.
    """
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=max_tokens,
    )
    text = response.output_text or ""
    return text.strip()


def parse_json_from_text(raw: str):
    """
    Extract the first JSON object from a text string and parse it.

    This prevents crashes when the model adds extra prose or backticks.
    """
    first = raw.find("{")
    last = raw.rfind("}")
    if first == -1 or last == -1 or last <= first:
        raise ValueError("Model did not return a valid JSON object.")
    json_str = raw[first : last + 1]
    return json.loads(json_str)


# ------------------------- DATA DEFINITIONS --------------------------- #

task1_categories = [
    # High-level procurement domains
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
    # Dell-specific granular categories
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

# Session state for cross-task data
for key in ["market_data", "contract_data", "score_initial", "score_refined"]:
    if key not in st.session_state:
        st.session_state[key] = None

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

tabs = st.tabs(
    [
        "🔍 1 · Supplier Market Intelligence",
        "📑 2 · Contract Type Recommendation",
        "🏅 3 · Supplier Evaluation Scorecard",
    ]
)

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
                Select a procurement category for Dell and generate top suppliers plus
                country-level sourcing risks.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
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
            st.write("")  # vertical align
            gen_btn = st.button("🔍 Generate Intelligence", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    if gen_btn:
        if selected_cat == "-- Select Category --":
            st.warning("Please select a category first.")
        else:
            with st.spinner("Calling GenAI for market intelligence…"):
                prompt1 = f"""
You are a senior procurement market-intelligence analyst for Dell Technologies.

For the procurement category: "{selected_cat}".

1. Identify the **top 5 global suppliers** that Dell could realistically source from.
2. Summarize **country-level sourcing risks** for 3–4 key sourcing countries.

Return **ONLY valid JSON**, no markdown, no backticks, exactly with this schema:

{{
  "category": "{selected_cat}",
  "marketOverview": "2-3 sentence overview of the global supplier market for Dell",
  "topSuppliers": [
    {{
      "rank": 1,
      "name": "Company name",
      "headquarters": "City, Country",
      "marketShare": "~25% (estimate)",
      "keyCapabilities": ["capability 1", "capability 2", "capability 3", "capability 4"],
      "differentiators": "1-2 sentences on what makes this supplier unique",
      "dellRelevance": "1-2 sentences on why this supplier is relevant for Dell"
    }}
  ],
  "countryRisks": [
    {{
      "country": "Country name",
      "supplierConcentration": "High/Medium/Low",
      "politicalRisk": {{
        "score": 1-10,
        "assessment": "short assessment",
        "keyFactors": ["factor 1", "factor 2"]
      }},
      "logisticsRisk": {{
        "score": 1-10,
        "assessment": "short assessment",
        "keyFactors": ["factor 1", "factor 2"]
      }},
      "complianceRisk": {{
        "score": 1-10,
        "assessment": "short assessment",
        "keyFactors": ["factor 1", "factor 2"]
      }},
      "esgRisk": {{
        "score": 1-10,
        "assessment": "short assessment",
        "keyFactors": ["factor 1", "factor 2"]
      }},
      "overallRiskLevel": "High/Medium/Low",
      "mitigation": "1-2 sentence risk mitigation guidance for Dell"
    }}
  ]
}}

All numeric fields like scores must be numbers, not strings.
                """.strip()

                raw = call_llm(prompt1)
                try:
                    market_data = parse_json_from_text(raw)
                    st.session_state.market_data = market_data
                except Exception as e:
                    st.error(f"Could not parse model output as JSON: {e}")
                    st.caption(raw)
                    st.stop()

    market_data = st.session_state.market_data
    if market_data:
        # Market overview card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🌍 Market Overview</div>', unsafe_allow_html=True)
        st.write(market_data.get("marketOverview", ""))
        st.markdown("</div>", unsafe_allow_html=True)

        # Top suppliers
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏭 Top 5 Global Suppliers</div>', unsafe_allow_html=True)
        for s in market_data.get("topSuppliers", []):
            st.markdown(
                f"""
                **{s.get('rank', '')}. {s.get('name','')}**  ·  *{s.get('headquarters','')}*  
                **Market share:** {s.get('marketShare','')}  
                **Key capabilities:** {", ".join(s.get("keyCapabilities", []))}  
                **Differentiators:** {s.get("differentiators","")}  
                **Dell relevance:** {s.get("dellRelevance","")}
                """.strip()
            )
            st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)

        # Country risks
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚠️ Country Risk Snapshot</div>', unsafe_allow_html=True)
        for r in market_data.get("countryRisks", []):
            col_left, col_right = st.columns([2, 1])
            with col_left:
                st.markdown(f"**{r.get('country','')}**  ·  Supplier concentration: {r.get('supplierConcentration','')}")
                st.markdown(f"**Mitigation:** {r.get('mitigation','')}")
            with col_right:
                st.metric("Overall risk", r.get("overallRiskLevel", ""))
                st.caption(
                    f"Political: {r['politicalRisk'].get('score','?')}/10 · "
                    f"Logistics: {r['logisticsRisk'].get('score','?')}/10 · "
                    f"Compliance: {r['complianceRisk'].get('score','?')}/10 · "
                    f"ESG: {r['esgRisk'].get('score','?')}/10"
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
                Select one or more Dell procurement items. The tool recommends suitable
                supply-chain contract types such as Buy-back, Revenue-Sharing, Wholesale, 
                Quantity Flexibility, Option, VMI and Cost-Sharing.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">DELL PROCUREMENT ITEMS</div>', unsafe_allow_html=True)
    selected_products = st.multiselect(
        "Select products/services",
        options=task2_products,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    analyze_btn = st.button("📑 Analyze Contract Options", use_container_width=True)

    if analyze_btn:
        if not selected_products:
            st.warning("Please select at least one procurement item.")
        else:
            list_str = "; ".join(selected_products)
            with st.spinner("Calling GenAI for contract analysis…"):
                prompt2 = f"""
You are a supply-chain contracts specialist working for Dell's global procurement team.

For the following Dell procurement items:
{list_str}

Recommend suitable **supply-chain contract types** chosen only from:
- Buy-back Contract
- Revenue-Sharing Contract
- Wholesale Price Contract
- Quantity Flexibility Contract
- Option Contract
- Vendor-Managed Inventory (VMI)
- Cost-Sharing / Incentive Contract

items_csv = ", ".join(selected_items)

prompt = f"""
You are a supply-chain contract expert for Dell Technologies.

Evaluate the most suitable contract types for the following items: {items_csv}.

For each item, you must:
- Assess cost predictability (High / Medium / Low + 1-2 line explanation).
- Assess market volatility (High / Medium / Low + 1-2 line explanation).
- Assess duration and volume requirements (Short / Medium / Long term and Low / Medium / High volume + explanation).
- Summarise the overall risk profile in a few short phrases.

Then for each item:
- Recommend a contract type from this list:
  ["Buy-back Contract", "Revenue-Sharing Contract", "Wholesale Price Contract",
   "Quantity Flexibility Contract", "Option Contract",
   "Vendor-Managed Inventory (VMI)", "Cost-Sharing Contract"].
- Suggest an alternative contract type from the remaining options.
- Compare the recommended vs alternative contract, explicitly referring to
  cost predictability, market volatility, and duration/volume fit.

Finally, provide a short overall decision summary for Dell.

Return ONLY valid JSON (no markdown, no commentary) with EXACTLY this structure:

{{
  "analysisDate": "2025-12-11",
  "categories": [
    {{
      "name": "Item name exactly as provided",
      "assessment": {{
        "costPredictability": {{
          "level": "High / Medium / Low",
          "explanation": "Why cost is or is not predictable under this contract."
        }},
        "marketVolatility": {{
          "level": "High / Medium / Low",
          "explanation": "How volatile prices/supply are and how the contract handles it."
        }},
        "durationAndVolume": {{
          "profile": "Short / Medium / Long term; Low / Medium / High volume",
          "explanation": "How well the contract fits the duration and volume requirements."
        }},
        "riskProfile": "2-3 short phrases summarising the key supply and financial risks."
      }},
      "recommendedContract": "One of the allowed contract names",
      "confidence": "High / Medium / Low",
      "justification": "Why this contract is best overall for this item.",
      "alternativeContract": "Another allowed contract name",
      "comparisonSummary": "Comparison between recommended and alternative for this item."
    }}
  ],
  "contractComparison": {{
    "Wholesale Price Contract": {{
      "description": "1-2 sentences.",
      "bestFor": "When this contract structure is most appropriate.",
      "advantages": ["Advantage 1", "Advantage 2"],
      "disadvantages": ["Limitation 1"]
    }},
    "Quantity Flexibility Contract": {{
      "description": "1-2 sentences.",
      "bestFor": "When this works best.",
      "advantages": ["Advantage 1", "Advantage 2"],
      "disadvantages": ["Limitation 1"]
    }},
    "Vendor-Managed Inventory (VMI)": {{
      "description": "1-2 sentences.",
      "bestFor": "Typical use cases.",
      "advantages": ["Advantage 1", "Advantage 2"],
      "disadvantages": ["Limitation 1"]
    }}
  }},
  "finalDecisionSummary": "2-3 sentences summarising Dell's contract selection decisions and trade-offs."
}}
"""

Only include contract types that are actually relevant.
                """.strip()

                raw2 = call_llm(prompt2)
                try:
                    contract_data = parse_json_from_text(raw2)
                    st.session_state.contract_data = contract_data
                except Exception as e:
                    st.error(f"Could not parse model output as JSON: {e}")
                    st.caption(raw2)

    contract_data = st.session_state.contract_data
    if contract_data:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📌 Contract Recommendations</div>', unsafe_allow_html=True)

        for cat in contract_data.get("categories", []):
            st.markdown(f"### {cat.get('name','')}")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Recommended contract:** " + cat.get("recommendedContract", ""))
                st.markdown("**Confidence:** " + cat.get("confidence", ""))
                    assess = cat.get("assessment", {})
    cp = assess.get("costPredictability", {})
    mv = assess.get("marketVolatility", {})
    dv = assess.get("durationAndVolume", {})

    st.markdown("**Contract fit assessment**")
    st.markdown(
        f"- **Cost predictability:** {cp.get('level', '')}"
        f"{' – ' + cp.get('explanation', '') if cp.get('explanation') else ''}\n"
        f"- **Market volatility:** {mv.get('level', '')}"
        f"{' – ' + mv.get('explanation', '') if mv.get('explanation') else ''}\n"
        f"- **Duration & volume requirements:** {dv.get('profile', '')}"
        f"{' – ' + dv.get('explanation', '') if dv.get('explanation') else ''}"
    )

                st.markdown("**Why this works for Dell**")
                st.write(cat.get("justification", ""))
            with col_b:
                st.markdown("**Alternative contract:** " + cat.get("alternativeContract", ""))
                st.markdown("**Implementation considerations**")
                st.write("• " + "\n• ".join(cat.get("implementationConsiderations", [])))
                st.markdown("**Key contract clauses to focus on**")
                st.write("• " + "\n• ".join(cat.get("keyContractClauses", [])))
            st.markdown("---")
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

    market_data = st.session_state.market_data
    if not market_data or not market_data.get("topSuppliers"):
        st.info("Run **Task 1 – Supplier Market Intelligence** first to identify suppliers.")
        st.stop()

    suppliers = [s["name"] for s in market_data["topSuppliers"]]
    category = market_data.get("category", "Selected category")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">CONTEXT</div>', unsafe_allow_html=True)
    st.write(f"**Category:** {category}")
    st.write("**Suppliers to evaluate:** " + ", ".join(suppliers))
    st.markdown("</div>", unsafe_allow_html=True)

    score_btn = st.button("🏅 Generate Scorecards", use_container_width=True)

    if score_btn:
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

For each supplier, assign 0-100 scores on each dimension, and compute a numeric
`weightedTotal` (0-100) using the weights above. Also assign a textual `rating`
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
            """.strip()

            raw_initial = call_llm(prompt_score_initial)
            try:
                score_initial = parse_json_from_text(raw_initial)
                st.session_state.score_initial = score_initial
            except Exception as e:
                st.error(f"Could not parse initial scorecard JSON: {e}")
                st.caption(raw_initial)
                st.stop()

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
`"kpis":[{{"name":"KPI name","description":"what it measures","importance":"why it matters for Dell"}}]`

Recalculate `weightedTotal` scores based on the new weights.

Return **ONLY valid JSON** with the same top-level structure as before,
plus the `kpis` field inside each dimension.
Do not include any explanation text or markdown.
            """.strip()

            raw_refined = call_llm(prompt_score_refined)
            try:
                score_refined = parse_json_from_text(raw_refined)
                st.session_state.score_refined = score_refined
            except Exception as e:
                st.error(f"Could not parse refined scorecard JSON: {e}")
                st.caption(raw_refined)

    score_initial = st.session_state.score_initial
    score_refined = st.session_state.score_refined

    if score_initial:
        st.markdown('<div class="card">', unsafe_allow_html=True)
            # ---------- INITIAL SCORECARD ----------
    st.markdown("### 🟢 Initial Scorecard")

    st.caption(
        f"{category} · {score_initial.get('evaluationDate', '')}"
    )

    # Build a flat dataframe for the initial scorecard
    initial_rows = []
    for s in score_initial.get("supplierScores", []):
        row = {"Supplier": s.get("supplierName", "")}
        # Add each dimension score as a column
        for dim in score_initial.get("dimensions", []):
            dim_name = dim.get("name")
            if dim_name:
                row[dim_name] = s.get("scores", {}).get(dim_name)
        row["Weighted total"] = s.get("weightedTotal")
        row["Rating"] = s.get("rating")
        initial_rows.append(row)

    if initial_rows:
        df_initial = (
            pd.DataFrame(initial_rows)
            .sort_values("Weighted total", ascending=False)
            .reset_index(drop=True)
        )

        st.dataframe(
            df_initial,
            use_container_width=True,
            height=260,
        )

    # Best-supplier call-out for the initial scorecard
    if score_initial.get("bestSupplier"):
        best = score_initial["bestSupplier"]
        st.markdown("#### 🏆 Best Supplier (Initial Scorecard)")
        st.markdown(
            f"**{best.get('name', '')}** — overall score **{best.get('score', '')}**"
        )
        if best.get("reasoning"):
            st.write(best["reasoning"])

    # ---------- REFINED SCORECARD ----------
    st.markdown("### 🔵 Refined Scorecard (with KPIs)")

    st.caption(
        f"{category} · {score_refined.get('evaluationDate', '')}"
    )

    refined_rows = []
    for s in score_refined.get("supplierScores", []):
        row = {"Supplier": s.get("supplierName", "")}
        for dim in score_refined.get("dimensions", []):
            dim_name = dim.get("name")
            if dim_name:
                row[dim_name] = s.get("scores", {}).get(dim_name)
        row["Weighted total"] = s.get("weightedTotal")
        row["Rating"] = s.get("rating")
        refined_rows.append(row)

    if refined_rows:
        df_refined = (
            pd.DataFrame(refined_rows)
            .sort_values("Weighted total", ascending=False)
            .reset_index(drop=True)
        )

        st.dataframe(
            df_refined,
            use_container_width=True,
            height=260,
        )

    # Optional: show best supplier for refined scorecard
    if score_refined.get("bestSupplier"):
        best2 = score_refined["bestSupplier"]
        st.markdown("#### 🥇 Best Supplier (Refined Scorecard)")
        st.markdown(
            f"**{best2.get('name', '')}** — overall score **{best2.get('score', '')}**"
        )
        if best2.get("reasoning"):
            st.write(best2["reasoning"])

