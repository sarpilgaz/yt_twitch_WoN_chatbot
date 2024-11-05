import time
from googleapiclient.discovery import build

class YtBot:
    def __init__(self, bot_manager, verbosity,  flow, livestream_id):
        self.credentials = flow.credentials
        self.bot_manager = bot_manager
        self.livestream_id = livestream_id
        self.livestream_chat_id = None
        self.verbose = verbosity
        self.youtube = build('youtube', 'v3', credentials=self.credentials)

        self.all_messages = []
        self.unread_messages = []

        self.get_streamchat_Id()

    def get_streamchat_Id(self):
        """get, and set the id of the livechat, from the id of a stream
        return value is the id of the livechat
        """
        stream = self.youtube.liveBroadcasts().list(
            part="snippet",
            id=self.livestream_id
        )
        response = stream.execute()
        print()
        self.livestream_chat_id = response['items'][0]['snippet']['liveChatId']

    def getUserName(self, userId):
        """given a userid, return the channel name, aka the username"""
        channelDetails = self.youtube.channels().list(
            part="snippet",
            id=userId,
        )
    
        response = channelDetails.execute()
        return response['items'][0]['snippet']['title']
    
    def sendReplyToLiveChat(self, message):
        """
        given a message, send the message to the chat
        """
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