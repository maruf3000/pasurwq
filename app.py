import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pasur Surface Water Quality Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("pasur_surface_water_quality.csv")

    # --- CLEANING ---
    df["date"] = df["date"].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")

    df["time"] = pd.to_datetime(
    df["time"], format="%I:%M %p", errors="coerce"
    ).dt.time
    return df

df = load_data()

st.title("🌊 Pasur Surface Water Quality Dashboard")

PARAMETER_MAP = {
    "Water Temperature (°C)": "water_temp_c",
    "pH": "ph",
    "Dissolved Oxygen (mg/L)": "do_mg_l",
    "Electrical Conductivity (mS/cm)": "ec_ms_cm",
    "Salinity (ppt)": "salinity_ppt",
    "Turbidity (NTU)": "turbidity_ntu",
    "TDS (ppt)": "tds_ppt",
    "TSS (mg/L)": "tss_mg_l",
    "Ammonia-N (mg/L)": "nh3_n_mg_l",
    "Nitrate (mg/L)": "nitrate_mg_l",
    "Phosphate (mg/L)": "phosphate_mg_l",
    "Sulphate (mg/L)": "sulphate_mg_l",
    "Iron (mg/L)": "fe_mg_l",
    "Oil & Grease (mg/L)": "oil_grease_mg_l",
}

WQI_PARAMS = {
    "pH": {
        "column": "ph",
        "standard": 8.5,
        "ideal": 7.0,
        "weight": 0.11
    },
    "DO (mg/L)": {
        "column": "do_mg_l",
        "standard": 5.0,
        "ideal": 14.6,
        "weight": 0.17
    },
    "EC (mS/cm)": {
        "column": "ec_ms_cm",
        "standard": 1.5,
        "ideal": 0.0,
        "weight": 0.10
    },
    "TDS (ppt)": {
        "column": "tds_ppt",
        "standard": 0.5,
        "ideal": 0.0,
        "weight": 0.10
    },
    "Nitrate (mg/L)": {
        "column": "nitrate_mg_l",
        "standard": 10.0,
        "ideal": 0.0,
        "weight": 0.10
    },
    "Phosphate (mg/L)": {
        "column": "phosphate_mg_l",
        "standard": 0.1,
        "ideal": 0.0,
        "weight": 0.08
    },
    "Turbidity (NTU)": {
        "column": "turbidity_ntu",
        "standard": 5.0,
        "ideal": 0.0,
        "weight": 0.09
    }
}



# Pollution Thresholds (example values – adjust to your regulatory standards)
POLLUTION_THRESHOLDS = {
    "do_mg_l": {"limit": 5, "type": "min"},              # DO below 5 mg/L is critical
    "ph": {"limit_low": 6.5, "limit_high": 8.5},
    "nh3_n_mg_l": {"limit": 0.5, "type": "max"},
    "nitrate_mg_l": {"limit": 10, "type": "max"},
    "phosphate_mg_l": {"limit": 0.5, "type": "max"},
    "turbidity_ntu": {"limit": 100, "type": "max"},
    "oil_grease_mg_l": {"limit": 10, "type": "max"},
    "fe_mg_l": {"limit": 0.3, "type": "max"},
}






# Sidebar
st.sidebar.header("🔍 Filters")

month = st.sidebar.selectbox("Month", sorted(df["month"].unique()))
location = st.sidebar.selectbox("Location", sorted(df["location"].unique()))
tide = st.sidebar.selectbox("Tide Type", ["Spring", "Neap"])

parameter_map = {
    "Water Temperature (°C)": "water_temp_c",
    "pH": "ph",
    "Dissolved Oxygen (mg/L)": "do_mg_l",
    "Salinity (ppt)": "salinity_ppt",
    "Turbidity (NTU)": "turbidity_ntu",
    "NH3-N (mg/L)": "nh3_n_mg_l",
    "Nitrate (mg/L)": "nitrate_mg_l",
    "Phosphate (mg/L)": "phosphate_mg_l",
    "Iron (mg/L)": "fe_mg_l"
}

param_label = st.sidebar.selectbox("Parameter", list(parameter_map.keys()))
parameter = parameter_map[param_label]

# Filter
filtered = df[
    (df["month"] == month) &
    (df["location"] == location) &
    (df["tide_type"] == tide)
]

# Summary stats
st.subheader("📊 Summary Statistics")
vals = filtered[parameter]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Mean", f"{vals.mean():.2f}")
c2.metric("Min", f"{vals.min():.2f}")
c3.metric("Max", f"{vals.max():.2f}")
c4.metric("Std", f"{vals.std():.2f}")
c5.metric("Range", f"{vals.max() - vals.min():.2f}")

# Time series
st.subheader("⏱ Diurnal Variation")
fig = px.line(
    filtered,
    x="hour",
    y=parameter,
    color="weather",
    markers=True
)
st.plotly_chart(fig, use_container_width=True)

# Distribution
st.subheader("📦 Distribution")
fig2 = px.box(filtered, y=parameter, points="all")
st.plotly_chart(fig2, use_container_width=True)

# Context
st.subheader("📌 Sampling Context")
st.write("Weather:", filtered["weather"].unique())
st.write("Avg Wind Speed (km/h):", round(filtered["wind_speed_kmh"].mean(), 2))
st.write("Wind Direction:", filtered["wind_direction"].mode()[0])
st.write("Sampling Dates:", filtered["date"].dt.date.unique())

# Download
st.download_button(
    "⬇ Download Filtered Data",
    filtered.to_csv(index=False),
    "filtered_water_quality.csv"
)


