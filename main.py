import pygame
import random
import time
from queue import PriorityQueue

# Janela pygame
WIDTH = 1200
HEIGHT = 700


# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (150, 111, 214)


# Espaçamento
OFF_SET = 20


# Labirinto
class Maze:
    def __init__(self, rows, cols, cell_size):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.grid = []
        self.stack = []
        self.current = None

    # Inicializar as células do labirinto
    def initialize(self):
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                cell = Cell(r, c, self.grid)
                row.append(cell)
            self.grid.append(row)

        self.current = self.grid[0][0]
        # self.grid[0][0].walls["left"] = False
        # self.grid[-1][-1].walls["right"] = False

    # Método para desenhar os caminhos do labirinto
    def draw(self, screen):
        self.current.visited = True
        self.stack.append(self.current)

        while self.stack:
            # pygame.display.flip()

            self.current.show(self.cell_size, screen)

            next_neighbor = self.current.check_neighbors()

            if next_neighbor:
                next_neighbor.visited = True

                self.current.remove_walls(self.current, next_neighbor)
                self.current = next_neighbor
                self.stack.append(self.current)
                # self.current.highlight(self.cell_size, screen)
            elif len(self.stack) > 0:
                cell = self.stack.pop()
                self.current = cell
                # self.current.highlight(self.cell_size, screen)

        pygame.display.flip()

    def remove_random_wall(self, screen):
        quantity = (self.rows * self.cols) // 5

        for i in range(quantity):
            random_cell = random.choice(random.choice(self.grid))
            walls = {}
            for wall in random_cell.walls:
                if wall == "top" and random_cell.row == 0:
                    continue
                if wall == "right" and random_cell.col == self.cols - 1:
                    continue
                if wall == "bottom" and random_cell.row == self.rows - 1:
                    continue
                if wall == "left" and random_cell.col == 0:
                    continue
                walls[wall] = wall
            if len(walls) >= 2:
                wall_to_remove = random.choice(list(walls.keys()))
                random_cell.walls[wall_to_remove] = False
                random_cell.show(self.cell_size, screen)
        pygame.display.flip()


######################################################################################################


class Cell:
    def __init__(self, row, col, parent_grid):
        self.row = row
        self.col = col
        self.parent_grid = parent_grid
        self.visited = False
        self.walls = {
            "top": True,
            "right": True,
            "bottom": True,
            "left": True
        }

    # def __lt__(self, other):
    #     if self.col == other.col:
    #         return self.row < other.row
    #     return self.col < other.col
    def __lt__(self, other):
        if self.row == other.row:
            return self.col < other.col
        return self.row < other.row

    def __str__(self):
        return f"[{self.col}, {self.row}]"

    # Método para checar se a célula atual possui vizinhos válidos
    def check_neighbors(self):
        grid = self.parent_grid
        x = self.col
        y = self.row
        neighbors = []

        # Checar se a célula atual não está nos cantos e/ou bordas do labirinto
        top = grid[y - 1][x] if y != 0 else False
        right = grid[y][x + 1] if x < (len(grid[0]) - 1) else False
        bottom = grid[y + 1][x] if y < (len(grid) - 1) else False
        left = grid[y][x - 1] if x != 0 else False

        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)

        if neighbors:
            random_neighbor = random.choice(neighbors)
            return random_neighbor
        else:
            return

    # Remover paredes entre as células que formam o caminho
    def remove_walls(self, current_cell, next_cell):
        x = current_cell.col - next_cell.col

        if x == 1:
            current_cell.walls["left"] = False
            next_cell.walls["right"] = False
        elif x == -1:
            current_cell.walls["right"] = False
            next_cell.walls["left"] = False

        y = current_cell.row - next_cell.row

        if y == 1:
            current_cell.walls["top"] = False
            next_cell.walls["bottom"] = False
        elif y == -1:
            current_cell.walls["bottom"] = False
            next_cell.walls["top"] = False

    # Método para cada célula se desenhar
    def show(self, cell_size, screen):
        x = self.col * cell_size + OFF_SET
        y = self.row * cell_size + OFF_SET

        if self.walls["top"]:
            pygame.draw.line(screen, WHITE, [x, y], [x + cell_size, y])  # topo da célula
        else:
            pygame.draw.line(screen, BLACK, [x, y], [x + cell_size, y])
        if self.walls["right"]:
            pygame.draw.line(screen, WHITE, [x + cell_size, y],
                             [x + cell_size, y + cell_size])  # direita da celula
        else:
            pygame.draw.line(screen, BLACK, [x + cell_size, y + 1],
                             [x + cell_size, y + cell_size - 1])
        if self.walls["bottom"]:
            pygame.draw.line(screen, WHITE, [x + cell_size, y + cell_size],
                             [x, y + cell_size])  # inferior da célula
        else:
            pygame.draw.line(screen, BLACK, [x + cell_size, y + cell_size],
                             [x, y + cell_size])
        if self.walls["left"]:
            pygame.draw.line(screen, WHITE, [x, y + cell_size], [x, y])  # esquerda da celula
        else:
            pygame.draw.line(screen, BLACK, [x, y + cell_size - 1], [x, y + 1])
        # if self.visited:
        #     pygame.draw.rect(screen, BLACK, (x + 1, y + 1, cell_size - 1, cell_size - 1))

    # Método para destacar a célula atual com outra cor
    def highlight(self, cell_size, screen):
        x = self.col * cell_size + OFF_SET
        y = self.row * cell_size + OFF_SET

        pygame.draw.rect(screen, GREEN, (x + 1, y + 1, cell_size, cell_size))

