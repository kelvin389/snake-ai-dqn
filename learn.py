import gymnasium as gym
import numpy as np
import math
import stable_baselines3 as sb3
from stable_baselines3 import PPO
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
import sys
import pygame
from stable_baselines3.common.env_checker import check_env

# pygame
FPS = 15

GRID_CELL_SIZE = 25
GRID_WIDTH = 10
GRID_HEIGHT = 10

SCREEN_WIDTH = GRID_WIDTH * GRID_CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_CELL_SIZE

# ai
REWARD_EAT = 50
REWARD_DIE = -100
REWARD_CLOSER = 1 
REWARD_FURTHER = -3
REWARD_TRUNCATION = -200
MAX_STEPS_SINCE_LAST_FOOD = GRID_WIDTH * GRID_HEIGHT # allow ai to at most traverse the entire screen

DIRECTION_UP = 0
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3

STEPS_TO_TRAIN = 1000000

class SnakeEnv(gym.Env):
    def __init__(self):
        self.action_space = gym.spaces.Discrete(4)
        '''
        spaces = {
            "grid": gym.spaces.Box(0, 3, shape=(GRID_WIDTH, GRID_HEIGHT), dtype=int),
            "direction": gym.spaces.Discrete(4)
        }
        self.observation_space = gym.spaces.Dict(spaces)
        '''
        self.observation_space = gym.spaces.Box(0,3, shape=(GRID_WIDTH * GRID_HEIGHT + 1,), dtype=int)
        self.reset()

        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.snake_head_x = math.floor(GRID_WIDTH / 2)
        self.snake_head_y = math.floor(GRID_HEIGHT / 2)
        self.snake_body = [(self.snake_head_x, self.snake_head_y)]
        self.snake_length = 1

        # initialize food to be in the same spot as the head
        # which forces it to spawn somewhere else (kinda jank)
        self.food_x = self.snake_head_x
        self.food_y = self.snake_head_y
        self.spawn_food()

        self.cur_direction = DIRECTION_RIGHT
    
        self.steps_since_last_food = 0

        return self.get_observation(), {}

    def step(self, action):
        done = False

        if action == DIRECTION_UP and (self.cur_direction == DIRECTION_LEFT or self.cur_direction == DIRECTION_RIGHT):
            self.cur_direction = DIRECTION_UP
        if action == DIRECTION_DOWN and (self.cur_direction == DIRECTION_LEFT or self.cur_direction == DIRECTION_RIGHT):
            self.cur_direction = DIRECTION_DOWN
        if action == DIRECTION_LEFT and (self.cur_direction == DIRECTION_UP or self.cur_direction == DIRECTION_DOWN):
            self.cur_direction = DIRECTION_LEFT
        if action == DIRECTION_RIGHT and (self.cur_direction == DIRECTION_UP or self.cur_direction == DIRECTION_DOWN):
            self.cur_direction = DIRECTION_RIGHT

        old_dist = distance_between_points((self.food_x, self.food_y), (self.snake_head_x, self.snake_head_y))

        if self.cur_direction == DIRECTION_UP:
            self.snake_head_y -= 1
        if self.cur_direction == DIRECTION_DOWN:
            self.snake_head_y += 1
        if self.cur_direction == DIRECTION_LEFT:
            self.snake_head_x -= 1
        if self.cur_direction == DIRECTION_RIGHT:
            self.snake_head_x += 1

        # collide with edge
        if self.snake_head_x < 0 or self.snake_head_x == GRID_WIDTH or self.snake_head_y < 0 or self.snake_head_y == GRID_HEIGHT: 
            reward = REWARD_DIE
            done = True
            return self.get_observation(), reward, done, False, {}

        new_dist = distance_between_points((self.food_x, self.food_y), (self.snake_head_x, self.snake_head_y))
        # reward = 1 when is snake moves closer to food,
        # reward = -1 when moving further
        reward = REWARD_CLOSER if (old_dist - new_dist) > 0 else REWARD_FURTHER

        self.snake_body.insert(0, (self.snake_head_x, self.snake_head_y))

        if len(self.snake_body) > self.snake_length:
            self.snake_body.pop()

        # collide with self
        if (self.snake_head_x, self.snake_head_y) in self.snake_body[1:]:
            reward = REWARD_DIE # reward is overwritten
            done = True

        # eat food
        if self.snake_head_x == self.food_x and self.snake_head_y == self.food_y:
            reward = REWARD_EAT # reward is overwritten
            self.snake_length += 1
            self.spawn_food()
            self.steps_since_last_food = 0
        else:
            self.steps_since_last_food += 1
        
        truncated = False
        if self.steps_since_last_food >= MAX_STEPS_SINCE_LAST_FOOD:
            truncated = True
            reward = REWARD_TRUNCATION

        return self.get_observation(), reward, done, truncated, {}

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

        # wipe screen
        self.screen.fill((0,0,0))

        # draw snake
        draw_pos = grid_to_screen(self.snake_body[0][0], self.snake_body[0][1])
        pygame.draw.rect(self.screen, (0, 124, 255), [draw_pos[0], draw_pos[1], GRID_CELL_SIZE, GRID_CELL_SIZE])

        for piece in self.snake_body[1:]:
            draw_pos = grid_to_screen(piece[0], piece[1])
            pygame.draw.rect(self.screen, (255, 255, 255), [draw_pos[0], draw_pos[1], GRID_CELL_SIZE, GRID_CELL_SIZE])

        # draw food
        draw_pos = grid_to_screen(self.food_x, self.food_y)
        pygame.draw.rect(self.screen, (255, 0, 0), [draw_pos[0], draw_pos[1], GRID_CELL_SIZE, GRID_CELL_SIZE])

        # update
        pygame.display.update()
        self.clock.tick(FPS)

    def get_observation(self):
        grid = np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=int)

        grid[self.snake_body[0][0], self.snake_body[0][1]] = 1
        for piece in self.snake_body[1:]:
            grid[piece[0], piece[1]] = 2

        grid[self.food_x, self.food_y] = 3

        obs = np.append(grid.flatten(), self.cur_direction)

        #return {"grid": grid, "direction": np.array([self.cur_direction])}
        return obs
    
    def spawn_food(self):
        while (self.food_x, self.food_y) in self.snake_body:
            self.food_x = self.np_random.integers(0, GRID_WIDTH - 1)
            self.food_y = self.np_random.integers(0, GRID_HEIGHT - 1)

def grid_to_screen(grid_x, grid_y):
    return (grid_x * GRID_CELL_SIZE, grid_y * GRID_CELL_SIZE)

def distance_between_points(pt1, pt2):
    return abs(pt1[0] - pt2[0]) + abs(pt1[1] - pt2[1])

def main():
    args = sys.argv[1:]

    if "train" in args or "learn" in args:
        train()
    elif "run" in args or "play" in args:
        play()
    else:
        train()
        play()

def train():
    env = SnakeEnv()
    check_env(env)
    env = DummyVecEnv([lambda: env])
    model = DQN("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=STEPS_TO_TRAIN)
    model.save("dqn_snake_model")

def play():
    model = DQN.load("dqn_snake_model")

    env = SnakeEnv()
    while True:
        done = False
        obs, info = env.reset()
        truncated = False

        while not done and not truncated:
            action, states = model.predict(obs)
            obs, reward, done, truncated, _ = env.step(action)
            env.render()
            print(f"reward: {reward}")


if __name__ == "__main__":
    main()