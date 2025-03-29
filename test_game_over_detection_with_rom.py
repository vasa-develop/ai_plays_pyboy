import os
import sys
import numpy as np
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time
from PIL import Image
import matplotlib.pyplot as plt

def test_game_over_detection_with_rom():
    """
    Test the game over detection logic with the actual ROM file.
    """
    print("Testing game over detection with ROM file...")
    
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
        os.makedirs("game_over_test", exist_ok=True)
        
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
        
        save_screenshot("game_over_test/initial_state.png")
        
        print("\nInitializing game...")
        
        is_tetris_dx = "DX" in pyboy.cartridge_title.upper()
        
        if is_tetris_dx:
            print("Detected Tetris DX (Game Boy Color ROM)")
            
            tetris.start_game(timer_div=0x00)
            
            for i in range(150):
                pyboy.tick()
            
            for j in range(3):
                pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
                pyboy.tick()
                pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
                
                for i in range(60):
                    pyboy.tick()
            
            pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
            pyboy.tick()
            pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
            
            for i in range(90):
                pyboy.tick()
        else:
            tetris.start_game(timer_div=0x00)
            
            for i in range(120):
                pyboy.tick()
            
            pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
            pyboy.tick()
            pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
            
            for i in range(60):
                pyboy.tick()
            
            pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
            pyboy.tick()
            pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
            
            for i in range(30):
                pyboy.tick()
            
            pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
            pyboy.tick()
            pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
            
            for i in range(60):
                pyboy.tick()
        
        save_screenshot("game_over_test/game_initialized.png")
        
        print("\nTesting game over detection methods...")
        
        if hasattr(tetris, 'game_over'):
            if callable(tetris.game_over):
                try:
                    game_over = tetris.game_over()
                    print(f"Game over status (method): {game_over}")
                except Exception as e:
                    print(f"Error calling game_over method: {e}")
            else:
                print(f"Game over status (attribute): {tetris.game_over}")
        else:
            print("game_over method/attribute not available")
        
        if hasattr(tetris, 'tilemap_background'):
            try:
                tile_value = tetris.tilemap_background[2, 0]
                print(f"Tilemap background tile at [2, 0]: {tile_value}")
                print(f"Is game over tile (135): {tile_value == 135}")
            except Exception as e:
                print(f"Error checking tilemap background: {e}")
        else:
            print("tilemap_background not available")
        
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
        
        print("\nSimulating game over...")
        
        for i in range(100):
            pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
            pyboy.tick()
            pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
            
            if i % 10 == 0:
                save_screenshot(f"game_over_test/gameplay_{i}.png")
                
                if hasattr(tetris, 'game_over') and (callable(tetris.game_over) and tetris.game_over() or not callable(tetris.game_over) and tetris.game_over):
                    print(f"Game over detected at iteration {i}")
                    break
                
                try:
                    screen_buffer = screen.ndarray()
                    center_region = screen_buffer[120:300, 80:240]
                    white_pixels = np.sum(center_region > 200)
                    black_pixels = np.sum(center_region < 50)
                    white_to_black_ratio = white_pixels / (black_pixels + 1)
                    
                    if white_pixels > 500 and white_pixels < 5000 and white_to_black_ratio > 0.05 and white_to_black_ratio < 0.3:
                        print(f"Game over screen detected at iteration {i}")
                        break
                except Exception as e:
                    print(f"Error analyzing screen: {e}")
        
        save_screenshot("game_over_test/final_state.png")
        
        print("\nCheck the game_over_test folder for screenshots of the game over detection process.")
        
        pyboy.stop()
        
    except Exception as e:
        print(f"Error during test: {e}")
        if 'pyboy' in locals():
            pyboy.stop()

if __name__ == "__main__":
    test_game_over_detection_with_rom()
