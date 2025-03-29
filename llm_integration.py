import os
import requests
import json
import logging
from typing import Dict, List, Any, Optional, Union

class LLMIntegration:
    """
    Integration with Language Models through OpenRouter API for the Zelda AI.
    This class provides methods to query LLMs for game understanding, planning,
    and decision-making to complement the reinforcement learning agent.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-4-turbo", log_dir: str = "./llm_logs"):
        """
        Initialize the LLM integration.
        
        Args:
            api_key: OpenRouter API key
            model: Model identifier to use (default: gpt-4-turbo)
            log_dir: Directory to save logs
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Provide it as an argument or set OPENROUTER_API_KEY environment variable.")
        
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.log_dir = log_dir
        
        os.makedirs(log_dir, exist_ok=True)
        
        self.logger = logging.getLogger("llm_integration")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            file_handler = logging.FileHandler(os.path.join(log_dir, "llm.log"))
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        self.logger.info(f"LLM Integration initialized with model: {model}")
    
    def query(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> Optional[str]:
        """
        Query the LLM with a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text response or None if the request failed
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            self.logger.info(f"Sending request to LLM: {messages[-1]['content'][:100]}...")
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                self.logger.info(f"Received response from LLM: {content[:100]}...")
                return content
            else:
                self.logger.error(f"Unexpected response format: {result}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error querying LLM: {str(e)}")
            return None
    
    def analyze_game_state(self, game_state: Dict[str, Any], game_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the current game state and history to provide high-level guidance.
        
        Args:
            game_state: Current game state information
            game_history: List of previous game states and actions
            
        Returns:
            Dictionary with analysis and recommendations
        """
        context = self._prepare_game_context(game_state, game_history)
        
        messages = [
            {"role": "system", "content": "You are an AI assistant helping to play The Legend of Zelda: Link's Awakening. "
                                         "Analyze the game state and provide guidance on what to do next."},
            {"role": "user", "content": context}
        ]
        
        response = self.query(messages)
        if not response:
            return {"error": "Failed to get LLM response"}
        
        return self._parse_analysis_response(response)
    
    def plan_quest_progression(self, current_objective: str, game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a plan for progressing in the current quest objective.
        
        Args:
            current_objective: Description of the current objective
            game_state: Current game state information
            
        Returns:
            List of steps to progress in the quest
        """
        context = f"""
        Current objective in Zelda: Link's Awakening: {current_objective}
        
        Current game state:
        - Location: {game_state.get('map_position', 'Unknown')}
        - Health: {game_state.get('health', 'Unknown')}
        - Inventory: {game_state.get('inventory', [])}
        
        Based on this information, provide a step-by-step plan to progress in this objective.
        Format your response as a JSON list of steps, where each step has:
        1. "description": A brief description of what to do
        2. "location": Where to go (if applicable)
        3. "items_needed": Items needed for this step (if any)
        4. "expected_outcome": What should happen after completing this step
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant helping to play The Legend of Zelda: Link's Awakening. "
                                         "Create detailed plans for quest progression."},
            {"role": "user", "content": context}
        ]
        
        response = self.query(messages)
        if not response:
            return [{"error": "Failed to get LLM response"}]
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(json_str)
            return plan
        except Exception as e:
            self.logger.error(f"Error parsing LLM response as JSON: {str(e)}")
            return [{"error": f"Failed to parse response: {str(e)}", "raw_response": response}]
    
    def interpret_dialogue(self, dialogue_text: str, game_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret in-game dialogue to extract quest information and guidance.
        
        Args:
            dialogue_text: Text from in-game dialogue
            game_context: Current game context
            
        Returns:
            Dictionary with interpretation and recommendations
        """
        context = f"""
        In-game dialogue from Zelda: Link's Awakening:
        "{dialogue_text}"
        
        Current game context:
        - Location: {game_context.get('map_position', 'Unknown')}
        - Previous objectives: {game_context.get('previous_objectives', [])}
        
        Analyze this dialogue and extract:
        1. Any new quest information
        2. Hints about where to go next
        3. Items that might be needed
        4. Characters that should be visited
        
        Format your response as JSON with these keys.
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant helping to play The Legend of Zelda: Link's Awakening. "
                                         "Interpret in-game dialogue to extract important information."},
            {"role": "user", "content": context}
        ]
        
        response = self.query(messages)
        if not response:
            return {"error": "Failed to get LLM response"}
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            
            interpretation = json.loads(json_str)
            return interpretation
        except Exception as e:
            self.logger.error(f"Error parsing LLM response as JSON: {str(e)}")
            return {"error": f"Failed to parse response: {str(e)}", "raw_response": response}
    
    def suggest_action(self, game_state: Dict[str, Any], current_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Suggest the next action based on the current game state and plan.
        
        Args:
            game_state: Current game state
            current_plan: Current plan being followed
            
        Returns:
            Dictionary with suggested action and reasoning
        """
        context = f"""
        Current game state in Zelda: Link's Awakening:
        - Location: {game_state.get('map_position', 'Unknown')}
        - Health: {game_state.get('health', 'Unknown')}
        - Position on screen: {game_state.get('position', 'Unknown')}
        - Visible elements: {game_state.get('visible_elements', [])}
        
        Current plan step: {current_plan[0] if current_plan else 'No plan'}
        
        Based on this information, suggest the next immediate action Link should take.
        Choose from: move_up, move_down, move_left, move_right, use_sword, use_item, interact, open_menu, or wait.
        
        Format your response as JSON with:
        1. "action": The suggested action
        2. "reasoning": Why this action is appropriate
        3. "expected_outcome": What should happen after taking this action
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant helping to play The Legend of Zelda: Link's Awakening. "
                                         "Suggest specific actions based on the current game state."},
            {"role": "user", "content": context}
        ]
        
        response = self.query(messages)
        if not response:
            return {"error": "Failed to get LLM response"}
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            
            suggestion = json.loads(json_str)
            return suggestion
        except Exception as e:
            self.logger.error(f"Error parsing LLM response as JSON: {str(e)}")
            return {"error": f"Failed to parse response: {str(e)}", "raw_response": response}
    
    def _prepare_game_context(self, game_state: Dict[str, Any], game_history: List[Dict[str, Any]]) -> str:
        """
        Prepare a textual context from the game state and history for the LLM.
        
        Args:
            game_state: Current game state
            game_history: Game history
            
        Returns:
            Formatted context string
        """
        location = game_state.get('map_position', 'Unknown')
        health = game_state.get('health', 'Unknown')
        inventory = game_state.get('inventory', [])
        
        recent_events = []
        for event in game_history[-5:] if game_history else []:
            recent_events.append(f"- {event.get('description', 'Unknown event')}")
        
        recent_history = "\n".join(recent_events) if recent_events else "No recent events"
        
        context = f"""
        Current game state in Zelda: Link's Awakening:
        - Location: {location}
        - Health: {health}
        - Inventory: {inventory}
        
        Recent history:
        {recent_history}
        
        Based on this information, analyze the current situation and provide:
        1. An assessment of the current game state
        2. Recommendations for what to do next
        3. Any potential obstacles or challenges to be aware of
        4. Items or abilities that might be useful in the current situation
        
        Format your response as a JSON object with these four keys.
        """
        
        return context
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM's analysis response into a structured format.
        
        Args:
            response: Raw response from the LLM
            
        Returns:
            Structured analysis dictionary
        """
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(json_str)
            return analysis
        except Exception as e:
            self.logger.error(f"Error parsing LLM response as JSON: {str(e)}")
            return {
                "assessment": "Failed to parse LLM response",
                "recommendations": ["Continue with default RL behavior"],
                "obstacles": ["Unknown due to parsing error"],
                "useful_items": [],
                "raw_response": response
            }


if __name__ == "__main__":
    api_key = os.environ.get("OPENROUTER_API_KEY")
    
    llm = LLMIntegration(api_key=api_key)
    
    game_state = {
        "map_position": (5, 7),
        "health": 3,
        "inventory": ["Sword", "Shield", "Ocarina"]
    }
    
    game_history = [
        {"description": "Entered Mysterious Forest"},
        {"description": "Found Toadstool"},
        {"description": "Returned to Witch's Hut"}
    ]
    
    analysis = llm.analyze_game_state(game_state, game_history)
    print(json.dumps(analysis, indent=2))
    
    plan = llm.plan_quest_progression("Find the Tail Key", game_state)
    print(json.dumps(plan, indent=2))
