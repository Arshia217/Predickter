# import os
# import json
# import time
# import joblib
# import pandas as pd
# import numpy as np
# import streamlit as st
# from sklearn.linear_model import LogisticRegression
# from sklearn.preprocessing import StandardScaler
# import requests 

# # Set page configuration
# st.set_page_config(page_title="Predickter IPL Analytics", layout="wide", page_icon="🎮")

# # =========================================================================
# # ⚙️ SYSTEM CORE & MODEL SERIALIZATION MODULE
# # =========================================================================
# MODELS_DIR = "models"
# MATRIX_PATH = os.path.join("data", "processed", "modeling_matrix.csv")
# os.makedirs(MODELS_DIR, exist_ok=True)

# @st.cache_resource
# def load_or_train_serialized_models():
#     """
#     Handles Model Serialization (joblib). Automatically trains and saves 
#     the brain if pkl files are missing, ensuring instant dashboard startup.
#     """
#     model_path = os.path.join(MODELS_DIR, "logistic_win_model.pkl")
#     scaler_path = os.path.join(MODELS_DIR, "feature_scaler.pkl")
#     venue_path = os.path.join("data", "processed", "venue_profiles.csv")
    
#     # Validation fallback if pre-trained objects exist
#     if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(venue_path):
#         clf_model = joblib.load(model_path)
#         scaler = joblib.load(scaler_path)
#         venue_df = pd.read_csv(venue_path)
#         return clf_model, scaler, venue_df
        
#     st.warning("⚠️ Serialized models not found in 'models/'. Auto-generating baseline model weights...")
#     if not os.path.exists(MATRIX_PATH):
#         st.error("❌ modeling_matrix.csv missing. Run phase_2_features.py first!")
#         st.stop()
        
#     # Quick fallback training sequence
#     df = pd.read_csv(MATRIX_PATH)
#     feature_cols = ['temperature', 'humidity', 'stadium_avg_runs', 'stadium_volatility', 'stadium_boundary_density', 'index_differential']
#     X = df[feature_cols].dropna()
#     y_clf = df.loc[X.index, 'team1_won']
    
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X)
    
#     clf_model = LogisticRegression(random_state=42)
#     clf_model.fit(X_scaled, y_clf)
    
#     # Save objects to disk (Serialization)
#     joblib.dump(clf_model, model_path)
#     joblib.dump(scaler, scaler_path)
    
#     # Grab venue list fallback
#     venue_df = df[['venue', 'stadium_avg_runs', 'stadium_volatility', 'stadium_boundary_density']].drop_duplicates().reset_index(drop=True)
#     venue_df.to_csv(venue_path, index=False)
    
#     return clf_model, scaler, venue_df

# # Load models and rules configuration
# clf_model, scaler, venue_df = load_or_train_serialized_models()
# with open("game_rules.json", "r") as f:
#     game_config = json.load(f)

# # =========================================================================
# # 🔄 LIVE DATA FETCHING ENGINE (ETL SCRAPER MOCK / LIVE SWITCHER)
# # =========================================================================
# def fetch_live_match_feed():
#     """
#     Simulates a live API scraper call (e.g., Cricbuzz/Cricsheet feed).
#     In production, replace this return statement with a requests.get() API call.
#     """
#     # Simulating data arriving from an active live match state
#     return {
#         "status": "Live Match Active",
#         "team1": "Royal Challengers Bangalore",
#         "team2": "Mumbai Indians",
#         "venue": "M Chinnaswamy Stadium",
#         "current_runs": 118,
#         "wickets_lost": 2,
#         "overs_bowled": 11.4,
#         "temperature": 31.0,
#         "humidity": 45.0,
#         "index_differential": 8.75
#     }

# #######Adding code to reconnect it to a live match for metrics and predictions################

# def fetch_live_match_feed():
#     """
#     🔥 PRODUCTION READY: Fetches live scorecard data from a real sports API gateway.
#     """
#     # Replace with your chosen API provider's endpoint URL
#     API_URL = "https://cricket-live-data-provider.p.rapidapi.com/match-current" 
    
#     headers = {
#         "X-RapidAPI-Key": "YOUR_SECRET_RAPID_API_KEY_HERE", # Get a free key from rapidapi.com
#         "X-RapidAPI-Host": "cricket-live-data-provider.p.rapidapi.com"
#     }
    
#     try:
#         response = requests.get(API_URL, headers=headers, timeout=5)
#         data = response.json()
        
#         # --- PARSING THE RAW API STATE SPACE ENGINE ---
#         # Note: Adjust these keys based on your specific API provider's JSON structure
#         live_match = data["results"][0]  # Grab the primary active match block
        
#         current_innings = live_match["live_scoreboard"]["innings"][-1] 
        
#         return {
#             "status": "Live Match Active",
#             "team1": live_match["team_home"]["name"],
#             "team2": live_match["team_away"]["name"],
#             "venue": live_match["venue"]["name"],
#             "current_runs": int(current_innings["runs"]),
#             "wickets_lost": int(current_innings["wickets"]),
#             "overs_bowled": float(current_innings["overs"]),
#             "temperature": 30.0, # Can layer in a weather API call here if desired
#             "humidity": 55.0,
#             # Calculated automatically in backend from live player rosters
#             "index_differential": 5.4 
#         }
        
