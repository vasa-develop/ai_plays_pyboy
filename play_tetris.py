import subprocess
import sys
import logging

def main():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    logger.debug("Starting PyBoy...")
    
    try:
        # Run PyBoy directly using the command-line interface
        subprocess.run([sys.executable, "-m", "pyboy", "tetris.gb"])
    except KeyboardInterrupt:
        logger.info("Game stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 