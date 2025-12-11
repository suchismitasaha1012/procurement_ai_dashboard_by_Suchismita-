import os
import json
import textwrap
from typing import Dict, Any

import pandas as pd
import streamlit as st
from openai import OpenAI

# ---------- CONFIG & STYLING ---------- #

st.set_page_config(
    page_title="AI-Enabled Procurement Decision Support – Dell",
    page_icon="💼",
    layout="wide",
)

# Custom CSS for colourful UI
st.markdown(
    """
    <style>
    /* Whole page background */
    .stApp {
        background: radial-gradient(circle at top left, #0f172a 0, #020617 35%, #020617 100%);
        color: #0b1120;
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* Main white card */
    .main-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 2.2rem 2.4rem;
        box-shadow: 0 24px 80px rgba(15,23,42,0.40);
        border: 1px solid rgba(148,163,184,0.35);
    }

    /* Header badge */
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.2rem 0.85rem;
        border-radius: 999px;
        background: rgba(15,118,110,0.08);
        color: #0f766e;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .big-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.1rem;
        color: #020617;
    }

    .subtitle {
        font-size: 0.95rem;
        color: #64748b;
    }

    /* Section headers for each task */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
    }

    .section-header span.emoji {
        font-size: 1.8rem;
    }

    .section-title {
        font-weight: 700;
        font-size: 1.3rem;
        color: #020617;
    }

    .section-subtitle {
        font-size: 0.9rem;
        color: #6b7280;
    }

    /* Coloured section cards */
    .section-card {
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1.25rem;
        border: 1px solid rgba(148,163,184,0.4);
        background: linear-gradient(135deg, #eff6ff 0, #ffffff 38%, #eef2ff 100%);
    }
    .section-card-purple {
        background: linear-gradient(135deg, #f5f3ff 0, #ffffff 38%, #fdf2ff 100%);
    }
    .section-card-green {
        background: linear-gradient(135deg, #ecfdf5 0, #ffffff 38%, #dcfce7 100%);
    }

    /* Buttons */
    .stButton>button {
        border-radius: 999px !important;
        padding: 0.7rem 1.8rem;
        font-weight: 600;
        font-size: 0.95rem;
        border: 1px solid transparent;
    }

    /* Select boxes & multiselects */
    .stSelectbox, .stMultiselect {
        font-size: 0.92rem !important;
    }

    /* Error alert text a little smaller */
    .stAlert p {
        font-size: 0.9rem;
    }

    /* Scorecard table */
    .score-table thead tr th {
        background: #047857 !important;
        color: #ecfdf5 !important;
        font-size: 0.88rem;
    }
    .score-table tbody tr:nth-child(even) {
        background: #f0fdf4;
    }
    .score-table tbody tr:nth-child(odd) {
        background: #ffffff;
    }

    .metric-pill {
        display:inline-flex;
        align-items:center;
        gap:0.4rem;
        padding:0.25rem 0.75rem;
        border-radius:999px;
        font-size:0.8rem;
        font-weight:600;
    }
    .metric-pill-green {
        background:#dcfce7;
        color:#166534;
    }
    .metric-pill-yellow {
        background:#fef9c3;
        color:#a16207;
    }
    .metric-pill-red {
        background:#fee2e2;
        color:#b91c1c;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- LLM CLIENT ---------- #

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def call_llm(prompt: str, temperature: float = 0.2, max_tokens: int = 1600) -> str:
    """
    Wrapper around the OpenAI Responses API that:
    - calls the model
    - extracts the text
    """
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=max_tokens,
        temperature=temperature,
    )
    try:
        text = resp.output[0].content[0].text
    except Exception:
        raise RuntimeError("Unexpected model output format (no content).")

    # strip accidental markdown fences
    text = text.replace("```json", "").replace("```", "").strip()
    return text


def parse_json_from_text(raw: str) -> Dict[str, Any]:
    """Try to pull the first {...} JSON block from the LLM output."""
    first = raw.find("{")
    last = raw.rfind("}")
    if first == -1 or last == -1:
        raise ValueError("No JSON object found in model output.")
    return json.loads(raw[first : last + 1])


# ---------- STATIC DATA ---------- #

TASK1_CATEGORIES = [
    # high-level categories
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
    # granular categories you asked to add
    "Laptop Components (Displays, Batteries)",
    "Server Processors (CPUs)",
    "Semiconductor & Microchips",
    "Standard Cables & Connectors",
    "Cooling Systems & Thermal Solutions",
    "Power Supply Units",
    "Networking Equipment (Switches, Routers)",
    "Data Storage Devices (SSDs)",
]

TASK2_ITEMS = [
    "Laptop Components (Displays, Batteries, Keyboards)",
    "Server Components (Processors, Memory, Storage)",
    "Semiconductor & Microchips",
    "Printed Circuit Boards (PCBs)",
    "Standard Cables & Connectors",
    "Cooling Systems & Thermal Solutions",
    "Power Supply Units",
    "Networking Equipment (Switches, Routers)",
    "Data Storage Devices (SSDs, HDDs)",
    "Graphics Processing Units (GPUs)",
    "Packaging Materials",
    "Logistics & Freight Services",
    "Green / Sustainable Materials",
    "Software Licensing",
    "Cloud Infrastructure Services",
    "IT Support & Consulting",
    "Security & Compliance Solutions",
    "Manufacturing Equipment & Tools",
    "Testing & Quality Assurance Equipment",
    "Raw Materials (Plastics, Metals, Composites)",
]

# ---------- PROMPTS ---------- #


def supplier_prompt(category: str) -> str:
    return textwrap.dedent(
        f"""
        You are a senior procurement analyst advising Dell Technologies.

        TASK: For the procurement category **"{category}"**, create supplier market intelligence.

        Return ONLY a valid JSON object with this exact structure:

        {{
          "category": "...",
          "marketOverview": "2-3 sentences about global market, key trends, and why it matters for Dell.",
          "topSuppliers": [
            {{
              "rank": 1,
              "name": "Supplier name",
              "headquarters": "City, Country",
              "marketShare": "~25% (estimate)",
              "keyCapabilities": ["capability 1", "capability 2", "capability 3", "capability 4"],
              "differentiators": "1–2 sentence explanation of what makes them unique.",
              "dellRelevance": "1–2 sentence explanation of why Dell should care."
            }}
          ],
          "countryRisks": [
            {{
              "country": "Country name",
              "overallRiskLevel": "Low / Medium / High",
              "supplierConcentration": "Low / Medium / High",
              "politicalRisk": {{
                "score": 1-10,
                "assessment": "short text",
                "keyFactors": ["factor1","factor2"]
              }},
              "logisticsRisk": {{
                "score": 1-10,
                "assessment": "short text",
                "keyFactors": ["factor1","factor2"]
              }},
              "complianceRisk": {{
                "score": 1-10,
                "assessment": "short text",
                "keyFactors": ["factor1","factor2"]
              }},
              "esgRisk": {{
                "score": 1-10,
                "assessment": "short text",
                "keyFactors": ["factor1","factor2"]
              }},
              "mitigation": "1–2 sentence risk mitigation suggestion for Dell."
            }}
          ]
        }}

        Rules:
        - Provide exactly 5 items in "topSuppliers".
        - Provide 3 or 4 countries in "countryRisks".
        - Do NOT include any markdown, code fences, or comments.
        """
    )


def contracts_prompt(items: str) -> str:
    return textwrap.dedent(
        f"""
        You are designing supply chain contract strategies for Dell Technologies.

        PROCUREMENT ITEMS (comma separated):
        {items}

        Consider these contract types:
        - Buy-back Contract
        - Revenue-Sharing Contract
        - Wholesale Price Contract
        - Quantity Flexibility Contract
        - Option Contract
        - Vendor Managed Inventory (VMI)
        - Cost-Sharing / Incentive Contract

        Return ONLY a JSON object:

        {{
          "categories": [
            {{
              "name": "Laptop Components (example)",
              "assessment": {{
                "demandPattern": "Stable / Seasonal / Highly volatile",
                "demandReason": "1–2 lines explanation",
                "marketCharacteristics": "1–2 lines on competition, lead times, etc.",
                "volumeFlexibility": "High / Medium / Low",
                "riskProfile": "1–2 lines on key supply risks"
              }},
              "recommendedContract": "one of the contract types above",
              "confidence": "High / Medium / Low",
              "justification": "3–4 lines linking demand, risk and contract logic.",
              "alternativeContract": "another contract type",
              "implementationConsiderations": [
                "bullet point",
                "bullet point"
              ],
              "keyContractClauses": [
                "bullet point",
                "bullet point"
              ]
            }}
          ],
          "contractComparison": {{
            "Buy-back Contract": {{
              "description": "1 short line",
              "bestFor": "when it works best",
              "advantages": ["adv1","adv2"],
              "disadvantages": ["dis1"],
              "dellExamples": ["illustrative Dell use-case"]
            }}
          }},
          "procurementRecommendations": [
            "concise recommendation",
            "another recommendation"
          ]
        }}

        - Create one object in "categories" for each procurement item.
        - No markdown or comments, pure JSON.
        """
    )


def scorecard_prompt_initial(category: str, suppliers: str) -> str:
    return textwrap.dedent(
        f"""
        You are evaluating suppliers for Dell Technologies.

        CATEGORY: {category}
        SUPPLIERS: {suppliers}

        Dimensions and weights (initial):
        - Technical Capability – 25%
        - Quality Performance – 20%
        - Financial Health – 20%
        - ESG Compliance – 20%
        - Innovation Capability – 15%

        Score each supplier 0–100 on each dimension. Calculate a weighted total (0–100) using the weights.

        Return ONLY JSON:

        {{
          "evaluationTitle": "Initial Scorecard",
          "category": "{category}",
          "evaluationDate": "YYYY-MM-DD",
          "dimensions": [
            {{ "name":"Technical Capability","weight":25,"description":"..." }},
            {{ "name":"Quality Performance","weight":20,"description":"..." }},
            {{ "name":"Financial Health","weight":20,"description":"..." }},
            {{ "name":"ESG Compliance","weight":20,"description":"..." }},
            {{ "name":"Innovation Capability","weight":15,"description":"..." }}
          ],
          "supplierScores": [
            {{
              "supplierName": "Supplier name",
              "scores": {{
                "Technical Capability": 85,
                "Quality Performance": 82,
                "Financial Health": 90,
                "ESG Compliance": 78,
                "Innovation Capability": 80
              }},
              "weightedTotal": 84.5,
              "rating": "Excellent / Good / Average / Poor",
              "strengths": ["strength1","strength2"],
              "weaknesses": ["weak1"]
            }}
          ],
          "bestSupplier": {{
            "name": "Best supplier",
            "score": 88.7,
            "reasoning": "3–5 lines comparative reasoning"
          }},
          "conclusion": "2–3 lines summary and recommendation for Dell."
        }}

        - Ensure weightedTotal is mathematically consistent with the scores and weights.
        - Include all suppliers provided in SUPPLIERS.
        """
    )


def scorecard_prompt_refined(category: str, previous_json: Dict[str, Any]) -> str:
    prev = json.dumps(previous_json)
    return textwrap.dedent(
        f"""
        Refine the previous scorecard for Dell Technologies.

        CATEGORY: {category}

        New weights:
        - Technical Capability – 30%
        - Quality Performance – 25%
        - ESG Compliance – 25%
        - Financial Health – 15%
        - Innovation Capability – 5%

        STARTING POINT (previous scorecard JSON):
        {prev}

        Create a REFINED scorecard with the same suppliers but:
        - Apply the new weights and recalculate weighted totals.
        - For each dimension, add 2–3 specific KPIs.

        Return ONLY JSON:

        {{
          "evaluationTitle": "Refined Scorecard",
          "category": "{category}",
          "evaluationDate": "YYYY-MM-DD",
          "dimensions": [
            {{
              "name":"Technical Capability",
              "weight":30,
              "description":"...",
              "kpis":[
                {{"name":"KPI name","description":"what it measures","importance":"why it matters"}}
              ]
            }}
          ],
          "supplierScores": [... same structure as before, but recalculated ...],
          "bestSupplier": {{
            "name":"Best supplier",
            "score": 0-100,
            "reasoning":"3–5 lines"
          }},
          "conclusion": "2–3 line summary for Dell."
        }}

        - Make sure weights sum to 100.
        - No markdown, no comments – pure JSON.
        """
    )


# ---------- UI HELPERS ---------- #


def risk_pill(level: str) -> str:
    lvl = (level or "").lower()
    if "high" in lvl:
        cls = "metric-pill-red"
        txt = "High"
    elif "medium" in lvl:
        cls = "metric-pill-yellow"
        txt = "Medium"
    else:
        cls = "metric-pill-green"
        txt = "Low"
    return f'<span class="metric-pill {cls}">{txt} risk</span>'


# ---------- LAYOUT ---------- #

# HEADER
st.markdown(
    '<div class="main-card">',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pill">Dell Technologies · Procurement · GenAI</div>
    <div class="big-title">AI-Enabled Procurement Decision Support</div>
    <p class="subtitle">
      Use GenAI to generate global supplier intelligence, recommend supply-chain contract types,
      and build supplier evaluation scorecards for Dell.
    </p>
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

error_placeholder = st.empty()

# ---------- TAB 1: SUPPLIER MARKET INTELLIGENCE ---------- #
with tabs[0]:
    st.markdown(
        """
        <div class="section-card">
          <div class="section-header">
            <span class="emoji">🔍</span>
            <div>
              <div class="section-title">Task 1 – Supplier Market Intelligence</div>
              <div class="section-subtitle">
                Select a procurement category for Dell and generate top suppliers and country-level sourcing risks.
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.4, 1])

    with col1:
        category = st.selectbox(
            "Select procurement category",
            ["-- Select Category --"] + TASK1_CATEGORIES,
            index=0,
        )

    with col2:
        st.write("")
        st.write("")
        gen_task1 = st.button("🔎 Generate Intelligence", key="btn_task1")

    if gen_task1 and category == "-- Select Category --":
        error_placeholder.error("Please select a category before generating intelligence.")

    supplier_result = None
    if gen_task1 and category != "-- Select Category --":
        error_placeholder.empty()
        with st.spinner("Calling GenAI for supplier intelligence…"):
            raw = call_llm(supplier_prompt(category))
            supplier_result = parse_json_from_text(raw)

    # allow showing previous result if user already ran once during this session
    if "supplier_result" not in st.session_state:
        st.session_state.supplier_result = None
    if supplier_result:
        st.session_state.supplier_result = supplier_result

    supplier_result = st.session_state.supplier_result

    if supplier_result:
        st.markdown("### 🌍 Market Overview")
        st.markdown(
            f"> **{supplier_result.get('category','')}** — {supplier_result.get('marketOverview','')}"
        )
        st.markdown("---")

        # Top suppliers
        st.markdown("### 🏢 Top 5 Global Suppliers")
        for s in supplier_result.get("topSuppliers", []):
            with st.container():
                st.markdown(
                    f"""
                    <div style="padding:0.75rem 1rem; border-radius:14px; border:1px solid rgba(148,163,184,0.5); margin-bottom:0.8rem; background:#f9fafb;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                          <div style="font-weight:700; font-size:1.02rem;">{s.get('rank','?')}. {s.get('name','')}</div>
                          <div style="font-size:0.85rem; color:#6b7280;">📍 {s.get('headquarters','')}</div>
                        </div>
                        <div style="text-align:right;">
                          <div style="font-size:0.85rem; color:#64748b;">Market share</div>
                          <div style="font-weight:700;">{s.get('marketShare','')}</div>
                        </div>
                      </div>
                      <div style="margin-top:0.6rem; font-size:0.9rem;">
                        <b>Key capabilities:</b> {", ".join(s.get("keyCapabilities", []))}
                      </div>
                      <div style="margin-top:0.25rem; font-size:0.9rem;">
                        <b>Differentiators:</b> {s.get("differentiators","")}
                      </div>
                      <div style="margin-top:0.25rem; font-size:0.9rem;">
                        <b>Dell relevance:</b> {s.get("dellRelevance","")}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("### ⚠️ Country-Level Sourcing Risks")
        for r in supplier_result.get("countryRisks", []):
            col_left, col_right = st.columns([1.4, 1])
            with col_left:
                st.markdown(
                    f"#### {r.get('country','')} &nbsp;&nbsp; {risk_pill(r.get('overallRiskLevel',''))}",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"*Supplier concentration:* **{r.get('supplierConcentration','')}**"
                )
            with col_right:
                st.markdown(
                    f"**Mitigation for Dell:** {r.get('mitigation','')}",
                )

            # risk grid
            grid = st.columns(4)
            dims = [
                ("Political", r.get("politicalRisk", {})),
                ("Logistics", r.get("logisticsRisk", {})),
                ("Compliance", r.get("complianceRisk", {})),
                ("ESG", r.get("esgRisk", {})),
            ]
            for (label, data), col in zip(dims, grid):
                score = data.get("score", "")
                col.markdown(
                    f"""
                    <div style="padding:0.7rem; border-radius:12px; background:#f9fafb; border:1px solid rgba(148,163,184,0.5); font-size:0.85rem;">
                      <div style="font-weight:600; margin-bottom:0.1rem;">{label}</div>
                      <div style="font-size:0.95rem; font-weight:700;">{score}/10</div>
                      <div style="color:#6b7280; margin-top:0.2rem;">{data.get("assessment","")}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")

# ---------- TAB 2: CONTRACT SELECTION ---------- #
with tabs[1]:
    st.markdown(
        """
        <div class="section-card section-card-purple">
          <div class="section-header">
            <span class="emoji">📑</span>
            <div>
              <div class="section-title">Task 2 – GenAI-Supported Contract Selection</div>
              <div class="section-subtitle">
                Select which Dell procurement items you are sourcing and let GenAI recommend the most suitable contract type.
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_items = st.multiselect(
        "Select Dell procurement items",
        options=TASK2_ITEMS,
        default=[],
        help="You can select multiple items – each will get its own contract recommendation.",
    )

    gen_task2 = st.button("📊 Analyze Contract Options", key="btn_task2")

    contract_result = None
    if gen_task2 and not selected_items:
        error_placeholder.error("Please select at least one procurement item.")
    elif gen_task2 and selected_items:
        error_placeholder.empty()
        with st.spinner("Calling GenAI for contract recommendations…"):
            raw = call_llm(contracts_prompt(", ".join(selected_items)), temperature=0.25)
            contract_result = parse_json_from_text(raw)

    if "contract_result" not in st.session_state:
        st.session_state.contract_result = None
    if contract_result:
        st.session_state.contract_result = contract_result

    contract_result = st.session_state.contract_result

    if contract_result:
        st.markdown("### 🧾 Contract Recommendations by Item")
        for cat in contract_result.get("categories", []):
            st.markdown(
                f"""
                <div style="padding:1rem 1.1rem; border-radius:18px; border:1px solid rgba(192,132,252,0.6); margin-bottom:0.9rem; background:#faf5ff;">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1rem;">
                    <div style="flex:1;">
                      <div style="font-size:1.05rem; font-weight:700; color:#4c1d95;">{cat.get("name","")}</div>
                      <div style="margin-top:0.25rem; font-size:0.9rem; color:#4b5563;">
                        {cat.get("assessment",{}).get("demandReason","")}
                      </div>
                    </div>
                    <div style="text-align:right;">
                      <div style="font-size:0.8rem; text-transform:uppercase; color:#6b21a8; letter-spacing:0.06em;">Recommended contract</div>
                      <div style="font-size:0.96rem; font-weight:700; color:#4c1d95;">{cat.get("recommendedContract","")}</div>
                      <div style="font-size:0.82rem; color:#6b7280; margin-top:0.15rem;">Alternative: {cat.get("alternativeContract","")}</div>
                      <div style="font-size:0.82rem; margin-top:0.35rem;">
                        <span class="metric-pill metric-pill-green">Confidence: {cat.get("confidence","")}</span>
                      </div>
                    </div>
                  </div>
                  <div style="margin-top:0.65rem; font-size:0.9rem;">
                    <b>Why this works:</b> {cat.get("justification","")}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Comparison section
        if contract_result.get("contractComparison"):
            st.markdown("### 📚 Contract Type Comparison")
            for name, info in contract_result["contractComparison"].items():
                with st.expander(f"📄 {name}", expanded=False):
                    st.markdown(f"**Description**: {info.get('description','')}")
                    st.markdown(f"**Best for**: {info.get('bestFor','')}")
                    st.markdown("**Advantages:**")
                    for a in info.get("advantages", []):
                        st.markdown(f"- {a}")
                    st.markdown("**Disadvantages:**")
                    for d in info.get("disadvantages", []):
                        st.markdown(f"- {d}")
                    if info.get("dellExamples"):
                        st.markdown("**Dell-specific examples:**")
                        for ex in info["dellExamples"]:
                            st.markdown(f"- {ex}")

        if contract_result.get("procurementRecommendations"):
            st.markdown("### ✅ Overall Procurement Recommendations")
            for r in contract_result["procurementRecommendations"]:
                st.markdown(f"- {r}")

# ---------- TAB 3: SUPPLIER SCORECARD ---------- #
with tabs[2]:
    st.markdown(
        """
        <div class="section-card section-card-green">
          <div class="section-header">
            <span class="emoji">🏅</span>
            <div>
              <div class="section-title">Task 3 – Supplier Evaluation Scorecard</div>
              <div class="section-subtitle">
                Based on Task 1 suppliers, build an initial weighted scorecard and then a refined scorecard with KPIs.
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("supplier_result"):
        st.info("Please run **Task 1 – Supplier Market Intelligence** first to get the supplier list.")
    else:
        sup_res = st.session_state.supplier_result
        category = sup_res.get("category", "Selected category")
        supplier_names = [s.get("name", "") for s in sup_res.get("topSuppliers", [])]
        supplier_str = ", ".join(supplier_names)

        colA, colB = st.columns([1.2, 1])
        with colA:
            st.markdown(f"**Category:** {category}")
            st.markdown(f"**Suppliers to evaluate:** {', '.join(supplier_names)}")
        with colB:
            st.write("")
            st.write("")
            gen_score = st.button("🏁 Generate Scorecards", key="btn_task3")

        score_initial = score_refined = None

        if gen_score:
            error_placeholder.empty()
            with st.spinner("Building initial scorecard…"):
                raw1 = call_llm(scorecard_prompt_initial(category, supplier_str), temperature=0.15)
                score_initial = parse_json_from_text(raw1)
            with st.spinner("Refining scorecard & KPIs…"):
                raw2 = call_llm(scorecard_prompt_refined(category, score_initial), temperature=0.15)
                score_refined = parse_json_from_text(raw2)

            st.session_state.score_initial = score_initial
            st.session_state.score_refined = score_refined

        score_initial = st.session_state.get("score_initial")
        score_refined = st.session_state.get("score_refined")

        if score_initial:
            st.markdown("### 📊 Initial Scorecard")

            dims = score_initial.get("dimensions", [])
            scores = score_initial.get("supplierScores", [])

            rows = []
            for s in scores:
                row = {"Supplier": s["supplierName"]}
                for d in dims:
                    row[d["name"]] = s["scores"].get(d["name"], None)
                row["Weighted total"] = s.get("weightedTotal", None)
                row["Rating"] = s.get("rating", "")
                rows.append(row)

            df = pd.DataFrame(rows)

            # Style: striping + coloured total column
            styled = (
                df.style.format("{:.1f}", subset=["Weighted total"])
                .background_gradient(subset=["Weighted total"], cmap="Greens")
            )

            st.dataframe(
                styled,
                use_container_width=True,
                hide_index=True,
            )

            if score_initial.get("bestSupplier"):
                bs = score_initial["bestSupplier"]
                st.markdown(
                    f"""
                    <div style="margin-top:0.9rem; padding:1rem 1.1rem; border-radius:18px; border:1px solid #86efac; background:#ecfdf5;">
                      <div style="font-size:0.95rem; text-transform:uppercase; letter-spacing:0.08em; color:#047857; font-weight:700; margin-bottom:0.3rem;">
                        Best supplier (initial)
                      </div>
                      <div style="font-size:1.15rem; font-weight:800; color:#065f46;">{bs.get("name","")}</div>
                      <div style="font-size:0.95rem; margin-top:0.1rem;">Score: <b>{bs.get("score","")}</b></div>
                      <div style="font-size:0.9rem; margin-top:0.4rem; color:#064e3b;">
                        {bs.get("reasoning","")}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if score_refined:
            st.markdown("### 🧠 Refined Scorecard (with KPIs)")

            dims_r = score_refined.get("dimensions", [])
            scores_r = score_refined.get("supplierScores", [])

            rows_r = []
            for s in scores_r:
                row = {"Supplier": s["supplierName"]}
                for d in dims_r:
                    row[d["name"]] = s["scores"].get(d["name"], None)
                row["Weighted total"] = s.get("weightedTotal", None)
                row["Rating"] = s.get("rating", "")
                rows_r.append(row)

            df_r = pd.DataFrame(rows_r)
            styled_r = (
                df_r.style.format("{:.1f}", subset=["Weighted total"])
                .background_gradient(subset=["Weighted total"], cmap="Blues")
            )

            st.dataframe(
                styled_r,
                use_container_width=True,
                hide_index=True,
            )

            # KPI cards per dimension
            st.markdown("#### 🔬 Dimension KPIs")
            for d in dims_r:
                with st.expander(
                    f"{d.get('name','')} – weight {d.get('weight',0)}%", expanded=False
                ):
                    st.markdown(f"_{d.get('description','')}_")
                    st.markdown("**KPIs to track:**")
                    for k in d.get("kpis", []):
                        st.markdown(
                            f"- **{k.get('name','')}** – {k.get('description','')}  \n"
                            f"  ↳ _Why important for Dell:_ {k.get('importance','')}"
                        )

            if score_refined.get("bestSupplier"):
                bs = score_refined["bestSupplier"]
                st.markdown(
                    f"""
                    <div style="margin-top:0.9rem; padding:1rem 1.1rem; border-radius:18px; border:1px solid #bfdbfe; background:#eff6ff;">
                      <div style="font-size:0.95rem; text-transform:uppercase; letter-spacing:0.08em; color:#1d4ed8; font-weight:700; margin-bottom:0.3rem;">
                        Best supplier (refined)
                      </div>
                      <div style="font-size:1.15rem; font-weight:800; color:#1d4ed8;">{bs.get("name","")}</div>
                      <div style="font-size:0.95rem; margin-top:0.1rem;">Score: <b>{bs.get("score","")}</b></div>
                      <div style="font-size:0.9rem; margin-top:0.4rem; color:#1e40af;">
                        {bs.get("reasoning","")}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

st.markdown("</div>", unsafe_allow_html=True)  # close main-card
