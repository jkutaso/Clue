import numpy as np
from .constants import WIDTH, HEIGHT, ROOMS, UNREACHABLE_BLOCKS, UNREACHABLE_SQUARES, START_LOCATIONS, DOOR_LOCATIONS


class ClueBoard:
	def __init__(self):
		self._create_board(WIDTH, HEIGHT)
		self.square_to_square_distances = self._construct_square_to_square_distances()
		self.square_to_room_distances = self._construct_square_to_room_distances()
		self.room_to_room_distances = self._construct_room_to_room_distances()
		self._check_room_to_room()
		self._check_doors()

	def _make_block_unreachable(self, bottom_left, top_right, board):
		for i in range(WIDTH):
			for j in range(HEIGHT):
				if (bottom_left[0] <= i <= top_right[0]) and (bottom_left[1] <= j <= top_right[1]):
					self.board[i, j] = -1

	def _create_board(self, x, y):
		self.board = np.zeros((x, y))
		for block in UNREACHABLE_BLOCKS:
			self._make_block_unreachable(block[0], block[1], self.board)
		for square in UNREACHABLE_SQUARES:
			self.board[square] = -1
		for square in START_LOCATIONS.values():

			self.board[square] = 0

		for square_list in DOOR_LOCATIONS.values():
			for square in square_list:
				self.board[square] = 0
	def _initialize_distances_to_inf(self):
		distances = dict()
		for x1 in range(WIDTH):
			for y1 in range(HEIGHT):
				for x2 in range(WIDTH):
					for y2 in range(HEIGHT):
						if self.board[x1, y1] == -1 or self.board[x2, y2] == -1:
							continue
						distances[(x1, y1, x2, y2)] = np.inf
						distances[(x2, y2, x1, y1)] = np.inf
		return distances

	def _set_adjacent_squares_to_distance_one(self, distances):
		for (x1, y1, x2, y2) in distances.keys():
			if abs(x1 - x2) == 1 and abs(y1 - y2) == 0:
				distances[(x1, y1, x2, y2)] = 1
			if abs(x1 - x2) == 0 and abs(y1 - y2) == 1:
				distances[(x1, y1, x2, y2)] = 1
		return distances

	def _construct_square_to_square_distances(self):
		distances = self._initialize_distances_to_inf()
		distances = self._set_adjacent_squares_to_distance_one(distances)
		while max(distances.values()) > 100:

			for (x1, y1, x2, y2) in distances.keys():
				distance = min(distances[(x1, y1, x2, y2)], distances[(x2, y2, x1, y1)])

				if y1 > 0 and self.board[x1, y1 - 1] != -1:
					distance = min(distance, 1 + distances[(x1, y1 - 1, x2, y2)])
				if x1 > 0 and self.board[x1 - 1, y1] != -1:
					distance = min(distance, 1 + distances[(x1 - 1, y1, x2, y2)])
				if y1 < HEIGHT - 1 and self.board[x1, y1 + 1] != -1:
					distance = min(distance, 1 + distances[(x1, y1 + 1, x2, y2)])
				if x1 < WIDTH - 1 and self.board[x1 + 1, y1] != -1:
					distance = min(distance, 1 + distances[(x1 + 1, y1, x2, y2)])
				distances[(x1, y1, x2, y2)] = distance
				distances[(x2, y2, x1, y1)] = distance
		return distances

	def _initialize_square_to_room_distances_to_inf(self):
		distances = dict()
		for x in range(WIDTH):
			for y in range(HEIGHT):
				for room in ROOMS:
					if self.board[x, y] == -1:
						continue
					distances[(x, y, room)] = np.inf
		return distances

	def _construct_square_to_room_distances(self):
		distances = self._initialize_square_to_room_distances_to_inf()
		for (x1, y1, room) in distances.keys():
			if (x1, y1) in DOOR_LOCATIONS[room]:
				distances[(x1, y1, room)] = 1
		while max(distances.values()) > 100:
			for (x1, y1, room) in distances.keys():
				distance = distances[(x1, y1, room)]
				if y1 > 0 and self.board[x1, y1 - 1] != -1:
					distance = min(distance, 1 + distances[(x1, y1 - 1, room)])
				if x1 > 0 and self.board[x1 - 1, y1] != -1:
					distance = min(distance, 1 + distances[(x1 - 1, y1, room)])
				if y1 < HEIGHT - 1 and self.board[x1, y1 + 1] != -1:
					distance = min(distance, 1 + distances[(x1, y1 + 1, room)])
				if x1 < WIDTH - 1 and self.board[x1 + 1, y1] != -1:
					distance = min(distance, 1 + distances[(x1 + 1, y1, room)])
				distances[(x1, y1, room)] = distance

		return distances

	def _construct_room_to_room_distances(self):
		distances = dict()
		for r1 in ROOMS:
			for r2 in ROOMS:
				if r1 == r2:
					distances[(r1, r2)] = 0
					continue
				d = 1 + min([self.square_to_room_distances[(x, y, r2)] for (x, y) in DOOR_LOCATIONS[r1]])
				distances[(r1, r2)] = d
				distances[(r2, r1)] = d
		distances[('Study', 'Kitchen')] = 0
		distances[('Kitchen', 'Study')] = 0
		distances[('Lounge', 'Conservatory')] = 0
		distances[('Conservatory', 'Lounge')] = 0

		return distances

	def _check_room_to_room(self):
		assert self.room_to_room_distances[('Study', 'Kitchen')] == 0
		assert self.room_to_room_distances[('Conservatory', 'Lounge')] == 0
		assert self.room_to_room_distances[('Study', 'Library')] == 7
		assert self.room_to_room_distances[('Billiard Room', 'Library')] == 4
		assert self.room_to_room_distances[('Billiard Room', 'Conservatory')] == 7
		assert self.room_to_room_distances[('Ballroom', 'Conservatory')] == 4
		assert self.room_to_room_distances[('Ballroom', 'Kitchen')] == 7
		assert self.room_to_room_distances[('Dining Room', 'Kitchen')] == 11
		assert self.room_to_room_distances[('Dining Room', 'Lounge')] == 4
		assert self.room_to_room_distances[('Lounge', 'Hall')] == 8
		assert self.room_to_room_distances[('Study', 'Hall')] == 4

	def _check_doors(self):
		for all_doors in DOOR_LOCATIONS.values():
			for (x, y) in all_doors:
				assert self.board[x, y] != -1
				assert (self.board[x-1, y] == -1) or (self.board[x+1, y] == -1) or (self.board[x, y + 1] == -1) or (self.board[x, y - 1] == -1)

	def get_square_to_square_distances(self):
		return self.square_to_square_distances

	def get_square_to_room_distances(self):
		return self.square_to_room_distances

	def get_room_to_room_distances(self):
		return self.room_to_room_distances

	def get_board(self):
		return self.board



