import logging
from pyboy.utils import WindowEvent

BUTTON_RULES = """
Use the following notation for Game Boy buttons:
A (A button), B (B button), U (UP), D (DOWN), L (LEFT), R (RIGHT), S (START), E (SELECT).

You can combine multiple button presses with their duration:
- A5 (press A for 5 frames)
- U10 (hold UP for 10 frames)

Separate each input with spaces:
"A2 B2 R5 L2 U2"

For quick taps, use inputs like:
"A1 B1" or just "A B"

For discrete presses (e.g. navigating menus), use:
"R1 R1" to move right twice in a row

For long holds, specify the number of frames:
"U10" (hold UP for 10 frames)
"""

BUTTON_MAP = {
    'A': WindowEvent.PRESS_BUTTON_A,
    'B': WindowEvent.PRESS_BUTTON_B,
    'U': WindowEvent.PRESS_ARROW_UP,
    'D': WindowEvent.PRESS_ARROW_DOWN,
    'L': WindowEvent.PRESS_ARROW_LEFT,
    'R': WindowEvent.PRESS_ARROW_RIGHT,
    'S': WindowEvent.PRESS_BUTTON_START,
    'E': WindowEvent.PRESS_BUTTON_SELECT
}

RELEASE_MAP = {
    'A': WindowEvent.RELEASE_BUTTON_A,
    'B': WindowEvent.RELEASE_BUTTON_B,
    'U': WindowEvent.RELEASE_ARROW_UP,
    'D': WindowEvent.RELEASE_ARROW_DOWN,
    'L': WindowEvent.RELEASE_ARROW_LEFT,
    'R': WindowEvent.RELEASE_ARROW_RIGHT,
    'S': WindowEvent.RELEASE_BUTTON_START,
    'E': WindowEvent.RELEASE_BUTTON_SELECT
}

def parse_and_execute_input(env, input_string):
    """
    Parse a button input string and execute the button presses.
    
    Args:
        env: The environment instance (may be wrapped in Monitor)
        input_string: String of button inputs in the format "A5 B2 R3 L1"
        
    Returns:
        List of actions taken
    """
    if not input_string.strip():
        logging.warning("Received empty input string")
        return []
    
    if hasattr(env, 'env'):
        unwrapped_env = env.env
    else:
        unwrapped_env = env
    
    if not hasattr(unwrapped_env, 'pyboy'):
        logging.error("Environment does not have PyBoy instance")
        return []
    
    actions_taken = []
    
    try:
        inputs = input_string.strip().split()
        
        for button_input in inputs:
            if len(button_input) == 1:
                button = button_input
                duration = 1
            else:
                button = button_input[0]
                try:
                    duration = int(button_input[1:])
                except ValueError:
                    logging.warning(f"Invalid button input: {button_input}, using duration of 1")
                    duration = 1
            
            if button not in BUTTON_MAP:
                logging.warning(f"Unknown button: {button}, skipping")
                continue
            
            unwrapped_env.pyboy.send_input(BUTTON_MAP[button])
            actions_taken.append(button)
            
            for _ in range(duration):
                if hasattr(unwrapped_env, 'tick'):
                    unwrapped_env.tick(1)
                else:
                    unwrapped_env.pyboy.tick()
            
            unwrapped_env.pyboy.send_input(RELEASE_MAP[button])
            
    except Exception as e:
        logging.error(f"Error executing button inputs: {str(e)}")
    
    return actions_taken
