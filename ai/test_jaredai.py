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

        state.turn_type = 'Place'
        getAction(state, time_left=None)
        self.fail()

    def test_update_exp_rewards(self):
        #old values testing for multiple players
        #curr_values = [{0: 10, 1: 20, 2: 30}, {0: 50, 1: 10, 2: 20}, {0: 10, 1: 30, 2: 30}]
        probs = [0.1, 0.4, 0.5]
        curr_values = [10, 50, 10]

        result = update_exp_attack_reward(curr_values, probs)
        print("done with test")

    def test_placement(self):
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

        state.owners = [0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                        1, 0, 1, 1, 0, 0, 0, 0, 0, 0]
        state.armies = [1, 4, 1, 1, 3, 2, 3, 1, 3, 1, 1, 2, 2, 1, 1, 1, 2, 1, 1, 1, 3, 1, 3, 1, 1, 1, 1, 2, 2, 1, 1, 1,
                        2, 1, 2, 1, 1, 1, 1, 2, 1, 1]

        state.turn_type = 'Place'
        for i in range(40):
            action = getAction(state, time_left=None)
            print(state.players[state.current_player].free_armies)
            risktools.simulateAction(state, action)
            state.players[state.current_player].free_armies -= 1
            print(state.players[state.current_player].free_armies)
        self.fail()

    def test_index(self):
        test_array = [0, 0]
        obj = test_array[3]
        print(obj)

    def test_attack_search(self):
        board = risktools.loadBoard("../world.zip")

        # Create the players
        for name in ['A', 'B']:
            ap = risktools.RiskPlayer(name, len(board.players), 0, False)
            board.add_player(ap)

        state = risktools.getInitialState(board)
        state.from_string('RISKSTATE|"A".0.[15].7.false;"B".1.[5, 5, 16, 6].0.false;|[1, 1, 1, 1, 4, 2, 3, 3, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 2, 4, 3, 2, 2, 1, 1, 1]|[1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|0|"Place"|[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]|5|1|4', board)

        for i in range(14):
            action = getAction(state, time_left=None)
            risktools.simulateAction(state, action)
            state.players[state.current_player].free_armies -= 1
        print("end test")

