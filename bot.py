import os
import sys
import json
import argparse
from datetime import datetime
from rich.console import Console
from rich.table import Table

import api_client
import engine

console = Console()
PREDICTIONS_FILE = "predictions.json"
DOCS_DATA_DIR = os.path.join("docs", "data")
DOCS_PREDICTIONS_FILE = os.path.join(DOCS_DATA_DIR, "predictions.json")
DOCS_HISTORY_FILE = os.path.join(DOCS_DATA_DIR, "history.json")

def ensure_docs_dir():
    if not os.path.exists(DOCS_DATA_DIR):
        os.makedirs(DOCS_DATA_DIR)

def predict(league_code, threshold=0.60):
    ensure_docs_dir()
    console.print(f"[cyan]Fetching standings for {league_code}...[/cyan]")
    try:
        standings = api_client.get_standings(league_code)
        league_name = standings.get('competition', {}).get('name', league_code)
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        console.print("[yellow]Please make sure you have added your API Key in the .env file.[/yellow]")
        return
        
    league_avg, team_stats = engine.extract_league_stats(standings)
    
    console.print(f"[cyan]Fetching upcoming fixtures for {league_code}...[/cyan]")
    upcoming = api_client.get_upcoming_matches(league_code)
    matches = upcoming.get('matches', [])
    
    if not matches:
        console.print("[yellow]No scheduled matches found.[/yellow]")
        return
        
    predictions_data = {}
    
    # Load existing to append
    if os.path.exists(PREDICTIONS_FILE):
        with open(PREDICTIONS_FILE, 'r') as f:
            predictions_data = json.load(f)
            
    # Docs JSON format for web UI
    docs_data = {
        "date": datetime.now().isoformat(),
        "matches": []
    }
            
    table = Table(title=f"Weekend Predictions ({league_name})", show_header=True, header_style="bold magenta")
    table.add_column("Match", style="cyan")
    table.add_column("xG (Home - Away)", justify="center")
    table.add_column("Prediction", justify="center", style="bold red")
    table.add_column("Confidence", justify="right", style="green")
    
    md_report = f"# 🔥 Over/Under Predictions\n*Generated on: {datetime.now().strftime('%Y-%m-%d')}*\n\n"
    md_report += "| Match | Expected Goals (xG) | Prediction | Confidence |\n"
    md_report += "|---|---|---|---|\n"
    
    for match in matches:
        match_id = str(match['id'])
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        home_logo = match['homeTeam'].get('crest', '')
        away_logo = match['awayTeam'].get('crest', '')
        
        home_xg, away_xg = engine.calculate_expected_goals(home_team, away_team, league_avg, team_stats)
        prob_over, prob_under = engine.calculate_over_under_probabilities(home_xg, away_xg)
        
        if prob_over >= threshold:
            pred = "OVER 2.5"
            conf = prob_over
            advice = f"Strong indicator for goals. Total xG: {home_xg+away_xg:.2f}"
        elif prob_under >= threshold:
            pred = "UNDER 2.5"
            conf = prob_under
            advice = f"Defensive matchup expected. Total xG: {home_xg+away_xg:.2f}"
        else:
            continue # skip matches without high confidence
            
        predictions_data[match_id] = {
            'home': home_team,
            'away': away_team,
            'prediction': pred,
            'confidence': conf,
            'status': 'PENDING'
        }
        
        # Format for UI
        docs_data['matches'].append({
            "id": match_id,
            "status": "Pending",
            "league": league_name,
            "home_team": home_team,
            "home_logo": home_logo,
            "away_team": away_team,
            "away_logo": away_logo,
            "percent_home": f"{prob_over*100:.0f}%", 
            "percent_draw": "N/A", 
            "percent_away": f"{prob_under*100:.0f}%",
            "short_tip": pred,
            "advice": advice,
            "odds": {"home": "N/A", "draw": "N/A", "away": "N/A"}
        })
        
        match_str = f"{home_team} vs {away_team}"
        xg_str = f"{home_xg:.2f} - {away_xg:.2f}"
        conf_str = f"{conf*100:.1f}%"
        
        table.add_row(match_str, xg_str, pred, conf_str)
        md_report += f"| {match_str} | {xg_str} | **{pred}** | {conf_str} |\n"
        
    with open(PREDICTIONS_FILE, 'w') as f:
        json.dump(predictions_data, f, indent=4)
        
    with open(DOCS_PREDICTIONS_FILE, 'w') as f:
        json.dump(docs_data, f, indent=4)
        
    with open("LATEST_PREDICTIONS.md", "w", encoding='utf-8') as f:
        f.write(md_report)
        
    console.print(table)
    console.print("[green]Predictions saved for backend and frontend UI![/green]")

