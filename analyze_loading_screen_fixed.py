import os
import sys
import numpy as np
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time
from PIL import Image
import matplotlib.pyplot as plt

def analyze_loading_screen():
    """
    Analyze the Tetris loading screen issue by testing different initialization sequences.
    """
    print("Analyzing Tetris loading screen issue...")
    
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
        os.makedirs("loading_screen_analysis", exist_ok=True)
        
        pyboy = PyBoy(rom_path, window="SDL2", scale=3)
        pyboy.set_emulation_speed(1)  # Set to normal speed for visualization
        
        print(f"ROM title: {pyboy.cartridge_title}")
        
        tetris = pyboy.game_wrapper
        print(f"Game wrapper type: {type(tetris)}")
        print(f"Game wrapper methods: {[m for m in dir(tetris) if not m.startswith('_')]}")
        print(f"PyBoy attributes: {[m for m in dir(pyboy) if not m.startswith('_')]}")
        
        def save_screenshot(filename):
            try:
                screen = pyboy.screen
                if screen is not None:
                    print(f"Screen attributes: {[m for m in dir(screen) if not m.startswith('_')]}")
                    
                    if hasattr(screen, 'ndarray'):
                        try:
                            screen_buffer = screen.ndarray
                            if callable(screen_buffer):
                                screen_buffer = screen_buffer()
                            img = Image.fromarray(screen_buffer)
                            img.save(filename)
                            print(f"Screenshot saved to {filename} using ndarray")
                            return True
                        except Exception as e:
                            print(f"Error using ndarray: {e}")
                    
                    if hasattr(screen, 'image'):
                        try:
                            img_func = screen.image
                            if callable(img_func):
                                img = img_func()
                            else:
                                img = img_func
                            img.save(filename)
                            print(f"Screenshot saved to {filename} using image")
                            return True
                        except Exception as e:
                            print(f"Error using image: {e}")
                    
                    print(f"Could not save screenshot to {filename} - no suitable method found")
                    return False
                else:
                    print(f"Failed to save screenshot to {filename} - screen is None")
                    return False
            except Exception as e:
                print(f"Error saving screenshot to {filename}: {e}")
                return False
        
        save_screenshot("loading_screen_analysis/initial_state.png")
        
        print("\nTesting initialization sequence...")
        print("1. Calling start_game(timer_div=0x00)")
        tetris.start_game(timer_div=0x00)
        
        save_screenshot("loading_screen_analysis/after_start_game.png")
        
        print("2. Advancing 120 frames")
        for i in range(120):
            pyboy.tick()
            if i % 30 == 0:
                print(f"  - Advanced {i} frames")
                save_screenshot(f"loading_screen_analysis/frame_{i}.png")
        
        print("3. Pressing START button")
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        save_screenshot("loading_screen_analysis/after_start_button.png")
        
        print("4. Advancing 60 more frames")
        for i in range(60):
            pyboy.tick()
            if i % 20 == 0:
                print(f"  - Advanced {i} more frames")
                save_screenshot(f"loading_screen_analysis/after_start_{i}.png")
        
        print("5. Pressing START button again")
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        save_screenshot("loading_screen_analysis/after_second_start.png")
        
        print("6. Advancing 60 more frames")
        for i in range(60):
            pyboy.tick()
            if i % 20 == 0:
                print(f"  - Advanced {i} more frames after second START")
                save_screenshot(f"loading_screen_analysis/after_second_start_{i}.png")
        
        print("7. Pressing A button")
        pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
        
        save_screenshot("loading_screen_analysis/after_a_button.png")
        
        print("8. Advancing 60 more frames")
        for i in range(60):
            pyboy.tick()
            if i % 20 == 0:
                print(f"  - Advanced {i} more frames after A button")
                save_screenshot(f"loading_screen_analysis/after_a_button_{i}.png")
        
        try:
            screen = pyboy.screen
            if hasattr(screen, 'ndarray'):
                screen_buffer = screen.ndarray
                if callable(screen_buffer):
                    screen_buffer = screen_buffer()
                
                center_region = screen_buffer[120:300, 80:240]
                white_pixels = np.sum(center_region > 200)
                print(f"\nWhite pixel analysis (game over detection):")
                print(f"White pixels in center region: {white_pixels}")
                print(f"Would trigger game over detection: {white_pixels > 500}")
        except Exception as e:
            print(f"Error analyzing white pixels: {e}")
        
        save_screenshot("loading_screen_analysis/final_state.png")
        
        print("\nCheck the loading_screen_analysis folder for screenshots of the initialization process.")
        input("Press Enter to exit...")
        
        pyboy.stop()
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        if 'pyboy' in locals():
            pyboy.stop()

if __name__ == "__main__":
    analyze_loading_screen()