#     except Exception as e:
#         # 🛡️ Safety Net: If the internet drops or API limits hit, fallback seamlessly
#         return {
#             "status": "API Stream Offline - Fallback Engaged",
#             "team1": "Gujarat Titans",
#             "team2": "Rajasthan Royals",
#             "venue": "Narendra Modi Stadium",
#             "current_runs": 84,
#             "wickets_lost": 2,
#             "overs_bowled": 9.3,
#             "temperature": 32.0,
#             "humidity": 50.0,
#             "index_differential": 2.1
#         }

# # =========================================================================
# # 📊 UI DASHBOARD ASSEMBLY
# # =========================================================================
# st.title("🏏 Predickter: Sports Forecasting Engine")
# st.markdown("---")

# # Sidebar - Mode Selection and Metadata Inputs
# st.sidebar.header("🕹️ Control Room")
# mode = st.sidebar.radio("Data Engine Mode", ["Manual Sandbox Mode", "Live Active Match Feed"])

# if mode == "Live Active Match Feed":
#     st.sidebar.info("🔄 Streaming active match state metadata...")
#     live_data = fetch_live_match_feed()
    
#     # Populating from live scraper stream
#     selected_venue = live_data["venue"]
#     team1 = live_data["team1"]
#     team2 = live_data["team2"]
#     temp = live_data["temperature"]
#     humidity = live_data["humidity"]
#     idx_diff = live_data["index_differential"]
    
#     c_runs = live_data["current_runs"]
#     c_wickets = live_data["wickets_lost"]
#     c_overs = live_data["overs_bowled"]
# else:
#     # Sandbox user inputs for off-season fantasy guessing
#     st.sidebar.info("💡 Off-Season Sandbox Mode enabled. Configure parameters manually.")
#     venue_list = venue_df['venue'].tolist() if not venue_df.empty else ["M Chinnaswamy Stadium"]
#     selected_venue = st.sidebar.selectbox("Select Match Venue", venue_list)
    
#     team1 = st.sidebar.text_input("Team 1 (Batting First)", "Chennai Super Kings")
#     team2 = st.sidebar.text_input("Team 2 (Bowling First)", "Kolkata Knight Riders")
    
#     temp = st.sidebar.slider("Temperature (°C)", 15.0, 45.0, 28.0)
#     humidity = st.sidebar.slider("Humidity (%)", 10.0, 100.0, 60.0)
#     idx_diff = st.sidebar.slider("Roster Index Differential", -25.0, 25.0, 4.2)
    
#     st.sidebar.markdown("---")
#     st.sidebar.subheader("Live Match Progression State")
#     c_runs = st.sidebar.number_input("Current Runs Scored", min_value=0, max_value=300, value=95)
#     c_wickets = st.sidebar.number_input("Wickets Fallen", min_value=0, max_value=10, value=3)
#     c_overs = st.sidebar.slider("Overs Bowled", 0.0, 20.0, 11.0)

# # Resolve venue profiles vectors
# v_profile = venue_df[venue_df['venue'] == selected_venue]
# if not v_profile.empty:
#     v_avg = v_profile['stadium_avg_runs'].values[0]
#     v_vol = v_profile['stadium_volatility'].values[0]
#     v_den = v_profile['stadium_boundary_density'].values[0]
# else:
#     v_avg, v_vol, v_den = 165.0, 18.0, 0.085

# # Display Active State Panel on Main Board
# col1, col2, col3 = st.columns(3)
# with col1:
#     st.metric(label="Match Up", value=f"{team1} vs {team2}")
# with col2:
#     st.metric(label="Current Match Scoreboard", value=f"{c_runs}/{c_wickets} ({c_overs} ov)")
# with col3:
#     st.metric(label="Ground Baseline Score", value=f"{v_avg} runs")

# st.markdown("---")

# # =========================================================================
# # 🧠 RUN PREDICTIONS ENGINE
# # =========================================================================

# # 1. Tier 1: Win Probability Evaluation (Logistic Regression via Serialized .pkl)
# input_features = np.array([[temp, humidity, v_avg, v_vol, v_den, idx_diff]])
# scaled_features = scaler.transform(input_features)
# win_probability = clf_model.predict_proba(scaled_features)[0][1]

# # 2. Tier 2: State-Space Live Target Projection
# total_overs = game_config["total_overs"]
# max_wickets = game_config["max_wickets"]

# if c_wickets >= max_wickets or c_overs >= total_overs:
#     proj_score = c_runs
#     lower_bound = c_runs
#     upper_bound = c_runs
# else:
#     crr = c_runs / c_overs if c_overs > 0 else (v_avg / total_overs)
#     base_ground_per_over = v_avg / total_overs
    
#     # Compute system dynamics
#     wicket_percent_lost = c_wickets / max_wickets
#     wicket_penalty_factor = np.cos(wicket_percent_lost * (np.pi / 2))
    
#     overs_remaining = total_overs - c_overs
#     if c_overs <= game_config["powerplay_overs"]:
#         phase_modifier = 1.10
#     elif overs_remaining <= 4:
#         phase_modifier = game_config["base_historical_death_acceleration"]
#     else:
#         phase_modifier = 0.95
        
#     roster_modifier = 1 + (idx_diff / 1000)
#     expected_run_rate = ((0.4 * crr) + (0.6 * base_ground_per_over)) * wicket_penalty_factor * phase_modifier * roster_modifier
    
#     proj_score = int(c_runs + (expected_run_rate * overs_remaining))
#     variance_scalar = np.sqrt(overs_remaining) * 6.5
#     lower_bound = int(proj_score - variance_scalar)
#     upper_bound = int(proj_score + variance_scalar)

