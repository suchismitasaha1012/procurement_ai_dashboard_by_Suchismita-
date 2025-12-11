import json
import streamlit as st
import pandas as pd
from openai import OpenAI

# --------------------------------------------------
# BASIC PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AI-Enabled Procurement Decision Support – Dell",
    layout="wide",
)

st.title("AI-Enabled Procurement Decision Support")
st.caption("Company: **Dell Technologies** | Use case: AI-driven supplier intelligence, contract selection, and evaluation scorecards.")

# --------------------------------------------------
# OPENAI HELPER
# --------------------------------------------------
def call_llm(prompt: str, max_tokens: int = 1500) -> str | None:
    """Call OpenAI Responses API and safely return plain text."""
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OPENAI_API_KEY missing in Streamlit Secrets.")
        return None

    try:
        client = OpenAI(api_key=api_key)

        resp = client.responses.create(
            model="gpt-5-nano",          # test/freemium model
            input=prompt,
            max_output_tokens=max_tokens,
        )

        # Safely extract text from response
        if not resp.output:
            st.error("Model returned empty output.")
            return None
        first_block = resp.output[0]
        if not getattr(first_block, "content", None):
            st.error("Unexpected model output format (no content).")
            return None
        text = first_block.content[0].text
        return text
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        return None


def extract_json_from_text(text: str) -> dict:
    """Extract first {...} block from text and parse as JSON."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model output.")
    json_str = text[start : end + 1]
    return json.loads(json_str)


# --------------------------------------------------
# STATIC DATA (CATEGORIES & PRODUCTS)
# --------------------------------------------------
CATEGORIES = [
    "Electronics & Semiconductors",
    "Packaging Materials",
    "Logistics & Transportation",
    "Chemicals & Materials",
    "IT Services & Software",
    "Hardware Components",
    "Cloud Computing Services",
    "Network Equipment",
    "Data Storage Solutions",
    "Manufacturing Equipment",
    "Office Supplies",
    "Energy & Utilities",
]

DELL_PRODUCTS = [
    "Laptop Components (Displays, Batteries, Keyboards)",
    "Server Components (Processors, Memory, Storage)",
    "Semiconductor & Microchips",
    "Printed Circuit Boards (PCBs)",
    "Cooling Systems & Thermal Solutions",
    "Power Supply Units",
    "Networking Equipment (Switches, Routers)",
    "Data Storage Devices (SSDs, HDDs)",
    "Graphics Processing Units (GPUs)",
    "Packaging Materials",
    "Logistics & Freight Services",
    "Software Licensing",
    "Cloud Infrastructure Services",
    "IT Support & Consulting",
    "Security & Compliance Solutions",
    "Manufacturing Equipment & Tools",
    "Testing & Quality Assurance Equipment",
    "Raw Materials (Plastics, Metals, Composites)",
]

# --------------------------------------------------
# SESSION STATE KEYS
# --------------------------------------------------
for key, default in [
    ("selected_category", None),
    ("market_result", None),
    ("selected_products", []),
    ("contract_result", None),
    ("scorecard_initial", None),
    ("scorecard_refined", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# --------------------------------------------------
# HELPER FOR COLORS (risk labels etc.)
# --------------------------------------------------
def risk_label(score_or_level: str) -> str:
    """Return colored label HTML for risk."""
    if score_or_level is None:
        return ""
    s = str(score_or_level).lower()
    try:
        n = int(score_or_level)
    except Exception:
        n = None

    color = "#16a34a"   # green
    bg = "#dcfce7"
    label = str(score_or_level)

    if "high" in s or (n is not None and n >= 8):
        color, bg = "#b91c1c", "#fee2e2"  # red
    elif "medium" in s or (n is not None and n >= 5):
        color, bg = "#92400e", "#fef3c7"  # amber

    return f"<span style='background:{bg};color:{color};padding:2px 8px;border-radius:999px;font-size:0.8rem;font-weight:600;'>{label}</span>"


def contract_badge(contract_type: str) -> str:
    colors = {
        "Buy-back Contract": "#2563eb",
        "Revenue-Sharing Contract": "#7c3aed",
        "Wholesale Price Contract": "#16a34a",
        "Quantity Flexibility Contract": "#ca8a04",
        "Option Contract": "#dc2626",
        "VMI": "#4f46e5",
        "Cost-Sharing Contract": "#0d9488",
        "Cost-Sharing/Incentive Contract": "#0d9488",
    }
    c = colors.get(contract_type, "#4b5563")
    return f"<span style='background:{c};color:white;padding:4px 10px;border-radius:999px;font-weight:600;font-size:0.8rem;'>{contract_type}</span>"


# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    [
        "1️⃣ Supplier Market Intelligence",
        "2️⃣ Contract Type Recommendation",
        "3️⃣ Supplier Evaluation Scorecard",
    ]
)

# ==================================================
# TAB 1 – SUPPLIER MARKET INTELLIGENCE
# ==================================================
with tab1:
    st.subheader("Task 1 – Supplier Market Intelligence using GenAI")
    st.write(
        "Select a **procurement category** relevant to Dell and generate structured global "
        "supplier intelligence (top suppliers, capabilities & country-level risks)."
    )

    col_sel, col_btn = st.columns([2, 1])
    with col_sel:
        st.session_state.selected_category = st.selectbox(
            "Select procurement category",
            ["-- Select --"] + CATEGORIES,
            index=0 if st.session_state.selected_category is None else
            (["-- Select --"] + CATEGORIES).index(
                st.session_state.selected_category
            ) if st.session_state.selected_category in CATEGORIES else 0,
        )
    with col_btn:
        generate_market = st.button(
            "🔍 Generate Supplier Intelligence",
            use_container_width=True,
        )

    if generate_market:
        if (
            not st.session_state.selected_category
            or st.session_state.selected_category == "-- Select --"
        ):
            st.error("Please choose a category first.")
        else:
            category = st.session_state.selected_category
            with st.spinner("Calling GenAI for market intelligence..."):
                prompt = f"""
