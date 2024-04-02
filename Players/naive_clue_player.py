import numpy as np
import pandas as pd
from GameCode.constants import ROOMS, SUSPECTS, WEAPONS, WIDTH, HEIGHT


class NaiveCluePlayer:
    def __init__(self, cards, player_card_count, my_player_number, played_suspects):
        self.my_player_number = my_player_number
        self.player_card_count = player_card_count
        self.my_suspect = played_suspects[my_player_number]
        self.played_suspects = played_suspects
        self.cards = cards
        self.information_df = pd.DataFrame(0, index=ROOMS + SUSPECTS + WEAPONS, columns=range(len(played_suspects)))
        self.known_results = []

        for card in cards:
            self.information_df.loc[card] = -1
            self.information_df.loc[card, self.my_player_number] = 1

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
                if (location in ROOMS and square_to_room_distances.get((x, y, location), -1)==roll_result) or square_to_square_distances.get((x, y, *location), -1) == roll_result:
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

    def _make_move_decision(self, locations: dict, roll_result: int, room_to_room_distances: dict, square_to_square_distances: dict, square_to_room_distances: dict):
        location = locations[self.my_suspect]
        if location in ROOMS:
            for room in ROOMS:
                if room_to_room_distances[(location, room)] <= roll_result and not self._check_if_card_is_known_to_me(room):
                    return room
            return self._find_best_square_to_go_to(location, square_to_square_distances, square_to_room_distances, roll_result)
        else:
            for room in ROOMS:
                if square_to_room_distances.get((*location, room), -1) <= roll_result:
                    return room
            return self._find_best_square_to_go_to(location, square_to_square_distances, square_to_room_distances, roll_result)

    def _make_ask_decision(self, room: str):
        weapon_scores = []
        for weapon in WEAPONS:
            if self._check_if_card_is_known_to_me(weapon):
                weapon_scores.append(1)
            else:
                weapon_scores.append(sum(self.information_df.loc[weapon]))
        weapon_to_guess = WEAPONS[weapon_scores.index(min(weapon_scores))]

        suspect_scores = []
        for suspect in SUSPECTS:
            if self._check_if_card_is_known_to_me(suspect):
                suspect_scores.append(1)
            else:
                suspect_scores.append(sum(self.information_df.loc[suspect]))

        suspect_to_guess = SUSPECTS[suspect_scores.index(min(suspect_scores))]
        return room, weapon_to_guess, suspect_to_guess

    def _is_type_of_card_solved(self, list_to_check: list):
        for card in list_to_check:
            if sum(self.information_df.loc[card]) == -len(self.played_suspects):
                return True, card
        return False, None

    def _assign_card_to_player(self, card: str, player_id: int):
        self.information_df.loc[card] = -1
        self.information_df.loc[card, player_id] = 1

    def _check_for_pigeonhole(self):
        for player_id in range(len(self.player_card_count)):
            if player_id == self.my_player_number:
                continue
            if self.information_df[player_id].eq(1).sum() == self.player_card_count[player_id]:
                self.information_df[player_id] = self.information_df[player_id].apply(lambda x: -1 if x != 1 else x)

    def _update_known_results(self, player_id, room, weapon, suspect, response):
        if not response:
            for card in (room, weapon, suspect):
                self.information_df.loc[card, player_id] = -1
        elif response in ROOMS + WEAPONS + SUSPECTS:
            self._assign_card_to_player(response, player_id)

        keep_running = True
        count = 0
        while keep_running and count < 20:
            count += 1
            keep_running = False
            for result in self.known_results:
                this_id = result[0]
                this_room = result[1]
                this_weapon = result[2]
                this_suspect = result[3]

                current_status_list = [self.information_df.loc[card, player_id] for card in (this_room, this_weapon, this_suspect)]
                if 1 in current_status_list:
                    continue
                assert sum(current_status_list) > -3, f"It must be possible to have one of {this_room, this_weapon, this_suspect}"

                if sum(current_status_list) == -2:
                    card_they_have = result[1:][current_status_list.index(0)]
                    self._assign_card_to_player(card_they_have, this_id)

        self._check_for_pigeonhole()







