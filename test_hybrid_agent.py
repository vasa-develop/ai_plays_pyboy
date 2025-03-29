"""
Test script for the hybrid RL+LLM approach for Zelda: Link's Awakening.
This script allows testing different aspects of the hybrid agent.
"""

import os
import argparse
import logging
from hybrid_zelda_agent import HybridZeldaAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("hybrid_test.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Test the Hybrid Zelda Agent")
    parser.add_argument("--rom", required=True, help="Path to Zelda ROM file")
    parser.add_argument("--mode", choices=["play", "train", "test_llm"], default="play", 
                        help="Test mode: play with hybrid agent, train RL component, or test LLM integration")
    parser.add_argument("--rl-model", help="Path to pre-trained RL model (for play mode)")
    parser.add_argument("--timesteps", type=int, default=10000, help="Number of timesteps to train for")
    parser.add_argument("--episodes", type=int, default=1, help="Number of episodes to play")
    parser.add_argument("--llm-frequency", type=float, default=0.2, 
                        help="Frequency of LLM guidance (0.0 to 1.0)")
    parser.add_argument("--log-dir", default="./hybrid_logs", help="Directory to save logs")
    parser.add_argument("--render", choices=["human", "rgb_array"], default="human", 
                        help="Rendering mode")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.rom):
        logger.error(f"ROM file not found: {args.rom}")
        return
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.warning("OpenRouter API key not found in environment. Set OPENROUTER_API_KEY.")
        return
    
    logger.info(f"Starting hybrid agent test in {args.mode} mode")
    
    if args.mode == "test_llm":
        from llm_integration import LLMIntegration
        
        llm = LLMIntegration(api_key=api_key)
        
        game_state = {
            "map_position": (5, 7),
            "health": 3,
            "inventory": ["Sword", "Shield", "Ocarina"]
        }
        
        dialogue = "You need to find the Tail Key to enter the Tail Cave. It's hidden somewhere in the Mysterious Forest."
        dialogue_context = {
            "map_position": (5, 7),
            "previous_objectives": ["Find the sword"]
        }
        
        logger.info("Testing dialogue interpretation...")
        interpretation = llm.interpret_dialogue(dialogue, dialogue_context)
        logger.info(f"Dialogue interpretation: {interpretation}")
        
        logger.info("Testing quest planning...")
        plan = llm.plan_quest_progression("Find the Tail Key", game_state)
        logger.info(f"Quest plan: {plan}")
        
        return
    
    agent = HybridZeldaAgent(
        rom_path=args.rom,
        rl_model_path=args.rl_model,
        llm_api_key=api_key,
        log_dir=args.log_dir,
        render_mode=args.render
    )
    
    try:
        if args.mode == "train":
            logger.info(f"Training RL component for {args.timesteps} timesteps")
            agent.train_rl_component(
                total_timesteps=args.timesteps,
                eval_freq=max(1000, args.timesteps // 10),
                save_freq=max(1000, args.timesteps // 5)
            )
        else:  # play mode
            if args.rl_model:
                agent.load_rl_model(args.rl_model)
            
            logger.info(f"Playing {args.episodes} episodes with LLM guidance frequency {args.llm_frequency}")
            episode_rewards = agent.play(
                episodes=args.episodes,
                llm_guidance_frequency=args.llm_frequency
            )
            
            logger.info(f"Episode rewards: {episode_rewards}")
    
    finally:
        agent.close()

if __name__ == "__main__":
    main()
