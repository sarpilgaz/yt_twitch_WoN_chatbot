import time
from collections import deque
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YtBot:
    def __init__(self, bot_manager, verbosity,  flow, livestream_id):
        """fields:
        start_time: record the starting time of the bot to prevent is from reading messages before it starts
        credentials: the credentials received from the oauth flow passed to the constructor
        bot_manager: the bot manager singleton that has the command executions and shared data
        livestream_id: the Id of the livestream the bot will conecct to
        livestream_chat_id: the id of the livestream's chat. Will be set at the end of the constructor
        verbose: verbosity of the commands executed as defined in the config.json
        paging_token: paging token received from the polling API request to the chat.
        MAX_MESSAGES: maximum number of messages that will be stored before deleting the oldest messages
        MIN_INTERVAL: the minimum interval required between two of the same command from a person to be processed.
        all_messages: a set of all messages sent to the chat
        unread_messages: a double-ended queue for messages that were unprocessed for commands
        """

        self.start_time = datetime.now(timezone.utc)
        self.credentials = flow.credentials
        self.bot_manager = bot_manager
        self.livestream_id = livestream_id
        self.livestream_chat_id = None
        self.verbose = verbosity
        self.paging_token = None
        self.pollingIntervalMillis = 0
        self.MAX_MESSAGES = 300
        self.MIN_INTERVAL = timedelta(seconds=1)

        #building of the youtube service object
        self.youtube = build('youtube', 'v3', credentials=self.credentials)

        #collection of tuples of userId who sent the message, the message sent, and the timestamp
        self.all_messages = set()
        self.unread_messages = deque(maxlen=self.MAX_MESSAGES)

        #get the chat identification from the stream id
        self.__get_streamchat_Id()

    def __get_streamchat_Id(self):
        """get, and set the id of the livechat, from the id of a stream
        return value is the id of the livechat
        """
        try:
            stream = self.youtube.liveBroadcasts().list(
                part="snippet",
                id=self.livestream_id
            )
            response = stream.execute()
            self.livestream_chat_id = response['items'][0]['snippet']['liveChatId']
        except HttpError as e:
            status = e.resp.status
            if status == 403:
                print("Error: Insufficient permissions to access the live stream. Check API scope and user permissions.")
            if status == 404:
                print(f"Error: Stream with ID {self.livestream_id} not found.")
            else:
                print(f"An unexpected error occurred: {e}")


    def __get_user_name(self, userId):
        """given a userid, return the channel name, aka the username"""
        channelDetails = self.youtube.channels().list(
            part="snippet",
            id=userId,
        )
    
        response = channelDetails.execute()
        return response['items'][0]['snippet']['title']
    
    def __send_reply_to_livechat(self, message):
        """
        given a message, send the message to the chat
        """
        try:
            reply = self.youtube.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": self.livestream_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": message,
                        }
                    }
                }
            )
            response = reply.execute()
        except HttpError as e:
            status = e.resp.status
            if status == 403:
                print("Error: Insufficient permissions to access the live stream. Check API scope and user permissions.")
            if status == 404:
                print(f"Error: Stream with ID {self.livestream_id} not found.")
            else:
                print(f"An unexpected error occurred: {e}")
    
    def __grab_messages(self):
        """"Grabs chat messages according to paging token, and sets pollingIntervalMillis

        return value is an array of livechat message objects, ready for further processing.
        """
        latest_chat = None
        try:
            #if paging token is unset, this is the first request, try to grab everything
            if self.paging_token is None:
                latest_chat = self.youtube.liveChatMessages().list(
                    liveChatId=self.livestream_chat_id,
                    part="snippet"
                )
            else:
                latest_chat = self.youtube.liveChatMessages().list(
                    liveChatId=self.livestream_chat_id,
                    part="snippet",
                    pageToken=self.paging_token
                )
            response = latest_chat.execute()
            self.paging_token = response['nextPageToken']
            self.pollingIntervalMillis = response['pollingIntervalMillis']

            return response['items']

        except HttpError as e:
            status = e.resp.status
            if status == 403:
                print("Error: Insufficient permissions to access the live stream. Check API scope and user permissions.")
            if status == 404:
                print(f"Error: Chat not found not found.")
            else:
                print(f"An unexpected error occurred: {e}")
    
    def __setup_unread_messages(self, livechat_message_objects):
        """function to setup the arrays all_messages and unread_messages 
        for actual command processing.

        parameter is livechat_message object retreived from the API call made
        in function __grab_messages

        at the end, unread_messages field is setup with messages yet unprocessed 
        for commands. 
        """

        for message_obj in livechat_message_objects:
            userId = message_obj['snippet']['authorChannelId']
            message = message_obj['snippet']['textMessageDetails']['messageText']
            timestamp = message_obj['snippet'] ['publishedAt']

            message_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
            
            #ignore messages if they were before start time of the bot
            message_tuple = (userId, message, message_time)


            # Check for recent duplicate messages by the same user
            if not any(
                userId == msg[0] and message == msg[1] and message_time - msg[2] < self.MIN_INTERVAL
                for msg in self.all_messages
            ):
                self.unread_messages.append((userId, message, message_time))
                self.all_messages.add(message_tuple)

                # Ensure `all_messages` only holds the last 300 unique messages
                if len(self.all_messages) > self.MAX_MESSAGES:
                    # Remove the oldest message to maintain the limit
                    oldest_message = next(iter(self.all_messages))
                    self.all_messages.remove(oldest_message)

    def __process_for_commands(self):
        """function to process the messages in unread_messages for commands.
        currently, only !wheel and !here are allowed in the youtube bot.
        the syntax for the commands is precise.
        
        """
        to_remove = []  # Collect messages to remove after processing

        for message in self.unread_messages:
            userId = message[0]
            message_text = message[1]
            time = message[2]

            #if the message was sent before the bot started, ignore
            if time < self.start_time:
                continue

            username = self.__get_user_name(userId)

            if message_text == "!wheel":
                self.__wheel_command(username)
            elif message_text == "!here":
                self.__here_command(username)

            to_remove.append(message)  # Mark message for removal

        #remove all processed messages
        for message in to_remove:
            self.unread_messages.remove(message)


    def __wheel_command(self, username):
        """function to try to add a given username to the list of wheel candidates
        simply calls the corresponding function from the bot manager
        """
        ret = self.bot_manager.add_username_to_wheel(username)
        match ret:
            case -3:
                if self.verbose:
                    self.__send_reply_to_livechat(f'{username}, the bot is not currently listening for usernames.')
            case -2:
                if self.verbose:
                    self.__send_reply_to_livechat('Maximum name limit has been reached')
            case -1:
                if self.verbose:
                    self.__send_reply_to_livechat(f'{username}, you are already on the wheel!')
            case 0:
                self.__send_reply_to_livechat(f'{username}, you have been added to the wheel!')
    
    def __here_command(self, username):
        """function to try to add a given username to the list of wheel candidates
        simply calls the corresponding function from the bot manager
        """
        ret = self.bot_manager.double_odds(username)
        match ret:
            case -4:
                if self.verbose:
                    self.__send_reply_to_livechat('doubling odds is not allowed during active listening')
            case -3:
                if self.verbose:
                    self.__send_reply_to_livechat('doubling odds is not allowed right now.')
            case -2:
                if self.verbose:
                    self.__send_reply_to_livechat(f'{username}, you already doubled your odds once')
            case -1:
                if self.verbose:
                    self.__send_reply_to_livechat(f'{username}, you are not a member of the previos wheel!')
            case 0:
                self.__send_reply_to_livechat(f'{username}, your chances have been doubled!')


    def run(self):
        """
        main bot loop that handles everything
        should run forever until the applciation is closed
        """
        self.__send_reply_to_livechat("connection made!")

        while True:
            message_objs = self.__grab_messages()

            self.__setup_unread_messages(message_objs)

            self.__process_for_commands()

            #calculate the time in seconds before we are allowed to poll 
            # for the next set of messages, wait a default of 5 seconds
            interval = self.pollingIntervalMillis / 1000 if self.pollingIntervalMillis else 5

            time.sleep(interval)

