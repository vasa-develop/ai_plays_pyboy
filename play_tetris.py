import logging
import time
from pyboy import PyBoy

def main():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    logger.debug("Starting PyBoy...")
    
    try:
        # Initialize PyBoy
        pyboy = PyBoy("tetris.gb")
        
        tetris = pyboy.game_wrapper
        tetris.game_area_mapping(tetris.mapping_compressed, 0)
        tetris.start_game()

        # Main game loop
        while pyboy.tick():
            # Get and print game state every 60 frames (1 second)
            if pyboy.frame_count % 60 == 0:
                print(tetris)
            
            # Small delay to prevent maxing out CPU
            time.sleep(0.016)  # ~60 FPS
            
    except KeyboardInterrupt:
        logger.info("Game stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise
    finally:
        pyboy.stop()

if __name__ == "__main__":
    main() 