# Описываем классы: классы всегда начинаются с Заглавной буквы
# Dot - клас точек по х и у
# Ship - класс кораблей на поле
# Board - доска
# Player, AI - игрок и копуктер
# Game - класс самой игры, расположение досок, описание
from random import randint
from colorama import *


# далее опрделям имена классов и их содержимое

class Color:
    red_ = '\33[31m'
    no_color = '\33[0m'
    blue_ = '\33[34m'


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Попытка выстрелить вне доски!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "В данную клетку уже стреляли"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, _l_, o):
        self.bow = bow
        self._l_ = _l_
        self.o = o
        self.lives = _l_

    @property
    def dots(self):
        ship_dots = []
        for i in range(self._l_):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):  # названия функций входящих в Board
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["*"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "H"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "    1   2   3   4   5   6  "   # размечаем нашу доску по горизонтали и вертикали
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("H", "*")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = Color.red_ + "X" + Color.no_color
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:  # названия функций входящих в Player
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):  # добавляем исключение, то есть будем вводить данные пока правильно
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход:").split()

            if len(cords) != 2:
                print(" Введите 2 координаты!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


def greet():  # функция класса приветсвия, на экран выводится приветственный текст
    print("-------------------")
    print(Fore.GREEN + """   Приветсвую Вас
      в игре
   'морской бой'    """ + Color.no_color)
    print("-------------------")
    print(" формат ввода через пробел:")
    print(" x - номер строки  ")
    print(" y - номер столбца ")


class Game:
    def __init__(self, size=6):  # названия функций входящих в Game
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [1, 1, 1, 1, 2, 2, 3]  # количество кораблей на доске, количество ходов
        board = Board(size=self.size)
        attempts = 0
        for l_ in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l_, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def loop(self):  # отображение досок при запуске и после хода игроков
        num = 0
        while True:
            print("--" * 14)
            print(Fore.BLUE + "Ваша доска:" + Color.no_color)
            print("--" * 14)
            print(self.us.board)
            print("--" * 14)
            print(Fore.BLUE + "Доска компьютера:" + Color.no_color)
            print("--" * 14)
            print(self.ai.board)
            if num % 2 == 0:
                print("--" * 14)
                repeat = self.us.move()
            else:
                print("--" * 14)
                print("Ход компьютера!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
                pass
            if self.ai.board.count == 7:
                print("--" * 14)
                print("Вы победили :) ")
                break

            if self.us.board.count == 7:
                print("--" * 14)
                print("""Вы проиграли :( 
                Побел компьютер """)
                break
            num += 1

    def start(self):
        greet()
        self.loop()


g = Game()
g.start()
