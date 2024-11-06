import BotManager
import TwitchBot
import YtBot
from yt_auth import Authorize
import json
import threading

#setup the bots with settings from the config, and run the oauth flow for the youtube bot.
with open('config.json') as config_file:
    config = json.load(config_file)

allowed_users = [user.lower() for user in config['allowed_users']]

yt_flow_response = Authorize(config)

manager = BotManager.BotManager(config['max_users'], config['WoN_api_key'], allowed_users.copy(), config['wheel_name'])
twbot = TwitchBot.TwitchBot(manager, config['oauth_token'], [config['channel']], config['verbose'])
ytbot = YtBot.YtBot(manager, config['verbose'], yt_flow_response, config['yt_livestream_ID'])

if __name__ == '__main__':
    yt_thread = threading.Thread(target=ytbot.run)
    tw_thread = threading.Thread(target=twbot.run)

    yt_thread.start()
    tw_thread.start()

    yt_thread.join()
    tw_thread.join()