import os
import argparse
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from rl_agent import TetrisRLAgent, create_tetris_env

class TetrisPerformanceAnalyzer:
    """
    Analyzes the performance of Tetris AI agents.
    Collects metrics, generates visualizations, and compares different approaches.
    """
    
    def __init__(self, log_dir="./tetris_logs"):
        """
        Initialize the performance analyzer.
        
        Args:
            log_dir: Directory to save logs and analysis results
        """
        self.log_dir = log_dir
        self.results_dir = os.path.join(log_dir, "analysis")
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        self.results = {
            "agent_type": [],
            "episode": [],
            "score": [],
            "lines_cleared": [],
            "level": [],
            "duration": [],
            "pieces_placed": [],
            "avg_height": [],
            "max_height": [],
            "holes": [],
            "bumpiness": []
        }
    
    def evaluate_agent(self, agent_type, rom_path, model_path=None, algorithm="ppo", 
                      episodes=10, render=False):
        """
        Evaluate an agent and collect performance metrics.
        
        Args:
            agent_type: Type of agent being evaluated
            rom_path: Path to the Tetris ROM file
            model_path: Path to the trained model (if applicable)
            algorithm: RL algorithm used (if applicable)
            episodes: Number of episodes to evaluate
            render: Whether to render the game during evaluation
        """
        self.logger.info(f"Evaluating {agent_type} agent for {episodes} episodes")
        
        render_mode = "human" if render else "headless"
        env = create_tetris_env(rom_path, render_mode=render_mode)
        
        if agent_type == "random":
            for episode in range(episodes):
                obs, info = env.reset()
                done = False
                truncated = False
                episode_reward = 0
                episode_start_time = datetime.now()
                steps = 0
                
                while not (done or truncated):
                    action = env.action_space.sample()
                    obs, reward, done, truncated, info = env.step(action)
                    episode_reward += reward
                    steps += 1
                
                episode_duration = (datetime.now() - episode_start_time).total_seconds()
                self._record_results(agent_type, episode, info, episode_duration, steps)
                
                self.logger.info(f"Episode {episode+1}/{episodes} - Score: {info.get('score', 0)}, "
                                f"Lines: {info.get('lines', 0)}, Level: {info.get('level', 0)}")
        
        elif agent_type == "rl":
            agent = TetrisRLAgent(
                env=env,
                algorithm=algorithm,
                model_path=model_path,
                log_dir=self.log_dir
            )
            
            agent.load(model_path)
            
            episode_rewards = []
            for episode in range(episodes):
                episode_start_time = datetime.now()
                obs, info = env.reset()
                done = False
                truncated = False
                episode_reward = 0
                steps = 0
                
                while not (done or truncated):
                    action, _ = agent.model.predict(obs, deterministic=True)
                    obs, reward, done, truncated, info = env.step(action)
                    episode_reward += reward
                    steps += 1
                
                episode_rewards.append(episode_reward)
                episode_duration = (datetime.now() - episode_start_time).total_seconds()
                self._record_results(agent_type, episode, info, episode_duration, steps)
                
                self.logger.info(f"Episode {episode+1}/{episodes} - Score: {info.get('score', 0)}, "
                                f"Lines: {info.get('lines', 0)}, Level: {info.get('level', 0)}")
        
        else:
            self.logger.error(f"Unknown agent type: {agent_type}")
            return
        
        env.close()
        self.logger.info(f"Evaluation of {agent_type} agent completed")
    
    def _record_results(self, agent_type, episode, info, duration, steps):
        """
        Record the results of an episode.
        
        Args:
            agent_type: Type of agent being evaluated
            episode: Episode number
            info: Information dictionary from the environment
            duration: Duration of the episode in seconds
            steps: Number of steps taken in the episode
        """
        self.results["agent_type"].append(agent_type)
        self.results["episode"].append(episode + 1)
        self.results["score"].append(info.get("score", 0))
        self.results["lines_cleared"].append(info.get("lines", 0))
        self.results["level"].append(info.get("level", 0))
        self.results["duration"].append(duration)
        self.results["pieces_placed"].append(info.get("pieces_placed", steps // 5))
        self.results["avg_height"].append(info.get("avg_height", 0))
        self.results["max_height"].append(info.get("max_height", 0))
        self.results["holes"].append(info.get("holes", 0))
        self.results["bumpiness"].append(info.get("bumpiness", 0))
    
    def analyze_results(self):
        """
        Analyze the collected results and generate visualizations.
        """
        if not self.results["agent_type"]:
            self.logger.warning("No results to analyze")
            return
        
        df = pd.DataFrame(self.results)
        
        csv_path = os.path.join(self.results_dir, "performance_results.csv")
        df.to_csv(csv_path, index=False)
        self.logger.info(f"Raw results saved to {csv_path}")
        
        summary = df.groupby("agent_type").agg({
            "score": ["mean", "std", "min", "max"],
            "lines_cleared": ["mean", "std", "min", "max"],
            "level": ["mean", "std", "min", "max"],
            "duration": ["mean", "std", "min", "max"],
            "pieces_placed": ["mean", "std", "min", "max"]
        })
        
        summary_path = os.path.join(self.results_dir, "performance_summary.csv")
        summary.to_csv(summary_path)
        self.logger.info(f"Summary statistics saved to {summary_path}")
        
        self._generate_visualizations(df)
        
        return df, summary
    
    def _generate_visualizations(self, df):
        """
        Generate visualizations of the performance metrics.
        
        Args:
            df: DataFrame containing the results
        """
        sns.set(style="whitegrid")
        
        plt.figure(figsize=(12, 8))
        sns.boxplot(x="agent_type", y="score", data=df)
        plt.title("Score Comparison by Agent Type")
        plt.xlabel("Agent Type")
        plt.ylabel("Score")
        plt.savefig(os.path.join(self.results_dir, "score_comparison.png"))
        
        plt.figure(figsize=(12, 8))
        sns.boxplot(x="agent_type", y="lines_cleared", data=df)
        plt.title("Lines Cleared Comparison by Agent Type")
        plt.xlabel("Agent Type")
        plt.ylabel("Lines Cleared")
        plt.savefig(os.path.join(self.results_dir, "lines_comparison.png"))
        
        plt.figure(figsize=(12, 8))
        sns.boxplot(x="agent_type", y="level", data=df)
        plt.title("Level Comparison by Agent Type")
        plt.xlabel("Agent Type")
        plt.ylabel("Level")
        plt.savefig(os.path.join(self.results_dir, "level_comparison.png"))
        
        plt.figure(figsize=(12, 8))
        sns.boxplot(x="agent_type", y="duration", data=df)
        plt.title("Game Duration Comparison by Agent Type")
        plt.xlabel("Agent Type")
        plt.ylabel("Duration (seconds)")
        plt.savefig(os.path.join(self.results_dir, "duration_comparison.png"))
        
        plt.figure(figsize=(12, 8))
        sns.boxplot(x="agent_type", y="pieces_placed", data=df)
        plt.title("Pieces Placed Comparison by Agent Type")
        plt.xlabel("Agent Type")
        plt.ylabel("Pieces Placed")
        plt.savefig(os.path.join(self.results_dir, "pieces_comparison.png"))
        
        plt.figure(figsize=(12, 10))
        numeric_cols = ["score", "lines_cleared", "level", "duration", "pieces_placed", 
                        "avg_height", "max_height", "holes", "bumpiness"]
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation Between Performance Metrics")
        plt.savefig(os.path.join(self.results_dir, "correlation_heatmap.png"))
        
        key_metrics = ["score", "lines_cleared", "level", "duration", "pieces_placed"]
        plt.figure(figsize=(15, 15))
        g = sns.pairplot(df, vars=key_metrics, hue="agent_type")
        g.fig.suptitle("Pairwise Relationships Between Key Metrics", y=1.02)
        plt.savefig(os.path.join(self.results_dir, "metrics_pairplot.png"))
        
        self.logger.info(f"Visualizations saved to {self.results_dir}")

def analyze_tetris_performance():
    """Analyze the performance of Tetris AI agents."""
    parser = argparse.ArgumentParser(description="Analyze Tetris AI performance")
    parser.add_argument("--rom", default="tetris.gb", help="Path to Tetris ROM file")
    parser.add_argument("--model", required=True, help="Path to trained model")
    parser.add_argument("--algorithm", choices=["ppo", "a2c", "dqn"], default="ppo", 
                        help="RL algorithm used for the model")
    parser.add_argument("--episodes", type=int, default=20, 
                        help="Number of episodes to evaluate per agent")
    parser.add_argument("--render", action="store_true", 
                        help="Render the game during evaluation")
    parser.add_argument("--log-dir", default="./tetris_logs", 
                        help="Directory to save logs and analysis results")
    parser.add_argument("--compare-random", action="store_true", 
                        help="Compare with random agent")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(args.log_dir, "analysis.log")),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    os.makedirs(args.log_dir, exist_ok=True)
    
    if not os.path.exists(args.rom):
        logger.error(f"ROM file not found: {args.rom}")
        logger.info("Please download a Tetris ROM and place it in the project directory")
        return
    
    if not os.path.exists(args.model):
        logger.error(f"Model file not found: {args.model}")
        return
    
    logger.info(f"Analyzing Tetris AI performance with the following parameters:")
    logger.info(f"  Model: {args.model}")
    logger.info(f"  Algorithm: {args.algorithm}")
    logger.info(f"  Episodes: {args.episodes}")
    logger.info(f"  Render: {args.render}")
    logger.info(f"  Compare with random agent: {args.compare_random}")
    
    try:
        analyzer = TetrisPerformanceAnalyzer(log_dir=args.log_dir)
        
        logger.info("Evaluating RL agent")
        analyzer.evaluate_agent(
            agent_type="rl",
            rom_path=args.rom,
            model_path=args.model,
            algorithm=args.algorithm,
            episodes=args.episodes,
            render=args.render
        )
        
        if args.compare_random:
            logger.info("Evaluating random agent")
            analyzer.evaluate_agent(
                agent_type="random",
                rom_path=args.rom,
                episodes=args.episodes,
                render=args.render
            )
        
        logger.info("Analyzing results")
        df, summary = analyzer.analyze_results()
        
        logger.info("Performance Summary:")
        for agent_type in summary.index:
            logger.info(f"Agent: {agent_type}")
            logger.info(f"  Score: {summary.loc[agent_type, ('score', 'mean')]:.2f} ± {summary.loc[agent_type, ('score', 'std')]:.2f}")
            logger.info(f"  Lines: {summary.loc[agent_type, ('lines_cleared', 'mean')]:.2f} ± {summary.loc[agent_type, ('lines_cleared', 'std')]:.2f}")
            logger.info(f"  Level: {summary.loc[agent_type, ('level', 'mean')]:.2f} ± {summary.loc[agent_type, ('level', 'std')]:.2f}")
            logger.info(f"  Duration: {summary.loc[agent_type, ('duration', 'mean')]:.2f} ± {summary.loc[agent_type, ('duration', 'std')]:.2f} seconds")
        
        logger.info(f"Analysis completed. Results saved to {analyzer.results_dir}")
        
    except KeyboardInterrupt:
        logger.info("Analysis stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    analyze_tetris_performance()
