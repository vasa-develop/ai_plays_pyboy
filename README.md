# AI Plays PyBoy

A Python project for running Game Boy games using PyBoy emulator. This project is set up to play Tetris on the Game Boy emulator.

## Prerequisites

- Python 3.8 or higher
- macOS (tested on Apple Silicon M1)
- Game Boy ROM files (not included in this repository)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai_plays_pyboy.git
cd ai_plays_pyboy
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Add your Game Boy ROM files to the project directory:
   - Place your ROM files (e.g., `tetris.gb`) in the project root
   - Note: ROM files are not included in this repository due to copyright restrictions

## Usage

To play Tetris:

```bash
python3 play_tetris.py
```

### Controls

- **Arrow Keys**: Move piece left/right
- **Up Arrow**: Rotate piece
- **Down Arrow**: Drop piece faster
- **Space**: Drop piece instantly
- **Escape**: Quit game

Additional PyBoy controls:
- **F11**: Toggle fullscreen
- **D**: Debug mode
- **Z**: Save state
- **X**: Load state
- **I**: Toggle screen recording
- **O**: Save screenshot

## Project Structure

- `play_tetris.py`: Main script to run the game
- `requirements.txt`: Python dependencies
- `*.gb`: Game Boy ROM files (not included)
- `*.ram`: Save state files (generated automatically)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [PyBoy](https://github.com/Baekalfen/PyBoy) - Game Boy emulator
- Nintendo - Tetris (Game Boy version) 