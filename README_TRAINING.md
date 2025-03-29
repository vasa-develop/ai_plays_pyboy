# Training and Evaluating the Tetris RL Agent

This document provides instructions for training and evaluating the reinforcement learning agent for playing Tetris using the PyBoy emulator.

## Prerequisites

Ensure you have installed all required dependencies:

```bash
pip install -r requirements.txt
```

Make sure you have the Tetris ROM file (`tetris.gb`) in the project directory.

## Training the Agent

The training script `train_rl_agent.py` provides a flexible way to train the RL agent with various configurations.

### Basic Training

To train the agent with default settings:

```bash
python train_rl_agent.py --rom tetris.gb
```

This will train a PPO agent for 100,000 timesteps and save the model in the `./tetris_logs` directory.

### Advanced Training Options

The training script supports several command-line arguments:

- `--rom`: Path to the Tetris ROM file (default: `tetris.gb`)
- `--algorithm`: RL algorithm to use (`ppo`, `a2c`, or `dqn`) (default: `ppo`)
- `--timesteps`: Number of timesteps to train for (default: `100000`)
- `--checkpoint-freq`: Frequency (in timesteps) to save model checkpoints (default: `10000`)
- `--eval-freq`: Frequency (in timesteps) to evaluate the model (default: `10000`)
- `--log-dir`: Directory to save logs and models (default: `./tetris_logs`)
- `--model`: Path to pre-trained model to continue training (default: `None`)
- `--render`: Render the game during training (default: `False`)

Example with custom settings:

```bash
python train_rl_agent.py --rom tetris.gb --algorithm dqn --timesteps 200000 --checkpoint-freq 20000 --render
```

## Evaluating the Agent

After training, you can evaluate the agent's performance using the `evaluate_rl_agent.py` script.

### Basic Evaluation

To evaluate a trained model:

```bash
python evaluate_rl_agent.py --rom tetris.gb --model ./tetris_logs/model.zip
```

This will run the agent for 10 episodes and report performance metrics.

### Advanced Evaluation Options

The evaluation script supports several command-line arguments:

- `--rom`: Path to the Tetris ROM file (default: `tetris.gb`)
- `--model`: Path to trained model (required)
- `--algorithm`: RL algorithm used for the model (`ppo`, `a2c`, or `dqn`) (default: `ppo`)
- `--episodes`: Number of episodes to evaluate (default: `10`)
- `--render`: Render the game during evaluation (default: `False`)
- `--log-dir`: Directory to save logs and evaluation results (default: `./tetris_logs`)
- `--save-video`: Save video of gameplay (not implemented yet) (default: `False`)

Example with custom settings:

```bash
python evaluate_rl_agent.py --rom tetris.gb --model ./tetris_logs/model.zip --algorithm ppo --episodes 20 --render
```

## Using the Hybrid Tetris AI

The `hybrid_tetris_ai.py` module provides a higher-level interface for training and playing Tetris using the RL agent.

### Example Usage

```python
from hybrid_tetris_ai import TetrisHybridAI

# Create the AI
ai = TetrisHybridAI(rom_path="tetris.gb")

# Train the AI
ai.train(total_timesteps=100000, save_path="tetris_model")

# Play using the trained model
ai.model_path = "tetris_model.zip"
ai.play(episodes=5)

# Clean up
ai.close()
```

You can also use the `test_hybrid_ai.py` script to test the hybrid AI:

```bash
python test_hybrid_ai.py --mode train --timesteps 50000
```

## Visualizing Results

The evaluation script generates plots of episode rewards and saves them in the `./tetris_logs/results` directory. These plots can be used to analyze the agent's performance across multiple episodes.

## Troubleshooting

If you encounter issues with the training or evaluation:

1. Ensure the Tetris ROM file is in the correct location
2. Check that all dependencies are installed correctly
3. Verify that the model path is correct when evaluating
4. Check the log files in the `./tetris_logs` directory for error messages
