import json
import os
import time
from typing import Callable

import requests
from mac_controller import MacController


class Agent:
    """Agent that manages interactions with the OpenAI API for computer control."""

    def __init__(
        self,
        computer: MacController,
        model: str,
        acknowledge_safety_check_callback: Callable = lambda msg: False,
    ):
        self.computer = computer
        self.model = model
        self.print_steps = True
        self.debug = False
        self.tools = [
            {
                "type": "computer-preview",
                "display_width": computer.dimensions[0],
                "display_height": computer.dimensions[1],
                "environment": computer.environment,
            }
        ]
        self.acknowledge_safety_check_callback = acknowledge_safety_check_callback

    def debug_print(self, *args):
        if self.debug:
            print(json.dumps(*args, indent=4))

    def handle_item(self, item):
        if item["type"] == "message":
            if self.print_steps:
                print(item["content"][0]["text"])
                self.computer.say(item["content"][0]["text"])
            return []

        if item["type"] == "function_call":
            name, args = item["name"], json.loads(item["arguments"])
            if self.print_steps:
                print(f"{name}{{args}}" if args else f"{name}")
            if hasattr(self.computer, name):
                method = getattr(self.computer, name)
                method(**args)
            return [
                {
                    "type": "function_call_output",
                    "call_id": item["call_id"],
                    "output": "success",
                }
            ]

        if item["type"] == "computer_call":
            action = item["action"]
            action_type = action["type"]
            action_args = {k: v for k, v in action.items() if k != "type"}
            if self.print_steps:
                print(f"{action_type}({action_args})")
            method = getattr(self.computer, action_type)
            ret = method(**action_args)
            if action_type == "screenshot":
                screenshot_base64 = ret
            else:
                time.sleep(1.5)
                screenshot_base64 = self.computer.screenshot()
            pending_checks = item.get("pending_safety_checks", [])
            for check in pending_checks:
                message = check["message"]
                if not self.acknowledge_safety_check_callback(message):
                    raise ValueError(
                        f"Safety check failed: {message}. Cannot continue with unacknowledged safety checks."
                    )
            return [
                {
                    "type": "computer_call_output",
                    "call_id": item["call_id"],
                    "acknowledged_safety_checks": pending_checks,
                    "output": {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{screenshot_base64}",
                    },
                }
            ]
        return []

    def run_full_turn(self, input_items, print_steps=True, debug=False):
        self.print_steps = print_steps
        self.debug = debug
        new_items = []
        while new_items[-1].get("role") != "assistant" if new_items else True:
            if debug:
                self.debug_print([msg for msg in input_items + new_items])
            response = create_response(
                model=self.model,
                input=input_items + new_items,
                tools=self.tools,
                truncation="auto",
            )
            if debug:
                self.debug_print(response)
            if "output" not in response:
                if debug:
                    print(response)
                raise ValueError("No output from model")
            else:
                new_items += response["output"]
                for item in response["output"]:
                    new_items += self.handle_item(item)
        return new_items


def create_response(**kwargs):
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json",
    }
    openai_org = os.getenv("OPENAI_ORG")
    if openai_org:
        headers["Openai-Organization"] = openai_org
    response = requests.post(url, headers=headers, json=kwargs)
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
    return response.json()


def acknowledge_safety_check_callback(message: str) -> bool:
    response = input(
        f"Safety Check Warning: {message}\nDo you want to acknowledge and proceed? (y/n): "
    ).lower()
    return response.strip() == "y"
