import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Auto DCF Valuation", layout="centered")

st.title("📊 Public Company DCF Valuation Tool")

ticker = st.text_input("Enter a stock ticker (e.g. AAPL, MSFT, TSLA):")

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        st.subheader(f"🔍 {info.get('longName', 'Company')} ({ticker.upper()})")

        # Financial data
        revenue = info.get("totalRevenue", 0)
        ebitda = info.get("ebitda", 0)
        cash = info.get("totalCash", 0)
        debt = info.get("totalDebt", 0)
        shares = info.get("sharesOutstanding", 1)

        st.markdown("### 📥 Pulled Financials (TTM)")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Revenue", f"${revenue / 1e9:.2f}B")
            st.metric("EBITDA", f"${ebitda / 1e9:.2f}B")
        with col2:
            st.metric("Cash", f"${cash / 1e9:.2f}B")
            st.metric("Total Debt", f"${debt / 1e9:.2f}B")

        st.divider()

        st.markdown("### 🧮 DCF Inputs (Editable)")

        # Pre-fill with reasonable assumptions
        fcf = ebitda * 0.7 if ebitda else 0  # Est. 70% of EBITDA as FCF
        fcf_year1 = st.number_input("Year 1 Free Cash Flow ($M)", value=round(fcf / 1e6, 2))
        growth_rate = st.slider("Annual FCF Growth Rate (%)", 0.0, 20.0, 5.0)
        discount_rate = st.slider("Discount Rate (%)", 5.0, 15.0, 10.0)
        terminal_multiple = st.slider("Terminal EV/FCF Multiple", 5.0, 25.0, 12.0)

        st.divider()

        # DCF Calculation (5-year forecast)
        years = [1, 2, 3, 4, 5]
        fcfs = [fcf_year1 * ((1 + growth_rate / 100) ** i) for i in years]
        discount_factors = [(1 + discount_rate / 100) ** i for i in years]
        discounted_fcfs = [fcfs[i] / discount_factors[i] for i in range(5)]

        # Terminal Value
        terminal_value = fcfs[-1] * terminal_multiple
        discounted_terminal = terminal_value / discount_factors[-1]

        enterprise_value = sum(discounted_fcfs) + discounted_terminal
        equity_value = enterprise_value - (debt / 1e6) + (cash / 1e6)
        price_per_share = equity_value * 1e6 / shares if shares else 0

        st.markdown("### 📈 DCF Valuation Output")
        st.metric("Enterprise Value", f"${enterprise_value:,.1f}M")
        st.metric("Equity Value", f"${equity_value:,.1f}M")
        st.metric("Implied Price per Share", f"${price_per_share:,.2f}")

        st.caption("📌 Based on estimated FCF from EBITDA and your input assumptions.")

    except Exception as e:
        st.error("⚠️ Could not fetch financials — check the ticker or try again.")

