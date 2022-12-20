from unittest import TestCase

import risktools
from ai.jaredai import getAction
from ai.jaredai import update_exp_attack_reward

class JaredGetAction(TestCase):
    def test_get_action(self):
        board = risktools.loadBoard("../world.zip")

        # Create the players
        for name in ['A', 'B']:
            ap = risktools.RiskPlayer(name, len(board.players), 0, False)
            board.add_player(ap)

        # Get initial game state
        state = risktools.getInitialState(board)
        for i in range(len(state.armies)):
            state.owners[i] = 0
            state.armies[i] = 1

        state.armies[38] = 6
        state.owners[39] = 1
        state.owners[40] = 1
        state.owners[41] = 1

        state.owners = [0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0]
        state.armies = [1, 4, 1, 1, 3, 2, 3, 1, 3, 1, 1, 2, 2, 1, 1, 1, 2, 1, 1, 1, 3, 1, 3, 1, 1, 1, 1, 2, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 2, 1, 1]

        state.turn_type = 'Attack'
        getAction(state, time_left=None)
        self.fail()

    def test_update_exp_rewards(self):
        #old values testing for multiple players
        #curr_values = [{0: 10, 1: 20, 2: 30}, {0: 50, 1: 10, 2: 20}, {0: 10, 1: 30, 2: 30}]
        probs = [0.1, 0.4, 0.5]
        curr_values = [10, 50, 10]

        result = update_exp_attack_reward(curr_values, probs)
        print("done with test")
