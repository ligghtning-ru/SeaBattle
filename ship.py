from shipdescriptor import ShipDescriptor


class Ship:
    x = ShipDescriptor()
    y = ShipDescriptor()
    tp = ShipDescriptor()
    length = ShipDescriptor()
    is_move = ShipDescriptor()

    def __init__(self, length, tp=1, x=None, y=None):
        self._x = x
        self._y = y
        self._tp = tp
        self._length = length
        self.is_move = True
        self._cells = [1 for _ in range(length)]

    def get_start_coords(self):
        return self._x, self._y

    def move(self, go):
        if self.is_move:

            if self._tp == 1:
                self._y += go
            elif self._tp == 2:
                self._x += go

    def is_collide(self, ship):
        self_cords = ((self.x, self.y),) + tuple(
            (self.x, self.y + i) if self.tp == 1 else (self.x + i, self.y) for i in range(1, self.length))
        ship_cords = ((ship.x, ship.y),) + tuple(
            (ship.x, ship.y + i) if ship.tp == 1 else (ship.x + i, ship.y) for i in range(1, ship.length))

        for el in self_cords:

            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    x, y = el[0] + dx, el[1] + dy

                    if (x, y) in ship_cords:
                        return True
        return False

    def is_out_pole(self, size):
        self_cords = ((self.x, self.y),) + tuple(
            (self.x, self.y + i) if self.tp == 1 else (self.x + i, self.y) for i in range(1, self.length))
        if any(map(lambda x: not (0 <= x[0] < size) or not (0 <= x[1] < size), self_cords)):
            return True
        return False

    def check_destroy(self):
        if all(el == 2 for el in self._cells):
            return True
        return False

    def __getitem__(self, item):
        if item in range(len(self._cells)):
            return self._cells[item]

    def __setitem__(self, key, value):
        if value in (1, 2):
            self._cells[key] = value
