![Over/Under Predictions Banner](docs/assets/banner.png)

# 🤖 Over/Under Predictions (Poisson Engine)

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Live-success?style=for-the-badge)
![Automation](https://img.shields.io/badge/Automated-GitHub%20Actions-blueviolet?style=for-the-badge)

**🌐 Live UI Dashboard:** [View Today's Predictions](https://karidasd.github.io/over-under-predictions/)

---

## Overview

**Over/Under Predictions** is a fully automated, data-driven football betting engine. Every morning it fetches real fixtures from across the globe, runs each match through an AI prediction model (powered by [api-football.com](https://www.api-football.com/)), and publishes high-confidence **Over 2.5 / Under 2.5** signals directly to the live dashboard.

Every night, it evaluates the results of those predictions and updates the **Track Record** — a transparent, cumulative Win Rate visible to everyone on the dashboard.

No human intervention. No fake data. Pure statistics.

---

## ⚙️ How It Works

```
Every Morning (07:17 UTC)            Every Night (23:22 UTC)
────────────────────────             ──────────────────────
1. Fetch today's fixtures            1. Read today's predictions
   (all leagues, globally)           2. Fetch final scores from API
2. Get AI prediction per match       3. Mark each as Correct / Wrong
3. Filter by xG confidence           4. Update Win Rate (history.json)
4. Publish to docs/data/             5. Publish results to dashboard
   predictions.json
```

### The Prediction Logic

For each match, the API returns a predicted goal count for home and away teams:

- If **total xG ≥ 2.7** → signal: `OVER 2.5`
- If **total xG ≤ 2.2** → signal: `UNDER 2.5`
- If **total xG > 4.5** → match is skipped (amateur league, unreliable data)
- Matches with no strong signal are skipped

This ensures only **high-conviction** calls appear on the dashboard.

---

## 📂 Project Structure

```
over-under-predictions/
├── scripts/
│   ├── fetch_predictions.py   # Morning: fetches fixtures & generates predictions
│   └── fetch_results.py       # Night: evaluates results & updates history
├── docs/                      # GitHub Pages site
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── data/
│       ├── predictions.json   # Today's predictions (auto-updated)
│       └── history.json       # Cumulative track record (auto-updated)
├── .github/workflows/
│   ├── morning_predictions.yml  # Runs at 07:17 UTC daily
│   └── evening_results.yml      # Runs at 23:22 UTC daily
├── engine.py                  # Poisson distribution engine (manual use)
├── api_client.py              # football-data.org client (manual use)
├── bot.py                     # CLI tool for manual predictions
├── .env.example               # API key template
└── requirements.txt
```

---

## 🚀 Run Locally

### 1. Get a Free API Key

Register at [api-football.com](https://www.api-football.com/) for a free account (100 requests/day).

### 2. Install & Configure

```bash
git clone https://github.com/karidasd/over-under-predictions.git
cd over-under-predictions
pip install -r requirements.txt
```

Rename `.env.example` to `.env` and add your key:
```
FOOTBALL_DATA_API_KEY=your_key_here
```

### 3. Run

```bash
# Generate predictions for today
python bot.py predict --league PL

# Evaluate last weekend's results
python bot.py evaluate --league PL
```

*Supported leagues: `PL` (Premier League), `PD` (La Liga), `SA` (Serie A), `BL1` (Bundesliga), `FL1` (Ligue 1).*

---

## 📈 Example Output

**Prediction Phase (Terminal):**
```
Match                         | xG (Home-Away) | Prediction  | Confidence
------------------------------|----------------|-------------|----------
Arsenal vs Everton            | 2.45 - 0.81    | OVER 2.5    | 68.2%
Crystal Palace vs Burnley     | 0.95 - 0.60    | UNDER 2.5   | 74.1%
```

**Evaluation Phase (Terminal):**
```
Match                         | Prediction  | Actual Score | Result
------------------------------|-------------|--------------|--------
Arsenal vs Everton            | OVER 2.5    | 3-1          | WON
Crystal Palace vs Burnley     | UNDER 2.5   | 1-1          | WON

Win Rate: 100.0% (2W - 0L)
```

---

> ⚠️ Predictions are based on statistical models and historical data. Not financial advice. Gamble responsibly.

*Built by DARKAIS Data Science.*
