import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Netflix Content Analytics Dashboard",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Netflix Content Analytics Dashboard")
st.markdown(
    "Interactive dashboard analysing Netflix content trends, countries, genres, ratings and creators."
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("netflix_titles.csv")

    df = df.drop_duplicates()

    df["director"] = df["director"].fillna("Unknown")
    df["cast"] = df["cast"].fillna("Unknown")
    df["country"] = df["country"].fillna("Unknown")
    df["rating"] = df["rating"].fillna("Unknown")
    df["duration"] = df["duration"].fillna("Unknown")

    df["date_added"] = pd.to_datetime(
        df["date_added"],
        errors="coerce"
    )

    df["year_added"] = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month_name()
    df["decade"] = (df["release_year"] // 10) * 10

    return df


df = load_data()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.title("Filters")

selected_type = st.sidebar.multiselect(
    "Content Type",
    options=sorted(df["type"].unique()),
    default=sorted(df["type"].unique())
)

year_range = st.sidebar.slider(
    "Release Year",
    int(df.release_year.min()),
    int(df.release_year.max()),
    (
        int(df.release_year.min()),
        int(df.release_year.max())
    )
)

filtered_df = df[
    (df["type"].isin(selected_type))
    &
    (df["release_year"] >= year_range[0])
    &
    (df["release_year"] <= year_range[1])
]

# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------

movies = filtered_df[
    filtered_df["type"] == "Movie"
].shape[0]

tvshows = filtered_df[
    filtered_df["type"] == "TV Show"
].shape[0]

titles = filtered_df.shape[0]

countries = (
    filtered_df["country"]
    .str.split(",")
    .explode()
    .str.strip()
    .nunique()
)

genres = (
    filtered_df["listed_in"]
    .str.split(",")
    .explode()
    .str.strip()
    .nunique()
)

avg_year = round(filtered_df["release_year"].mean(), 0)

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Titles", titles)
c2.metric("Movies", movies)
c3.metric("TV Shows", tvshows)
c4.metric("Countries", countries)
c5.metric("Genres", genres)
c6.metric("Avg Year", avg_year)

st.divider()

# =================================================
# CHART 1
# =================================================

st.subheader("1. Movies vs TV Shows")

fig = px.pie(
    filtered_df,
    names="type",
    hole=0.55,
    color="type",
    color_discrete_sequence=[
        "#E50914",
        "#221F1F"
    ]
)

fig.update_layout(
    template="plotly_white",
    showlegend=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =================================================
# CHART 2
# =================================================

st.subheader("2. Growth of Netflix Content")

growth = (
    filtered_df["release_year"]
    .value_counts()
    .sort_index()
)

fig = px.area(
    x=growth.index,
    y=growth.values,
    labels={
        "x": "Release Year",
        "y": "Titles"
    },
    color_discrete_sequence=["#E50914"]
)

fig.update_layout(
    template="plotly_white"
)

fig.add_annotation(
    x=2016,
    y=max(growth.values),
    text="Rapid growth after 2015",
    showarrow=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =================================================
# CHART 3
# =================================================

st.subheader("3. Movies vs TV Shows Over Time")

trend = (
    filtered_df
    .groupby(
        ["release_year", "type"]
    )
    .size()
    .reset_index(name="Titles")
)

fig = px.line(
    trend,
    x="release_year",
    y="Titles",
    color="type",
    markers=True,
    color_discrete_sequence=[
        "#E50914",
        "#221F1F"
    ]
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =================================================
# CHART 4
# =================================================

st.subheader("4. Top 15 Countries")

country = filtered_df.copy()

country["country"] = country["country"].str.split(",")

country = country.explode("country")

country["country"] = country["country"].str.strip()

top_country = (
    country["country"]
    .value_counts()
    .head(15)
)

fig = px.bar(
    x=top_country.values,
    y=top_country.index,
    orientation="h",
    color=top_country.values,
    color_continuous_scale="Reds"
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Titles",
    yaxis_title="Country"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =================================================
# CHART 5
# =================================================

st.subheader("5. Global Distribution")

country_map = (
    country["country"]
    .value_counts()
    .reset_index()
)

country_map.columns = [
    "country",
    "Titles"
]

fig = px.choropleth(
    country_map,
    locations="country",
    locationmode="country names",
    color="Titles",
    hover_name="country",
    color_continuous_scale="Reds"
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =================================================
# CHART 6
# =================================================

st.subheader("6. Movies vs TV Shows by Country")
top15 = (
    country["country"]
    .value_counts()
    .head(15)
    .index
)

country_type = country[
    country["country"].isin(top15)
]

country_type = (
    country_type
    .groupby(["country", "type"])
    .size()
    .reset_index(name="Titles")
)

fig = px.bar(
    country_type,
    x="country",
    y="Titles",
    color="type",
    barmode="stack",
    color_discrete_sequence=[
        "#E50914",
        "#221F1F"
    ]
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Country",
    yaxis_title="Titles"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =================================================
# CHART 7
# =================================================

st.subheader("7. Genre Distribution")

genre = filtered_df.copy()

genre["listed_in"] = genre["listed_in"].str.split(",")

genre = genre.explode("listed_in")

genre["listed_in"] = genre["listed_in"].str.strip()

genre_count = (
    genre
    .groupby(["type", "listed_in"])
    .size()
    .reset_index(name="Titles")
)

fig = px.sunburst(
    genre_count,
    path=["type", "listed_in"],
    values="Titles",
    color="Titles",
    color_continuous_scale="Reds"
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =================================================
# CHART 8
# =================================================

st.subheader("8. Genre Distribution by Content Type")

heat = (
    genre
    .groupby(["listed_in", "type"])
    .size()
    .reset_index(name="Count")
)

heat = heat.pivot(
    index="listed_in",
    columns="type",
    values="Count"
).fillna(0)

fig = px.imshow(
    heat,
    color_continuous_scale="Reds",
    aspect="auto"
)

fig.update_layout(
    template="plotly_white",
    height=700
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =================================================
# CHART 9
# =================================================

st.subheader("9. Countries with Highest Genre Diversity")

diversity = filtered_df.copy()

diversity["country"] = diversity["country"].str.split(",")

diversity = diversity.explode("country")

diversity["country"] = diversity["country"].str.strip()

diversity["listed_in"] = diversity["listed_in"].str.split(",")

diversity = diversity.explode("listed_in")

diversity["listed_in"] = diversity["listed_in"].str.strip()

country_genre = (
    diversity
    .groupby("country")["listed_in"]
    .nunique()
    .reset_index(name="Genres")
)

country_genre = (
    country_genre
    .sort_values(
        by="Genres",
        ascending=False
    )
    .head(20)
)

fig = px.treemap(
    country_genre,
    path=["country"],
    values="Genres",
    color="Genres",
    color_continuous_scale="Reds"
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =================================================
# CHART 10
# =================================================

st.subheader("10. Audience Ratings")

rating = (
    filtered_df
    .groupby(["rating", "type"])
    .size()
    .reset_index(name="Count")
)

pivot = rating.pivot(
    index="rating",
    columns="type",
    values="Count"
).fillna(0)

fig = px.imshow(
    pivot,
    color_continuous_scale="Reds",
    aspect="auto"
)

fig.update_layout(
    template="plotly_white",
    height=600
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =================================================
# FOOTER
# =================================================

st.markdown("---")

st.markdown(
    """
    ### 📌 Dashboard Summary

    - Netflix's catalogue has grown rapidly since 2015.
    - Movies make up the majority of the platform.
    - The United States and India contribute the most content.
    - Drama and International Movies dominate the catalogue.
    - TV-MA and TV-14 are the most common audience ratings.

    **Dataset:** Netflix Titles Dataset
    """
)