import os
import argparse
import logging
import numpy as np
import matplotlib.pyplot as plt
from zelda_rl_agent import ZeldaRLAgent, create_zelda_env

def evaluate_zelda_agent():
    """Evaluate a trained reinforcement learning agent playing Zelda: Link's Awakening."""
    parser = argparse.ArgumentParser(description="Evaluate RL agent for Zelda: Link's Awakening")
    parser.add_argument("--rom", default="zelda.gbc", help="Path to Zelda ROM file")
    parser.add_argument("--model", required=True, help="Path to trained model")
    parser.add_argument("--algorithm", choices=["ppo", "a2c", "dqn"], default="ppo", 
                        help="RL algorithm used for the model")
    parser.add_argument("--episodes", type=int, default=5, 
                        help="Number of episodes to evaluate")
    parser.add_argument("--render", action="store_true", 
                        help="Render the game during evaluation")
    parser.add_argument("--log-dir", default="./zelda_logs", 
                        help="Directory to save logs and evaluation results")
    parser.add_argument("--delay", type=float, default=0.0, 
                        help="Delay between moves in seconds (for streaming)")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(args.log_dir, "evaluation.log")),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(os.path.join(args.log_dir, "results"), exist_ok=True)
    
    if not os.path.exists(args.rom):
        logger.error(f"ROM file not found: {args.rom}")
        logger.info("Please download a Zelda: Link's Awakening ROM and place it in the project directory")
        return
    
    if not os.path.exists(args.model):
        logger.error(f"Model file not found: {args.model}")
        return
    
    logger.info(f"Evaluating Zelda RL agent with the following parameters:")
    logger.info(f"  Model: {args.model}")
    logger.info(f"  Algorithm: {args.algorithm}")
    logger.info(f"  Episodes: {args.episodes}")
    logger.info(f"  Render: {args.render}")
    logger.info(f"  Delay: {args.delay}s")
    
    try:
        render_mode = "human" if args.render else "headless"
        env = create_zelda_env(args.rom, render_mode=render_mode)
        
        agent = ZeldaRLAgent(
            env=env,
            algorithm=args.algorithm,
            model_path=args.model,
            log_dir=args.log_dir
        )
        
        agent.load(args.model)
        
        logger.info(f"Starting evaluation for {args.episodes} episodes with {args.delay}s delay")
        episode_rewards = agent.play(episodes=args.episodes, deterministic=True, delay=args.delay)
        
        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards)
        min_reward = np.min(episode_rewards)
        max_reward = np.max(episode_rewards)
        
        logger.info(f"Evaluation completed")
        logger.info(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")
        logger.info(f"Min reward: {min_reward:.2f}")
        logger.info(f"Max reward: {max_reward:.2f}")
        
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(episode_rewards) + 1), episode_rewards, marker='o')
        plt.axhline(y=mean_reward, color='r', linestyle='-', label=f'Mean: {mean_reward:.2f}')
        plt.fill_between(
            range(1, len(episode_rewards) + 1),
            mean_reward - std_reward,
            mean_reward + std_reward,
            alpha=0.2,
            color='r',
            label=f'Std Dev: {std_reward:.2f}'
        )
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.title('Zelda RL Agent Evaluation')
        plt.legend()
        plt.grid(True)
        
        plot_path = os.path.join(args.log_dir, "results", "evaluation_plot.png")
        plt.savefig(plot_path)
        logger.info(f"Evaluation plot saved to {plot_path}")
        
        results_path = os.path.join(args.log_dir, "results", "evaluation_results.txt")
        with open(results_path, 'w') as f:
            f.write(f"Evaluation Results for Zelda RL Agent\n")
            f.write(f"Model: {args.model}\n")
            f.write(f"Algorithm: {args.algorithm}\n")
            f.write(f"Episodes: {args.episodes}\n\n")
            f.write(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}\n")
            f.write(f"Min reward: {min_reward:.2f}\n")
            f.write(f"Max reward: {max_reward:.2f}\n\n")
            f.write("Episode Rewards:\n")
            for i, reward in enumerate(episode_rewards):
                f.write(f"Episode {i+1}: {reward:.2f}\n")
        
        logger.info(f"Evaluation results saved to {results_path}")
        
        env.close()
        
    except KeyboardInterrupt:
        logger.info("Evaluation stopped by user")
        if 'env' in locals():
            env.close()
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        if 'env' in locals():
            env.close()
        raise

if __name__ == "__main__":
    evaluate_zelda_agent()
