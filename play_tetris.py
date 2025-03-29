import os
import sys
import logging
import argparse
from tetris_ai import play_tetris_ai
from hybrid_tetris_ai import play_tetris_hybrid_ai

def main():
    parser = argparse.ArgumentParser(description="Play Tetris with AI on PyBoy")
    parser.add_argument("--mode", choices=["heuristic", "hybrid-play", "hybrid-train"], 
                        default="heuristic", help="AI mode to use")
    parser.add_argument("--rom", default="tetris.gb", help="Path to Tetris ROM file")
    parser.add_argument("--model", default=None, help="Path to pre-trained model (for hybrid mode)")
    parser.add_argument("--timesteps", type=int, default=100000, 
                        help="Number of timesteps to train for (hybrid-train mode)")
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    rom_path = args.rom
    if not os.path.exists(rom_path):
        logger.warning(f"ROM file not found: {rom_path}")
        logger.info("Running PyBoy without AI. Please download a Tetris ROM for AI functionality.")
        try:
            import subprocess
            subprocess.run([sys.executable, "-m", "pyboy", rom_path])
        except KeyboardInterrupt:
            logger.info("Game stopped by user")
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            raise
    else:
        logger.debug(f"Starting PyBoy with Tetris AI in {args.mode} mode...")
        
        if args.mode == "heuristic":
            play_tetris_ai(rom_path)
        elif args.mode == "hybrid-play":
            play_tetris_hybrid_ai(rom_path, args.model, "play")
        elif args.mode == "hybrid-train":
            play_tetris_hybrid_ai(rom_path, args.model, "train", args.timesteps)

if __name__ == "__main__":
    main()    