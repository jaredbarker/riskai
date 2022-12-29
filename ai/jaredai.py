import random
import time

import numpy

import risktools
from risktools import *
# For interacting with interactive GUI
from gui.aihelper import *
from gui.turbohelper import *

placement_total_assigned = False
placement_total = 0
placement_terr = 0

def getAction(state, time_left=None):
    """Main AI function.  It should return a valid AI action for this state."""
    global placement_total_assigned
    global placement_total
    global placement_terr

    if state.turn_type == 'PrePlace' and state.players[state.current_player].free_armies == 19:
        #print(f"Free armies for first player: {state.players[state.current_player].free_armies}")
        final_reward = eval_final_placement(state)
        for player in final_reward:
            print(f"Player {state.players[player].name} has score: {final_reward[player]}")

    if state.turn_type == 'Place' and not placement_total_assigned:
        placement_total_assigned = True
        placement_total = state.players[state.current_player].free_armies

    if state.turn_type == 'Attack' and placement_total_assigned:
        placement_total_assigned = False

    # Get the possible actions in this state
    actions = getAllowedActions(state)

    myaction = random.choice(actions)

    if state.turn_type == 'TurnInCards':
        myaction = actions[0]  # always turn in cards if I can

    if state.turn_type == 'Occupy':
        myaction = max(actions, key=lambda a: a.troops)

    if state.turn_type == 'PreAssign':
        myaction = get_pre_assign(actions, state)

    if state.turn_type == 'Place':
        attack_total = numpy.ceil(placement_total / 2)
        current_armies = state.players[state.current_player].free_armies

        if current_armies > attack_total:
            myaction = get_troop_movement(actions, state)
        elif current_armies == attack_total:
            best_value = -numpy.inf
            best_action = None
            for terr_action in get_bordering_territory_actions(actions, state):
                new_state = state.copy_state()
                place_remaining_armies(new_state, terr_action)
                action_options = []
                attack_actions = getAttackActions(new_state)
                for i in range(len(attack_actions)):
                    if dice_advantage(attack_actions[i], new_state):
                        action_options.append(attack_actions[i])

                temp_action, value = get_attack(action_options, new_state)

                if value > best_value:
                    best_action = temp_action
                    best_value = value

            placement_terr = best_action.from_territory
            for a in actions:
                if a.to_territory == placement_terr:
                    myaction = a
        else:
            for a in actions:
                if a.to_territory == placement_terr:
                    myaction = a

    if state.turn_type == 'PrePlace' or state.turn_type == 'Fortify':
        myaction = get_troop_movement(actions, state)

    if state.turn_type == 'Attack':
        current_valuation = risk_eval(state)
        if current_valuation > 35.0:
            action_index = 0
            while not dice_advantage(actions[action_index], state):
                action_index += 1
            myaction = actions[action_index]
        else:
            action_options = []
            for i in range(len(actions)):
                if dice_advantage(actions[i], state):
                    action_options.append(actions[i])

            if len(action_options) > 1:
                myaction, value = get_attack(action_options, state)
            else:
                myaction = action_options[0]
    # Return the chosen action
    return myaction


def get_attack(actions, state: RiskState):
    #print(state.to_string())
    depth = 3
    best_move = 0
    best_move_value = -numpy.inf
    value = -numpy.inf
    for i in range(len(actions)):
        if actions[i].from_territory is None:
            value = risk_eval(state)
        else:
            new_states, probs = risktools.simulateAttack(state, actions[i])
            exp_values = list()

            for j in range(len(new_states)):
                if new_states[j].armies[new_states[j].board.territory_to_id[actions[i].to_territory]] == 0:
                    new_states[j].players[new_states[j].current_player].conquered_territory = True
                    occupy_actions = getOccupyActions(new_states[j])
                    occupy_action = max(occupy_actions, key=lambda a: a.troops)
                    simulateOccupyAction(new_states[j], occupy_action)

                exp_values.append(attack_search(new_states[j], depth - 1))

            value = update_exp_attack_reward(exp_values, probs)

        if value > best_move_value:
            best_move_value = value
            best_move = i

    return actions[best_move], best_move_value


def attack_search(state: RiskState, depth):
    if depth == 0:
        return risk_eval(state)

    possible_actions = risktools.getAttackActions(state)
    valid_actions = list()
    for i in range(len(possible_actions)):
        if dice_advantage(possible_actions[i], state):
            valid_actions.append(possible_actions[i])

    values = list()
    for i in range(len(valid_actions)):
        if valid_actions[i].from_territory is None:
            values.append(risk_eval(state))
        else:
            new_states, probs = risktools.simulateAttack(state, valid_actions[i])
            exp_values = list()

            for j in range(len(new_states)):
                if new_states[j].armies[new_states[j].board.territory_to_id[valid_actions[i].to_territory]] == 0:
                    new_states[j].players[new_states[j].current_player].conquered_territory = True
                    occupy_actions = getOccupyActions(new_states[j])
                    occupy_action = max(occupy_actions, key=lambda a: a.troops)
                    simulateOccupyAction(new_states[j], occupy_action)

                exp_values.append(attack_search(new_states[j], depth - 1))

            values.append(update_exp_attack_reward(exp_values, probs))

    return max(values)


