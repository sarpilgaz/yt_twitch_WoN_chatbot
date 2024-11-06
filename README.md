# Twitch and YouTube Chatbot

This bot automates actions for the Wheel of Names, such as adding users to a wheel, doubling their odds if allowed, loading an existing wheel, and more.

Currently, the bot operates as a console application for both Twitch and youtube, privilaged commands such as starting and closing the wheel, etc are only available from Twitch chat. This is because Twitch API is much more responsive and robust compared to youtube.
All actions are accessible as commands with the `!` prefix.

---

## Youtube Commands

### `!wheel`
- Adds people to the wheel if they are not already present.
- Can only be run when the wheel is open.

### `!here`
- Usable only when doubling is enabled.
- Doubles the odds for the command user if they are already in the wheel.
- Users cannot double their odds more than once.

## Twitch Commands

### `!wheel`
- Adds people to the wheel if they are not already present.
- Can only be run when the wheel is open.

### `!here`
- Usable only when doubling is enabled.
- Doubles the odds for the command user if they are already in the wheel.
- Users cannot double their odds more than once.

### `!odds`
- Allows users from the previous wheel to double their odds for the next spin by toggling the permission for the `!here` command.
- Restricted to authorized users.

### `!start`
- Initiates the gathering of names.
- Restricted to authorized users.

### `!stop`
- Ends the gathering of names.
- Restricted to authorized users.

### `!loadWheel`
- Loads an existing wheel and its contents into the application for further actions.
- Restricted to authorized users.

### `!getWheel`
- Creates or updates a wheel with the stored usernames. If a wheel with the specified name exists in `config.json`, it will be updated; otherwise, a new wheel will be created under the user's wheels.
- Restricted to authorized users.

---

## Usage

To use the bot locally or in production, follow these steps:

1. **Configuration:**  
   - Store all configurations and credentials in a `config.json` file in the same directory as the main application. An example config file is available in the app directory.
   
2. **API Key Setup for Wheel of Names:**
   - Create an API key on the [Wheel of Names website](https://wheelofnames.com/faq/api). The key will allow access to manage private wheels.
   - Add the wheel name and channel name to the appropriate fields in `config.json`.
   - Refer to the [Wheel of Names API documentation](https://wheelofnames.stoplight.io/docs/wheelofnames/aqbgvmfot9ua7-wheelofnames-v1) for more details.

3. **Twitch OAuth Token:**
   - Generate an OAuth token for either yourself or the bot account that will manage chat messaging.
   - The account responsible for registering the bot as an application will need 2FA enabled. For more details on registering a bot and obtaining OAuth, refer to:
      - [Twitch Chat Documentation](https://dev.twitch.tv/docs/chat/)
      - [Twitch Token Generator](https://twitchtokengenerator.com/)
4. **Youtube application registiration**
    - Youtube has a more elaborate requirements in place compared to twitch.
    - A very crude process is as follows:
    - go to [google developer console](https://console.cloud.google.com/) for the google account that is going to manage chat messaging
    - create a new project, name it however you wish
    - Find and enable youtube data API v3
    - click create credentials, then oauth client ID
    - select desktop app, and finally note the client id and secret

---

## Building and Running

This application allows you to run both Twitch and YouTube bots for a live-streaming interaction. The bots handle chat messages, process commands, and interact with users. The bots can be run either directly from the Python interpreter or compiled into standalone executables using `PyInstaller`.

For the youtube bot to work, you need to have a livestream already open, as you cannot access the chat without a livestream, unlike twitch.


## Requirements

### Dependencies
- **Python 3** (tested with Python 3.7+)
- **Additional Dependencies**: Install required dependencies from `requirements.txt`.

```bash
pip install -r requirements.txt
```

## Configuration
Before running the bot, ensure that the `config.json` file is correctly set up. For the YouTube bot, you will need to provide a valid YouTube livestream ID in the field `"yt_livestream_id"`. You can find the livestream ID in the URL of your stream.

## Running the bots

### Python Interpreter
You can run the bot directly from the source code. Make sure you have Python 3 and the required dependencies installed. `config.json` must be in the same directory as `main.py` To start the bot, execute the following command from the project directory:

```bash
python3 app.py
```
When starting the bot, a popup will appear for the user to follow the OAuth process and grant the necessary permissions to access the streaming resources.

### Compiling
`pyinstaller` can be used to compile the source code.
```bash
pyinstaller --clean --onefile --add-data "config.json:." --name chatbots main.py
```
This will create a single executable file located in the `dist` directory. It should not be necessary, but it is best practice to have `config.json` in the same directory as the executeable created.



## Todo & Ideas

- **Better config file handling:**
  Currently, the handling of the config file is very flimsy, as it is hardcoded to assume config.json lives in the same directory. This can potentially be made more robust.

- **State Machine implementation for commands:**
  Currently, many if statements are used to check if a command can be run with the current state. A better way to control which commands can be run when is to implement a state machine. 

- **GUI or Web Interface:**  
  Developing a GUI or web interface can be considered. A web interface may require remote hosting, introducing security challenges.

- **Alternative Command Access:**  
  Currently, all interactions happen through commands. It may be beneficial to provide certain privileged commands (e.g., starting/stopping name collection) via GUI buttons or console text commands for more secure access control.

---