#Spring vs Neap side-by-side comparison

st.sidebar.header("Spring vs Neap Comparison")

compare_month = st.sidebar.selectbox(
    "Select Month",
    sorted(df["month"].unique())
)

compare_location = st.sidebar.selectbox(
    "Select Location",
    df["location"].unique()
)

selected_param_label = st.sidebar.selectbox(
    "Select Parameter",
    list(PARAMETER_MAP.keys())
)

compare_parameter = PARAMETER_MAP[selected_param_label]



compare_df = df[
    (df["month"] == compare_month) &
    (df["location"] == compare_location) &
    (df["tide_type"].isin(["Spring", "Neap"]))
]


st.subheader(
    f"🌊 Spring vs Neap Comparison | {compare_parameter.upper()} | {compare_month} | {compare_location}"
)

col1, col2 = st.columns(2)

spring_data = compare_df[compare_df["tide_type"] == "Spring"]
neap_data = compare_df[compare_df["tide_type"] == "Neap"]


import plotly.express as px

fig = px.box(
    compare_df,
    x="tide_type",
    y=compare_parameter,
    color="tide_type",
    title=f"{selected_param_label} | Spring vs Neap"
)

st.plotly_chart(fig, use_container_width=True)



with col1:
    st.markdown("### 🌕 Spring Tide")
    if not spring_data.empty:
        st.metric(
            "Mean",
            f"{spring_data[compare_parameter].mean():.2f}"
        )

        st.metric(
            "Min",
            f"{spring_data[compare_parameter].min():.2f}"
        )

        st.metric(
            "Max",
            f"{spring_data[compare_parameter].max():.2f}"
        )

    else:
        st.info("No Spring data available")

with col2:
    st.markdown("### 🌑 Neap Tide")
    if not neap_data.empty:
        st.metric(
            "Mean",
            f"{spring_data[compare_parameter].mean():.2f}"
        )

        st.metric(
            "Min",
            f"{spring_data[compare_parameter].min():.2f}"
        )

        st.metric(
            "Max",
            f"{spring_data[compare_parameter].max():.2f}"
        )
    else:
        st.info("No Neap data available")

if compare_parameter not in df.columns:
    st.error(f"Column '{compare_parameter}' not found in dataset")
    st.stop()


#Seasonal signal (Monsoon vs Dry vs Pre-monsoon)

st.sidebar.header("Seasonal Analysis")

season_location = st.sidebar.selectbox(
    "Select Location (Seasonal)",
    df["location"].unique()
)

season_param_label = st.sidebar.selectbox(
    "Select Parameter (Seasonal)",
    list(PARAMETER_MAP.keys()),
    key="season_param"
)

season_selected = st.sidebar.multiselect(
    "Select Seasons",
    df["season"].unique(),
    default=df["season"].unique()
)

season_param = PARAMETER_MAP[season_param_label]


season_df = df[
    (df["location"] == season_location) &
    (df["season"].isin(season_selected))
]

if season_df.empty:
    st.warning("No data available for selected filters")
    st.stop()


st.subheader(
    f"🌦️ Seasonal Variation of {season_param_label} at {season_location}"
)

import plotly.express as px

fig_season = px.box(
    season_df,
    x="season",
    y=season_param,
    color="season",
    points="all",
    title="Season-wise Distribution"
)

st.plotly_chart(fig_season, use_container_width=True)


fig_trend = px.line(
    season_df.sort_values("month_num"),
    x="month_num",
    y=season_param,
    color="season",
    markers=True,
    title="Monthly Trend by Season"
)

fig_trend.update_xaxes(
    tickmode="array",
    tickvals=season_df["month_num"].unique(),
    ticktext=season_df["month"].unique()
)

st.plotly_chart(fig_trend, use_container_width=True)


st.subheader("📊 Season-wise Summary Statistics")

stats_df = (
    season_df
    .groupby("season")[season_param]
    .agg(["mean", "min", "max", "std"])
    .round(2)
    .reset_index()
)

st.dataframe(stats_df, use_container_width=True)





#Correlation heatmap (Temp–DO–Salinity–EC–TDS)

CORR_VARS = {
    "Water Temperature (°C)": "water_temp_c",
    "Dissolved Oxygen (mg/L)": "do_mg_l",
    "Salinity (ppt)": "salinity_ppt",
    "Electrical Conductivity (mS/cm)": "ec_ms_cm",
    "TDS (ppt)": "tds_ppt",
}


st.sidebar.header("Correlation Analysis")

corr_location = st.sidebar.selectbox(
    "Select Location (Correlation)",
    df["location"].unique(),
    key="corr_loc"
)

corr_season = st.sidebar.multiselect(
    "Select Season(s)",
    df["season"].unique(),
    default=df["season"].unique(),
    key="corr_season"
)

corr_tide = st.sidebar.multiselect(
    "Select Tide Type(s)",
    df["tide_type"].unique(),
    default=df["tide_type"].unique(),
    key="corr_tide"
)


corr_df = df[
    (df["location"] == corr_location) &
    (df["season"].isin(corr_season)) &
    (df["tide_type"].isin(corr_tide))
]

if corr_df.shape[0] < 5:
    st.warning("Not enough data points for correlation analysis")
    


corr_data = corr_df[list(CORR_VARS.values())].dropna()

corr_matrix = corr_data.corr(method="pearson").round(2)


import plotly.figure_factory as ff

st.subheader(
    f"🔥 Correlation Heatmap | {corr_location}"
)

