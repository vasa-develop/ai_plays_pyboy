import os
import argparse
import logging
import numpy as np
from rl_agent import TetrisRLAgent, create_tetris_env

def train_tetris_agent():
    """Train a reinforcement learning agent to play Tetris."""
    parser = argparse.ArgumentParser(description="Train RL agent for Tetris")
    parser.add_argument("--rom", default="tetris.gb", help="Path to Tetris ROM file")
    parser.add_argument("--algorithm", choices=["ppo", "a2c", "dqn"], default="ppo", 
                        help="RL algorithm to use")
    parser.add_argument("--timesteps", type=int, default=100000, 
                        help="Number of timesteps to train for")
    parser.add_argument("--checkpoint-freq", type=int, default=10000, 
                        help="Frequency (in timesteps) to save model checkpoints")
    parser.add_argument("--eval-freq", type=int, default=10000, 
                        help="Frequency (in timesteps) to evaluate the model")
    parser.add_argument("--log-dir", default="./tetris_logs", 
                        help="Directory to save logs and models")
    parser.add_argument("--model", default=None, 
                        help="Path to pre-trained model to continue training")
    parser.add_argument("--render", action="store_true", 
                        help="Render the game during training")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(args.log_dir, "training.log")),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(os.path.join(args.log_dir, "checkpoints"), exist_ok=True)
    os.makedirs(os.path.join(args.log_dir, "evaluations"), exist_ok=True)
    
    if not os.path.exists(args.rom):
        logger.error(f"ROM file not found: {args.rom}")
        logger.info("Please download a Tetris ROM and place it in the project directory")
        return
    
    logger.info(f"Training Tetris RL agent with the following parameters:")
    logger.info(f"  Algorithm: {args.algorithm}")
    logger.info(f"  Timesteps: {args.timesteps}")
    logger.info(f"  Checkpoint frequency: {args.checkpoint_freq}")
    logger.info(f"  Evaluation frequency: {args.eval_freq}")
    logger.info(f"  Log directory: {args.log_dir}")
    logger.info(f"  Pre-trained model: {args.model if args.model else 'None'}")
    logger.info(f"  Render: {args.render}")
    
    try:
        render_mode = "human" if args.render else "headless"
        env = create_tetris_env(args.rom, render_mode=render_mode)
        
        agent = TetrisRLAgent(
            env=env,
            algorithm=args.algorithm,
            model_path=args.model,
            log_dir=args.log_dir
        )
        
        agent.create_model()
        
        logger.info(f"Starting training for {args.timesteps} timesteps")
        agent.train(
            total_timesteps=args.timesteps,
            checkpoint_freq=args.checkpoint_freq,
            eval_freq=args.eval_freq
        )
        
        logger.info("Evaluating trained agent")
        mean_reward, std_reward = agent.evaluate(n_eval_episodes=5)
        
        logger.info(f"Training completed successfully")
        logger.info(f"Final evaluation: Mean reward = {mean_reward:.2f} +/- {std_reward:.2f}")
        
        env.close()
        
    except KeyboardInterrupt:
        logger.info("Training stopped by user")
        if 'env' in locals():
            env.close()
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        if 'env' in locals():
            env.close()
        raise

if __name__ == "__main__":
    train_tetris_agent()
