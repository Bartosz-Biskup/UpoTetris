from enum import nonmember

Color = tuple[int, int, int]


class TetrisGrid:
    def __init__(self, size: tuple[int, int]) -> None:
        self.size_x: int = size[0]
        self.size_y: int = size[1]
        self._grid: list[list[Color | None]] = [[None for _ in range(self.size_x)] for _ in range(self.size_y)]

    def valid_cell(self, point: tuple[int, int]) -> bool:
        x, y = point
        return 0 <= x < self.size_x and 0 <= y < self.size_y

    def set_cell(self, cell: tuple[int, int], value: Color | None) -> None:
        if not self.valid_cell(cell):
            raise ValueError('Invalid Cell')

        self._grid[cell[1]][cell[0]] = value

    def get_cell(self, cell: tuple[int, int]) -> Color | None:
        if not self.valid_cell(cell):
            raise ValueError('Invalid Cell')

        return self._grid[cell[1]][cell[0]]

    def clear_row(self, row: int) -> None:
        self._grid.pop(row)
        self._grid.insert(0, [None for _ in range(self.size_x)])
