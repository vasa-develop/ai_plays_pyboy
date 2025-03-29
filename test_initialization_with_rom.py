import os
import sys
import numpy as np
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time
from PIL import Image
import matplotlib.pyplot as plt

def test_initialization_with_rom():
    """
    Test the initialization sequence with the actual ROM file to verify it skips loading screens.
    """
    print("Testing initialization sequence with ROM file...")
    
    rom_paths = ["tetris.gbc", "tetris.gb"]
    rom_path = None
    
    for path in rom_paths:
        if os.path.exists(path):
            rom_path = path
            print(f"Found ROM file: {rom_path}")
            break
    
    if rom_path is None:
        print("ROM file not found. Please ensure tetris.gb or tetris.gbc is in the current directory.")
        return
    
    try:
        os.makedirs("initialization_test", exist_ok=True)
        
        pyboy = PyBoy(rom_path, window="SDL2", scale=3)
        pyboy.set_emulation_speed(1)  # Set to normal speed for visualization
        
        print(f"ROM title: {pyboy.cartridge_title}")
        
        tetris = pyboy.game_wrapper
        print(f"Game wrapper type: {type(tetris)}")
        
        def save_screenshot(filename):
            screen = pyboy.screen
            if hasattr(screen, 'image'):
                img_func = screen.image
                if callable(img_func):
                    img = img_func()
                else:
                    img = img_func
                img.save(filename)
                print(f"Screenshot saved to {filename}")
                return True
            return False
        
        save_screenshot("initialization_test/initial_state.png")
        
        print("\nExecuting initialization sequence...")
        
        print("1. Calling start_game(timer_div=0x00)")
        tetris.start_game(timer_div=0x00)
        save_screenshot("initialization_test/after_start_game.png")
        
        print("2. Advancing 120 frames")
        for i in range(120):
            pyboy.tick()
            if i % 30 == 0:
                save_screenshot(f"initialization_test/frame_{i}.png")
        
        print("3. Pressing START button")
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        save_screenshot("initialization_test/after_start_button.png")
        
        print("4. Advancing 60 more frames")
        for i in range(60):
            pyboy.tick()
            if i % 20 == 0:
                save_screenshot(f"initialization_test/after_start_{i}.png")
        
        print("5. Pressing START button again")
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        save_screenshot("initialization_test/after_second_start.png")
        
        print("6. Advancing 30 more frames")
        for i in range(30):
            pyboy.tick()
            if i % 10 == 0:
                save_screenshot(f"initialization_test/after_second_start_{i}.png")
        
        print("7. Pressing A button")
        pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
        save_screenshot("initialization_test/after_a_button.png")
        
        print("8. Advancing 60 more frames")
        for i in range(60):
            pyboy.tick()
            if i % 20 == 0:
                save_screenshot(f"initialization_test/after_a_button_{i}.png")
        
        print("9. Checking game state")
        save_screenshot("initialization_test/final_state.png")
        
        if hasattr(tetris, 'game_over'):
            if callable(tetris.game_over):
                game_over = tetris.game_over()
                print(f"Game over status (method): {game_over}")
            else:
                print(f"Game over status (attribute): {tetris.game_over}")
        
        if hasattr(tetris, 'tilemap_background'):
            try:
                tile_value = tetris.tilemap_background[2, 0]
                print(f"Tilemap background tile at [2, 0]: {tile_value}")
                print(f"Is game over tile (135): {tile_value == 135}")
            except Exception as e:
                print(f"Error checking tilemap background: {e}")
        
        try:
            screen = pyboy.screen
            if hasattr(screen, 'ndarray'):
                screen_buffer = screen.ndarray
                if callable(screen_buffer):
                    screen_buffer = screen_buffer()
                
                center_region = screen_buffer[120:300, 80:240]
                white_pixels = np.sum(center_region > 200)
                black_pixels = np.sum(center_region < 50)
                white_to_black_ratio = white_pixels / (black_pixels + 1)
                
                print(f"Screen analysis: white={white_pixels}, black={black_pixels}, ratio={white_to_black_ratio:.2f}")
                print(f"Would trigger game over detection: {white_pixels > 500 and white_pixels < 5000 and white_to_black_ratio > 0.05 and white_to_black_ratio < 0.3}")
        except Exception as e:
            print(f"Error analyzing screen: {e}")
        
        print("\nCheck the initialization_test folder for screenshots of the initialization process.")
        
        pyboy.stop()
        
    except Exception as e:
        print(f"Error during test: {e}")
        if 'pyboy' in locals():
            pyboy.stop()

if __name__ == "__main__":
    test_initialization_with_rom()
