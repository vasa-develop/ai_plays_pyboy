# Zelda AI Implementation

This document provides a detailed overview of the AI implementation for playing "The Legend of Zelda: Link's Awakening" on the Game Boy using PyBoy emulator and reinforcement learning techniques.

## Project Structure

The Zelda AI implementation consists of the following components:

1. **PyBoy Wrapper (`gym_wrapper/zelda_env.py`)**: A Gymnasium-compatible environment that interfaces with the PyBoy emulator to control Zelda gameplay.

2. **State Preprocessor (`zelda_state_preprocessor.py`)**: Extracts and processes game state information from the emulator's memory.

3. **Reward Function (`zelda_reward_function.py`)**: Defines the reward structure to guide the AI's learning process.

4. **RL Agent (`zelda_rl_agent.py`)**: Implements the reinforcement learning algorithms and training process.

5. **Training Script (`train_zelda_agent.py`)**: Provides a command-line interface for training the AI.

6. **Evaluation Script (`evaluate_zelda_agent.py`)**: Allows testing and visualization of the trained AI's performance.

7. **Testing Script (`test_zelda_ai.py`)**: Provides utilities for testing different components of the Zelda AI implementation.

## Environment Wrapper

The Zelda environment wrapper (`ZeldaPyBoyEnv`) provides a standardized interface between the PyBoy emulator and reinforcement learning algorithms:

```python
class ZeldaPyBoyEnv(gym.Env):
    """PyBoy Zelda: Link's Awakening environment that follows the Gymnasium interface."""
    
    ACTIONS = [
        WindowEvent.PRESS_ARROW_UP,     # Move up
        WindowEvent.PRESS_ARROW_RIGHT,  # Move right
        WindowEvent.PRESS_ARROW_LEFT,   # Move left
        WindowEvent.PRESS_ARROW_DOWN,   # Move down
        WindowEvent.PRESS_BUTTON_A,     # A button (action/interact)
        WindowEvent.PRESS_BUTTON_B,     # B button (sword/cancel)
        WindowEvent.PRESS_BUTTON_START, # Start button (menu)
        WindowEvent.PRESS_BUTTON_SELECT,# Select button (item swap)
        None,                           # No action
    ]
```

The environment provides:
- A discrete action space with 9 possible actions
- A complex observation space including screen pixels, health, position, map position, rupees, and inventory
- Methods for calculating rewards based on game progress
- Game state tracking and episode management

## State Representation

The state preprocessor (`ZeldaStatePreprocessor`) extracts relevant information from the game's memory:

```python
class ZeldaStatePreprocessor:
    """Preprocesses the Zelda game state for use with reinforcement learning algorithms."""
    
    def __init__(self, pyboy_instance=None):
        self.pyboy = pyboy_instance
        
        self.ADDR_HEALTH = 0xDB5D        # Player's health
        self.ADDR_MAX_HEALTH = 0xDB5E    # Player's maximum health
        self.ADDR_RUPEES = 0xDB8C        # Player's rupee count
        self.ADDR_PLAYER_X = 0xD362      # Player's X position on screen
        self.ADDR_PLAYER_Y = 0xD363      # Player's Y position on screen
        self.ADDR_MAP_X = 0xD35E         # Current map X position
        self.ADDR_MAP_Y = 0xD35F         # Current map Y position
        # ... other memory addresses
```

The preprocessor provides methods for:
- Reading memory values from specific addresses
- Normalizing and vectorizing game state information
- Detecting game progress and state changes
- Creating CNN-compatible state representations

## Reward Function

The reward function (`ZeldaRewardFunction`) defines the learning signal for the AI:

```python
class ZeldaRewardFunction:
    """Reward function for the Zelda: Link's Awakening environment."""
    
    def __init__(self):
        # Reward weights for different aspects of gameplay
        self.weights = {
            'health_gain': 2.0,      # Reward for gaining health
            'health_loss': -1.0,     # Penalty for losing health
            'rupee_gain': 0.1,       # Reward for collecting rupees
            'item_collect': 5.0,     # Reward for collecting new items
            'enemy_defeat': 2.0,     # Reward for defeating enemies
            'room_explore': 3.0,     # Reward for exploring new rooms
            'movement': 0.01,        # Small reward for movement
            'time_penalty': -0.001,  # Small penalty for each step
            'death_penalty': -10.0,  # Large penalty for dying
            'progress_reward': 10.0, # Large reward for game progress
            'puzzle_solve': 5.0      # Reward for solving puzzles
        }
```

The reward function balances:
- Exploration incentives (room discovery, movement)
- Combat rewards (defeating enemies)
- Collection rewards (items, rupees, health)
- Progress rewards (completing objectives)
- Penalties (taking damage, dying, time)

## RL Agent

The RL agent (`ZeldaRLAgent`) implements the training and inference logic:

```python
class ZeldaRLAgent:
    """Reinforcement learning agent for playing Zelda: Link's Awakening."""
    
    def __init__(self, env=None, algorithm="ppo", model_path=None, log_dir="./zelda_logs"):
        self.env = env
        self.algorithm = algorithm.lower()
        self.model_path = model_path
        self.log_dir = log_dir
        self.model = None
```

The agent supports:
- Multiple RL algorithms (PPO, A2C, DQN)
- Training with customizable parameters
- Evaluation and visualization
- Model saving and loading
- Delayed gameplay for visualization

## Challenges and Considerations

Implementing an AI for Zelda presents several unique challenges compared to Tetris:

1. **Complex State Space**: Zelda has a much larger state space with many different screens, items, and game states.

2. **Long-term Planning**: Success in Zelda requires long-term planning and memory of previous locations and actions.

3. **Sparse Rewards**: Many important rewards in Zelda (completing dungeons, finding items) are sparse and delayed.

4. **Exploration vs. Exploitation**: The AI must balance exploring new areas with exploiting known rewards.

5. **Memory Mapping**: Identifying the correct memory addresses for game state information requires reverse engineering.

6. **Multi-objective Learning**: The AI must learn to navigate, fight enemies, solve puzzles, and manage inventory simultaneously.

## Future Improvements

Potential areas for improvement include:

1. **Memory Mapping**: Refine the memory address mapping for more accurate game state extraction.

2. **Hierarchical RL**: Implement hierarchical reinforcement learning to handle different aspects of gameplay.

3. **Curriculum Learning**: Start with simpler tasks and gradually increase complexity.

4. **Imitation Learning**: Use human gameplay demonstrations to bootstrap the learning process.

5. **Meta-learning**: Develop meta-learning approaches to help the AI adapt to different game scenarios.

## Usage

### Training

```bash
python train_zelda_agent.py --rom zelda.gb --algorithm ppo --timesteps 1000000
```

### Evaluation

```bash
python evaluate_zelda_agent.py --rom zelda.gb --model ./zelda_logs/zelda_ppo_final.zip --render --delay 0.5
```

### Testing

```bash
python test_zelda_ai.py --rom zelda.gb --mode env
```

## Comparison with Tetris AI

The Zelda AI implementation builds on the foundation of the Tetris AI but addresses several additional challenges:

1. **Navigation**: Unlike Tetris, Zelda requires spatial navigation and exploration.

2. **Combat**: The AI must learn combat strategies against different enemy types.

3. **Puzzle Solving**: Zelda contains puzzles that require specific sequences of actions.

4. **Inventory Management**: The AI must learn to select and use appropriate items.

5. **Quest Progression**: The AI needs to understand and follow the game's quest structure.

These differences necessitate a more sophisticated reward function and state representation compared to the Tetris implementation.
