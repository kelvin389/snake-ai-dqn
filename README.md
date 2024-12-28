## Snake AI

This is an AI that learns to play [snake](<https://en.wikipedia.org/wiki/Snake_(video_game_genre)>) using the [DQN implementation available in stable-baselines3](https://stable-baselines3.readthedocs.io/en/master/modules/dqn.html). The model that is bundled inside the repository is trained using the rewards specified in learn.py with 1,000,000 steps (1 movement in the game is 1 step). This AI is not necessarily good at playing the game nor are neural networks required to create a better snake AI, this is just a project to learn the basics of AI.

## Usage

### Playing

`python game.py` to play the human playable version of the game

### Training AI

`python learn.py` to train and play

`python learn.py train` to train only

`python learn.py play` to play with the currently trained model (dqn_snake_model.zip)
