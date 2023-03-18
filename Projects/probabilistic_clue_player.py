import numpy as np
import itertools


class ProbabilisticCluePlayer:
    def __init__(self, rooms, suspects, weapons, cards, player_card_count, my_player_number, played_suspects):
        self.rooms = rooms
        self.suspects = suspects
        self.weapons = weapons
        self.my_player_number = my_player_number
        self.player_card_count = player_card_count
        self.my_suspect = played_suspects[my_player_number]
        self.played_suspects = played_suspects
        self.cards = cards
        #print(cards)
        self.known_results = []
        self.known_cards = dict()
        self.rooms_suspects_weapons = rooms + suspects + weapons
        #print(self.rooms_suspects_weapons)
        self.probability_matrix = np.zeros((len(self.rooms_suspects_weapons), len(played_suspects)))
        for card in cards:
            index = self.rooms_suspects_weapons.index(card)
            self.probability_matrix[index, my_player_number] = 1
        for player_id in range(len(played_suspects)):
            if player_id == my_player_number:
                continue
            for i in range(len(self.rooms_suspects_weapons)):
                card = self.rooms_suspects_weapons[i]
                if card in cards:
                    continue
                self.probability_matrix[i, player_id] = player_card_count[player_id]/(len(self.rooms_suspects_weapons) - len(cards))

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

    def get_item_score(self, item):
        return sum(self.probability_matrix[self.rooms_suspects_weapons.index(item)])

    def make_move_decision(self, locations, roll_result, board, room_to_room_distances, square_to_square_distances, square_to_room_distances):
        location = locations[self.my_suspect]
        if location in self.rooms:
            room_scores = []
            for room in self.rooms:
                if room_to_room_distances[(location, room)] <= roll_result:
                    room_scores.append(self.get_item_score(room))
                else:
                    room_scores.append(1)
            if min(room_scores) <= 1:
                return self.rooms[room_scores.index(min(room_scores))]

            for x in range(len(board[0])):
                for y in range(len(board)):
                    if square_to_room_distances.get((x, y, location), -1) == roll_result:
                        return x, y
        else:
            room_scores = []
            for room in self.rooms:
                if square_to_room_distances[(*location, room)] <= roll_result:
                    room_scores.append(sum(self.probability_matrix[self.rooms_suspects_weapons.index(room)]))
                else:
                    room_scores.append(1)
            if min(room_scores) <= 1:
                return self.rooms[room_scores.index(min(room_scores))]

            possible_moves = []
            for x in range(len(board[0])):
                for y in range(len(board)):
                    if square_to_square_distances.get((*location, x, y), -1) == roll_result:
                        possible_moves.append((x, y))
            distance_from_acceptable_room = []
            for (x, y) in possible_moves:
                distance = np.inf
                for room in self.rooms:
                    if self.get_item_score(room) <= 1:
                        distance = min(distance, square_to_room_distances[(x, y, room)])
                distance_from_acceptable_room.append(distance)
            return possible_moves[distance_from_acceptable_room.index(min(distance_from_acceptable_room))]

    def make_ask_decision(self, room):
        weapon_scores = []
        for weapon in self.weapons:
            weapon_scores.append(self.get_item_score(weapon))
        weapon_to_guess = self.weapons[weapon_scores.index(min(weapon_scores))]

        suspect_scores = []
        for suspect in self.suspects:
            suspect_scores.append(self.get_item_score(suspect))
        suspect_to_guess = self.suspects[suspect_scores.index(min(suspect_scores))]
        return room, weapon_to_guess, suspect_to_guess

    def ready_to_guess(self):
        room_to_guess = None
        for room in self.rooms:
            if self.get_item_score(room) < 0.0001:
                room_to_guess = room
        if room_to_guess is None:
            return False

        weapon_to_guess = None
        for weapon in self.weapons:
            if self.get_item_score(weapon) < 0.0001:
                weapon_to_guess = weapon
        if weapon_to_guess is None:
            return False

        suspect_to_guess = None
        for suspect in self.suspects:
            if self.get_item_score(suspect) < 0.0001:
                suspect_to_guess = suspect
        if suspect_to_guess is None:
            return False
        return room_to_guess, weapon_to_guess, suspect_to_guess

    def take_turn(self, locations, board, room_to_room_distances, square_to_square_distances, square_to_room_distances, roll):
        self.probability_matrix = self.construct_new_probability_matrix(1000)
        move_decision = self.make_move_decision(locations, roll, board, room_to_room_distances, square_to_square_distances, square_to_room_distances)
        if move_decision in self.rooms:
            ask_decision = self.make_ask_decision(move_decision)
            return ask_decision
        return move_decision

    def check_probability_matrix(self, probability_matrix):
        for id_number in range(len(self.played_suspects)):

            assert abs(sum([probability_matrix[x, id_number] for x in range(len(self.rooms_suspects_weapons))]) - self.player_card_count[id_number]) < 0.0001, (sum([probability_matrix[x, id_number] for x in range(len(self.rooms_suspects_weapons))]), self.player_card_count[id_number], id_number)
        # for card_index in range(len(self.rooms_suspects_weapons)):
        #     assert sum(probability_matrix[card_index]) <= 1.02, (sum(probability_matrix[card_index]))

    def initialize_new_probability_matrix(self, old_probability_matrix):
        new_probability_matrix = -1 * np.ones((len(self.rooms_suspects_weapons), len(self.played_suspects)))
        for card_index in range(len(self.rooms_suspects_weapons)):
            for i in range(len(self.played_suspects)):
                if old_probability_matrix[card_index, i] in [0, 1]:
                    new_probability_matrix[card_index, i] = old_probability_matrix[card_index, i]
        return new_probability_matrix

    def check_assignments_against_results(self, known_results, proposed_cards, known_cards_in_hand):
        for result in known_results:
            if not result[4]:
                continue
            if len(np.intersect1d(known_cards_in_hand.get(result[0], []), result[1:4])) > 0:
                continue
            if len(np.intersect1d(proposed_cards.get(result[0], []), result[1:4])) == 0:
                #print(result)
                return False
        return True

    def simulate_hands(self, known_results, known_cards_in_hand, num_cards_left_to_assign, cards_available, num_trials):
        scores = dict()
        cutoffs = [0]
        for k in num_cards_left_to_assign.keys():
            cutoffs.append(cutoffs[-1] + num_cards_left_to_assign[k])
        total_possibilities = 0
        for i in range(num_trials):
            np.random.shuffle(cards_available)
            proposed_cards = dict()
            for i in range(len(self.played_suspects)):
                proposed_cards[i] = cards_available[cutoffs[i]:cutoffs[i + 1]]
            possibility = True
            for result in known_results:
                if not result[4] and len(np.intersect1d(result[1:4], proposed_cards[result[0]])) > 0:
                    possibility = False
                    break
            if not possibility:
                continue
            total_possibilities += 1
            works = self.check_assignments_against_results(known_results, proposed_cards, known_cards_in_hand)
            # print('proposed', proposed_cards, works)
            # print('known', known_cards_in_hand)
            #
            # assert works
            if works:
                for i in proposed_cards.keys():
                    this_player_cards = proposed_cards[i]
                    for card in this_player_cards:
                        scores[(i, card)] = scores.get((i, card), 0) + 1
        return scores, total_possibilities

    def construct_new_probability_matrix(self, num_trials):
        new_probability_matrix = self.initialize_new_probability_matrix(self.probability_matrix)
        known_cards_in_hand = dict()
        cards_available = set()
        num_cards_left_to_assign = dict()
        for id_number in range(len(self.played_suspects)):
            for card_index in range(len(self.rooms_suspects_weapons)):
                if new_probability_matrix[card_index, id_number] == -1:
                    cards_available.add(self.rooms_suspects_weapons[card_index])
                elif new_probability_matrix[card_index, id_number] == 1:
                    known_cards_in_hand[id_number] = known_cards_in_hand.get(id_number, []) + [self.rooms_suspects_weapons[card_index]]
                elif new_probability_matrix[card_index, id_number] != 0:
                    assert False
            num_cards_left_to_assign[id_number] = self.player_card_count[id_number] - len(known_cards_in_hand.get(id_number, []))
        cards_available = list(cards_available)
        scores, total_possibilities = self.simulate_hands(self.known_results, known_cards_in_hand, num_cards_left_to_assign, cards_available, num_trials)
        #print(scores)
        for i in range(len(self.rooms_suspects_weapons)):
            card = self.rooms_suspects_weapons[i]
            for id_number in range(len(self.played_suspects)):
                if new_probability_matrix[i, id_number] == -1:
                    new_probability_matrix[i, id_number] = scores.get((id_number, card), 1)/total_possibilities
        return new_probability_matrix

    def update_known_results(self, player_id, room, weapon, suspect, response):
        self.known_results.append([player_id, room, weapon, suspect, response])
        if not response:
            for card in [room, weapon, suspect]:
                self.probability_matrix[self.rooms_suspects_weapons.index(card), player_id] = 0

    def update_given_shown(self, player_id, shown_card):
        card_index = self.rooms_suspects_weapons.index(shown_card)
        if self.probability_matrix[card_index, player_id] == 1:
            return
        for id_number in range(len(self.played_suspects)):
            self.probability_matrix[card_index, id_number] = 0
        self.probability_matrix[card_index, player_id] = 1


