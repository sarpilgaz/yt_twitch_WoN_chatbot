import requests
import json
import threading

#TODO: do we need a mechanism to flush doubled_odds_usernames during execution?

class BotManager:
    def __init__(self, max_users, won_key, admins, wheel_name):
        """fields:
        usernames: list of usernames whoare part of the wheel
        doubled odds usernames: a set of usernames who doubled their odds once during the execution of the bots
        MAX USERS: maximum amount of users allowed to be on a wheel, defined in the config
        WON_KEY: the wheel of names API key for user, whose wheels will be accessed and changed
        usernames and toggle locks: thread locks to guarantee mutual exclusion to shared data objects
        allowed users: privilaged users defined in the config who are allowed to use privilaged commands
        wheel name: name of the wheel that will be acted upon for wheel of name commands.
                    If the given wheel name doesnt exist when creating a wheel, a new wheel wil be made, 
                    otherwise, the existing one is edited
                    If the given wheel with name doesnt exist when trying to load from, a failure is given, and an exection is raised  
        """

        self.usernames = []
        self.doubled_odds_usernames = set()
        self.MAX_USERS = max_users
        self.WON_KEY = won_key
        self.usernames_lock = threading.Lock()
        self.toggle_lock = threading.Lock()
        self.allowed_users = admins
        self.wheel_name = wheel_name

        self.listening = False
        self.doubling_allowed = False

    def __is_user_allowed(self, user):
        """Helper function to check if the user is allowed to run certain commands."""
        return user.lower() in self.allowed_users

    def __unique_usernames(self):
        """helper function to return the count of unique usernames"""
        return len(set(self.usernames))
    
    def toggle_listening(self, user, toggle) -> int:
        """"toggle for the bots to allow or disallow the collection of usernames
        exit codes:
        -2 random failure, should never happen tbh
        -1: given user is not privilaged, therefore cannot execute this command
        0: success
        """
        if not self.__is_user_allowed(user):
            return -1

        #critical section
        self.toggle_lock.acquire()

        self.listening = toggle

        self.toggle_lock.release()

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
        if not self.__is_user_allowed(user):
            return -1
    
        #critical section
        self.toggle_lock.acquire()

        self.doubling_allowed = not self.doubling_allowed

        self.toggle_lock.release()

        if self.doubling_allowed: return 1 
        else: return 0 

    
    def add_username_to_wheel(self, username) -> int:
        """add a given username to the list.
        exit codes:
        -3: bots are not allowed to listen currently
        -2: Maximum name limit has been reached
        -1: Given username is already present in the list
        0: success 
        """
        if not self.listening:
            return -3

        if self.__unique_usernames() >= self.MAX_USERS:
            return -2
        
        if username in self.usernames:
            return -1
        
        #critical section
        self.usernames_lock.acquire()

        self.usernames.append(username)

        self.usernames_lock.release()
        return 0
    
    def double_odds(self, username) -> int:
        """
        double the odds of a given username, essentialls doubling their occurance in the list
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
        
        #critical section
        self.usernames_lock.acquire()

        odds = self.usernames.count(username)
        for _ in range (odds):
            self.usernames.append(username)
        self.doubled_odds_usernames.add(username)

        self.usernames_lock.release()

        return 0
    
    def create_wheel(self, username):
        """create a wheel from the usernames list stored. The private wheel is created in the account of the key holder
        if the wheel name defined in the config doesn't exist, a wheel will be created, if it exists, then the wheel will be overriden instead
        exit codes:
        -2: Wheel of names API error occured
        -1: given username is not allowed to run this command
        0: success
        """

        if not self.__is_user_allowed(username):
            return -1

        if self.listening:
            return -2

        #critical section
        self.usernames_lock.acquire()

        wheel = {
            'config': {
                'title': self.wheel_name,
                'description': 'A wheel of elite Ghostdivers.',
                'entries': [{'text': user} for user in self.usernames]
            }
        }

        self.usernames_lock.release()

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

            self.usernames_lock
            return 0
            
        
        except Exception as e:
            return -2
        
    def load_wheel(self, username):
        """load a wheel with the name defined in the config file into the list.:
        -2: Wheel of names API error occured
        -1: given username is not allowed to run this command
        0: success
        """
        if not self.__is_user_allowed(username):
            return -1

        if self.listening:
            return -2        
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
            #critical section
            self.usernames_lock.acquire()

            #if a wheel is found, grab the usernames from entries section
            entries = wheel_found['config']['entries']
            self.usernames.clear()
            self.usernames.extend([entry['text'] for entry in entries])

            self.usernames_lock.release()
            return 0               
        else:
            return -2
