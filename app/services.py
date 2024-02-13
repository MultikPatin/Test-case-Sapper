import random
import uuid
from collections.abc import Generator

from pydantic import UUID4

from app.schemas import GameInfoResponse, GameTurnRequest, NewGameRequest


class Sapper:
    def __init__(self):
        self.games = {}

    def create_new_game(self, params: NewGameRequest) -> GameInfoResponse:
        game_id: UUID4 = uuid.uuid4()
        self.games[game_id] = GameField(params=params, game_id=game_id)
        res: GameInfoResponse = self.games[game_id].get_game_info_response()
        return res

    def create_new_turn(self, params: GameTurnRequest) -> GameInfoResponse:
        game_field: GameField = self.games[params.game_id]
        game_field.create_new_turn(row=params.row, col=params.col)
        res = game_field.get_game_info_response()
        return res


class GameField:
    __field: list[list["Cell"]]

    def __init__(self, params: NewGameRequest, game_id: UUID4):
        self.game_id = game_id
        self.config = params
        self.completed = False
        self.defeat = False
        self.__init_field()
        self.__create_mines()
        self.__init_relations()

    def __init_field(self):
        self.__field = [
            [
                Cell(i, j, self.config.height - 1, self.config.width - 1)
                for j in range(self.config.width)
            ]
            for i in range(self.config.height)
        ]

    def __create_mines(self):
        count = self.config.mines_count
        while count != 0:
            col = random.randint(0, self.config.width - 1)
            row = random.randint(0, self.config.height - 1)
            cell = self.__get_cell(row, col)
            if not cell.is_bomb():
                cell.mark_as_bomb()
            count -= 1

    def __init_relations(self):
        bombs = (
            cell for cell in self.__get_all_cells_generator() if cell.is_bomb()
        )
        neighbors = (
            neighbor
            for bomb in bombs
            for neighbor in bomb.get_neighbors()
            if neighbor
        )
        for neighbor in neighbors:
            cell = self.__get_cell(*neighbor)
            if not cell.is_bomb():
                cell.increment_amount()

    def create_new_turn(self, row: int, col: int):
        if self.completed:
            return
        cell = self.__get_cell(row, col)
        cell.mark_as_pushed()
        if cell.is_bomb():
            self.defeat = True
            return
        self.__check_if_save_cells_around(cell)
        if self.__is_complete():
            self.completed = True
            return

    def __is_complete(self):
        count = 0
        for cell in self.__get_all_cells_generator():
            if cell.is_pushed():
                count += 1
        return (
            count + self.config.mines_count
            == self.config.height * self.config.width
        )

    def __check_if_save_cells_around(self, cell: "Cell"):
        for neighbor in cell.get_neighbors():
            if neighbor:
                cell_neighbor = self.__get_cell(*neighbor)
                if cell_neighbor.amount == 0 and not cell_neighbor.is_pushed():
                    cell_neighbor.mark_as_pushed()
                    self.__check_if_save_cells_around(cell_neighbor)
                else:
                    cell_neighbor.mark_as_pushed()

    def get_game_info_response(self) -> GameInfoResponse:
        values = [
            self.__visualize_cell(cell)
            for cell in self.__get_all_cells_generator()
        ]
        fields = []
        start_slice = 0
        for _ in range(self.config.height):
            fields.append(values[start_slice : self.config.width + start_slice])
            start_slice += self.config.width
        return GameInfoResponse(
            game_id=self.game_id,
            width=self.config.width,
            height=self.config.height,
            mines_count=self.config.mines_count,
            completed=self.completed,
            field=fields,
        )

    def __visualize_cell(self, cell) -> str:
        match cell.amount:
            case 9:
                if self.completed:
                    return "M"
                if self.defeat:
                    return "X"
                return " "
            case _:
                if self.completed or self.defeat or cell.is_pushed():
                    return str(cell.amount)
                return " "

    def __get_all_cells_generator(self) -> Generator:
        for row in self.__field:
            for cell in row:
                yield cell

    def __get_cell(self, row: int, col: int) -> "Cell":
        return self.__field[row][col]


class Cell:
    def __init__(self, row: int, col: int, row_max: int, col_max: int):
        self.amount = 0
        self.pushed = False
        self.up_cell_position: tuple | None = (
            (row - 1, col) if row != 0 else None
        )
        self.down_cell_position: tuple | None = (
            (row + 1, col) if row != row_max else None
        )
        self.left_cell_position: tuple | None = (
            (row, col - 1) if col != 0 else None
        )
        self.right_cell_position: tuple | None = (
            (row, col + 1) if col != col_max else None
        )

    def get_neighbors(self) -> tuple:
        return (
            self.up_cell_position,
            self.down_cell_position,
            self.left_cell_position,
            self.right_cell_position,
        )

    def mark_as_bomb(self):
        self.amount = 9

    def is_bomb(self) -> bool:
        return self.amount == 9

    def mark_as_pushed(self):
        self.pushed = True

    def is_pushed(self):
        return self.pushed

    def increment_amount(self):
        self.amount += 1

    def __repr__(self):
        return f"{self.amount}"
