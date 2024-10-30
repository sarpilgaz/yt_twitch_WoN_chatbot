# Twitch and YouTube Chatbot

This bot automates actions for the Wheel of Names, such as adding users to a wheel, doubling their odds if allowed, loading an existing wheel, and more.

Currently, the bot operates as a console application for Twitch, where all actions are accessible as Twitch commands with the `!` prefix.

---

## Twitch Commands

### `!wheel`
- Adds people to the wheel if they are not already present.
- Can only be run when the wheel is open.

### `!here`
- Usable only when doubling is enabled.
- Doubles the odds for the command user if they are already in the wheel.
- Users cannot double their odds more than once.
- Restricted to authorized users.

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

---

## Building and Running

Currently, the application is run through the Python interpreter rather than as an executable. Python 3 and additional dependencies specified in `requirements.txt` are required.

To run the bot from its directory, use:

```bash
python3 app.py
```
## Todo & Ideas

- **Critical: YouTube Chatbot Integration:**  
  Add functionality to support YouTube chat alongside Twitch.

- **Code Refactoring:**  
  Commands for both platforms will likely share functionality. Common actions should be abstracted into functions for better reusability.

- **GUI or Web Interface:**  
  After full functionality is added, consider developing a GUI or web interface. A web interface may require remote hosting, introducing security challenges.

- **Alternative Command Access:**  
  Currently, all interactions happen through commands. It may be beneficial to provide certain privileged commands (e.g., starting/stopping name collection) via GUI buttons or console text commands for more secure access control.

---

