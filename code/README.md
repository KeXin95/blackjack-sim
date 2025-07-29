# 🎰 Blackjack Simulation and Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-success.svg)]()

> **Advanced blackjack strategy simulation and analysis with interactive dashboard**

---

## 🚀 Live Dashboard

**Experience the interactive dashboard with all simulation results and analysis:**

### 🌐 [**View Live Dashboard**](https://blackjack-dashboard.vercel.app/)

The dashboard provides:
- 📊 **Interactive visualizations** of all blackjack strategies
- ⚡ **Real-time comparison** of different betting strategies  
- 📈 **Detailed analysis plots** and statistics
- 🎯 **User-friendly interface** to explore simulation results

---

## 📋 Table of Contents

- [🎯 Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📊 Simulation Results](#-simulation-results)
- [📁 File Structure](#-file-structure)
- [🔧 Usage](#-usage)

---

## 🎯 Features

- **Multiple Strategy Simulation**: Test various blackjack strategies
- **Statistical Analysis**: Comprehensive win/loss/push rate analysis
- **Interactive Visualizations**: Beautiful charts and graphs
- **Real-time Dashboard**: Live web interface for results exploration
- **Detailed Reporting**: Complete statistical breakdowns

---

## 🚀 Quick Start

### Prerequisites

```bash
# Ensure you have Python 3.8+ installed
python --version
```

### Installation

1. **Clone or download** the project files
2. **Navigate** to the project directory:
   ```bash
   cd submission/code
   ```

---

## 📊 Simulation Results

### 🎲 Strategy Performance Overview

| Strategy | Games | Profit | Win% | Loss% | Push% | Avg Bet | Max Bet |
|----------|-------|--------|------|-------|-------|---------|---------|
| **Mimic Dealer** | 1,000,000 | -$619,970 | 40.90% | 49.38% | 9.72% | $10.00 | $10.00 |
| **Dealer Weakness** | 1,000,000 | -$361,145 | 42.80% | 48.66% | 8.54% | $10.00 | $10.00 |
| **Basic Strategy** | 1,000,000 | -$102,350 | 42.97% | 47.85% | 9.18% | $10.00 | $10.00 |
| **Card Counter** | 1,000,000 | **+$112,295** | 43.08% | 47.89% | 9.03% | $18.01 | $100.00 |
| **Martingale** | 1,000,000 | **+$827,470** | 43.07% | 47.79% | 9.14% | $72.12 | $2,621,440 |

### 🎯 Fixed Threshold Strategy Results

| Threshold | Profit | Win% | Loss% | Push% |
|-----------|--------|------|-------|-------|
| 12 | -$788,425 | 41.79% | 51.93% | 6.28% |
| 13 | -$674,485 | 42.05% | 51.06% | 6.89% |
| 14 | -$579,615 | 42.21% | 50.27% | 7.52% |
| 15 | -$548,100 | 42.03% | 49.78% | 8.19% |
| 16 | -$540,655 | 41.70% | 49.38% | 8.93% |
| 17 | -$627,430 | 40.88% | 49.41% | 9.71% |
| 18 | -$963,670 | 39.86% | 51.74% | 8.40% |
| 19 | -$1,820,410 | 36.36% | 56.84% | 6.80% |
| 20 | -$3,347,795 | 29.60% | 65.35% | 5.05% |

---

## 📁 File Structure

```
submission/code/
├── 📄 README.md                    # This file
├── 🐍 blackjack_sim2.py           # Main simulation script
├── 📊 analyze_blackjack_results.py # Analysis and plotting script
├── 📁 results/                     # Generated JSON result files
│   ├── basic_results.json
│   ├── card_counter_results.json
│   ├── dealer_weakness_results.json
│   ├── martingale_results.json
│   ├── mimic_dealer_results.json
│   └── fixed_threshold_*.json
└── 📁 analysis_plots/             # Generated visualization plots
    ├── martingale_running_bankroll.png
    ├── player_edge_vs_fixed_threshold.png
    ├── profit_per_dollar_barplot.png
    ├── profit_per_dollar_boxplot.png
    ├── profit_per_dollar_distribution.png
    └── profit_per_dollar_violinplot.png
```

---

## 🔧 Usage

### 1️⃣ **Run the Blackjack Simulation**

Generate all result JSON files in the `results/` directory:

```bash
python blackjack_sim2.py
```

**Expected Output:**
```
🎰 --- Blackjack Strategy Simulation Results ---

Strategy                  Games       Profit     Win%    Loss%    Push%   AvgBet   MaxBet
Mimic Dealer          1,000,000 $ -619,970.00   40.90%   49.38%    9.72%    10.00    10.00
✅ Saved detailed results to results/mimic_dealer_results.json
Dealer Weakness       1,000,000 $ -361,145.00   42.80%   48.66%    8.54%    10.00    10.00
✅ Saved detailed results to results/dealer_weakness_results.json
Basic                 1,000,000 $ -102,350.00   42.97%   47.85%    9.18%    10.00    10.00
✅ Saved detailed results to results/basic_results.json
Card Counter          1,000,000 $  112,295.00   43.08%   47.89%    9.03%    18.01   100.00
✅ Saved detailed results to results/card_counter_results.json

🎯 Fixed Threshold Strategy (Threshold 12-20):
Threshold        Profit     Win%    Loss%    Push%
12         $ -788,425.00   41.79%   51.93%    6.28%
✅ Saved detailed results to results/fixed_threshold_12_results.json
13         $ -674,485.00   42.05%   51.06%    6.89%
✅ Saved detailed results to results/fixed_threshold_13_results.json
...
```

### 2️⃣ **Analyze Results and Generate Plots**

Create analysis plots used in the report:

```bash
python analyze_blackjack_results.py
```

**Generated Output:**
- 📊 **Analysis plots** saved in `analysis_plots/` directory
- 📄 **JSON result files** saved in `results/` directory

---

## 🎯 Key Findings

- **Card Counter Strategy**: Most profitable with +$112,295 profit
- **Martingale Betting**: Highest profit at +$827,470 but with extreme risk
- **Basic Strategy**: Best balance of risk/reward for casual players
- **Fixed Threshold 16**: Optimal threshold strategy with -$540,655 loss

---

## 📈 Analysis Plots

The analysis script generates several insightful visualizations:

- **Profit Distribution Analysis**: Understanding strategy performance variability
- **Player Edge Comparison**: Visual comparison of different strategies
- **Martingale Risk Analysis**: Examining the high-risk, high-reward nature
- **Threshold Strategy Analysis**: Finding optimal hit/stand thresholds

---

## 🤝 Contributing

This project was developed for ISYE 6739 Statistical Methods course. For questions or improvements, please refer to the course materials or contact the development team.

---

## 📄 License

This project is part of an academic course assignment. All rights reserved.

---

<div align="center">

**🎰 Happy Simulating! 🎰**

*Built with ❤️ for statistical analysis and blackjack strategy research*

</div> 