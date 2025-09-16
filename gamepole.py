from random import randint, choice
from ship import Ship


class GamePole:
    def __init__(self, size):
        self._size = size
        self._ships = []

    def __check_collides_with_any_ship(self, ship):
        if not any(ship.is_collide(el) for el in self._ships):
            return False
        return True

    def init(self):
        ship_numbers = {'ship_1': 4, 'ship_2': 3, 'ship_3': 2, 'ship_4': 1}

        while ship_numbers['ship_4']:
            x, y = randint(0, self._size - 1), randint(0, self._size - 1)
            tp = randint(1, 2)

            ship4_to_generate = Ship(4, tp, x, y)

            if ship4_to_generate.is_out_pole(self._size):
                continue

            self._ships.append(Ship(4, tp, x, y))
            ship_numbers['ship_4'] -= 1

        while ship_numbers['ship_3']:
            x, y = randint(0, self._size - 1), randint(0, self._size - 1)
            tp = randint(1, 2)

            ship3_to_generate = Ship(3, tp, x, y)
            if self.__check_collides_with_any_ship(ship3_to_generate) or ship3_to_generate.is_out_pole(self._size):
                continue
            ship_numbers['ship_3'] -= 1
            self._ships.append(ship3_to_generate)

        while ship_numbers['ship_2']:
            x, y = randint(0, self._size - 1), randint(0, self._size - 1)
            tp = randint(1, 2)

            ship2_to_generate = Ship(2, tp, x, y)
            if self.__check_collides_with_any_ship(ship2_to_generate) or ship2_to_generate.is_out_pole(self._size):
                continue
            ship_numbers['ship_2'] -= 1
            self._ships.append(ship2_to_generate)

        while ship_numbers['ship_1']:
            x, y = randint(0, self._size - 1), randint(0, self._size - 1)
            tp = randint(1, 2)

            ship1_to_generate = Ship(1, tp, x, y)
            if self.__check_collides_with_any_ship(ship1_to_generate) or ship1_to_generate.is_out_pole(self._size):
                continue
            self._ships.append(ship1_to_generate)
            ship_numbers['ship_1'] -= 1

    def get_ships(self):
        return self._ships

    def move_ships(self):

        for i in range(len(self._ships)):
            is_moved = False
            go_first = choice((-1, 1))
            for go in (go_first, -go_first):
                if not is_moved:
                    self._ships[i].move(go)
                else:
                    break

                move = go
                for j in range(len(self._ships)):

                    if self._ships[i] != self._ships[j] and (self._ships[i].is_collide(self._ships[j]) or
                                                             self._ships[i].is_out_pole(self._size)):
                        self._ships[i].move(-1 * move)
                        break
                else:
                    is_moved = True

    def show(self):
        pole = self.get_pole()

        for el in pole:
            print(*el)

    def get_pole(self):
        lst = [[0 for _ in range(self._size)] for _ in range(self._size)]

        for el in self._ships:
            x = el.x
            y = el.y
            lst[x][y] = el[0]
            for i in range(1, el.length):
                x += 1 if el.tp == 2 else 0
                y += 1 if el.tp == 1 else 0
                lst[x][y] = el[i]

        return tuple(map(tuple, lst))
