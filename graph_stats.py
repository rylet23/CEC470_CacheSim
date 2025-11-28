import csv
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def read_csv_stats(filename):
    """Read cache statistics from CSV file"""
    stats = []
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats.append(row)
        return stats
    except FileNotFoundError:
        print(f"Error: {filename} not found. Run a simulation first.")
        return None

def generate_all_graphs(csv_filename, output_dir="graphs"):
    """Generate all visualization graphs from CSV statistics"""
    stats = read_csv_stats(csv_filename)
    if not stats:
        return False

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)

    # Extract data
    levels = [s['level'] for s in stats]
    hit_rates = [float(s['hit_rate']) * 100 for s in stats]
    hits = [int(s['hits']) for s in stats]
    misses = [int(s['misses']) for s in stats]
    accesses = [int(s['accesses']) for s in stats]
    capacities = [int(s['capacity']) for s in stats]

    # Get overall statistics (same for all rows)
    total_accesses = int(stats[0]['total_accesses_overall'])
    main_memory_accesses = int(stats[0]['main_memory_accesses'])
    amat = float(stats[0]['AMAT'])

    # Set up the plotting style
    plt.style.use('seaborn-v0_8-darkgrid')
    colors = ['#3498db', '#e74c3c', '#2ecc71']

    # 1. Hit Rate Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(levels, hit_rates, color=colors, alpha=0.8, edgecolor='black')
    ax.set_ylabel('Hit Rate (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Cache Level', fontsize=12, fontweight='bold')
    ax.set_title('Cache Hit Rate by Level', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 100])

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/hit_rate_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Hits vs Misses
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(levels))
    width = 0.35

    bars1 = ax.bar(x - width/2, hits, width, label='Hits', color='#2ecc71', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, misses, width, label='Misses', color='#e74c3c', alpha=0.8, edgecolor='black')

    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_xlabel('Cache Level', fontsize=12, fontweight='bold')
    ax.set_title('Hits vs Misses by Cache Level', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(levels)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/hits_vs_misses.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Access Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(levels, accesses, color=colors, alpha=0.8, edgecolor='black')
    ax.set_ylabel('Number of Accesses', fontsize=12, fontweight='bold')
    ax.set_xlabel('Cache Level', fontsize=12, fontweight='bold')
    ax.set_title('Access Distribution Across Cache Levels', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/access_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Cache Capacity vs Hit Rate
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.set_xlabel('Cache Level', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Capacity (blocks)', fontsize=12, fontweight='bold', color='#3498db')
    bars1 = ax1.bar(np.arange(len(levels)) - 0.2, capacities, 0.4,
                    label='Capacity', color='#3498db', alpha=0.8, edgecolor='black')
    ax1.tick_params(axis='y', labelcolor='#3498db')
    ax1.set_xticks(range(len(levels)))
    ax1.set_xticklabels(levels)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Hit Rate (%)', fontsize=12, fontweight='bold', color='#e74c3c')
    bars2 = ax2.bar(np.arange(len(levels)) + 0.2, hit_rates, 0.4,
                    label='Hit Rate', color='#e74c3c', alpha=0.8, edgecolor='black')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    ax2.set_ylim([0, 100])

    ax1.set_title('Cache Capacity vs Hit Rate', fontsize=14, fontweight='bold')

    # Add legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/capacity_vs_hitrate.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 5. Memory Access Breakdown (Pie Chart)
    # Calculate where data was found
    l1_hits = hits[0]
    l2_hits = hits[1]
    l3_hits = hits[2]
    mem_accesses = main_memory_accesses

    fig, ax = plt.subplots(figsize=(10, 8))
    sizes = [l1_hits, l2_hits, l3_hits, mem_accesses]
    labels = [f'L1 Cache\n({l1_hits} hits)',
              f'L2 Cache\n({l2_hits} hits)',
              f'L3 Cache\n({l3_hits} hits)',
              f'Main Memory\n({mem_accesses} accesses)']
    colors_pie = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
    explode = (0.05, 0.05, 0.05, 0.1)

    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
                                        autopct='%1.1f%%', shadow=True, startangle=90,
                                        textprops={'fontsize': 11, 'fontweight': 'bold'})

    ax.set_title('Memory Access Distribution', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/memory_access_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 6. Performance Summary
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')

    # Create summary statistics
    summary_text = f"""
    CACHE PERFORMANCE SUMMARY
    {'='*50}

    Overall Statistics:
    • Total Memory Accesses: {total_accesses:,}
    • Main Memory Accesses: {main_memory_accesses:,}
    • Average Memory Access Time (AMAT): {amat:.2f} cycles

    Cache Level Performance:
    """

    for i, level in enumerate(levels):
        summary_text += f"\n    {level}:\n"
        summary_text += f"      - Capacity: {capacities[i]} blocks\n"
        summary_text += f"      - Accesses: {accesses[i]:,}\n"
        summary_text += f"      - Hits: {hits[i]:,} ({hit_rates[i]:.2f}%)\n"
        summary_text += f"      - Misses: {misses[i]:,}\n"

    ax.text(0.1, 0.95, summary_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(f'{output_dir}/performance_summary.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\nGraphs successfully generated in '{output_dir}/' directory:")
    print(f"  - hit_rate_comparison.png")
    print(f"  - hits_vs_misses.png")
    print(f"  - access_distribution.png")
    print(f"  - capacity_vs_hitrate.png")
    print(f"  - memory_access_distribution.png")
    print(f"  - performance_summary.png")

    return True

def show_graphs_interactive(csv_filename):
    """Generate and display graphs interactively"""
    if generate_all_graphs(csv_filename):
        print("\nGraphs have been saved. Opening for display...")
        # Note: plt.show() would block, so we just save the files

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = "results_gui.csv"

    generate_all_graphs(csv_file)
