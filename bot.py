from random import randint, choice, shuffle


class BotState:
    def bot_shot(self, size, checked_cords, human_ships, probability_map, shot):
        return NotImplementedError

    def update_state(self, res, x, y):
        return NotImplementedError


class Shot:
    def __init__(self, bot):
        self.__bot = bot

    def bot_shot(self, x, y, human_ships):
        for ship in human_ships:
            ship_cords = ((ship.x, ship.y),) + tuple(
                (ship.x + i, ship.y) if ship.tp == 2 else (ship.x, ship.y + i) for i in range(1, ship.length))

            if (x, y) in ship_cords:
                cell_index = ship_cords.index((x, y))
                ship[cell_index] = 2

                if ship.check_destroy():
                    self.__bot.bot_shots_to_destroyed_ship(ship_cords)
                    return 'destroyed'
                return 'hit'
        return 'pass'


class SmartBot(BotState):
    def __init__(self, size, human_ships):
        self._state = RandomShot(self)
        self._size = size
        self._checked_cords = []
        self._human_ships = human_ships
        self._probability_map = ProbabilityMap(size)
        self._shot = Shot(self)
        self._detected_ship = None
        self._chessboard = ChessBoard(size, self)
        self._orientation = None
        self._shot_count = 0
        self._debug = True

    def general_shot(self):
        self._state.bot_shot(self._size, self._checked_cords, self._human_ships, self._probability_map, self._shot)

    def update_general_state(self, res, x, y):
        if res == 'hit':
            self._state = HuntState(x, y, self)
        elif res == 'destroyed':
            self._state = ShotOnProbability(self)
        elif res == 'no_targets':
            self._state = self._chessboard

    def bot_shots_to_destroyed_ship(self, ship_cords):
        for cord in ship_cords:
            x, y = cord

            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):

                    cur_x, cur_y = x + dx, y + dy

                    if (cur_x, cur_y) in ship_cords or (cur_x, cur_y) in self._checked_cords:
                        continue

                    if not (0 <= cur_x < self._size) or not (0 <= cur_y < self._size):
                        continue

                    self._checked_cords.append((cur_x, cur_y))

    def update_cords(self, cords):
        self._checked_cords.append(cords)

    def get_cords(self):
        return self._checked_cords

    def update_detected_ship(self, ship):
        self._detected_ship = ship

    def get_detected_ship(self):
        return self._detected_ship


class ShotOnProbability(BotState):
    def __init__(self, link):
        self._link = link

    def bot_shot(self, size, checked_cords, human_ships, probability_map, shot):
        probability_map.update_map(human_ships, checked_cords)
        prob_map = probability_map.get_map()
        probability = -1
        targets = []

        for x in range(size):
            for y in range(size):
                if (x, y) not in checked_cords:
                    if prob_map[x][y] > probability:
                        probability = prob_map[x][y]
                        targets = [(x, y)]
                    elif prob_map[x][y] == probability:
                        targets.append((x, y))

        if targets:
            if len(targets) > 1:
                best_target = self.__choose_best_target(targets, size, checked_cords)
                x, y = best_target
                res = shot.bot_shot(x, y, human_ships)
            else:
                x, y = choice(targets)
                res = shot.bot_shot(x, y, human_ships)
            self._link.update_cords((x, y))
            self.update_state(res, x, y)
        else:
            res = 'no_targets'
            self.update_state(res, None, None)

    def update_state(self, res, x, y):
        self._link.update_general_state(res, x, y)

    @staticmethod
    def __choose_best_target(targets, size, checked_cords):
        scores = []

        for x, y in targets:
            score = 0

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                for i in range(1, 5):
                    nx, ny = x + dx * i, y + dy * i

                    if not (0 <= nx < size and 0 <= ny < size):
                        break
                    if (nx, ny) not in checked_cords:
                        score += 1

            scores.append(score)

        return targets[scores.index(max(scores))]


class RandomShot(BotState):
    def __init__(self, link):
        self._link = link

    def bot_shot(self, size, checked_cords, human_ships, probability_map, shot):
        while True:
            x, y = randint(0, size - 1), randint(0, size - 1)
            if (x, y) not in checked_cords:
                self._link.update_cords((x, y))
                break

        res = shot.bot_shot(x, y, human_ships)
        probability_map.update_map(human_ships, checked_cords)
        self.update_state(res, x, y)

    def update_state(self, res, x, y):
        self._link.update_general_state(res, x, y)


