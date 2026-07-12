import streamlit as st
import plotly.express as px

from utils import load_data

st.title("What explains the differences between countries?")

df = load_data()

countries = sorted(df["country"].unique())

if "highlight_country" not in st.session_state:
    st.session_state.highlight_country = "Germany"

selected_country = st.selectbox(
    "Select a Country",
    countries,
    index=countries.index(st.session_state.highlight_country)
)

st.session_state.highlight_country = selected_country

country_df = df[df["country"] == selected_country]

fig = px.line(
    country_df,
    x="year",
    y="gdpPercap",
    markers=True,
    title=f"GDP per Capita of {selected_country}"
)

# Colour type: Sequential (Single Colour)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Country Data")

st.dataframe(country_df)