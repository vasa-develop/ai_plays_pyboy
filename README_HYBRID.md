# Hybrid RL+LLM Approach for Zelda: Link's Awakening

This document outlines the hybrid approach that combines Reinforcement Learning (RL) with Large Language Models (LLMs) to play "The Legend of Zelda: Link's Awakening" on the PyBoy emulator.

## Overview

The hybrid approach addresses the limitations of pure RL when dealing with complex game mechanics, especially dialogue-based progression and long-term planning in Zelda. By integrating LLMs, the agent can better understand game context, interpret dialogue, and make strategic decisions.

## Architecture

The hybrid system consists of two main components:

1. **RL Component**: Handles low-level actions and learns from direct game interactions
2. **LLM Component**: Provides high-level guidance, interprets dialogue, and plans quest progression

### Key Files

- `hybrid_zelda_agent.py`: Main implementation of the hybrid agent
- `llm_integration.py`: Integration with OpenRouter API for accessing LLMs
- `zelda_rl_agent.py`: RL agent implementation
- `zelda_state_preprocessor.py`: Game state extraction (needs improvement)
- `zelda_reward_function.py`: Reward calculation for the RL agent

## How It Works

1. **State Extraction**: The agent extracts game state information (health, position, inventory, etc.)
2. **Decision Making**:
   - The agent decides whether to use LLM guidance based on specific triggers (dialogue, flat rewards, new areas, etc.)
   - If LLM guidance is needed, the agent sends the game state to the LLM for analysis
   - The LLM provides action suggestions, quest planning, or dialogue interpretation
   - The agent converts LLM suggestions into game actions
   - If no LLM guidance is needed, the RL model selects actions

3. **Learning**: The RL component continues to learn from interactions, while the LLM provides strategic guidance

## LLM Integration

The LLM integration provides several key functions:

1. **Game State Analysis**: Analyzing the current game situation and providing recommendations
2. **Quest Planning**: Creating step-by-step plans for completing objectives
3. **Dialogue Interpretation**: Extracting quest information and hints from in-game dialogue
4. **Action Suggestions**: Recommending specific actions based on the current context

## Usage

```bash
# Train the RL component
python hybrid_zelda_agent.py --rom path/to/zelda.gbc --train --timesteps 100000

# Play with a pre-trained model
python hybrid_zelda_agent.py --rom path/to/zelda.gbc --rl-model path/to/model.zip --episodes 5

# Adjust LLM guidance frequency
python hybrid_zelda_agent.py --rom path/to/zelda.gbc --llm-frequency 0.2
```

## Environment Setup

1. Set up the Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set the OpenRouter API key:
   ```bash
   export OPENROUTER_API_KEY="your-api-key"
   ```

3. Ensure you have the Zelda: Link's Awakening ROM file (not included)

## Addressing Current Issues

The hybrid approach addresses several issues in the current implementation:

1. **Flat Rewards**: By using LLM guidance when rewards are flat, the agent can break out of local optima
2. **Dialogue Understanding**: LLMs can interpret dialogue and extract quest information
3. **Long-term Planning**: LLMs provide strategic planning for complex quest objectives
4. **Game State Extraction**: While this still needs improvement, the hybrid approach can work with partial state information

## Future Improvements

1. **Better Game State Extraction**: Implement proper memory reading for accurate game state
2. **OCR for Dialogue**: Add optical character recognition to extract text from dialogue boxes
3. **Hierarchical RL**: Implement hierarchical RL with LLM guidance at the higher level
4. **Imitation Learning**: Use human gameplay demonstrations to improve the RL component
5. **Adaptive LLM Usage**: Dynamically adjust when to use LLM guidance based on performance

## References

- [PyBoy Documentation](https://github.com/Baekalfen/PyBoy)
- [Stable Baselines3 Documentation](https://stable-baselines3.readthedocs.io/)
- [OpenRouter API Documentation](https://openrouter.ai/docs)
