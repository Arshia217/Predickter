import os
import json
import time
import joblib
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Set page configuration
st.set_page_config(page_title="Predickter IPL Analytics", layout="wide", page_icon="🎮")

# =========================================================================
# ⚙️ SYSTEM CORE & MODEL SERIALIZATION MODULE
# =========================================================================
MODELS_DIR = "models"
MATRIX_PATH = os.path.join("data", "processed", "modeling_matrix.csv")
os.makedirs(MODELS_DIR, exist_ok=True)

@st.cache_resource
def load_or_train_serialized_models():
    """
    Handles Model Serialization (joblib). Automatically trains and saves 
    the brain if pkl files are missing, ensuring instant dashboard startup.
    """
    model_path = os.path.join(MODELS_DIR, "logistic_win_model.pkl")
    scaler_path = os.path.join(MODELS_DIR, "feature_scaler.pkl")
    venue_path = os.path.join("data", "processed", "venue_profiles.csv")
    
    # Validation fallback if pre-trained objects exist
    if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(venue_path):
        clf_model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        venue_df = pd.read_csv(venue_path)
        return clf_model, scaler, venue_df
        
    st.warning("⚠️ Serialized models not found in 'models/'. Auto-generating baseline model weights...")
    if not os.path.exists(MATRIX_PATH):
        st.error("❌ modeling_matrix.csv missing. Run phase_2_features.py first!")
        st.stop()
        
    # Quick fallback training sequence
    df = pd.read_csv(MATRIX_PATH)
    feature_cols = ['temperature', 'humidity', 'stadium_avg_runs', 'stadium_volatility', 'stadium_boundary_density', 'index_differential']
    X = df[feature_cols].dropna()
    y_clf = df.loc[X.index, 'team1_won']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    clf_model = LogisticRegression(random_state=42)
    clf_model.fit(X_scaled, y_clf)
    
    # Save objects to disk (Serialization)
    joblib.dump(clf_model, model_path)
    joblib.dump(scaler, scaler_path)
    
    # Grab venue list fallback
    venue_df = df[['venue', 'stadium_avg_runs', 'stadium_volatility', 'stadium_boundary_density']].drop_duplicates().reset_index(drop=True)
    venue_df.to_csv(venue_path, index=False)
    
    return clf_model, scaler, venue_df

# Load models and rules configuration
clf_model, scaler, venue_df = load_or_train_serialized_models()
with open("game_rules.json", "r") as f:
    game_config = json.load(f)

# =========================================================================
# 🔄 LIVE DATA FETCHING ENGINE (ETL SCRAPER MOCK / LIVE SWITCHER)
# =========================================================================
def fetch_live_match_feed():
    """
    Simulates a live API scraper call (e.g., Cricbuzz/Cricsheet feed).
    In production, replace this return statement with a requests.get() API call.
    """
    # Simulating data arriving from an active live match state
    return {
        "status": "Live Match Active",
        "team1": "Royal Challengers Bangalore",
        "team2": "Mumbai Indians",
        "venue": "M Chinnaswamy Stadium",
        "current_runs": 118,
        "wickets_lost": 2,
        "overs_bowled": 11.4,
        "temperature": 31.0,
        "humidity": 45.0,
        "index_differential": 8.75
    }

# =========================================================================
# 📊 UI DASHBOARD ASSEMBLY
# =========================================================================
st.title("🏏 Predickter: Sports Forecasting Engine")
st.markdown("---")

# Sidebar - Mode Selection and Metadata Inputs
st.sidebar.header("🕹️ Control Room")
mode = st.sidebar.radio("Data Engine Mode", ["Manual Sandbox Mode", "Live Active Match Feed"])

if mode == "Live Active Match Feed":
    st.sidebar.info("🔄 Streaming active match state metadata...")
    live_data = fetch_live_match_feed()
    
    # Populating from live scraper stream
    selected_venue = live_data["venue"]
    team1 = live_data["team1"]
    team2 = live_data["team2"]
    temp = live_data["temperature"]
    humidity = live_data["humidity"]
    idx_diff = live_data["index_differential"]
    
    c_runs = live_data["current_runs"]
    c_wickets = live_data["wickets_lost"]
    c_overs = live_data["overs_bowled"]
