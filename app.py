
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dividend Portfolio Simulator", layout="wide")

st.title("📈 Dividend Portfolio Dashboard")

st.markdown("""Upload your investment CSV file and adjust assumptions below. The simulator will calculate projected annual income, inflation-adjusted income, and portfolio value over time.""")

uploaded_file = st.file_uploader("Upload your Input.csv file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.sidebar.header("Simulation Parameters")
    years = st.sidebar.number_input("Years to Simulate", min_value=1, max_value=50, value=12)
    div_growth = st.sidebar.slider("Annual Dividend Growth (%)", 0.0, 10.0, 2.0) / 100
    price_growth = st.sidebar.slider("Annual Price Growth (%)", 0.0, 10.0, 1.0) / 100
    reinvest_pct = st.sidebar.slider("Dividend Reinvestment (%)", 0.0, 100.0, 100.0) / 100
    inflation = st.sidebar.slider("Inflation Rate (%)", 0.0, 10.0, 2.0) / 100

    st.subheader("Input Preview")
    st.dataframe(df)

    all_results = []
    portfolio_summary = []

    freq_map = {'M': 12, 'Q': 4}

    for _, row in df.iterrows():
        symbol = row['Symbol']
        shares = row['Starting Shares']
        price = row['Share Price']
        dividend = row['Dividend']
        freq = freq_map.get(row['Payout Frequency'].upper(), 12)

        history = []
        for year in range(1, years + 1):
            for _ in range(freq):
                payout = (dividend / freq) * shares
                shares += (payout * reinvest_pct) / price

            annual_income = shares * dividend
            portfolio_value = shares * price
            real_income = annual_income / ((1 + inflation) ** year)

            history.append({
                'Year': year,
                'Symbol': symbol,
                'Shares': round(shares, 2),
                'Dividend/Share': round(dividend, 4),
                'Share Price': round(price, 2),
                'Annual Income': round(annual_income, 2),
                'Portfolio Value': round(portfolio_value, 2),
                'Real Income': round(real_income, 2)
            })

            dividend *= (1 + div_growth)
            price *= (1 + price_growth)

        hist_df = pd.DataFrame(history)
        all_results.append(hist_df)
        portfolio_summary.append(hist_df.groupby('Year')[['Annual Income', 'Real Income', 'Portfolio Value']].sum().reset_index())

    result_df = pd.concat(all_results)
    portfolio_df = portfolio_summary[0]
    for add_df in portfolio_summary[1:]:
        portfolio_df[['Annual Income', 'Real Income', 'Portfolio Value']] += add_df[['Annual Income', 'Real Income', 'Portfolio Value']]

    st.subheader("Year-by-Year Portfolio Summary")
    st.dataframe(portfolio_df)

    csv = portfolio_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Summary CSV", csv, "Portfolio_Summary.csv", "text/csv")

    st.subheader("📊 Income Charts")
    fig, ax = plt.subplots()
    ax.plot(portfolio_df['Year'], portfolio_df['Annual Income'], label='Total Income', marker='o')
    ax.plot(portfolio_df['Year'], portfolio_df['Real Income'], label='Real Income', marker='o')
    ax.set_xlabel("Year")
    ax.set_ylabel("Income ($)")
    ax.set_title("Annual vs Inflation-Adjusted Income")
    ax.legend()
    st.pyplot(fig)
