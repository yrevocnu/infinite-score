
import unittest

import sys, os
testdir = os.path.dirname(__file__)
srcdir = '../yrevocnu'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

import yrevocnu as yre

class GameTest(unittest.TestCase):
    def setUp(self):
        self.game = yre.Game()
        self.game.load_bounty_metadata(os.path.abspath(os.path.join(testdir, "test_bounties.yml")))
        self.game.load_event_metadata(os.path.abspath(os.path.join(testdir, "test_events.yml")))
        self.game.load_player_metadata(os.path.abspath(os.path.join(testdir, "test_players.yml")))
      
class test_Game(GameTest):
    def test_load_data(self):
        self.assertTrue('open' in self.game.bounty_metadata)
        self.assertTrue(1 in self.game.events_metadata)
        self.assertTrue('A' in self.game.player_metadata)

class test_playthrough(GameTest):
    """
    An 'integration test' across several Yrevocnu game elements.
    """

    def test_new_players(self):
        a = yre.Player('A')

        a.join(self.game)
        self.assertTrue(a.meta['fullname'] == 'Alice')
        self.assertTrue('A' in self.game.p)

        a.select("B")

        self.assertTrue(self.game.p['B'].meta['fullname'] == 'Bob')
        b = self.game.p['B']

        # tests Event creation

        e0 = self.game.begin_event(0, a)

        ## tests Houses

        a.join(yre.houses['woods'], event = e0)
        b.join(yre.houses['reef'], event = e0)

        self.assertTrue('B' in yre.houses['reef'].members)

        ## players attend the event

        e0.involves(a)
        e0.involves(b)

        # organizer bonus (5) + house joining bonus (1) + attendance (1)
        self.assertTrue(a.account.balance == 7)
        self.assertTrue(b.account.balance == 2)

        # just a smoke test
        pn = self.game.player_network()
        self.assertTrue(len(pn.nodes) == 2)
