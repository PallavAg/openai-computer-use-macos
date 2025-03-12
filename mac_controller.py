import base64
import io
import subprocess
import time
from typing import List, Dict

import pyautogui

# Key mapping for consistent behavior
KEY_MAPPING = {
    "/": "/",
    "\\": "\\",
    "alt": "alt",
    "arrowdown": "down",
    "arrowleft": "left",
    "arrowright": "right",
    "arrowup": "up",
    "backspace": "backspace",
    "capslock": "capslock",
    "cmd": "command",
    "ctrl": "ctrl",
    "delete": "delete",
    "end": "end",
    "enter": "enter",
    "esc": "esc",
    "home": "home",
    "insert": "insert",
    "option": "option",
    "pagedown": "pagedown",
    "pageup": "pageup",
    "shift": "shift",
    "space": "space",
    "super": "command",
    "tab": "tab",
    "win": "command",
}


class MacController:
    """A computer implementation for controlling macOS using PyAutoGUI."""

    environment = "mac"  # Tells the model we're on macOS

    def __init__(self, enable_speech=True):
        # Get screen dimensions
        self.width, self.height = pyautogui.size()
        self.dimensions = (self.width, self.height)
        self.enable_speech = enable_speech

        # If the screen is aspect ratio is not 16:10, log a warning that the model may not work well if not being run on the built in MacBook display
        aspect_ratio = self.width / self.height
        if aspect_ratio < 1.5 or aspect_ratio > 1.6:
            print(
                "Warning: This script may not work well with an external display connected."
            )

        # Scale factor for screenshots (reduces size if needed)
        self.MAX_WIDTH = 1728  # Max screenshot width
        if self.width > self.MAX_WIDTH:
            self.scale_factor = self.MAX_WIDTH / self.width
            self.target_width = self.MAX_WIDTH
            self.target_height = int(self.height * self.scale_factor)
        else:
            self.scale_factor = 1.0
            self.target_width = self.width
            self.target_height = self.height

        # Flag to enable/disable coordinate scaling
        self._scaling_enabled = True

        # Announce initialization
        self.say("Initializing.")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass

    def say(self, text):
        """Use macOS 'say' command to speak the given text."""
        if self.enable_speech:
            # Format text to sound more natural
            text = text.replace("(", " ").replace(")", " ")
            text = text.replace(",", " ").replace(":", " ")
            text = text.replace("{", " ").replace("}", " ")
            text = text.replace("'", " ")

            # Use subprocess to call the 'say' command
            subprocess.Popen(["say", text])

    def screenshot(self) -> str:
        """Take a screenshot and return it as a base64-encoded string."""
        # Announce screenshot
        self.say("Taking screenshot")

        # Capture screenshot using PyAutoGUI
        screenshot = pyautogui.screenshot()

        # Scale down the screenshot if needed
        if self._scaling_enabled and self.scale_factor < 1.0:
            screenshot = screenshot.resize((self.target_width, self.target_height))

        # Convert to base64
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format="PNG", optimize=True)
        img_buffer.seek(0)
        base64_image = base64.b64encode(img_buffer.read()).decode()

        return base64_image

    def click(self, x: int, y: int, button: str = "left") -> None:
        """Click at the specified coordinates with the given button."""
        # Scale coordinates if needed
        scaled_x, scaled_y = self._scale_coordinates_to_screen(x, y)

        # Map button names
        button_mapping = {"left": "left", "right": "right", "middle": "middle"}
        button_name = button_mapping.get(button, "left")

        # Announce click
        self.say(f"Clicking {button} at coordinates {x} {y}")

        # Perform the click
        pyautogui.click(x=scaled_x, y=scaled_y, button=button_name, duration=1)

    def double_click(self, x: int, y: int) -> None:
        """Double-click at the specified coordinates."""
        # Scale coordinates if needed
        scaled_x, scaled_y = self._scale_coordinates_to_screen(x, y)

        # Announce double click
        self.say(f"Double clicking at coordinates {x} {y}")

        # Perform the double click
        pyautogui.doubleClick(x=scaled_x, y=scaled_y)

    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        """Scroll at the specified coordinates by the given amounts."""
        # Scale coordinates if needed
        scaled_x, scaled_y = self._scale_coordinates_to_screen(x, y)

        # Announce scroll
        direction = "down" if scroll_y < 0 else "up"
        self.say(f"Scrolling {direction} at coordinates {x} {y}")

        # Move to position first
        pyautogui.moveTo(scaled_x, scaled_y)

        # Perform the scroll
        pyautogui.scroll(scroll_y)  # PyAutoGUI primarily supports vertical scrolling

    def type(self, text: str) -> None:
        """Type the specified text."""
        # Announce typing (shortened version for privacy/security)
        shortened_text = text[:20] + "..." if len(text) > 20 else text
        self.say(f"Typing {shortened_text}")

        # Type the text
        pyautogui.write(
            text, interval=0.01
        )  # Small interval to avoid missed keystrokes

    def wait(self, ms: int = 1000) -> None:
        """Wait for the specified number of milliseconds."""
        # Announce wait
        seconds = ms / 1000
        self.say(f"Waiting for {seconds} seconds")

        # Wait
        time.sleep(ms / 1000)

    def move(self, x: int, y: int) -> None:
        """Move the mouse to the specified coordinates."""
        # Scale coordinates if needed
        scaled_x, scaled_y = self._scale_coordinates_to_screen(x, y)

        # Announce move
        self.say(f"Moving mouse to coordinates {x} {y}")

        # Move the mouse with a visible duration
        pyautogui.moveTo(scaled_x, scaled_y, duration=1)

    def keypress(self, keys: List[str]) -> None:
        """Press the specified keys."""
        if not keys:
            return

        # Map keys to PyAutoGUI format
        mapped_keys = [KEY_MAPPING.get(key.lower(), key) for key in keys]

        # Announce keypress
        key_names = " and ".join(keys)
        self.say(f"Pressing keys {key_names}")

        if len(mapped_keys) == 1:
            # If only one key, just press it
            pyautogui.press(mapped_keys[0])
        else:
            # Hold down all modifier keys except the last one
            for key in mapped_keys[:-1]:
                pyautogui.keyDown(key)

            # Press the last key
            pyautogui.press(mapped_keys[-1].lower())

            # Release all modifier keys in reverse order
            for key in reversed(mapped_keys[:-1]):
                pyautogui.keyUp(key)

    def drag(self, path: List[Dict[str, int]]) -> None:
        """Drag the mouse along the specified path."""
        if not path:
            return

        # Log drag action
        start_point = path[0]
        end_point = path[-1]

        # Get start position
        start_x, start_y = self._scale_coordinates_to_screen(path[0]["x"], path[0]["y"])

        # Announce drag
        self.say(
            f"Dragging from coordinates {start_point['x']} {start_point['y']} to {end_point['x']} {end_point['y']}"
        )

        # Move to start position and press mouse button
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()

        # Move along the path
        for point in path[1:]:
            x, y = self._scale_coordinates_to_screen(point["x"], point["y"])
            pyautogui.moveTo(x, y)

        # Release mouse button
        pyautogui.mouseUp()

    def get_current_url(self) -> str:
        """
        Placeholder for compatibility with browser environments.
        Not applicable for Mac OS general control.
        """
        return ""

    def _scale_coordinates_to_screen(self, x: int, y: int) -> tuple[int, int]:
        """Scale coordinates from the model's coordinate system to the screen's coordinates."""
        if not self._scaling_enabled:
            return x, y

        # Convert from model coordinates to screen coordinates
        screen_x = round(x * (self.width / self.target_width))
        screen_y = round(y * (self.height / self.target_height))

        return screen_x, screen_y
