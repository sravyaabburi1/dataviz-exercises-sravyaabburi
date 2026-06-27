
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    path = "/Users/sravyaabburi/Desktop/yd/co2_emissions.csv"
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
#   a) st.selectbox for Region (with 'All')
#   b) st.multiselect for Countries (updates based on region — chained)
#   c) st.date_input for date range (two-handle; convert years to Jan-1 dates)
#   d) st.radio for Metric: "Total CO2 (Mt)" vs "CO2 per capita"
#   e) st.checkbox labelled "Show only top emitter highlighted"
#
# Guards:
#   - empty countries → st.warning + st.stop()
#   - incomplete date_input → st.warning + st.stop()
# Convert date_input result to pd.Timestamp before filtering.
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    # a) Region dropdown
    regions = ["All"] + sorted(df["Region"].unique())

    region = st.selectbox(
        "Select Region",
        regions
    )

    # b) Countries (changes when region changes)
    if region == "All":
        country_options = sorted(df["Country"].unique())
    else:
        country_options = sorted(
            df[df["Region"] == region]["Country"].unique()
        )

    countries = st.multiselect(
        "Select Countries",
        country_options
    )

    # Stop if no country is selected
    if not countries:
        st.warning("Please select at least one country.")
        st.stop()

    # c) Date range picker
    date_range = st.date_input(
        "Select Date Range",
        value=(df["Date"].min(), df["Date"].max())
    )

    # Stop if only one date is selected
    if len(date_range) != 2:
        st.warning("Please select both start and end dates.")
        st.stop()

    # Convert to pandas timestamps
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    # d) Metric selection
    metric = st.radio(
        "Metric",
        ["Total CO2 (Mt)", "CO2 per capita"]
    )

    # e) Checkbox
    highlight_top = st.checkbox(
        "Show only top emitter highlighted"
    )


# filtered = ...  # apply all filters and store here
filtered = df[
    (df["Country"].isin(countries)) &
    (df["Date"] >= start_date) &
    (df["Date"] <= end_date)
]
if metric == "Total CO2 (Mt)":
    metric_col = "CO2_Mt"
else:
    metric_col = "CO2_per_capita"


# ── TASK 2: Filter summary caption ────────────────────────────────────────────
# Show: "X countries | Region | Date range | Metric"
# BBD rule: always show users how many records match current filters
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE
st.caption(
    f"{len(countries)} countries | "
    f"{region} | "
    f"{start_date.year}-{end_date.year} | "
    f"{metric}"
)


# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
#   Left: line chart — selected metric over time, one line per country
#         If "Show only top emitter highlighted" checkbox is on:
#           - grey all lines except the highest emitter in the date range
#           - label that country at the end of its line (SWD grey-and-highlight)
#   Right: bar chart — ranking for the last year in selected date range
#
# BBD colour requirement: name the colour type in a comment next to each chart
# SWD requirements: white background, insight title, use_container_width=True
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:

    fig = px.line(
        filtered,
        x="Year",
        y=metric_col,
        color="Country",   # Qualitative colours
        title=f"{metric} over time"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col_right:

    last_year = filtered["Year"].max()

    last_data = filtered[
        filtered["Year"] == last_year
    ]

    fig_bar = px.bar(
        last_data,
        x=metric_col,
        y="Country",
        orientation="h",   # Sequential colours
        title=f"Ranking in {last_year}"
    )

    fig_bar.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
#   - Total CO2 in last year of selected range (sum across selected countries)
#   - % change from first to last year
#   - Country with highest emissions in last year
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE (optional)
# Last year and first year in selected range
last_year = filtered["Year"].max()
first_year = filtered["Year"].min()

last_data = filtered[filtered["Year"] == last_year]
first_data = filtered[filtered["Year"] == first_year]

# KPI 1: Total CO2 in last year
total_last = last_data[metric_col].sum()

# KPI 2: Percentage change
total_first = first_data[metric_col].sum()

if total_first != 0:
    change_pct = ((total_last - total_first) / total_first) * 100
else:
    change_pct = 0

# KPI 3: Top emitting country
top_country = last_data.loc[
    last_data[metric_col].idxmax(),
    "Country"
]

# Create 3 KPI boxes
kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric(
    "Total CO2 in 2022",
    f"{total_last:,.0f} Mt"
)

kpi2.metric(
    "% Change",
    f"{change_pct:.1f}%"
)

kpi3.metric(
    "Top Emitter",
    top_country
)