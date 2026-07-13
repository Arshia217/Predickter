#adding this file so that the live mode doesn't have a manual roster index slider and uses players and other match data to predict

import os
import pandas as pd
import numpy as np
from datetime import datetime

DELIVERIES_PATH = os.path.join("data", "processed", "deliveries.csv")
MATCHES_PATH = os.path.join("data", "processed", "matches.csv")

LAMBDA_DECAY = 0.002
BASELINE_SR = 125.0


def _player_decayed_strike_rate(player, past_deliveries, reference_date):
    player_stats = past_deliveries[past_deliveries["batsman"] == player]
    if player_stats.empty:
        return BASELINE_SR

    days_ago = (reference_date - player_stats["date"]).dt.days
    weights = np.exp(-LAMBDA_DECAY * days_ago)
    raw_sr = player_stats["total_runs"] * 100
    decayed_sr = np.sum(raw_sr * weights) / np.sum(weights)
    return float(np.clip(decayed_sr, 80.0, 180.0))


def _roster_index_from_players(players_str, past_deliveries, reference_date):
    clean = str(players_str).replace("[", "").replace("]", "").replace("'", "").replace('"', "")
    players = [p.strip() for p in clean.split(",") if p.strip()]
    if not players:
        return BASELINE_SR

    strike_rates = [
        _player_decayed_strike_rate(p, past_deliveries, reference_date)
        for p in players
    ]
    return float(np.mean(strike_rates))


def get_latest_roster_string(team_name, matches_df, reference_date):
    """Most recent playing XI we have for this team."""
    team_matches = matches_df[
        (matches_df["date"] < reference_date)
        & ((matches_df["team1"] == team_name) | (matches_df["team2"] == team_name))
    ].sort_values("date")

    if team_matches.empty:
        return ""

    latest = team_matches.iloc[-1]
    return latest["team1_players"] if latest["team1"] == team_name else latest["team2_players"]


def calculate_index_differential(team1, team2, reference_date=None):
    """
    Returns team1_index - team2_index using only data BEFORE reference_date.
    """
    if not os.path.exists(DELIVERIES_PATH) or not os.path.exists(MATCHES_PATH):
        return 0.0

    reference_date = pd.to_datetime(reference_date or datetime.now())
    matches = pd.read_csv(MATCHES_PATH)
    deliveries = pd.read_csv(DELIVERIES_PATH)

    matches["date"] = pd.to_datetime(matches["date"])
    date_map = matches.set_index("match_id")["date"]
    deliveries["date"] = deliveries["match_id"].map(date_map)
    deliveries["date"] = pd.to_datetime(deliveries["date"])

    past_deliveries = deliveries[deliveries["date"] < reference_date]

    t1_roster = get_latest_roster_string(team1, matches, reference_date)
    t2_roster = get_latest_roster_string(team2, matches, reference_date)

    t1_index = _roster_index_from_players(t1_roster, past_deliveries, reference_date)
    t2_index = _roster_index_from_players(t2_roster, past_deliveries, reference_date)

    return round(t1_index - t2_index, 2)


def get_all_ipl_teams():
    """Unique team names from historical matches."""
    if not os.path.exists(MATCHES_PATH):
        return []
    matches = pd.read_csv(MATCHES_PATH)
    teams = pd.concat([matches["team1"], matches["team2"]]).dropna().unique()
    return sorted(teams.tolist())