# # =========================================================================
# # 🖥️ METRIC VISUALIZATIONS OUTPUT
# # =========================================================================
# layout_left, layout_right = st.columns(2)

# with layout_left:
#     st.subheader("🔮 Tier 1: Live Match Win Probability")
#     st.markdown(f"Calculated win probability for **{team1}** based on active environmental vectors:")
    
#     # Clean visual gauge using Streamlit component bars
#     st.progress(int(win_probability * 100))
#     st.markdown(f"📈 **{team1} Win Probability:** `{win_probability * 100:.2f}%`")
#     st.markdown(f"📉 **{team2} Win Probability:** `{(1 - win_probability) * 100:.2f}%`")

# with layout_right:
#     st.subheader("🎯 Tier 2: In-Play State Run Projection")
#     st.markdown("Dynamic state-space calculation adapting to active resource depletion:")
    
#     metric_col1, metric_col2 = st.columns(2)
#     with metric_col1:
#         st.metric(label="Projected Final Total", value=f"{proj_score} Runs")
#     with metric_col2:
#         st.markdown(f"**95% Confidence Interval Limits:**")
#         st.error(f"🔴 Lower Limit bound: {lower_bound} runs")
#         st.success(f"🟢 Upper Acceleration limit: {upper_bound} runs")



############################################################################################################################

# import os
# import json
# import time
# import joblib
# import pandas as pd
# import numpy as np
# import streamlit as st
# from sklearn.linear_model import LogisticRegression
# from sklearn.preprocessing import StandardScaler
# import requests
# from datetime import datetime
# from scripts.weather import WeatherPitchLookup

# # Set page configuration
# st.set_page_config(page_title="Predickter IPL Analytics", layout="wide", page_icon="🎮")

# # =========================================================================
# # 🔑 LIVE DATA PROVIDER CONFIG (CricketData.org — free tier: 100 req/day)
# # =========================================================================
# # Get a free key at https://cricketdata.org (no credit card required).
# # Set it as an environment variable, e.g.:
# #   export CRICKETDATA_API_KEY="your-key-here"
# # or, if deploying on Streamlit Community Cloud, add it to .streamlit/secrets.toml as:
# #   CRICKETDATA_API_KEY = "your-key-here"
# CRICKETDATA_API_KEY = os.getenv("CRICKETDATA_API_KEY") or st.secrets.get("CRICKETDATA_API_KEY", "")
# CRICKETDATA_BASE_URL = "https://api.cricapi.com/v1"

# # =========================================================================
# # ⚙️ SYSTEM CORE & MODEL SERIALIZATION MODULE
# # =========================================================================
# MODELS_DIR = "models"
# MATRIX_PATH = os.path.join("data", "processed", "modeling_matrix.csv")
# os.makedirs(MODELS_DIR, exist_ok=True)

# @st.cache_resource
# def load_or_train_serialized_models():
#     """
#     Handles Model Serialization (joblib). Automatically trains and saves 
#     the brain if pkl files are missing, ensuring instant dashboard startup.
#     """
#     model_path = os.path.join(MODELS_DIR, "logistic_win_model.pkl")
#     scaler_path = os.path.join(MODELS_DIR, "feature_scaler.pkl")
#     venue_path = os.path.join("data", "processed", "venue_profiles.csv")
    
#     # Validation fallback if pre-trained objects exist
#     if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(venue_path):
#         clf_model = joblib.load(model_path)
#         scaler = joblib.load(scaler_path)
#         venue_df = pd.read_csv(venue_path)
#         return clf_model, scaler, venue_df
        
#     st.warning("⚠️ Serialized models not found in 'models/'. Auto-generating baseline model weights...")
#     if not os.path.exists(MATRIX_PATH):
#         st.error("❌ modeling_matrix.csv missing. Run phase_2_features.py first!")
#         st.stop()
        
#     # Quick fallback training sequence
#     df = pd.read_csv(MATRIX_PATH)
#     feature_cols = ['temperature', 'humidity', 'stadium_avg_runs', 'stadium_volatility', 'stadium_boundary_density', 'index_differential']
#     X = df[feature_cols].dropna()
#     y_clf = df.loc[X.index, 'team1_won']
    
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X)
    
#     clf_model = LogisticRegression(random_state=42)
#     clf_model.fit(X_scaled, y_clf)
    
#     # Save objects to disk (Serialization)
#     joblib.dump(clf_model, model_path)
#     joblib.dump(scaler, scaler_path)
    
#     # Grab venue list fallback
#     venue_df = df[['venue', 'stadium_avg_runs', 'stadium_volatility', 'stadium_boundary_density']].drop_duplicates().reset_index(drop=True)
#     venue_df.to_csv(venue_path, index=False)
    
#     return clf_model, scaler, venue_df

# # Load models and rules configuration
# clf_model, scaler, venue_df = load_or_train_serialized_models()
# with open("game_rules.json", "r") as f:
#     game_config = json.load(f)

# # =========================================================================
# # 🔄 LIVE DATA FETCHING ENGINE (ETL SCRAPER MOCK / LIVE SWITCHER)
# # =========================================================================
# _weather_lookup = WeatherPitchLookup()

# _FALLBACK_MATCH = {
#     "status": "API Stream Offline - Fallback Engaged",
#     "team1": "Gujarat Titans",
#     "team2": "Rajasthan Royals",
#     "venue": "Narendra Modi Stadium",
#     "current_runs": 84,
#     "wickets_lost": 2,
#     "overs_bowled": 9.3,
#     "temperature": 32.0,
#     "humidity": 50.0,
#     "index_differential": 2.1
# }

