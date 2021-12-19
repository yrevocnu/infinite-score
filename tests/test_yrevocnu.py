
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
        a.select("C")
        
        self.assertTrue(self.game.p['B'].meta['fullname'] == 'Bob')
        b = self.game.p['B']
        c = self.game.p['C']

        c.select('D')
        d = self.game.p['D']

        # tests Event creation

        e0 = self.game.begin_event(0, a)

        # because of bounty from metadata
        self.assertEquals(b.account.balance, -1)
        self.assertEqual(len(self.game.bounties), 2)

        ## tests Houses

        c.join(yre.houses['fruits'], event = e0)
        a.join(yre.houses['woods'], event = e0)
        b.join(yre.houses['reef'], event = e0)

        self.assertEquals(b.account.balance, 0)
        d.join(yre.houses['woods'], event = e0)

        self.assertTrue('B' in yre.houses['reef'].members)

        ## players attend the event

        e0.involves(a)
        e0.involves(b)
        self.assertEquals(b.account.balance, 1)
        e0.involves(c)
        e0.involves(d)

        # organizer bonus (5) + house joining bonus (1) + attendance (1)
        self.assertTrue(a.account.balance == 7)
        # house joining bonus (1) + attendance (1) - bounty escrow (1)
        self.assertTrue(c.account.balance == 2)

        # just a smoke test
        pn = self.game.player_network()
        self.assertTrue(len(pn.nodes) == 4)

        c.select('E')

        e = self.game.p['E']

        e1 = self.game.begin_event(1, b)

        e.join(yre.houses['reef'], event = e1)

        e1.involves(c)
        e1.involves(d)
        e1.involves(e)

        # 2 from event 0 + 1 attendance + 1 bounty award
        self.assertEquals(c.account.balance, 4)



