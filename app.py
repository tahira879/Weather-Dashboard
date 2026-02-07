import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from dotenv import load_dotenv

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Weather Dashboard Pro",
    page_icon="⚡",
    layout="wide"
)

# ---------------- THEME & CUSTOM CSS ----------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
        color: white;
    }
    /* Metric labels white */
    [data-testid="stMetricLabel"] {
        color: white !important;
    }
    /* Metric values orange like the graph */
    [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
        color: #FFA500 !important;
    }
    /* Input box label white */
    .stTextInput>label {
        color: white !important;
        font-weight: bold;
    }
    /* Sleek input box with orange focus */
    .stTextInput input {
        background-color: #262626 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    .stTextInput input:focus {
        border-color: #FFA500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- API SETUP ----------------
load_dotenv()
API_KEY = os.getenv("API_KEY")

# ---------------- HELPERS (WITH CACHING) ----------------
@st.cache_data(ttl=600)
def get_weather_data(city):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo_res = requests.get(geo_url).json()
        if not geo_res: return None, None, None
        
        lat, lon = geo_res[0]["lat"], geo_res[0]["lon"]

        w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        f_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        
        curr = requests.get(w_url).json()
        fore = requests.get(f_url).json()
        
        return curr, fore, geo_res[0]["name"]
    except Exception as e:
        return None, None, None

# ---------------- WEATHER EMOJI MAPPING ----------------
weather_emoji = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
}

# ---------------- APP LAYOUT ----------------
st.title("⚡ Weather Dashboard")

# Input box with label now white
city_input = st.text_input("Enter City Name", value="Karachi")

curr, fore, name = get_weather_data(city_input)

if curr:
    # --- HEADER SECTION ---
    col_title, col_icon = st.columns([4, 1])
    with col_title:
        st.header(f"Weather in {name}")
        st.write(f"**{curr['weather'][0]['description'].title()}** | {datetime.now().strftime('%A, %d %B %Y')}")
    with col_icon:
        icon_code = curr['weather'][0]['icon']
        st.image(f"http://openweathermap.org/img/wn/{icon_code}@2x.png", width=100)

    # --- METRICS SECTION ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temperature", f"{round(curr['main']['temp'])}°C", f"Feels {round(curr['main']['feels_like'])}°C")
    m2.metric("Humidity", f"{curr['main']['humidity']}%")
    m3.metric("Wind Speed", f"{curr['wind']['speed']} m/s")
    m4.metric("Pressure", f"{curr['main']['pressure']} hPa")

    st.divider()

    # --- MAIN CONTENT: CHART & SIDEBAR ---
    left_main, right_sidebar = st.columns([3, 1])

    with left_main:
        st.write("### 24-Hour Temperature Trend")
        
        chart_data = pd.DataFrame([
            {"Time": datetime.fromtimestamp(i['dt']), "Temp": i['main']['temp']} 
            for i in fore['list'][:8]
        ])
        
        fig = px.area(
            chart_data, x="Time", y="Temp", 
            markers=True, 
            template="plotly_dark",
            line_shape='spline',
            color_discrete_sequence=["#FFA500"]
        )
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(showgrid=True, gridcolor="#333", title="Temp (°C)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with right_sidebar:
        st.write("### 5-Day Forecast")
        for item in fore['list'][::8]:
            date = datetime.fromtimestamp(item['dt']).strftime("%d %b")
            f_temp = round(item['main']['temp'])
            main_weather = item['weather'][0]['main']
            emoji = weather_emoji.get(main_weather, "")
            st.write(f"**{date}**: {f_temp}°C {emoji}")

    # --- OPTIONAL: MAP ---
    with st.expander("📍 View Map Location"):
        map_df = pd.DataFrame({'lat': [curr['coord']['lat']], 'lon': [curr['coord']['lon']]})
        st.map(map_df, zoom=10)

else:
    st.error("⚠️ City not found or API Key missing. Please check your credentials.")
