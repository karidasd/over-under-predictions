import math
from scipy.stats import poisson

def extract_league_stats(standings_data):
    """
    Parses the standings to calculate league averages and team-specific stats.
    Returns: league_avg_goals, team_stats_dict
    """
    total_goals = 0
    total_matches = 0
    team_stats = {}
    
    # standings_data['standings'][0]['table'] usually contains the total table
    try:
        table = standings_data['standings'][0]['table']
    except KeyError:
        return 0, {}
        
    for row in table:
        team_name = row['team']['name']
        played = row['playedGames']
        goals_for = row['goalsFor']
        goals_against = row['goalsAgainst']
        
        if played == 0:
            continue
            
        total_goals += goals_for
        total_matches += played
        
        team_stats[team_name] = {
            'avg_scored': goals_for / played,
            'avg_conceded': goals_against / played
        }
        
    # Total matches in standings counts each match twice (home/away)
    league_avg_goals_per_game = (total_goals / (total_matches / 2)) / 2 if total_matches > 0 else 1.5
    
    return league_avg_goals_per_game, team_stats

def calculate_expected_goals(home_team, away_team, league_avg, team_stats):
    """
    Calculates expected goals (xG) for Home and Away team using Poisson fundamentals.
    """
    if home_team not in team_stats or away_team not in team_stats:
        return 1.0, 1.0 # fallback
        
    # Home Team Attack Strength = (Home Avg Scored) / League Avg
    home_attack = team_stats[home_team]['avg_scored'] / league_avg
    # Away Team Defense Weakness = (Away Avg Conceded) / League Avg
    away_defense = team_stats[away_team]['avg_conceded'] / league_avg
    
    home_xg = home_attack * away_defense * league_avg
    
    # Away Team Attack Strength
    away_attack = team_stats[away_team]['avg_scored'] / league_avg
    # Home Team Defense Weakness
    home_defense = team_stats[home_team]['avg_conceded'] / league_avg
    
    away_xg = away_attack * home_defense * league_avg
    
    return home_xg, away_xg

def calculate_over_under_probabilities(home_xg, away_xg):
    """
    Uses the Poisson distribution to calculate the probability of total goals.
    Returns the probability of Over 2.5 and Under 2.5
    """
    prob_under_2_5 = 0.0
    
    # Calculate probabilities for 0, 1, 2 total goals
    for home_goals in range(3):
        for away_goals in range(3):
            if home_goals + away_goals < 3:
                # Probability of this exact scoreline
                p_home = poisson.pmf(home_goals, home_xg)
                p_away = poisson.pmf(away_goals, away_xg)
                prob_under_2_5 += p_home * p_away
                
    prob_over_2_5 = 1.0 - prob_under_2_5
    
    return prob_over_2_5, prob_under_2_5
