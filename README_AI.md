# AI Plays Tetris with PyBoy

This project implements an AI that plays Tetris on the Game Boy emulator PyBoy. The AI analyzes the game state and makes decisions on where to place pieces to maximize score.

## Implementation Details

The AI implementation consists of:

1. **tetris_ai.py**: Contains the TetrisAI class that implements the AI logic
2. **play_tetris.py**: Main script that runs the game with AI

## How the AI Works

The AI follows these steps to play Tetris:

1. Observes the current game state (board configuration, current piece)
2. Evaluates possible moves (positions and rotations)
3. Selects the best move based on heuristics
4. Executes the move by sending button presses to the emulator

## Heuristics

The current implementation uses a simple placeholder heuristic. For a more advanced AI, you could implement heuristics that consider:

- Height of the stack
- Number of holes (empty spaces with blocks above them)
- Line completions
- Bumpiness (height differences between adjacent columns)
- Well depth (deep holes perfect for I-pieces)

## Requirements

- Python 3.8 or higher
- PyBoy 2.5.1
- NumPy 1.21.0 or higher
- Tetris ROM file (not included due to copyright)

## Usage

1. Place a Tetris ROM file named `tetris.gb` in the project directory
2. Run the AI:

```bash
python play_tetris.py
```

## Future Improvements

- Implement more sophisticated evaluation heuristics
- Add machine learning capabilities
- Optimize piece placement decisions
- Add visualization of AI decision-making process

## License

This project is licensed under the MIT License.
