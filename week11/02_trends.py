import streamlit as st
import plotly.express as px

from utils import load_data

st.title("How has life expectancy changed over time?")

df = load_data()

continent = st.selectbox(
    "Choose a Continent",
    sorted(df["continent"].unique())
)

filtered = df[df["continent"] == continent]

fig = px.line(
    filtered,
    x="year",
    y="lifeExp",
    color="country",
    title="Life Expectancy Over Time"
)

# Colour type: Categorical

st.plotly_chart(fig, use_container_width=True)