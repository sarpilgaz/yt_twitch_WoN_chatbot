import BotManager
import TwitchBot
import json

with open('config.json') as config_file:
    config = json.load(config_file)

allowed_users = [user.lower() for user in config['allowed_users']]

manager = BotManager.BotManager(config['max_users'], config['WoN_api_key'], allowed_users.copy(), config['wheel_name'])
twbot = TwitchBot.TwitchBot(manager, config['oauth_token'], [config['channel']], config['verbose'], allowed_users.copy())

if __name__ == '__main__':
    twbot.run()