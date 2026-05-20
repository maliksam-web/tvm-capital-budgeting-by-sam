import streamlit as st
import numpy_financial as npf

# --- Financial Functions ---

def calculate_pbp(initial_investment, cash_flows):
    """Calculates the Payback Period (PBP)"""
    cumulative_cash_flow = 0
    for i, cf in enumerate(cash_flows):
        cumulative_cash_flow += cf
        if cumulative_cash_flow >= initial_investment:
            # Linear interpolation for partial year accuracy
            previous_cumulative = cumulative_cash_flow - cf
            needed = initial_investment - previous_cumulative
            pbp = i + (needed / cf)
            return pbp
    return None  # Returns None if investment is never recovered

# --- Streamlit Web App Interface ---

st.set_page_config(page_title="Capital Budgeting Calculator", layout="centered")

st.title("💰 Time Value of Money & Capital Budgeting")
st.write("Input your project financial data below to get instant PBP, NPV, and IRR calculations.")

st.divider()

# --- User Inputs ---
st.subheader("📋 Input Financial Data")

# 1. Initial Investment
initial_investment = st.number_input(
    "Initial Investment ($)", 
    min_value=0.0, 
    value=10000.0, 
    step=500.0
)

# 2. Discount Rate
discount_rate_pct = st.number_input(
    "Discount Rate / Cost of Capital (%)", 
    min_value=0.0, 
    max_value=100.0, 
    value=10.0, 
    step=0.5
)
discount_rate = discount_rate_pct / 100  # Convert to decimal

# 3. Cash Flows
st.write("**Enter Future Cash Flows (comma-separated for each year):**")
cash_flows_raw = st.text_input("Year 1, Year 2, Year 3, etc.", "3000, 4000, 4000, 3000")

# --- Processing the Data ---
try:
    # Convert comma-separated string into a list of floats
    cash_flows = [float(x.strip()) for x in cash_flows_raw.split(",") if x.strip()]
    
    if cash_flows:
        # Prepare cash flow array for numpy_financial (Initial investment must be negative)
        npv_irr_cash_flows = [-initial_investment] + cash_flows
        
        # --- Calculations ---
        npv = npf.npv(discount_rate, npv_irr_cash_flows)
        
        try:
            irr = npf.irr(npv_irr_cash_flows) * 100
        except:
            irr = None # Handles cases where IRR cannot be calculated mathematically
            
        pbp = calculate_pbp(initial_investment, cash_flows)
        
        # --- Display Results ---
        st.divider()
        st.subheader("📊 Evaluation Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Net Present Value (NPV)", value=f"${npv:,.2f}")
            if npv >= 0:
                st.success("🟢 Economically Feasible")
            else:
                st.error("🔴 Economically Unfeasible")
                
        with col2:
            if irr is not None:
                st.metric(label="Internal Rate of Return (IRR)", value=f"{irr:.2f}%")
            else:
                st.metric(label="Internal Rate of Return (IRR)", value="N/A")
                
        with col3:
            if pbp is not None:
                st.metric(label="Payback Period (PBP)", value=f"{pbp:.2f} Years")
            else:
                st.metric(label="Payback Period (PBP)", value="Never Recovered")

except ValueError:
    st.error("⚠️ Please ensure the cash flows are numbers separated only by commas (e.g., 3000, 4000, 5000).")
  
