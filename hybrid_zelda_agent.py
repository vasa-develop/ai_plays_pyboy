import os
import logging
import numpy as np
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from stable_baselines3 import PPO
from zelda_rl_agent import ZeldaRLAgent, create_zelda_env
from llm_integration import LLMIntegration

class HybridZeldaAgent:
    """
    Hybrid agent for playing Zelda: Link's Awakening that combines
    reinforcement learning with LLM guidance for complex game mechanics
    and dialogue-based progression.
    """

    def __init__(
        self,
        rom_path: str = "zelda.gbc",
        rl_model_path: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_model: str = "openai/gpt-4-turbo",
        log_dir: str = "./zelda_hybrid_logs",
        render_mode: str = "human",
        emulation_mode: str = "continuous"
    ):
        """
        Initialize the hybrid Zelda agent.

        Args:
            rom_path: Path to the Zelda ROM file
            rl_model_path: Path to a pre-trained RL model (optional)
            llm_api_key: API key for OpenRouter (optional)
            llm_model: LLM model to use
            log_dir: Directory to save logs
            render_mode: Rendering mode for the environment
        """
        self.rom_path = rom_path
        self.log_dir = log_dir
        self.render_mode = render_mode

        os.makedirs(log_dir, exist_ok=True)

        self.logger = logging.getLogger("hybrid_zelda_agent")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            file_handler = logging.FileHandler(os.path.join(log_dir, "hybrid_agent.log"))
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        self.env = create_zelda_env(
            rom_path, 
            render_mode=render_mode,
            save_state_path=os.path.join(log_dir, "zelda_gameplay.state"),
            emulation_mode=emulation_mode
        )
        
        self.emulation_mode = emulation_mode

        self.rl_agent = ZeldaRLAgent(
            env=self.env,
            algorithm="ppo",
            model_path=rl_model_path,
            log_dir=os.path.join(log_dir, "rl_logs")
        )

        self.llm = LLMIntegration(
            api_key=llm_api_key or os.environ.get("OPENROUTER_API_KEY"),
            model=llm_model,
            log_dir=os.path.join(log_dir, "llm_logs")
        )

        self.current_plan = []
        self.game_history = []
        self.dialogue_history = []
        self.current_objective = "Start the game and find the sword"

        self.logger.info(f"Hybrid Zelda Agent initialized with ROM: {rom_path}")
        if rl_model_path:
            self.logger.info(f"Using pre-trained RL model: {rl_model_path}")

    def train_rl_component(self, total_timesteps: int = 100000, eval_freq: int = 10000,
                          save_freq: int = 10000, n_eval_episodes: int = 5):
        """
        Train the RL component of the hybrid agent.

        Args:
            total_timesteps: Total number of timesteps to train for
            eval_freq: Frequency of evaluation during training
            save_freq: Frequency of saving model checkpoints
            n_eval_episodes: Number of episodes to evaluate on

        Returns:
            Trained RL model
        """
        self.logger.info(f"Training RL component for {total_timesteps} timesteps")

        save_path = os.path.join(self.log_dir, "rl_logs", "zelda_ppo_final.zip")

        model = self.rl_agent.train(
            total_timesteps=total_timesteps,
            eval_freq=eval_freq,
            save_freq=save_freq,
            n_eval_episodes=n_eval_episodes,
            save_path=save_path
        )

        self.logger.info(f"RL component training completed. Model saved to {save_path}")

        return model

    def load_rl_model(self, model_path: str):
        """
        Load a pre-trained RL model.

        Args:
            model_path: Path to the model file
        """
        self.logger.info(f"Loading RL model from {model_path}")
        self.rl_agent.load(model_path)

    def _extract_game_state(self, observation) -> Dict[str, Any]:
        """
        Extract relevant game state information from the observation.

        Args:
            observation: Raw observation from the environment

        Returns:
            Processed game state dictionary
        """
        if not isinstance(observation, dict):
            if isinstance(observation, (list, tuple, np.ndarray)) and len(observation) > 0:
                observation = observation[0]  # Extract first element if it's a batch
                if not isinstance(observation, dict):
                    observation = {"screen": observation}
            else:
                observation = {"screen": observation}

        health = 0
        health_value = observation.get("health")
        if isinstance(health_value, (list, np.ndarray)) and len(health_value) > 0:
            health = health_value[0]
        elif health_value is not None:
            health = health_value

        position = (0, 0)
        position_value = observation.get("position")
        if isinstance(position_value, (list, tuple, np.ndarray)) and len(position_value) > 0:
            position = tuple(position_value)
        elif position_value is not None:
            position = position_value

        map_position = (0, 0)
        map_position_value = observation.get("map_position")
        if isinstance(map_position_value, (list, tuple, np.ndarray)) and len(map_position_value) > 0:
            map_position = tuple(map_position_value)
        elif map_position_value is not None:
            map_position = map_position_value

        rupees = 0
        rupees_value = observation.get("rupees")
        if isinstance(rupees_value, (list, np.ndarray)) and len(rupees_value) > 0:
            rupees = rupees_value[0]
        elif rupees_value is not None:
            rupees = rupees_value

        inventory = []
        inventory_value = observation.get("inventory")
        if isinstance(inventory_value, np.ndarray):
            inventory = inventory_value.tolist()
        elif isinstance(inventory_value, (list, tuple)):
            inventory = list(inventory_value)

        game_state = {
            "screen": observation.get("screen", None),
            "health": health,
            "position": position,
            "map_position": map_position,
            "rupees": rupees,
            "inventory": inventory
        }

        game_state["current_objective"] = self.current_objective
        game_state["has_plan"] = len(self.current_plan) > 0

        return game_state

    def _detect_dialogue(self, observation) -> Optional[str]:
        """
        Detect if there's dialogue on screen and extract it.
        This is a placeholder - actual implementation would need OCR or memory reading.
        Includes dialogue buffering to only return complete dialogue.
        Ignores title screens and loading screens.

        Args:
            observation: Raw observation from the environment

        Returns:
            Extracted dialogue text or None
        """
        if not isinstance(observation, dict):
            if isinstance(observation, (list, tuple, np.ndarray)) and len(observation) > 0:
                observation = observation[0]  # Extract first element if it's a batch
                if not isinstance(observation, dict):
                    return None
            else:
                return None

        if not hasattr(self, '_game_started'):
            self._game_started = True
            self._dialogue_buffer = []
            self._dialogue_stable_count = 0
            self._last_dialogue = None
            self._gameplay_frames = 0
            self._last_screen_state = None
            self._screen_stable_count = 0
            self._in_gameplay = True
            self._loading_screen_count = 0
            
        self._gameplay_frames += 1
            
        screen_data = None
        if 'screen' in observation and observation['screen'] is not None:
            screen_data = observation['screen']
            
        is_title_or_loading_screen = True  # Default to true until proven otherwise
        
        if screen_data is not None:
            if hasattr(self, '_last_screen_state') and self._last_screen_state is not None:
                if isinstance(screen_data, np.ndarray) and isinstance(self._last_screen_state, np.ndarray):
                    try:
                        if screen_data.shape == self._last_screen_state.shape:
                            screen_diff = np.mean(np.abs(screen_data - self._last_screen_state))
                            
                            if screen_diff < 0.05:  # Very little change
                                self._screen_stable_count += 1
                                if self._screen_stable_count > 30:  # If stable for 30 frames
                                    is_title_or_loading_screen = True
                                    if self._gameplay_frames % 60 == 0:  # Log every second
                                        self.logger.info(f"Detected loading/title screen (stable screen)")
                            else:
                                self._screen_stable_count = 0
                                
                                if self._in_gameplay and self._gameplay_frames > 1000:
                                    is_title_or_loading_screen = False
                    except Exception as e:
                        self.logger.warning(f"Error comparing screens: {e}")
            
            self._last_screen_state = screen_data
            
        if 'health' in observation and observation['health'] > 0:
            if 'position' in observation and not np.array_equal(observation['position'], np.array([0, 0])):
                self._in_gameplay = True
                is_title_or_loading_screen = False
                
        if is_title_or_loading_screen:
            self._loading_screen_count += 1
            if self._loading_screen_count % 60 == 0:  # Log every ~60 frames
                self.logger.info(f"Still detecting loading/title screen (frame {self._gameplay_frames})")
        else:
            if self._loading_screen_count > 0:
                self.logger.info(f"Exited loading/title screen after {self._loading_screen_count} frames")
            self._loading_screen_count = 0
                
        if is_title_or_loading_screen:
            return None
            
        if not self._game_started:
            self._game_started = True
            self.logger.info("Game has started, beginning dialogue detection")
            
        is_dialogue_frame = False
        dialogue_text = None

        if is_dialogue_frame and dialogue_text:
            if not hasattr(self, '_dialogue_buffer'):
                self._dialogue_buffer = []
                self._dialogue_stable_count = 0
                self._last_dialogue = None

            self._dialogue_buffer.append(dialogue_text)

            if self._last_dialogue == dialogue_text:
                self._dialogue_stable_count += 1
            else:
                self._dialogue_stable_count = 0
                self._last_dialogue = dialogue_text

            if self._dialogue_stable_count >= 5:  # Adjust threshold as needed
                complete_dialogue = dialogue_text
                self._dialogue_buffer = []
                self._dialogue_stable_count = 0
                self._last_dialogue = None
                return complete_dialogue

            return None
        else:
            if hasattr(self, '_dialogue_buffer') and len(self._dialogue_buffer) > 0:
                self._dialogue_stable_count += 1
                if self._dialogue_stable_count >= 10:  # Adjust threshold as needed
                    if self._last_dialogue:
                        complete_dialogue = self._last_dialogue
                        self._dialogue_buffer = []
                        self._dialogue_stable_count = 0
                        self._last_dialogue = None
                        return complete_dialogue
                    self._dialogue_buffer = []
                    self._dialogue_stable_count = 0
                    self._last_dialogue = None

            return None

    def _update_game_history(self, game_state: Dict[str, Any], action: int, reward: float,
                            info: Dict[str, Any], dialogue: Optional[str] = None):
        """
        Update the game history with the latest state and action.

        Args:
            game_state: Current game state
            action: Action taken
            reward: Reward received
            info: Additional information
            dialogue: Detected dialogue (if any)
        """
        event = {
            "state": {
                "health": game_state["health"],
                "position": game_state["position"],
                "map_position": game_state["map_position"],
                "rupees": game_state["rupees"]
            },
            "action": action,
            "reward": float(reward),
            "description": f"Took action {action} at position {game_state['position']} on map {game_state['map_position']}"
        }

        if dialogue:
            event["dialogue"] = dialogue
            self.dialogue_history.append(dialogue)

        self.game_history.append(event)

        if len(self.game_history) > 1000:
            self.game_history = self.game_history[-1000:]

    def _should_use_llm(self, game_state: Dict[str, Any], reward_history: List[float]) -> bool:
        """
        Determine if LLM guidance should be used based on current state.

        Args:
            game_state: Current game state
            reward_history: Recent reward history

        Returns:
            True if LLM should be used, False otherwise
        """

        if len(reward_history) >= 100:
            recent_rewards = reward_history[-100:]
            reward_variance = np.var(recent_rewards)
            if reward_variance < 0.01 and np.mean(recent_rewards) <= 0:
                return True

        if len(self.game_history) > 1:
            try:
                prev_map = self.game_history[-2]["state"]["map_position"]
                curr_map = game_state["map_position"]

                prev_map_array = np.array(prev_map)
                curr_map_array = np.array(curr_map)

                if not np.array_equal(prev_map_array, curr_map_array):
                    return True
            except (ValueError, TypeError, IndexError) as e:
                self.logger.warning(f"Error comparing map positions: {e}")

        health = game_state["health"]
        if isinstance(health, (list, tuple, np.ndarray)):
            if len(health) > 0 and health[0] <= 1:
                return True
        elif health <= 1:
            return True

        if len(self.game_history) % 500 == 0 and len(self.game_history) > 0:
            return True

        return False

    def _get_llm_guidance(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get guidance from the LLM based on current game state.

        Args:
            game_state: Current game state

        Returns:
            Guidance information
        """
        self.logger.info("Getting LLM guidance for current game state")

        if hasattr(self, '_last_llm_request_step'):
            self._last_llm_request_step = len(self.game_history)

        if len(self.dialogue_history) > 0 and self.dialogue_history[-1]:
            if hasattr(self, '_last_dialogue_processed'):
                self._last_dialogue_processed = self.dialogue_history[-1]

            dialogue_context = {
                "map_position": game_state["map_position"],
                "previous_objectives": [self.current_objective]
            }

            dialogue_interpretation = self.llm.interpret_dialogue(
                self.dialogue_history[-1], dialogue_context
            )

            if "quest_information" in dialogue_interpretation and dialogue_interpretation["quest_information"]:
                self.current_objective = dialogue_interpretation["quest_information"]
                self.current_plan = []  # Reset plan since objective changed

            return {
                "type": "dialogue_guidance",
                "interpretation": dialogue_interpretation,
                "suggested_action": None
            }

        if not self.current_plan:
            plan = self.llm.plan_quest_progression(self.current_objective, game_state)
            self.current_plan = plan

            return {
                "type": "new_plan",
                "plan": plan,
                "suggested_action": None
            }

        suggestion = self.llm.suggest_action(game_state, self.current_plan)

        return {
            "type": "action_suggestion",
            "current_plan_step": self.current_plan[0] if self.current_plan else None,
            "suggestion": suggestion
        }

    def _llm_action_to_env_action(self, llm_action: str) -> int:
        """
        Convert LLM action suggestion to environment action.

        Args:
            llm_action: Action suggested by LL
        Returns:
            Environment action index
        """
        action_map = {
            "move_up": 0,      # WindowEvent.PRESS_ARROW_UP
            "move_right": 1,   # WindowEvent.PRESS_ARROW_RIGHT
            "move_left": 2,    # WindowEvent.PRESS_ARROW_LEFT
            "move_down": 3,    # WindowEvent.PRESS_ARROW_DOWN
            "use_sword": 5,    # WindowEvent.PRESS_BUTTON_B
            "interact": 4,     # WindowEvent.PRESS_BUTTON_A
            "use_item": 4,     # WindowEvent.PRESS_BUTTON_A
            "open_menu": 6,    # WindowEvent.PRESS_BUTTON_START
            "swap_item": 7,    # WindowEvent.PRESS_BUTTON_SELECT
            "wait": 8,         # No action
        }

        return action_map.get(llm_action.lower(), 8)  # Default to "wait" if unknown

    def play(self, episodes: int = 1, max_steps_per_episode: int = 10000,
             llm_guidance_frequency: float = 0.1, deterministic: bool = True):
        """
        Play Zelda using the hybrid agent.

        Args:
            episodes: Number of episodes to play
            max_steps_per_episode: Maximum steps per episode
            llm_guidance_frequency: Frequency of LLM guidance (0.0 to 1.0)
            deterministic: Whether to use deterministic actions for RL

        Returns:
            List of episode rewards
        """
        if hasattr(self, 'emulation_mode') and self.emulation_mode == "turn_based":
            self.logger.info(f"Using turn-based mode for gameplay")
            return self.play_turn_based(episodes=episodes, max_steps_per_episode=max_steps_per_episode)
        else:
            self.logger.info(f"Using continuous mode for gameplay")
            return self.play_continuous(episodes=episodes, max_steps_per_episode=max_steps_per_episode,
                                       llm_guidance_frequency=llm_guidance_frequency, 
                                       deterministic=deterministic)
    
    def play_continuous(self, episodes: int = 1, max_steps_per_episode: int = 10000,
                       llm_guidance_frequency: float = 0.1, deterministic: bool = True):
        """
        Play Zelda using the hybrid agent in continuous mode.

        Args:
            episodes: Number of episodes to play
            max_steps_per_episode: Maximum steps per episode
            llm_guidance_frequency: Frequency of LLM guidance (0.0 to 1.0)
            deterministic: Whether to use deterministic actions for RL

        Returns:
            List of episode rewards
        """
        self.logger.info(f"Playing {episodes} episodes with hybrid agent in continuous mode")

        episode_rewards = []

        if not hasattr(self, '_last_llm_request_step'):
            self._last_llm_request_step = 0
            self._last_dialogue_processed = None
            self._min_steps_between_llm_requests = 30  # Minimum steps between random LLM requests

        for episode in range(episodes):
            self.logger.info(f"Starting episode {episode+1}/{episodes}")

            reset_result = self.env.reset()
            if isinstance(reset_result, tuple) and len(reset_result) == 2:
                obs, info = reset_result
            else:
                obs = reset_result
                info = {}
            done = False
            truncated = False
            episode_reward = 0
            step = 0

            reward_history = []

            while not (done or truncated) and step < max_steps_per_episode:
                game_state = self._extract_game_state(obs)

                dialogue = self._detect_dialogue(obs)

                if dialogue is not None:
                    if not hasattr(self, 'dialogue_history'):
                        self.dialogue_history = []
                    self.dialogue_history.append(dialogue)
                    game_state['dialogue'] = dialogue  # Add to game state for LLM context

                steps_since_last_request = step - self._last_llm_request_step

                in_title_screen = step < 200  # Skip first 200 frames (approx. 3-4 seconds)

                dialogue_trigger = not in_title_screen and dialogue is not None and dialogue != self._last_dialogue_processed

                random_trigger = not in_title_screen and steps_since_last_request >= self._min_steps_between_llm_requests and np.random.random() < llm_guidance_frequency

                other_trigger = not in_title_screen and self._should_use_llm(game_state, reward_history)

                use_llm = dialogue_trigger or random_trigger or other_trigger

                if in_title_screen and (step % 50 == 0):  # Log every 50 steps during title screen
                    self.logger.info(f"Skipping LLM requests during title screen (step {step})")

                if use_llm:
                    guidance = self._get_llm_guidance(game_state)

                    if guidance["type"] == "action_suggestion" and guidance["suggestion"] and "action" in guidance["suggestion"]:
                        llm_action = guidance["suggestion"]["action"]
                        action = self._llm_action_to_env_action(llm_action)

                        self.logger.info(f"Using LLM suggested action: {llm_action} (mapped to {action})")

                        if guidance["suggestion"].get("completed_step", False) and self.current_plan:
                            self.current_plan.pop(0)
                    else:
                        if hasattr(self.rl_agent, 'model') and self.rl_agent.model is not None:
                            action, _ = self.rl_agent.model.predict(obs, deterministic=deterministic)
                            if isinstance(action, np.ndarray):
                                action = action[0]
                        else:
                            action = self.env.action_space.sample()
                else:
                    if hasattr(self.rl_agent, 'model') and self.rl_agent.model is not None:
                        action, _ = self.rl_agent.model.predict(obs, deterministic=deterministic)
                        if isinstance(action, np.ndarray):
                            action = action[0]
                    else:
                        action = self.env.action_space.sample()

                step_result = self.env.step([action])

                if isinstance(step_result, tuple):
                    if len(step_result) == 5:  # New Gymnasium API: obs, reward, terminated, truncated, info
                        next_obs, reward, done, truncated, info = step_result
                    elif len(step_result) == 4:  # Old Gym API: obs, reward, done, info
                        next_obs, reward, done, info = step_result
                        truncated = False
                    else:
                        next_obs = step_result[0] if len(step_result) > 0 else None
                        reward = step_result[1] if len(step_result) > 1 else 0
                        done = step_result[2] if len(step_result) > 2 else False
                        truncated = False
                        info = {}
                        if len(step_result) > 0 and isinstance(step_result[-1], dict):
                            info = step_result[-1]
                else:
                    next_obs = step_result
                    reward = 0
                    done = False
                    truncated = False
                    info = {}

                self._update_game_history(game_state, action, reward, info, dialogue)

                obs = next_obs
                episode_reward += reward
                reward_history.append(reward)
                step += 1

                if step % 100 == 0:
                    self.logger.info(f"Episode {episode+1}, Step {step}, Reward: {float(episode_reward):.2f}")

            episode_rewards.append(episode_reward)
            self.logger.info(f"Episode {episode+1} completed with reward {float(episode_reward):.2f} in {step} steps")

            episode_data = {
                "episode": episode + 1,
                "reward": float(episode_reward),
                "steps": step,
                "history": self.game_history[-min(step, 1000):]
            }

            episode_file = os.path.join(self.log_dir, f"episode_{episode+1}_data.json")
            with open(episode_file, 'w') as f:
                json.dump(episode_data, f, indent=2)

            self.logger.info(f"Episode data saved to {episode_file}")

        return episode_rewards

    def _get_llm_button_guidance(self, game_state: Dict[str, Any]) -> str:
        """
        Get button input suggestions from the LLM in the format used by ClaudePlayer.
        
        Args:
            game_state: Current game state
            
        Returns:
            String of button inputs in the format "A5 B2 R3 L1"
        """
        if not hasattr(self, 'llm') or self.llm is None:
            self.logger.warning("LLM not initialized, using default button sequence")
            return "A1"  # Default to pressing A once
        
        context = {
            "game_state": game_state,
            "current_objective": game_state.get("current_objective", "Explore the game"),
            "dialogue_history": getattr(self, "dialogue_history", [])[-3:] if hasattr(self, "dialogue_history") else [],
            "current_plan_step": self.current_plan[0] if hasattr(self, "current_plan") and self.current_plan else "No current plan step"
        }
        
        self.logger.info("Requesting button inputs from LLM...")
        response = self.llm.get_button_inputs(context)
        
        if "error" in response:
            self.logger.warning(f"Error getting button inputs: {response['error']}")
            return "A1"  # Default to pressing A once
        
        button_inputs = response.get("inputs", "A1")
        self.logger.info(f"LLM suggested button inputs: {button_inputs}")
        
        return button_inputs
    
    def play_turn_based(self, episodes: int = 1, max_steps_per_episode: int = 10000):
        """
        Play Zelda using the hybrid agent in turn-based mode.
        
        Args:
            episodes: Number of episodes to play
            max_steps_per_episode: Maximum steps per episode
            
        Returns:
            List of episode rewards
        """
        self.logger.info(f"Playing {episodes} episodes with hybrid agent in turn-based mode")
        
        episode_rewards = []
        
        if not hasattr(self, '_last_llm_request_step'):
            self._last_llm_request_step = 0
            self._last_dialogue_processed = None
            self._min_steps_between_llm_requests = 10  # Shorter interval for turn-based mode
        
        for episode in range(episodes):
            self.logger.info(f"Starting episode {episode+1}/{episodes}")
            
            reset_result = self.env.reset()
            if isinstance(reset_result, tuple) and len(reset_result) == 2:
                obs, info = reset_result
            else:
                obs = reset_result
                info = {}
            
            done = False
            truncated = False
            episode_reward = 0
            step = 0
            
            reward_history = []
            
            while not (done or truncated) and step < max_steps_per_episode:
                game_state = self._extract_game_state(obs)
                
                dialogue = self._detect_dialogue(obs)
                if dialogue is not None:
                    if not hasattr(self, 'dialogue_history'):
                        self.dialogue_history = []
                    self.dialogue_history.append(dialogue)
                    game_state['dialogue'] = dialogue
                    self.logger.info(f"Detected dialogue: {dialogue[:50]}...")
                
                button_sequence = self._get_llm_button_guidance(game_state)
                
                self.logger.info(f"Executing button sequence: {button_sequence}")
                actions_taken = self.execute_button_sequence(button_sequence)
                
                if hasattr(self.env, 'envs') and len(self.env.envs) > 0:
                    env_instance = self.env.envs[0]
                    
                    unwrapped_env = env_instance
                    while hasattr(unwrapped_env, 'env') and not hasattr(unwrapped_env, 'pyboy'):
                        unwrapped_env = unwrapped_env.env
                    
                    if hasattr(unwrapped_env, '_get_observation'):
                        next_obs = unwrapped_env._get_observation()
                    else:
                        self.logger.warning("Could not get observation from environment")
                        break
                    
                    prev_state = game_state
                    curr_state = self._extract_game_state(next_obs)
                    
                    reward = 0.0  # Initialize as float to avoid type errors
                    
                    health_diff = float(curr_state.get('health', 0) - prev_state.get('health', 0))
                    reward += health_diff * 5.0  # Reward for gaining health, penalty for losing
                    
                    rupee_diff = float(curr_state.get('rupees', 0) - prev_state.get('rupees', 0))
                    reward += rupee_diff * 0.5  # Small reward for collecting rupees
                    
                    import numpy as np
                    if not np.array_equal(curr_state.get('map_position'), prev_state.get('map_position')):
                        reward += 2.0  # Reward for exploring new screens
                    
                    done = env_instance._is_game_over() if hasattr(env_instance, '_is_game_over') else False
                    truncated = step >= max_steps_per_episode
                    
                    self._update_game_history(game_state, 0, reward, {}, dialogue)  # Use 0 as placeholder for action
                    
                    obs = next_obs
                    episode_reward += reward
                    reward_history.append(reward)
                else:
                    self.logger.warning("Could not access underlying environment")
                    break
                
                step += 1
                
                if step % 10 == 0:
                    self.logger.info(f"Episode {episode+1}, Step {step}, Reward: {float(episode_reward):.2f}")
            
            episode_rewards.append(episode_reward)
            self.logger.info(f"Episode {episode+1} completed with reward {float(episode_reward):.2f} in {step} steps")
            
            episode_data = {
                "episode": episode + 1,
                "reward": float(episode_reward),
                "steps": step,
                "history": self.game_history[-min(step, 1000):] if hasattr(self, 'game_history') else []
            }
            
            episode_file = os.path.join(self.log_dir, f"episode_{episode+1}_turn_based_data.json")
            with open(episode_file, 'w') as f:
                json.dump(episode_data, f, indent=2)
            
            self.logger.info(f"Episode data saved to {episode_file}")
        
        return episode_rewards
    
    def execute_button_sequence(self, input_string: str) -> List[str]:
        """
        Execute a sequence of button inputs in the format used by ClaudePlayer.
        
        Args:
            input_string: String of button inputs in the format "A5 B2 R3 L1"
            
        Returns:
            List of actions taken
        """
        from zelda_input_utils import parse_and_execute_input
        
        self.logger.info(f"Executing button sequence: {input_string}")
        
        if self.emulation_mode == "turn_based":
            if hasattr(self.env, 'envs') and len(self.env.envs) > 0:
                env_instance = self.env.envs[0]
                
                while hasattr(env_instance, 'env') and not hasattr(env_instance, 'pyboy'):
                    env_instance = env_instance.env
                
                if hasattr(env_instance, 'pyboy'):
                    return parse_and_execute_input(env_instance, input_string)
                else:
                    self.logger.warning("Could not find PyBoy instance in environment")
                    return []
            else:
                self.logger.warning("Could not access underlying environment")
                return []
        else:
            self.logger.warning("Button sequence execution is designed for turn-based mode")
            return []
    
    def close(self):
        """Close the environment."""
        if hasattr(self, 'env') and self.env is not None:
            self.env.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Hybrid Zelda Agent")
    parser.add_argument("--rom", default="zelda.gbc", help="Path to Zelda ROM file")
    parser.add_argument("--rl-model", default=None, help="Path to pre-trained RL model")
    parser.add_argument("--train", action="store_true", help="Train the RL component")
    parser.add_argument("--timesteps", type=int, default=100000, help="Number of timesteps to train for")
    parser.add_argument("--episodes", type=int, default=1, help="Number of episodes to play")
    parser.add_argument("--llm-frequency", type=float, default=0.1, help="Frequency of LLM guidance (0.0 to 1.0)")
    parser.add_argument("--log-dir", default="./zelda_hybrid_logs", help="Directory to save logs")

    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")

    agent = HybridZeldaAgent(
        rom_path=args.rom,
        rl_model_path=args.rl_model,
        llm_api_key=api_key,
        log_dir=args.log_dir
    )

    try:
        if args.train:
            agent.train_rl_component(total_timesteps=args.timesteps)

        if args.rl_model:
            agent.load_rl_model(args.rl_model)

        episode_rewards = agent.play(
            episodes=args.episodes,
            llm_guidance_frequency=args.llm_frequency
        )

        print(f"Episode rewards: {episode_rewards}")

    finally:
        agent.close()
