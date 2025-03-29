import os
import sys
import logging
import numpy as np
from pyboy import PyBoy
from pyboy.utils import WindowEvent

class TetrisAI:
    """AI that plays Tetris on PyBoy emulator"""
    
    def __init__(self, pyboy, tetris):
        self.pyboy = pyboy
        self.tetris = tetris
        self.logger = logging.getLogger(__name__)
        
    def get_board_state(self):
        """Get the current state of the Tetris board"""
        board_state = np.zeros((18, 10), dtype=np.int8)
        
        for y in range(18):
            for x in range(10):
                if self.tetris.game_area()[y][x]:
                    board_state[y][x] = 1
                    
        return board_state
    
    def get_current_piece(self):
        """Get the current falling piece"""
        return self.tetris.next_tetromino()
    
    def evaluate_move(self, board, x_pos, rotation):
        """Evaluate a potential move based on heuristics"""
        return 0
    
    def find_best_move(self):
        """Find the best move for the current piece"""
        board = self.get_board_state()
        current_piece = self.get_current_piece()
        
        best_score = float('-inf')
        best_x = 0
        best_rotation = 0
        
        for x in range(10):
            for rotation in range(4):  # Most pieces have 4 rotations
                score = self.evaluate_move(board, x, rotation)
                if score > best_score:
                    best_score = score
                    best_x = x
                    best_rotation = rotation
        
        return best_x, best_rotation
    
    def execute_move(self, target_x, target_rotation):
        """Execute the move by sending button presses"""
        for _ in range(target_rotation):
            self.pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
            self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
            self.pyboy.tick()
        
        current_x = 5  # Assuming pieces start at center
        
        if target_x < current_x:
            for _ in range(current_x - target_x):
                self.pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT)
                self.pyboy.tick()
                self.pyboy.send_input(WindowEvent.RELEASE_ARROW_LEFT)
                self.pyboy.tick()
        else:
            for _ in range(target_x - current_x):
                self.pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
                self.pyboy.tick()
                self.pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
                self.pyboy.tick()
        
        self.pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
        for _ in range(20):  # Hold down for a while to ensure it drops
            self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
        self.pyboy.tick()
    
    def play_game(self):
        """Main game loop for the AI"""
        self.logger.info("AI starting to play Tetris")
        
        while True:
            target_x, target_rotation = self.find_best_move()
            self.execute_move(target_x, target_rotation)
            
            for _ in range(10):
                self.pyboy.tick()
            
            if self.tetris.score() == 0 and self.tetris.level() == 0:
                self.logger.info("Game over! Final score: %s", self.tetris.score())
                break

def play_tetris_ai(rom_path="tetris.gb"):
    """Run the Tetris AI with the specified ROM"""
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    logger.debug("Starting PyBoy with Tetris AI...")
    
    if not os.path.exists(rom_path):
        logger.error(f"ROM file not found: {rom_path}")
        logger.info("Please download a Tetris ROM and place it in the project directory")
        return
    
    try:
        pyboy = PyBoy(rom_path, window_type="SDL2", scale=3)
        pyboy.set_emulation_speed(0)
        
        if pyboy.cartridge_title != "TETRIS":
            logger.error("The provided ROM is not Tetris")
            pyboy.stop()
            return
        
        tetris = pyboy.game_wrapper()
        tetris.start_game()
        
        ai = TetrisAI(pyboy, tetris)
        ai.play_game()
        
        pyboy.stop()
        
    except KeyboardInterrupt:
        logger.info("Game stopped by user")
        if 'pyboy' in locals():
            pyboy.stop()
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        if 'pyboy' in locals():
            pyboy.stop()
        raise

if __name__ == "__main__":
    play_tetris_ai()
