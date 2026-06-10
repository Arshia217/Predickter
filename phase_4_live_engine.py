import json
import os
import numpy as np
import pandas as pd

class PredickterLiveEngine:
    def __init__(self):
        # Load externalized game rules
        with open("game_rules.json", "r") as f:
            self.config = json.load(f)
            
        self.total_overs = self.config["total_overs"]
        self.max_wickets = self.config["max_wickets"]
        
    def calculate_live_projection(self, current_runs, wickets_lost, overs_bowled, venue_avg, index_differential):
        """
        Pillar 3 & 4: Event-driven state projection calculation
        """
        if wickets_lost >= self.max_wickets or overs_bowled >= self.total_overs:
            return {
                "projected_final_score": current_runs,
                "lower_bound_95": current_runs,
                "upper_bound_95": current_runs,
                "current_run_rate": round(current_runs / overs_bowled, 2) if overs_bowled > 0 else 0
            }
            
        # 1. Calculate current run rate (CRR)
        crr = current_runs / overs_bowled if overs_bowled > 0 else (venue_avg / self.total_overs)
        
        # 2. Determine base baseline expectation for the ground per over
        base_ground_per_over = venue_avg / self.total_overs
        
        # 3. Calculate Wicket Resource Penalty (Non-linear decay)
        # As wickets drop, the scoring speed drops because batsmen defend more
        wicket_percent_lost = wickets_lost / self.max_wickets
        wicket_penalty_factor = np.cos(wicket_percent_lost * (np.pi / 2)) # Drops from 1.0 to 0.0 smoothly
        
        # 4. Phase-Specific Momentum Shifters (Powerplay vs Death Overs)
        overs_remaining = self.total_overs - overs_bowled
        if overs_bowled <= self.config["powerplay_overs"]:
            phase_modifier = 1.10  # Powerplay acceleration field restrictions
        elif overs_remaining <= 4:
            phase_modifier = self.config["base_historical_death_acceleration"] # Death overs hitting
        else:
            phase_modifier = 0.95  # Middle overs consolidation
            
        # 5. Integrate Roster Momentum
        # Positive index differential pushes the base scoring rate up
        roster_modifier = 1 + (index_differential / 1000)
        
        # 6. Compute Dynamic Expected Run Rate (ERR) for remaining overs
        # Blends historical venue performance, active match state execution, and roster talent
        expected_run_rate = (
            (0.4 * crr) + 
            (0.6 * base_ground_per_over)
        ) * wicket_penalty_factor * phase_modifier * roster_modifier
        
        # 7. State Projection
        projected_remaining_runs = expected_run_rate * overs_remaining
        final_projected_score = int(current_runs + projected_remaining_runs)
        
        # Dynamic error variance collapses as overs_remaining approaches 0
        variance_scalar = np.sqrt(overs_remaining) * 6.5
        
        return {
            "current_match_state": f"{current_runs}/{wickets_lost} after {overs_bowled} overs",
            "current_run_rate": round(crr, 2),
            "dynamic_expected_run_rate": round(expected_run_rate, 2),
            "projected_final_score": final_projected_score,
            "lower_bound_95": int(final_projected_score - variance_scalar),
            "upper_bound_95": int(final_projected_score + variance_scalar)
        }

# Simulated Live Execution Test Trace
if __name__ == "__main__":
    engine = PredickterLiveEngine()
    
    print("📈 TESTING LIVE TIER-2 STATE-SPACE SIMULATION:")
    print("-" * 50)
    
    # Context Scenario: Match is at an explosive ground (Avg 182), Team 1 has strong roster (+4.5)
    venue_baseline = 182.0
    roster_diff = 4.5
    
    # Live Mid-Game State Snapshots to Evaluate
    live_states = [
        {"runs": 52, "wickets": 0, "overs": 6.0},   # Great powerplay start
        {"runs": 112, "wickets": 3, "overs": 14.0}, # Middle overs choke
        {"runs": 112, "wickets": 6, "overs": 14.0}, # Disaster alternative scenario: 6 wickets down
        {"runs": 165, "wickets": 4, "overs": 18.0}  # Going into the death phase
    ]
    
    for state in live_states:
        projection = engine.calculate_live_projection(
            current_runs=state["runs"],
            wickets_lost=state["wickets"],
            overs_bowled=state["overs"],
            venue_avg=venue_baseline,
            index_differential=roster_diff
        )
        print(f"📍 State: {projection['current_match_state']}")
        print(f"   -> CRR: {projection['current_run_rate']} | Dynamic ERR: {projection['dynamic_expected_run_rate']}")
        print(f"   🎯 Projected Score Range: {projection['projected_final_score']} runs (95% CI: {projection['lower_bound_95']} - {projection['upper_bound_95']})")
        print("-" * 50)