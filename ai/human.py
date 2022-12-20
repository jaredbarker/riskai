import random
from risktools import *
# For interacting with interactive GUI
from gui.aihelper import *
from gui.turbohelper import *


### RANDOM AI ####
#
#  This AI always chooses an action uniformly at random from the allowed actions
#  This results in an AI that behaves erratically, but doesn't push to end the game
#  Any reasonable AI should beat this easily and consistently


def getAction(state, time_left=None):
    """Main AI function.  It should return a valid AI action for this state."""
    print("Human's turn!")
    # Get the possible actions in this state
    actions = getAllowedActions(state)

    for i in range(len(actions)):
        print(f"{i}: {actions[i].to_string()}")

    myaction = actions[int(input("Action index: "))]


    # Select a Random Action
    return myaction


# Code below this is the interface with Risk.pyw GUI version
# DO NOT MODIFY

def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    action = getAction(game_state)
    return translateAction(game_state, action)


def Assignment(player):
    # Need to Return the name of the chosen territory
    return aiWrapper('Assignment')


def Placement(player):
    # Need to return the name of the chosen territory
    return aiWrapper('Placement')


def Attack(player):
    # Need to return the name of the attacking territory, then the name of the defender territory
    return aiWrapper('Attack')


def Occupation(player, t1, t2):
    # Need to return the number of armies moving into new territory
    occupying = [t1.name, t2.name]
    return aiWrapper('Occupation', occupying)


def Fortification(player):
    return aiWrapper('Fortification')


"""def get_attack(actions, state: RiskState):
    depth = 5

    best_move = 0
    best_move_value = -numpy.inf

    for i in range(len(actions)):
        new_states, probs = risktools.simulateAttack(state, actions[i])
        exp_values = list()

        for j in range(len(new_states)):
            exp_values.append(attack_expectimax_search(new_states[j], depth-1,))

        value = update_exp_attack_reward(exp_values, probs)

        if value[state.current_player] > best_move_value:
            best_move_value = value[state.current_player]
            best_move = i

    return actions[best_move]


def attack_expectimax_search(state: RiskState, depth):
    if depth == 0:
        return risk_eval(state)

    valid_actions = risktools.getAllowedActions(state)
    
    for i in range(len(valid_actions)):
        if not dice_advantage(valid_actions[i], state):
            valid_actions.pop(i)

    values = list()
    for i in range(len(valid_actions)):
        new_states, probs = risktools.simulateAttack(state, valid_actions[i])
        exp_values = list()

        for j in range(len(new_states)):
            exp_values.append(attack_expectimax_search(new_states[j], depth-1))

        values.append(update_exp_attack_reward(exp_values, probs))

    return max(values, key=lambda value: value[state.current_player])


def risk_eval(state: RiskState):
    values = dict()
    for player in state.players:
        pass

    return values
    
    
def update_exp_attack_reward(curr_values, probs):
    exp_value = dict()
    for player in curr_values[0]:
        exp_value.update({player: (curr_values[0][player] * probs[0])})
    for i in range(1, len(curr_values)):
        for player in curr_values[i]:
            prev = exp_value[player]
            exp_value.update({player: (prev + (curr_values[i][player] * probs[i]))})
    return exp_value"""
