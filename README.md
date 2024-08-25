# Interview Task: Real-Time Object Tracking Simulation

- The script is developed based on the "task_description.md" file
- See the guide.png file for detailed description of the UI

- Note: This code was developed using the python 3.10.4, please use 3.10.x (ideally the 3.10.4) version or try to install requirements for windows, where specific version of PyQt5 is not defined, otherwise the pip will throw version error. If this wasn't interview task, I would dockerize the app and ship it as runnable container.

### How to run the app:
    - (Optional) Create new virtual environment:
        python3 -m venv name_of_your_venv

    - (Optional) Activate the venv
        On macOS:
            . name_of_your_venv/bin/activate
        Linux:
            source name_of_your_venv/bin/activate
        Windows (cmd):
            name_of_your_venv\Scripts\activate.bat
        Windows (powershell):
            name_of_your_venv\Scripts\Activate.ps1

    - Install requirements: (see the Note above the "how to run" part)
        pip3 install -r requirements.txt            (Linux/macOS)
        pip3 install -r requirements_windows.txt    (Windows)
        
    - Run the script:
        python3 main.py

    (for the following steps see the guide.png file)
    - Select desired file (__./task_video.mp4__)
    - Start the detection algorithm


### Code documentation (how to use the individual parts):

    - Object detector class (detector.py):
        - very simple class with 2 methods for detecting shapes, code is self-explanatory
        - pre-processing and detection functions parameters are suited directly for the file specified in the task description, however the app allows to load other videos - in the case of loading different source, consider changing the parameters based on the video you are loading (app is created for interview, not general video detection)

    - Tracker class (tracker.py):
        - class handling the tracking and drawing logic of the script
        - tracker start with empty shape tracking list
        - use the new_frame() method for each new frame, with possible new (or duplicate) detections -> returns all the tracked shapes up until current frame (included)

    - other:
        main.py:
            - app entry point
        gui.py: 
            - responsible for the whole app user interface (main thread)
        shape_info_ui.py:
            - handles the elements in the detected shape list and the shape history window
        video_processor.py:
            - engine for processing the video
            - started from the main thread (gui) as separate thread
            - manages both detector and tracker objects
        shape.py: 
            - definition of the Shape object, and ShapeType type
        utils.py:
            - small function toolbox
        

### task description notes:

    "The visualization tool should be simple and easy to understand, allowing easy recognition of whether all objects were correctly tracked."
        - For this purpose I have created simple GUI

    "Any detection or tracking mistakes should be easily identifiable."
        - In the shape tracking output, there can be seen 4 lines that are discontinuous because of overlaping of the shapes / shape went out of the frame bounds

