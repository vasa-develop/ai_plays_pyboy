import os
import argparse
import logging
from zelda_rl_agent import ZeldaRLAgent, create_zelda_env

def test_zelda_ai():
    """Test the Zelda AI implementation with basic functionality."""
    parser = argparse.ArgumentParser(description="Test Zelda AI implementation")
    parser.add_argument("--rom", default="zelda.gb", help="Path to Zelda ROM file")
    parser.add_argument("--mode", choices=["env", "random", "train", "play"], default="env",
                        help="Test mode: env (test environment), random (random actions), "
                             "train (train for a few steps), play (play with trained model)")
    parser.add_argument("--model", default=None, help="Path to trained model for play mode")
    parser.add_argument("--timesteps", type=int, default=1000, 
                        help="Number of timesteps to train for in train mode")
    parser.add_argument("--episodes", type=int, default=1, 
                        help="Number of episodes to play in play mode")
    parser.add_argument("--delay", type=float, default=0.1, 
                        help="Delay between actions in seconds")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(args.rom):
        logger.error(f"ROM file not found: {args.rom}")
        return
    
    logger.info(f"Testing Zelda AI with ROM: {args.rom}")
    logger.info(f"Test mode: {args.mode}")
    
    try:
        if args.mode == "env":
            logger.info("Testing Zelda environment...")
            env = create_zelda_env(args.rom, render_mode="human")
            
            logger.info("Resetting environment...")
            obs, info = env.reset()
            logger.info(f"Observation shape: {obs['screen'].shape}")
            logger.info(f"Info: {info}")
            
            logger.info("Taking random actions...")
            for i in range(100):
                action = env.action_space.sample()
                obs, reward, done, truncated, info = env.step(action)
                
                if i % 10 == 0:
                    logger.info(f"Step {i}, Action: {action}, Reward: {reward}")
                
                if done or truncated:
                    logger.info(f"Episode ended after {i+1} steps")
                    break
                
                import time
                time.sleep(args.delay)
            
            env.close()
            logger.info("Environment test completed")
            
        elif args.mode == "random":
            logger.info("Testing random actions...")
            env = create_zelda_env(args.rom, render_mode="human")
            
            total_reward = 0
            obs, info = env.reset()
            
            for i in range(1000):
                action = env.action_space.sample()
                obs, reward, done, truncated, info = env.step(action)
                total_reward += reward
                
                if i % 100 == 0:
                    logger.info(f"Step {i}, Total reward: {total_reward:.2f}")
                
                if done or truncated:
                    logger.info(f"Episode ended after {i+1} steps with total reward {total_reward:.2f}")
                    break
                
                import time
                time.sleep(args.delay)
            
            env.close()
            logger.info("Random actions test completed")
            
        elif args.mode == "train":
            logger.info(f"Testing training for {args.timesteps} timesteps...")
            env = create_zelda_env(args.rom, render_mode="human")
            
            agent = ZeldaRLAgent(
                env=env,
                algorithm="ppo",
                log_dir="./zelda_logs"
            )
            
            logger.info("Training agent...")
            agent.train(
                total_timesteps=args.timesteps,
                eval_freq=args.timesteps // 2,
                save_freq=args.timesteps,
                n_eval_episodes=1,
                save_path="./zelda_logs/zelda_test_model.zip"
            )
            
            env.close()
            logger.info("Training test completed")
            
        elif args.mode == "play":
            if args.model is None or not os.path.exists(args.model):
                logger.error("Model file not specified or not found")
                return
            
            logger.info(f"Testing playing with model: {args.model}")
            env = create_zelda_env(args.rom, render_mode="human")
            
            agent = ZeldaRLAgent(
                env=env,
                algorithm="ppo",
                model_path=args.model,
                log_dir="./zelda_logs"
            )
            
            agent.load(args.model)
            
            logger.info(f"Playing for {args.episodes} episodes...")
            episode_rewards = agent.play(
                episodes=args.episodes,
                deterministic=True,
                delay=args.delay
            )
            
            logger.info(f"Episode rewards: {episode_rewards}")
            
            env.close()
            logger.info("Play test completed")
            
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
        if 'env' in locals():
            env.close()
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        if 'env' in locals():
            env.close()
        raise

if __name__ == "__main__":
    test_zelda_ai()