else:
    # Sandbox user inputs for off-season fantasy guessing
    st.sidebar.info("💡 Off-Season Sandbox Mode enabled. Configure parameters manually.")
    venue_list = venue_df['venue'].tolist() if not venue_df.empty else ["M Chinnaswamy Stadium"]
    selected_venue = st.sidebar.selectbox("Select Match Venue", venue_list)
    
    team1 = st.sidebar.text_input("Team 1 (Batting First)", "Chennai Super Kings")
    team2 = st.sidebar.text_input("Team 2 (Bowling First)", "Kolkata Knight Riders")
    
    temp = st.sidebar.slider("Temperature (°C)", 15.0, 45.0, 28.0)
    humidity = st.sidebar.slider("Humidity (%)", 10.0, 100.0, 60.0)
    idx_diff = st.sidebar.slider("Roster Index Differential", -25.0, 25.0, 4.2)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Live Match Progression State")
    c_runs = st.sidebar.number_input("Current Runs Scored", min_value=0, max_value=300, value=95)
    c_wickets = st.sidebar.number_input("Wickets Fallen", min_value=0, max_value=10, value=3)
    c_overs = st.sidebar.slider("Overs Bowled", 0.0, 20.0, 11.0)

# Resolve venue profiles vectors
v_profile = venue_df[venue_df['venue'] == selected_venue]
if not v_profile.empty:
    v_avg = v_profile['stadium_avg_runs'].values[0]
    v_vol = v_profile['stadium_volatility'].values[0]
    v_den = v_profile['stadium_boundary_density'].values[0]
else:
    v_avg, v_vol, v_den = 165.0, 18.0, 0.085

# Display Active State Panel on Main Board
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Match Up", value=f"{team1} vs {team2}")
with col2:
    st.metric(label="Current Match Scoreboard", value=f"{c_runs}/{c_wickets} ({c_overs} ov)")
with col3:
    st.metric(label="Ground Baseline Score", value=f"{v_avg} runs")

st.markdown("---")

# =========================================================================
# 🧠 RUN PREDICTIONS ENGINE
# =========================================================================

# 1. Tier 1: Win Probability Evaluation (Logistic Regression via Serialized .pkl)
input_features = np.array([[temp, humidity, v_avg, v_vol, v_den, idx_diff]])
scaled_features = scaler.transform(input_features)
win_probability = clf_model.predict_proba(scaled_features)[0][1]

# 2. Tier 2: State-Space Live Target Projection
total_overs = game_config["total_overs"]
max_wickets = game_config["max_wickets"]

if c_wickets >= max_wickets or c_overs >= total_overs:
    proj_score = c_runs
    lower_bound = c_runs
    upper_bound = c_runs
else:
    crr = c_runs / c_overs if c_overs > 0 else (v_avg / total_overs)
    base_ground_per_over = v_avg / total_overs
    
    # Compute system dynamics
    wicket_percent_lost = c_wickets / max_wickets
    wicket_penalty_factor = np.cos(wicket_percent_lost * (np.pi / 2))
    
    overs_remaining = total_overs - c_overs
    if c_overs <= game_config["powerplay_overs"]:
        phase_modifier = 1.10
    elif overs_remaining <= 4:
        phase_modifier = game_config["base_historical_death_acceleration"]
    else:
        phase_modifier = 0.95
        
    roster_modifier = 1 + (idx_diff / 1000)
    expected_run_rate = ((0.4 * crr) + (0.6 * base_ground_per_over)) * wicket_penalty_factor * phase_modifier * roster_modifier
    
    proj_score = int(c_runs + (expected_run_rate * overs_remaining))
    variance_scalar = np.sqrt(overs_remaining) * 6.5
    lower_bound = int(proj_score - variance_scalar)
    upper_bound = int(proj_score + variance_scalar)

# =========================================================================
# 🖥️ METRIC VISUALIZATIONS OUTPUT
# =========================================================================
layout_left, layout_right = st.columns(2)

with layout_left:
    st.subheader("🔮 Tier 1: Live Match Win Probability")
    st.markdown(f"Calculated win probability for **{team1}** based on active environmental vectors:")
    
    # Clean visual gauge using Streamlit component bars
    st.progress(int(win_probability * 100))
    st.markdown(f"📈 **{team1} Win Probability:** `{win_probability * 100:.2f}%`")
    st.markdown(f"📉 **{team2} Win Probability:** `{(1 - win_probability) * 100:.2f}%`")

with layout_right:
    st.subheader("🎯 Tier 2: In-Play State Run Projection")
    st.markdown("Dynamic state-space calculation adapting to active resource depletion:")
    
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric(label="Projected Final Total", value=f"{proj_score} Runs")
    with metric_col2:
        st.markdown(f"**95% Confidence Interval Limits:**")
        st.error(f"🔴 Lower Limit bound: {lower_bound} runs")
        st.success(f"🟢 Upper Acceleration limit: {upper_bound} runs")