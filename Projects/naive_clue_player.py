import numpy as np


class NaiveCluePlayer:
    def __init__(self, rooms, suspects, weapons, cards, player_card_count, my_player_number, played_suspects):
        self.rooms = rooms
        self.suspects = suspects
        self.weapons = weapons
        self.my_player_number = my_player_number
        self.player_card_count = player_card_count
        self.my_suspect = played_suspects[my_player_number]
        self.played_suspects = played_suspects
        self.cards = cards
        self.rooms_to_players = dict()
        self.suspects_to_players = dict()
        self.weapons_to_players = dict()
        self.players_to_weapons = dict()
        self.players_to_suspects = dict()
        self.players_to_rooms = dict()
        self.ruled_out_rooms = dict()
        self.ruled_out_weapons = dict()
        self.ruled_out_suspects = dict()
        self.known_results = []
        for card in cards:
            if card in rooms:
                self.rooms_to_players[card] = my_player_number
                self.players_to_rooms[my_player_number] = [card]
                for i in range(len(self.player_card_count)):
                    if i == my_player_number:
                        continue
                    self.ruled_out_rooms[i] = self.ruled_out_rooms.get(i, []) + [card]
            elif card in suspects:
                self.suspects_to_players[card] = my_player_number
                self.players_to_suspects[my_player_number] = [card]
                for i in range(len(self.player_card_count)):
                    if i == my_player_number:
                        continue
                    self.ruled_out_suspects[i] = self.ruled_out_suspects.get(i, []) + [card]
            elif card in weapons:
                self.weapons_to_players[card] = my_player_number
                self.players_to_weapons[my_player_number] = [card]
                for i in range(len(self.player_card_count)):
                    if i == my_player_number:
                        continue
                    self.ruled_out_weapons[i] = self.ruled_out_weapons.get(i, []) + [card]
            else:
                assert False
        for room in rooms:
            if room not in cards:
                self.ruled_out_rooms[my_player_number] = self.ruled_out_rooms.get(my_player_number, []) + [room]
        for weapon in weapons:
            if weapon not in cards:
                self.ruled_out_weapons[my_player_number] = self.ruled_out_weapons.get(my_player_number, []) + [weapon]
        for suspect in suspects:
            if suspect not in cards:
                self.ruled_out_suspects[my_player_number] = self.ruled_out_suspects.get(my_player_number, []) + [suspect]

    def ask_player(self, room, weapon, suspect):
        if room in self.cards:
            return True
        if weapon in self.cards:
            return True
        if suspect in self.cards:
            return True
        return False

    def ask_player_specific(self, room, weapon, suspect):
        if room in self.cards:
            return room
        if weapon in self.cards:
            return weapon
        if suspect in self.cards:
            return suspect
        return False

    def make_move_decision(self, locations, roll_result, board, room_to_room_distances, square_to_square_distances, square_to_room_distances):
        location = locations[self.my_suspect]
        if location in self.rooms:
            for room in self.rooms:
                if room_to_room_distances[(location, room)] <= roll_result and room not in self.rooms_to_players.keys():
                    return room
            for x in range(len(board[0])):
                for y in range(len(board)):
                    if square_to_room_distances.get((x, y, location), -1) == roll_result:
                        return x, y
        else:
            for room in self.rooms:
                if square_to_room_distances.get((*location, room), -1) <= roll_result:
                    return room
            possible_moves = []
            for x in range(len(board[0])):
                for y in range(len(board)):
                    if square_to_square_distances.get((*location, x, y), -1) == roll_result:
                        possible_moves.append((x, y))
            distance_from_acceptable_room = []
            for (x, y) in possible_moves:
                distance = np.inf
                for room in self.rooms:
                    if room in self.rooms_to_players.keys():
                        continue
                    distance = min(distance, square_to_room_distances[(x, y, room)])
                distance_from_acceptable_room.append(distance)
            return possible_moves[distance_from_acceptable_room.index(min(distance_from_acceptable_room))]

    def make_ask_decision(self, room):
        weapon_scores = []
        for weapon in self.weapons:
            if weapon in self.weapons_to_players.keys():
                weapon_scores.append(-1)
            else:
                score = 0
                for i in range(len(self.played_suspects)):
                    if i == self.my_player_number:
                        continue
                    if weapon in self.ruled_out_weapons.get(i, []):
                        score += 1
                weapon_scores.append(score)
        weapon_to_guess = self.weapons[weapon_scores.index(max(weapon_scores))]

        suspect_scores = []
        for suspect in self.suspects:
            if suspect in self.suspects_to_players.keys():
                suspect_scores.append(-1)
            else:
                score = 0
                for i in range(len(self.played_suspects)):
                    if i == self.my_player_number:
                        continue
                    if suspect in self.ruled_out_suspects.get(i, []):
                        score += 1
                suspect_scores.append(score)
        suspect_to_guess = self.suspects[suspect_scores.index(max(suspect_scores))]
        return room, weapon_to_guess, suspect_to_guess

    def ready_to_guess(self):
        room_to_guess = None
        for room in self.rooms:
            count = 0
            for player_id in range(len(self.player_card_count)):
                if room not in self.ruled_out_rooms.get(player_id, []):
                    break
                count += 1
            if count == len(self.player_card_count):
                room_to_guess = room
                break
        if room_to_guess is None:
            return False

        weapon_to_guess = None
        for weapon in self.weapons:
            count = 0
            for player_id in range(len(self.player_card_count)):
                if weapon not in self.ruled_out_weapons.get(player_id, []):
                    break
                count += 1
            if count == len(self.player_card_count):
                weapon_to_guess = weapon
                break
        if weapon_to_guess is None:
            return False

        suspect_to_guess = None
        for suspect in self.suspects:
            count = 0
            for player_id in range(len(self.player_card_count)):
                if suspect not in self.ruled_out_suspects.get(player_id, []):
                    break
                count += 1
            if count == len(self.player_card_count):
                suspect_to_guess = suspect
                break
        if suspect_to_guess is None:
            return False
        return room_to_guess, weapon_to_guess, suspect_to_guess

    def take_turn(self, locations, board, room_to_room_distances, square_to_square_distances, square_to_room_distances, roll):
        move_decision = self.make_move_decision(locations, roll, board, room_to_room_distances, square_to_square_distances, square_to_room_distances)
        if move_decision in self.rooms:
            ask_decision = self.make_ask_decision(move_decision)
            return ask_decision
        return move_decision

    def assign_room_to_player(self, room, player_id):
        assert room in self.rooms
        self.rooms_to_players[room] = player_id
        self.players_to_rooms[player_id] = self.players_to_rooms.get(player_id, []) + [room]
        for i in range(len(self.player_card_count)):
            if i == player_id or room in self.ruled_out_rooms.get(i, []):
                continue
            if room not in self.ruled_out_rooms.get(i, []):
                self.ruled_out_rooms[i] = self.ruled_out_rooms.get(i, []) + [room]

    def assign_weapon_to_player(self, weapon, player_id):
        assert weapon in self.weapons
        self.weapons_to_players[weapon] = player_id
        self.players_to_weapons[player_id] = self.players_to_weapons.get(player_id, []) + [weapon]
        for i in range(len(self.player_card_count)):
            if i == player_id or weapon in self.ruled_out_weapons.get(i, []):
                continue
            if weapon not in self.ruled_out_weapons.get(i, []):
                self.ruled_out_weapons[i] = self.ruled_out_weapons.get(i, []) + [weapon]

    def assign_suspect_to_player(self, suspect, player_id):
        assert suspect in self.suspects
        self.suspects_to_players[suspect] = player_id
        self.players_to_suspects[player_id] = self.players_to_suspects.get(player_id, []) + [suspect]
        for i in range(len(self.player_card_count)):
            if i == player_id or suspect in self.ruled_out_suspects.get(i, []):
                continue
            if suspect not in self.ruled_out_suspects.get(i, []):
                self.ruled_out_suspects[i] = self.ruled_out_suspects.get(i, []) + [suspect]

    def check_for_pigeonhole(self):
        for player_id in range(len(self.player_card_count)):
            if player_id == self.my_player_number:
                continue
            total_known_cards = len(self.players_to_rooms.get(player_id, [])) + len(self.players_to_suspects.get(player_id, [])) + len(self.players_to_weapons.get(player_id, []))
            if total_known_cards == self.player_card_count[player_id]:
                for room in self.rooms:
                    if room not in self.players_to_rooms.get(player_id, []):
                        self.ruled_out_rooms[player_id] = self.ruled_out_rooms.get(player_id, []) + [room]
                for weapon in self.weapons:
                    if weapon not in self.players_to_weapons.get(player_id, []):
                        self.ruled_out_weapons[player_id] = self.ruled_out_weapons.get(player_id, []) + [weapon]
                for suspect in self.suspects:
                    if suspect not in self.players_to_suspects.get(player_id, []):
                        self.ruled_out_suspects[player_id] = self.ruled_out_suspects.get(player_id, []) + [suspect]
            total_ruled_out = len(self.ruled_out_rooms.get(player_id, [])) + len(
                self.ruled_out_suspects.get(player_id, [])) + len(self.ruled_out_weapons.get(player_id, []))
            if total_ruled_out + self.player_card_count[player_id] == len(self.rooms) + len(self.suspects) + len(self.weapons):
                for room in self.rooms:
                    if room not in self.ruled_out_rooms.get(player_id, []):
                        self.assign_room_to_player(room, player_id)
                for weapon in self.weapons:
                    if weapon not in self.ruled_out_weapons.get(player_id, []):
                        self.assign_weapon_to_player(weapon, player_id)
                for suspect in self.suspects:
                    if suspect not in self.ruled_out_suspects.get(player_id, []):
                        self.assign_suspect_to_player(suspect, player_id)

    def update_known_results(self, player_id, room, weapon, suspect, response):
        self.known_results.append([player_id, room, weapon, suspect, response])
        if not response:
            if room not in self.ruled_out_rooms.get(player_id, []):
                self.ruled_out_rooms[player_id] = self.ruled_out_rooms.get(player_id, []) + [room]
            if weapon not in self.ruled_out_weapons.get(player_id, []):
                self.ruled_out_weapons[player_id] = self.ruled_out_weapons.get(player_id, []) + [weapon]
            if suspect not in self.ruled_out_suspects.get(player_id, []):
                self.ruled_out_suspects[player_id] = self.ruled_out_suspects.get(player_id, []) + [suspect]

        keep_running = True
        count = 0
        while keep_running and count < 20:
            count +=1
            keep_running = False
            for result in self.known_results:
                if not result[4]:
                    continue
                this_id = result[0]
                this_room = result[1]
                this_weapon = result[2]
                this_suspect = result[3]

                if this_room in self.players_to_rooms.get(this_id, []):
                    continue
                elif this_weapon in self.players_to_weapons.get(this_id, []):
                    continue
                elif this_suspect in self.players_to_suspects.get(this_id, []):
                    continue
                could_have_room = True
                if this_room in self.ruled_out_rooms.get(this_id, []):
                    could_have_room = False
                could_have_weapon = True
                if this_weapon in self.ruled_out_weapons.get(this_id, []):
                    could_have_weapon = False
                could_have_suspect = True
                if this_suspect in self.ruled_out_suspects.get(this_id, []):
                    could_have_suspect = False
                assert could_have_weapon or could_have_room or could_have_suspect, (this_id, this_room, this_weapon, this_suspect)
                if could_have_suspect + could_have_room + could_have_weapon == 1:
                    keep_running = True
                    if could_have_weapon:
                        assert this_weapon not in self.players_to_weapons.get(this_id, [])
                        self.assign_weapon_to_player(this_weapon, this_id)
                    if could_have_room:
                        assert this_room not in self.players_to_rooms.get(this_id, [])
                        self.assign_room_to_player(this_room, this_id)
                    if could_have_suspect:
                        assert this_suspect not in self.players_to_suspects.get(this_id, [])
                        self.assign_suspect_to_player(this_suspect, this_id)
        self.check_for_pigeonhole()

    def update_given_shown(self, player_id, shown_card):
        if shown_card in self.players_to_suspects.get(player_id, []):
            return
        if shown_card in self.players_to_rooms.get(player_id, []):
            return
        if shown_card in self.players_to_weapons.get(player_id, []):
            return
        if shown_card in self.rooms:
            self.assign_room_to_player(shown_card, player_id)
        if shown_card in self.weapons:
            self.assign_weapon_to_player(shown_card, player_id)
        if shown_card in self.suspects:
            self.assign_suspect_to_player(shown_card, player_id)





