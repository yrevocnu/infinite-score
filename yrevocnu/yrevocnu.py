import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

## Configuration. TODO: Move to a config file.
JOINING_HOUSE_AWARD = 1

ORGANIZER_AWARD = 5

LOW_HOUSE_COMMANDER_AWARD = 2

class Game():
    
    def __init__(self):
        self.board = {}
        self.p = {}
        
    def add_player(self, player):
        if player.name not in self.p:
            self.p[player.name] = player
        else:
            raise Exception(f"{player.name} has already joined the game.")
        
    def lookup_player(self, name):
        return self.p[name]
        
    def __repr__(self):
        return f"<Game Players:{list(self.p.keys())}>"

class Player():
    
    def __init__(self, name, selector = None, **meta):
        self.name = name
        self.house = None
        self.selector = None
        self.meta = meta
        
        self.event_joined = None
        
        self.account = SamsaraCoinAccount()
        
        if type(selector) is Player: 
            self.selector = selector
        elif type(selector) is str:
            self.selector = self.game.lookup_player(name)
        
    def join(self, entity, event = None):
        
        if self.event_joined is None:
            self.event_joined = event
        
        if type(entity) is Game:
            self.game = entity
            entity.add_player(self)
        elif type(entity) is House or entity is None:
            if self.house is not None:
                self.house.remove_member(self)
            
            self.house = entity
            
            if entity is not None:
                entity.add_member(self)
                
                ## TODO: Move to event rule
                self.account.transact(JOINING_HOUSE_AWARD)
        
    def select(self, new_name, **meta):
        new_player = Player(new_name, selector = self, **meta)
        new_player.join(self.game)
        
class House():
    
    def __init__(self, name):
        self.name = name
        self.members = {}
        
    def add_member(self, player):
        self.members[player.name] = player
        
    def remove_member(self, player):
        del self.members[player.name]
                              
    def __repr__(self):
        return f"<House:{self.name}; Members:{list(self.members.keys())}>"

class Event():
    
    future_ball = None
    
    def __init__(self, organizer, succeeds = None):
        self.attendees = {}
        self.organizer = organizer
        
        ## TODO: Move to event loop -- really this happens when the event _happens_
        self.organizer.account.transact(ORGANIZER_AWARD)
        
        if succeeds is not None:
            succeeds.future_ball = self
        
    def involves(self, player, amount = 1.0):
        if player in self.attendees:
            raise Exception(f"{player.name} is already involved in this Event.")
        
        self.attendees[player] = amount
        
        ## TODO: Move to event rule
        player.account.transact(amount)

class SamsaraCoinAccount():
    ## TODO : The account keeps track of the history of transactions with notes
    
    def __init__(self):
        self.balance = 0
    
    def transact(self, value, note = None):
        self.balance += value
        
    def transfer(self, account, value, note = None):
        account.transact(value)
        self.balance += - value
        
class SoulBounty():
    
    def __init__(self, issuer, description, value, open_event = None, long_description = None):
        self.issuer = issuer
        self.description = description
        
        self.long_description = long_description
        
        self.target = None
        self.awardee = None
        
        self.open_event = open_event
        self.close_event = None
        
        self.value = value
        self.account = SamsaraCoinAccount()
        
        # hold the value of the bounty in escrow
        self.issuer.account.transfer(self.account, value)
        
    def cancel(self):
        if self.awardee is not None:
            raise Exception("Bounty has already been awarded and cannot be canceled.")

        self.account.transfer(self.issuer, self.value)
        del self.account
        
    def fulfill(self, target):
        print(f"Bounty fulfilled by {target.name}, award goes to {target.selector.name}")
        self.target = target
        self.awardee = target.selector
        
        self.account.transfer(self.awardee.account, self.value)
        del self.account
        
        # figure out what to do here; you should be able to collect multiple epitaphs?
        self.target.epitaph = self 
        self.close_event = self.target.event_joined