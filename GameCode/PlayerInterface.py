import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
import numpy as np
from Players.naive_clue_player import NaiveCluePlayer
from Players.probabilistic_clue_player import ProbabilisticCluePlayer
from ClueBoard import ClueBoard
from GameState import GameState
from constants import ROOMS, WEAPONS, SUSPECTS


def roll(debugging):
    r = 2 + sum(np.random.choice(6, 2))
    if debugging:
        print("Player rolls {}".format(r))
    return r


class PlayerInterface:
    def __init__(self, player_types, clue_board, debugging):
        self.player_types = player_types
        self.debugging = debugging
        self.clue_board = clue_board
        self.game_state = GameState(self.clue_board, len(player_types))
        self.players = dict()
        self._initialize_players()

    def get_players(self):
        return self.players

    def increment_turn(self):
        next_player_id = (self.game_state.get_current_turn_id() + 1) % len(self.game_state.get_played_suspects())
        while self.players[next_player_id] == -1:
            next_player_id = (next_player_id + 1) % len(self.game_state.get_played_suspects())
        self.game_state.update_turn(next_player_id)

    def _initialize_players(self):
        for i in range(len(self.player_types)):
            if self.debugging:
                print("Cards assigned to", i, self.game_state.get_cards(i))
            self.players[i] = self.player_types[i](self.game_state.get_cards(i), self.game_state.get_player_card_count(), i, self.game_state.get_played_suspects())

    def handle_guess(self, guess, debugging):
        current_player_id = self.game_state.get_current_turn_id()
        players = self.players
        if guess == (self.game_state.get_true_room(), self.game_state.get_true_weapon(), self.game_state.get_true_suspect()):
            if True:
                print("Player {} wins by guessing {}".format(current_player_id, guess))
            return True
        else:
            if debugging:
                print("Player {} eliminated".format(current_player_id))
                print("Guessed {}".format(guess))
                print("Truth is {}".format((self.game_state.get_true_room(), self.game_state.get_true_weapon(), self.game_state.get_true_suspect())))
                assert False
            players[current_player_id] = -1
            return False

    def handle_move_decision(self, move_decision, this_roll):
        current_suspect = self.game_state.get_current_turn_suspect()
        current_location = self.game_state.get_locations()[current_suspect]
        if move_decision in ROOMS:
            if current_location in ROOMS:
                assert self.clue_board.get_room_to_room_distances()[
                           current_location, move_decision] <= this_roll, f"{self.game_state.get_current_turn_suspect()} tried to move from {current_location} to {move_decision} with roll of {this_roll}"
            else:
                assert self.clue_board.get_square_to_room_distances()[*current_location, move_decision] <= this_roll, f"{self.game_state.get_current_turn_suspect()} tried to move from {current_location} to {move_decision} with roll of {this_roll}"
            self.game_state.update_location(current_suspect, move_decision)
        else:
            self._handle_move_to_square(move_decision, this_roll)

    def _handle_move_to_square(self, turn_decision, this_roll):
        current_suspect = self.game_state.get_current_turn_suspect()
        if self.debugging:
            print("Player moved from {} to {}".format(self.game_state.get_locations()[current_suspect], turn_decision))
        current_location = self.game_state.get_locations()[current_suspect]
        if current_location in ROOMS:
            assert self.clue_board.get_square_to_room_distances()[(*turn_decision, current_location)] <= this_roll
        else:
            assert self.clue_board.square_to_square_distances[(*current_location, *turn_decision)] == this_roll
        self.game_state.update_location(current_suspect, turn_decision)

    def handle_ask(self, room, weapon, suspect):
        current_suspect = self.game_state.get_current_turn_suspect()
        self.game_state.update_location(suspect, room)
        assert self.game_state.get_locations()[current_suspect] == room, f"{current_suspect} is asking about a room they're not in"
        output = dict()
        player_id = (self.game_state.get_current_turn_id() + 1) % len(self.player_types)

        while player_id != self.game_state.get_current_turn_id():
            player_cards = self.game_state.get_cards(player_id)
            intersection = [card for card in player_cards if card in (room, weapon, suspect)]
            if len(intersection) == 0:
                output[player_id] = False
            elif len(intersection) == 1:
                output[player_id] = intersection[0]
                return (room, weapon, suspect), output
            else:
                output[player_id] = self.players[player_id].ask_player(room, weapon, suspect)
                return (room, weapon, suspect), output
            player_id = (player_id + 1) % len(self.player_types)
        return (room, weapon, suspect), output

    def get_current_turn(self):
        current_player_id = self.game_state.get_current_turn_id()
        current_player = self.players[current_player_id]
        while current_player == -1:
            if self.debugging:
                print("Player {} is already eliminated".format(current_player_id))
            self.increment_turn()
            current_player_id = self.game_state.get_current_turn_id()
            current_player = self.players[current_player_id]
        if self.debugging:
            print("Player {} is taking their turn".format(current_player_id))
        return current_player_id, current_player, self.game_state.get_played_suspects()[current_player_id]


def run_full_game(clue_board, player_types, debugging):

    player_interface = PlayerInterface(player_types=player_types, clue_board = clue_board, debugging=debugging)
    count = 0
    while count < 100:
        count += 1
        if debugging:
            print("Turn {}".format(count))
        current_player_id, current_player, current_suspect = player_interface.get_current_turn()
        assert current_player != -1
        ready_to_guess, guess = current_player.ready_to_guess()
        if ready_to_guess:
            guess_result = player_interface.handle_guess(guess, debugging)
            if guess_result:
                print(count)
                return current_player_id
            else:
                for player_id in range(len(player_interface.player_types)):
                    if player_id == current_player_id:
                        continue
                    for card in player_interface.game_state.get_cards(current_player_id):
                        player_interface.players[player_id].update_given_shown(current_player_id, card)

        this_roll = roll(debugging)
        move_decision, ask_decision = current_player.take_turn(player_interface.game_state.get_locations(), player_interface.game_state.get_board(), this_roll)
        if debugging:
            print(f"Move decision was {move_decision}, ask decision was {ask_decision}")
        player_interface.handle_move_decision(move_decision, this_roll)
        if ask_decision is not None:
            assert ask_decision[2] in SUSPECTS
            assert ask_decision[0] in ROOMS
            assert ask_decision[1] in WEAPONS

            (room, weapon, suspect), ask_result = player_interface.handle_ask(*ask_decision)
            current_player.parse_ask_result((room, weapon, suspect), current_player_id, ask_result)
            hidden_ask_result = {key: True if value and value != '' else False for key, value in ask_result.items()}
            for player in player_interface.get_players().values():
                player.parse_ask_result((room, weapon, suspect), current_player_id, hidden_ask_result)
        player_interface.increment_turn()


def main():
    clue_board = ClueBoard()
    player_types = [NaiveCluePlayer] * 3 + [ProbabilisticCluePlayer]
    wins = [0] * len(player_types)
    for i in range(20):
        wins[run_full_game(clue_board, player_types, False)] += 1
    print(wins)


main()