def risk_eval(state: RiskState):
    final_value = 0.0

    if state.players[state.current_player].conquered_territory:
        final_value += 3.0

    for player in state.players:
        for cont in state.board.continents:
            has_cont = True
            for terr in state.board.continents[cont].territories:
                if state.owners[terr] != player.id:
                    has_cont = False
            if has_cont and player.id != state.current_player:
                final_value -= cont_army_values[cont]
            elif has_cont:
                final_value += cont_army_values[cont]

    final_value += 0.5 * state.owners.count(state.current_player)

    border_armies = 0
    owned_territories = []
    for i in range(len(state.owners)):
        if state.owners[i] == state.current_player:
            owned_territories.append(i)

    border_territories = []
    for i in range(len(owned_territories)):
        for n in state.board.territories[owned_territories[i]].neighbors:
            if state.owners[n] != state.current_player:
                border_territories.append(owned_territories[i])

    for i in range(len(border_territories)):
        border_armies += state.armies[border_territories[i]]

    final_value += border_armies * 0.1

    return final_value


def update_exp_attack_reward(curr_values, probs):
    result = 0.0
    for i in range(len(curr_values)):
        result += curr_values[i] * probs[i]
    return result


def get_troop_movement(actions, state):
    possible_actions = get_bordering_territory_actions(actions, state)
    min_score = troop_movement_eval(possible_actions, state)
    action = actions[len(actions) - 1]
    for a in possible_actions:
        new_state = state.copy_state()
        if a.type == 'PrePlace':
            risktools.simulatePrePlaceAction(new_state, a)
        elif a.type == 'Fortify':
            risktools.simulateFortifyAction(new_state, a)
        elif a.type == 'Place':
            risktools.simulatePlaceAction(new_state, a)
        score = troop_movement_eval(possible_actions, new_state)
        if score < min_score:
            min_score = score
            action = a
    return action


def troop_movement_eval(actions, state):
    tot_value = 0.0
    for a in actions:
        terr_val = 0.0
        num_enemies = 0
        terr = state.board.territory_to_id[a.to_territory]
        for n in state.board.territories[terr].neighbors:
            if state.owners[n] == state.owners[terr]:
                terr_val += 0.96
            else:
                num_enemies += 1
                num_enemies += state.armies[n]
        for cont in state.board.continents:
            if terr in state.board.continents[cont].territories:
                terr_val += has_cont_value(state.current_player, state.board.continents[cont], state)
        terr_val = terr_val / state.armies[terr]
        terr_val += num_enemies
        tot_value += terr_val
    return tot_value

def place_remaining_armies(new_state, terr_action):
    while new_state.players[new_state.current_player].free_armies > 0:
        simulatePlaceAction(new_state, RiskAction('Place', terr_action.to_territory, None, None))


def get_pre_assign(actions, state):
    root_node = PreAssignNode(state)

    start_time = time.time()

    action = actions[0]

    while time.time() - start_time < 2:
        mcts(root_node)

    max_searches = 0
    for a in root_node.children:
        if root_node.children[a] is not None:
            if root_node.children[a].searches > max_searches:
                action = a
                max_searches = root_node.children[a].searches
    #print(f"Total Searches: {root_node.searches}")
    #for a in root_node.children:
        #print(f"{root_node.children[a].searches} with avg reward: {root_node.children[a].tot_reward[root_node.state.current_player]/root_node.children[a].searches}")
    return action


def mcts(node):
    if node.is_leaf:
        if node.next_action is not None:
            new_state = node.state.copy_state()
            simulatePreAssignAction(new_state, node.actions[node.next_action])
            nextPlayer(new_state)
            child = PreAssignNode(new_state)
            node.children[node.actions[node.next_action]] = child
            reward = simulate_final_placement(child.state.copy_state())
            child.tot_reward = reward
            child.searches = 1
            node.next_action += 1
            if node.next_action >= len(node.children):
                node.is_leaf = False
            update_reward(node.tot_reward, reward)
            node.searches += 1
            return reward
        else:
            reward = eval_final_placement(node.state)
            update_reward(node.tot_reward, reward)
            node.searches += 1
            return reward
    else:
        action = get_max_ucb_action(node, node.children)
        reward = mcts(node.children[action])
        update_reward(node.tot_reward, reward)
        node.searches += 1
        return reward


