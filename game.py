import pygame
import random

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

GRID_CELL_SIZE = 10
GRID_WIDTH = 20
GRID_HEIGHT = 20

DIRECTION_UP = 0
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3


def main():
    snake_head_x = GRID_WIDTH / 2
    snake_head_y = GRID_HEIGHT / 2
    snake_body = [(snake_head_x, snake_head_y)]
    snake_length = 1

    food_x = random.randint(0, GRID_WIDTH)
    food_y = random.randint(0, GRID_HEIGHT)

    cur_direction = DIRECTION_RIGHT


    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                if event.key == pygame.K_UP:
                    cur_direction = DIRECTION_UP
                if event.key == pygame.K_DOWN:
                    cur_direction = DIRECTION_DOWN
                if event.key == pygame.K_LEFT:
                    cur_direction = DIRECTION_LEFT
                if event.key == pygame.K_RIGHT:
                    cur_direction = DIRECTION_RIGHT

        if cur_direction == DIRECTION_UP:
            snake_head_y -= 1
        if cur_direction == DIRECTION_DOWN:
            snake_head_y += 1
        if cur_direction == DIRECTION_LEFT:
            snake_head_x -= 1
        if cur_direction == DIRECTION_RIGHT:
            snake_head_x += 1

        snake_body.insert(0, (snake_head_x, snake_head_y))

        if len(snake_body) > snake_length:
            snake_body.pop()

        if snake_head_x < 0:
            snake_head_x = GRID_WIDTH
        if snake_head_x > GRID_WIDTH:
            snake_head_x = 0
        if snake_head_y < 0:
            snake_head_y = GRID_HEIGHT
        if snake_head_y > GRID_HEIGHT:
            snake_head_y = 0

        # eat food
        if snake_head_x == food_x and snake_head_y == food_y:
            snake_length += 1
            food_x = random.randint(0, GRID_WIDTH)
            food_y = random.randint(0, GRID_HEIGHT)

        # wipe screen
        screen.fill((0,0,0))

        # draw snake
        for piece in snake_body:
            draw_pos = grid_to_screen(piece[0], piece[1])
            pygame.draw.rect(screen, (255, 255, 255), [draw_pos[0], draw_pos[1], 10, 10])

        # draw food
        draw_pos = grid_to_screen(food_x, food_y)
        pygame.draw.rect(screen, (255, 0, 0), [draw_pos[0], draw_pos[1], 10, 10])

        # update
        pygame.display.update()
        clock.tick(5)

def grid_to_screen(grid_x, grid_y):
    return (grid_x * GRID_CELL_SIZE, grid_y * GRID_CELL_SIZE)

if __name__ == "__main__":
    main()