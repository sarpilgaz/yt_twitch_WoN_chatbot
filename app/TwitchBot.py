from twitchio.ext import commands

class TwitchBot(commands.Bot):
    """
        Class for the twitch bot, inherits from twitch API bot
        Reads the necessary config from the config populated before
    """
    def __init__(self, bot_manager, tokenn, channels, verbosity):
        """Fields:

            listening: if the bot is collecting usernames for the wheel or not
            doubling_allowed: essentially allows the usage of the command !here, which Doubles the odds of the people already on the wheel.
            verbose: enables or disables extra result reporting for used commands
            allowed_users: privilaged users who are able to execute privilaged commands such as start, stop, etc. These are defined in the file config.json

        """
        super().__init__(token=tokenn, prefix='!', initial_channels=channels)
        self.bot_manager = bot_manager
        self.verbose = verbosity

    async def event_ready(self):
        """initial print to confirm starting of the bot"""
        print(f'Logged in as | {self.nick}')
        print(f'Connected to {self.connected_channels}')

    @commands.command(name='start') 
    async def __start_command(self, ctx):
        """Command: !start

            executable only by users in allowed_users
            allows the bot to listen for users who wish to join the wheel
        
        """
        ret = self.bot_manager.toggle_listening(ctx.author.name, True)

        match ret:
            case -2:
                if self.verbose:
                    await ctx.send("lmao fail, dunno why")
            case -1:
                if self.verbose:
                     await ctx.send(f'{ctx.author.name}, you are not allowed to start the bot.')
            case 0:
                await ctx.send('Now listening for usernames!')

    @commands.command(name='stop')
    async def __stop_command(self, ctx):
        """Command: !stop

            executable only by users in allowed_users
            disallows the bot to listen for users who wish to join the wheel
        
        """
        ret = self.bot_manager.toggle_listening(ctx.author.name, False)

        match ret:
            case -2:
                if self.verbose:
                    await ctx.send("lmao fail, dunno why")  
            case -1:
                if self.verbose:
                    await ctx.send(f'{ctx.author.name}, you are not allowed to stop the bot.')
            case 0:
                await ctx.send('Now stopped listening for usernames!')

    @commands.command(name='odds')
    async def __odds_command(self, ctx):
        """Command: !odds

            executable only by users in allowed_users
            toggles the use permission of !here command. 
        
        """
        ret = self.bot_manager.toggle_doubling(ctx.author.name)

        match ret:
            case -2:
                if self.verbose:
                    await ctx.send("lmao fail, dunno why")
            case -1:
                if self.verbose:
                    await ctx.send(f'{ctx.author.name}, you are not allowed to allow the doubling.')
            case 0:
                await ctx.send('Doubling your odds is now disallowed!')
            case 1:
                await ctx.send('Doubling your odds is now allowed!')


    @commands.command(name='wheel')
    async def __wheel_command(self, ctx):
        """Command: !wheel

            executable by users only after the command !start
            Attempts to add the user to the wheel, if not already present
        
        """
        username = ctx.author.name
        ret = self.bot_manager.add_username_to_wheel(username)

        match ret:
            case -3:
                if self.verbose:
                    await ctx.send(f'{ctx.author.name}, the bot is not currently listening for usernames.')
            case -2:
                if self.verbose:
                    await ctx.send('Reached the maximum number of users. Stopping collection.')
            case -1:
                if self.verbose:
                    await ctx.send(f'{username}, you are already on the wheel!')
            case 0:
                await ctx.send(f'{username} has been added to the wheel!')

    @commands.command(name='here')
    async def __here_command(self, ctx):
        """Command: !here

            executable only after the commands !odds and while the bot is not listening, so before !start
            attempts to double the odds of the user for the wheel if and only if:
                the user is present on the wheel and,
                the user haven't used this command before
   
        """
        
        username = ctx.author.name
        ret = self.bot_manager.double_odds(username)

        match ret:
            case -4:
                if self.verbose:
                    await ctx.send('doubling odds is not allowed during active listening.')
            case -3:
                if self.verbose:
                    await ctx.send('doubling odds is not allowed right now.')
            case -2:
                if self.verbose:
                    await ctx.send(f'{ctx.author.name}, you already doubled your odds once')
            case -1:
                if self.verbose:
                    await ctx.send(f'{ctx.author.name}, you are not a member of the previos wheel!')
            case 0:
                await ctx.send(f'{ctx.author.name}, your chances have been doubled!')

    @commands.command(name='getWheel')
    async def __getWheel_command(self, ctx):
        """Command: getWheel:
        
            executable only by users in allowed_users
            Uses the current stored list usernames to update OR create a private wheel
            A new wheel is created if:
                * the wheel named defined in config.json doesn't exist in the user's private wheels
            An existing wheel is updated if:
                ** the wheel named defined in config.json does exist in the user's private wheels

            The wheel created can be accessed through the website.
        
        """

        ret = self.bot_manager.create_wheel(ctx.author.name)

        match ret:
            case -2:
                print('Failed to create the wheel. Please try again later.')
            case -1: 
                if self.verbose:
                    await ctx.send(f'{ctx.author.name}, you are not allowed to create a wheel.')
            case 0:
                print("wheel created! go check it out in your account!")


    @commands.command(name='loadWheel')
    async def __loadWheel_command(self, ctx):
        """Command: loadWheel
            Executeable only by users in allowed_users
            once called, grabs the users from the wheel named in the config "wheel_name"
            and replaces the array 'usernames' with the content retrieved.
            This is questionable behaviour, but unsure of the requirements here we are.    
        """

        ret = self.bot_manager.load_wheel(ctx.author.name)

        match ret:
            case -2:
                print('Failed to create the wheel. Please try again later.')
            case -1: 
                if self.verbose:
                    await ctx.send(f'{ctx.author.name}, you are not allowed to load a wheel.')
            case 0:
                print(f'Users on Wheel has been loaded!')
