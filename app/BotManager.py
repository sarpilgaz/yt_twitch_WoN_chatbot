import requests
import json
import asyncio

#TODO: do we need a mechanism to flush doubled_odds_usernames during execution?

class BotManager:
    def __init__(self, max_users, won_key, admins, wheel_name):
        self.usernames = []
        self.doubled_odds_usernames = set()
        self.MAX_USERS = max_users
        self.WON_KEY = won_key
        self.usernames_lock = asyncio.Lock()
        self.allowed_users = admins
        self.wheel_name = wheel_name

        self.listening = False
        self.doubling_allowed = False

    def is_user_allowed(self, user):
        """Helper function to check if the user is allowed to run certain commands."""
        return user.lower() in self.allowed_users

    def unique_usernames(self):
        """helper function to return the count of unique usernames"""
        return len(set(self.usernames))
    
    def toggle_listening(self, user, toggle) -> int:
        """"toggle for the bots to allow or disallow the collection of usernames
        exit codes:
        -2 random failure, should never happen tbh
        -1: given user is not privilaged, therefore cannot execute this command
        0: success
        """
        if not self.is_user_allowed(user):
            return -1
    
        self.listening = toggle

        if self.listening != toggle:
            return -2
        else: return 0

    def toggle_doubling(self, user) -> int:
        """"toggle for the bots to allow or disallow the doubling of username odds
            so, allow the use of !here command
        exit codes:
        -1: given user is not privilaged, therefore cannot execute this command
        0: success, doubling is not allowed
        1: success, doubling is allowed
        """
        if not self.is_user_allowed(user):
            return -1
    
        self.doubling_allowed = not self.doubling_allowed

        if self.doubling_allowed: return 1 
        else: return 0 

    
    async def add_username_to_wheel(self, username) -> int:
        """add a given username to the list.
        exit codes:
        -3: bots are not allowed to listen currently
        -2: Maximum name limit has been reached
        -1: Given username is already present in the list
        0: success 
        """
        if not self.listening:
            return -3

        if self.unique_usernames() >= self.MAX_USERS:
            return -2
        
        if username in self.usernames:
            return -1
        
        async with self.usernames_lock:
            self.usernames.append(username)
        
        return 0
    
    async def double_odds(self, username) -> int:
        """double the odds of a given username, essentialls doubling their occurance in the list
        exit codes:
        -4: doubling odds is not allowed during active listening, 
        -3: doubling was not allowed yet
        -2: username has already double their odds once this stream
        -1: the username cannot double their odds, because they don't occur at least once already in the list usernames
        0: success
        """
        if self.listening:
            return -4
        
        if not self.doubling_allowed:
            return -3

        if username in self.doubled_odds_usernames:
            return -2
        
        if username not in self.usernames:
            return -1
        
        async with self.usernames_lock:
            odds = self.usernames.count(username)
            for _ in range (odds):
                self.usernames.append(username)
            self.doubled_odds_usernames.add(username)

        return 0
    
    def create_wheel(self, username):
        """create a wheel from the usernames list stored. The private wheel is created in the account of the key holder
        exit codes:
        -2: Wheel of names API error occured
        -1: given username is not allowed to run this command
        0: success
        """

        if not self.is_user_allowed(username):
            return -1

        wheel = {
            'config': {
                'title': self.wheel_name,
                'description': 'A wheel of elite Ghostdivers.',
                'entries': [{'text': user} for user in self.usernames]
            }
        }

        url = 'https://wheelofnames.com/api/v1/wheels/private'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, application/xml',
            'x-api-key': self.WON_KEY
        }

        try: #response is not used for anything currently, could be removed in the future.
            response = requests.put(url, headers=headers, data=json.dumps(wheel))
            response.raise_for_status()
            jsonResponse = response.json()
            path = jsonResponse['data']['path']
            return 0
            
        
        except Exception as e:
            return -2
        
    def load_wheel(self, username):
        """load a wheel with the name defined in the config file into the list.:
        -2: Wheel of names API error occured
        -1: given username is not allowed to run this command
        0: success
        """
        if not self.is_user_allowed(username):
            return -1
        
        url = "https://wheelofnames.com/api/v1/wheels/private"
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.WON_KEY
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            jsonresponse = response.json()

            wheels = jsonresponse['data'] ['wheels']
            #grab the wheel name from the llocal config file
            wheel_name = self.wheel_name
            wheel_found = None
            #loop over the titles from the json response and grab the wheel that matches the name.
            for wheel in wheels:
                if wheel['config']['title'] == wheel_name:
                    wheel_found = wheel
                    break

        except Exception as e:
            return -2

        if wheel_found:
            #if a wheel is found, grab the usernames from entries section
            entries = wheel_found['config']['entries']
            self.usernames.clear()
            self.usernames.extend([entry['text'] for entry in entries])
            return 0               
        else:
            return -2