# @st.cache_data(ttl=60, show_spinner=False)
# def fetch_live_match_feed():
#     """
#     Fetches live scorecard data from CricketData.org (free tier: 100 requests/day).
#     Cached for 60s per Streamlit session so auto-reruns don't burn through the daily quota.
#     Falls back to simulated data if no key is set, no match is live, or the request fails.
#     """
#     if not CRICKETDATA_API_KEY:
#         fallback = dict(_FALLBACK_MATCH)
#         fallback["status"] = "No API Key Set - Fallback Engaged"
#         return fallback

#     try:
#         response = requests.get(
#             f"{CRICKETDATA_BASE_URL}/currentMatches",
#             params={"apikey": CRICKETDATA_API_KEY, "offset": 0},
#             timeout=6
#         )
#         response.raise_for_status()
#         payload = response.json()

#         if payload.get("status") != "success" or not payload.get("data"):
#             fallback = dict(_FALLBACK_MATCH)
#             fallback["status"] = "No Live Matches Found - Fallback Engaged"
#             return fallback

#         # Only keep matches that have actually started and not yet ended
#         live_matches = [
#             m for m in payload["data"]
#             if m.get("matchStarted") and not m.get("matchEnded")
#         ]
#         # Prefer an IPL match specifically if one is live; otherwise take any live match
#         ipl_matches = [m for m in live_matches if "indian premier league" in m.get("name", "").lower()
#                         or "ipl" in m.get("name", "").lower()]
#         candidates = ipl_matches or live_matches

#         if not candidates:
#             fallback = dict(_FALLBACK_MATCH)
#             fallback["status"] = "No Live Matches Found - Fallback Engaged"
#             return fallback

#         match = candidates[0]
#         teams = match.get("teams", ["Team A", "Team B"])
#         scores = match.get("score", [])
#         current_innings = scores[-1] if scores else {"r": 0, "w": 0, "o": 0.0}
#         venue = match.get("venue", "Unknown Venue")

#         # Real weather for the venue, using your existing WeatherPitchLookup module
#         match_date = match.get("date", datetime.now().strftime("%Y-%m-%d"))
#         temperature, humidity = _weather_lookup.get_weather(venue, match_date)

#         return {
#             "status": "Live Match Active",
#             "team1": teams[0] if len(teams) > 0 else "Team A",
#             "team2": teams[1] if len(teams) > 1 else "Team B",
#             "venue": venue,
#             "current_runs": int(current_innings.get("r", 0)),
#             "wickets_lost": int(current_innings.get("w", 0)),
#             "overs_bowled": float(current_innings.get("o", 0.0)),
#             "temperature": temperature,
#             "humidity": humidity,
#             # CricketData's free tier doesn't expose roster strength, so this stays
#             # a neutral default until you plug in your own roster-index calculation.
#             "index_differential": 0.0
#         }

#     except requests.exceptions.RequestException as e:
#         fallback = dict(_FALLBACK_MATCH)
#         fallback["status"] = f"API Stream Offline - Fallback Engaged ({type(e).__name__})"
#         return fallback

# # =========================================================================
# # 📊 UI DASHBOARD ASSEMBLY
# # =========================================================================
# st.title("🏏 Predickter: Sports Forecasting Engine")
# st.markdown("---")

# # Sidebar - Mode Selection and Metadata Inputs
# st.sidebar.header("🕹️ Control Room")
# mode = st.sidebar.radio("Data Engine Mode", ["Manual Sandbox Mode", "Live Active Match Feed"])

# if mode == "Live Active Match Feed":
#     live_data = fetch_live_match_feed()

#     if live_data["status"] == "Live Match Active":
#         st.sidebar.success(f"🔴 {live_data['status']}")
#     elif live_data["status"] == "No API Key Set - Fallback Engaged":
#         st.sidebar.warning("⚠️ No CRICKETDATA_API_KEY set — showing sample data. See app.py header for setup steps.")
#     else:
#         st.sidebar.warning(f"⚠️ {live_data['status']}")
    
#     # Populating from live scraper stream
#     selected_venue = live_data["venue"]
#     team1 = live_data["team1"]
#     team2 = live_data["team2"]
#     temp = live_data["temperature"]
#     humidity = live_data["humidity"]
#     idx_diff = live_data["index_differential"]
    
#     c_runs = live_data["current_runs"]
#     c_wickets = live_data["wickets_lost"]
#     c_overs = live_data["overs_bowled"]
# else:
#     # Sandbox user inputs for off-season fantasy guessing
#     st.sidebar.info("💡 Off-Season Sandbox Mode enabled. Configure parameters manually.")
#     venue_list = venue_df['venue'].tolist() if not venue_df.empty else ["M Chinnaswamy Stadium"]
#     selected_venue = st.sidebar.selectbox("Select Match Venue", venue_list)
    
#     team1 = st.sidebar.text_input("Team 1 (Batting First)", "Chennai Super Kings")
#     team2 = st.sidebar.text_input("Team 2 (Bowling First)", "Kolkata Knight Riders")
    
#     temp = st.sidebar.slider("Temperature (°C)", 15.0, 45.0, 28.0)
#     humidity = st.sidebar.slider("Humidity (%)", 10.0, 100.0, 60.0)
#     idx_diff = st.sidebar.slider("Roster Index Differential", -25.0, 25.0, 4.2)
    
