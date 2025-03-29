import os
import argparse
import logging
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Set up a save state for Zelda: Link's Awakening")
    parser.add_argument("--rom", required=True, help="Path to Zelda ROM file")
    parser.add_argument("--output", default="zelda_gameplay.state", 
                        help="Path to save the state file")
    parser.add_argument("--setup-time", type=int, default=30,
                        help="Time in seconds to set up the game before saving state")
    parser.add_argument("--skip-title", action="store_true", default=True,
                        help="Automatically skip the title screen")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.rom):
        logger.error(f"ROM file not found: {args.rom}")
        return
    
    logger.info(f"Starting PyBoy with ROM: {args.rom}")
    pyboy = PyBoy(args.rom, window_type="SDL2", scale=3)
    pyboy.set_emulation_speed(1)
    
    if "ZELDA" not in pyboy.cartridge_title:
        pyboy.stop()
        logger.error(f"The provided ROM is not Zelda: Link's Awakening (found: {pyboy.cartridge_title})")
        return
    
    logger.info(f"ROM loaded successfully: {pyboy.cartridge_title}")
    
    if args.skip_title:
        logger.info("Skipping title screen...")
        
        for _ in range(60):
            pyboy.tick()
        
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        for _ in range(60):
            pyboy.tick()
        
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        for _ in range(60):
            pyboy.tick()
    
    logger.info(f"Game started. You have {args.setup_time} seconds to set up the game...")
    logger.info("Use arrow keys to move, Z for B button, X for A button, Enter for Start, Backspace for Select")
    
    start_time = time.time()
    while time.time() - start_time < args.setup_time:
        remaining = int(args.setup_time - (time.time() - start_time))
        if remaining % 5 == 0 and remaining > 0:
            logger.info(f"{remaining} seconds remaining...")
        pyboy.tick()
        
    logger.info("Time's up! Saving game state...")
    
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        with open(output_path, "wb") as file:
            pyboy.save_state(file)
        logger.info(f"Game state saved to {output_path}")
        logger.info("You can now use this save state with the hybrid agent by specifying --save-state-path")
    except Exception as e:
        logger.error(f"Failed to save state: {e}")
    
    pyboy.stop()

if __name__ == "__main__":
    main()
