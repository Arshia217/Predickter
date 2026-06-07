import os
import glob
import pandas as pd
from scripts.weather import WeatherPitchLookup

def parse_ipl_csv_files(raw_dir="data/raw", processed_dir="data/processed", use_weather_api=True):
    print("Initializing Weather & Pitch Lookup Service...")
    weather_lookup = WeatherPitchLookup(cache_dir=processed_dir)
    
    # Grab all CSV files in your raw folder
    all_files = glob.glob(os.path.join(raw_dir, "**", "*.csv"), recursive=True)
    
    # Filter: Separate metadata info files from core delivery files
    info_files = [f for f in all_files if "_info.csv" in f]
    ball_files = [f for f in all_files if "_info.csv" not in f and "README" not in f]
    
    print(f"Found {len(info_files)} metadata info files and {len(ball_files)} ball-by-ball files.")
    
    # 1. PARSE METADATA INFO FILES NATIVELY
    matches_list = []
    for filepath in info_files:
        match_id = os.path.basename(filepath).replace("_info.csv", "").strip()
        metadata = {
            "match_id": match_id, "season": None, "date": None, "venue": None, "city": None,
            "team1": None, "team2": None, "toss_winner": None, "toss_decision": None, "winner": None,
            "outcome": None, "innings1_runs": 0, "innings2_runs": 0, "team1_players": "", "team2_players": ""
        }
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    row = line.strip().split(",")
                    if len(row) < 3 or row[0] != "info": continue
                    key, val = row[1], row[2].strip('"')
                    if key == "season": metadata["season"] = val
                    elif key == "date": metadata["date"] = val
                    elif key == "venue": metadata["venue"] = val
                    elif key == "city": metadata["city"] = val
                    elif key == "toss_winner": metadata["toss_winner"] = val
                    elif key == "toss_decision": metadata["toss_decision"] = val
                    elif key == "winner": metadata["winner"] = val
                    elif key == "outcome": metadata["outcome"] = val
                    elif key == "team":
                        if not metadata["team1"]: metadata["team1"] = val
                        else: metadata["team2"] = val
            matches_list.append(metadata)
        except Exception as e:
            print(f"Error reading info file {match_id}: {e}")

    matches_df = pd.DataFrame(matches_list)

    # 2. PARSE BALL DELIVERIES USING PANDAS
    print("Processing tabular data using Pandas engine...")
    deliveries_container = []
    
    for idx, filepath in enumerate(ball_files):
        match_id = os.path.basename(filepath).replace(".csv", "").strip()
        try:
            # Load the file natively with pandas since it has clean headers
            df = pd.read_csv(filepath)
            
            # Fill missing data fields cleanly to protect math operations
            df['wides'] = df['wides'].fillna(0)
            df['noballs'] = df['noballs'].fillna(0)
            df['byes'] = df['byes'].fillna(0)
            df['legbyes'] = df['legbyes'].fillna(0)
            df['penalty'] = df['penalty'].fillna(0)
            
            # Calculate total runs per delivery matching your exact columns
            df["total_runs"] = df["runs_off_bat"] + df["extras"]
            
            # Keep only what we need for feature metrics
            # Renamed 'batsman' -> 'striker' to match your actual column names!
            clean_df = df[["match_id", "innings", "ball", "batting_team", "striker", "bowler", "total_runs"]].copy()
            clean_df = clean_df.rename(columns={"ball": "over_ball", "striker": "batsman"})
            
            deliveries_container.append(clean_df)
            
            # Accumulate match totals directly via fast pandas grouping
            match_mask = matches_df["match_id"] == match_id
            if match_mask.any():
                matches_df.loc[match_mask, "innings1_runs"] = df[df["innings"] == 1]["total_runs"].sum()
                matches_df.loc[match_mask, "innings2_runs"] = df[df["innings"] == 2]["total_runs"].sum()
                
                # Dynamically compile playing rosters
                t1 = matches_df.loc[match_mask, "team1"].values[0]
                t2 = matches_df.loc[match_mask, "team2"].values[0]
                
                t1_players = df[df["batting_team"] == t1]["striker"].unique()
                t2_players = df[df["batting_team"] == t2]["striker"].unique()
                
                matches_df.loc[match_mask, "team1_players"] = ",".join(t1_players)
                matches_df.loc[match_mask, "team2_players"] = ",".join(t2_players)

        except Exception as e:
            # Skip any corrupt formatting variants safely
            continue
            
        if (idx + 1) % 300 == 0 or (idx + 1) == len(ball_files):
            print(f"Loaded {idx + 1}/{len(ball_files)} ball-by-ball files...")

    # 3. WEATHER PROFILES INTEGRATION
    print("Finalizing weather profiles...")
    final_matches = []
    for _, row in matches_df.iterrows():
        m_dict = row.to_dict()
        if m_dict["date"]:
            temp, humidity = weather_lookup.get_weather(venue=m_dict["venue"], date_str=str(m_dict["date"]), use_api=use_weather_api)
            m_dict["temperature"], m_dict["humidity"] = temp, humidity
        else:
            m_dict["temperature"], m_dict["humidity"] = 30.0, 50.0
        m_dict["pitch_type"] = weather_lookup.get_pitch_type(m_dict["venue"])
        final_matches.append(m_dict)

    # Save outputs
    weather_lookup.save_cache()
    os.makedirs(processed_dir, exist_ok=True)
    
    output_matches_df = pd.DataFrame(final_matches)
    output_matches_df.to_csv(os.path.join(processed_dir, "matches.csv"), index=False)
    
    if deliveries_container:
        final_deliveries_df = pd.concat(deliveries_container, ignore_index=True)
    else:
        final_deliveries_df = pd.DataFrame(columns=["match_id", "innings", "over_ball", "batting_team", "batsman", "bowler", "total_runs"])
        
    final_deliveries_df.to_csv(os.path.join(processed_dir, "deliveries.csv"), index=False)
    
    print(f"\n✅ Pipeline Complete! Saved {len(output_matches_df)} matches and {len(final_deliveries_df)} individual deliveries.")
    return output_matches_df, final_deliveries_df