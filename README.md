# infinite-score
_An infinite game score engine_

_score. noun_

_1. the number of points, goals, runs, etc. achieved in a game or by a team or an individual._

_2. a written representation of a musical composition showing all the vocal and instrumental parts arranged one below the other._

An engine for maintaining an infinite game score.

Currently only supports the rule set of Yrevocnu, specifically the game of Yrevocnu that began at the Glass Bead Symposium in 2018.

Future versions of `infinite-score` will support infinite games more generally.

## Yrevocnu Rules

### Game

Everything is part of the Game.

A lot of metadata about a particular game, such as about individual events, players, and bounties, are stored in .yml files.

### Player

Players can:

 - Select other players to enter the game
 - Join the game
 - Join a House
 
### Event

Events are discrete moments of the Game. Events are numbered. They are organized by a single Player. They succeed other Events.

Events can involve Players to variable degrees (default is 1).

### SamsaraCoinAccounts and Bounties

Each player has an account of an in-game currency, SamsaraCoin (SC)

SC can be transferred between accounts or put into escrow for a Bounty.

A Bounty is fulfilled when a Player fitting its description joins the Game in an Event.
This information is tracked in a YAML metadata file.

The Player who selected the Bounty target gets the award.

### Visualization

This package supports the visualization of a network which shows the participants in a particular event.

You can use it like this:

    draw_player_network(game,game.e[1])

This will draw a picture of the network of players involved in Event 1.

