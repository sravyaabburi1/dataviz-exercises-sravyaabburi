import streamlit as st
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import load_data, sidebar_filters

# --------------------------------------------------------------------
# Load data + shared sidebar
# --------------------------------------------------------------------

df, p95 = load_data()
filtered = sidebar_filters(df, p95)

st.title("Where is guest demand strongest?")
st.caption(
    "Guest demand is approximated using reviews per month."
)

# --------------------------------------------------------------------
# Persisted widget
# --------------------------------------------------------------------

room_types = sorted(filtered["room_type"].unique())

if "sel_room" not in st.session_state:
    st.session_state.sel_room = room_types[0]

st.session_state.sel_room = st.session_state.sel_room

if st.session_state.sel_room not in room_types:
    st.session_state.sel_room = room_types[0]

st.selectbox(
    "Select Room Type",
    room_types,
    key="sel_room"
)

selected_room = st.session_state.sel_room

room_df = filtered[
    filtered["room_type"] == selected_room
]

# --------------------------------------------------------------------
# KPI Row
# --------------------------------------------------------------------

k1, k2, k3 = st.columns(3)

k1.metric(
    "Listings",
    f"{len(room_df):,}"
)

k2.metric(
    "Median Reviews / Month",
    f"{room_df['reviews_per_month'].median():.1f}",
    f"{room_df['reviews_per_month'].median()-filtered['reviews_per_month'].median():+.1f} vs market"
)

k3.metric(
    "Median Price",
    f"£{room_df['price'].median():.0f}/night",
    f"£{room_df['price'].median()-filtered['price'].median():+.0f} vs market"
)

st.divider()

# --------------------------------------------------------------------
# Scatter Plot
# --------------------------------------------------------------------

plot_df = filtered.copy()

plot_df["highlight"] = plot_df["room_type"].apply(
    lambda x: selected_room if x == selected_room else "Other"
)

fig = px.scatter(
    plot_df,
    x="price",
    y="reviews_per_month",
    color="highlight",
    hover_name="neighbourhood",
    size="number_of_reviews",
    color_discrete_map={
        selected_room: "#2E75B6",
        "Other": "#AAAAAA"
    },
    labels={
        "price": "Nightly Price (£)",
        "reviews_per_month": "Reviews per Month",
        "highlight": ""
    },
    title="Higher review activity suggests stronger guest demand"
)

# Colour type: Highlight (Blue vs Grey)

fig.update_traces(marker=dict(opacity=0.75))

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Arial",
        size=12
    ),
    xaxis=dict(gridcolor="#EEEEEE"),
    yaxis=dict(gridcolor="#EEEEEE"),
    legend=dict(
        orientation="h",
        y=1.08
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

with st.expander("📊 Show raw data sample"):
    st.dataframe(
        room_df.head(100),
        use_container_width=True
    )