fig_corr = ff.create_annotated_heatmap(
    z=corr_matrix.values,
    x=list(CORR_VARS.keys()),
    y=list(CORR_VARS.keys()),
    colorscale="RdBu",
    zmin=-1,
    zmax=1,
    showscale=True
)

fig_corr.update_layout(
    title="Pearson Correlation Coefficients",
    height=500
)

st.plotly_chart(fig_corr, use_container_width=True)



st.markdown("""
**Interpretation guide:**
- **Positive (+)**: Variables increase together (e.g., EC–Salinity)
- **Negative (−)**: Inverse relationship (e.g., Temp–DO)
- **Near 0**: Weak or no linear relationship
""")



#parameter summary-statistics visualization

PARAMETER_LABELS = {
    "water_temp_c": "Water Temperature (°C)",
    "ph": "pH",
    "do_mg_l": "Dissolved Oxygen (mg/L)",
    "salinity_ppt": "Salinity (ppt)",
    "ec_ms_cm": "Electrical Conductivity (mS/cm)",
    "tds_ppt": "TDS (ppt)",
    "turbidity_ntu": "Turbidity (NTU)",
    "tds_ppt": "TDS (ppt)",
    "tss_mg_l": "TSS (mg/L)",
    "nh3_n_mg_l": "Ammonia-N (mg/L)",
    "nitrate_mg_l": "Nitrate (mg/L)",
    "phosphate_mg_l": "Phosphate (mg/L)",
    "sulphate_mg_l": "Sulphate (mg/L)",
    "oil_grease_mg_l": "Oil & Grease (mg/L)"
}


st.sidebar.header("📊 Summary Statistics Filter")

selected_location = st.sidebar.selectbox(
    "Select Location",
    sorted(df["location"].dropna().unique())
)

selected_parameter = st.sidebar.selectbox(
    "Select Parameter",
    list(PARAMETER_LABELS.keys()),
    format_func=lambda x: PARAMETER_LABELS[x]
)

selected_tide = st.sidebar.radio(
    "Select Tide Type",
    ["Spring", "Neap"]
)

