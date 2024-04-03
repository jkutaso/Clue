WIDTH = 24
HEIGHT = 25
PROBABILISTIC_AGGRESSION = 0

ROOMS = ['Study', 'Hall', 'Lounge', 'Dining Room', 'Kitchen', 'Ballroom', 'Conservatory', 'Billiard Room', 'Library']
SUSPECTS = ['Green', 'White', 'Peacock', 'Plum', 'Scarlett', 'Mustard']
WEAPONS = ['Revolver', 'Dagger', 'Lead Pipe', 'Rope', 'Candlestick', 'Wrench']

DOOR_LOCATIONS = dict()
DOOR_LOCATIONS['Study'] = [(6, 20)]
DOOR_LOCATIONS['Library'] = [(7, 16), (3, 13)]
DOOR_LOCATIONS['Billiard Room'] = [(1, 13), (6, 9)]
DOOR_LOCATIONS['Conservatory'] = [(5, 5)]
DOOR_LOCATIONS['Ballroom'] = [(7, 5), (9, 8), (14, 8), (16, 5)]
DOOR_LOCATIONS['Kitchen'] = [(19, 7)]
DOOR_LOCATIONS['Dining Room'] = [(15, 12), (17, 16)]
DOOR_LOCATIONS['Lounge'] = [(17, 18)]
DOOR_LOCATIONS['Hall'] = [(11, 17), (12, 17), (8, 20)]

START_LOCATIONS = dict()
START_LOCATIONS['Plum'] = (0, 19)
START_LOCATIONS['Peacock'] = (0, 6)
START_LOCATIONS['Green'] = (9, 0)
START_LOCATIONS['White'] = (14, 0)
START_LOCATIONS['Mustard'] = (23, 17)
START_LOCATIONS['Scarlett'] = (16, 24)

UNREACHABLE_BLOCKS = [((0, 0), (5, 5)), ((0, 7), (5, 11)), ((0, 14), (5, 18)), ((0, 21), (6, 24)), ((8, 2), (15, 7)),
                      ((18, 0), (23, 6)), ((16, 10), (23, 15)), ((17, 19), (24, 25)), ((9, 18), (14, 25)),
                      ((9, 10), (13, 16))]

UNREACHABLE_SQUARES = [(6, 14), (6, 15), (6, 16), (10, 1), (11, 1), (12, 1), (19, 9), (20, 9), (21, 9), (22, 9),
                       (23, 9)]
for i in range(HEIGHT):
    UNREACHABLE_SQUARES.append((0, i))
    UNREACHABLE_SQUARES.append((-1, i))
for j in range(WIDTH):
    UNREACHABLE_SQUARES.append((j, 0))
    UNREACHABLE_SQUARES.append((j, -1))