######################################################################################################


class Agent:
    def __init__(self, maze):
        self.maze = maze

    def dfs(self):
        maze = self.maze
        start_cell = maze.grid[0][0]
        end_cell = maze.grid[-1][-1]
        stack = [start_cell]
        visited = [start_cell]
        dfs_path = {}

        while stack:
            current_cell = stack.pop()
            r = current_cell.row
            c = current_cell.col

            if current_cell == end_cell:
                break

            for direction in ["top", "left", "bottom", "right"]:
                next_cell = None
                if not maze.grid[r][c].walls[direction]:
                    if direction == "top":
                        next_cell = maze.grid[r - 1][c]
                    elif direction == "left":
                        next_cell = maze.grid[r][c - 1]
                    elif direction == "bottom":
                        next_cell = maze.grid[r + 1][c]
                    elif direction == "right":
                        next_cell = maze.grid[r][c + 1]
                    if next_cell in visited:
                        continue
                    visited.append(next_cell)
                    stack.append(next_cell)
                    dfs_path[next_cell] = current_cell

        path = {}
        while end_cell != start_cell:
            path[dfs_path[end_cell]] = end_cell
            end_cell = dfs_path[end_cell]

        print('Algoritmo Busca em Profundidade (verde): ')
        # print('Passos totais: ', len(dfs_path))
        print('Passos: ', len(path))
        print()

        return path

    def h(self, cell1, cell2):
        x1, y1 = cell1.col, cell1.row
        x2, y2 = cell2.col, cell2.row

        return max(abs(x1 - x2), abs(y1 - y2))

    def a_star(self):
        maze = self.maze
        start_cell = maze.grid[0][0]
        end_cell = maze.grid[-1][-1]
        g = {cell: float('inf') for row in maze.grid for cell in row}
        g[start_cell] = 0
        f = {cell: float('inf') for row in maze.grid for cell in row}
        f[start_cell] = self.h(start_cell, end_cell) + g[start_cell]

        open_queue = PriorityQueue()
        open_queue.put((f[start_cell], self.h(start_cell, end_cell), start_cell))
        a_star_path = {}

        while not open_queue.empty():
            current_cell = open_queue.get()[2]
            r = current_cell.row
            c = current_cell.col

            if current_cell == end_cell:
                break

            for direction in ["top", "left", "bottom", "right"]:
                next_cell = None
                if not maze.grid[r][c].walls[direction]:
                    if direction == "top":
                        next_cell = maze.grid[r - 1][c]
                    if direction == "left":
                        next_cell = maze.grid[r][c - 1]
                    if direction == "bottom":
                        next_cell = maze.grid[r + 1][c]
                    if direction == "right":
                        next_cell = maze.grid[r][c + 1]

                    temp_g = g[current_cell] + 1
                    temp_f = temp_g + self.h(next_cell, end_cell)

                    if temp_f < f[next_cell]:
                        g[next_cell] = temp_g
                        f[next_cell] = temp_f
                        # f[next_cell] = temp_g + self.h(next_cell, end_cell)
                        open_queue.put((temp_f, self.h(next_cell, end_cell), next_cell))
                        a_star_path[next_cell] = current_cell


        path = {}
        while end_cell != start_cell:
            path[a_star_path[end_cell]] = end_cell
            end_cell = a_star_path[end_cell]
        print('Algoritmo A* (roxo): ')
        # print('Passos totais: ', len(a_star_path))
        print('Passos: ', len(path))

        return path

    def print_path(self, path, screen, color):
        cell_size = self.maze.cell_size
        for cell in path:
            x = path[cell].col * cell_size + OFF_SET
            y = path[cell].row * cell_size + OFF_SET

            pygame.draw.rect(screen, color, (cell.col * cell_size + OFF_SET + 1,
                               cell.row * cell_size + OFF_SET + 1, cell_size - 1, cell_size - 1))
            pygame.draw.rect(screen, color, (x + 1, y + 1, cell_size - 1, cell_size - 1))
            time.sleep(0.01)
            pygame.display.flip()

######################################################################################################


while True:
    try:
        # Entrada de dados do usuário para definir o tamanho
        ROWS = int(input("Digite o número de linhas: "))
        COLS = int(input("Digite o número de colunas: "))
        break
    except ValueError:
        print("Valor inválido. Insira um número inteiro")


# Fórmula para adicionar espçamento entre o grid e a janela do pygame
CELL_SIZE = min((WIDTH - 2 * OFF_SET) // COLS, (HEIGHT - 2 * OFF_SET) // ROWS)


# Iniciar o pygame
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Labirinto Python")


new_maze = Maze(ROWS, COLS, CELL_SIZE)
new_maze.initialize()
new_maze.draw(SCREEN)
new_maze.remove_random_wall(SCREEN)
time.sleep(2)
a = Agent(new_maze)
a.print_path(a.dfs(), SCREEN, (76, 90, 40))
time.sleep(2)
a.print_path(a.a_star(), SCREEN, PURPLE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False


pygame.quit()

