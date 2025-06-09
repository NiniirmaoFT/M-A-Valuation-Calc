import streamlit as st

st.set_page_config(page_title="Valuation App", layout="centered")

st.title("💰 M&A Valuation Calculator")

st.header("📊 Step 1: Company Financials")

revenue = st.number_input("Revenue ($ millions)", min_value=0.0, value=100.0)
ebitda = st.number_input("EBITDA ($ millions)", min_value=0.0, value=20.0)
net_debt = st.number_input("Net Debt ($ millions)", min_value=0.0, value=10.0)
shares_outstanding = st.number_input("Shares Outstanding (millions)", min_value=0.01, value=50.0)

st.divider()

st.header("📈 Step 2: Comparable Multiples")

ev_revenue_multiple = st.number_input("EV / Revenue Multiple", min_value=0.0, value=3.0)
ev_ebitda_multiple = st.number_input("EV / EBITDA Multiple", min_value=0.0, value=10.0)

st.divider()

st.header("📋 Step 3: Valuation Output")

# Calculate implied enterprise values
ev_from_revenue = ev_revenue_multiple * revenue
ev_from_ebitda = ev_ebitda_multiple * ebitda

# Average enterprise value
avg_ev = (ev_from_revenue + ev_from_ebitda) / 2

# Equity value = EV - Net Debt
equity_value = avg_ev - net_debt
price_per_share = equity_value / shares_outstanding

# Show results
st.subheader("📍 Implied Valuation")
st.metric("Average Enterprise Value", f"${avg_ev:,.1f}M")
st.metric("Equity Value", f"${equity_value:,.1f}M")
st.metric("Price per Share", f"${price_per_share:,.2f}")

st.caption("🔎 Based on selected multiples and financials")