filtered_df = df[
    (df["location"] == selected_location) &
    (df["tide_type"] == selected_tide)
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

summary_stats = (
    filtered_df
    .groupby("location")[selected_parameter]
    .agg(["min", "mean", "max"])
    .reset_index()
)

summary_stats.columns = [
    "Location", "Minimum", "Mean", "Maximum"
]

import plotly.express as px

fig = px.bar(
    summary_stats,
    x="Location",
    y=["Minimum", "Mean", "Maximum"],
    barmode="group",
    title=(
        f"{PARAMETER_LABELS[selected_parameter]} "
        f"(Min, Mean, Max) — {selected_tide} Tide"
    ),
    labels={"value": PARAMETER_LABELS[selected_parameter]},
)

fig.update_layout(
    xaxis_title="Location",
    yaxis_title=PARAMETER_LABELS[selected_parameter],
    legend_title="Statistic",
    height=500
)

st.plotly_chart(fig, use_container_width=True)


with st.expander("📋 View Summary Statistics Table"):
    st.dataframe(summary_stats, use_container_width=True)

#Monthly Min–Mean–Max

st.markdown("---")
st.header("📆 Monthly Min–Mean–Max (Spring + Neap Combined)")

st.sidebar.header("📆 Monthly Statistics Filter")

monthly_location = st.sidebar.selectbox(
    "Select Location (Monthly)",
    sorted(df["location"].dropna().unique()),
    key="monthly_location"
)

monthly_parameter = st.sidebar.selectbox(
    "Select Parameter (Monthly)",
    list(PARAMETER_LABELS.keys()),
    format_func=lambda x: PARAMETER_LABELS[x],
    key="monthly_parameter"
)

monthly_df = df[
    (df["location"] == monthly_location)
].copy()

if monthly_df.empty:
    st.warning("No data available for the selected location.")
    st.stop()


df["month_num"] = df["date"].dt.month
df["month"] = df["date"].dt.strftime("%b")


monthly_stats = (
    monthly_df
    .groupby(["month_num", "month"])[monthly_parameter]
    .agg(["min", "mean", "max"])
    .reset_index()
    .sort_values("month_num")
)


monthly_stats.columns = [
    "Month_Num", "Month", "Minimum", "Mean", "Maximum"
]


import plotly.express as px

fig_monthly = px.bar(
    monthly_stats,
    x="Month",
    y=["Minimum", "Mean", "Maximum"],
    barmode="group",
    title=(
        f"Monthly {PARAMETER_LABELS[monthly_parameter]} "
        f"(Min–Mean–Max)\nLocation: {monthly_location} "
        f"(Spring + Neap Combined)"
    ),
    labels={"value": PARAMETER_LABELS[monthly_parameter]},
)

fig_monthly.update_layout(
    xaxis_title="Month",
    yaxis_title=PARAMETER_LABELS[monthly_parameter],
    legend_title="Statistic",
    height=500
)

st.plotly_chart(fig_monthly, use_container_width=True)


with st.expander("📋 View Monthly Statistics Table"):
    st.dataframe(
        monthly_stats.drop(columns="Month_Num"),
        use_container_width=True
    )


#Monthly Trend with Moving Average

st.markdown("---")
st.header("📈 Monthly Trend with Moving Average")


st.sidebar.header("📈 Trend Analysis Filter")

trend_location = st.sidebar.selectbox(
    "Select Location (Trend)",
    sorted(df["location"].dropna().unique()),
    key="trend_location"
)

trend_parameter = st.sidebar.selectbox(
    "Select Parameter (Trend)",
    list(PARAMETER_LABELS.keys()),
    format_func=lambda x: PARAMETER_LABELS[x],
    key="trend_parameter"
)

ma_window = st.sidebar.slider(
    "Moving Average Window (Months)",
    min_value=2,
    max_value=6,
    value=3,
    step=1
)


trend_df = df[df["location"] == trend_location].copy()

if trend_df.empty:
    st.warning("No data available for the selected location.")
    st.stop()


trend_df["year_month"] = trend_df["date"].dt.to_period("M").astype(str)


monthly_mean = (
    trend_df
    .groupby("year_month")[trend_parameter]
    .mean()
    .reset_index()
)


monthly_mean["year_month"] = pd.to_datetime(monthly_mean["year_month"])
monthly_mean = monthly_mean.sort_values("year_month")


monthly_mean["moving_avg"] = (
    monthly_mean[trend_parameter]
    .rolling(window=ma_window, min_periods=1)
    .mean()
)


import plotly.graph_objects as go

fig_trend = go.Figure()

# Monthly Mean
fig_trend.add_trace(go.Scatter(
    x=monthly_mean["year_month"],
    y=monthly_mean[trend_parameter],
    mode="lines+markers",
    name="Monthly Mean",
    line=dict(width=2)
))

# Moving Average
fig_trend.add_trace(go.Scatter(
    x=monthly_mean["year_month"],
    y=monthly_mean["moving_avg"],
    mode="lines",
    name=f"{ma_window}-Month Moving Average",
    line=dict(width=3, dash="dash")
))

fig_trend.update_layout(
    title=(
        f"Monthly Trend of {PARAMETER_LABELS[trend_parameter]}<br>"
        f"Location: {trend_location} (Spring + Neap Combined)"
    ),
    xaxis_title="Month",
    yaxis_title=PARAMETER_LABELS[trend_parameter],
    height=500,
    hovermode="x unified"
)

st.plotly_chart(fig_trend, use_container_width=True)


with st.expander("📋 View Monthly Trend Data"):
    display_df = monthly_mean.copy()
    display_df["Month"] = display_df["year_month"].dt.strftime("%Y-%m")
    display_df = display_df.rename(columns={
        trend_parameter: "Monthly Mean",
        "moving_avg": f"{ma_window}-Month Moving Avg"
    })
    st.dataframe(
        display_df[["Month", "Monthly Mean", f"{ma_window}-Month Moving Avg"]],
        use_container_width=True
    )


#Compare Multiple Locations (Month + Tide Based)
st.markdown("---")
st.header("🌍 Compare Multiple Locations (Month + Tide Based)")

st.sidebar.header("🌍 Location Comparison Filter")

compare_month = st.sidebar.selectbox(
    "Select Month",
    sorted(df["month"].dropna().unique()),
    key="compare_month"
)

compare_tide = st.sidebar.selectbox(
    "Select Tide Type",
    sorted(df["tide_type"].dropna().unique()),
    key="compare_tide"
)

compare_parameter_multi = st.sidebar.selectbox(
    "Select Parameter",
    list(PARAMETER_LABELS.keys()),
    format_func=lambda x: PARAMETER_LABELS[x],
    key="compare_parameter_multi"
)

compare_stat = st.sidebar.selectbox(
    "Select Statistic",
    ["Max", "Min", "Mean"],
    key="compare_stat"
)


multi_df = df[
    (df["month"] == compare_month) &
    (df["tide_type"] == compare_tide)
].copy()

if multi_df.empty:
    st.warning("No data available for selected month and tide type.")
    st.stop()


if compare_stat == "Max":
    result_df = (
        multi_df
        .groupby("location")[compare_parameter_multi]
        .max()
        .reset_index()
    )
elif compare_stat == "Min":
    result_df = (
        multi_df
        .groupby("location")[compare_parameter_multi]
        .min()
        .reset_index()
    )
else:
    result_df = (
        multi_df
        .groupby("location")[compare_parameter_multi]
        .mean()
        .reset_index()
    )


result_df = result_df.rename(columns={
    compare_parameter_multi: compare_stat
})


import plotly.express as px

fig_multi = px.bar(
    result_df,
    x="location",
    y=compare_stat,
    title=(
        f"{compare_stat} of {PARAMETER_LABELS[compare_parameter_multi]}<br>"
        f"Month: {compare_month} | Tide: {compare_tide}"
    ),
)

fig_multi.update_layout(
    xaxis_title="Location",
    yaxis_title=PARAMETER_LABELS[compare_parameter_multi],
    height=500
)

st.plotly_chart(fig_multi, use_container_width=True)


with st.expander("📋 View Comparison Data"):
    st.dataframe(result_df, use_container_width=True)



#Interactive Map Showing Selected Statistic
st.markdown("---")
st.header("🗺️ Spatial Distribution Map")


st.sidebar.header("🗺️ Map Filter")

map_month = st.sidebar.selectbox(
    "Select Month (Map)",
    sorted(df["month"].dropna().unique()),
    key="map_month"
)

map_tide = st.sidebar.selectbox(
    "Select Tide Type (Map)",
    sorted(df["tide_type"].dropna().unique()),
    key="map_tide"
)

map_parameter = st.sidebar.selectbox(
    "Select Parameter (Map)",
    list(PARAMETER_LABELS.keys()),
    format_func=lambda x: PARAMETER_LABELS[x],
    key="map_parameter"
)

map_stat = st.sidebar.selectbox(
    "Select Statistic (Map)",
    ["Max", "Min", "Mean"],
    key="map_stat"
)


map_df = df[
    (df["month"] == map_month) &
    (df["tide_type"] == map_tide)
].copy()

if map_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()


if map_stat == "Max":
    map_result = (
        map_df.groupby(["location", "latitude", "longitude"])[map_parameter]
        .max()
        .reset_index()
    )
elif map_stat == "Min":
    map_result = (
        map_df.groupby(["location", "latitude", "longitude"])[map_parameter]
        .min()
        .reset_index()
    )
else:
    map_result = (
        map_df.groupby(["location", "latitude", "longitude"])[map_parameter]
        .mean()
        .reset_index()
    )

map_result = map_result.rename(columns={
    map_parameter: map_stat
})


import numpy as np
import plotly.express as px

# Calculate dynamic center
center_lat = map_result["latitude"].mean()
center_lon = map_result["longitude"].mean()

# Calculate spatial spread
lat_range = map_result["latitude"].max() - map_result["latitude"].min()
lon_range = map_result["longitude"].max() - map_result["longitude"].min()

max_range = max(lat_range, lon_range)

# Auto zoom logic
if max_range < 0.01:
    zoom_level = 12
elif max_range < 0.05:
    zoom_level = 10
elif max_range < 0.1:
    zoom_level = 9
elif max_range < 0.5:
    zoom_level = 8
else:
    zoom_level = 6

fig_map = px.scatter_mapbox(
    map_result,
    lat="latitude",
    lon="longitude",
    size=map_stat,
    color=map_stat,
    hover_name="location",
    hover_data={
        map_stat: True,
        "latitude": False,
        "longitude": False
    },
    color_continuous_scale="Viridis",
    size_max=25,
    zoom=zoom_level,
    center={"lat": center_lat, "lon": center_lon},
    height=600,
    title=(
        f"{map_stat} of {PARAMETER_LABELS[map_parameter]}<br>"
        f"Month: {map_month} | Tide: {map_tide}"
    )
)

fig_map.update_layout(mapbox_style="open-street-map")

st.plotly_chart(fig_map, use_container_width=True)


#Pollution Hotspot
st.markdown("---")
st.header("🔥 Pollution Hotspot Detector")


st.sidebar.header("🔥 Hotspot Filter")

hotspot_month = st.sidebar.selectbox(
    "Select Month (Hotspot)",
    sorted(df["month"].dropna().unique()),
    key="hotspot_month"
)

hotspot_tide = st.sidebar.selectbox(
    "Select Tide Type (Hotspot)",
    sorted(df["tide_type"].dropna().unique()),
    key="hotspot_tide"
)

hotspot_parameter = st.sidebar.selectbox(
    "Select Parameter (Hotspot)",
    list(POLLUTION_THRESHOLDS.keys()),
    format_func=lambda x: PARAMETER_LABELS.get(x, x),
    key="hotspot_parameter"
)


hotspot_df = df[
    (df["month"] == hotspot_month) &
    (df["tide_type"] == hotspot_tide)
].copy()

if hotspot_df.empty:
    st.warning("No data available.")
    st.stop()


hotspot_grouped = (
    hotspot_df
    .groupby(["location", "latitude", "longitude"])[hotspot_parameter]
    .mean()
    .reset_index()
)


threshold_info = POLLUTION_THRESHOLDS[hotspot_parameter]

def detect_hotspot(value):
    if "type" in threshold_info:
        if threshold_info["type"] == "max":
            return value > threshold_info["limit"]
        elif threshold_info["type"] == "min":
            return value < threshold_info["limit"]
    else:
        return (
            value < threshold_info["limit_low"] or
            value > threshold_info["limit_high"]
        )

hotspot_grouped["Hotspot"] = hotspot_grouped[hotspot_parameter].apply(detect_hotspot)


import plotly.express as px

fig_hotspot = px.scatter_mapbox(
    hotspot_grouped,
    lat="latitude",
    lon="longitude",
    color="Hotspot",
    size=hotspot_parameter,
    hover_name="location",
    hover_data={hotspot_parameter: True},
    zoom=8,
    height=600,
    title=(
        f"Hotspot Detection: {PARAMETER_LABELS.get(hotspot_parameter)}<br>"
        f"{hotspot_month} | {hotspot_tide}"
    ),
    color_discrete_map={
        True: "red",
        False: "green"
    }
)

fig_hotspot.update_layout(mapbox_style="open-street-map")

st.plotly_chart(fig_hotspot, use_container_width=True)


st.subheader("Hotspot Summary")

hotspot_count = hotspot_grouped["Hotspot"].sum()

st.write(f"🚨 Total Hotspot Locations: {hotspot_count}")

st.dataframe(hotspot_grouped, use_container_width=True)





# 🌊 Annual Max Envelope Plot (Spring vs Neap)

st.markdown("---")
st.header("📈 Annual Max Envelope (Spring vs Neap)")

st.sidebar.header("📈 Annual Max Envelope Filter")

annual_parameter = st.sidebar.selectbox(
    "Select Parameter (Annual Max)",
    list(PARAMETER_LABELS.keys()),
    format_func=lambda x: PARAMETER_LABELS[x],
    key="annual_parameter"
)

# Group by month, tide, location → get max
annual_df = (
    df.groupby(["month_num", "month", "tide_type", "location"])[annual_parameter]
    .max()
    .reset_index()
)

annual_df = annual_df.sort_values("month_num")

spring_df = annual_df[annual_df["tide_type"] == "Spring"]
neap_df = annual_df[annual_df["tide_type"] == "Neap"]

spring_pivot = spring_df.pivot(
    index="month_num",
    columns="location",
    values=annual_parameter
)

neap_pivot = neap_df.pivot(
    index="month_num",
    columns="location",
    values=annual_parameter
)

import plotly.graph_objects as go

fig = go.Figure()

months = sorted(df["month_num"].unique())

# ----------------------
# 🌊 SPRING
# ----------------------
if not spring_pivot.empty and len(spring_pivot.columns) == 2:

    loc1, loc2 = spring_pivot.columns.tolist()

    fig.add_trace(go.Scatter(
        x=months,
        y=spring_pivot[loc1],
        mode="lines+markers",
        name=f"Spring - {loc1}",
        line=dict(dash="solid")
    ))

    fig.add_trace(go.Scatter(
        x=months,
        y=spring_pivot[loc2],
        mode="lines+markers",
        name=f"Spring - {loc2}",
        line=dict(dash="solid")
    ))

    fig.add_trace(go.Scatter(
        x=months + months[::-1],
        y=list(spring_pivot[loc1]) + list(spring_pivot[loc2][::-1]),
        fill='toself',
        fillcolor='rgba(0, 100, 255, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name="Spring Max Range"
    ))

# ----------------------
# 🌙 NEAP
# ----------------------
if not neap_pivot.empty and len(neap_pivot.columns) == 2:

    loc1, loc2 = neap_pivot.columns.tolist()

    fig.add_trace(go.Scatter(
        x=months,
        y=neap_pivot[loc1],
        mode="lines+markers",
        name=f"Neap - {loc1}",
        line=dict(dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=months,
        y=neap_pivot[loc2],
        mode="lines+markers",
        name=f"Neap - {loc2}",
        line=dict(dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=months + months[::-1],
        y=list(neap_pivot[loc1]) + list(neap_pivot[loc2][::-1]),
        fill='toself',
        fillcolor='rgba(255, 100, 0, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name="Neap Max Range"
    ))

fig.update_layout(
    title=f"Annual Maximum {PARAMETER_LABELS[annual_parameter]} Envelope (Spring vs Neap)",
    xaxis_title="Month",
    yaxis_title=PARAMETER_LABELS[annual_parameter],
    xaxis=dict(
        tickmode='array',
        tickvals=months,
        ticktext=[
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ][:len(months)]
    ),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# ======================================================
# 📊 TABLE SECTION (NEW)
# ======================================================

st.subheader("📋 Monthly Maximum Values Table")

# Merge Spring & Neap into one table
table_df = pd.DataFrame({"Month_Num": months})

# Add Spring columns
if not spring_pivot.empty:
    for col in spring_pivot.columns:
        table_df[f"Spring - {col}"] = spring_pivot[col].values

# Add Neap columns
if not neap_pivot.empty:
    for col in neap_pivot.columns:
        table_df[f"Neap - {col}"] = neap_pivot[col].values

# Add Month Name
month_map = dict(zip(df["month_num"], df["month"]))
table_df["Month"] = table_df["Month_Num"].map(month_map)

# Reorder columns
cols = ["Month"] + [c for c in table_df.columns if c not in ["Month", "Month_Num"]]
table_df = table_df[cols]

# Display table
st.dataframe(table_df, use_container_width=True)



# 🌊 Annual Min Envelope Plot (Spring vs Neap)

st.markdown("---")
st.header("📉 Annual Min Envelope (Spring vs Neap)")

st.sidebar.header("📉 Annual Min Envelope Filter")

annual_min_parameter = st.sidebar.selectbox(
    "Select Parameter (Annual Min)",
    list(PARAMETER_LABELS.keys()),
    format_func=lambda x: PARAMETER_LABELS[x],
    key="annual_min_parameter"
)

# ---------------------------------------------------
# Calculate Monthly Minimum
# ---------------------------------------------------

annual_min_df = (
    df.groupby(["month_num", "month", "tide_type", "location"])[annual_min_parameter]
    .min()
    .reset_index()
)

annual_min_df = annual_min_df.sort_values("month_num")

spring_df = annual_min_df[annual_min_df["tide_type"] == "Spring"]
neap_df = annual_min_df[annual_min_df["tide_type"] == "Neap"]

spring_pivot = spring_df.pivot(
    index="month_num",
    columns="location",
    values=annual_min_parameter
)

neap_pivot = neap_df.pivot(
    index="month_num",
    columns="location",
    values=annual_min_parameter
)

import plotly.graph_objects as go

fig_min = go.Figure()

months = sorted(df["month_num"].unique())

# ---------------------------------------------------
# SPRING
# ---------------------------------------------------

if not spring_pivot.empty and len(spring_pivot.columns) == 2:

    loc1, loc2 = spring_pivot.columns.tolist()

    fig_min.add_trace(go.Scatter(
        x=months,
        y=spring_pivot[loc1],
        mode="lines+markers",
        name=f"Spring - {loc1}",
        line=dict(dash="solid")
    ))

    fig_min.add_trace(go.Scatter(
        x=months,
        y=spring_pivot[loc2],
        mode="lines+markers",
        name=f"Spring - {loc2}",
        line=dict(dash="solid")
    ))

    # Shaded envelope
    fig_min.add_trace(go.Scatter(
        x=months + months[::-1],
        y=list(spring_pivot[loc1]) + list(spring_pivot[loc2][::-1]),
        fill='toself',
        fillcolor='rgba(0, 150, 0, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name="Spring Min Range"
    ))

# ---------------------------------------------------
# NEAP
# ---------------------------------------------------

if not neap_pivot.empty and len(neap_pivot.columns) == 2:

    loc1, loc2 = neap_pivot.columns.tolist()

    fig_min.add_trace(go.Scatter(
        x=months,
        y=neap_pivot[loc1],
        mode="lines+markers",
        name=f"Neap - {loc1}",
        line=dict(dash="dash")
    ))

    fig_min.add_trace(go.Scatter(
        x=months,
        y=neap_pivot[loc2],
        mode="lines+markers",
        name=f"Neap - {loc2}",
        line=dict(dash="dash")
    ))

    # Shaded envelope
    fig_min.add_trace(go.Scatter(
        x=months + months[::-1],
        y=list(neap_pivot[loc1]) + list(neap_pivot[loc2][::-1]),
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name="Neap Min Range"
    ))

fig_min.update_layout(
    title=f"Annual Minimum {PARAMETER_LABELS[annual_min_parameter]} Envelope (Spring vs Neap)",
    xaxis_title="Month",
    yaxis_title=PARAMETER_LABELS[annual_min_parameter],
    xaxis=dict(
        tickmode='array',
        tickvals=months,
        ticktext=[
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ][:len(months)]
    ),
    height=600
)

st.plotly_chart(fig_min, use_container_width=True)

# ======================================================
# 📋 TABLE SECTION
# ======================================================

st.subheader("📋 Monthly Minimum Values Table")

table_df = pd.DataFrame({"Month_Num": months})

# Add Spring columns
if not spring_pivot.empty:
    for col in spring_pivot.columns:
        table_df[f"Spring - {col}"] = spring_pivot[col].values

# Add Neap columns
if not neap_pivot.empty:
    for col in neap_pivot.columns:
        table_df[f"Neap - {col}"] = neap_pivot[col].values

# Add month names
month_map = dict(zip(df["month_num"], df["month"]))
table_df["Month"] = table_df["Month_Num"].map(month_map)

# Reorder columns
cols = ["Month"] + [c for c in table_df.columns if c not in ["Month", "Month_Num"]]
table_df = table_df[cols]

# Round values
table_df = table_df.round(3)

st.dataframe(table_df, use_container_width=True)




# 📉 Annual Min Difference (Location A – Location B)

st.markdown("---")
st.header("📉 Annual Min Difference Between Locations")

st.sidebar.header("📉 Min Difference Filter")

min_diff_parameter = st.sidebar.selectbox(
    "Select Parameter (Min Difference)",
    list(PARAMETER_LABELS.keys()),
    format_func=lambda x: PARAMETER_LABELS[x],
    key="min_diff_parameter"
)

# --------------------------------------------------
# Calculate Monthly Minimum
# --------------------------------------------------

min_diff_df = (
    df.groupby(["month_num", "month", "tide_type", "location"])[min_diff_parameter]
    .min()
    .reset_index()
)

min_diff_df = min_diff_df.sort_values("month_num")

# Pivot table
pivot_min_df = min_diff_df.pivot_table(
    index=["month_num", "month", "tide_type"],
    columns="location",
    values=min_diff_parameter
).reset_index()

locations = df["location"].unique().tolist()

if len(locations) != 2:
    st.warning("This feature works for exactly two locations.")
    st.stop()

loc1, loc2 = locations

# Difference Calculation
pivot_min_df["Difference"] = pivot_min_df[loc1] - pivot_min_df[loc2]

# Separate tide type
spring_min_diff = pivot_min_df[pivot_min_df["tide_type"] == "Spring"]
neap_min_diff = pivot_min_df[pivot_min_df["tide_type"] == "Neap"]

# --------------------------------------------------
# Plot
# --------------------------------------------------

import plotly.graph_objects as go

fig_min_diff = go.Figure()

# Spring
fig_min_diff.add_trace(go.Scatter(
    x=spring_min_diff["month_num"],
    y=spring_min_diff["Difference"],
    mode="lines+markers",
    name="Spring Min Difference",
    line=dict(color="green")
))

# Neap
fig_min_diff.add_trace(go.Scatter(
    x=neap_min_diff["month_num"],
    y=neap_min_diff["Difference"],
    mode="lines+markers",
    name="Neap Min Difference",
    line=dict(color="red", dash="dash")
))

# Zero line
fig_min_diff.add_hline(
    y=0,
    line_dash="dot",
    line_color="black"
)

fig_min_diff.update_layout(
    title=f"Annual Min Difference ({loc1} - {loc2})<br>{PARAMETER_LABELS[min_diff_parameter]}",
    xaxis_title="Month",
    yaxis_title="Min Difference",
    xaxis=dict(
        tickmode='array',
        tickvals=sorted(df["month_num"].unique()),
        ticktext=[
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]
    ),
    height=600
)

st.plotly_chart(fig_min_diff, use_container_width=True)

# ======================================================
# 📋 TABLE SECTION
# ======================================================

st.subheader("📋 Monthly Minimum Difference Table")

# Sort properly
pivot_min_df = pivot_min_df.sort_values(["month_num", "tide_type"])

# Prepare table
table_min_df = pivot_min_df[[
    "month",
    "tide_type",
    loc1,
    loc2,
    "Difference"
]].copy()

table_min_df.columns = [
    "Month",
    "Tide Type",
    f"Min - {loc1}",
    f"Min - {loc2}",
    f"Difference ({loc1} - {loc2})"
]

# Round for clean display
table_min_df = table_min_df.round(3)

st.dataframe(table_min_df, use_container_width=True)




# 📊 Annual Max Difference (Location A – Location B)

st.markdown("---")
st.header("📉 Annual Max Difference Between Locations")

st.sidebar.header("📉 Max Difference Filter")

diff_parameter = st.sidebar.selectbox(
    "Select Parameter (Max Difference)",
    list(PARAMETER_LABELS.keys()),
    format_func=lambda x: PARAMETER_LABELS[x],
    key="diff_parameter"
)

# Group and calculate max
diff_df = (
    df.groupby(["month_num", "month", "tide_type", "location"])[diff_parameter]
    .max()
    .reset_index()
)

diff_df = diff_df.sort_values("month_num")

# Pivot
pivot_df = diff_df.pivot_table(
    index=["month_num", "month", "tide_type"],
    columns="location",
    values=diff_parameter
).reset_index()

locations = df["location"].unique().tolist()

if len(locations) != 2:
    st.warning("This feature works for exactly two locations.")
    st.stop()

loc1, loc2 = locations

# Calculate difference
pivot_df["Difference"] = pivot_df[loc1] - pivot_df[loc2]

# Separate tide types
spring_diff = pivot_df[pivot_df["tide_type"] == "Spring"]
neap_diff = pivot_df[pivot_df["tide_type"] == "Neap"]

import plotly.graph_objects as go

fig_diff = go.Figure()

# Spring line
fig_diff.add_trace(go.Scatter(
    x=spring_diff["month_num"],
    y=spring_diff["Difference"],
    mode="lines+markers",
    name="Spring Difference",
    line=dict(color="blue")
))

# Neap line
fig_diff.add_trace(go.Scatter(
    x=neap_diff["month_num"],
    y=neap_diff["Difference"],
    mode="lines+markers",
    name="Neap Difference",
    line=dict(color="orange", dash="dash")
))

# Zero reference line
fig_diff.add_hline(
    y=0,
    line_dash="dot",
    line_color="black"
)

fig_diff.update_layout(
    title=f"Annual Max Difference ({loc1} - {loc2})<br>{PARAMETER_LABELS[diff_parameter]}",
    xaxis_title="Month",
    yaxis_title="Max Difference",
    xaxis=dict(
        tickmode='array',
        tickvals=sorted(df["month_num"].unique()),
        ticktext=[
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]
    ),
    height=600
)

st.plotly_chart(fig_diff, use_container_width=True)

# ======================================================
# 📋 TABLE SECTION (NEW)
# ======================================================

st.subheader("📋 Monthly Maximum Difference Table")

# Sort properly
pivot_df = pivot_df.sort_values(["month_num", "tide_type"])

# Select and rename columns for clarity
table_df = pivot_df[[
    "month",
    "tide_type",
    loc1,
    loc2,
    "Difference"
]].copy()

table_df.columns = [
    "Month",
    "Tide Type",
    f"Max - {loc1}",
    f"Max - {loc2}",
    f"Difference ({loc1} - {loc2})"
]

# Round values for cleaner display
table_df = table_df.round(3)

st.dataframe(table_df, use_container_width=True)







#Water Quality Index (WQI) computation + class (Excellent–Poor)




st.sidebar.header("Water Quality Index (WQI)")

wqi_location = st.sidebar.selectbox(
    "Select Location (WQI)",
    df["location"].unique(),
    key="wqi_loc"
)

wqi_season = st.sidebar.selectbox(
    "Select Season (WQI)",
    df["season"].unique(),
    key="wqi_season"
)

wqi_tide = st.sidebar.selectbox(
    "Select Tide Type (WQI)",
    df["tide_type"].unique(),
    key="wqi_tide"
)



wqi_df = df[
    (df["location"] == wqi_location) &
    (df["season"] == wqi_season) &
    (df["tide_type"] == wqi_tide)
]


if wqi_df.empty:
    st.warning("No data available for WQI calculation")
    st.stop()

wqi_mean = wqi_df.mean(numeric_only=True)



wqi_components = []
wqi_sum = 0
weight_sum = 0

for param, info in WQI_PARAMS.items():
    value = wqi_mean.get(info["column"], None)

    if value is None or pd.isna(value):
        continue

    Qi = ((value - info["ideal"]) / (info["standard"] - info["ideal"])) * 100
    Wi = info["weight"]

    wqi_components.append({
        "Parameter": param,
        "Value": round(value, 2),
        "Qi": round(Qi, 2),
        "Wi": Wi,
        "Qi×Wi": round(Qi * Wi, 2)
    })

    wqi_sum += Qi * Wi
    weight_sum += Wi

WQI = round(wqi_sum / weight_sum, 2)



def classify_wqi(wqi):
    if wqi <= 25:
        return "Excellent"
    elif wqi <= 50:
        return "Good"
    elif wqi <= 75:
        return "Poor"
    elif wqi <= 100:
        return "Very Poor"
    else:
        return "Unsuitable"

wqi_class = classify_wqi(WQI)



st.subheader("💧 Water Quality Index (WQI)")

st.metric(
    label="WQI Score",
    value=WQI,
    delta=wqi_class
)



import plotly.express as px

wqi_comp_df = pd.DataFrame(wqi_components)

fig_wqi = px.bar(
    wqi_comp_df,
    x="Parameter",
    y="Qi×Wi",
    title="Parameter-wise Contribution to WQI"
)

st.plotly_chart(fig_wqi, use_container_width=True)


st.dataframe(wqi_comp_df, use_container_width=True)