Analyze supplier market for Dell Technologies in the category: "{category}".

Return ONLY valid JSON (no markdown) with the following structure:

{{
  "category": "{category}",
  "marketOverview": "2-3 sentences overview of supplier market and trends",
  "topSuppliers": [
    {{
      "rank": 1,
      "name": "Company name",
      "headquarters": "City, Country",
      "marketShare": "e.g., 25%",
      "annualRevenue": "$ value or 'N/A'",
      "keyCapabilities": ["cap1","cap2","cap3","cap4"],
      "differentiators": "1-2 lines about what makes them unique",
      "dellRelevance": "Why this supplier is relevant for Dell"
    }}
  ],
  "countryRisks": [
    {{
      "country": "Country name",
      "supplierConcentration": "High/Medium/Low",
      "politicalRisk": {{"score": "1-10", "assessment": "short text", "keyFactors": ["f1","f2"]}},
      "logisticsRisk": {{"score": "1-10", "assessment": "short text", "keyFactors": ["f1","f2"]}},
      "complianceRisk": {{"score": "1-10", "assessment": "short text", "keyFactors": ["f1","f2"]}},
      "esgRisk": {{"score": "1-10", "assessment": "short text", "keyFactors": ["f1","f2"]}},
      "overallRiskLevel": "High/Medium/Low",
      "mitigation": "Key mitigation strategies for Dell"
    }}
  ]
}}

