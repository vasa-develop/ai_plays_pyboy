import os
import argparse
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation

def load_performance_data(file_path):
    """
    Load performance data from a CSV file.
    
    Args:
        file_path: Path to the CSV file containing performance data
        
    Returns:
        DataFrame containing the performance data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Performance data file not found: {file_path}")
    
    return pd.read_csv(file_path)

def create_performance_dashboard(data, output_dir):
    """
    Create a comprehensive performance dashboard with multiple visualizations.
    
    Args:
        data: DataFrame containing the performance data
        output_dir: Directory to save the visualizations
    """
    os.makedirs(output_dir, exist_ok=True)
    
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12
    
    plt.figure()
    sns.histplot(data=data, x="score", hue="agent_type", kde=True, bins=20)
    plt.title("Score Distribution by Agent Type")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    plt.savefig(os.path.join(output_dir, "score_distribution.png"))
    plt.close()
    
    plt.figure()
    sns.histplot(data=data, x="lines_cleared", hue="agent_type", kde=True, bins=20)
    plt.title("Lines Cleared Distribution by Agent Type")
    plt.xlabel("Lines Cleared")
    plt.ylabel("Frequency")
    plt.savefig(os.path.join(output_dir, "lines_distribution.png"))
    plt.close()
    
    plt.figure()
    sns.scatterplot(data=data, x="lines_cleared", y="score", hue="agent_type", size="level", sizes=(50, 200))
    plt.title("Score vs. Lines Cleared")
    plt.xlabel("Lines Cleared")
    plt.ylabel("Score")
    plt.savefig(os.path.join(output_dir, "score_vs_lines.png"))
    plt.close()
    
    plt.figure()
    sns.scatterplot(data=data, x="duration", y="score", hue="agent_type", size="level", sizes=(50, 200))
    plt.title("Score vs. Game Duration")
    plt.xlabel("Duration (seconds)")
    plt.ylabel("Score")
    plt.savefig(os.path.join(output_dir, "score_vs_duration.png"))
    plt.close()
    
    plt.figure()
    sns.scatterplot(data=data, x="pieces_placed", y="score", hue="agent_type", size="level", sizes=(50, 200))
    plt.title("Score vs. Pieces Placed")
    plt.xlabel("Pieces Placed")
    plt.ylabel("Score")
    plt.savefig(os.path.join(output_dir, "score_vs_pieces.png"))
    plt.close()
    
    plt.figure()
    sns.scatterplot(data=data, x="pieces_placed", y="lines_cleared", hue="agent_type", size="level", sizes=(50, 200))
    plt.title("Lines Cleared vs. Pieces Placed")
    plt.xlabel("Pieces Placed")
    plt.ylabel("Lines Cleared")
    plt.savefig(os.path.join(output_dir, "lines_vs_pieces.png"))
    plt.close()
    
    plt.figure()
    sns.lineplot(data=data, x="episode", y="score", hue="agent_type", marker="o")
    plt.title("Score Progression Over Episodes")
    plt.xlabel("Episode")
    plt.ylabel("Score")
    plt.savefig(os.path.join(output_dir, "score_progression.png"))
    plt.close()
    
    plt.figure()
    sns.lineplot(data=data, x="episode", y="lines_cleared", hue="agent_type", marker="o")
    plt.title("Lines Cleared Progression Over Episodes")
    plt.xlabel("Episode")
    plt.ylabel("Lines Cleared")
    plt.savefig(os.path.join(output_dir, "lines_progression.png"))
    plt.close()
    
    plt.figure()
    sns.lineplot(data=data, x="episode", y="level", hue="agent_type", marker="o")
    plt.title("Level Progression Over Episodes")
    plt.xlabel("Episode")
    plt.ylabel("Level")
    plt.savefig(os.path.join(output_dir, "level_progression.png"))
    plt.close()
    
    plt.figure()
    sns.lineplot(data=data, x="episode", y="duration", hue="agent_type", marker="o")
    plt.title("Game Duration Progression Over Episodes")
    plt.xlabel("Episode")
    plt.ylabel("Duration (seconds)")
    plt.savefig(os.path.join(output_dir, "duration_progression.png"))
    plt.close()
    
    create_radar_chart(data, output_dir)
    
    create_summary_table(data, output_dir)
    
    create_animated_visualization(data, output_dir)

def create_radar_chart(data, output_dir):
    """
    Create a radar chart comparing different agents across multiple metrics.
    
    Args:
        data: DataFrame containing the performance data
        output_dir: Directory to save the visualization
    """
    metrics = ["score", "lines_cleared", "level", "duration", "pieces_placed"]
    
    normalized_data = {}
    
    for agent_type in data["agent_type"].unique():
        agent_data = data[data["agent_type"] == agent_type]
        normalized_data[agent_type] = {}
        
        for metric in metrics:
            if metric == "duration":
                min_val = data[metric].min()
                max_val = data[metric].max()
                if max_val > min_val:
                    normalized_data[agent_type][metric] = 1 - (agent_data[metric].mean() - min_val) / (max_val - min_val)
                else:
                    normalized_data[agent_type][metric] = 0.5
            else:
                min_val = data[metric].min()
                max_val = data[metric].max()
                if max_val > min_val:
                    normalized_data[agent_type][metric] = (agent_data[metric].mean() - min_val) / (max_val - min_val)
                else:
                    normalized_data[agent_type][metric] = 0.5
    
    plt.figure(figsize=(10, 10))
    
    angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # Close the loop
    
    ax = plt.subplot(111, polar=True)
    
    plt.xticks(angles[:-1], metrics)
    
    for agent_type, metrics_data in normalized_data.items():
        values = [metrics_data[metric] for metric in metrics]
        values += values[:1]  # Close the loop
        
        ax.plot(angles, values, linewidth=2, label=agent_type)
        ax.fill(angles, values, alpha=0.25)
    
    plt.title("Agent Performance Comparison")
    plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))
    
    plt.savefig(os.path.join(output_dir, "radar_chart.png"))
    plt.close()

def create_summary_table(data, output_dir):
    """
    Create a summary table of performance metrics for each agent type.
    
    Args:
        data: DataFrame containing the performance data
        output_dir: Directory to save the table
    """
    summary = data.groupby("agent_type").agg({
        "score": ["mean", "std", "min", "max"],
        "lines_cleared": ["mean", "std", "min", "max"],
        "level": ["mean", "std", "min", "max"],
        "duration": ["mean", "std", "min", "max"],
        "pieces_placed": ["mean", "std", "min", "max"]
    })
    
    summary_path = os.path.join(output_dir, "performance_summary.csv")
    summary.to_csv(summary_path)
    
    plt.figure(figsize=(15, 10))
    plt.axis('off')
    
    table_data = []
    table_columns = ["Agent Type", "Score", "Lines Cleared", "Level", "Duration (s)", "Pieces Placed"]
    
    for agent_type in summary.index:
        row = [
            agent_type,
            f"{summary.loc[agent_type, ('score', 'mean')]:.2f} ± {summary.loc[agent_type, ('score', 'std')]:.2f}",
            f"{summary.loc[agent_type, ('lines_cleared', 'mean')]:.2f} ± {summary.loc[agent_type, ('lines_cleared', 'std')]:.2f}",
            f"{summary.loc[agent_type, ('level', 'mean')]:.2f} ± {summary.loc[agent_type, ('level', 'std')]:.2f}",
            f"{summary.loc[agent_type, ('duration', 'mean')]:.2f} ± {summary.loc[agent_type, ('duration', 'std')]:.2f}",
            f"{summary.loc[agent_type, ('pieces_placed', 'mean')]:.2f} ± {summary.loc[agent_type, ('pieces_placed', 'std')]:.2f}"
        ]
        table_data.append(row)
    
    table = plt.table(
        cellText=table_data,
        colLabels=table_columns,
        loc='center',
        cellLoc='center',
        colColours=['#f2f2f2'] * len(table_columns)
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 2)
    
    plt.title("Performance Summary", fontsize=16, pad=20)
    
    plt.savefig(os.path.join(output_dir, "summary_table.png"), bbox_inches='tight')
    plt.close()

def create_animated_visualization(data, output_dir):
    """
    Create an animated visualization of performance metrics over episodes.
    
    Args:
        data: DataFrame containing the performance data
        output_dir: Directory to save the animation
    """
    if len(data["episode"].unique()) <= 1:
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    ax1.set_xlim(0, data["score"].max() * 1.1)
    ax1.set_ylim(0, data["lines_cleared"].max() * 1.1)
    ax1.set_xlabel("Score")
    ax1.set_ylabel("Lines Cleared")
    ax1.set_title("Score vs. Lines Cleared")
    
    ax2.set_xlim(0, data["pieces_placed"].max() * 1.1)
    ax2.set_ylim(0, data["level"].max() * 1.1)
    ax2.set_xlabel("Pieces Placed")
    ax2.set_ylabel("Level")
    ax2.set_title("Pieces Placed vs. Level")
    
    scatters1 = {}
    scatters2 = {}
    
    for agent_type in data["agent_type"].unique():
        color = next(ax1._get_lines.prop_cycler)['color']
        scatters1[agent_type] = ax1.scatter([], [], label=agent_type, color=color, s=100)
        scatters2[agent_type] = ax2.scatter([], [], label=agent_type, color=color, s=100)
    
    ax1.legend()
    ax2.legend()
    
    episode_text = fig.text(0.5, 0.95, "", ha='center', fontsize=12)
    
    def update(frame):
        episode = frame + 1
        episode_data = data[data["episode"] <= episode]
        
        episode_text.set_text(f"Episode: {episode}")
        
        for agent_type in data["agent_type"].unique():
            agent_data = episode_data[episode_data["agent_type"] == agent_type]
            
            scatters1[agent_type].set_offsets(np.column_stack((agent_data["score"], agent_data["lines_cleared"])))
            scatters2[agent_type].set_offsets(np.column_stack((agent_data["pieces_placed"], agent_data["level"])))
        
        return list(scatters1.values()) + list(scatters2.values()) + [episode_text]
    
    max_episodes = data["episode"].max()
    ani = FuncAnimation(fig, update, frames=max_episodes, blit=True)
    
    ani.save(os.path.join(output_dir, "performance_animation.gif"), writer='pillow', fps=2)
    plt.close()

def visualize_performance():
    """Visualize the performance of Tetris AI agents."""
    parser = argparse.ArgumentParser(description="Visualize Tetris AI performance")
    parser.add_argument("--data", required=True, help="Path to performance data CSV file")
    parser.add_argument("--output-dir", default="./tetris_logs/visualizations", 
                        help="Directory to save visualizations")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Loading performance data from {args.data}")
        data = load_performance_data(args.data)
        
        logger.info(f"Creating performance visualizations in {args.output_dir}")
        create_performance_dashboard(data, args.output_dir)
        
        logger.info(f"Visualizations created successfully")
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    visualize_performance()
