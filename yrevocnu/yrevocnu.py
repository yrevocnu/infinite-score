import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from yaml import safe_load, dump

## Configuration. TODO: Move to a config file.
JOINING_HOUSE_AWARD = 1

ORGANIZER_AWARD = 5

LOW_HOUSE_COMMANDER_AWARD = 2

class Game():
    
    def __init__(self):
        self.board = {}
        
        self.p = {}
        self.player_metadata = {}

        # Yrevocnu specific?
        self.e = {}
        self.events_metadata = {}

        # Yrevocnu specific -- consider moveing to subclass/mixin
        self.bounty_metadata = {}
        self.bounties = {}
        
    def add_player(self, player):
        if player.name not in self.p:
            self.p[player.name] = player
        else:
            raise Exception(f"{player.name} has already joined the game.")

    def begin_event(self, number, organizer, **meta):
        if (number - 1) in self.e:
            succeeds = self.e[(number - 1)]
        else:
            succeeds = None

        if number in self.events_metadata:
            meta.update(self.events_metadata[number])
            ## TODO: Get organzier from event metadata if available.
            ## For now delete and specify in code.

        self.e[number] = Event(number, organizer, succeeds = succeeds, metadata = meta)

        self.open_bounties_from_metadata(self.e[number])

        return self.e[number]

    def open_bounties_from_metadata(self, event, player = None):

        if player is None:
            players = self.p
        else:
            players = {player.name : player}

        for bm in self.bounty_metadata['open']:
            ## TODO: Bug here. New members will not have their bounties auto-loaded from metadata when events begin.
            if bm['open'] == event.number and bm['issuer'] in players and bm['short'] not in self.bounties:
                self.bounties[bm['short']] = SoulBounty.from_metadata(bm, event, players)

        # Also need to add the closed ones, because they are not yet closed _in the simulation_
        for bm in self.bounty_metadata['closed']:
            ## TODO: Bug here. New members will not have their bounties auto-loaded from metadata when events begin.
            if bm['open'] == event.number and bm['issuer'] in players and bm['short'] not in self.bounties:
                self.bounties[bm['short']] = SoulBounty.from_metadata(bm, event, players)

    def load_bounty_metadata(self, filename):
        self.bounty_metadata = safe_load(open(filename))

    def load_event_metadata(self, filename):
        self.events_metadata = safe_load(open(filename))

    def load_player_metadata(self, filename):
        self.player_metadata = safe_load(open(filename))
 
    def lookup_player(self, name):
        return self.p[name]
        
    def __repr__(self):
        return f"<Game Players:{list(self.p.keys())}>"

    def player_network(self):
        """
        Yrevocnu specific: house and selectors
        """
        return player_network(self.p) 

class Player():
    
    def __init__(self, name, selector = None, **meta):
        self.name = name
        self.house = None
        self.selector = None
        self.meta = meta
        
        self.event_joined = None
        
        self.account = SamsaraCoinAccount()
        self.total_attendance = 0
        
        if type(selector) is Player: 
            self.selector = selector
        elif type(selector) is str:
            self.selector = self.game.lookup_player(name)
        
    def join(self, entity, event = None):
        
        # joined game? joined house?
        if self.event_joined is None and event is not None:
            self.event_joined = event
        
        if type(entity) is Game:
            self.game = entity
            if self.name in self.game.player_metadata:
                self.meta.update(self.game.player_metadata[self.name])
            entity.add_player(self)

        elif type(entity) is House or entity is None:
            if self.house is not None:
                self.house.remove_member(self)
            
            self.house = entity
            
            if entity is not None:
                entity.add_member(self)
                
                ## TODO: Move to event rule
                self.account.transact(JOINING_HOUSE_AWARD)

        if event is not None:
            self.game.open_bounties_from_metadata(event, player = self)

        ## bounty specific -- move to an event handler eventually?
        if event is not None:
            bounties_targetting_me = [bm for bm in self.game.bounty_metadata['closed'] if bm['target'] == self.name]
            if len(bounties_targetting_me) > 0:
                for bm in bounties_targetting_me:
                    try:
                        self.game.bounties[bm['short']].fulfill(self)
                    except:
                        # debugging
                        print(b)
                        print(self.game.bounties)
        
    def select(self, new_name, **meta):
        new_player = Player(new_name, selector = self, **meta)
        new_player.join(self.game)
        
class House():
    
    def __init__(self, name, short_name):
        self.name = name
        self.short_name = short_name
        self.members = {}
        
    def add_member(self, player):
        self.members[player.name] = player
        
    def remove_member(self, player):
        del self.members[player.name]
                              
    def __repr__(self):
        return f"<House:{self.name}; Members:{list(self.members.keys())}>"


## Should move to a configuration file
reef = House("Reef Structure", "reef")
woods = House("The Woods", "woods")
fruits = House("Fruits Paradise", "fruits")

