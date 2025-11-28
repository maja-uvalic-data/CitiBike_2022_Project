import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ----- PAGE CONFIG -----
st.set_page_config(
    page_title="Citi Bike 2022 – NYC Dashboard",
    layout="wide"
)

# ----- DATA LOADING -----
@st.cache_data
def load_data():
    df = pd.read_csv("Data/citibike_2022_with_weather_sample.csv")
    df["date"] = pd.to_datetime(df["date"])
    if "trip_count" not in df.columns:
        df["trip_count"] = 1
    return df

df = load_data()

# ----- TITLE & DESCRIPTION -----
st.title("Citi Bike 2022 – NYC Dashboard")
st.write(
    """
    Most popular Citi Bike stations and their usage in 2022.
    """
)

# ----- FUNCTION: TOP STATIONS BAR CHART -----
def plot_top_stations(df, column="start_station_name", top_n=10):
    data = df[column].value_counts().head(top_n).reset_index()
    data.columns = ["Station", "Trips"]

    fig = px.bar(
        data,
        x="Station",
        y="Trips",
        title=f"Top {top_n} Start Stations in NYC",
        labels={"Station": "Station Name", "Trips": "Number of Trips"}
    )
    fig.update_layout(xaxis_tickangle=45)
    return fig

# ----- PREPARE DAILY DATA FOR DUAL-AXIS LINE CHART -----
daily = df.groupby("date").agg(
    trips=("trip_count", "sum"),
    avg_temp=("avgTemp", "mean")
).reset_index()

def plot_trips_vs_temp(daily_df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=daily_df["date"],
            y=daily_df["trips"],
            name="Number of Trips",
            mode="lines"
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=daily_df["date"],
            y=daily_df["avg_temp"],
            name="Average Temperature (°C)",
            mode="lines"
        ),
        secondary_y=True
    )

    fig.update_layout(
        title="Daily Citi Bike Trips vs Average Temperature (2022)",
        hovermode="x unified"
    )

    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Number of Trips", secondary_y=False)
    fig.update_yaxes(title_text="Average Temperature (°C)", secondary_y=True)

    return fig

# ----- LAYOUT: TWO COLUMNS FOR PLOTLY CHARTS -----
col1, col2 = st.columns(2)

with col1:
    st.subheader("Most Popular Start Stations")
    fig_bar = plot_top_stations(df)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Daily Trips vs Average Temperature")
    fig_line = plot_trips_vs_temp(daily)
    st.plotly_chart(fig_line, use_container_width=True)

# ----- KEPLER MAP -----
st.subheader("Citi Bike Trips Map – Kepler.gl")

try:
    with open("Docs/citibike_kepler_map.html", "r", encoding="utf-8") as f:
        kepler_html = f.read()

    components.html(kepler_html, height=700, scrolling=True)
except FileNotFoundError:
    st.error("Kepler.gl HTML mapa nije pronađena. Proveri putanju i ime fajla u folderu 'Docs'.")