#     st.sidebar.markdown("---")
#     st.sidebar.subheader("Live Match Progression State")
#     c_runs = st.sidebar.number_input("Current Runs Scored", min_value=0, max_value=300, value=95)
#     c_wickets = st.sidebar.number_input("Wickets Fallen", min_value=0, max_value=10, value=3)
#     c_overs = st.sidebar.slider("Overs Bowled", 0.0, 20.0, 11.0)

# # Resolve venue profiles vectors
# v_profile = venue_df[venue_df['venue'] == selected_venue]
# if not v_profile.empty:
#     v_avg = v_profile['stadium_avg_runs'].values[0]
#     v_vol = v_profile['stadium_volatility'].values[0]
#     v_den = v_profile['stadium_boundary_density'].values[0]
# else:
#     v_avg, v_vol, v_den = 165.0, 18.0, 0.085

# # Display Active State Panel on Main Board
# col1, col2, col3 = st.columns(3)
# with col1:
#     st.metric(label="Match Up", value=f"{team1} vs {team2}")
# with col2:
#     st.metric(label="Current Match Scoreboard", value=f"{c_runs}/{c_wickets} ({c_overs} ov)")
# with col3:
#     st.metric(label="Ground Baseline Score", value=f"{v_avg} runs")

# st.markdown("---")

# # =========================================================================
# # 🧠 RUN PREDICTIONS ENGINE
# # =========================================================================

# # 1. Tier 1: Win Probability Evaluation (Logistic Regression via Serialized .pkl)
# input_features = np.array([[temp, humidity, v_avg, v_vol, v_den, idx_diff]])
# scaled_features = scaler.transform(input_features)
# win_probability = clf_model.predict_proba(scaled_features)[0][1]

# # 2. Tier 2: State-Space Live Target Projection
# total_overs = game_config["total_overs"]
# max_wickets = game_config["max_wickets"]

# if c_wickets >= max_wickets or c_overs >= total_overs:
#     proj_score = c_runs
#     lower_bound = c_runs
#     upper_bound = c_runs
# else:
#     crr = c_runs / c_overs if c_overs > 0 else (v_avg / total_overs)
#     base_ground_per_over = v_avg / total_overs
    
#     # Compute system dynamics
#     wicket_percent_lost = c_wickets / max_wickets
#     wicket_penalty_factor = np.cos(wicket_percent_lost * (np.pi / 2))
    
#     overs_remaining = total_overs - c_overs
#     if c_overs <= game_config["powerplay_overs"]:
#         phase_modifier = 1.10
#     elif overs_remaining <= 4:
#         phase_modifier = game_config["base_historical_death_acceleration"]
#     else:
#         phase_modifier = 0.95
        
#     roster_modifier = 1 + (idx_diff / 1000)
#     expected_run_rate = ((0.4 * crr) + (0.6 * base_ground_per_over)) * wicket_penalty_factor * phase_modifier * roster_modifier
    
#     proj_score = int(c_runs + (expected_run_rate * overs_remaining))
#     variance_scalar = np.sqrt(overs_remaining) * 6.5
#     lower_bound = int(proj_score - variance_scalar)
#     upper_bound = int(proj_score + variance_scalar)

# # =========================================================================
# # 🖥️ METRIC VISUALIZATIONS OUTPUT
# # =========================================================================
# layout_left, layout_right = st.columns(2)

# with layout_left:
#     st.subheader("🔮 Tier 1: Live Match Win Probability")
#     st.markdown(f"Calculated win probability for **{team1}** based on active environmental vectors:")
    
#     # Clean visual gauge using Streamlit component bars
#     st.progress(int(win_probability * 100))
#     st.markdown(f"📈 **{team1} Win Probability:** `{win_probability * 100:.2f}%`")
#     st.markdown(f"📉 **{team2} Win Probability:** `{(1 - win_probability) * 100:.2f}%`")

# with layout_right:
#     st.subheader("🎯 Tier 2: In-Play State Run Projection")
#     st.markdown("Dynamic state-space calculation adapting to active resource depletion:")
    
#     metric_col1, metric_col2 = st.columns(2)
#     with metric_col1:
#         st.metric(label="Projected Final Total", value=f"{proj_score} Runs")
#     with metric_col2:
#         st.markdown(f"**95% Confidence Interval Limits:**")
#         st.error(f"🔴 Lower Limit bound: {lower_bound} runs")
#         st.success(f"🟢 Upper Acceleration limit: {upper_bound} runs")

###################################################################################################################################

import os
import json
import time
import joblib
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import requests
from datetime import datetime
from scripts.weather import WeatherPitchLookup
from scripts.roster_index import calculate_index_differential, get_all_ipl_teams

# Set page configuration
st.set_page_config(page_title="Predickter IPL Analytics", layout="wide", page_icon="🎮")

# =========================================================================
# 🔑 LIVE DATA PROVIDER CONFIG (CricketData.org — free tier: 100 req/day)
# =========================================================================
# Get a free key at https://cricketdata.org (no credit card required).
# Set it as an environment variable, e.g.:
#   export CRICKETDATA_API_KEY="your-key-here"
# or, if deploying on Streamlit Community Cloud, add it to .streamlit/secrets.toml as:
#   CRICKETDATA_API_KEY = "your-key-here"
CRICKETDATA_API_KEY = os.getenv("CRICKETDATA_API_KEY") or st.secrets.get("CRICKETDATA_API_KEY", "")
CRICKETDATA_BASE_URL = "https://api.cricapi.com/v1"

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

