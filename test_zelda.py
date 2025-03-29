import os
import time
import logging
from pyboy import PyBoy
from pyboy.utils import WindowEvent

def test_zelda_rom():
    """Test the Zelda ROM with PyBoy."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    rom_path = "zelda.gb"
    if not os.path.exists(rom_path):
        logger.error(f"ROM file not found: {rom_path}")
        return
    
    logger.info(f"Testing Zelda ROM: {rom_path}")
    
    try:
        pyboy = PyBoy(rom_path, window="SDL2", scale=3)
        
        logger.info(f"Cartridge title: {pyboy.cartridge_title}")
        
        screen = pyboy.botsupport_manager().screen()
        logger.info(f"Screen dimensions: {screen.raw_screen_buffer_dims()}")
        
        logger.info("Running game for 5 seconds...")
        
        for _ in range(60):
            pyboy.tick()
        
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        for i in range(300):
            pyboy.tick()
            
            if i % 60 == 0:
                logger.info(f"Frame {i}: Pressing A button")
                pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
                pyboy.tick()
                pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
        
        pyboy.stop()
        
        logger.info("Test completed successfully")
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    test_zelda_rom()
