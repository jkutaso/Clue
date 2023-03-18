import numpy as np


class Clue:
	def __init__(self, rooms, suspects, weapons, board, doors, square_to_square_distances, 
		square_to_room_distances, room_to_room_distances, locations, num_players):
		self.rooms = rooms
		self.suspects = suspects
		self.weapons = weapons
		self.board = board
		self.doors = doors
		self.width = 24
		self.height = 25
		self.square_to_square_distances = square_to_square_distances
		self.square_to_room_distances = square_to_room_distances
		self.room_to_room_distances = room_to_room_distances
		self.locations = locations
		self.num_players = num_players
		self.played_suspects = np.random.choice(suspects, num_players, replace=False)
		#print("Players are {}".format(self.played_suspects))
		self.true_suspect = np.random.choice(suspects)
		self.true_weapon = np.random.choice(weapons)
		self.true_room = np.random.choice(rooms)
		#print("True suspect, weapon, room is {}, {}, {}".format(self.true_suspect, self.true_weapon, self.true_room))
		self.assigned_cards = dict()
		cards_in_play = [x for x in rooms + suspects + weapons if x not in [self.true_room, self.true_suspect, self.true_weapon]]
		np.random.shuffle(cards_in_play)
		for i in range(num_players):
			self.assigned_cards[i] = cards_in_play[i * len(cards_in_play)//num_players: (i+1) * len(cards_in_play)//num_players]
			#print("Cards assigned to {} are {}".format(i, self.assigned_cards[i]))
		assert sum([len(self.assigned_cards[i]) for i in range(num_players)]) + 3 == len(rooms) + len(suspects) + len(weapons)
		self.turn = np.random.choice(len(self.played_suspects))

	def get_current_turn(self):
		return self.turn

	def get_rooms(self):
		return self.rooms

	def get_suspects(self):
		return self.suspects

	def get_weapons(self):
		return self.weapons

	def get_locations(self):
		return self.locations

	def get_square_to_square_distances(self):
		return self.square_to_square_distances

	def get_square_to_room_distances(self):
		return self.square_to_room_distances

	def get_room_to_room_distances(self):
		return self.room_to_room_distances

	def get_cards(self, player_id):
		return self.assigned_cards[player_id]

	def get_player_card_count(self):
		card_count = dict()
		for i in range(self.num_players):
			card_count[i] = len(self.assigned_cards[i])
		return card_count

	def get_played_suspects(self):
		return self.played_suspects

	def update_turn(self, new_turn):
		self.turn = new_turn

	def get_true_room(self):
		return self.true_room

	def get_true_weapon(self):
		return self.true_weapon

	def get_true_suspect(self):
		return self.true_suspect

	def get_board(self):
		return self.board

	def update_location(self, suspect, location):
		self.locations[suspect] = location

	def set_locations(self, locations):
		self.locations = locations

	def set_played_suspects(self):
		self.played_suspects = np.random.choice(self.suspects, self.num_players, replace=False)

	def set_true_values(self):
		self.true_suspect = np.random.choice(self.suspects)
		self.true_weapon = np.random.choice(self.weapons)
		self.true_room = np.random.choice(self.rooms)

	def set_card_assignments(self):
		self.assigned_cards = dict()
		cards_in_play = [x for x in self.rooms + self.suspects + self.weapons if x not in [self.true_room, self.true_suspect, self.true_weapon]]
		np.random.shuffle(cards_in_play)
		for i in range(self.num_players):
			self.assigned_cards[i] = cards_in_play[i * len(cards_in_play) // self.num_players: (i + 1) * len(cards_in_play) // self.num_players]
			#print("Cards assigned to {} are {}".format(i, self.assigned_cards[i]))

	def set_turn(self):
		self.turn = np.random.choice(len(self.played_suspects))




	
