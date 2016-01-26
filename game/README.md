## Scripts
This folder contains two scripts:

1. [algo.py](algo.py) - partial NUI engine class and abstract classes used by it. You need to implement it!
2. [game.py](game.py) - very simple shooter arcade style game to be controlled by the NUI engine. You don't need to touch it. The **data** folder contains resources used by the game script.
3. [utils.py](utils.py) - some useful utility functions.

## Exercise
### 1. Find the face
* Use OpenCV to find a face in each frame - put it's resolution normalized coordinates (e.g. 320,192 in 640x480 is (0.5, 0.4)) into *NUIEngine.face_position*. 
* You will soon see that the face detector in some frames will miss the face (false-negative) and sometimes detect faces where the face is doesn't exist (false-positive). Try to find a way to deal with both problems by taking advantage of the fact that the actual face doesn't move much from one frame to the next (smoothness and locality).
### 2. Track the face
* Try to reduce face detection false-positives as much as possible even on the expense of extra false-negatives.
* When a face isn't detected in a frame, use the learned tracker to track the face from the previous frame.

 

