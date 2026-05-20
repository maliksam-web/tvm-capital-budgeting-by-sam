import streamlit as st
import numpy_financial as npf
import pandas as pd

# --- CORE FINANCIAL FUNCTIONS ---

def calculate_pbp(initial_investment, cash_flows):
    """Calculates the exact Payback Period (PBP) with linear interpolation."""
    cumulative_cash_flow = 0
    for i, cf in enumerate(cash_flows):
        cumulative_cash_flow += cf
        if cumulative_cash_flow >= initial_investment:
            previous_cumulative = cumulative_cash_flow - cf
            needed = initial_investment - previous_cumulative
            return round(i + (needed / cf), 2)
    return None

# --- APP CONFIGURATION & UI THEME ---
st.set_page_config(
    page_title="Corporate Finance Analytics Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for professional look
st.markdown("""
    <style>
    .main .block-container {padding-top: 2rem;}
    div[data-testid="stMetricValue"] {font-size: 24px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.header("⚙️ Project Controls")
st.sidebar.write("Adjust configuration details below:")

initial_investment = st.sidebar.number_input(
    "Initial Capital Outlay ($)", 
    min_value=1.0, 
    value=50000.0, 
    step=1000.0,
    format="%.2f"
)

discount_rate_pct = st.sidebar.slider(
    "Cost of Capital / WACC (%)", 
    min_value=0.0, 
    max_value=100.0, 
    value=12.0, 
    step=0.25
)
discount_rate = discount_rate_pct / 100

st.sidebar.subheader("💡 Sample Data Presets")
preset = st.sidebar.selectbox(
    "Load Example Scenario:",
    ["Custom", "Project Alpha (Steady Growth)", "Project Beta (High Risk/High Return)"]
)

# Manage preset cash flows
if preset == "Project Alpha (Steady Growth)":
    default_cf = "15000, 18000, 22000, 25000, 25000"
elif preset == "Project Beta (High Risk/High Return)":
    default_cf = "5000, 10000, 40000, 30000, 10000"
else:
    default_cf = "15000, 20000, 25000, 20000"

st.sidebar.divider()
st.sidebar.info("💡 **Tip:** Keep this repository 'Public' on GitHub so your live cloud server syncs automatically.")

# --- MAIN DASHBOARD INTERFACE ---
st.title("📊 Corporate Finance & Capital Budgeting Suite")
st.caption("Advanced Time Value of Money (TVM) Evaluation Engine")

st.subheader("📥 Future Cash Flows Entry")
cash_flows_raw = st.text_input(
    "Enter projected cash inflows for each consecutive year (separated cleanly by commas):", 
    value=default_cf
)

# --- DATA PROCESSING & CALCULATIONS ---
try:
    # Parsing input string into clean float array
    cash_flows = [float(x.strip()) for x in cash_flows_raw.split(",") if x.strip()]
    
    if cash_flows:
        # Full array mapping starting with negative initial investment
        full_cash_flows = [-initial_investment] + cash_flows
        
        # Calculate Primary Metrics
        npv = npf.npv(discount_rate, full_cash_flows)
        pbp = calculate_pbp(initial_investment, cash_flows)
        
        try:
            irr = npf.irr(full_cash_flows) * 100
        except Exception:
            irr = None
            
        # Advanced Metric: Profitability Index (PI)
        pv_of_inflows = npv + initial_investment
        profitability_index = pv_of_inflows / initial_investment if initial_investment > 0 else 0
        
        # --- METRICS DISPLAY ROW ---
        st.divider()
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        with m_col1:
            if npv >= 0:
                st.metric("Net Present Value (NPV)", f"${npv:,.2f}", delta="🟢 Profitable")
            else:
                st.metric("Net Present Value (NPV)", f"${npv:,.2f}", delta="🔴 Value Destructive", delta_color="inverse")
                
        with m_col2:
            if irr is not None:
                st.metric("Internal Rate of Return (IRR)", f"{irr:.2f}%", 
                          delta="Acceptable" if irr > (discount_rate*100) else "Below WACC",
                          delta_color="normal" if irr > (discount_rate*100) else "inverse")
            else:
                st.metric("Internal Rate of Return (IRR)", "N/A")
                
        with m_col3:
            if pbp is not None:
                st.metric("Payback Period (PBP)", f"{pbp:.2f} Years")
            else:
                st.metric("Payback Period (PBP)", "Never Recovered")
                
        with m_col4:
            st.metric("Profitability Index (PI)", f"{profitability_index:.2f}x",
                      delta="Good (>1.0)" if profitability_index >= 1 else "Bad (<1.0)",
                      delta_color="normal" if profitability_index >= 1 else "inverse")

        # --- DATA VISUALIZATION & BREAKDOWN ---
        st.divider()
        left_chart_col, right_table_col = st.columns([2, 1])
        
        # Construct DataFrame for analytics charts
        cumulative = -initial_investment
        cum_list = []
        for cf in cash_flows:
            cumulative += cf
            cum_list.append(cumulative)
            
        df_analytics = pd.DataFrame({
            "Year": [f"Year {i+1}" for i in range(len(cash_flows))],
            "Annual Inflow ($)": cash_flows,
            "Cumulative Recovery ($)": cum_list
        }).set_index("Year")
        
        with left_chart_col:
            st.subheader("📈 Project Break-Even & Cumulative Recovery Path")
            # Show interactive area chart tracking capital recovery over time
            st.area_chart(df_analytics["Cumulative Recovery ($)"])
            
        with right_table_col:
            st.subheader("📋 Ledger Details")
            st.dataframe(df_analytics.style.format("${:,.2f}"), use_container_width=True)
            
            # Actionable Final Recommendation
            st.subheader("📢 Decision Verdict")
            if npv >= 0 and (irr is not None and irr >= (discount_rate*100)):
                st.success("✅ **RECOMMENDATION:** ACCEPT THIS PROJECT. The asset clears financial barriers, creates real enterprise value, and covers your total cost of capital.")
            else:
                st.error("❌ **RECOMMENDATION:** REJECT THIS PROJECT. The investment does not yield sufficient cash flows to clear your cost of capital requirements.")

except ValueError:
    st.error("🚨 **Formatting Error:** Please verify that your cash flows entry contains only numbers separated by standard commas.")
except Exception as e:
    st.error(f"An unexpected system exception occurred: {e}")
    
