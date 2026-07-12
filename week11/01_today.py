import streamlit as st
import plotly.express as px

from utils import load_data

st.title("How do countries compare today?")

df = load_data()

latest_year = df["year"].max()

latest = df[df["year"] == latest_year]

st.metric(
    label="Number of Countries",
    value=latest["country"].nunique()
)

tab1, tab2 = st.tabs(
    ["GDP vs Life Expectancy",
     "Population vs Life Expectancy"]
)

with tab1:

    fig = px.scatter(
        latest,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        log_x=True,
        title="GDP vs Life Expectancy"
    )

    # Colour type: Categorical

    st.plotly_chart(fig, use_container_width=True)

with tab2:

    fig2 = px.scatter(
        latest,
        x="pop",
        y="lifeExp",
        size="gdpPercap",
        color="continent",
        hover_name="country",
        log_x=True,
        title="Population vs Life Expectancy"
    )

    # Colour type: Categorical

    st.plotly_chart(fig2, use_container_width=True)