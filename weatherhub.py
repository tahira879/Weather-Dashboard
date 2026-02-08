import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from dotenv import load_dotenv

# ------------------- CONFIG & API SETUP -------------------
load_dotenv()
API_KEY = os.getenv("API_KEY") 

st.set_page_config(
    page_title="Weather Hub",
    page_icon="🌦️",
    layout="wide"
)

# ------------------- HELPER FUNCTIONS -------------------
def get_weather_data(city):
    try:
        geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo_data = requests.get(geo_url).json()
        if not geo_data: return None, None
        lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

        curr_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        curr_data = requests.get(curr_url).json()

        fore_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        fore_data = requests.get(fore_url).json()
        return curr_data, fore_data
    except:
        return None, None

# ------------------- SEARCH BAR LOGIC -------------------
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.markdown("<h1 style='text-align: center; margin-bottom: 0; color: white; text-shadow: 0 0 15px rgba(255,255,255,0.6);'>Weather Hub</h1>", unsafe_allow_html=True)
    city_input = st.text_input("", value="Karachi", placeholder="Search City...")

curr, fore = get_weather_data(city_input)

if curr and fore and curr.get("cod") == 200:
    # --- TIME & THEME LOGIC ---
    timezone_offset = curr['timezone']
    now = datetime.utcfromtimestamp(curr['dt'] + timezone_offset)
    sunrise = datetime.utcfromtimestamp(curr['sys']['sunrise'] + timezone_offset)
    sunset = datetime.utcfromtimestamp(curr['sys']['sunset'] + timezone_offset)
    is_day = sunrise <= now <= sunset

    if is_day:
        # MORNING THEME: Bright Sky
        bg_url = "https://images.unsplash.com/photo-1513002749550-c59d786b8e6c?q=80&w=1974&auto=format&fit=crop"
        overlay = "linear-gradient(rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.1))"
        card_bg = "rgba(255, 255, 255, 0.3)"
        text_color = "#000000"
        search_bg = "#FFFFFF"
        search_text = "#000000"
        accent = "#7000FF" # Electric Purple
        glow_color = "rgba(112, 0, 255, 0.8)"
        moon_html = ""
    else:
        # NIGHT THEME: Moody Clouds
        bg_url = "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?q=80&w=2000&auto=format&fit=crop"
        overlay = "linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.8))"
        card_bg = "rgba(0, 0, 0, 0.5)"
        text_color = "#E0E0E0"
        search_bg = "#000000"
        search_text = "#FFFFFF"
        accent = "#00E5FF" # Cyan
        glow_color = "rgba(0, 229, 255, 0.9)"
        moon_html = '<span style="font-size: 2rem; margin-left: 10px;">🌙</span>'

    # --- CUSTOM CSS ---
    st.markdown(f"""
        <style>
        .stApp {{ 
            background: {overlay}, url('{bg_url}'); 
            background-size: cover;
            background-position: center;
            color: {text_color}; 
            background-attachment: fixed; 
        }}
        
        .glass-card {{
            background: {card_bg};
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        }}

        .neon-accent {{
            color: {accent} !important;
            text-shadow: 0 0 10px {glow_color}, 0 0 20px {glow_color};
            font-weight: bold;
        }}

        .temp-display {{
            font-size: 5rem; 
            margin: 0;
            color: {accent} !important;
            text-shadow: 0 0 15px {glow_color};
            font-weight: 800;
        }}
        
        h1, h2, h3, p, span {{ color: {text_color}; }}

        /* DYNAMIC SEARCH BAR COLOR */
        div[data-baseweb="input"] {{
            background-color: {search_bg} !important; 
            border-radius: 12px !important;
            border: 1px solid {accent} !important; 
            box-shadow: 0 0 10px {glow_color};
            padding: 5px !important;
        }}

        div[data-baseweb="input"] input {{ 
            color: {search_text} !important; 
            text-align: center !important; 
            background-color: {search_bg} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- DASHBOARD CONTENT ---
    left_col, right_col = st.columns([1.2, 2])

    with left_col:
        st.markdown(f"""
        <div class="glass-card">
            <p style="opacity: 0.9; font-size: 0.9rem; margin:0; letter-spacing: 2px;">
                {curr['name'].upper()} {moon_html}
            </p>
            <p style="font-size: 0.8rem; opacity: 0.7;">{now.strftime('%A, %I:%M %p')}</p>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <h1 class="temp-display">{round(curr['main']['temp'])}°</h1>
                <img src="http://openweathermap.org/img/wn/{curr['weather'][0]['icon']}@4x.png" width="120">
            </div>
            <p class="neon-accent" style="text-transform: capitalize; font-size: 1.5rem;">
                {curr['weather'][0]['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        s1, s2, s3 = st.columns(3)
        stats = [("Humidity", curr["main"]["humidity"], "%"), ("Wind", int(curr["wind"]["speed"]), "m/s"), ("Feels", round(curr["main"]["feels_like"]), "°")]
        for col, (label, val, unit) in zip([s1, s2, s3], stats):
            col.markdown(f'''
                <div class="glass-card" style="text-align:center; padding:15px 10px;">
                    <p style="font-size:0.6rem; margin:0; opacity:0.8;">{label}</p>
                    <b class="neon-accent" style="font-size:1.1rem;">{val}{unit}</b>
                </div>''', unsafe_allow_html=True)

        # --- FILLING THE EMPTY SPACE ---
        temp = curr['main']['temp']
        wear = "Wear a light T-shirt" if temp > 25 else "Grab a light jacket" if temp > 15 else "Wear a heavy coat"
        st.markdown(f"""
        <div class="glass-card" style="margin-top: 10px;">
            <p class="neon-accent" style="font-size: 1rem; margin-bottom: 10px;">📋 Daily Insight</p>
            <p style="font-size: 0.9rem; line-height: 1.5; opacity: 0.9;">
                <b>Recommendation:</b> {wear}. 
                { 'Perfect for a walk!' if 'clear' in curr['weather'][0]['description'].lower() else 'Check for rain before heading out.'}
            </p>
            <p style="font-size: 0.8rem; opacity: 0.7; margin-top: 10px;">
                Visibility: {curr.get('visibility', 0)/1000} km | Pressure: {curr['main']['pressure']} hPa
            </p>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="glass-card" style="padding:20px;">', unsafe_allow_html=True)
        st.write("### 24-Hour Trend")
        chart_data = pd.DataFrame([{"Time": datetime.fromtimestamp(i['dt']).strftime("%H:%M"), "Temp": i['main']['temp']} for i in fore['list'][:8]])
        fig = px.area(chart_data, x="Time", y="Temp")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color=text_color, height=230, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
        )
        fig.update_traces(line_color=accent, fillcolor=glow_color.replace("0.8", "0.2").replace("0.9", "0.2"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("### 5-Day Forecast")
        f_cols = st.columns(5)
        for idx, item in enumerate(fore['list'][::8][:5]):
            with f_cols[idx]:
                day = datetime.fromtimestamp(item['dt']).strftime("%a")
                st.markdown(f"""
                <div class="glass-card" style="text-align: center; padding: 15px 5px;">
                    <p style="font-size: 0.8rem; margin:0; font-weight:600;">{day}</p>
                    <img src="http://openweathermap.org/img/wn/{item['weather'][0]['icon']}.png" width="40">
                    <p class="neon-accent" style="margin:0; font-size:1.1rem;">{round(item['main']['temp'])}°</p>
                </div>
                """, unsafe_allow_html=True)

    # --- FOOTER ---
    st.write("---")
    foot1, foot2, foot3 = st.columns(3)
    foot1.markdown(f'<div class="glass-card" style="text-align:center;">🌅 Sunrise: {sunrise.strftime("%I:%M %p")}</div>', unsafe_allow_html=True)
    foot2.markdown(f'<div class="glass-card" style="text-align:center;">🌇 Sunset: {sunset.strftime("%I:%M %p")}</div>', unsafe_allow_html=True)
    foot3.markdown(f'<div class="glass-card" style="text-align:center;">☁️ Cloudiness: {curr["clouds"]["all"]}%</div>', unsafe_allow_html=True)

else:
    st.error("⚠️ City not found. Please check spelling.")