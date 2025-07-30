import os
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import glob

RESULTS_DIR = "results"
RESULT_FILES = [
    "basic_results.json",
    "card_counter_results.json",
    "dealer_weakness_results.json",
    "mimic_dealer_results.json",
    "martingale_results.json",
    # Fixed threshold files will be added automatically
]

OUTPUT_TEXT = "analysis_output.txt"
PLOTS_DIR = "analysis_plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

def load_results(filename):
    with open(os.path.join(RESULTS_DIR, filename), "r") as f:
        data = json.load(f)
    return data

# def analyze_strategy(results, name):
#     print(name)
#     profits = np.array([r['profit'] for r in results])
#     # import pdb; pdb.set_trace()
#     bets = np.array([r['bet'] for r in results])
#     profit_per_dollar = profits / bets
#     mean_edge = profit_per_dollar.mean()
#     std_edge = profit_per_dollar.std(ddof=1)
#     n = len(profit_per_dollar)
#     se = std_edge / np.sqrt(n)
#     ci_low, ci_high = mean_edge - 1.96*se, mean_edge + 1.96*se
#     t_stat, p_value = stats.ttest_1samp(profit_per_dollar, 0)
#     return {
#         "name": name,
#         "mean_edge": mean_edge,
#         "std_edge": std_edge,
#         "ci_low": ci_low,
#         "ci_high": ci_high,
#         "p_value": p_value,
#         "n": n,
#         "profits": profits,
#         "profit_per_dollar": profit_per_dollar,
#         "bets": bets,
#     }
def analyze_strategy(results, name):
    """
    Analyzes the results of a blackjack strategy simulation, combining all calculated metrics.
    """
    print(name)
    
    # --- Initial Data Extraction ---
    profits = np.array([r['profit'] for r in results])
    bets = np.array([r.get('bet',) for r in results])
    
    # --- Per-Hand Statistical Analysis ---
    # Filter out any hands with a zero bet to prevent errors
    valid_bets_mask = bets > 0
    profit_per_dollar = profits[valid_bets_mask] / bets[valid_bets_mask]
    
    # Unweighted average and standard deviation of per-hand returns
    mean_edge = profit_per_dollar.mean()
    std_edge = profit_per_dollar.std(ddof=1)
    
    n = len(profit_per_dollar)
    se = std_edge / np.sqrt(n)
    ci_low, ci_high = mean_edge - 1.96 * se, mean_edge + 1.96 * se
    t_stat, p_value = stats.ttest_1samp(profit_per_dollar, 0)
    
    # --- Aggregate / Overall Analysis ---
    total_profit = profits.sum()
    total_wagered = bets.sum()
    
    # Standard player edge calculation (Total Profit / Total Wagered)
    if total_wagered > 0:
        overall_player_edge = total_profit / total_wagered
    else:
        overall_player_edge = 0

    # --- Return All Calculated Stats ---
    return {
        # Aggregate stats
        "name": name,
        "overall_player_edge": overall_player_edge,
        "total_profit": total_profit,
        "total_wagered": total_wagered,
        
        # Per-hand stats
        "mean_edge": mean_edge,
        "std_edge": std_edge,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": p_value,
        "n": n,
        
        # Raw data arrays
        "profits": profits,
        "bets": bets,
        "profit_per_dollar": profit_per_dollar,
    }

def get_fixed_threshold_files():
    pattern = os.path.join(RESULTS_DIR, "fixed_threshold_*_results.json")
    return sorted(glob.glob(pattern))

def probability_of_ruin(profits, initial_bankroll=10000):
    running = np.cumsum(profits) + initial_bankroll
    ruined = np.any(running <= 0)
    return ruined, running

def max_drawdown(running):
    peak = np.maximum.accumulate(running)
    drawdown = peak - running
    max_dd = np.max(drawdown)
    return max_dd

