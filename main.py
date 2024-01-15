import numpy as np
from enum import IntEnum


class TileStatus(IntEnum):
    Empty = 0
    Black = 1
    White = 2

    @property
    def inverse_color(self):
        if self.value == 0:
            return self
        elif self.value == 1:
            return TileStatus.White
        elif self.value == 2:
            return TileStatus.Black


class MoveStatus(IntEnum):
    Human = 0
    StronkAI = 1


class AiBot:

    def __init__(self, color):
        self.color = color

    def minmax_move(self, gameboard, max_depth):
        score, x, y = self.minmax(gameboard, self.color, 3)
        gameboard.calc_move_(x, y, self.color)

    def minmax(self, gameboard, color, depth):
        if depth == 0:
            return gameboard.get_score(color),
        legal_moves = gameboard.get_legal_moves(color)
        if not legal_moves:
            return gameboard.get_score(color),

        if color == self.color:  # Максимизируем для своего цвета
            best_score = -1000000
            for x, y in legal_moves:
                if gameboard.calc_move_(x, y, color):
                    score = self.minmax(gameboard, color.inverse_color,
                                        depth - 1)[0]
                    gameboard.undo_last()
                    if score > best_score:
                        best_score, best_x, best_y = score, x, y
                else:
                    return gameboard.get_score(color),
        else:  # Минимизируем для оппонента
            best_score = 1000000
            for x, y in legal_moves:
                if gameboard.calc_move_(x, y, color):
                    score = self.minmax(gameboard, color.inverse_color,
                                        depth - 1)[0]
                    gameboard.undo_last()
                    if score < best_score:
                        best_score, best_x, best_y = score, x, y
                else:
                    return gameboard.get_score(color),
        return best_score, best_x, best_y



