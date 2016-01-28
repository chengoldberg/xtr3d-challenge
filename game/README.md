## Structure
This folder contains 3 scripts:

1. [algo.py](algo.py) - partial NUI engine class and abstract classes used by it. You need to implement it!
2. [game.py](game.py) - very simple shooter arcade style game to be controlled by the NUI engine. You don't need to touch it. The **data** folder contains resources used by the game script.
3. [utils.py](utils.py) - some useful utility functions.

## Commandline Interface
Use these on either algo.py or game.py:
* **-playback-video** Full path to the video file/image sequence dir to playback
* **-record-video** Full path to the video file to record

For example to run with the included image sequence:

`game.py -playback-video ..\inputs\image_sequence_1`

## Exercise
The code in algo.py is partial. It only deals with reading input and setting face position and arm orientation for the game to use. Your exercise is to implement the actual algorithm. We seperate the task into 5 stages - each stage has an equivalent tutorial. Read the tutorial and implement the stage. **Good luck!**.

### 1. Find the face
* Use OpenCV to find a face in each frame - put it's resolution normalized coordinates (e.g. 320,192 in 640x480 is (0.5, 0.4)) into *NUIEngine.face_position*. 
* You will soon see that the face detector in some frames will miss the face (false-negative) and sometimes detect faces where the face is doesn't exist (false-positive). Try to find a way to deal with both problems by taking advantage of the fact that the actual face doesn't move much from one frame to the next (smoothness and locality).

### 2. Track the face
* Try to reduce face detection false-positives as much as possible even on the expense of extra false-negatives.
* When a face isn't detected in a frame, use the learned tracker to track the face from the previous frame.

### 3. Detect the skin color
* Learn a color model of the detected face in each frame.
* Use the learned color model in each frame to create a binary skin map for that frame where a pixel is 255 if it has skin it in.
 
### 4. Detect the arm blobs
* Use morphologies on the binary skin map to eliminate small non-skin blobs and merge larger skin blobs.
* Detect the two largest blobs on either side of the face and estimate its orientation. Place the detected orientation in: *NUIEngine.left_degrees* and *NUIEngine.right_degrees* (as degrees).

### 5. Background Subtraction
* Use the MOG background subtraction algorithm to seperate foreground pixels from background pixels.
* Intersect the background map with the skin map to improve recall (reduce false-positives).

## Goal
Your final implementation should work well and allow the player to enjoy playing the game and obtain a high score - that's the only test.