def main():
    all_stats = []
    output_lines = []
    output_lines.append(f"Files in RESULTS_DIR: {os.listdir(RESULTS_DIR)}\n")
    # Add fixed threshold files dynamically
    fixed_files = get_fixed_threshold_files()
    # Compose the full list of files to analyze
    all_files = RESULT_FILES + [os.path.basename(f) for f in fixed_files]
    for fname in all_files:
        full_path = os.path.join(RESULTS_DIR, fname)
        if not os.path.exists(full_path):
            output_lines.append(f"File {fname} not found, skipping.\n")
            continue
        name = fname.replace("_results.json", "").replace("_", " ").title()
        results = load_results(fname)
        stats_dict = analyze_strategy(results, name)
        all_stats.append(stats_dict)
        # Print summary
        output_lines.append(f"{name}:\n")
        output_lines.append(f"  Mean Edge: {100*stats_dict['overall_player_edge']:.2f}%\n")
        output_lines.append(f"  95% CI: [{100*stats_dict['ci_low']:.2f}%, {100*stats_dict['ci_high']:.2f}%]\n")
        output_lines.append(f"  p-value (edge ≠ 0): {stats_dict['p_value']:.4g}\n")
        output_lines.append(f"  Std Dev: {100*stats_dict['std_edge']:.2f}%\n")
        output_lines.append(f"  N: {stats_dict['n']:,}\n\n")

    if not all_stats:
        output_lines.append("No data loaded. Please check your RESULTS_DIR and file names.\n")
        with open(OUTPUT_TEXT, 'w') as f:
            f.writelines(output_lines)
        return

    # --- Fixed Threshold Analysis ---
    fixed_stats = [s for s in all_stats if s['name'].startswith('Fixed Threshold')]
    if fixed_stats:
        thresholds = [int(s['name'].split()[2]) for s in fixed_stats]
        edges = [s['overall_player_edge'] for s in fixed_stats]
        ci_lows = [s['ci_low'] for s in fixed_stats]
        ci_highs = [s['ci_high'] for s in fixed_stats]
        # Plot
        plt.figure(figsize=(8,5))
        plt.errorbar(thresholds, [100*e for e in edges], 
                     yerr=[100*(hi-lo)/2 for lo, hi in zip(ci_lows, ci_highs)],
                     fmt='o-', capsize=5)
        plt.xlabel("Fixed Threshold")
        plt.ylabel("Player Edge (%)")
        plt.title("Player Edge vs. Fixed Threshold")
        plt.grid(True)
        plt.savefig(os.path.join(PLOTS_DIR, "player_edge_vs_fixed_threshold.png"))
        plt.close()
        # Print summary table
        output_lines.append("Threshold | Player Edge (%) | 95% CI\n")
        for t, e, lo, hi in zip(thresholds, edges, ci_lows, ci_highs):
            output_lines.append(f"{t:9d} | {100*e:14.2f} | [{100*lo:.2f}, {100*hi:.2f}]\n")
        output_lines.append("\n")

    # --- Martingale Risk Analysis ---
    martingale_stats = next((s for s in all_stats if "Martingale" in s['name']), None)
    if martingale_stats:
        ruined, running = probability_of_ruin(martingale_stats['profits'], initial_bankroll=10000)
        output_lines.append(f"\nMartingale: Probability of Ruin (bankroll $10,000): {'Yes' if ruined else 'No'}\n")
        max_dd = max_drawdown(running)
        output_lines.append(f"Martingale: Maximum Drawdown: ${max_dd:,.2f}\n")
        plt.figure(figsize=(10,5))
        plt.plot(running)
        plt.axhline(0, color='red', linestyle='--')
        plt.title("Martingale: Running Bankroll ($10,000 start)")
        plt.xlabel("Hand Number")
        plt.ylabel("Bankroll")
        plt.savefig(os.path.join(PLOTS_DIR, "martingale_running_bankroll.png"))
        plt.close()

    # --- Distribution Plots for All Strategies ---
    plt.figure(figsize=(10,6))
    # Only include 'Fixed Threshold 15' among fixed threshold strategies
    filtered_stats = []
    for s in all_stats:
        if s['name'].startswith('Fixed Threshold'):
            if s['name'] == 'Fixed Threshold 15':
                filtered_stats.append(s)
        else:
            filtered_stats.append(s)
    for s in filtered_stats:
        plt.hist(s['profit_per_dollar'], bins=100, alpha=0.5, label=s['name'], density=True)
    plt.xlabel("Profit per Dollar Bet")
    plt.ylabel("Density")
    plt.title("Distribution of Profit per Dollar Bet")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "profit_per_dollar_distribution.png"))
    plt.close()

    # Boxplot for visual comparison
    plt.figure(figsize=(10,6))
    plt.boxplot([s['profit_per_dollar'] for s in all_stats], tick_labels=[s['name'] for s in all_stats])
    plt.ylabel("Profit per Dollar Bet")
    plt.title("Boxplot: Profit per Dollar Bet by Strategy")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "profit_per_dollar_boxplot.png"))
    plt.close()

    # --- Violin Plot for Distribution ---
    import seaborn as sns
    plt.figure(figsize=(12, 6))
    data = []
    labels = []
    for s in all_stats:
        data.extend(s['profit_per_dollar'])
        labels.extend([s['name']] * len(s['profit_per_dollar']))
    df = pd.DataFrame({'Strategy': labels, 'Profit per Dollar Bet': data})
    sns.violinplot(x='Strategy', y='Profit per Dollar Bet', data=df, cut=0)
    plt.xticks(rotation=45, ha='right')
    plt.title("Violin Plot: Profit per Dollar Bet by Strategy")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "profit_per_dollar_violinplot.png"))
    plt.close()

    # --- Bar Plot of Mean Values with Error Bars ---
    plt.figure(figsize=(14, 8))
    strategy_names = [s['name'] for s in all_stats]
    overall_player_edges = [s['overall_player_edge'] for s in all_stats]
    ci_lows = [s['ci_low'] for s in all_stats]
    ci_highs = [s['ci_high'] for s in all_stats]
    
    # Create error bars (confidence intervals)
    errors = [(hi - lo) / 2 for lo, hi in zip(ci_lows, ci_highs)]
    
    # Create bar plot with thicker bars
    bars = plt.bar(range(len(strategy_names)), [100 * edge for edge in overall_player_edges], 
                   yerr=[100 * err for err in errors], capsize=5, alpha=0.8, width=0.7)
    
    # Color bars based on performance (green for positive, red gradient for negative)
    for i, bar in enumerate(bars):
        if overall_player_edges[i] >= 0:
            bar.set_color('#2E8B57')  # Sea green for positive
        else:
            # Use color gradient for negative values - darker red for worse performance
            intensity = min(abs(overall_player_edges[i]) / 0.35, 1.0)  # Normalize to max seen (~35%)
            red_value = 0.8 + (0.2 * intensity)  # Range from 0.8 to 1.0
            bar.set_color((red_value, 0.2, 0.2))
    
    plt.xlabel("Strategy", fontsize=12, fontweight='bold')
    plt.ylabel("Player Edge (%)", fontsize=12, fontweight='bold')
    plt.title("Player Edge by Strategy (with 95% Confidence Intervals)", fontsize=14, fontweight='bold', pad=20)
    plt.xticks(range(len(strategy_names)), strategy_names, rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.7, linewidth=1)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on top of bars
    for i, (bar, edge) in enumerate(zip(bars, overall_player_edges)):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height >= 0 else -1.5),
                f'{100*edge:.1f}%', ha='center', va='bottom' if height >= 0 else 'top', 
                fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "profit_per_dollar_barplot.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # Write all output to file
    with open(OUTPUT_TEXT, 'w') as f:
        f.writelines(output_lines)

if __name__ == "__main__":
    main()