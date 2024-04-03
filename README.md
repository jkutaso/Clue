Two years ago I played a game of clue with my friends and I lost which made me angry, so I decided to try to train a model to play it. Two years later I actually started making progress on it.

**Summary**

The GameCode files are what you need to actually play the game. There are a few classes there that help organize the code, but essentially it tries to perfectly recreate the way a game of clue would work.

The Players files have two hardcoded strategies for playing Clue and a third one which is intended to be my guinea pig for different models. 

The q_learning.py file is sort of a scratch script I used to run some basic experiments on how well the training actually goes. For now the only decision that has any kind of variability is the decision of whether or not to guess. In practice, this decision should be monotonic in the variables I'm using there, so the decision to use Q learning with discrete states was questionable. 
