import math
import matplotlib.pyplot as plt
import networkx as nx

from operator import itemgetter

from pprint import pprint as pp
import random

from yrevocnu import (
    Game, 
    Player, 
    House, 
    Event, 
    SamsaraCoinAccount, 
    SoulBounty, 
    draw_player_network,
    reef, 
    woods, 
    fruits
)


def team_leader_score(team, g):
    return max([g.nodes[p]["total_attendance"] for p in team])


def team_dist_score(team, g):
    ## team is a tuple of node labels
    ## Compute area of implied triangle using Heron's Formula
    
    a = nx.shortest_path_length(g,source=team[0],target=team[1]) + 1
    b = nx.shortest_path_length(g,source=team[1],target=team[2]) + 1
    c = nx.shortest_path_length(g,source=team[2],target=team[0]) + 1

    p = (a + b + c) / 2

    return math.log(math.sqrt(p * (p - a) * (p - b) * (p - c)))

def team_blend_score(team, g):
    return 3 * team_dist_score(team, g) + team_leader_score(team, g)
        
def team_assignment_value(teams, g, score_func = team_blend_score):
    return sum(map(score_func,teams, [g.to_undirected()] * len(teams)))


def find_best_team_assigment(phl : dict[str, list[str]], game : Game, score_func = team_blend_score, tries = 500):
    """
    """

    gn = game.player_network()
    values = [0]

    teams = list(zip(*[phl[ph] for ph in phl]))
    value = team_assignment_value(teams, gn, score_func = score_func)

    for i in range(tries):
        new_teams = list(zip(*[random.sample(phl[ph], len(phl[ph])) for ph in phl]))
    
        new_value = team_assignment_value(new_teams, gn, score_func = score_func)
        values.append(new_value)
    
        if new_value > value:
            teams = new_teams
            value = new_value
     
    return teams, value, values

def create_pseudohouses(event, houses = (reef, woods, fruits), to_remove = []):
    """
    Creates pseudohouse lists for the use in the triad algorithm,
    
    Null house members will be assigned to each house list in an appropriate
    (Pattern norm sanctioned) way in order to equalize the number of participants
    in each pseudohouse.
    
    Parameters
    -----------
    
    to_remove: list of strings
        A list of player identifiers to be removed from the lists.
        This is useful for removing judges and those who don't want to play.
    """

    # get base lists for each house, and the Null house
    epn = event.player_network()
    
    house_lists = {h.short_name : [x[0] for x in list(epn.nodes(data=True))
                                   if 'house' in x[1] and x[1]['house'] == h]
                 for h
                 in houses}
    
    null_house_list = [x[0] for x in list(epn.nodes(data=True))
                       if 'house' not in x[1] or x[1]['house'] is None]

    
    # Remove the nonplayers
    for rp in to_remove:
        for hl in house_lists:
            if rp in house_lists[hl]:
                house_lists[hl].remove(rp)
                
        if rp in null_house_list:
            null_house_list.remove(rp)

    players = {p.name : p for p in event.attendees}
            
    for null_player in null_house_list:
        selector_house = players[null_player].selector.house if players[null_player].selector is not None else None
    
        house_options = [
            house_lists[hn] for hn in house_lists 
            if selector_house is None or hn != selector_house.short_name ]
    
        index, element = min(enumerate(house_options), key=lambda x: len(itemgetter(1)(x)))
    
        element.append(null_player)
        
    return house_lists



def draw_event_with_teams(game : Game, event : Event, teams : list[tuple[str]]):

    team_graph = nx.Graph()
    
    for team in teams:
        a = team[0]
        b = team[1]
        c = team[2]
    
        ## surely wrong, but hacking for now
        team_graph.add_edge(a,b, team = True)
        team_graph.add_edge(b,c, team = True)
        team_graph.add_edge(c,a, team = True)
        
    plt.figure(3,figsize=(12,7.5)) 


    epn, epos = draw_player_network(game, event)

    nx.draw_networkx_edges(
        team_graph,
        pos = epos,
        style = ":",
        alpha=0.25
    )