def eval_final_placement(state):
    reward = {}
    for player in range(len(state.players)):
        reward.update({player: tot_continent_value(player, state)})
        if state.current_player == player:
            reward[player] += 13.38
        next_player_state = state.copy_state()
        risktools.nextPlayer(next_player_state)
        if next_player_state.current_player == player:
            reward[player] += 5.35
        for terr in state.board.territories:
            for neighbor in terr.neighbors:
                unique_enemies = set()
                if state.owners[terr.id] == state.owners[neighbor]:
                    reward[player] += 0.96
                elif state.owners[neighbor] not in unique_enemies:
                    reward[player] -= 0.07
                    unique_enemies.add(state.owners[neighbor])
    final_reward = {}
    for player in reward:
        enemy_total = 0.0
        for other_player in reward:
            if player != other_player:
                enemy_total += reward[other_player]
        if enemy_total == 0.0:
            enemy_total = 1.0
        final_reward.update({player: reward[player]/enemy_total})
    return final_reward


def get_max_ucb_action(parent, children):
    max_ucb = -numpy.inf
    action = None
    for child in children:
        child_ucb = calc_ucb(children[child], parent)
        if child_ucb > max_ucb:
            max_ucb = child_ucb
            action = child
    return action


def calc_ucb(node, parent):
    return (node.tot_reward[parent.state.current_player] / node.searches) + (0.5 * numpy.sqrt(
        (numpy.log(parent.searches) / node.searches)))


def simulate_final_placement(state):
    while len(getPreAssignActions(state)) > 0:
        risktools.simulatePreAssignAction(state, random.choice(getPreAssignActions(state)))
        risktools.nextPlayer(state)
    return eval_final_placement(state)


def tot_continent_value(player, state):
    value = 0.0
    for cont in state.board.continents:
        value += cont_value(player, state.board.continents[cont], state)
    return value


def cont_value(player, cont, state):
    num_in_cont = 0
    for terr in cont.territories:
        if state.owners[state.board.territories[terr].id] == player:
            num_in_cont += 1
    value = continent_values[cont.name][num_in_cont]
    return value


def has_cont_value(player, cont, state):
    num_in_cont = 0
    for terr in cont.territories:
        if state.owners[state.board.territories[terr].id] == player:
            num_in_cont += 1
    value = (num_in_cont/len(cont.territories)) * continent_values[cont.name][len(cont.territories) - 1]
    return value


def update_reward(reward, new_values):
    for player in reward:
        reward[player] += new_values[player]


def get_bordering_territory_actions(actions, state):
    possible_actions = []
    for a in actions:
        if a.to_territory is not None:
            for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                if state.owners[n] != state.current_player:
                    possible_actions.append(a)
    return possible_actions


def dice_advantage(attack, state):
    if attack.to_territory is None:
        return True
    else:
        enemy_dice = 1
        if state.armies[state.board.territory_to_id[attack.to_territory]] > 1:
            enemy_dice = 2
        my_dice = state.armies[state.board.territory_to_id[attack.from_territory]] - 1
        return my_dice >= enemy_dice


asia_values = {0: 27.10,
               1: 23.90,
               2: 23.61,
               3: 23.10,
               4: 23.61,
               5: 23.68,
               6: 19.32,
               7: 15.63,
               8: 17.43,
               9: 13.84,
               10: 10.25,
               11: 6.66,
               12: 3.07}

africa_values = {0: 14.4,
                 1: 12.87,
                 2: 10.72,
                 3: 7.16,
                 4: 1.23,
                 5: 0.0,
                 6: 29.8}

north_america_values = {0: 2.97,
                        1: 0.98,
                        2: 0.0,
                        3: 2.17,
                        4: 7.15,
                        5: 19.35,
                        6: 24.82,
                        7: 24.1,
                        8: 36.15,
                        9: 48.2}

europe_values = {0: 42.44,
                 1: 45.11,
                 2: 43.11,
                 3: 43.77,
                 4: 41.35,
                 5: 50.77,
                 6: 43.85,
                 7: 36.93}

australia_values = {0: 3.11,
                    1: 0.0,
                    2: 8.45,
                    3: 9.99,
                    4: 10.71}

south_america_values = {0: 0.69,
                        1: 0.98,
                        2: 3.90,
                        3: 2.17,
                        4: 17.72}

continent_values = {"Asia": asia_values,
                    "North America": north_america_values,
                    "Africa": africa_values,
                    "Europe": europe_values,
                    "Australia": australia_values,
                    "South America": south_america_values
                    }

cont_army_values = {"Asia": 7,
                    "North America": 5,
                    "Africa": 3,
                    "Europe": 5,
                    "Australia": 2,
                    "South America": 2
                    }


class PreAssignNode:
    def __init__(self, state):
        self.searches = 0
        self.tot_reward = {}
        self.state = state
        self.is_leaf = True
        self.next_action = None
        self.actions = getAllowedActions(state)
        if len(self.actions) > 0:
            self.children = {self.actions[0]: None}
            self.next_action = 0
            for i in range(1, len(self.actions)):
                self.children.update({self.actions[i]: None})


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
