
import unittest

import sys, os
testdir = os.path.dirname(__file__)
srcdir = '../yrevocnu'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

import yrevocnu

class GameTest(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.load_bounty_metadata("test_bounties.yml")
        self.game.load_event_metadata("test_events.yml")
        self.game.load_player_metadata("test_players.yml")
        

      
class test_Game(GameTest):
    def test_load_data(self):
        self.assertTrue('open' in self.game.bounty_metadata)
        self.assertTrue(1 in self.game.event_metadata)
        self.assertTrue('A' in self.game.player_metadata)

class test_Player(GameTest):
    def setUp(self):
        return


class test_House(unittest.TestCase):
    def setUp(self):
        return


class test_SamsaraCoinAccount(unittest.TestCase):
    def setUp(self):
        return


class test_SoulBountye(unittest.TestCase):
    def setUp(self):
        return


class test_Game(unittest.TestCase):
    def setUp(self):
        return

