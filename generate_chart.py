import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Load data from values.json
data = json.loads(Path("values.json").read_text())

# Process data
series = {}
for guid, entries in data.items():
    series[guid] = sorted(
        (datetime.strptime(hour, "%Y-%m-%dT%H"), value)
        for hour, value in entries.items()
        if hour != "total"
    )

recent_start = datetime(2026, 9, 29)

# Create professional dashboard
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Define color palette
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

# 1. Main time series chart
ax_main = fig.add_subplot(gs[0:2, :])
for (guid, points), color in zip(series.items(), colors):
    recent = [(time, value) for time, value in points if time >= recent_start]
    if recent:
        times, values = zip(*recent)
        label = f"Task {guid[:8]}" 
        ax_main.plot(times, values, linewidth=2, marker="o", markersize=4, label=label, color=color, alpha=0.7)

ax_main.set_title("Hourly Activity by Task ID (Sep 29 - Oct 5, 2026)", fontsize=14, fontweight='bold', pad=20)
ax_main.set_ylabel("Count", fontsize=11, fontweight='bold')
ax_main.set_xlabel("Date & Time", fontsize=11, fontweight='bold')
ax_main.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax_main.xaxis.set_major_locator(mdates.DayLocator())
ax_main.grid(True, alpha=0.3, linestyle='--')
ax_main.legend(loc='upper left', framealpha=0.9, fontsize=10)

# 2. Total values bar chart
ax_totals = fig.add_subplot(gs[2, 0])
guids = list(series.keys())
totals = [data[guid].get('total', 0) for guid in guids]
labels = [f"Task\n{guid[:8]}" for guid in guids]
bars = ax_totals.bar(labels, totals, color=colors[:len(guids)], alpha=0.7, edgecolor='black', linewidth=1.5)
ax_totals.set_title("Total Count by Task", fontsize=12, fontweight='bold')
ax_totals.set_ylabel("Total", fontsize=10, fontweight='bold')
ax_totals.grid(axis='y', alpha=0.3, linestyle='--')
# Add value labels on bars
for bar, total in zip(bars, totals):
    height = bar.get_height()
    ax_totals.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(total)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# 3. Peak values summary
ax_summary = fig.add_subplot(gs[2, 1])
ax_summary.axis('off')
summary_text = "Summary Statistics\n" + "="*40 + "\n\n"
for (guid, points), label in zip(series.items(), labels):
    recent = [(time, value) for time, value in points if time >= recent_start]
    if recent:
        values = [v for _, v in recent]
        summary_text += f"{label.replace(chr(10), ' ')}: Max={max(values)}, Avg={np.mean(values):.0f}\n"

ax_summary.text(0.05, 0.95, summary_text, transform=ax_summary.transAxes,
                fontsize=10, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.suptitle("Task Performance Metrics Dashboard", fontsize=16, fontweight='bold', y=0.98)
fig.text(0.99, 0.01, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
         ha='right', fontsize=8, style='italic', color='gray')

plt.savefig("metrics_dashboard.png", dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Chart saved: metrics_dashboard.png (300 DPI)")

# Also create a simpler version
fig2, axes = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle("Task Metrics - Detailed View", fontsize=14, fontweight='bold')

for idx, ((guid, points), color, ax) in enumerate(zip(series.items(), colors, axes.flat)):
    recent = [(time, value) for time, value in points if time >= recent_start]
    if recent:
        times, values = zip(*recent)
        ax.fill_between(times, values, alpha=0.3, color=color)
        ax.plot(times, values, linewidth=2, marker="o", markersize=5, color=color)
        ax.set_title(f"Task {guid[:8]}", fontweight='bold')
        ax.set_ylabel("Count", fontsize=10)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig("metrics_detailed.png", dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Chart saved: metrics_detailed.png (300 DPI)")
plt.close('all')
