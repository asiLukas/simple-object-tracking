# Real-Time Object Tracking Simulation

### Objective:

Develop a Python script that simulates real-time object tracking using input from a simulated video feed, __luxonis_task_video.mp4__. 

The task will involve processing a series of images (frames) to identify and track the movement of circles and rectangles of various colors across
these frames.
The output will include the coordinates of the object in each frame and a simple visualization showing the tracked path of the object over time.

### Usage
Create a virtual environment(ideally with python 3.11) and download requirements.
`pip -r install requirements`

To run the app (which includes starting the object detector) run `python main.py`
This will start the object detector, you can press `ESC` key on your keyboard at any point to skip ahead to the output visualization (by doing so, the visualization will end in the same frame as you pressed `ESC`)

While in visualization mode, you can also press the `ESC` key to manually exit the program. The end result will be saved to `out.mp4`.

### Inconsistencies
1. When two objects collide, the bigger one "eats" the smaller one and only one object is displayed for the following frames that they collide. This also causes the width and height to fluctuate, which is hotfixed by only displaying the initial size of each object.
2. When objects collide with a wall, the code to determine the correct color of the object fails, which results in unwanted creation of new objects. This is hotfixed by removing objects that lasted less than 5 frames.
3. Coordinates for circles are little off compared to the original.

There are NOTEs for those issues throughout the `main.py` file.
