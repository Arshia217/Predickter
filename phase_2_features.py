import os
import pandas as pd
import numpy as np

def compile_modeling_matrix():
    print("🚀 Starting Phase 2: Chronological Feature Engineering...")
    
    # 1. Define Paths
    processed_dir = os.path.join("data", "processed")
    matches_path = os.path.join(processed_dir, "matches.csv")
    deliveries_path = os.path.join(processed_dir, "deliveries.csv")
    output_path = os.path.join(processed_dir, "modeling_matrix.csv")
    
    if not os.path.exists(matches_path) or not os.path.exists(deliveries_path):
        raise FileNotFoundError("❌ Phase 1 data missing! Run run_pipeline.py first.")
        
    # 2. Load Data
    matches = pd.read_csv(matches_path)
    deliveries = pd.read_csv(deliveries_path)
    
    # Clean and parse match dates
    matches['date'] = pd.to_datetime(matches['date'])
    matches = matches.sort_values(by='date').reset_index(drop=True)
    
    # --- EXACT SCHEMA COUPLING ---
    # Hard-mapped to your specified columns: 'batsman' and 'total_runs'
    striker_col = 'batsman'
    runs_col = 'total_runs'
    
    print(f"🎯 Parsing delivery logs using verified keys: ['{striker_col}', '{runs_col}']")
    
    # Map match dates onto deliveries using match_id
    print("🔗 Mapping match timelines to delivery logs...")
    date_mapping = matches.set_index('match_id')['date']
    deliveries['date'] = deliveries['match_id'].map(date_mapping)
    deliveries['date'] = pd.to_datetime(deliveries['date'])
    
    matrix_rows = []
    
    # 3. Iterative Timeline Processing Loop
    for idx, current_match in matches.iterrows():
        match_id = current_match['match_id']
        match_date = current_match['date']
        venue = current_match['venue']
        
        # Isolate historical data strictly BEFORE the current match date (Zero Data Leakage)
        past_matches = matches[matches['date'] < match_date]
        past_deliveries = deliveries[deliveries['date'] < match_date]
        
        # --- FEATURE A: Historic Ground Baseline (G_v) ---
        venue_matches = past_matches[past_matches['venue'] == venue]
        if len(venue_matches) >= 3:
            stadium_avg_runs = venue_matches['innings1_runs'].mean()
        else:
            stadium_avg_runs = 160.0  
            
        # --- FEATURE B: Player-Environment Roster Indices (E_pe) ---
        def calculate_roster_index(player_string, past_data):
            # Strip brackets, quotes, and whitespace from the player string list
            clean_str = str(player_string).replace('[', '').replace(']', '').replace("'", "").replace('"', '')
            players = [p.strip() for p in clean_str.split(',') if p.strip()]
            
            player_strike_rates = []
            
            for player in players:
                player_stats = past_data[past_data[striker_col] == player]
                if not player_stats.empty:
                    runs = player_stats[runs_col].sum()
                    balls = len(player_stats)
                    # Traditional T20 Strike Rate formulation per player
                    sr = (runs / balls * 100) if balls > 10 else 120.0
                    player_strike_rates.append(sr)
                else:
                    # Default base index for a player with no historical data yet
                    player_strike_rates.append(120.0)
                    
            # Return average of individual strike rates to generate team performance variance
            return np.mean(player_strike_rates) if player_strike_rates else 120.0

        t1_index = calculate_roster_index(current_match['team1_players'], past_deliveries)
        t2_index = calculate_roster_index(current_match['team2_players'], past_deliveries)
        
        # --- COVARIATE C: Index Differential ---
        index_differential = t1_index - t2_index
        
        # --- TARGET MAPPING & CLIMATE COVARIATES ---
        team1_won = 1 if current_match['winner'] == current_match['team1'] else 0
        
        matrix_rows.append({
            'match_id': match_id,
            'date': match_date,
            'venue': venue,
            'team1': current_match['team1'],
            'team2': current_match['team2'],
            'temperature': current_match.get('temperature', 28.0), 
            'humidity': current_match.get('humidity', 65.0),       
            'stadium_avg_runs': round(stadium_avg_runs, 2),
            'team1_roster_index': round(t1_index, 2),
            'team2_roster_index': round(t2_index, 2),
            'index_differential': round(index_differential, 2),
            'innings1_runs': current_match['innings1_runs'],
            'team1_won': team1_won
        })
        
        if (idx + 1) % 100 == 0 or (idx + 1) == len(matches):
            print(f"  Processed {idx + 1}/{len(matches)} matches...")

    # 4. Convert to DataFrame & Truncate Initial Data Volatility
    modeling_matrix = pd.DataFrame(matrix_rows)
    if len(modeling_matrix) > 15:
        modeling_matrix = modeling_matrix.iloc[15:].reset_index(drop=True)
        
    # 5. Export finalized matrix to disk
    modeling_matrix.to_csv(output_path, index=False)
    print(f"✅ Phase 2 Complete! Master matrix compiled at: {output_path}")
    print(f"📊 Final Matrix Dimensions: {modeling_matrix.shape[0]} rows x {modeling_matrix.shape[1]} features")

if __name__ == "__main__":
    compile_modeling_matrix()