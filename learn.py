import gymnasium as gym
import numpy as np
import math
import stable_baselines3 as sb3
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

GRID_CELL_SIZE = 10
GRID_WIDTH = 20
GRID_HEIGHT = 20

SCREEN_WIDTH = GRID_WIDTH * GRID_CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_CELL_SIZE

DIRECTION_UP = 0
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3

class SnakeEnv(gym.Env):
    def __init__(self):
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(0, GRID_WIDTH - 1, shape=(20,20), dtype=int)
        self.reset()

    def reset(self, seed=123):
        super().reset(seed=seed)
        self.snake_head_x = math.floor(GRID_WIDTH / 2)
        self.snake_head_y = math.floor(GRID_HEIGHT / 2)
        self.snake_body = [(self.snake_head_x, self.snake_head_y)]
        self.snake_length = 1

        self.food_x = np.random.randint(0, GRID_WIDTH - 1)
        self.food_y = np.random.randint(0, GRID_HEIGHT - 1)

        self.cur_direction = DIRECTION_RIGHT

        self.steps_since_last_food = 0

        return self.get_observation(), {}

    def step(self, action):
        if action == DIRECTION_UP and (self.cur_direction == DIRECTION_LEFT or self.cur_direction == DIRECTION_RIGHT):
            self.cur_direction = DIRECTION_UP
        if action == DIRECTION_DOWN and (self.cur_direction == DIRECTION_LEFT or self.cur_direction == DIRECTION_RIGHT):
            self.cur_direction = DIRECTION_DOWN
        if action == DIRECTION_LEFT and (self.cur_direction == DIRECTION_UP or self.cur_direction == DIRECTION_DOWN):
            self.cur_direction = DIRECTION_LEFT
        if action == DIRECTION_RIGHT and (self.cur_direction == DIRECTION_UP or self.cur_direction == DIRECTION_DOWN):
            self.cur_direction = DIRECTION_RIGHT


        if self.cur_direction == DIRECTION_UP:
            self.snake_head_y -= 1
        if self.cur_direction == DIRECTION_DOWN:
            self.snake_head_y += 1
        if self.cur_direction == DIRECTION_LEFT:
            self.snake_head_x -= 1
        if self.cur_direction == DIRECTION_RIGHT:
            self.snake_head_x += 1

        if self.snake_head_x < 0:
            self.snake_head_x = GRID_WIDTH - 1
        elif self.snake_head_x == GRID_WIDTH:
            self.snake_head_x = 0
        elif self.snake_head_y < 0:
            self.snake_head_y = GRID_HEIGHT - 1
        elif self.snake_head_y == GRID_HEIGHT:
            self.snake_head_y = 0

        self.snake_body.insert(0, (self.snake_head_x, self.snake_head_y))

        if len(self.snake_body) > self.snake_length:
            self.snake_body.pop()

        # collide with self
        if (self.snake_head_x, self.snake_head_y) in self.snake_body[1:]:
            done = True
        else:
            done = False

        # eat food
        if self.snake_head_x == self.food_x and self.snake_head_y == self.food_y:
            self.snake_length += 1
            self.food_x = np.random.randint(0, GRID_WIDTH - 1)
            self.food_y = np.random.randint(0, GRID_HEIGHT - 1)
            reward = 1
            self.steps_since_last_food = 0
        else:
            reward = 0
            self.steps_since_last_food += 1

        truncated = True if self.steps_since_last_food >= 50 else False

        return self.get_observation(), reward, done, truncated, {}

    def render(self):
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if (i, j) == self.snake_body[0]:
                    print("H", end="")
                elif (i, j) in self.snake_body[1:]:
                    print("O", end="")
                elif (i, j) == (self.food_x, self.food_y):
                    print("X", end="")
                else:
                    print(" ", end="")
            print("")

    def get_observation(self):
        grid = np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=int)

        grid[self.snake_body[0][0], self.snake_body[0][1]] = 1
        for piece in self.snake_body[1:]:
            grid[piece[0], piece[1]] = 2

        grid[self.food_x, self.food_y] = 3

        return grid

def grid_to_screen(grid_x, grid_y):
    return (grid_x * GRID_CELL_SIZE, grid_y * GRID_CELL_SIZE)

def main():
    train()
    model = PPO.load("ppo_snake_model")

    env = SnakeEnv()
    done = False
    obs, info = env.reset()

    while not done:
        action, states = model.predict(obs)
        obs, reward, done, truncated, _ = env.step(action)
        env.render()
        print(f"reward: {reward}")

def train():
    env = SnakeEnv()
    env = DummyVecEnv([lambda: env])
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=100000)
    model.save("ppo_snake_model")

if __name__ == "__main__":
    main()