# def adjust_win_probability(pre_match_prob, team1, team2, innings_num,
#                            c_runs, c_wickets, c_overs, proj_score,
#                            chase_target, v_avg):
#     """
#     Blends pre-match model output with live match state.
#     pre_match_prob = win chance for team1 (team that batted first in training).
#     """
#     total_overs = game_config["total_overs"]
#     inplay_prob = pre_match_prob

#     if innings_num == 1:
#         # 1st innings: adjust based on projected total vs venue average
#         if v_avg > 0:
#             pace_factor = (proj_score - v_avg) / v_avg
#             inplay_prob = pre_match_prob + np.clip(pace_factor * 0.12, -0.12, 0.12)

#     else:
#         # 2nd innings: team2 is chasing (team1 batted first)
#         overs_left = max(total_overs - c_overs, 0.1)
#         runs_needed = max(chase_target - c_runs, 0)
#         required_rr = runs_needed / overs_left
#         current_rr = c_runs / c_overs if c_overs > 0 else 0

#         if runs_needed == 0:
#             chase_team_prob = 0.98   # chasing team (team2) almost won
#         else:
#             rr_edge = (current_rr - required_rr) / max(required_rr, 1)
#             chase_team_prob = 1 / (1 + np.exp(-3 * rr_edge))

#         wicket_pressure = c_wickets / game_config["max_wickets"]
#         chase_team_prob *= (1 - wicket_pressure * 0.25)

#         # team2 is chasing → team1 win prob is the inverse
#         inplay_prob = 1 - chase_team_prob

#     # 35% pre-match + 65% live situation
#     final_team1_prob = np.clip(0.35 * pre_match_prob + 0.65 * inplay_prob, 0.02, 0.98)
#     return final_team1_prob, 1 - final_team1_prob

def adjust_win_probability(pre_match_prob, team1, team2, innings_num,
                           c_runs, c_wickets, c_overs, proj_score,
                           chase_target, v_avg):
    """
    Blends pre-match model output with live match state.
    pre_match_prob = win chance for team1 (team that batted first).
    In innings 2, current score is ALWAYS the chasing team (team2).
    """
    total_overs = game_config["total_overs"]
    max_wickets = game_config["max_wickets"]

    if innings_num == 1:
        if v_avg > 0:
            pace_factor = (proj_score - v_avg) / v_avg
            inplay_prob = pre_match_prob + np.clip(pace_factor * 0.12, -0.12, 0.12)
        else:
            inplay_prob = pre_match_prob
        final_team1_prob = np.clip(0.35 * pre_match_prob + 0.65 * inplay_prob, 0.02, 0.98)
        return final_team1_prob, 1 - final_team1_prob

    # ── Innings 2: team2 is chasing ──
    runs_needed = chase_target - c_runs
    overs_left = max(total_overs - c_overs, 0.1)
    innings_over = c_overs >= total_overs or c_wickets >= max_wickets

    # Definitive outcomes — no blending
    if runs_needed <= 0:
        # Chasing team (team2) reached target → they win
        return 0.02, 0.98

    if innings_over:
        # Innings finished, target not reached → defending team (team1) wins
        return 0.98, 0.02

    # Chase still in progress
    required_rr = runs_needed / overs_left
    current_rr = c_runs / c_overs if c_overs > 0 else 0
    rr_edge = (current_rr - required_rr) / max(required_rr, 1)
    chase_team_prob = 1 / (1 + np.exp(-3 * rr_edge))

    wicket_pressure = c_wickets / max_wickets
    chase_team_prob *= (1 - wicket_pressure * 0.25)
    chase_team_prob = np.clip(chase_team_prob, 0.02, 0.98)

    inplay_prob = 1 - chase_team_prob  # team1 perspective
    final_team1_prob = np.clip(0.35 * pre_match_prob + 0.65 * inplay_prob, 0.02, 0.98)
    return final_team1_prob, 1 - final_team1_prob

# =========================================================================
# 🔄 LIVE DATA FETCHING ENGINE (ETL SCRAPER MOCK / LIVE SWITCHER)
# =========================================================================
_weather_lookup = WeatherPitchLookup()

_FALLBACK_MATCH = {
    "status": "API Stream Offline - Fallback Engaged",
    "team1": "Gujarat Titans",
    "team2": "Rajasthan Royals",
    "venue": "Narendra Modi Stadium",
    "current_runs": 84,
    "wickets_lost": 2,
    "overs_bowled": 9.3,
    "temperature": 32.0,
    "humidity": 50.0,
    "index_differential": 2.1,
    "innings_num": 1,     
    "chase_target": 0,
}

@st.cache_data(ttl=3600, show_spinner=False)  # series ID barely changes; cache for an hour
def get_ipl_series_id():
    """
    Looks up the seriesId for the current/most recent IPL season via CricketData.org's
    /series search endpoint, so we can scope all live-match calls to IPL specifically.
    Only ever returns a series whose name genuinely matches IPL — never falls back to
    an unrelated series just because it was first in the results (the /series search
    endpoint isn't reliably strict, so we double-check client-side).
    """
    try:
        response = requests.get(
            f"{CRICKETDATA_BASE_URL}/series",
            params={"apikey": CRICKETDATA_API_KEY, "offset": 0, "search": "IPL"},
            timeout=6
        )
        response.raise_for_status()
        payload = response.json()
        series_list = payload.get("data", [])

        # Only keep series that genuinely look like IPL, e.g. "IPL 2026" or
        # "Indian Premier League 2026" — reject anything else even if the API returned it
        ipl_candidates = [
            s for s in series_list
            if "indian premier league" in s.get("name", "").lower()
            or s.get("name", "").lower().strip().startswith("ipl")
        ]
        if not ipl_candidates:
            return None

        # Prefer the season matching the current year; otherwise take the most recent one
        current_year = str(datetime.now().year)
        for s in ipl_candidates:
            if current_year in s.get("name", ""):
                return s["id"]
        return ipl_candidates[0]["id"]

    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=60, show_spinner=False)
