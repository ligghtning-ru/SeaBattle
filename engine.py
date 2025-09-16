from bot import SmartBot


class SeaBattle:
    def __init__(self, size, human_ships, bot_ships, human_game_pole):
        self._size = size
        self._human_ships = human_ships
        self._bot_ships = bot_ships
        self._human_game_pole = human_game_pole
        self._winner = None
        self._shots_by_human = 0
        self._human_shots = set()
        self._bot_shots = set()
        self._bot = SmartBot(size, human_ships) if human_ships else None

    def human_shot_target(self, x, y):
        if (x, y) in self._human_shots:
            return 'already_shot'

        self._human_shots.add((x, y))
        shot_result = 'pass'

        for ship in self._bot_ships:
            ship_coords = self.get_ship_coordinates(ship)
            if (x, y) in ship_coords:
                cell_index = ship_coords.index((x, y))
                ship[cell_index] = 2

                if ship.check_destroy():
                    self.mark_area_around_ship(ship)
                    shot_result = 'destroyed'
                else:
                    shot_result = 'hit'
                break

        return shot_result

    @staticmethod
    def get_ship_coordinates(ship):
        coords = [(ship.x, ship.y)]
        for i in range(1, ship.length):
            if ship.tp == 1:
                coords.append((ship.x, ship.y + i))
            else:
                coords.append((ship.x + i, ship.y))
        return coords

    def mark_area_around_ship(self, ship):
        ship_coords = self.get_ship_coordinates(ship)
        for x, y in ship_coords:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self._size and 0 <= ny < self._size and
                            (nx, ny) not in self._human_shots):
                        self._human_shots.add((nx, ny))

    def bot_shot(self):
        if self._bot:
            self._bot.general_shot()
            for shot in self._bot.get_cords():
                self._bot_shots.add(shot)

    def get_human_shots(self):
        return self._human_shots

    def update_shots_by_human(self):
        self._shots_by_human += 1

    def get_bot_shots(self):
        return self._bot_shots

    def get_human_ships(self):
        return self._human_ships

    def get_bot_ships(self):
        return self._bot_ships

    def check_winner(self):
        if all(el.check_destroy() for el in self._bot_ships):
            self._winner = 'human'
            self._bot = None
        elif all(el.check_destroy() for el in self._human_ships):
            self._winner = 'bot'
            self._bot = None
        return self._winner
