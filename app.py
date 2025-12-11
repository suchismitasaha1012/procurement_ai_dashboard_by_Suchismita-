import os
import json
import textwrap
import streamlit as st
from openai import OpenAI

# ---------- OpenAI Client ----------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error(
        "OPENAI_API_KEY is not set. "
        "Add it in Streamlit → Manage app → Settings → Secrets."
    )
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)


def call_llm(prompt: str, max_tokens: int = 2800) -> str:
    """
    Call OpenAI Responses API and robustly extract the text output.
    """
    try:
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            max_output_tokens=max_tokens,
        )

        # Primary expected path
        try:
            text = resp.output[0].content[0].text
        except Exception:
            # Fallback: scan all output items and content parts for text
            parts = []
            if getattr(resp, "output", None):
                for item in resp.output:
                    content = getattr(item, "content", None) or []
                    for c in content:
                        t = getattr(c, "text", None)
                        if t:
                            parts.append(t)
            text = "\n".join(parts)

        text = (text or "").strip()
        if not text:
            raise ValueError("Model returned empty content")
        return text

    except Exception as e:
        raise RuntimeError(f"Error calling OpenAI API: {e}")


def parse_json_str(raw: str):
    """
    Safely extract a single JSON object from the model text.
    Removes anything before the first '{' or after the last '}'.
    """
    if not raw:
        raise ValueError("Empty model response")

    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model did not return JSON")

    json_str = raw[start : end + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parsing failed: {e}\nRaw snippet: {json_str[:200]}...")


# ---------- Static Data ----------

# Task 1 categories (high-level + detailed Dell procurement categories)
PROCUREMENT_CATEGORIES = [
    # High-level categories (as in your screenshot)
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
    # More granular Dell-specific categories you requested
    "Laptop Components (Displays, Batteries)",
    "Server Processors (CPUs)",
    "Semiconductor & Microchips",
    "Standard Cables & Connectors",
    "Cooling Systems & Thermal Solutions",
    "Power Supply Units",
    "Networking Equipment (Switches, Routers)",
    "Data Storage Devices (SSDs)",
]

# Task 2 products / services (Dell items)
DELL_ITEMS = [
    "Laptop Components (Displays, Batteries, Keyboards)",
    "Server Components (Processors, Memory, Storage)",
    "Server Processors (CPUs)",
    "Semiconductor & Microchips",
    "Graphics Processing Units (GPUs)",
    "Standard Cables & Connectors",
    "Printed Circuit Boards (PCBs)",
    "Cooling Systems & Thermal Solutions",
    "Power Supply Units",
    "Networking Equipment (Switches, Routers)",
    "Data Storage Devices (SSDs, HDDs)",
    "Packaging Materials",
    "Logistics & Freight Services",
    "Green / Sustainable Materials & Packaging",
    "Cloud Infrastructure Services",
    "IT Support & Consulting",
]

# ---------- LLM Task Functions ----------


def gen_market_intel(category: str):
    prompt = textwrap.dedent(
        f"""
        You are a procurement intelligence analyst for Dell Technologies.

        Task: Analyse the global supplier market for the procurement category:
        "{category}".

        Output format:
        Return ONLY ONE JSON object (no markdown, no backticks), with exactly
        this shape:

        {{
          "category": "{category}",
          "marketOverview": "2–3 sentence overview of the global supply market.",
          "topSuppliers": [
            {{
              "rank": 1,
              "name": "Supplier name",
              "headquarters": "City, Country",
              "marketShare": "e.g., ~24% (estimate)",
              "annualRevenue": "e.g., ~$50B",
              "keyCapabilities": ["capability 1", "capability 2", "capability 3"],
              "differentiators": "Short paragraph on unique strengths vs peers.",
              "dellRelevance": "Why this supplier is relevant to Dell."
            }}
          ],
          "countryRisks": [
            {{
              "country": "Country name",
              "supplierConcentration": "High | Medium | Low",
              "politicalRisk": {{
                "score": "1–10",
                "assessment": "Short explanation",
                "keyFactors": ["factor 1", "factor 2"]
              }},
              "logisticsRisk": {{
                "score": "1–10",
                "assessment": "Short explanation",
                "keyFactors": ["factor 1", "factor 2"]
              }},
              "complianceRisk": {{
                "score": "1–10",
                "assessment": "Short explanation",
                "keyFactors": ["factor 1", "factor 2"]
              }},
              "esgRisk": {{
                "score": "1–10",
                "assessment": "Short explanation",
                "keyFactors": ["factor 1", "factor 2"]
              }},
              "overallRiskLevel": "Low | Medium | High",
              "mitigation": "2–3 key mitigation strategies"
            }}
          ]
        }}

        Provide:
        • exactly 5 suppliers in "topSuppliers"
        • 3 or 4 countries in "countryRisks".
        """
    )
    raw = call_llm(prompt)
    return parse_json_str(raw)


def gen_contract_analysis(selected_items):
    items_str = ", ".join(selected_items)
    prompt = textwrap.dedent(
        f"""
        You are advising Dell Technologies on supply chain contracts.

        Dell procurement items:
        {items_str}

        Contract types to consider:
        - Buy-back Contract
        - Revenue-Sharing Contract
        - Wholesale Price Contract
        - Quantity Flexibility Contract
        - Option Contract
        - Vendor-Managed Inventory (VMI)
        - Cost-Sharing Contract

        For EACH selected item:
        1. Assess demand pattern, market volatility, and volume flexibility.
        2. Recommend the most suitable contract type.
        3. Suggest one alternative contract that could also work.

        RETURN ONLY ONE JSON OBJECT with this exact structure (no markdown):

        {{
          "categories": [
            {{
              "name": "Exact item name",
              "assessment": {{
                "demandPattern": "Stable | Seasonal | Highly volatile",
                "demandReason": "1–2 sentence explanation",
                "marketCharacteristics": "2–3 sentence description",
                "volumeFlexibility": "High | Medium | Low",
                "riskProfile": "Summary of key risks"
              }},
              "recommendedContract": "One of the listed contract types",
              "confidence": "High | Medium | Low",
              "justification": "3–4 sentence business justification",
              "alternativeContract": "Another contract type from the list",
              "implementationConsiderations": [
                "bullet point 1",
                "bullet point 2"
              ],
              "keyContractClauses": [
                "clause focus 1",
                "clause focus 2"
              ]
            }}
          ],
          "contractComparison": {{
            "Buy-back Contract": {{
              "description": "Short description",
              "bestFor": "When it works best",
              "advantages": ["adv 1", "adv 2"],
              "disadvantages": ["risk 1"],
              "dellExamples": ["Example scenario"]
            }}
          }},
          "procurementRecommendations": [
            "Overall recommendation 1",
            "Overall recommendation 2"
          ]
        }}

        • Ensure each selected item appears once in "categories".
        • Do NOT add any commentary outside this JSON.
        """
    )
    raw = call_llm(prompt)
    return parse_json_str(raw)


def gen_scorecards(market_json):
    suppliers = ", ".join([s["name"] for s in market_json.get("topSuppliers", [])])
    category = market_json.get("category", "Dell procurement")

    # Initial scorecard
    prompt1 = textwrap.dedent(
        f"""
        You are building a supplier evaluation scorecard for Dell Technologies.

        Suppliers: {suppliers}
        Category: {category}

        Dimensions (weights in %):
        - Technical Capability (25)
        - Quality Performance (20)
        - Financial Health (20)
        - ESG Compliance (20)
        - Innovation Capability (15)

        For each supplier, score each dimension 0–100 and calculate a weighted total.

        RETURN ONLY ONE JSON OBJECT:

        {{
          "evaluationTitle": "Initial Scorecard",
          "category": "{category}",
          "evaluationDate": "YYYY-MM-DD",
          "dimensions": [
            {{
              "name": "Technical Capability",
              "weight": 25,
              "description": "Short explanation"
            }}
          ],
          "supplierScores": [
            {{
              "supplierName": "Name",
              "scores": {{
                "Technical Capability": 85,
                "Quality Performance": 78,
                "Financial Health": 90,
                "ESG Compliance": 75,
                "Innovation Capability": 82
              }},
              "weightedTotal": 81.5,
              "rating": "Excellent | Good | Average | Poor",
              "strengths": ["strength 1", "strength 2"],
              "weaknesses": ["weakness 1"]
            }}
          ],
          "bestSupplier": {{
            "name": "Best supplier name",
            "score": 88.2,
            "reasoning": "Why this supplier is best"
          }},
          "conclusion": "Overall recommendation"
        }}

        Ensure:
        • weightedTotal is correctly calculated using the weights.
        • One entry per supplier in "supplierScores".
        """
    )

    raw1 = call_llm(prompt1)
    score1 = parse_json_str(raw1)

    # Refined scorecard with new weights + KPIs
    prompt2 = textwrap.dedent(
        f"""
        Refine this supplier scorecard for Dell.

        Previous scorecard JSON:
        {json.dumps(score1)}

        New weights:
        - Technical Capability: 30%
        - Quality Performance: 25%
        - ESG Compliance: 25%
        - Financial Health: 15%
        - Innovation Capability: 5%

        Add 2–3 KPIs for each dimension.

        RETURN ONLY ONE JSON OBJECT with SAME structure as before, plus:

        dimensions[*].kpis: [
          {{
            "name": "KPI name",
            "description": "What it measures",
            "importance": "Why this matters for Dell"
          }}
        ]

        Keep field names identical. Just update weights, scores, and add KPIs.
        """
    )

    raw2 = call_llm(prompt2, max_tokens=3200)
    score2 = parse_json_str(raw2)

    return score1, score2


# ---------- Streamlit UI ----------

st.set_page_config(
    page_title="AI-Enabled Procurement Decision Support",
    layout="wide",
)

# App header
st.markdown(
    """
    <div style="padding: 1.2rem 1.5rem; border-radius: 0.75rem;
                background: linear-gradient(90deg,#0f172a,#1d4ed8,#0891b2);
                color: white; margin-bottom: 1rem;">
      <h2 style="margin: 0;">AI-Enabled Procurement Decision Support – Dell Technologies</h2>
      <p style="margin: 0.3rem 0 0; font-size: 0.9rem;">
        Use GenAI to analyse global suppliers, recommend optimal contract types, and
        generate data-driven supplier scorecards for Dell’s hardware and services categories.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Tabs for tasks
tab1, tab2, tab3 = st.tabs(
    [
        "1️⃣ Supplier Market Intelligence",
        "2️⃣ Contract Type Recommendation",
        "3️⃣ Supplier Evaluation Scorecard",
    ]
)

# Session state
if "market_json" not in st.session_state:
    st.session_state.market_json = None
if "score1" not in st.session_state:
    st.session_state.score1 = None
if "score2" not in st.session_state:
    st.session_state.score2 = None

# ----- Tab 1: Market Intelligence -----
with tab1:
    st.subheader("Task 1 – Supplier Market Intelligence using GenAI")
    st.info(
        "Select any Dell procurement category – either a broad family "
        "(e.g., *Electronics & Semiconductors*) or a specific component "
        "(e.g., *Laptop Components (Displays, Batteries)*). The tool will "
        "return top global suppliers and country-level sourcing risks."
    )

    col1, col2 = st.columns([1.2, 1])

    with col1:
        category = st.selectbox(
            "Select procurement category",
            ["-- Select Category --"] + PROCUREMENT_CATEGORIES,
            index=0,
        )

        generate_btn = st.button(
            "🔍 Generate Intelligence",
            type="primary",
            use_container_width=True,
            disabled=category == "-- Select Category --",
        )

    with col2:
        st.markdown("**Tip**")
        st.write(
            "- Use granular categories (e.g., *Server Processors (CPUs)*) when "
            "you want deeper, part-specific insights.\n"
            "- Use broad categories for a high-level market view."
        )

    if generate_btn and category != "-- Select Category --":
        try:
            with st.spinner("Calling OpenAI and generating structured supplier insights..."):
                st.session_state.market_json = gen_market_intel(category)
                st.success("Supplier market intelligence generated successfully.")
        except Exception as e:
            st.error(str(e))

    data = st.session_state.market_json
    if data:
        st.markdown("### 🌍 Market Overview")
        st.write(data.get("marketOverview", ""))

        st.markdown("### 🏭 Top 5 Global Suppliers")
        for s in data.get("topSuppliers", []):
            with st.container():
                st.markdown(
                    f"**{s['rank']}. {s['name']}**  "
                    f"<span style='color:#6b7280;'>({s.get('headquarters','')})</span>",
                    unsafe_allow_html=True,
                )
                st.write("• **Market share:**", s.get("marketShare", "N/A"))
                st.write("• **Key capabilities:**", ", ".join(s.get("keyCapabilities", [])))
                st.write("• **Differentiators:**", s.get("differentiators", ""))
                st.write("• **Dell relevance:**", s.get("dellRelevance", ""))
                st.markdown("---")

        st.markdown("### ⚠️ Country-Level Sourcing Risks")
        for r in data.get("countryRisks", []):
            st.markdown(f"**{r['country']}** – Overall risk: `{r.get('overallRiskLevel')}`")
            cols = st.columns(4)
            cols[0].write("**Supplier concentration**")
            cols[0].write(r.get("supplierConcentration"))
            cols[1].write("**Political risk**")
            cols[1].write(r.get("politicalRisk", {}).get("assessment"))
            cols[2].write("**Logistics risk**")
            cols[2].write(r.get("logisticsRisk", {}).get("assessment"))
            cols[3].write("**Compliance risk**")
            cols[3].write(r.get("complianceRisk", {}).get("assessment"))
            st.write("**ESG risk:**", r.get("esgRisk", {}).get("assessment"))
            st.write("**Mitigation:**", r.get("mitigation"))
            st.markdown("---")

# ----- Tab 2: Contract Recommendation -----
with tab2:
    st.subheader("Task 2 – GenAI-Supported Contract Selection for Procurement")
    st.info(
        "Select one or more Dell items (components, logistics, or materials). "
        "The tool recommends suitable contract types (Buy-back, Revenue-Sharing, "
        "Wholesale Price, Quantity Flexibility, Option, VMI, Cost-Sharing) with "
        "justification and key clauses."
    )

    selected_items = st.multiselect(
        "Select Dell products / services",
        DELL_ITEMS,
        help="You can select multiple items – the model will analyse each separately.",
    )

    analyze_btn = st.button(
        "📄 Analyze Contract Options",
        type="primary",
        use_container_width=True,
        disabled=len(selected_items) == 0,
    )

    if analyze_btn and selected_items:
        try:
            with st.spinner("Analyzing demand, risk and recommending contract types..."):
                st.session_state.contract_json = gen_contract_analysis(selected_items)
                st.success("Contract recommendations generated.")
        except Exception as e:
            st.error(str(e))

    contract_json = st.session_state.get("contract_json")
    if contract_json:
        st.markdown("### Recommended Contract Types by Category")
        for cat in contract_json.get("categories", []):
            st.markdown(f"#### {cat['name']}")
            col_a, col_b = st.columns([1, 1])
            col_a.write("**Recommended contract:**")
            col_a.write(cat.get("recommendedContract"))
            col_b.write("**Alternative contract:**")
            col_b.write(cat.get("alternativeContract"))
            st.write("**Confidence:**", cat.get("confidence"))
            st.write("**Justification:**", cat.get("justification"))
            st.write("**Implementation considerations:**")
            for c in cat.get("implementationConsiderations", []):
                st.write("- ", c)
            st.write("**Key contract clauses to focus on:**")
            for c in cat.get("keyContractClauses", []):
                st.write("- ", c)
            st.markdown("---")

        st.markdown("### Portfolio-Level Procurement Recommendations")
        for r in contract_json.get("procurementRecommendations", []):
            st.write("•", r)

# ----- Tab 3: Scorecard -----
with tab3:
    st.subheader("Task 3 – GenAI-Enhanced Supplier Evaluation Scorecard")
    st.info(
        "Using suppliers from Task 1, the tool builds an initial weighted scorecard "
        "and then refines it with new weights and category-specific KPIs."
    )

    if st.session_state.market_json is None:
        st.warning("Please complete **Task 1** first to identify suppliers.")
    else:
        generate_scores = st.button(
            "🏅 Generate Supplier Scorecards",
            type="primary",
            use_container_width=True,
        )

        if generate_scores:
            try:
                with st.spinner("Building initial and refined supplier scorecards..."):
                    s1, s2 = gen_scorecards(st.session_state.market_json)
                    st.session_state.score1 = s1
                    st.session_state.score2 = s2
                    st.success("Scorecards generated.")
            except Exception as e:
                st.error(str(e))

        score1 = st.session_state.score1
        score2 = st.session_state.score2

        if score1:
            st.markdown("### Initial Scorecard")
            st.write(score1.get("conclusion", ""))

            dims = [d["name"] for d in score1.get("dimensions", [])]
            cols_header = ["Supplier"] + dims + ["Weighted total", "Rating"]
            rows = []
            for s in score1.get("supplierScores", []):
                row = [s["supplierName"]]
                for d in dims:
                    row.append(s["scores"].get(d))
                row.append(s.get("weightedTotal"))
                row.append(s.get("rating"))
                rows.append(row)
            st.table([cols_header] + rows)

        if score2:
            st.markdown("### Refined Scorecard (with KPIs)")
            for d in score2.get("dimensions", []):
                st.markdown(f"**{d['name']} – weight {d.get('weight')}%**")
                for k in d.get("kpis", []):
                    st.write(f"- {k['name']}: {k['description']} ({k['importance']})")
            best = score2.get("bestSupplier")
            if best:
                st.markdown(
                    f"**Best supplier (refined): {best['name']} – score {best['score']}**"
                )
