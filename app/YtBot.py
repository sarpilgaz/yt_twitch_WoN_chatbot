import time
import random
from googleapiclient.discovery import build

class YtBot:
    def __init__(self, bot_manager,  flow):
        self.credentials = flow.credentials
        self.bot_manager = bot_manager

        self.youtube = build('youtube', 'v3', credentials=self.credentials)
        print("uuuuhhhhh?? worked??")