class GameField:
    POSSIBLE_MOVES_DIRECTIONS = [(0, 1), (1, 1), (1, 0), (1, -1),
                                 (0, -1), (-1, -1), (-1, 0), (-1, 1)]

    def __init__(self):
        self.Battlefield = np.zeros((8, 8), dtype=np.dtype('int8'))
        self.Battlefield[3][3] = 2
        self.Battlefield[3][4] = 1
        self.Battlefield[4][3] = 1
        self.Battlefield[4][4] = 2
        self.flips = []
        self.moves = []

    def reset_battlefield(self):
        self.Battlefield = np.zeros((8, 8))
        self.Battlefield[3][3] = 2
        self.Battlefield[3][4] = 1
        self.Battlefield[4][3] = 1
        self.Battlefield[4][4] = 2
        self.flips = []
        self.moves = []


    # def print_battlefield(self):
    #     print("Черные: " + str(self.get_score(1)) + " Белые: " + str(self.get_score(2)))
    #     for x in range(self.Battlefield.shape[0]):
    #         for y in range(self.Battlefield.shape[1]):
    #             print(self.Battlefield[x][y], end=' ')
    #         print()
    def print_battlefield(self):
        print("Черные: " + str(self.get_score(1)) + " Белые: " + str(self.get_score(2)))
        for x in range(self.Battlefield.shape[0]):
            for y in range(self.Battlefield.shape[1]):
                cell_value = self.Battlefield[x][y]
                if cell_value == 2:
                    print("\033[97m" + str(cell_value) + "\033[0m", end=' ')
                elif cell_value == 1:
                    print("\033[91m" + str(cell_value) + "\033[0m", end=' ')
                else:
                    print(cell_value, end=' ')
            print()
    def get_score(self, color):
        # Подсчет счета
        score = 0
        for x in range(8):
            for y in range(8):
                if self.Battlefield[x][y] == color:
                    score += 1

        return score

    def undo_last(self):
        last_flips = self.flips.pop()
        last_x, last_y = self.moves.pop()
        self.Battlefield[last_x][last_y] = TileStatus.Empty
        for x, y in last_flips:
            self.Battlefield[x][y] = TileStatus(self.Battlefield[x][y]).inverse_color

    def _check_bounds(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def _check_move_legality_(self, x, y):
        # Check the bounds and whether the cell is not occupied
        return (self._check_bounds(x, y) and
                self.Battlefield[x][y] == TileStatus.Empty)

    def calc_move_(self, x, y, tiletype):
        flips = self.check_move_(x, y, tiletype)
        if not flips:
            return None

        self.Battlefield[x][y] = tiletype
        self.moves.append([x, y])

        for x, y in flips:
            self.Battlefield[x][y] = tiletype
        self.flips.append(flips)

        # print(x, y, tiletype, flips, 'self', self.flips)
        return flips

    def check_move_(self, move_x, move_y, tiletype):
        if not self._check_move_legality_(move_x, move_y):
            return None
        self.Battlefield[move_x][move_y] = tiletype
        flips = []
        for xdir, ydir in self.POSSIBLE_MOVES_DIRECTIONS:
            x, y = move_x + xdir, move_y + ydir
            if self._check_bounds(x, y) and self.Battlefield[x][y] == tiletype.inverse_color:
                x, y = x + xdir, y + ydir
                if not self._check_bounds(x, y):
                    continue  # The for loop
                while self._check_bounds(x, y) and self.Battlefield[x][y] == tiletype.inverse_color:
                    x, y = x + xdir, y + ydir
                    if not self._check_bounds(x, y):
                        break  # The while loop
                if not self._check_bounds(x, y):
                    continue  # The for loop

                if self.Battlefield[x][y] == tiletype:

                    while True:
                        x, y = x - xdir, y - ydir
                        if x == move_x and y == move_y:
                            break
                        flips.append([x, y])
        self.Battlefield[move_x][move_y] = TileStatus.Empty
        return flips

    def get_legal_moves(self, color):
        pos = []
        for x in range(8):
            for y in range(8):
                if self.check_move_(x, y, color):
                    pos.append([x, y])
        return pos


class GameStatus:

    def __init__(self):
        color = int(input("Выберите ваш цвет, 1 - Черные, 2 - Белые"))
        if color not in (1, 2):
            color = 1
        self.HumanColor = TileStatus.Black
        if color == 2:
            self.HumanColor = TileStatus.White

        self.Board = GameField()
        self.IsEnded = False
        self.AiBot = AiBot(self.HumanColor.inverse_color)
        self.MoveStatus = MoveStatus.Human
        if self.HumanColor == TileStatus.White:
            self.MoveStatus = MoveStatus.StronkAI

    def Check_Game_end(self):
        if not self.Board.get_legal_moves(TileStatus.Black) and not self.Board.get_legal_moves(TileStatus.White):
            return True

    def ParseMove(self, move):
        if len(move) > 2:
            return False
        elif not str(move).isdigit():
            return False
        elif not self.Board.check_move_(int(move[0]), int(move[1]), self.HumanColor):
            return False
        else:
            return True

    def Human_move(self):
        test = self.Board.get_legal_moves(self.HumanColor)
        print("Доступные ходы:", test)
        move = input("Ваш ход")
        while (not self.ParseMove(move)):
            move = input("Невозможный ход проверьте ваш ввод")
        self.Board.calc_move_(int(move[0]), int(move[1]), self.HumanColor)

    def game_step(self):
        while not self.Check_Game_end():
            if self.MoveStatus == MoveStatus.Human:
                if self.Board.get_legal_moves(self.HumanColor):
                    self.Human_move()
                self.MoveStatus = MoveStatus.StronkAI
            else:
                if self.Board.get_legal_moves(self.AiBot.color):
                    self.AiBot.minmax_move(self.Board, 3)
                self.MoveStatus = MoveStatus.Human
            self.Board.print_battlefield()

        if (self.Board.get_score(self.HumanColor)>self.Board.get_score(self.AiBot.color)):
            print("Человечество еще не потеряно, вы победили машину")
        else:
            print("Игра была подставной с самого начала, куда вам тягаться с бездушным куском металла, Вы проиграли")



# [2][3] [3][2] [4][5] [5][4]
# BattleBoard = GameField()
#
# BattleBoard.print_battlefield()
#
# test = BattleBoard.get_legal_moves(TileStatus.Black)
#
# print(test)

GM = GameStatus()
GM.Board.print_battlefield()
GM.game_step()


