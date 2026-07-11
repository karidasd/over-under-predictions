# 🤖 AI Football Predictions (Poisson Engine)

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Profitable-success?style=for-the-badge)

Welcome to the **AI Football Predictions** repository. This is an open-source, mathematical betting engine that uses the **Poisson Distribution** to predict `OVER 2.5` and `UNDER 2.5` goals for the top European Football Leagues.

Forget about "gut feelings". This bot relies purely on empirical data, attack strengths, and defensive weaknesses to find high-probability **Value Bets**.

## ✨ Features
1. **The Mathematical Engine:** Uses the Poisson distribution to calculate the exact Expected Goals (xG) and probability distribution for upcoming matches.
2. **Predict Mode:** Scans the weekend's upcoming fixtures and identifies matches with a high probability (>60%) of going Over or Under 2.5 Goals.
3. **Evaluate Mode:** The ultimate transparency tool. After the matches are played, the bot fetches the actual results and grades its own predictions. It outputs the exact **Win Rate** and ROI metrics.

## 🚀 Quick Start

### 1. Get a Free API Key
This script runs entirely on **[football-data.org](https://www.football-data.org/)**. 
Go to their website, register for a free account, and get your API Key.

### 2. Installation
```bash
git clone https://github.com/karidasd/ai-football-predictions.git
cd ai-football-predictions
pip install -r requirements.txt
```

Rename the `.env.example` file to `.env` and paste your API key inside:
```text
FOOTBALL_DATA_API_KEY=your_actual_key_here
```

### 3. Usage

**Step A: Predict the Weekend (Run on Friday)**
```bash
python bot.py predict --league PL
```
*Supported Leagues: `PL` (Premier League), `PD` (La Liga), `SA` (Serie A), `BL1` (Bundesliga), `FL1` (Ligue 1).*

This command will output a color-coded table in your terminal and generate a `LATEST_PREDICTIONS.md` file with the betting signals. It also saves state in `predictions.json`.

**Step B: Evaluate the Results (Run on Monday)**
```bash
python bot.py evaluate --league PL
```
The bot will check the final scores of the matches it predicted, update the json file, and show you your Win Rate!

---

## 📈 Example Output

**Prediction Phase:**
```text
Match                       | xG (Home - Away) | Prediction | Confidence
----------------------------|------------------|------------|-----------
Arsenal vs Everton          | 2.45 - 0.81      | OVER 2.5   | 68.2%
Man City vs Aston Villa     | 3.10 - 1.05      | OVER 2.5   | 81.4%
Crystal Palace vs Burnley   | 0.95 - 0.60      | UNDER 2.5  | 74.1%
```

**Evaluation Phase:**
```text
Match                       | Prediction | Actual Score | Result
----------------------------|------------|--------------|-------
Arsenal vs Everton          | OVER 2.5   | 3-1          | WON ✅
Man City vs Aston Villa     | OVER 2.5   | 4-0          | WON ✅
Crystal Palace vs Burnley   | UNDER 2.5  | 1-1          | WON ✅

Win Rate: 100.0% (3W - 0L)
```

*(Note: Past performance is not indicative of future results. Always gamble responsibly.)*

---
*Built by DARKAIS Data Science.*
