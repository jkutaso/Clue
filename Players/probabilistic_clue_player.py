import numpy as np
import pandas as pd
from GameCode.constants import ROOMS, SUSPECTS, WEAPONS, WIDTH, HEIGHT


class ProbabilisticCluePlayer:
    def __init__(self, cards, player_card_count, my_player_number, played_suspects):
        self.my_player_number = my_player_number
        self.player_card_count = player_card_count
        self.my_suspect = played_suspects[my_player_number]
        self.played_suspects = played_suspects
        self.cards = cards
        self.information_df = pd.DataFrame(0, index=ROOMS + SUSPECTS + WEAPONS, columns=range(len(played_suspects)))
        for player_id in range(len(played_suspects)):
            self.information_df[player_id] = player_card_count[player_id]/len(self.information_df)
        self.known_results = []
        for card in cards:
            self._assign_card_to_player(card, my_player_number)
        self._check_valid_df()

    def ask_player(self, room: str, weapon: str, suspect: str) -> str:
        if room in self.cards:
            return room
        if weapon in self.cards:
            return weapon
        if suspect in self.cards:
            return suspect
        raise f"I shouldn't have been asked about {room, weapon, suspect}"

    def ready_to_guess(self):
        is_room_solved, room_guess = self._is_type_of_card_solved(ROOMS)
        is_weapon_solved, weapon_guess = self._is_type_of_card_solved(WEAPONS)
        is_suspect_solved, suspect_guess = self._is_type_of_card_solved(SUSPECTS)
        if is_room_solved and is_suspect_solved and is_weapon_solved:
            return True, (room_guess, weapon_guess, suspect_guess)
        return False, None

    def take_turn(self, locations: dict, board, roll: int):
        move_decision = self._make_move_decision(locations, roll, board.get_room_to_room_distances(), board.get_square_to_square_distances(), board.get_square_to_room_distances())
        if move_decision in ROOMS:
            ask_decision = self._make_ask_decision(move_decision)
        else:
            ask_decision = None
        return move_decision, ask_decision

    def parse_ask_result(self, question, ask_result):
        for player_id in ask_result.keys():
            self._update_known_results(player_id, *question, ask_result[player_id])

    def update_given_shown(self, player_id, shown_card):
        self._assign_card_to_player(shown_card, player_id)

    def _check_if_card_is_known_to_me(self, card: str) -> bool:
        return max(self.information_df.loc[card]) == 1

    def _find_best_square_to_go_to(self, location, square_to_square_distances, square_to_room_distances, roll_result):
        possible_moves = []
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if (location in ROOMS and square_to_room_distances.get((x, y, location),
                                                                       -1) == roll_result) or square_to_square_distances.get(
                        (x, y, *location), -1) == roll_result:
                    possible_moves.append((x, y))
        distance_from_acceptable_room = []
        for (x, y) in possible_moves:
            distance = np.inf
            for room in ROOMS:
                if self._check_if_card_is_known_to_me(room):
                    continue
                distance = min(distance, square_to_room_distances.get((x, y, room), np.inf))
            distance_from_acceptable_room.append(distance)
        return possible_moves[distance_from_acceptable_room.index(min(distance_from_acceptable_room))]

    def _make_move_decision(self, locations: dict, roll_result: int, room_to_room_distances: dict,
                            square_to_square_distances: dict, square_to_room_distances: dict):
        location = locations[self.my_suspect]
        if location in ROOMS:
            for room in ROOMS:
                if room_to_room_distances[(location, room)] <= roll_result and not self._check_if_card_is_known_to_me(
                        room):
                    return room
            return self._find_best_square_to_go_to(location, square_to_square_distances, square_to_room_distances,
                                                   roll_result)
        else:
            for room in ROOMS:
                if square_to_room_distances.get((*location, room), -1) <= roll_result:
                    return room
            return self._find_best_square_to_go_to(location, square_to_square_distances, square_to_room_distances,
                                                   roll_result)

    def _make_ask_decision(self, room: str):
        weapon_scores = []
        for weapon in WEAPONS:
            if self._check_if_card_is_known_to_me(weapon):
                weapon_scores.append(1)
            else:
                weapon_scores.append(min(self.information_df.loc[weapon]))
        weapon_to_guess = WEAPONS[weapon_scores.index(min(weapon_scores))]

        suspect_scores = []
        for suspect in SUSPECTS:
            if self._check_if_card_is_known_to_me(suspect):
                suspect_scores.append(1)
            else:
                suspect_scores.append(min(self.information_df.loc[suspect]))

        suspect_to_guess = SUSPECTS[suspect_scores.index(min(suspect_scores))]
        return room, weapon_to_guess, suspect_to_guess

    def _is_type_of_card_solved(self, list_to_check: list):
        for card in list_to_check:
            if sum(self.information_df.loc[card]) == 0:
                return True, card
        return False, None

    def _normalize_column(self, player_id):
        confirmed_cards = [card for card in ROOMS + WEAPONS + SUSPECTS if
                           self.information_df.loc[card, player_id] == 1]
        sum_without_confirmed_cards = sum(self.information_df[player_id]) - len(confirmed_cards)
        if sum_without_confirmed_cards == 0:
            return
        self.information_df[player_id] *= (self.player_card_count[player_id] - len(confirmed_cards))/sum_without_confirmed_cards
        for c in confirmed_cards:
            self.information_df.loc[c, player_id] = 1

    def _assign_card_to_player(self, card: str, player_id: int):
        self.information_df.loc[card] = 0
        self.information_df.loc[card, player_id] = 1
        for id in range(len(self.player_card_count)):
            self._normalize_column(id)

    def _update_known_results(self, player_id, room, weapon, suspect, response):
        if not response:
            for card in (room, weapon, suspect):
                old_probability = self.information_df.loc[card, player_id]
                self.information_df.loc[card] /= (1 - old_probability)
                self.information_df.loc[card, player_id] = 0
                self.information_df[player_id] = self.information_df[player_id] * self.player_card_count[player_id]/sum(self.information_df[player_id])
                for id in range(len(self.player_card_count)):
                    self._normalize_column(id)
        elif response in ROOMS + WEAPONS + SUSPECTS:
            self._assign_card_to_player(response, player_id)
        self._check_valid_df()

    def _check_valid_df(self):
        for id in range(len(self.player_card_count)):
            assert abs(sum(self.information_df[id]) - self.player_card_count[id]) < 0.001, (sum(self.information_df[id]), self.player_card_count[id])

