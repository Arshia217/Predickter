import os
import pandas as pd
import numpy as np

def generate_venue_profiles(matches, deliveries, output_dir):
    """
    Pillar 1: Systematically vectorizes venues based on historical data footprints
    to handle unseen grounds gracefully.
    """
    print(" Building dynamic venue structural vectors...")
    venue_profiles_path = os.path.join(output_dir, "venue_profiles.csv")
    
    # Extract structural baseline signatures from past data
    striker_col = 'batsman'
    runs_col = 'total_runs'
    
    venue_stats = []
    global_avg_runs = matches['innings1_runs'].mean() if not matches.empty else 165.0
    
    for venue, group in matches.groupby('venue'):
        avg_score = group['innings1_runs'].mean()
        total_matches = len(group)
        
        # Calculate scoring volatility (Standard Deviation)
        score_std = group['innings1_runs'].std() if total_matches > 2 else 15.0
        
        # Calculate dynamic pacing (approximate ball-by-ball boundary density for the ground)
        m_ids = group['match_id'].unique()
        v_deliveries = deliveries[deliveries['match_id'].isin(m_ids)]
        
        if not v_deliveries.empty:
            boundary_balls = len(v_deliveries[v_deliveries[runs_col].isin([4, 6])])
            boundary_density = boundary_balls / len(v_deliveries)
        else:
            boundary_density = 0.08  # Global baseline density
            
        venue_stats.append({
            'venue': venue,
            'v_vector_avg_runs': round(avg_score, 2),
            'v_vector_volatility': round(score_std, 2),
            'v_vector_boundary_density': round(boundary_density, 4)
        })
        
    venue_df = pd.DataFrame(venue_stats)
    venue_df.to_csv(venue_profiles_path, index=False)
    print(f"💾 Venue profile vectors saved to {venue_profiles_path}")
    return venue_df, global_avg_runs

def compile_modeling_matrix():
    print("🚀 Starting Phase 2: Adaptive Chronological Feature Engineering...")
    
    processed_dir = os.path.join("data", "processed")
    matches_path = os.path.join(processed_dir, "matches.csv")
    deliveries_path = os.path.join(processed_dir, "deliveries.csv")
    output_path = os.path.join(processed_dir, "modeling_matrix.csv")
    
    if not os.path.exists(matches_path) or not os.path.exists(deliveries_path):
        raise FileNotFoundError("❌ Phase 1 data missing! Run run_pipeline.py first.")
        
    matches = pd.read_csv(matches_path)
    deliveries = pd.read_csv(deliveries_path)
    
    matches['date'] = pd.to_datetime(matches['date'])
    matches = matches.sort_values(by='date').reset_index(drop=True)
    
    # Auto-generate or load venue profile vectors
    venue_df, global_baseline_score = generate_venue_profiles(matches, deliveries, processed_dir)
    venue_vectors = venue_df.set_index('venue').to_dict(orient='index')
    
    striker_col = 'batsman'
    runs_col = 'total_runs'
    
    print("🔗 Mapping temporal timelines to delivery logs...")
    date_mapping = matches.set_index('match_id')['date']
    deliveries['date'] = deliveries['match_id'].map(date_mapping)
    deliveries['date'] = pd.to_datetime(deliveries['date'])
    
    matrix_rows = []
    
    # 3. Iterative Timeline Processing Loop with Time Decay
    for idx, current_match in matches.iterrows():
        match_id = current_match['match_id']
        match_date = current_match['date']
        venue = current_match['venue']
        
        # Zero Data Leakage Isolation Boundary
        past_deliveries = deliveries[deliveries['date'] < match_date]
        
        # --- PILLAR 1: Venue Vector Resolution ---
        # If ground is completely brand new, it cleanly falls back on regional global baselines
        v_meta = venue_vectors.get(venue, {
            'v_vector_avg_runs': global_baseline_score,
            'v_vector_volatility': 18.0,
            'v_vector_boundary_density': 0.085
        })
        
        # --- PILLAR 4: Player Form Calculation via Recency Time-Decay ---
        def calculate_decayed_roster_index(player_string, past_data, current_date):
            clean_str = str(player_string).replace('[', '').replace(']', '').replace("'", "").replace('"', '')
            players = [p.strip() for p in clean_str.split(',') if p.strip()]
            
            player_strike_rates = []
            
            for player in players:
                player_stats = past_data[past_data[striker_col] == player]
                
                if not player_stats.empty:
                    # Calculate delta time weights in days relative to match day
                    days_ago = (current_date - player_stats['date']).dt.days
                    
                    # 📉 Exponential Decay Formula: weights = e^(-lambda * t)
                    # lambda = 0.002 implies performance 365 days ago loses ~50% weight priority
                    lambda_decay = 0.002 
                    weights = np.exp(-lambda_decay * days_ago)
                    
                    raw_sr = (player_stats[runs_col] / 1) * 100 # Individual ball strike evaluation
                    decayed_sr = np.sum(raw_sr * weights) / np.sum(weights)
                    
                    # Bound outliers safely between safe cricketing floors/ceilings
                    decayed_sr = np.clip(decayed_sr, 80.0, 180.0)
                    player_strike_rates.append(decayed_sr)
                else:
                    # Adaptive baseline fallback if player has zero match footprint
                    player_strike_rates.append(125.0)
                    
            return np.mean(player_strike_rates) if player_strike_rates else 125.0

        t1_index = calculate_decayed_roster_index(current_match['team1_players'], past_deliveries, match_date)
        t2_index = calculate_decayed_roster_index(current_match['team2_players'], past_deliveries, match_date)
        
        index_differential = t1_index - t2_index
        team1_won = 1 if current_match['winner'] == current_match['team1'] else 0
        
        matrix_rows.append({
            'match_id': match_id,
            'date': match_date,
            'venue': venue,
            'team1': current_match['team1'],
            'team2': current_match['team2'],
            'temperature': current_match.get('temperature', 28.0), 
            'humidity': current_match.get('humidity', 65.0),       
            'stadium_avg_runs': v_meta['v_vector_avg_runs'],
            'stadium_volatility': v_meta['v_vector_volatility'],
            'stadium_boundary_density': v_meta['v_vector_boundary_density'],
            'index_differential': round(index_differential, 4),
            'innings1_runs': current_match['innings1_runs'],
            'team1_won': team1_won
        })
        
        if (idx + 1) % 100 == 0 or (idx + 1) == len(matches):
            print(f"  Processed {idx + 1}/{len(matches)} matches...")

    modeling_matrix = pd.DataFrame(matrix_rows)
    if len(modeling_matrix) > 15:
        modeling_matrix = modeling_matrix.iloc[15:].reset_index(drop=True)
        
    modeling_matrix.to_csv(output_path, index=False)
    print(f" Phase 2 Complete! Master matrix compiled at: {output_path}")
    print(f"📊 Final Matrix Dimensions: {modeling_matrix.shape[0]} rows x {modeling_matrix.shape[1]} features")

if __name__ == "__main__":
    compile_modeling_matrix()