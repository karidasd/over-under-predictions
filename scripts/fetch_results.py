import os
import json
import time
import requests
from datetime import datetime

API_KEY = os.environ.get('API_FOOTBALL_KEY')
BASE_URL = "https://v3.football.api-sports.io"

def fetch_api(endpoint, params):
    if not API_KEY:
        return []
    headers = {'x-apisports-key': API_KEY}
    response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('response', [])
    return []

def fetch_result(fixture_id):
    results = fetch_api("fixtures", {"id": fixture_id})
    if results and len(results) > 0:
        return results[0]
    return None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'docs', 'data')

    preds_file = os.path.join(data_dir, 'predictions.json')
    history_file = os.path.join(data_dir, 'history.json')

    if not os.path.exists(preds_file):
        print("No predictions file found, skipping evaluation.")
        return

    with open(preds_file, 'r') as f:
        data = json.load(f)

    updated_matches = []
    for match in data.get('matches', []):
        if match.get('status') == 'Pending':
            fix_id = match.get('fixture_id')
            print(f"Fetching result for {match['home_team']} vs {match['away_team']} (ID: {fix_id})...")
            result = fetch_result(fix_id)
            time.sleep(0.3)

            if result:
                status_short = result.get('fixture', {}).get('status', {}).get('short', '')
                if status_short in ['FT', 'AET', 'PEN']:
                    home_goals = result['goals']['home']
                    away_goals = result['goals']['away']

                    if home_goals is not None and away_goals is not None:
                        total_goals = home_goals + away_goals
                        short_tip = match.get('short_tip', '')

                        if short_tip == 'OVER 2.5':
                            correct = total_goals > 2
                        elif short_tip == 'UNDER 2.5':
                            correct = total_goals < 3
                        else:
                            correct = False

                        match['status'] = 'Finished'
                        match['home_goals'] = home_goals
                        match['away_goals'] = away_goals
                        match['correct_ou'] = correct
                        match['correct_1x2'] = correct  # UI uses correct_1x2 for ✅/❌

                        result_str = "Correct" if correct else "Wrong"
                        print(f"  Result: {home_goals}-{away_goals} | {result_str}")

        updated_matches.append(match)

    data['matches'] = updated_matches

    with open(preds_file, 'w') as f:
        json.dump(data, f, indent=4)

    # Update history
    history = {"total_1x2": 0, "correct_1x2": 0, "history_log": []}
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            try:
                history = json.load(f)
            except:
                pass

    existing_ids = [m.get('fixture_id') for m in history.get('history_log', [])]

    for match in updated_matches:
        if match.get('status') == 'Finished' and match.get('fixture_id') not in existing_ids:
            history['total_1x2'] += 1
            if match.get('correct_ou'):
                history['correct_1x2'] += 1
            history.setdefault('history_log', []).append(match)

    # Keep last 100 only
    history['history_log'] = history['history_log'][-100:]

    with open(history_file, 'w') as f:
        json.dump(history, f, indent=4)

    total = history['total_1x2']
    correct = history['correct_1x2']
    rate = round((correct / total) * 100, 1) if total > 0 else 0
    print(f"\nCumulative Win Rate: {rate}% ({correct}/{total})")

if __name__ == "__main__":
    main()
