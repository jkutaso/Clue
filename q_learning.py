import numpy as np
import pandas as pd
from GameCode.constants import ROOMS, SUSPECTS, WEAPONS, WIDTH, HEIGHT
from GameCode.ClueBoard import ClueBoard
from GameCode.PlayerInterface import PlayerInterface, run_full_game
from Players.learner import Learner
from Players.naive_clue_player import NaiveCluePlayer
import pickle

guess_rewards = dict()
guess_rewards[(True, True)] = 1
guess_rewards[(True, False)] = -1
guess_rewards[(False, True)] = 0
guess_rewards[(False, False)] = 0

length_of_known_results_normalization = 20
solutions_in_play_normalization = 30
guess_params_dict = dict()
for number_of_solved in range(3):
    guess_params_dict[number_of_solved] = dict()
    for length_of_known_results in range(20):
        guess_params_dict[number_of_solved][length_of_known_results] = dict()
        for solutions_in_play in range(20):
            guess_params_dict[number_of_solved][length_of_known_results][solutions_in_play] = dict()
            for action in [True, False]:
                guess_params_dict[number_of_solved][length_of_known_results][solutions_in_play][action] = 0
epsilon = 0.1
learning_rate = 0.9

clue_board = ClueBoard()
player_types = [Learner] * 3 + [NaiveCluePlayer]
naive_wins = 0
iterations = 1000
for i in range(iterations):
    if i % 100 == 1:
        print(naive_wins)
        naive_wins = 0
    epsilon *= 0.9
    learning_rate = 1 - i/iterations
    player_interface = PlayerInterface(player_types=player_types, clue_board=clue_board, debugging=False,
                                       guess_params_dict=guess_params_dict, epsilon=epsilon,
                                       length_of_known_results_normalization=length_of_known_results_normalization,
                                       solutions_in_play_normalization=solutions_in_play_normalization)

    winner = run_full_game(player_interface, False)
    if winner == 3:
        naive_wins+= 1
    players = player_interface.get_players()
    for player_id in players.keys():
        if type(players[player_id]) is Learner:
            results = players[player_id].report_results()
            for result in results:
                number_of_solved, length_of_known_results, solutions_in_play, action_plan = result
                won_game = winner == player_id
                guess_params_dict[number_of_solved][length_of_known_results][solutions_in_play][action_plan] = guess_params_dict[number_of_solved][length_of_known_results][solutions_in_play][action_plan] * (1 - learning_rate) + learning_rate * guess_rewards[(action_plan, won_game)]



with open('guess_param_dicts.pkl', 'wb') as f:
    pickle.dump(guess_params_dict, f)