class HuntState(BotState):
    def __init__(self, hit_x, hit_y, link):
        self._first_hit = (hit_x, hit_y)
        self._link = link
        self._hits = [(hit_x, hit_y)]
        self._targets = self._generate_targets()
        self._attempts = 0
        self._max_attempts = 20

    def _generate_targets(self):
        targets = set()

        if len(self._hits) == 2:
            self._check_orientation()

        for hit_x, hit_y in self._hits:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = hit_x + dx, hit_y + dy
                if self._is_valid_target(nx, ny):
                    if self._link._orientation == 'horizontal' and dx != 0:
                        continue
                    elif self._link._orientation == 'vertical' and dy != 0:
                        continue
                    targets.add((nx, ny))

        return list(targets)

    def _is_valid_target(self, x, y):
        return (0 <= x < self._link._size and
                0 <= y < self._link._size and
                (x, y) not in self._link.get_cords())

    def _check_orientation(self):
        x1, y1 = self._hits[0]
        x2, y2 = self._hits[1]

        if x1 == x2:
            self._link._orientation = 'horizontal'
        elif y1 == y2:
            self._link._orientation = 'vertical'

    def bot_shot(self, size, checked_cords, human_ships, probability_map, shot):
        self._attempts += 1

        if len(self._hits) == 2:
            self._check_orientation()

        if self._attempts > self._max_attempts:
            self._link.update_general_state('no_targets', None, None)
            return

        if not self._targets:
            self._targets = self._generate_targets()

        if not self._targets:
            self._link.update_general_state('no_targets', None, None)
            return

        x, y = self._targets.pop()

        res = shot.bot_shot(x, y, human_ships)
        self._link.update_cords((x, y))

        if res == 'hit':
            self._hits.append((x, y))
            self._targets = self._generate_targets()
            self._attempts = 0

        self.update_state(res, x, y)

    def update_state(self, res, x, y):
        if res == 'destroyed':
            self._link._orientation = None
            self._link.update_general_state('destroyed', x, y)
        elif res == 'hit':
            self._link.update_general_state('hit', x, y)
        else:
            self._link.update_general_state('pass', x, y)


class ChessBoard(BotState):
    def __init__(self, size, link):
        self._size = size
        self._link = link
        self._init_targets()

    def _init_targets(self):
        self._chessboard_targets = []
        for x in range(self._size):
            for y in range(self._size):
                if (x + y) % 2 == 0:
                    self._chessboard_targets.append((x, y))
        shuffle(self._chessboard_targets)

    def choose_cord(self):
        for x, y in self._chessboard_targets:
            if (x, y) not in self._link.get_cords():
                self._link.update_cords((x, y))
                return x, y
        return None, None

    def bot_shot(self, size, checked_cords, human_ships, probability_map, shot):
        x, y = self.choose_cord()
        if x is not None and y is not None:
            res = shot.bot_shot(x, y, human_ships)
            self.update_state(res, x, y)
        else:
            self._link.update_general_state('no_targets', None, None)

    def update_state(self, res, x, y):
        if res in ('hit', 'destroyed'):
            self._link.update_general_state(res, x, y)


class ProbabilityMap:
    def __init__(self, size):
        self._size = size
        self._map = [[0 for _ in range(size)] for _ in range(size)]
        self._ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

    def update_map(self, ships, checked_cords):
        for x in range(self._size):
            for y in range(self._size):
                self._map[x][y] = 0

        active_ships = [s for s in ships if not s.check_destroy()]
        active_sizes = [s.length for s in active_ships]

        if max(active_sizes) <= 2:
            return self._update_map_small_ships(checked_cords)

        for ship_size in active_sizes:
            for orientation in [1, 2]:
                for x in range(self._size):
                    for y in range(self._size):
                        if self._can_place_ship(x, y, ship_size, orientation, checked_cords):
                            self._add_ship_weight(x, y, ship_size, orientation)

    def _update_map_small_ships(self, checked_cords):
        for x in range(self._size):
            for y in range(self._size):
                if (x, y) in checked_cords:
                    continue

                empty_around = 0
                for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self._size and 0 <= ny < self._size and (nx, ny) in checked_cords:
                        empty_around += 1

                self._map[x][y] = empty_around * 10

    def _can_place_ship(self, x, y, length, orientation, checked_cords):
        if orientation == 1:
            if y + length >= self._size:
                return False
            for i in range(length):
                if (x, y + i) in checked_cords:
                    return False
        else:
            if x + length >= self._size:
                return False
            for i in range(length):
                if (x + i, y) in checked_cords:
                    return False
        return True

    def _add_ship_weight(self, x, y, length, orientation):
        weight = length * 2

        if orientation == 1:
            for i in range(length):
                self._map[x][y + i] += weight
        else:
            for i in range(length):
                self._map[x + i][y] += weight

    def get_map(self):
        return self._map