Provide **exactly 5** suppliers and **3-4** countries.
"""

                text = call_llm(prompt, max_tokens=1800)
                if text:
                    try:
                        parsed = extract_json_from_text(text)
                        if not parsed.get("topSuppliers") or not parsed.get(
                            "countryRisks"
                        ):
                            raise ValueError(
                                "Missing 'topSuppliers' or 'countryRisks' in JSON."
                            )
                        st.session_state.market_result = parsed
                    except Exception as e:
                        st.error(f"Failed to parse model output as JSON: {e}")
                        st.session_state.market_result = None

    market = st.session_state.market_result
    if market:
        st.markdown("---")
        st.markdown(f"### 🌍 Market Overview – {market.get('category','')}")
        st.write(market.get("marketOverview", ""))

        # Top suppliers
        st.markdown("#### 📈 Top 5 Global Suppliers")
        for s in market.get("topSuppliers", []):
            with st.expander(f"{s.get('rank','?')}. {s.get('name','Unknown Supplier')}"):
                st.write(f"**Headquarters:** {s.get('headquarters','N/A')}")
                st.write(f"**Market share:** {s.get('marketShare','N/A')}")
                st.write(f"**Annual revenue:** {s.get('annualRevenue','N/A')}")
                st.write("**Key capabilities:**")
                st.write(", ".join(s.get("keyCapabilities", [])))
                st.write("**Differentiators:**", s.get("differentiators", ""))
                st.write("**Dell relevance:**", s.get("dellRelevance", ""))

        # Country risks
        st.markdown("#### ⚠️ Country-Level Sourcing Risks")
        for r in market.get("countryRisks", []):
            st.markdown(f"**{r.get('country','Unknown Country')}**", help=r.get("mitigation",""))
            cols = st.columns(4)
            with cols[0]:
                st.markdown(
                    "Political<br>"
                    + risk_label(r.get("politicalRisk", {}).get("score", "N/A")),
                    unsafe_allow_html=True,
                )
            with cols[1]:
                st.markdown(
                    "Logistics<br>"
                    + risk_label(r.get("logisticsRisk", {}).get("score", "N/A")),
                    unsafe_allow_html=True,
                )
            with cols[2]:
                st.markdown(
                    "Compliance<br>"
                    + risk_label(r.get("complianceRisk", {}).get("score", "N/A")),
                    unsafe_allow_html=True,
                )
            with cols[3]:
                st.markdown(
                    "ESG<br>"
                    + risk_label(r.get("esgRisk", {}).get("score", "N/A")),
                    unsafe_allow_html=True,
                )
            st.markdown(
                "Overall risk: "
                + risk_label(r.get("overallRiskLevel", "Unknown")),
                unsafe_allow_html=True,
            )
            st.write("**Mitigation strategy for Dell:**", r.get("mitigation", "—"))
            st.markdown("---")

# ==================================================
# TAB 2 – CONTRACT TYPE RECOMMENDATION
# ==================================================
with tab2:
    st.subheader("Task 2 – GenAI-Supported Contract Selection for Procurement")
    st.write(
        "Select one or more **Dell procurement items**. The tool will suggest appropriate "
        "supply chain contract types (Buy-back, Revenue-Sharing, Wholesale Price, Quantity Flexibility, "
        "Option, VMI, Cost-Sharing, etc.) for each selected item."
    )

    selected_products = st.multiselect(
        "Select products / services",
        options=DELL_PRODUCTS,
        default=st.session_state.selected_products,
    )
    st.session_state.selected_products = selected_products

    analyze_contracts = st.button(
        "📄 Analyze Contract Options", use_container_width=True
    )

    if analyze_contracts:
        if not selected_products:
            st.error("Please select at least one product / service.")
        else:
            items = ", ".join(selected_products)
            with st.spinner("Analyzing best-fit contract types..."):
                prompt = f"""
You are a supply chain & procurement expert for Dell Technologies.

Products/services selected:
{items}

Consider the following contract types:
- Buy-back Contract
- Revenue-Sharing Contract
- Wholesale Price Contract
- Quantity Flexibility Contract
- Option Contract
- Vendor Managed Inventory (VMI)
- Cost-Sharing Contract
- Cost-Sharing/Incentive Contract

Return ONLY valid JSON in this structure:

{{
  "analysisDate": "YYYY-MM-DD",
  "categories": [
    {{
      "name": "product name",
      "assessment": {{
        "demandPattern": "Stable/Seasonal/Boom-Bust",
        "demandReason": "1-2 lines",
        "marketCharacteristics": "short description",
        "volumeFlexibility": "High/Medium/Low",
        "riskProfile": "key risks for Dell"
      }},
      "recommendedContract": "contract type from list above",
      "confidence": "High/Medium/Low",
      "justification": "3-4 lines on why this contract is preferred",
      "alternativeContract": "another contract type",
      "implementationConsiderations": ["c1","c2"],
      "keyContractClauses": ["cl1","cl2"]
    }}
  ],
  "contractComparison": {{
    "Buy-back Contract": {{
      "description": "short description",
      "bestFor": "when it works best",
      "advantages": ["a1","a2"],
      "disadvantages": ["d1"],
      "dellExamples": ["example use case"]
    }}
  }},
  "procurementRecommendations": ["summary1","summary2"]
}}

