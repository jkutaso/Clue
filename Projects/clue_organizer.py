import numpy as np
from clue_initializer import initialize_clue, reset_clue
from naive_clue_player import NaiveCluePlayer
from probabilistic_clue_player import ProbabilisticCluePlayer
PLAYER_TYPES = ['Naive'] * 3 + ['Probabilistic']
DEBUGGING = False


def roll(debugging):
    r = 2 + sum(np.random.choice(6, 2))
    if debugging:
        print("Player rolls {}".format(r))
    return r


def increment_id(players, player_id, clue_instance):
    next_player_id = (player_id + 1) % len(clue_instance.get_played_suspects())
    while players[next_player_id] == -1:
        next_player_id = (next_player_id + 1) % len(clue_instance.get_played_suspects())
    return next_player_id


def initialize_players(player_types, clue_instance, debugging):
    players = dict()
    for i in range(len(player_types)):
        if debugging:
            print("Cards assigned to", i, clue_instance.get_cards(i))
        if player_types[i] == 'Naive':
            players[i] = NaiveCluePlayer(clue_instance.get_rooms(), clue_instance.get_suspects(), clue_instance.get_weapons(),
                                         clue_instance.get_cards(i), clue_instance.get_player_card_count(), i, clue_instance.get_played_suspects())
        elif player_types[i] == 'Probabilistic':

            players[i] = ProbabilisticCluePlayer(clue_instance.get_rooms(), clue_instance.get_suspects(), clue_instance.get_weapons(),
                                         clue_instance.get_cards(i), clue_instance.get_player_card_count(), i, clue_instance.get_played_suspects())

        else:
            assert False
    return players


def check_ruled_out_rooms(current_player, players):
    ruled_out_rooms = current_player.ruled_out_rooms
    for i in ruled_out_rooms.keys():
        ruled_out_i = ruled_out_rooms[i]
        for room in ruled_out_i:
            assert room not in players[i].cards, (room, i)


def get_current_turn(clue_instance, players, debugging):
    current_player_id = clue_instance.get_current_turn()
    current_player = players[current_player_id]

    while current_player == -1:
        if debugging:
            print("Player {} is already eliminated".format(current_player_id))
        current_player_id = increment_id(players, current_player_id, clue_instance)
        current_player = players[current_player_id]
    if debugging:
        print("Player {} is taking their turn".format(current_player_id))
    return current_player_id, current_player, clue_instance.get_played_suspects()[current_player_id]


def handle_guess(clue_instance, current_player_id, guess, players, debugging):
    if guess == (clue_instance.get_true_room(), clue_instance.get_true_weapon(), clue_instance.get_true_suspect()):
        if True:
            print("Player {} wins by guessing {}".format(current_player_id, guess))
        return True
    else:
        if debugging:
            print("Player {} eliminated".format(current_player_id))
            print("Guessed {}".format(guess))
            print("Truth is {}".format((clue_instance.get_true_room(), clue_instance.get_true_weapon(), clue_instance.get_true_suspect())))
            assert False
        players[current_player_id] = -1
        clue_instance.update_turn((current_player_id + 1) % len(clue_instance.get_played_suspects()))
        return False


def handle_square_to_square(clue_instance, current_suspect, current_player_id, turn_decision, this_roll, debugging):
    if debugging:
        print("Player moved from {} to {}".format(clue_instance.get_locations()[current_suspect], turn_decision))
    current_location = clue.locations[current_suspect]
    if current_location in clue.get_rooms():
        assert clue.square_to_room_distances[(*turn_decision, current_location)] <= this_roll
    else:
        assert clue.square_to_square_distances[(*current_location, *turn_decision)] == this_roll
    clue.update_location(current_suspect, turn_decision)
    clue.update_turn((current_player_id + 1) % len(clue_instance.get_played_suspects()))


clue = initialize_clue(len(PLAYER_TYPES))


def _run(debugging):
    reset_clue(clue)
    assert clue.get_locations()['Plum'] == (0, 19)
    players = initialize_players(PLAYER_TYPES, clue, debugging)
    count = 0
    while True:
        count += 1
        if debugging:
            print("Turn {}".format(count))
        assert count < 100
        current_player_id, current_player, current_suspect = get_current_turn(clue, players, debugging)
        if current_player == -1:
            clue.update_turn((current_player_id + 1) % len(clue.get_played_suspects()))
            continue
        guess = current_player.ready_to_guess()
        if type(guess) != bool:
            guess_result = handle_guess(clue, current_player_id, guess, players, debugging)
            if guess_result:
                print(count)
                return current_player_id
            else:
                for player_id in range(len(players)):
                    if player_id == current_player_id:
                        continue
                    for card in clue.get_cards(current_player_id):
                        players[player_id].update_given_shown(current_player_id, card)

        this_roll = roll(debugging)
        turn_decision = current_player.take_turn(clue.get_locations(), clue.get_board(), clue.get_room_to_room_distances(), clue.get_square_to_square_distances(), clue.get_square_to_room_distances(), this_roll)
        if len(turn_decision) == 2:
            handle_square_to_square(clue, current_suspect, current_player_id, turn_decision, this_roll, debugging)
            continue
        else:
            if debugging:
                print("Player moved from {} to {}".format(clue.get_locations()[current_suspect], turn_decision[0]))

            clue.update_location(current_suspect, turn_decision[0])
            clue.update_location(turn_decision[2], turn_decision[0])
            assert turn_decision[2] in clue.get_suspects()
            assert turn_decision[0] in clue.get_rooms()
            assert turn_decision[1] in clue.get_weapons()
            if debugging:
                print("Player is asking about {} in {} with {}".format(turn_decision[2], turn_decision[0], turn_decision[1]))
            next_player_id = increment_id(players, current_player_id, clue)
            while not players[next_player_id].ask_player(*turn_decision):
                if debugging:
                    print("Player {} has nothing".format(next_player_id))
                for i in range(len(clue.get_played_suspects())):
                    if players[i] == -1:
                        continue
                    players[i].update_known_results(next_player_id, *turn_decision, False)
                next_player_id = increment_id(players, next_player_id, clue)
                if next_player_id == current_player_id:
                    break
            if next_player_id != current_player_id:
                if debugging:
                    print("Player {} is showing {}".format(next_player_id, players[next_player_id].ask_player_specific(*turn_decision)))
                current_player.update_given_shown(next_player_id, players[next_player_id].ask_player_specific(*turn_decision))
                for i in range(len(clue.get_played_suspects())):
                    if players[i] == -1:
                        continue
                    players[i].update_known_results(next_player_id, *turn_decision, True)

            else:
                if debugging:
                    print("No one showed a card")
        clue.update_turn((current_player_id + 1) % len(clue.get_played_suspects()))


wins = [0] * len(PLAYER_TYPES)
for i in range(100):
    wins[_run(DEBUGGING)] +=1

print(wins)
