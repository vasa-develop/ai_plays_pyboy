import os
import logging
import argparse
from hybrid_tetris_ai import TetrisHybridAI

def test_hybrid_ai():
    """Test the Tetris Hybrid AI implementation."""
    parser = argparse.ArgumentParser(description="Test Tetris Hybrid AI")
    parser.add_argument("--mode", choices=["train", "play"], default="play", 
                        help="Mode to test (train or play)")
    parser.add_argument("--model", default=None, help="Path to pre-trained model")
    parser.add_argument("--timesteps", type=int, default=10000, 
                        help="Number of timesteps to train for")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    rom_path = "tetris.gb"
    if not os.path.exists(rom_path):
        logger.error(f"ROM file not found: {rom_path}")
        logger.info("Please download a Tetris ROM and place it in the project directory")
        return
    
    logger.info(f"Testing Tetris Hybrid AI in {args.mode} mode")
    
    try:
        ai = TetrisHybridAI(rom_path=rom_path, model_path=args.model)
        
        ai.create_environment()
        ai.create_model()
        
        if args.mode == "train":
            logger.info(f"Training for {args.timesteps} timesteps")
            ai.train(total_timesteps=args.timesteps, save_path="test_model")
            logger.info("Training completed")
            
            logger.info("Testing the trained model")
            ai.model_path = "test_model.zip"
            ai.create_model()  # Reload the model
            ai.play(episodes=1)
        else:
            logger.info("Playing with the model")
            ai.play(episodes=1)
        
        ai.close()
        logger.info("Test completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    test_hybrid_ai()