Make sure every selected product appears in categories[].
"""
                text = call_llm(prompt, max_tokens=2200)
                if text:
                    try:
                        parsed = extract_json_from_text(text)
                        st.session_state.contract_result = parsed
                    except Exception as e:
                        st.error(f"Failed to parse contract JSON: {e}")
                        st.session_state.contract_result = None

    contract = st.session_state.contract_result
    if contract:
        st.markdown("---")
        st.markdown("### 🎯 Contract Recommendations by Category")
        for c in contract.get("categories", []):
            st.markdown(f"#### {c.get('name','Category')}")
            st.markdown(
                contract_badge(c.get("recommendedContract", "N/A")),
                unsafe_allow_html=True,
            )
            st.write("**Confidence:**", c.get("confidence", "N/A"))
            st.write("**Justification:**", c.get("justification", ""))
            assessment = c.get("assessment", {})
            st.write("**Demand pattern:**", assessment.get("demandPattern", ""))
            st.write(
                "**Market characteristics:**",
                assessment.get("marketCharacteristics", ""),
            )
            st.write("**Volume flexibility:**", assessment.get("volumeFlexibility", ""))
            st.write("**Risk profile:**", assessment.get("riskProfile", ""))
            st.write("**Alternative contract:**", c.get("alternativeContract", ""))
            if c.get("implementationConsiderations"):
                st.write("**Implementation considerations:**")
                for ic in c["implementationConsiderations"]:
                    st.write(f"- {ic}")
            if c.get("keyContractClauses"):
                st.write("**Key contract clauses to emphasise:**")
                for clause in c["keyContractClauses"]:
                    st.write(f"- {clause}")
            st.markdown("---")

        if contract.get("procurementRecommendations"):
            st.markdown("### 📌 Overall Procurement Recommendations")
            for r in contract["procurementRecommendations"]:
                st.write(f"- {r}")

# ==================================================
# TAB 3 – SUPPLIER EVALUATION SCORECARD
# ==================================================
with tab3:
    st.subheader("Task 3 – GenAI-Enhanced Supplier Evaluation Scorecard")
    st.write(
        "This task builds a **two-stage supplier scorecard** for the suppliers identified in Task 1.\n"
        "- Stage 1: Initial scorecard with base weights.\n"
        "- Stage 2: Refined scorecard with updated weights and KPIs."
    )

    col_left, col_right = st.columns([1, 1])
    with col_left:
        generate_scores = st.button(
            "🏅 Generate Supplier Scorecards",
            use_container_width=True,
        )
    with col_right:
        if not st.session_state.market_result:
            st.info(
                "Complete **Task 1: Supplier Market Intelligence** first so we know which suppliers to evaluate."
            )

    if generate_scores:
        market = st.session_state.market_result
        if not market or not market.get("topSuppliers"):
            st.error("Please complete Task 1 first (no suppliers found).")
        else:
            supplier_names = ", ".join(
                [s.get("name", "Supplier") for s in market["topSuppliers"]]
            )
            category = market.get("category", "Dell Procurement Category")

            # --------- First (initial) scorecard ----------
            with st.spinner("Generating initial supplier scorecard..."):
                prompt1 = f"""
You are designing a supplier evaluation scorecard for Dell Technologies.

Suppliers: {supplier_names}
Category: {category}

Dimensions and base weights:
- Technical Capability – 25%
- Quality Performance – 20%
- Financial Health – 20%
- ESG Compliance – 20%
- Innovation Capability – 15%

For each supplier, score each dimension from 0–100 and compute weightedTotal.

Return ONLY valid JSON in this structure:

{{
  "evaluationTitle": "Initial Scorecard",
  "category": "{category}",
  "evaluationDate": "YYYY-MM-DD",
  "dimensions": [
    {{"name": "Technical Capability", "weight": 25, "description": "short description"}},
    {{"name": "Quality Performance", "weight": 20, "description": "short description"}},
    {{"name": "Financial Health", "weight": 20, "description": "short description"}},
    {{"name": "ESG Compliance", "weight": 20, "description": "short description"}},
    {{"name": "Innovation Capability", "weight": 15, "description": "short description"}}
  ],
  "supplierScores": [
    {{
      "supplierName": "Supplier name",
      "scores": {{
        "Technical Capability": 85,
        "Quality Performance": 78,
        "Financial Health": 90,
        "ESG Compliance": 75,
        "Innovation Capability": 82
      }},
      "weightedTotal": 81.5,
      "rating": "Excellent/Good/Average/Poor",
      "strengths": ["s1","s2"],
      "weaknesses": ["w1"]
    }}
  ],
  "bestSupplier": {{"name": "best", "score": 85, "reasoning": "why best"}},
  "conclusion": "1-2 lines with recommendation."
}}

