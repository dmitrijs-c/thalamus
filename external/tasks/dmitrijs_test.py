# region -- Testing sound playback using PsychoPy
# import os

# from psychopy import visual, core, monitors, sound, prefs

# prefs.hardware['audioLib'] = 'PTB'  # Set PTB as the audio backend

# # Get the current working directory
# current_directory = os.getcwd()
# # Define a relative path (e.g., accessing a file in a subdirectory)
# relative_path = os.path.join(current_directory, 'thalamus\\task_controller', 'failure_clip.wav')

# # Load the .wav file (replace with your file path)
# my_sound = sound.Sound(relative_path)
# # my_sound = sound.Sound(r"C:\Thalamus\thalamus\task_controller\failure_clip.wav")

# # Play the sound
# my_sound.play()

# # Allow time for the sound to finish playing before the program exits
# core.wait(my_sound.getDuration())  # Wait for the sound's duration to finish

# trial_failed = []
# print(trial_failed != 1)

# endregion 


# region -- Measuring how large Gaussian targets can be drawn
# import numpy as np
# from psychopy import visual, core, monitors, sound, prefs

# my_monitor = monitors.Monitor('LG24GQ50B_behave2') # Create a Monitor object
# my_monitor.setSizePix((1920, 1080))  # # Set the screen resolution
# my_monitor.setWidth(52.83)  # # Set the screen width in centimeters
# my_monitor.setDistance(57)  # Set the distance from the user to the screen in centimeters
# FRAMERATE = 60
# INTERVAL = 1/FRAMERATE

# subject_win = visual.Window( # Create a window using the Monitor object
#     size=(1920, 1080),
#     monitor=my_monitor,
#     units='deg',  # Use degrees of visual angle
#     color='black'
#     )#, units='pix', fullscr=False, screen=2) 
# operator_win = visual.Window( # Create a window using the Monitor object
#     pos=(0, 0),
#     size=(1024//2, 768//2),
#     monitor=my_monitor,
#     units='deg',  # Use degrees of visual angle
#     color='black'
#     )#, units='pix', fullscr=False, screen=2) 
# # Get monitor details
# screen_width_cm = my_monitor.getWidth()  # Monitor width in cm
# screen_width_px = my_monitor.getSizePix()[0]  # Monitor width in pixels
# view_distance_cm = my_monitor.getDistance()  # Distance to monitor in cm
# # Manually calculate degrees per pixel using the formula
# cm_per_pixel = screen_width_cm / screen_width_px
# deg_per_px = 2 * np.arctan(cm_per_pixel / (2 * view_distance_cm)) * (180 / np.pi)
# # Convert the window size from pixels to degrees
# win_size_deg = (subject_win.size[0] * deg_per_px, subject_win.size[1] * deg_per_px)

# max_size = min(win_size_deg)  # The maximum diameter that fits in the window
# # Calculate the step size
# num_circles = 10
# step_size = max_size / num_circles
# print("biggest Gaussian width/height = ", step_size, " deg")
# circles = [] # List to store the circles
# for i in range(1, num_circles + 1, 2):  # Create circles #1, #3, #5, #7, and #9
#     circle_diameter = i * step_size
#     circle = visual.Circle(
#         win=subject_win,
#         radius=circle_diameter / 2,  # Radius is half of the diameter
#         edges=128,  # Number of edges to make the circle smooth
#         lineColor='white',
#         fillColor=None  # No fill color, only the outline
#     )
#     circles.append(circle)
# outermost_radius = 10 * step_size / 2 # Calculate the radius of the 10th circle
# lines = [] # List to store the lines
# for angle in np.arange(0, 360, 30): # Generate 12 lines, each 30 degrees apart
#     radians = np.deg2rad(angle)
#     x_end = outermost_radius * np.cos(radians)
#     y_end = outermost_radius * np.sin(radians)
#     line = visual.Line(
#         win=subject_win,
#         start=(0, 0),
#         end=(x_end, y_end),
#         lineColor='white'
#     )
#     lines.append(line)

# rand_pos = [] # Calculate the intersection points for position grid
# for circle in circles:
#     radius = circle.radius
#     for angle in np.arange(0, 360, 30):
#         radians = np.deg2rad(angle)
#         x = radius * np.cos(radians)
#         y = radius * np.sin(radians)
#         rand_pos.append((x, y))
# rand_pos = np.array(rand_pos) # Convert the list to a numpy array

# for win in [subject_win]:
#     for circle in circles:    # Draw spatial position grid circles
#       circle.draw(win)
#     for line in lines: # Draw all the lines
#       line.draw(win)
#     win.flip() # Switch drawing buffer to the screen
# core.wait(20000) # show target for 200ms
# endregion 

# region -- Measuring how large Gaussian targets can be drawn
from psychopy import visual, core
import numpy as np

# Create a window
win = visual.Window(size=(800, 800), units='pix', screen=1)

# Predefine maximum number of dots and their positions
max_dots = 10
positions = np.random.uniform(-400, 400, size=(max_dots, 2))

# Gradually increase the number of dots by recreating DotStim
for i in range(1, max_dots + 1):
    # Create a new DotStim with updated number of dots
    dots = visual.DotStim(
        win=win,
        nDots=i,  # Number of dots
        dotSize=5,
        fieldShape='circle',
        fieldSize=(800, 800),
        fieldPos=(0, 0),
        color='white',
        dotLife=5  # Optional: Control how long each dot lives
    )
    
    # Update positions for the current number of dots
    dots.fieldPos = (0, 0)  # Center the field (optional)
    dots.fieldShape = 'square'  # Optional: Use a square field
    dots.fieldSize = 800  # Field size (optional)

    # Draw and display
    dots.draw()
    win.flip()
    core.wait(0.5)

# Close the window
win.close()




# endregion


