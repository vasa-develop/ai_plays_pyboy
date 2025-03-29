import os
import argparse
import logging
from zelda_rl_agent import ZeldaRLAgent, create_zelda_env

def train_zelda_agent():
    """Train a reinforcement learning agent to play Zelda: Link's Awakening."""
    parser = argparse.ArgumentParser(description="Train RL agent for Zelda: Link's Awakening")
    parser.add_argument("--rom", default="zelda.gb", help="Path to Zelda ROM file")
    parser.add_argument("--algorithm", choices=["ppo", "a2c", "dqn"], default="ppo", 
                        help="RL algorithm to use")
    parser.add_argument("--timesteps", type=int, default=100000, 
                        help="Number of timesteps to train for")
    parser.add_argument("--checkpoint-freq", type=int, default=10000, 
                        help="Frequency (in timesteps) to save model checkpoints")
    parser.add_argument("--eval-freq", type=int, default=10000, 
                        help="Frequency (in timesteps) to evaluate the model")
    parser.add_argument("--log-dir", default="./zelda_logs", 
                        help="Directory to save logs and models")
    parser.add_argument("--model", default=None, 
                        help="Path to pre-trained model to continue training")
    parser.add_argument("--render", action="store_true", 
                        help="Render the game during training")
    args = parser.parse_args()
    
    os.makedirs(args.log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(args.log_dir, "training.log")),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(args.rom):
        logger.error(f"ROM file not found: {args.rom}")
        logger.info("Please download a Zelda: Link's Awakening ROM and place it in the project directory")
        return
    
    logger.info(f"Training Zelda RL agent with the following parameters:")
    logger.info(f"  Algorithm: {args.algorithm}")
    logger.info(f"  Timesteps: {args.timesteps}")
    logger.info(f"  Checkpoint frequency: {args.checkpoint_freq}")
    logger.info(f"  Evaluation frequency: {args.eval_freq}")
    logger.info(f"  Log directory: {args.log_dir}")
    logger.info(f"  Pre-trained model: {args.model}")
    logger.info(f"  Render: {args.render}")
    
    try:
        render_mode = "human" if args.render else "headless"
        env = create_zelda_env(args.rom, render_mode=render_mode)
        
        agent = ZeldaRLAgent(
            env=env,
            algorithm=args.algorithm,
            model_path=args.model,
            log_dir=args.log_dir
        )
        
        if args.model is not None and os.path.exists(args.model):
            agent.load(args.model)
        
        save_path = os.path.join(args.log_dir, f"zelda_{args.algorithm}_final.zip")
        agent.train(
            total_timesteps=args.timesteps,
            eval_freq=args.eval_freq,
            save_freq=args.checkpoint_freq,
            n_eval_episodes=5,
            save_path=save_path
        )
        
        env.close()
        
        logger.info(f"Training completed. Final model saved to {save_path}")
        
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
    train_zelda_agent()
