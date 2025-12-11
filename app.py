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
    Works even if the SDK output structure changes slightly.
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

PROCUREMENT_CATEGORIES = [
    "Electronics components",
    "Packaging",
    "Logistics & transportation",
    "Chemicals & materials",
    "IT & software services",
]

DELL_ITEMS = [
    "Laptop Components (Displays, Batteries, Keyboards)",
    "Server Components (Processors, Memory, Storage)",
    "Semiconductors & Microchips",
    "Printed Circuit Boards (PCBs)",
    "Cooling Systems & Thermal Solutions",
    "Power Supply Units",
    "Networking Equipment (Switches, Routers)",
    "Data Storage Devices (SSDs, HDDs)",
    "Packaging Materials",
    "Logistics & Freight Services",
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

st.title("AI-Enabled Procurement Decision Support")
st.caption(
    "Company: **Dell Technologies** | Use case: AI-driven supplier intelligence, "
    "contract selection, and evaluation scorecards."
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

    category = st.selectbox(
        "Select procurement category",
        ["-- Select --"] + PROCUREMENT_CATEGORIES,
        index=0,
    )

    if st.button("Generate Supplier Intelligence", type="primary", disabled=category == "-- Select --"):
        try:
            with st.spinner("Calling OpenAI and generating structured supplier insights..."):
                st.session_state.market_json = gen_market_intel(category)
                st.success("Supplier market intelligence generated successfully.")
        except Exception as e:
            st.error(str(e))

    data = st.session_state.market_json
    if data:
        st.markdown("### Market Overview")
        st.write(data.get("marketOverview", ""))

        st.markdown("### Top Suppliers")
        for s in data.get("topSuppliers", []):
            st.markdown(
                f"**{s['rank']}. {s['name']}** – {s.get('headquarters','')}"
            )
            st.write("• Market share:", s.get("marketShare", "N/A"))
            st.write("• Key capabilities:", ", ".join(s.get("keyCapabilities", [])))
            st.write("• Differentiators:", s.get("differentiators", ""))
            st.write("• Dell relevance:", s.get("dellRelevance", ""))
            st.markdown("---")

        st.markdown("### Country-Level Sourcing Risks")
        for r in data.get("countryRisks", []):
            st.markdown(f"**{r['country']}** – Overall risk: {r.get('overallRiskLevel')}")
            st.write("Supplier concentration:", r.get("supplierConcentration"))
            st.write("Political risk:", r.get("politicalRisk", {}).get("assessment"))
            st.write("Logistics risk:", r.get("logisticsRisk", {}).get("assessment"))
            st.write("Compliance risk:", r.get("complianceRisk", {}).get("assessment"))
            st.write("ESG risk:", r.get("esgRisk", {}).get("assessment"))
            st.write("Mitigation:", r.get("mitigation"))
            st.markdown("---")

# ----- Tab 2: Contract Recommendation -----
with tab2:
    st.subheader("Task 2 – GenAI-Supported Contract Selection for Procurement")

    selected_items = st.multiselect(
        "Select one or more Dell procurement items",
        DELL_ITEMS,
    )

    if st.button("Analyze Contract Options", type="primary", disabled=len(selected_items) == 0):
        try:
            with st.spinner("Analyzing demand, risk and recommending contract types..."):
                st.session_state.contract_json = gen_contract_analysis(selected_items)
                st.success("Contract recommendations generated.")
        except Exception as e:
            st.error(str(e))

    contract_json = st.session_state.get("contract_json")
    if contract_json:
        st.markdown("### Contract Recommendations by Category")
        for cat in contract_json.get("categories", []):
            st.markdown(f"#### {cat['name']}")
            st.write("**Recommended contract:**", cat.get("recommendedContract"))
            st.write("**Confidence:**", cat.get("confidence"))
            st.write("**Justification:**", cat.get("justification"))
            st.write("**Alternative:**", cat.get("alternativeContract"))
            st.write("**Implementation considerations:**")
            for c in cat.get("implementationConsiderations", []):
                st.write("-", c)
            st.markdown("---")

        st.markdown("### Overall Procurement Recommendations")
        for r in contract_json.get("procurementRecommendations", []):
            st.write("•", r)

# ----- Tab 3: Scorecard -----
with tab3:
    st.subheader("Task 3 – GenAI-Enhanced Supplier Evaluation Scorecard")

    if st.session_state.market_json is None:
        st.warning("Please complete **Task 1** first to identify suppliers.")
    else:
        if st.button("Generate Supplier Scorecards", type="primary"):
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

            # Simple table of scores
            dims = [d["name"] for d in score1.get("dimensions", [])]
            cols = ["Supplier"] + dims + ["Weighted total", "Rating"]
            rows = []
            for s in score1.get("supplierScores", []):
                row = [s["supplierName"]]
                for d in dims:
                    row.append(s["scores"].get(d))
                row.append(s.get("weightedTotal"))
                row.append(s.get("rating"))
                rows.append(row)
            st.table([cols] + rows)

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
