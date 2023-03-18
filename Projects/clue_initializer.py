import numpy as np
import clue

width = 24
height = 25

rooms = ['Study', 'Hall', 'Lounge', 'Dining Room', 'Kitchen', 'Ballroom', 'Conservatory', 'Billiard Room', 'Library']
suspects = ['Green', 'White', 'Peacock', 'Plum', 'Scarlett', 'Mustard']
weapons = ['Revolver', 'Dagger', 'Lead Pipe', 'Rope', 'Candlestick', 'Wrench']


def make_block_unreachable(bottom_left, top_right, board):
	new_board = np.zeros((width, height))
	for i in range(width):
		for j in range(height):
			if (bottom_left[0] <= i <= top_right[0]) and (bottom_left[1] <= j <= top_right[1]):
				new_board[i, j] = -1
			else:
				new_board[i, j] = board[i, j]
	return new_board


def create_board(x, y):
	board = np.zeros((x, y))
	for i in range(25):
		board[0, i] = -1
		board[-1, i] = -1
	for j in range(24):
		board[j, 0] = -1
		board[j, -1] = -1
	board = make_block_unreachable((0, 0), (5, 5), board)
	board[5, 5] = 0
	board = make_block_unreachable((0, 7), (5, 11), board)
	board = make_block_unreachable((0, 14), (5, 18), board)
	board[6, 14] = -1
	board[6, 15] = -1
	board[6, 16] = -1
	board = make_block_unreachable((0, 21), (6, 24), board)
	board = make_block_unreachable((8, 2), (15, 7), board)
	board[10, 1] = -1
	board[11, 1] = -1
	board[12, 1] = -1
	board = make_block_unreachable((18, 0), (23, 6), board)
	board = make_block_unreachable((16, 10), (23, 15), board)
	board[19, 9] = -1
	board[20, 9] = -1
	board[21, 9] = -1
	board[22, 9] = -1
	board[23, 9] = -1
	board = make_block_unreachable((17, 19), (x, y), board)
	board = make_block_unreachable((9, 18), (14, y), board)
	board = make_block_unreachable((9, 10), (13, 16), board)
	board[0, 6] = 0
	board[0, 19] = 0
	board[16, -1] = 0
	board[-1, 17] = 0
	board[9, 0] = 0
	board[14, 0] = 0
	board[23, 17] = 0
	return board


def create_doors():
	doors = dict()
	doors['Study'] = [(6, 20)]
	doors['Library'] = [(7, 16), (3, 13)]
	doors['Billiard Room'] = [(1, 13), (6, 9)]
	doors['Conservatory'] = [(5, 5)]
	doors['Ballroom'] = [(7, 5), (9, 8), (14, 8), (16, 5)]
	doors['Kitchen'] = [(19, 7)]
	doors['Dining Room'] = [(15, 12), (17, 16)]
	doors['Lounge'] = [(17, 18)]
	doors['Hall'] = [(11, 17), (12, 17), (8, 20)]
	return doors


def get_square_to_square_distances(board):
	distances = dict()
	for x1 in range(width):
		for y1 in range(height):
			for x2 in range(width):
				for y2 in range(height):
					if board[x1, y1] == -1 or board[x2, y2] == -1:
						continue
					distances[(x1, y1, x2, y2)] = 1000
					distances[(x2, y2, x1, y1)] = 1000
	while max(distances.values()) > 500:
		for (x1, y1, x2, y2) in distances.keys():
			if abs(x1 - x2) == 1 and abs(y1 - y2) == 0:
				distances[(x1, y1, x2, y2)] = 1
				continue
			if abs(x1 - x2) == 0 and abs(y1 - y2) == 1:
				distances[(x1, y1, x2, y2)] = 1
				continue
			distance = distances[(x1, y1, x2, y2)]
			if y1 > 0 and board[x1, y1 - 1] != -1:
				distance = min(distance, 1 + distances[(x1, y1 - 1, x2, y2)])
			if x1 > 0 and board[x1 - 1, y1] != -1:
				distance = min(distance, 1 + distances[(x1 - 1, y1, x2, y2)])
			if y1 < height - 1 and board[x1, y1 + 1] != -1:
				distance = min(distance, 1 + distances[(x1, y1 + 1, x2, y2)])
			if x1 < width - 1 and board[x1 + 1, y1] != -1:
				distance = min(distance, 1 + distances[(x1 + 1, y1, x2, y2)])
			distances[(x1, y1, x2, y2)] = distance
	return distances


