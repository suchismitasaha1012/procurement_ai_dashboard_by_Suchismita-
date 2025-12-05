import streamlit as st
import pandas as pd
from openai import OpenAI

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Procurement Assistant", layout="wide")

# Get API key safely (later you will use st.secrets)
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- LLM HELPER ----------
def call_llm(prompt: str, temperature: float = 0.2):
    if OPENAI_API_KEY is None:
        return "⚠️ No API key found. Add OPENAI_API_KEY to Streamlit secrets."
    response = client.responses.create(
        model="gpt-5.1-mini",  # or any available model
        input=prompt,
    )
    return response.output[0].content[0].text


# ----------------- UI LAYOUT -----------------
st.title("AI-Enabled Procurement Decision Support")

tab1, tab2, tab3 = st.tabs([
    "1️⃣ Supplier Market Intelligence",
    "2️⃣ Contract Type Recommendation",
    "3️⃣ Supplier Evaluation Scorecard"
])

# ------------- TAB 1: Supplier Market Intelligence -------------
with tab1:
    st.header("Supplier Market Intelligence using GenAI")

    category = st.selectbox(
        "Select procurement category:",
        ["Electronics components", "Packaging", "Logistics services",
         "Chemicals", "IT services"]
    )

    st.write("The tool will generate: top suppliers, capabilities and risks.")

    if st.button("Generate Supplier Intelligence"):
        prompt = f"""
        You are a procurement market intelligence assistant.

        Category: {category}

        1. List the Top 5 global suppliers for this category.
        2. For each supplier, provide:
           - Short description
           - Key capabilities
           - Differentiators (what makes them stand out)
        3. For each supplier, give a concise table of country-level sourcing risks
           using four headings: Political, Logistics, Compliance/Regulatory, ESG.

        Make the output structured and easy to read, using clear headings and bullet points.
        """
        output = call_llm(prompt)
        st.markdown(output)


# ------------- TAB 2: Contract Type Recommendation -------------
with tab2:
    st.header("GenAI-Supported Contract Selection")

    st.markdown("We compare **Firm Fixed Price (FFP)**, **Time & Material (T&M)**, and **Cost Reimbursable (CR)** contracts based on project conditions.")

    col1, col2 = st.columns(2)

    with col1:
        product_category = st.text_input(
            "Product / Service category (e.g., 'Cloud migration project', 'Laptop assembly line equipment')"
        )
        cost_predictability = st.select_slider(
            "Cost predictability",
            options=["Low", "Medium", "High"],
            value="Medium"
        )
        market_volatility = st.select_slider(
            "Market volatility of input costs",
            options=["Low", "Medium", "High"],
            value="Medium"
        )
        duration = st.select_slider(
            "Contract duration / volume certainty",
            options=["Short & uncertain", "Medium", "Long & stable"],
            value="Medium"
        )

    with col2:
        st.subheader("Quick reference: Contract Types")
        st.markdown("""
        - **Firm Fixed Price (FFP):** Best when scope is clear and costs are predictable. Seller bears more risk.  
        - **Time & Material (T&M):** Buyer pays for actual time and materials. Shared risk, flexible when scope is evolving.  
        - **Cost Reimbursable (CR):** Buyer reimburses actual cost + fee. Useful when scope is unclear; buyer bears high cost risk.
        """)

    def rule_based_contract(cost_pred, volatility, dur):
        # very simple heuristic
        if cost_pred == "High" and volatility == "Low" and dur == "Long & stable":
            return "Firm Fixed Price (FFP)"
        if cost_pred == "Low" and volatility == "High":
            return "Cost Reimbursable (CR)"
        # middle ground
        return "Time & Material (T&M)"

    if st.button("Recommend Contract Type"):
        recommended = rule_based_contract(cost_predictability, market_volatility, duration)

        # Ask LLM for explanation + comparison table
        prompt = f"""
        You are a procurement contracting expert.

        Context:
        - Product/Service category: {product_category}
        - Cost predictability: {cost_predictability}
        - Market volatility: {market_volatility}
        - Duration & volume certainty: {duration}

        Contract types to compare:
        1. Firm Fixed Price (FFP)
        2. Time & Material (T&M)
        3. Cost Reimbursable (CR)

        a) Provide a comparison table of these contract types using:
           - Cost risk for buyer
           - Schedule risk
           - Flexibility when scope changes
           - Administration complexity

        b) Then, clearly recommend **{recommended}** as the most suitable contract type
           for this situation, with a short 3–4 line justification that links back
           to cost predictability, volatility and duration conditions.
        """
        explanation = call_llm(prompt)
        st.subheader(f"Recommended Contract Type: {recommended}")
        st.markdown(explanation)


# ------------- TAB 3: Supplier Evaluation Scorecard -------------
with tab3:
    st.header("GenAI-Enhanced Supplier Evaluation Scorecard")

    st.markdown("Step 1: Generate initial scorecard using GenAI.  Step 2: Refine weights & KPIs manually.")

    procurement_category = st.text_input(
        "Procurement category (e.g., 'Electronics components for laptops', 'Global logistics services')"
    )

    if st.button("Generate Initial Scorecard"):
        prompt = f"""
        Design a supplier evaluation scorecard for the following procurement category:
        '{procurement_category}'.

        Mandatory evaluation dimensions:
        - Technical capability
        - Quality performance
        - Financial health
        - ESG compliance
        - Innovation capability

        For each dimension, give:
        - A weight (out of 100, total weights should sum to 100)
        - 2–4 specific KPIs with short descriptions

        Present the result in a clean markdown table.
        """
        scorecard_text = call_llm(prompt)
        st.markdown("### Initial GenAI-Generated Scorecard")
        st.markdown(scorecard_text)

    st.markdown("---")
    st.subheader("Refine Weightages & KPIs (Manual Customization)")

    st.markdown("You can create your final scorecard below. Adjust weights based on your priorities.")

    # Editable dataframe template
    default_data = {
        "Dimension": [
            "Technical capability",
            "Quality performance",
            "Financial health",
            "ESG compliance",
            "Innovation capability"
        ],
        "Weight (%)": [25, 25, 20, 15, 15],
        "Example KPIs": [
            "Technology fit, roadmap alignment",
            "Defect rate, OTIF delivery",
            "Credit rating, liquidity ratios",
            "Carbon footprint, labour practices",
            "Co-development projects, R&D intensity"
        ]
    }

    df = pd.DataFrame(default_data)
    edited_df = st.data_editor(df, num_rows="fixed")

    st.markdown("### Final Scorecard (Refined)")
    st.dataframe(edited_df, use_container_width=True)

    total_weight = edited_df["Weight (%)"].sum()
    st.markdown(f"**Total Weight = {total_weight} (should be 100)**")
    if total_weight != 100:
        st.warning("Adjust weights so that total equals 100 for a consistent scorecard.")
