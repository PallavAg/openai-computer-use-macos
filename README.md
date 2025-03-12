# OpenAI Computer Use for MacOS

This repository contains a Python script that lets you use OpenAI's [Computer Use](https://platform.openai.com/docs/guides/tools-computer-use?lang=python) directly on MacOS without requiring a Docker container. The script allows the OpenAI model to perform tasks by taking screenshots and simulating mouse and keyboard actions.

> [!WARNING]  
> Use this script with caution. Allowing an AI model to control your computer can be risky. By running this script, you assume all responsibility and liability.

## Prerequisites

- An **OpenAI API key**.

## Installation and Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/PallavAg/openai-computer-use-macos.git
   cd openai-computer-use-macos
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   ```

3. **Set your OpenAI API key as an environment variable:**

   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

   You can get an OpenAI API Key [here](https://platform.openai.com/account/api-keys).

4. **Grant Accessibility Permissions:**

   The script uses modules like `pyautogui` to control mouse and keyboard events. On macOS, you need to grant accessibility permissions. The permissions prompt should appear the first time you run the script. But to manually provide permissions:

   - Go to **System Preferences** > **Security & Privacy** > **Privacy** tab.
   - Select **Accessibility** from the list on the left.
   - Add your terminal application or Python interpreter to the allowed list.

## Usage

You can run the script by passing an instruction directly via the command line.

**Example using a command line instruction:**

```bash
python3 main.py "Open ChatGPT in Chrome"
```

You can replace `'Open ChatGPT in Safari'` with your desired task.

**Note:** If no instruction is provided via the command line, the script will prompt for one while running.

## Exiting the Script

Quit the script at any time by pressing `Ctrl+C` in the terminal.

## ⚠ Caution and Disclaimer

- **Security Risks:** This script controls your computer's mouse and keyboard events. Use it at your own risk.
- **Responsibility:** By running this script, you assume full responsibility and liability for any actions taken as a result.