def fetch_live_match_feed():
    """
    Fetches live scorecard data scoped to the IPL series only, via CricketData.org
    (free tier: 100 requests/day). Cached for 60s per session to protect the daily quota.
    Falls back to simulated data if no key is set, IPL isn't in season, or the request fails.
    """
    if not CRICKETDATA_API_KEY:
        fallback = dict(_FALLBACK_MATCH)
        fallback["status"] = "No API Key Set - Fallback Engaged"
        return fallback

    series_id = get_ipl_series_id()
    if not series_id:
        fallback = dict(_FALLBACK_MATCH)
        fallback["status"] = "IPL Series Not Found - Fallback Engaged"
        return fallback

    try:
        response = requests.get(
            f"{CRICKETDATA_BASE_URL}/series_info",
            params={"apikey": CRICKETDATA_API_KEY, "id": series_id},
            timeout=6
        )
        response.raise_for_status()
        payload = response.json()

        match_list = payload.get("data", {}).get("matchList", [])
        live_matches = [
            m for m in match_list
            if m.get("matchStarted") and not m.get("matchEnded")
        ]

        if not live_matches:
            fallback = dict(_FALLBACK_MATCH)
            fallback["status"] = "No Live IPL Match Right Now - Fallback Engaged"
            return fallback

        match = live_matches[0]
        teams = match.get("teams", ["Team A", "Team B"])
        scores = match.get("score", [])
        current_innings = scores[-1] if scores else {"r": 0, "w": 0, "o": 0.0}
        venue = match.get("venue", "Unknown Venue")

        match_date = match.get("date", datetime.now().strftime("%Y-%m-%d"))
        temperature, humidity = _weather_lookup.get_weather(venue, match_date)

        # return {
        #     "status": "Live Match Active",
        #     "team1": teams[0] if len(teams) > 0 else "Team A",
        #     "team2": teams[1] if len(teams) > 1 else "Team B",
        #     "venue": venue,
        #     "current_runs": int(current_innings.get("r", 0)),
        #     "wickets_lost": int(current_innings.get("w", 0)),
        #     "overs_bowled": float(current_innings.get("o", 0.0)),
        #     "temperature": temperature,
        #     "humidity": humidity,
        #     # CricketData's free tier doesn't expose roster strength, so this stays
        #     # a neutral default until you plug in your own roster-index calculation.
        #     "index_differential": 0.0
        # }

        teams = match.get("teams", ["Team A", "Team B"])
        team1 = teams[0] if len(teams) > 0 else "Team A"
        team2 = teams[1] if len(teams) > 1 else "Team B"

        scores = match.get("score", [])
        current_innings = scores[-1] if scores else {"r": 0, "w": 0, "o": 0.0}
        innings_num = len(scores) if scores else 1

        chase_target = 0
        if innings_num >= 2:
            chase_target = int(scores[0].get("r", 0)) + 1

        venue = match.get("venue", "Unknown Venue")
        match_date = match.get("date", datetime.now().strftime("%Y-%m-%d"))
        temperature, humidity = _weather_lookup.get_weather(venue, match_date)

        # Auto roster strength from your historical data
        idx_diff = calculate_index_differential(team1, team2, reference_date=match_date)

        return {
            "status": "Live Match Active",
            "team1": team1,
            "team2": team2,
            "venue": venue,
            "current_runs": int(current_innings.get("r", 0)),
            "wickets_lost": int(current_innings.get("w", 0)),
            "overs_bowled": float(current_innings.get("o", 0.0)),
            "temperature": temperature,
            "humidity": humidity,
            "index_differential": idx_diff,
            "innings_num": innings_num,
            "chase_target": chase_target,
        }

    except requests.exceptions.RequestException as e:
        fallback = dict(_FALLBACK_MATCH)
        fallback["status"] = f"API Stream Offline - Fallback Engaged ({type(e).__name__})"
        return fallback

# =========================================================================
# 📊 UI DASHBOARD ASSEMBLY
# =========================================================================
st.title("🏏 Predickter: Sports Forecasting Engine")
st.markdown("---")

# Sidebar - Mode Selection and Metadata Inputs
st.sidebar.header("🕹️ Control Room")
mode = st.sidebar.radio("Data Engine Mode", ["Manual Sandbox Mode", "Live Active Match Feed"])

if mode == "Live Active Match Feed":

    live_data = fetch_live_match_feed()

    if live_data["status"] == "Live Match Active":
        st.sidebar.success(f"🔴 {live_data['status']}")
    elif live_data["status"] == "No API Key Set - Fallback Engaged":
        st.sidebar.warning("⚠️ No CRICKETDATA_API_KEY set — showing sample data. See app.py header for setup steps.")
    else:
        st.sidebar.warning(f"⚠️ {live_data['status']}")
    
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

    #added lines
    innings_num = live_data.get("innings_num", 1)
    chase_target = live_data.get("chase_target", 0)

