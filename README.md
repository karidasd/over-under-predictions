![Over/Under Predictions Banner](docs/assets/banner.png)

# ⚽ Over/Under Predictions — AI Football Engine

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Live-success?style=for-the-badge)
![Automation](https://img.shields.io/badge/Automated-GitHub%20Actions-blueviolet?style=for-the-badge)

**🌐 Live Dashboard → [karidasd.github.io/over-under-predictions](https://karidasd.github.io/over-under-predictions/)**

---

> **Stop guessing. Start calculating.**
> This engine wakes up every morning, scans the globe for football fixtures, runs every match through an AI prediction model, and publishes only the high-confidence Over/Under signals — automatically, every single day. No subscriptions. No paywalls. No bullshit.

---

## Why This Exists

Every sports betting tool either:
- Sells you "insider tips" for €29/month with zero accountability
- Uses fake backtests and cherry-picked results

This repo does the opposite. Every prediction is **logged before the match starts**. Every result is **graded automatically at midnight**. The win rate you see on the dashboard is **real and cumulative** — updated daily by GitHub Actions.

If it loses, it shows. If it wins, it shows. No hiding.

---

## ⚙️ How It Works

```
07:17 UTC — Morning Job                 23:22 UTC — Night Job
───────────────────────                 ──────────────────────
Scan all global fixtures          →     Fetch final scores
Get AI prediction per match       →     Grade each prediction
Filter by xG confidence           →     Update Win Rate
  • xG ≥ 2.7  →  OVER 2.5              Commit results to repo
  • xG ≤ 2.2  →  UNDER 2.5             Dashboard auto-updates
  • xG > 4.5  →  SKIP (amateur)
Publish to live dashboard
```

The model uses **[api-football.com](https://www.api-football.com/)**'s machine learning engine — the same data layer used by professional analytics firms — to calculate expected goals (xG) for every fixture. Only matches where the model has a strong directional signal are published.

---

## 📂 Project Structure

```
over-under-predictions/
├── scripts/
│   ├── fetch_predictions.py   # Morning: scans fixtures, generates signals
│   └── fetch_results.py       # Night: grades results, updates history
├── docs/                      # GitHub Pages live dashboard
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── data/
│       ├── predictions.json   # Auto-updated every morning
│       └── history.json       # Cumulative track record
├── .github/workflows/
│   ├── morning_predictions.yml
│   └── evening_results.yml
├── engine.py                  # Poisson distribution engine (manual use)
├── bot.py                     # CLI for manual predictions
└── requirements.txt
```

---

## 🚀 Run It Yourself

```bash
git clone https://github.com/karidasd/over-under-predictions.git
cd over-under-predictions
pip install -r requirements.txt
```

Get a free API key at [api-football.com](https://www.api-football.com/) (100 req/day, no credit card).
Rename `.env.example` → `.env` and paste your key.

```bash
# Predict today's matches
python bot.py predict --league PL

# Grade last week's predictions
python bot.py evaluate --league PL
```

Supported: `PL` · `PD` · `SA` · `BL1` · `FL1`

---

## 📈 Sample Output

```
Match                       xG          Signal       Confidence
──────────────────────────  ──────────  ───────────  ──────────
Arsenal vs Everton          2.45 / 0.81 OVER 2.5     68.2%
Crystal Palace vs Burnley   0.95 / 0.60 UNDER 2.5    74.1%

Evaluation
──────────────────────────  ───────────  Score  Result
Arsenal vs Everton          OVER 2.5     3-1    WON
Crystal Palace vs Burnley   UNDER 2.5    1-1    WON

Win Rate: 100.0% (2W - 0L)
```

---

> ⚠️ For educational and research purposes only. Not financial advice. Gamble responsibly.

*Built by DARKAIS Data Science.*
