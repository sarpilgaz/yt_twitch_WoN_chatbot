import requests
import json
from twitchio.ext import commands


with open('config.json') as config_file:
    config = json.load(config_file)

API_KEY = config['WoN_api_key']

usernames = []
doubled_odds_usernames = []
MAX_USERS = config['max_users']

"""helper function to return the count of unique usernames"""
def unique_usernames():
    return len(set(usernames))

class TwitchBot(commands.Bot):
    """
        Class for the twitch bot, inherits from twitch API bot
        Reads the necessary config from the config.json file
    """
    def __init__(self):
        """Fields:

            listening: if the bot is collecting usernames for the wheel or not
            doubling_allowed: essentially allows the usage of the command !here, which Doubles the odds of the people already on the wheel.
            verbose: enables or disables extra result reporting for used commands
            allowed_users: privilaged users who are able to execute privilaged commands such as start, stop, etc. These are defined in the file config.json

        """
        super().__init__(token=config['oauth_token'], prefix='!', initial_channels=[config['channel']])
        self.listening = False
        self.doubling_allowed = False
        self.verbose = config['verbose']
        self.allowed_users = [user.lower() for user in config['allowed_users']]

    def is_user_allowed(self, user):
        """Helper function to check if the user is allowed to run certain commands."""
        return user.name.lower() in self.allowed_users


    async def event_ready(self):
        """initial print to confirm starting of the bot"""
        print(f'Logged in as | {self.nick}')
        print(f'Connected to {self.connected_channels}')

    @commands.command(name='start') 
    async def start_command(self, ctx):
        """Command: !start

            executable only by users in allowed_users
            allows the bot to listen for users who wish to join the wheel
        
        """
        if not self.is_user_allowed(ctx.author):
            if self.verbose:
                await ctx.send(f'{ctx.author.name}, you are not allowed to start the bot.')
            return

        if self.listening:
            if self.verbose:
                await ctx.send('Already listening')
            return
        else:
            self.listening = True
            await ctx.send('Now listening for usernames!')

    @commands.command(name='stop')
    async def stop_command(self, ctx):
        """Command: !stop

            executable only by users in allowed_users
            disallows the bot to listen for users who wish to join the wheel
        
        """
        if not self.is_user_allowed(ctx.author):
            if self.verbose:
                await ctx.send(f'{ctx.author.name}, you are not allowed to start the bot.')
            return

        if self.listening:
            self.listening = False
            await ctx.send('Stopped listening for usernames.')
        elif not self.listening:
            if self.verbose:
                await ctx.send('The bot is not currently listening for usernames.')

    @commands.command(name='odds')
    async def odds_command(self, ctx):
        """Command: !odds

            executable only by users in allowed_users
            allows the users to use the !here command
        
        """
        if not self.is_user_allowed(ctx.author):
            if self.verbose:
                await ctx.send(f'{ctx.author.name}, you are not allowed to start doubling odds.')
            return
        else:
            self.doubling_allowed = True
            await ctx.send('doubling your odds is now allowed!')

    @commands.command(name='wheel')
    async def wheel_command(self, ctx):
        """Command: !wheel

            executable by users only after the command !start
            Attempts to add the user to the wheel, if not already present
        
        """
        if not self.listening:
            if self.verbose:
                await ctx.send(f'{ctx.author.name}, the bot is not currently listening for usernames.')
            return
        
        if unique_usernames() >= MAX_USERS:
            if self.verbose:
                await ctx.send('Reached the maximum number of users. Stopping collection.')
            return

        
        username = ctx.author.name
        if username not in usernames:
            usernames.append(username)
            await ctx.send(f'{username} has been added to the wheel!')
        else:
            if self.verbose:
                ctx.send(f'{username}, you are already on the wheel!')

    @commands.command(name='here')
    async def here_command(self, ctx):
        """Command: !here

            executable only after the commands !odds and while the bot is not listening, so before !start
            attempts to double the odds of the user for the wheel if and only if:
                the user is present on the wheel and,
                the user haven't used this command before
   
        """

        if self.listening:
            if self.verbose:
                await ctx.send('doubling odds is not allowed right now.')

        if not self.doubling_allowed:
            if self.verbose:
                await ctx.send('doubling odds is not allowed right now.')
            return
        
        username = ctx.author.name
        if username in doubled_odds_usernames:
            if self.verbose:
                await ctx.send(f'{ctx.author.name}, you already doubled your odds once')
            return

        if username not in usernames:
            if self.verbose:
                await ctx.send(f'{ctx.author.name}, you are not a member of the previos wheel!')
            return
        else:
            odds = usernames.count(username)
            for _ in range (odds):
                usernames.append(username)
            doubled_odds_usernames.append(username)
            await ctx.send(f'{ctx.author.name}, your chances have been doubled!')

    @commands.command(name='getWheel')
    async def getWheel_command(self, ctx):
        """Command: getWheel:
        
            executable only by users in allowed_users
            Uses the current stored list usernames to update OR create a private wheel
            A new wheel is created if:
                * the wheel named defined in config.json doesn't exist in the user's private wheels
            An existing wheel is updated if:
                ** the wheel named defined in config.json does exist in the user's private wheels

            The wheel created can be accessed through the website.
        
        """

        if not self.is_user_allowed(ctx.author):
            if self.verbose:
                await ctx.send(f'{ctx.author.name}, you are not allowed to create a wheel.')
            return

        wheel = {
            'config': {
                'title': config['wheel_name'],
                'description': 'A wheel of elite Ghostdivers.',
                'entries': [{'text': user} for user in usernames]
            }
        }

        url = 'https://wheelofnames.com/api/v1/wheels/private'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, application/xml',
            'x-api-key': API_KEY
        }

        try:
            response = requests.put(url, headers=headers, data=json.dumps(wheel))
            response.raise_for_status()
            jsonResponse = response.json()
            path = jsonResponse['data']['path']
            print("wheel created! go check it out in your account!")
        
        except Exception as e:
            print('Failed to create the wheel. Please try again later.')


    @commands.command(name='loadWheel')
    async def loadWheel_command(self, ctx):
        """Command: loadWheel
            Executeable only by users in allowed_users
            once called, grabs the users from the wheel named in the config "wheel_name"
            and replaces the array  usernames with the content retrieved.
            This is questionable behaviour, but unsure of the requirements here we are.    
        """

        if not self.is_user_allowed(ctx.author):
            if self.verbose:
                await ctx.send(f'{ctx.author.name}, you are not allowed to create a wheel.')
            return
        
        url = "https://wheelofnames.com/api/v1/wheels/private"
        headers = {
            'Accept': 'application/json',
            'x-api-key': API_KEY
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            jsonresponse = response.json()

            wheels = jsonresponse['data'] ['wheels']
            wheel_name = config['wheel_name']
            wheel_found = None
            for wheel in wheels:
                if wheel['config']['title'] == wheel_name:
                    wheel_found = wheel
                    break

        except Exception as e:
            print(f'Failed to load the wheel. try again later. Error {e}')

        if wheel_found:
            entries = wheel_found['config']['entries']
            usernames.clear()
            usernames.extend([entry['text'] for entry in entries])               
            await ctx.send(f'Users on Wheel {wheel_name} has been loaded!')
        else:
            await ctx.send(f'Wheel named {wheel_name} has not been found from the account!')


if __name__ == '__main__':
    bot = TwitchBot()
    bot.run()