def evaluate(league_code):
    ensure_docs_dir()
    if not os.path.exists(PREDICTIONS_FILE):
        console.print("[red]No predictions found. Run `predict` first.[/red]")
        return
        
    with open(PREDICTIONS_FILE, 'r') as f:
        predictions_data = json.load(f)
        
    console.print(f"[cyan]Fetching finished matches for {league_code} to evaluate...[/cyan]")
    try:
        finished = api_client.get_finished_matches(league_code)
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        return
        
    matches = finished.get('matches', [])
    
    wins = 0
    losses = 0
    
    # Load frontend JSON to update it too
    docs_data = {"date": datetime.now().isoformat(), "matches": []}
    if os.path.exists(DOCS_PREDICTIONS_FILE):
        with open(DOCS_PREDICTIONS_FILE, 'r') as f:
            docs_data = json.load(f)
            
    table = Table(title=f"Evaluation Results", show_header=True, header_style="bold magenta")
    table.add_column("Match", style="cyan")
    table.add_column("Prediction", justify="center")
    table.add_column("Actual Score", justify="center")
    table.add_column("Result", justify="right", style="bold")
    
    for match in matches:
        match_id = str(match['id'])
        if match_id in predictions_data and predictions_data[match_id]['status'] == 'PENDING':
            score = match['score']['fullTime']
            if score['home'] is None or score['away'] is None:
                continue
                
            total_goals = score['home'] + score['away']
            pred = predictions_data[match_id]['prediction']
            
            won = False
            if pred == "OVER 2.5" and total_goals > 2:
                won = True
            elif pred == "UNDER 2.5" and total_goals < 3:
                won = True
                
            predictions_data[match_id]['status'] = 'WON' if won else 'LOST'
            predictions_data[match_id]['actual_score'] = f"{score['home']}-{score['away']}"
            
            # Update frontend JSON data
            for m in docs_data['matches']:
                if m['id'] == match_id:
                    m['status'] = 'Finished'
                    m['correct_1x2'] = won  # The UI uses correct_1x2 flag for ✅ / ❌
                    m['home_goals'] = score['home']
                    m['away_goals'] = score['away']
            
            if won:
                wins += 1
                result_str = "[green]WON ✅[/green]"
            else:
                losses += 1
                result_str = "[red]LOST ❌[/red]"
                
            match_str = f"{predictions_data[match_id]['home']} vs {predictions_data[match_id]['away']}"
            table.add_row(match_str, pred, predictions_data[match_id]['actual_score'], result_str)
            
    with open(PREDICTIONS_FILE, 'w') as f:
        json.dump(predictions_data, f, indent=4)
        
    with open(DOCS_PREDICTIONS_FILE, 'w') as f:
        json.dump(docs_data, f, indent=4)
        
    # Update History file for the UI
    total_evaluated = wins + losses
    history_data = {
        "correct_1x2": wins,
        "total_1x2": total_evaluated
    }
    
    # Check if history exists to accumulate
    if os.path.exists(DOCS_HISTORY_FILE):
        try:
            with open(DOCS_HISTORY_FILE, 'r') as f:
                old_hist = json.load(f)
                history_data['correct_1x2'] += old_hist.get('correct_1x2', 0)
                history_data['total_1x2'] += old_hist.get('total_1x2', 0)
        except:
            pass
            
    with open(DOCS_HISTORY_FILE, 'w') as f:
        json.dump(history_data, f, indent=4)
        
    console.print(table)
    
    if total_evaluated > 0:
        win_rate = (wins / total_evaluated) * 100
        console.print(f"\\n[bold]Win Rate:[/bold] [yellow]{win_rate:.1f}%[/yellow] ({wins}W - {losses}L)")
    else:
        console.print("[yellow]No pending matches have finished yet.[/yellow]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Football Predictions Engine")
    parser.add_argument("mode", choices=["predict", "evaluate"], help="Run mode")
    parser.add_argument("--league", default="PL", help="League Code (PL, PD, SA, BL1, FL1)")
    
    args = parser.parse_args()
    
    if args.mode == "predict":
        predict(args.league)
    else:
        evaluate(args.league)