houses = {}

houses['reef'] = reef
houses['woods'] = woods
houses['fruits'] = fruits



class Event():
    
    future_ball = None
    
    def __init__(self, number, organizer : Player, succeeds = None, metadata : dict = None):
        self.attendees = {}
        self.organizer = organizer
        self.number = number

        ## TODO: Guarantee consistency between metadata and object attribute organizer
        self.metadata = metadata
        
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
        player.total_attendance += amount

    def player_network(self):
        return player_network({player.name : player for player in self.attendees})

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

    @classmethod
    def from_metadata(cls, metadata, event, players):
        assert(event.number == metadata['open'])
        # construct a Bounty from metadata and return it.
        return cls(
            players[metadata['issuer']],
            metadata['short'],
            metadata['value'],
            open_event = event,
            long_description = (metadata['long'] if 'long' in metadata else None)
        )
        
    def fulfill(self, target):
        print(f"Bounty fulfilled by {target.name}, award goes to {target.selector.name}")
        self.target = target
        self.awardee = target.selector
        
        self.account.transfer(self.awardee.account, self.value)
        del self.account
        
        # figure out what to do here; you should be able to collect multiple epitaphs?
        self.target.epitaph = self 
        self.close_event = self.target.event_joined

### visualization methods

def house_color(house):
    if house == fruits:
        return 'y'
    elif house == woods:
        return '#7BC8A4'
    elif house == reef:
        return 'm'
    else:
        return '#444444'


def player_network(player_dict):
        """
        Yrevocnu specific: house and selectors
        """
        graph = nx.DiGraph()
    
        graph.add_nodes_from([
            (
                pn,
                {
                    "house" : player_dict[pn].house,
                    "player" : player_dict[pn],
                    "total_attendance" : player_dict[pn].total_attendance
                }
            )
            for pn # player name
            in player_dict
        ])
    
        graph.add_edges_from([
            (pn, player_dict[pn].selector.name)
            for pn
            in player_dict
            if player_dict[pn].selector is not None
        ])

        graph = graph.subgraph([pn for pn in player_dict])
    
        return graph   

    
def draw_player_network(game, event = None, size_scale = 300, only_attendees = True):
    pn = game.player_network()
    
    if event is not None and only_attendees:
        pn = pn.subgraph([p.name for p in event.attendees])
    
    node_colors = [house_color(m[1]['house']) for m in list(pn.nodes(data=True))]
    
    if event is not None:
        attendence = {p.name : event.attendees[p] for p in event.attendees}
        node_size = [attendence[pname] * size_scale if pname in attendence else 0.0 for pname in pn.nodes]
    elif size_scale == 'total_attendance':
        node_size = [game.p[pname].total_attendance * 300 for pname in pn.nodes]
    else:
        ## controversial ?!?
        node_size = [1 * size_scale for pname in pn.nodes]
        
        # current bank balance
        # node_size = [game.p[pname].account.balance * size_scale for pname in pn.nodes]

    # need to run layout on a copy of the network with no ':''s in the attributes for some reason.
    pn_double = pn.copy()

    for node, attributes in pn_double.nodes(data=True):
        for attr in list(attributes.keys()):
            del pn_double.nodes[node][attr]


    pos = nx.drawing.nx_pydot.pydot_layout(pn_double)

    if event is not None:
        # gray halo for organizer
        nx.draw_networkx_nodes(
            pn, pos=pos,
            nodelist=[event.organizer.name],
            node_color = '#444444',
            alpha = 0.1,
            node_size = size_scale * 2.5
        )
    
    nx.draw_networkx(
        pn, 
        pos = pos, 
        node_color = node_colors, 
        node_size = node_size, 
        alpha = 0.5
    )
    
    ## old control flow here is cruft.
    ## But should this be optional?
    bounties = game.bounties

    if bounties is not None:
        # get fulfilled bounties
        these_bounties = [
            bounties[b] for b in bounties 
            if bounties[b].close_event is not None and bounties[b].close_event == event
        ]

        print(these_bounties)
        
        if len(these_bounties) > 0:
            bg = nx.DiGraph()
    
            bg.add_edges_from([
                (b.issuer.name, b.target.name)
                for b
                in these_bounties
                if b.issuer.name in pos ## TODO: Deal with this better
            ])
        
            bounty_labels = {
                (b.issuer.name, b.target.name) : b.description
                for b
                in these_bounties
                if b.issuer.name in pos ## TODO: Deal with this better
            }
    
            nx.draw_networkx_edges(
                bg, 
                pos = pos, 
                style = 'dotted',
                alpha = 0.3
            )
    
            # draw the soul bounties
            nx.draw_networkx_edge_labels(
                bg, pos,
                edge_labels=bounty_labels,
                font_color='green',
                alpha = 0.7
            )

    return pn, pos