else:
    # Sandbox user inputs for off-season fantasy guessing
    # st.sidebar.info("💡 Off-Season Sandbox Mode enabled. Configure parameters manually.")
    # venue_list = venue_df['venue'].tolist() if not venue_df.empty else ["M Chinnaswamy Stadium"]
    # selected_venue = st.sidebar.selectbox("Select Match Venue", venue_list)
    
    # team1 = st.sidebar.text_input("Team 1 (Batting First)", "Chennai Super Kings")
    # team2 = st.sidebar.text_input("Team 2 (Bowling First)", "Kolkata Knight Riders")
    
    # temp = st.sidebar.slider("Temperature (°C)", 15.0, 45.0, 28.0)
    # humidity = st.sidebar.slider("Humidity (%)", 10.0, 100.0, 60.0)
    # idx_diff = st.sidebar.slider("Roster Index Differential", -25.0, 25.0, 4.2)
    
    # st.sidebar.markdown("---")
    # st.sidebar.subheader("Live Match Progression State")
    # c_runs = st.sidebar.number_input("Current Runs Scored", min_value=0, max_value=300, value=95)
    # c_wickets = st.sidebar.number_input("Wickets Fallen", min_value=0, max_value=10, value=3)
    # c_overs = st.sidebar.slider("Overs Bowled", 0.0, 20.0, 11.0)

    #added team name list instead of manually entering
    st.sidebar.info("💡 Off-Season Sandbox Mode enabled. Configure parameters manually.")
    venue_list = venue_df['venue'].tolist() if not venue_df.empty else ["M Chinnaswamy Stadium"]
    selected_venue = st.sidebar.selectbox("Select Match Venue", venue_list)

    ipl_teams = get_all_ipl_teams() or ["Chennai Super Kings", "Kolkata Knight Riders"]
    team1 = st.sidebar.selectbox("Team 1 (Batting First)", ipl_teams, index=0)
    team2 = st.sidebar.selectbox("Team 2 (Bowling First)", ipl_teams, index=min(1, len(ipl_teams) - 1))

    temp = st.sidebar.slider("Temperature (°C)", 15.0, 45.0, 28.0)
    humidity = st.sidebar.slider("Humidity (%)", 10.0, 100.0, 60.0)

    # Auto-calculated from historical player form
    idx_diff = calculate_index_differential(team1, team2)
    st.sidebar.metric("Roster Index Differential (auto)", f"{idx_diff:+.2f}")
    idx_diff = st.sidebar.slider("Override Roster Differential", -25.0, 25.0, float(idx_diff))

    # st.sidebar.markdown("---")
    # st.sidebar.subheader("Live Match Progression State")
    # c_runs = st.sidebar.number_input("Current Runs Scored", min_value=0, max_value=300, value=95)
    # c_wickets = st.sidebar.number_input("Wickets Fallen", min_value=0, max_value=10, value=3)
    # c_overs = st.sidebar.slider("Overs Bowled", 0.0, 20.0, 11.0)
    # innings_num = st.sidebar.radio("Innings", [1, 2], index=0)
    # chase_target = st.sidebar.number_input("Chase Target (innings 2 only)", min_value=0, max_value=300, value=180)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Live Match Progression State")
    innings_num = st.sidebar.radio("Innings", [1, 2], index=0)

    if innings_num == 1:
        st.sidebar.caption(f"Innings 1: **{team1}** is batting")
        c_runs = st.sidebar.number_input("Current Runs Scored", min_value=0, max_value=300, value=95)
        c_wickets = st.sidebar.number_input("Wickets Fallen", min_value=0, max_value=10, value=3)
        c_overs = st.sidebar.slider("Overs Bowled", 0.0, 20.0, 11.0)
        chase_target = 0

    else:
        st.sidebar.caption(f"Innings 2: **{team2}** is chasing (Team 1 batted first)")
        chase_target = st.sidebar.number_input("Chase Target", min_value=1, max_value=300, value=180)
        c_runs = st.sidebar.number_input(f"{team2} — Current Runs", min_value=0, max_value=300, value=95)
        c_wickets = st.sidebar.number_input(f"{team2} — Wickets Fallen", min_value=0, max_value=10, value=3)
        c_overs = st.sidebar.slider(f"{team2} — Overs Bowled", 0.0, 20.0, 11.0)

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
# 1. Build feature vector
input_features = np.array([[temp, humidity, v_avg, v_vol, v_den, idx_diff]])
scaled_features = scaler.transform(input_features)
pre_match_prob = clf_model.predict_proba(scaled_features)[0][1]

# 2. Tier 2: State-Space Live Target Projection (run BEFORE win blend)
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

# 3. Tier 1: Blend pre-match win % with live match state
win_probability, team2_win_prob = adjust_win_probability(
    pre_match_prob=pre_match_prob,
    team1=team1,
    team2=team2,
    innings_num=innings_num,
    c_runs=c_runs,
    c_wickets=c_wickets,
    c_overs=c_overs,
    proj_score=proj_score,
    chase_target=chase_target,
    v_avg=v_avg,
)

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
    st.markdown(f"📉 **{team2} Win Probability:** `{team2_win_prob * 100:.2f}%`")
    st.caption(f"Pre-match model: {pre_match_prob * 100:.1f}% → Blended with live state (Innings {innings_num})")

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