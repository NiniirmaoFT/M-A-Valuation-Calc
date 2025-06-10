import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Multi-Method Valuation App", layout="wide")

st.title("Multi-Method Company Valuation")

# Sidebar: select ticker and valuation method
ticker_input = st.sidebar.text_input("Enter stock ticker (e.g. AAPL)", "AAPL").upper()
valuation_method = st.sidebar.selectbox(
    "Choose a valuation method:",
    [
        "Discounted Cash Flow (DCF)",
        "Comparable Company Analysis (CCA)",
        "Precedent Transactions (PTA)",
        "Asset-Based Valuation",
        "Market Capitalization",
        "EV/EBITDA Multiple",
        "Price-to-Earnings (P/E) Ratio",
        "Dividend Discount Model (DDM)",
        "Leveraged Buyout (LBO)",
        "Sum-of-the-Parts (SOTP)"
    ]
)

stock = yf.Ticker(ticker_input)

# Pull data (handle missing with try/except)
try:
    financials = stock.financials
except:
    financials = pd.DataFrame()
try:
    balance_sheet = stock.balance_sheet
except:
    balance_sheet = pd.DataFrame()
try:
    cashflow = stock.cashflow
except:
    cashflow = pd.DataFrame()
info = stock.info

shares_outstanding = info.get("sharesOutstanding", 0) or 0
price = stock.history(period="1d")["Close"][-1] if not stock.history(period="1d").empty else 0

st.write(f"### Company: {info.get('longName', ticker_input)}")
st.write(f"Current Share Price: ${price:,.2f}")

### Helper function for safe extraction
def safe_get(df, key):
    try:
        return df.loc[key][0]
    except:
        return 0

# Calculate Market Cap
market_cap = price * shares_outstanding if shares_outstanding else 0

# Common financials for methods
revenue = safe_get(financials, "Total Revenue")
ebitda = safe_get(financials, "EBITDA")
cash = safe_get(balance_sheet, "Cash")
debt = safe_get(balance_sheet, "Total Debt")
equity = safe_get(balance_sheet, "Total Equity")
eps = info.get("trailingEps", 0)
dividend_yield = info.get("dividendYield", 0)
beta = info.get("beta", 1)
cost_of_equity = 0.08  # simplified assumption

# -----------------------------------------
# Valuation Methods Implementations

if valuation_method == "Discounted Cash Flow (DCF)":
    st.header("Discounted Cash Flow (DCF)")

    # Inputs for DCF
    fcf = st.number_input("Enter latest Free Cash Flow (USD)", value=abs(safe_get(cashflow, "Free Cash Flow")))
    growth_rate = st.number_input("Enter perpetual growth rate (%)", value=2.0) / 100
    discount_rate = st.number_input("Enter discount rate (%)", value=10.0) / 100
    years = st.number_input("Number of forecast years", value=5)

    # Forecast FCF
    fcf_forecast = [fcf * (1 + growth_rate) ** i for i in range(1, years + 1)]
    discounted_fcf = [fcf_forecast[i] / (1 + discount_rate) ** (i + 1) for i in range(years)]

    tv = fcf_forecast[-1] * (1 + growth_rate) / (discount_rate - growth_rate) if discount_rate > growth_rate else 0
    discounted_tv = tv / (1 + discount_rate) ** years if tv > 0 else 0

    npv = sum(discounted_fcf) + discounted_tv

    ev = npv
    equity_value = ev - debt + cash if ev else 0
    implied_share_price = equity_value / shares_outstanding if shares_outstanding else 0

    st.write(f"Enterprise Value (EV): ${ev:,.2f}")
    st.write(f"Equity Value: ${equity_value:,.2f}")
    st.write(f"Implied Share Price: ${implied_share_price:,.2f}")

elif valuation_method == "Market Capitalization":
    st.header("Market Capitalization")
    st.write(f"Shares Outstanding: {shares_outstanding:,.0f}")
    st.write(f"Market Cap: ${market_cap:,.2f}")

elif valuation_method == "EV/EBITDA Multiple":
    st.header("Enterprise Value / EBITDA Multiple")
    ev = market_cap + debt - cash
    multiple = ev / ebitda if ebitda else 0
    st.write(f"Enterprise Value (EV): ${ev:,.2f}")
    st.write(f"EBITDA: ${ebitda:,.2f}")
    st.write(f"EV / EBITDA Multiple: {multiple:.2f}x")

elif valuation_method == "Price-to-Earnings (P/E) Ratio":
    st.header("Price-to-Earnings (P/E) Ratio")
    pe_ratio = price / eps if eps else 0
    st.write(f"EPS (TTM): ${eps:.2f}")
    st.write(f"P/E Ratio: {pe_ratio:.2f}x")

elif valuation_method == "Dividend Discount Model (DDM)":
    st.header("Dividend Discount Model (DDM)")
    dividend = price * dividend_yield if dividend_yield else 0
    growth = st.number_input("Dividend growth rate (%)", value=3.0) / 100
    discount = st.number_input("Discount rate (%)", value=8.0) / 100
    ddm_value = dividend * (1 + growth) / (discount - growth) if discount > growth else 0
    st.write(f"Dividend per share (estimated): ${dividend:.2f}")
    st.write(f"Intrinsic Value (DDM): ${ddm_value:.2f}")