Make sure weightedTotal truly reflects the weights.
"""

                text1 = call_llm(prompt1, max_tokens=2000)
                if text1:
                    try:
                        initial = extract_json_from_text(text1)
                        if not initial.get("dimensions") or not initial.get(
                            "supplierScores"
                        ):
                            raise ValueError(
                                "Missing 'dimensions' or 'supplierScores' in initial scorecard."
                            )
                        st.session_state.scorecard_initial = initial
                    except Exception as e:
                        st.error(f"Failed to parse initial scorecard: {e}")
                        st.session_state.scorecard_initial = None

            initial = st.session_state.scorecard_initial
            if initial:
                # --------- Refined scorecard ----------
                with st.spinner("Refining scorecard with new weights & KPIs..."):
                    prompt2 = f"""
Refine the following Dell supplier scorecard with new weights and KPIs.

New weights:
- Technical Capability – 30%
- Quality Performance – 25%
- ESG Compliance – 25%
- Financial Health – 15%
- Innovation Capability – 5%

For each dimension, add 2-3 KPIs with name, description and importance.

Previous scorecard JSON:
{json.dumps(initial)}

Return ONLY valid JSON with the SAME structure as before, but:
- update weights
- recalculate weightedTotal
- add "kpis" list into each dimension item:

"kpis": [
  {{"name": "KPI name", "description": "what it measures", "importance": "why important"}}
]

"""
                    text2 = call_llm(prompt2, max_tokens=2200)
                    if text2:
                        try:
                            refined = extract_json_from_text(text2)
                            st.session_state.scorecard_refined = refined
                        except Exception as e:
                            st.error(f"Failed to parse refined scorecard: {e}")
                            st.session_state.scorecard_refined = None

    # ---------- Render scorecards ----------
    initial = st.session_state.scorecard_initial
    refined = st.session_state.scorecard_refined

    if initial:
        st.markdown("---")
        st.markdown("### 🟢 Initial Scorecard")
        st.write(
            f"**Category:** {initial.get('category','')}  |  **Date:** {initial.get('evaluationDate','')}"
        )
        dims = initial.get("dimensions", [])
        scores = initial.get("supplierScores", [])

        if scores:
            # Sort by weighted total descending
            scores_sorted = sorted(
                scores, key=lambda s: s.get("weightedTotal", 0), reverse=True
            )
            df_rows = []
            for s in scores_sorted:
                row = {"Supplier": s.get("supplierName", "")}
                for d in dims:
                    name = d.get("name", "")
                    row[name] = s.get("scores", {}).get(name, "")
                row["Weighted Total"] = s.get("weightedTotal", 0)
                row["Rating"] = s.get("rating", "")
                df_rows.append(row)
            df = pd.DataFrame(df_rows)
            st.dataframe(df, use_container_width=True)

        if initial.get("bestSupplier"):
            best = initial["bestSupplier"]
            st.markdown(
                f"**Best supplier:** {best.get('name','')} "
                f"– Score: {best.get('score','')}  \n"
                f"{best.get('reasoning','')}"
            )
        if initial.get("conclusion"):
            st.markdown(f"**Conclusion:** {initial['conclusion']}")

    if refined:
        st.markdown("---")
        st.markdown("### 🔵 Refined Scorecard (Updated Weights & KPIs)")
        st.write(
            f"**Category:** {refined.get('category','')}  |  **Date:** {refined.get('evaluationDate','')}"
        )

        dims_r = refined.get("dimensions", [])
        if dims_r:
            for d in dims_r:
                st.markdown(
                    f"#### {d.get('name','Dimension')} – {d.get('weight',0)}%"
                )
                st.write(d.get("description", ""))
                if d.get("kpis"):
                    st.write("**Key KPIs:**")
                    for k in d["kpis"]:
                        st.write(
                            f"- **{k.get('name','KPI')}** – {k.get('description','')} "
                            f"(_Importance: {k.get('importance','')}_)"
                        )

        if refined.get("bestSupplier"):
            best = refined["bestSupplier"]
            st.markdown(
                f"**Best supplier (refined):** {best.get('name','')} – "
                f"Score: {best.get('score','')}  \n"
                f"{best.get('reasoning','')}"
            )
