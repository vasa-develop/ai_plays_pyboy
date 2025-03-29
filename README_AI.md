# AI Plays Tetris with PyBoy: Hybrid Approach

This project implements an AI that plays Tetris on the Game Boy emulator PyBoy using a hybrid approach that combines direct game state access through PyBoy's game wrappers with reinforcement learning techniques.

## Table of Contents

1. [Overview](#overview)
2. [Hybrid Approach](#hybrid-approach)
3. [Implementation Details](#implementation-details)
   - [PyBoy-Gym Environment Wrapper](#pyboy-gym-environment-wrapper)
   - [State Representation and Preprocessing](#state-representation-and-preprocessing)
   - [Reward Function Design](#reward-function-design)
   - [RL Agent Architecture](#rl-agent-architecture)
   - [Custom Wrappers](#custom-wrappers)
4. [Training Process](#training-process)
5. [Performance Evaluation](#performance-evaluation)
6. [Challenges and Solutions](#challenges-and-solutions)
7. [Future Improvements](#future-improvements)
8. [Project Structure](#project-structure)
9. [Requirements](#requirements)
10. [Usage](#usage)

## Overview

The AI agent for playing Tetris uses a hybrid approach that combines direct game state access through PyBoy's game wrappers with reinforcement learning techniques. This approach leverages the benefits of both methods:

1. **Game Wrapper Access**: Provides direct access to game state information like the current board, score, level, and upcoming pieces.
2. **Reinforcement Learning**: Enables the agent to learn optimal strategies through experience and improve over time.

## Hybrid Approach

The hybrid approach consists of the following components:

1. **Gym Environment Wrapper**: Wraps the PyBoy Tetris game in a Gymnasium-compatible environment.
2. **State Preprocessor**: Extracts and processes relevant features from the game state.
3. **Reward Function**: Defines the reward signal for the RL agent.
4. **RL Agent**: Implements the reinforcement learning algorithm.
5. **Custom Wrappers**: Additional environment wrappers for feature extraction and reward shaping.

The main advantage of this hybrid approach is that it combines the precision of direct game state access with the learning capabilities of reinforcement learning. This allows the agent to make decisions based on a rich set of game features while still learning optimal strategies through experience.

## Implementation Details

### PyBoy-Gym Environment Wrapper

The PyBoy-Gym environment wrapper (`TetrisPyBoyEnv`) provides a standard Gymnasium interface for the Tetris game running on PyBoy. This allows the use of standard RL libraries like Stable Baselines3.

Key features of the environment wrapper:

- **Observation Space**: Provides game state information including the board, score, level, and lines cleared.
- **Action Space**: Maps actions to Tetris controls (move left, move right, rotate, drop).
- **Step Function**: Advances the game by one step and returns the new state, reward, and done flag.
- **Reset Function**: Resets the game to the initial state.
- **Render Function**: Renders the game for visualization.

Implementation example:

```python
class TetrisPyBoyEnv(gym.Env):
    """
    Gymnasium environment for Tetris on PyBoy.
    """
    
    def __init__(self, rom_path="tetris.gb", render_mode="human"):
        # Initialize PyBoy
        self.pyboy = PyBoy(rom_path, window_type="headless" if render_mode == "headless" else "SDL2")
        self.pyboy.set_emulation_speed(0)
        
        # Initialize Tetris game wrapper
        self.tetris = self.pyboy.game_wrapper()
        self.tetris.start_game()
        
        # Define action and observation spaces
        self.action_space = gym.spaces.Discrete(5)  # No-op, Left, Right, Rotate, Drop
        
        # Observation space includes the board state and game info
        self.observation_space = gym.spaces.Dict({
            'board': gym.spaces.Box(low=0, high=1, shape=(20, 10), dtype=np.uint8),
            'score': gym.spaces.Box(low=0, high=np.inf, shape=(1,), dtype=np.float32),
            'level': gym.spaces.Box(low=0, high=np.inf, shape=(1,), dtype=np.float32),
            'lines': gym.spaces.Box(low=0, high=np.inf, shape=(1,), dtype=np.float32),
            'next_piece': gym.spaces.Box(low=0, high=7, shape=(1,), dtype=np.uint8)
        })
```

### State Representation and Preprocessing

The state preprocessor (`TetrisStatePreprocessor`) extracts and processes relevant features from the game state to create a more informative representation for the RL agent.

Key features extracted:

1. **Board State**: The current configuration of the Tetris board.
2. **Height Profile**: The height of each column on the board.
3. **Holes**: Empty cells with filled cells above them.
4. **Bumpiness**: The sum of differences between adjacent column heights.
5. **Aggregate Height**: The sum of all column heights.
6. **Number of Lines Cleared**: The total number of lines cleared.
7. **Score**: The current game score.
8. **Level**: The current game level.
9. **Next Piece**: The type of the next piece (if available).

Implementation example:

```python
class TetrisStatePreprocessor:
    """
    Preprocesses the Tetris game state into a feature vector.
    """
    
    def preprocess(self, observation):
        """
        Preprocess the observation into a feature vector.
        """
        if 'board' not in observation:
            return np.zeros(20, dtype=np.float32)
        
        board = observation['board']
        score = observation.get('score', [0])[0]
        level = observation.get('level', [0])[0]
        lines = observation.get('lines', [0])[0]
        
        # Extract board features
        height_profile = self._get_height_profile(board)
        holes = self._count_holes(board, height_profile)
        bumpiness = self._calculate_bumpiness(height_profile)
        aggregate_height = sum(height_profile)
        
        # Create feature vector
        features = np.array([
            score,
            lines,
            level,
            holes,
            bumpiness,
            aggregate_height,
            max(height_profile) if len(height_profile) > 0 else 0,
            min(height_profile) if len(height_profile) > 0 else 0,
            np.std(height_profile) if len(height_profile) > 0 else 0,
            self._count_complete_lines(board),
            *height_profile  # Include all column heights
        ], dtype=np.float32)
        
        return features
```

### Reward Function Design

The reward function (`TetrisRewardFunction`) defines the reward signal for the RL agent. It is designed to encourage behaviors that lead to high scores and long gameplay.

Key components of the reward function:

1. **Score Increase**: Reward for increasing the game score.
2. **Lines Cleared**: Reward for clearing lines, with higher rewards for clearing multiple lines at once.
3. **Level Increase**: Reward for advancing to higher levels.
4. **Board State Penalties**: Penalties for creating holes, increasing bumpiness, and increasing the aggregate height.
5. **Game Over Penalty**: Penalty for ending the game.
6. **Survival Reward**: Small reward for surviving each step.

The adaptive reward function (`AdaptiveRewardFunction`) adjusts the weights of these components based on the game progress, encouraging different behaviors at different stages of the game.

Implementation example:

```python
class TetrisRewardFunction:
    """
    Reward function for the Tetris environment.
    """
    
    def __init__(self):
        """Initialize the reward function."""
        self.prev_score = 0
        self.prev_lines = 0
        self.prev_level = 0
        
        self.weights = {
            'score': 1.0,
            'lines': 10.0,
            'tetris': 20.0,
            'holes': -0.5,
            'bumpiness': -0.2,
            'height': -0.1,
            'game_over': -50.0,
            'survival': 0.01
        }
    
    def calculate_reward(self, prev_obs, obs, info, done):
        """
        Calculate the reward based on the current and previous observations.
        """
        current_score = info.get('score', 0)
        current_lines = info.get('lines', 0)
        current_level = info.get('level', 0)
        
        score_reward = (current_score - self.prev_score) * self.weights['score']
        
        lines_cleared = current_lines - self.prev_lines
        lines_reward = 0
        if lines_cleared > 0:
            lines_reward = lines_cleared * self.weights['lines']
            
            if lines_cleared == 4:
                lines_reward += self.weights['tetris']
        
        level_reward = (current_level - self.prev_level) * 20.0
        
        board_reward = self._calculate_board_reward(prev_obs, obs)
        
        game_over_penalty = self.weights['game_over'] if done else 0
        
        survival_reward = self.weights['survival']
        
        total_reward = (
            score_reward +
            lines_reward +
            level_reward +
            board_reward +
            game_over_penalty +
            survival_reward
        )
        
        return total_reward
```

### RL Agent Architecture

The RL agent (`TetrisRLAgent`) implements the reinforcement learning algorithm for playing Tetris. It supports multiple algorithms from the Stable Baselines3 library, including PPO, A2C, and DQN.

Key components of the RL agent:

1. **Policy Network**: Neural network that maps states to actions.
2. **Value Network**: Neural network that estimates the value of states.
3. **Algorithm**: Reinforcement learning algorithm (PPO, A2C, or DQN).
4. **Training Loop**: Process for updating the policy based on experience.
5. **Evaluation**: Methods for evaluating the agent's performance.

Implementation example:

```python
class TetrisRLAgent:
    """
    Reinforcement learning agent for playing Tetris.
    """
    
    def __init__(self, env, algorithm="ppo", model_path=None, log_dir="./tetris_logs"):
        """
        Initialize the RL agent.
        """
        self.env = env
        self.algorithm = algorithm
        self.model_path = model_path
        self.log_dir = log_dir
        self.model = None
    
    def create_model(self):
        """
        Create or load a reinforcement learning model.
        """
        policy_kwargs = dict(
            net_arch=[128, 128, dict(pi=[64, 32], vf=[64, 32])]
        )
        
        if self.algorithm == "ppo":
            self.model = PPO(
                "MlpPolicy",
                self.env,
                policy_kwargs=policy_kwargs,
                verbose=1,
                tensorboard_log=os.path.join(self.log_dir, "tensorboard")
            )
        elif self.algorithm == "a2c":
            self.model = A2C(
                "MlpPolicy",
                self.env,
                policy_kwargs=policy_kwargs,
                verbose=1,
                tensorboard_log=os.path.join(self.log_dir, "tensorboard")
            )
        elif self.algorithm == "dqn":
            self.model = DQN(
                "MlpPolicy",
                self.env,
                policy_kwargs=policy_kwargs,
                verbose=1,
                tensorboard_log=os.path.join(self.log_dir, "tensorboard")
            )
        
        if self.model_path and os.path.exists(self.model_path):
            self.model = self.model.load(self.model_path, env=self.env)
        
        return self.model
```

### Custom Wrappers

The custom wrappers enhance the Tetris environment with additional functionality:

1. **TetrisFeatureWrapper**: Transforms raw observations into feature vectors.
2. **TetrisRewardWrapper**: Enhances the reward function with additional components.
3. **VecTetrisFeatureWrapper**: Applies feature extraction to vectorized environments.

These wrappers make it easier to train the RL agent by providing a more informative state representation and a more effective reward signal.

## Training Process

The training process involves the following steps:

1. **Environment Setup**: Create and initialize the Tetris environment.
2. **Agent Setup**: Create and initialize the RL agent.
3. **Training Loop**: Train the agent for a specified number of timesteps.
4. **Checkpointing**: Save the model at regular intervals.
5. **Evaluation**: Evaluate the agent's performance during training.

The training script (`train_rl_agent.py`) provides a flexible way to train the RL agent with various configurations.

Example training command:

```bash
python train_rl_agent.py --rom tetris.gb --algorithm ppo --timesteps 100000
```

## Performance Evaluation

The performance evaluation process involves the following steps:

1. **Environment Setup**: Create and initialize the Tetris environment.
2. **Agent Setup**: Load the trained RL agent.
3. **Evaluation Loop**: Run the agent for a specified number of episodes.
4. **Metrics Collection**: Collect performance metrics such as score, lines cleared, and level.
5. **Analysis**: Analyze the collected metrics and generate visualizations.

The evaluation script (`evaluate_rl_agent.py`) and performance analysis script (`performance_analysis.py`) provide tools for evaluating the agent's performance and analyzing the results.

Example evaluation command:

```bash
python evaluate_rl_agent.py --rom tetris.gb --model ./tetris_logs/model.zip
```

## Challenges and Solutions

During the implementation of the AI agent, several challenges were encountered and addressed:

1. **Game State Extraction**: Extracting the game state from PyBoy required understanding the internal structure of the Tetris game wrapper. This was addressed by studying the PyBoy documentation and example code.

2. **Feature Engineering**: Determining the most relevant features for the RL agent required experimentation. The final feature set includes board state, height profile, holes, bumpiness, and other metrics that provide a comprehensive representation of the game state.

3. **Reward Function Design**: Designing an effective reward function was challenging due to the sparse nature of rewards in Tetris. The solution was to use a combination of immediate rewards (score, lines cleared) and shaping rewards (penalties for holes, bumpiness, etc.) to guide the agent's learning.

4. **Training Stability**: Reinforcement learning algorithms can be unstable during training. This was addressed by using stable algorithms like PPO and implementing checkpointing to save the model at regular intervals.

5. **Performance Evaluation**: Evaluating the agent's performance required defining appropriate metrics and visualization tools. The solution was to implement a comprehensive performance analysis framework that collects and analyzes various metrics.

## Future Improvements

Several potential improvements could enhance the AI agent's performance:

1. **Advanced Feature Engineering**: Incorporate more sophisticated features such as well detection, pattern recognition, and piece-specific strategies.

2. **Curriculum Learning**: Implement a curriculum learning approach where the agent starts with simpler tasks and gradually progresses to more complex ones.

3. **Multi-Agent Training**: Train multiple agents with different strategies and combine their policies to create a more robust agent.

4. **Meta-Learning**: Implement meta-learning techniques to enable the agent to adapt to different game conditions and strategies.

5. **Visual Input**: Extend the agent to learn directly from visual input (screenshots) rather than relying on the game wrapper, which would make it more generalizable to other games.

6. **Real-Time Adaptation**: Implement techniques for real-time adaptation to changing game conditions and strategies.

7. **Explainable AI**: Develop methods to explain the agent's decision-making process, which would help understand its strategies and improve them.

## Project Structure

The project consists of the following key files:

- `gym_wrapper/tetris_env.py`: PyBoy-Gym environment wrapper for Tetris
- `state_preprocessor.py`: Processes raw game state into features
- `reward_function.py`: Defines reward functions for the RL agent
- `custom_wrappers.py`: Additional environment wrappers
- `rl_agent.py`: Reinforcement learning agent implementation
- `hybrid_tetris_ai.py`: Main hybrid AI implementation
- `train_rl_agent.py`: Script for training the RL agent
- `evaluate_rl_agent.py`: Script for evaluating the trained agent
- `performance_analysis.py`: Script for analyzing agent performance
- `visualize_performance.py`: Script for visualizing performance metrics
- `test_gym_env.py`: Test script for the Gym environment
- `test_hybrid_ai.py`: Test script for the hybrid AI implementation

## Requirements

- Python 3.8 or higher
- PyBoy 2.5.1
- NumPy 1.21.0 or higher
- Gymnasium 0.28.1 or higher
- Stable Baselines3 2.0.0 or higher
- PyTorch 2.0.0 or higher
- Matplotlib 3.5.0 or higher
- Pygame 2.1.0 or higher
- Tetris ROM file (not included due to copyright)

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place a Tetris ROM file named `tetris.gb` in the project directory

3. Train the AI:
```bash
python train_rl_agent.py --rom tetris.gb --algorithm ppo --timesteps 100000
```

4. Evaluate the trained AI:
```bash
python evaluate_rl_agent.py --rom tetris.gb --model ./tetris_logs/model.zip
```

5. Analyze performance:
```bash
python performance_analysis.py --rom tetris.gb --model ./tetris_logs/model.zip --compare-random
```

6. Visualize results:
```bash
python visualize_performance.py --data ./tetris_logs/analysis/performance_results.csv
```

For more detailed information about training and evaluation, see `README_TRAINING.md`.
