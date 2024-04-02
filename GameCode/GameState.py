import numpy as np
from constants import ROOMS, SUSPECTS, WEAPONS, START_LOCATIONS


class GameState:
	def __init__(self, board, num_players):
		self.board = board
		self.locations = START_LOCATIONS.copy()
		self.num_players = num_players
		self.played_suspects = np.random.choice(SUSPECTS, num_players, replace=False)
		self.true_suspect = np.random.choice(SUSPECTS)
		self.true_weapon = np.random.choice(WEAPONS)
		self.true_room = np.random.choice(ROOMS)
		self.assigned_cards = dict()
		self._set_card_assignments()
		self.turn_id = np.random.choice(len(self.played_suspects))

		assert sum([len(self.assigned_cards[i]) for i in range(num_players)]) + 3 == len(ROOMS) + len(SUSPECTS) + len(WEAPONS)

	def get_current_turn_id(self):
		return self.turn_id

	def get_current_turn_suspect(self):
		return self.played_suspects[self.turn_id]

	def get_locations(self):
		return self.locations

	def get_cards(self, player_id):
		return self.assigned_cards[player_id]

	def get_player_card_count(self):
		card_count = dict()
		for i in range(self.num_players):
			card_count[i] = len(self.assigned_cards[i])
		return card_count

	def get_played_suspects(self):
		return self.played_suspects

	def get_true_room(self):
		return self.true_room

	def get_true_weapon(self):
		return self.true_weapon

	def get_true_suspect(self):
		return self.true_suspect

	def get_board(self):
		return self.board

	def update_turn(self, new_turn_id):
		self.turn_id = new_turn_id

	def update_location(self, suspect, location):
		self.locations[suspect] = location

	def set_locations(self, locations):
		self.locations = locations

	def _set_played_suspects(self):
		self.played_suspects = np.random.choice(SUSPECTS, self.num_players, replace=False)

	def _set_true_values(self):
		self.true_suspect = np.random.choice(SUSPECTS)
		self.true_weapon = np.random.choice(WEAPONS)
		self.true_room = np.random.choice(ROOMS)

	def _set_card_assignments(self):
		self.assigned_cards = dict()
		cards_in_play = [x for x in ROOMS + SUSPECTS + WEAPONS if x not in [self.true_room, self.true_suspect, self.true_weapon]]
		np.random.shuffle(cards_in_play)
		for i in range(self.num_players):
			self.assigned_cards[i] = cards_in_play[i * len(cards_in_play) // self.num_players: (i + 1) * len(cards_in_play) // self.num_players]

	def _set_turn_id(self):
		self.turn_id = np.random.choice(len(self.played_suspects))




	
