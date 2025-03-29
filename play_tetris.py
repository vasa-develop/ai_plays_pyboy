import os
import sys
import logging
from tetris_ai import play_tetris_ai

def main():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    logger.debug("Starting PyBoy with Tetris AI...")
    
    rom_path = "tetris.gb"
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
        play_tetris_ai(rom_path)

if __name__ == "__main__":
    main() 