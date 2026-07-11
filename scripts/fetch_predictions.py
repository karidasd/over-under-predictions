import os
import json
import time
import shutil
import requests
from datetime import datetime, timedelta

API_KEY = os.environ.get('API_FOOTBALL_KEY')
BASE_URL = "https://v3.football.api-sports.io"

# Top leagues to scan for over/under fixtures
LEAGUES = [39, 140, 135, 78, 61]  # PL, La Liga, Serie A, Bundesliga, Ligue 1

def fetch_api(endpoint, params):
    if not API_KEY:
        raise ValueError("API_FOOTBALL_KEY environment variable is not set.")
    headers = {'x-apisports-key': API_KEY}
    response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('response', [])
    return []

def get_fixtures_for_date(date_str):
    """Fetch all fixtures for a given date across our target leagues."""
    all_fixtures = []
    for league_id in LEAGUES:
        fixtures = fetch_api("fixtures", {"league": league_id, "date": date_str, "season": 2024})
        all_fixtures.extend(fixtures)
        time.sleep(0.2)
    return all_fixtures

def get_prediction(fixture_id):
    """Fetch API-Football's ML prediction for a fixture."""
    preds = fetch_api("predictions", {"fixture": fixture_id})
    if preds and len(preds) > 0:
        return preds[0]
    return None

def get_odds(fixture_id):
    """Fetch Over/Under 2.5 odds for a fixture."""
    odds_resp = fetch_api("odds", {"fixture": fixture_id, "bet": 5})  # bet id 5 = Goals Over/Under
    if odds_resp and len(odds_resp) > 0:
        bookmakers = odds_resp[0].get('bookmakers', [])
        if not bookmakers:
            return None
        for bookmaker in bookmakers:
            for bet in bookmaker.get('bets', []):
                if 'Over/Under' in bet.get('name', ''):
                    vals = bet.get('values', [])
                    over = next((v['odd'] for v in vals if '2.5' in str(v['value']) and 'Over' in str(v['value'])), 'N/A')
                    under = next((v['odd'] for v in vals if '2.5' in str(v['value']) and 'Under' in str(v['value'])), 'N/A')
                    return {"over": over, "under": under}
    return None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'docs', 'data')
    os.makedirs(data_dir, exist_ok=True)

    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')

    print(f"Fetching fixtures for {date_str}...")
    fixtures = get_fixtures_for_date(date_str)
    print(f"Found {len(fixtures)} fixtures total.")

    predictions = []
    api_calls = 0

    for f in fixtures:
        # Hard limit to protect API quota (100 calls/day on free tier)
        if api_calls >= 14:
            print("API call limit reached, stopping.")
            break

        fix_id = f['fixture']['id']
        status_short = f['fixture']['status']['short']

        # Only process scheduled fixtures
        if status_short != 'NS':
            continue

        print(f"  -> Getting prediction for fixture {fix_id}...")
        pred_data = get_prediction(fix_id)
        api_calls += 1
        time.sleep(0.2)

        if not pred_data:
            continue

        pred_goals = pred_data.get('predictions', {}).get('goals', {})
        home_g_pred = pred_goals.get('home')
        away_g_pred = pred_goals.get('away')

        try:
            home_g = float(str(home_g_pred).replace('-', '0')) if home_g_pred else 0.0
            away_g = float(str(away_g_pred).replace('-', '0')) if away_g_pred else 0.0
            total_xg = home_g + away_g
        except (ValueError, TypeError):
            total_xg = 0.0

        # Determine Over/Under signal
        if total_xg >= 2.7:
            short_tip = "OVER 2.5"
            confidence = min(int((total_xg - 2.5) * 25 + 55), 85)
            advice = f"AI expects {total_xg:.1f} total goals — leaning OVER 2.5"
        elif total_xg <= 2.2:
            short_tip = "UNDER 2.5"
            confidence = min(int((2.5 - total_xg) * 25 + 55), 85)
            advice = f"AI expects only {total_xg:.1f} total goals — leaning UNDER 2.5"
        else:
            # No high-confidence signal — skip
            continue

        # Fetch Over/Under odds
        odds_data = get_odds(fix_id)
        api_calls += 1
        time.sleep(0.2)

        win_percent = pred_data.get('predictions', {}).get('percent', {})

        predictions.append({
            "fixture_id": fix_id,
            "date": f['fixture']['date'],
            "league": f['league']['name'],
            "home_team": f['teams']['home']['name'],
            "home_logo": f['teams']['home']['logo'],
            "away_team": f['teams']['away']['name'],
            "away_logo": f['teams']['away']['logo'],
            "short_tip": short_tip,
            "confidence": f"{confidence}%",
            "total_xg": round(total_xg, 2),
            "percent_home": win_percent.get('home', 'N/A'),
            "percent_draw": win_percent.get('draw', 'N/A'),
            "percent_away": win_percent.get('away', 'N/A'),
            "advice": advice,
            "odds": odds_data if odds_data else {"over": "N/A", "under": "N/A"},
            "status": "Pending",
            "home_goals": None,
            "away_goals": None,
            "correct_ou": None
        })

    output = {"date": date_str, "matches": predictions}

    output_path = os.path.join(data_dir, 'predictions.json')
    with open(output_path, 'w') as f_out:
        json.dump(output, f_out, indent=4)

    print(f"Saved {len(predictions)} Over/Under predictions to {output_path}")

if __name__ == "__main__":
    main()