elif valuation_method == "Asset-Based Valuation":
    st.header("Asset-Based Valuation")
    st.write(f"Total Assets: ${safe_get(balance_sheet, 'Total Assets'):,.2f}")
    st.write(f"Total Liabilities: ${safe_get(balance_sheet, 'Total Liab'):,.2f}")
    asset_based_value = safe_get(balance_sheet, 'Total Assets') - safe_get(balance_sheet, 'Total Liab')
    st.write(f"Net Asset Value: ${asset_based_value:,.2f}")

elif valuation_method == "Comparable Company Analysis (CCA)":
    st.header("Comparable Company Analysis (CCA)")
    st.write("**Manual peer group with multiples**")

    # Manually define peers — ideally these come from user input or a DB
    peers = ["MSFT", "GOOGL", "AMZN", "META", "TSLA"]

    data = []
    for peer in peers:
        p = yf.Ticker(peer)
        p_info = p.info
        p_price = p.history(period="1d")["Close"][-1] if not p.history(period="1d").empty else 0
        p_shares = p_info.get("sharesOutstanding", 0) or 0
        p_market_cap = p_price * p_shares if p_price and p_shares else 0
        p_ebitda = safe_get(p.financials, "EBITDA")
        p_ev = p_market_cap + safe_get(p.balance_sheet, "Total Debt") - safe_get(p.balance_sheet, "Cash")
        p_ev_ebitda = p_ev / p_ebitda if p_ebitda else 0
        p_pe = p_price / p_info.get("trailingEps", 1) if p_info.get("trailingEps") else 0
        data.append({
            "Ticker": peer,
            "Price": p_price,
            "Market Cap": p_market_cap,
            "EV": p_ev,
            "EBITDA": p_ebitda,
            "EV/EBITDA": p_ev_ebitda,
            "P/E": p_pe
        })

    df_peers = pd.DataFrame(data)
    st.dataframe(df_peers.style.format({
        "Price": "${:,.2f}",
        "Market Cap": "${:,.2f}",
        "EV": "${:,.2f}",
        "EBITDA": "${:,.2f}",
        "EV/EBITDA": "{:.2f}",
        "P/E": "{:.2f}"
    }))

elif valuation_method == "Precedent Transactions (PTA)":
    st.header("Precedent Transactions Analysis (PTA)")

    # Static sample data — in reality, you'd pull from a database or API
    precedent_data = [
        {"Deal": "Company A buys B", "Date": "2023-01-15", "EV/EBITDA": 8.5, "EV/Sales": 2.1},
        {"Deal": "Company C buys D", "Date": "2022-09-30", "EV/EBITDA": 7.8, "EV/Sales": 1.9},
        {"Deal": "Company E buys F", "Date": "2021-12-20", "EV/EBITDA": 9.2, "EV/Sales": 2.5},
    ]

    df_precedent = pd.DataFrame(precedent_data)
    st.table(df_precedent)

elif valuation_method == "Leveraged Buyout (LBO)":
    st.header("Leveraged Buyout (LBO) Analysis")

    purchase_price = st.number_input("Purchase price (Enterprise Value)", value=market_cap + debt - cash)
    debt_used = st.number_input("Debt used in LBO", value=debt)
    interest_rate = st.number_input("Debt interest rate (%)", value=6.0) / 100
    exit_ebitda = st.number_input("Exit year EBITDA", value=ebitda)
    exit_multiple = st.number_input("Exit EV/EBITDA multiple", value=8.0)

    # Simple LBO calc: Equity value at exit - debt payoff
    exit_ev = exit_ebitda * exit_multiple
    exit_equity = exit_ev - debt_used * (1 + interest_rate)  # simplified
    cash_invested = purchase_price - debt_used
    irr = ((exit_equity / cash_invested) ** (1 / 5)) - 1 if cash_invested != 0 else 0  # 5 year hold

    st.write(f"Exit Enterprise Value: ${exit_ev:,.2f}")
    st.write(f"Exit Equity Value: ${exit_equity:,.2f}")
    st.write(f"Equity Invested: ${cash_invested:,.2f}")
    st.write(f"Estimated IRR over 5 years: {irr * 100:.2f}%")

elif valuation_method == "Sum-of-the-Parts (SOTP)":
    st.header("Sum-of-the-Parts (SOTP) Valuation")

    st.write("Enter values for each business segment:")

    segments = {}
    segments['Segment A'] = st.number_input("Segment A Value (USD)", value=0)
    segments['Segment B'] = st.number_input("Segment B Value (USD)", value=0)
    segments['Segment C'] = st.number_input("Segment C Value (USD)", value=0)

    total_sotp = sum(segments.values())
    st.write(f"Total Sum-of-the-Parts Value: ${total_sotp:,.2f}")

else:
    st.write("Please select a valuation method.")