def get_square_to_room_distances(board, doors):
	distances = dict()
	for x in range(width):
		for y in range(height):
			for room in rooms:
				if board[x, y] == -1:
					continue
				distances[(x, y, room)] = 1000
	while max(distances.values()) > 500:
		for (x1, y1, room) in distances.keys():
			if (x1, y1) in doors[room]:
				distances[(x1, y1, room)] = 1
			
			distance = distances[(x1, y1, room)]
			if y1 > 0 and board[x1, y1 - 1] != -1:
				distance = min(distance, 1 + distances[(x1, y1 - 1, room)])
			if x1 > 0 and board[x1 - 1, y1] != -1:
				distance = min(distance, 1 + distances[(x1 - 1, y1, room)])
			if y1 < height - 1 and board[x1, y1 + 1] != -1:
				distance = min(distance, 1 + distances[(x1, y1 + 1, room)])
			if x1 < width - 1 and board[x1 + 1, y1] != -1:
				distance = min(distance, 1 + distances[(x1 + 1, y1, room)])
			distances[(x1, y1, room)] = distance
	return distances


def get_room_to_room_distances(doors, square_to_room_distances):
	distances = dict()
	for r1 in rooms:
		for r2 in rooms:
			if r1 == r2:
				distances[(r1, r2)] = 0
				continue
			if 'Study' in [r1, r2] and 'Kitchen' in [r1, r2]:
				distances[(r1, r2)] = 0
				distances[(r2, r1)] = 0
				continue
			if 'Lounge' in [r1, r2] and 'Conservatory' in [r1, r2]:
				distances[(r1, r2)] = 0
				distances[(r2, r1)] = 0
				continue
			doors1 = doors[r1]
			d = 1 + min([square_to_room_distances[(x, y, r2)] for (x, y) in doors1])
			distances[(r1, r2)] = d
			distances[(r2, r1)] = d
	return distances


def get_start_locations():
	locations = dict()
	locations['Plum'] = (0, 19)
	locations['Peacock'] = (0, 6)
	locations['Green'] = (9, 0)
	locations['White'] = (14, 0)
	locations['Mustard'] = (23, 17)
	locations['Scarlett'] = (16, 24)
	return locations


def check_room_to_room(room_to_room_distances):
	assert room_to_room_distances[('Study', 'Kitchen')] == 0
	assert room_to_room_distances[('Conservatory', 'Lounge')] == 0
	assert room_to_room_distances[('Study', 'Library')] == 7
	assert room_to_room_distances[('Billiard Room', 'Library')] == 4, room_to_room_distances[('Billiard Room', 'Library')]
	assert room_to_room_distances[('Billiard Room', 'Conservatory')] == 7
	assert room_to_room_distances[('Ballroom', 'Conservatory')] == 4
	assert room_to_room_distances[('Ballroom', 'Kitchen')] == 7
	assert room_to_room_distances[('Dining Room', 'Kitchen')] == 11
	assert room_to_room_distances[('Dining Room', 'Lounge')] == 4
	assert room_to_room_distances[('Lounge', 'Hall')] == 8
	assert room_to_room_distances[('Study', 'Hall')] == 4


def check_doors(board, doors):
	for all_doors in doors.values():
		for (x, y) in all_doors:
			assert board[x, y] != -1
			assert (board[x-1, y] == -1) or (board[x+1, y] == -1) or (board[x, y + 1] == -1) or (board[x, y - 1] == -1)


def initialize_clue(num_players):
	clue_board = create_board(width, height)
	doors = create_doors()
	square_to_square_distances = get_square_to_square_distances(clue_board)
	square_to_room_distances = get_square_to_room_distances(clue_board, doors)
	room_to_room_distances = get_room_to_room_distances(doors, square_to_room_distances)
	locations = get_start_locations()
	check_room_to_room(room_to_room_distances)
	check_doors(clue_board, doors)
	return clue.Clue(rooms, suspects, weapons, clue_board, doors, square_to_square_distances,
			square_to_room_distances, room_to_room_distances, locations, num_players)


def reset_clue(clue_instance):
	clue_instance.set_locations(get_start_locations())
	clue_instance.set_played_suspects()
	clue_instance.set_true_values()
	clue_instance.set_card_assignments()
	clue_instance.set_turn()




