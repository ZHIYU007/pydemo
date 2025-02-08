import pygame
import random

# 初始化pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("俄罗斯方块")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

# 方块颜色定义
COLORS = [
    (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (0, 255, 255), (128, 0, 128)
]

# 旋转函数
def rotate_shape(shape):
    return list(map(list, zip(*shape[::-1])))

class Block:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = [shape]
        for _ in range(3):
            shape = rotate_shape(shape)
            self.shape.append(shape)
        self.color = random.choice(COLORS)
        self.rotation = 0

    def move_down(self):
        self.y += 1

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)

    def draw(self):
        for i in range(len(self.shape[self.rotation])):
            for j in range(len(self.shape[self.rotation][i])):
                if self.shape[self.rotation][i][j] == 1:
                    pygame.draw.rect(screen, self.color,
                                     (self.x + j * BLOCK_SIZE, self.y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, GRAY,
                                     (self.x + j * BLOCK_SIZE, self.y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)


def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(WIDTH // BLOCK_SIZE)] for _ in range(HEIGHT // BLOCK_SIZE)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


def valid_space(block, grid):
    accepted_positions = [[(j, i) for j in range(WIDTH // BLOCK_SIZE) if grid[i][j] == BLACK] for i in
                          range(HEIGHT // BLOCK_SIZE)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = []
    for i in range(len(block.shape[block.rotation])):
        for j in range(len(block.shape[block.rotation][i])):
            if block.shape[block.rotation][i][j] == 1:
                formatted.append((block.x // BLOCK_SIZE + j, block.y // BLOCK_SIZE + i))

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


def draw_grid(surface):
    sx = WIDTH // BLOCK_SIZE
    sy = HEIGHT // BLOCK_SIZE

    for i in range(sy):
        pygame.draw.line(surface, GRAY, (0, i * BLOCK_SIZE), (WIDTH, i * BLOCK_SIZE))
        for j in range(sx):
            pygame.draw.line(surface, GRAY, (j * BLOCK_SIZE, 0), (j * BLOCK_SIZE, HEIGHT))


def draw_window(surface, grid):
    surface.fill(BLACK)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    draw_grid(surface)
    pygame.draw.rect(surface, GRAY, (0, 0, WIDTH, HEIGHT), 5)
    pygame.display.update()


def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = Block(WIDTH // 2 - BLOCK_SIZE, 0, random.choice(SHAPES))
    clock = pygame.time.Clock()
    fall_time = 0
    # 正常下落速度
    normal_fall_speed = 0.05
    # 加速下落速度
    fast_fall_speed = 0.01
    fall_speed = normal_fall_speed

    # 左右移动的延迟和重复时间
    move_delay = 20
    move_interval = 50
    left_move_timer = 0
    right_move_timer = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            current_piece.move_down()
            fall_time = 0
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotate()
                        current_piece.rotate()
                        current_piece.rotate()
                if event.key == pygame.K_DOWN:
                    # 按下下键时，切换到加速下落速度
                    fall_speed = fast_fall_speed
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    # 松开下键时，恢复到正常下落速度
                    fall_speed = normal_fall_speed

        # 处理左右移动
        if keys[pygame.K_LEFT]:
            if left_move_timer == 0:
                current_piece.move_left()
                if not valid_space(current_piece, grid):
                    current_piece.move_right()
                left_move_timer = move_delay
            else:
                left_move_timer -= clock.get_rawtime()
                if left_move_timer <= 0:
                    current_piece.move_left()
                    if not valid_space(current_piece, grid):
                        current_piece.move_right()
                    left_move_timer = move_interval
        else:
            left_move_timer = 0

        if keys[pygame.K_RIGHT]:
            if right_move_timer == 0:
                current_piece.move_right()
                if not valid_space(current_piece, grid):
                    current_piece.move_left()
                right_move_timer = move_delay
            else:
                right_move_timer -= clock.get_rawtime()
                if right_move_timer <= 0:
                    current_piece.move_right()
                    if not valid_space(current_piece, grid):
                        current_piece.move_left()
                    right_move_timer = move_interval
        else:
            right_move_timer = 0

        shape_pos = []
        for i in range(len(current_piece.shape[current_piece.rotation])):
            for j in range(len(current_piece.shape[current_piece.rotation][i])):
                if current_piece.shape[current_piece.rotation][i][j] == 1:
                    shape_pos.append((current_piece.x // BLOCK_SIZE + j, current_piece.y // BLOCK_SIZE + i))

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = Block(WIDTH // 2 - BLOCK_SIZE, 0, random.choice(SHAPES))
            change_piece = False
            rows_cleared = clear_rows(grid, locked_positions)

        draw_window(screen, grid)

        if check_lost(locked_positions):
            run = False

    pygame.quit()


if __name__ == "__main__":
    main()