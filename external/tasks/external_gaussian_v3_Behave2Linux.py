# region -- Adding Thalamus folder to allow the use of Thalamus modules
import sys
import os

# Expand the '~' to the home directory
specific_folder = os.path.expanduser("~/Thalamus") # path on Linux behave2

# Add the specific folder to the Python path
if specific_folder not in sys.path:
    sys.path.insert(0, specific_folder)
# endregion 

# region -- Importing packages
import os
import time
import json
import queue
import typing
import random
# import asyncio
import threading
# import multiprocessing
from pprint import pprint

import grpc
import numpy as np

from thalamus import task_controller_pb2
from thalamus import task_controller_pb2_grpc
from thalamus import thalamus_pb2
from thalamus import thalamus_pb2_grpc

from psychopy import visual, core, monitors

from thalamus.thread import ThalamusThread
from thalamus.oculomatic_tool import OculomaticTool
# endregion

def get_value(config: dict, key: str, default: typing.Any = None) -> typing.Union[int, float, bool]:
   """
   Reads a number from the config for the parameters defindes as [min]...[max] and randomly choses 
   a single value from the defined interval
   """

   if default is None:
      default = {}
   value_config = config.get(key, default)

   # if key == 'shape':
   #    return value_config

   # if isinstance(value_config, (int, float, bool)):
   #    self.trial_summary_data.used_values[key] = value_config
   #    return value_config

   if ('min' in value_config or 'min' in default) and ('max' in value_config or 'max' in default):
      lower = value_config['min'] if 'min' in value_config else default['min']
      upper = value_config['max'] if 'max' in value_config else default['max']
      sampled_value = random.uniform(lower, upper)
      # trial_summary_data.used_values[key] = sampled_value
      return sampled_value

   raise RuntimeError(f'Expected number or object with min and max fields, got {key}={value_config}')

# remove??
# class Oculomatic(typing.NamedTuple):
#    x: float
#    y: float
#    diameter: float

def main():
  clock = core.Clock() # Create a clock object; > precise than core.wait(2.3) (accurate to ~1ms)
  # region -- Defining the monitor and windows
  # edit!!
  my_monitor = monitors.Monitor('DellLaptopMonitor') # Create a Monitor object
  my_monitor.setSizePix((3840, 2160))  # # Set the screen resolution
  my_monitor.setWidth(38.189)  # # Set the screen width in centimeters
  my_monitor.setDistance(57)  # Set the distance from the user to the screen in centimeters
  FRAMERATE = 60
  INTERVAL = 1/FRAMERATE
  subject_win = visual.Window( # Create a window using the Monitor object
    size=(1024, 768),
    monitor=my_monitor,
    units='deg',  # Use degrees of visual angle
    color='black'
  )#, units='pix', fullscr=False, screen=2) 
  operator_win = visual.Window( # Create a window using the Monitor object
    pos=(0, 0),
    size=(1024//2, 768//2),
    monitor=my_monitor,
    units='deg',  # Use degrees of visual angle
    color='black'
  )#, units='pix', fullscr=False, screen=2) 
  # endregion

  vertices = [ # Define the vertices for the fixation cross
      (-0.25, 0), (0.25, 0),  # Horizontal line
      (0, 0), (0, -0.25), (0, 0.25)  # Vertical line
  ]
  # Define the fixation cross
  fixation_cross = visual.ShapeStim(
    win=subject_win,
    closeShape=False,
    vertices=vertices,
    units='deg',
    lineWidth=3,
    lineColor='red'
  )
  # region -- Create a white rectangle for photodiode in top left corner
  ''
  # Calculate the position of the top-left corner in degrees.
  # Assuming the center of the window is (0, 0) in degrees.
  # The top-left corner will be at (-half_width, half_height).
  # Get monitor details
  screen_width_cm = my_monitor.getWidth()  # Monitor width in cm
  screen_width_px = my_monitor.getSizePix()[0]  # Monitor width in pixels
  view_distance_cm = my_monitor.getDistance()  # Distance to monitor in cm
  # Manually calculate degrees per pixel using the formula
  cm_per_pixel = screen_width_cm / screen_width_px
  deg_per_px = 2 * np.arctan(cm_per_pixel / (2 * view_distance_cm)) * (180 / np.pi)
  # Convert the window size from pixels to degrees
  win_size_deg = (subject_win.size[0] * deg_per_px, subject_win.size[1] * deg_per_px)
  # Define the size of the square in degrees (e.g. 0.5° x 0.5°)
  square_size = 0.5
  # Define the top-left corner position in degrees relative to the window center
  # (0, 0) is the center of the window in degrees
  top_left_position = (-win_size_deg[0] / 2 + square_size / 2, win_size_deg[1] / 2 - square_size / 2)
  # Defining a rectangle
  rectangle = visual.Rect(
    win=subject_win,
    width=square_size,
    height=square_size,
    fillColor='white',
    lineColor='white',
    pos=top_left_position  # Position in deg
  )
  ''
  # endregion

  # region -- Drawing a polar coordinates for defining the spatial grid for visual stimuli
  max_size = min(win_size_deg)  # The maximum diameter that fits in the window
  # Calculate the step size
  num_circles = 10
  step_size = max_size / num_circles
  circles = [] # List to store the circles
  for i in range(1, num_circles + 1, 2):  # Create circles #1, #3, #5, #7, and #9
      circle_diameter = i * step_size
      circle = visual.Circle(
          win=subject_win,
          radius=circle_diameter / 2,  # Radius is half of the diameter
          edges=128,  # Number of edges to make the circle smooth
          lineColor='white',
          fillColor=None  # No fill color, only the outline
      )
      circles.append(circle)
  outermost_radius = 10 * step_size / 2 # Calculate the radius of the 10th circle
  lines = [] # List to store the lines
  for angle in np.arange(0, 360, 30): # Generate 12 lines, each 30 degrees apart
      radians = np.deg2rad(angle)
      x_end = outermost_radius * np.cos(radians)
      y_end = outermost_radius * np.sin(radians)
      line = visual.Line(
          win=subject_win,
          start=(0, 0),
          end=(x_end, y_end),
          lineColor='white'
      )
      lines.append(line)

  intersection_points = [] # Calculate the intersection points for position grid
  for circle in circles:
      radius = circle.radius
      for angle in np.arange(0, 360, 30):
          radians = np.deg2rad(angle)
          x = radius * np.cos(radians)
          y = radius * np.sin(radians)
          intersection_points.append((x, y))
  intersection_points = np.array(intersection_points) # Convert the list to a numpy array
  # Example: Randomly pool a subset of the coordinates without repeating
  subset_size = int(intersection_points.size/2) # size/2 = total number of coordinate pairs
  rand_pos = intersection_points[np.random.choice(intersection_points.shape[0], subset_size, replace=False)]
  i = 1 # index for position iteration

  # # Check for repeated values
  # unique_elements, counts = np.unique(rand_pos, axis=0, return_counts=True)
  # repeated_values = unique_elements[counts > 1]

  # if repeated_values.size > 0:
  #     print("Repeated values found:")
  #     print(repeated_values)
  # else:
  #     print("No repeated values found.")
  # endregion

  gaussian_circle = visual.GratingStim( # Create a Gaussian blurred circle stimulus
      win=subject_win,
      size=(1, 1),  # Size of the circle
      pos=rand_pos[i], # If units for Visual.Window are not defined, pos is in fraction of the screen
      sf=0,  # Spatial frequency of the grating (0 means no grating)
      mask='gauss',  # Gaussian mask
      color=(255, 255, 255),  # Color of the circle
      colorSpace='rgb255'
  )

  eye_pos = visual.ElementArrayStim(
    operator_win,
    # nElements=n_elements,            # Number of elements to display
    # xys=np.array([[0, 0]]),                   # Specify the (x, y) positions
    sizes=0.05,                     # Specify the sizes of each point
    # elementTex=None,                 # Use default texture (None)
    # elementMask='circle',            # Shape of the points (circle)
    colors=[[0, 1, 1]],                # Cyan in RGB (normalized)
    colorSpace='rgb',                # Color space ('rgb' or 'hsv')
    # opacities=None,                  # Opacity (None means fully opaque)
    # fields='xys',                    # Indicates that xys are given as coordinates
    units='norm'                     # Units ('norm', 'pix', etc.)
  )

  thalamus_thread = ThalamusThread('localhost:50050')
  thalamus_thread.start()

  oculomatic_tool = OculomaticTool(thalamus_thread)
  oculomatic_tool.start()
  lock = threading.Lock() 

  try:
    while True: # this loop executes only once for regular tasks; haven't counted yet for task clusters
      # region -- Setting up the gRPC communication
      ''
      task_controller_channel = grpc.insecure_channel('localhost:50051') # Connect to the task_controller server
      task_controller_stub = task_controller_pb2_grpc.TaskControllerStub(task_controller_channel)
  
      task_queue = queue.Queue()
      next_task_config = None
      execution_stream = None
      def execution_func():
        nonlocal next_task_config, execution_stream
        execution_stream = task_controller_stub.execution(iter(task_queue.get, None))
        for message in execution_stream:
          with lock:
            next_task_config = json.loads(message.body)
  
      execution_thread = threading.Thread(target=execution_func)
      execution_thread.start()
      ''
      # endregion

      while True:
        # region -- Reading the config file
        #wait for task config
        config = None
        while config is None:
          with lock:
            config = next_task_config
            next_task_config = None
          core.wait(.032)
        pprint(config)

        if i==1:
          catch_trials, catch_opacity, goal = config['catch_trials'], config['catch_opacity'], config['goal']

        width, height = config['width'], config['height']
        orientation, opacity = config['orientation'], config['opacity']
        is_height_locked = config['is_height_locked']
        target_color_rgb = config['target_color']
   
        blink_timeout = get_value(config,'blink_timeout')
        decision_timeout = get_value(config,'decision_timeout')
        fix1_timeout = get_value(config,'fix1_timeout')
        fix2_timeout = get_value(config,'fix2_timeout')
        if is_height_locked:
            height = width
        # endregion

        gaussian_circle.size = width, height
        gaussian_circle.pos = rand_pos[i]
        gaussian_circle.color = target_color_rgb
        gaussian_circle.ori = orientation
        gaussian_circle.opacity = opacity

        print('1. Fixate 1')
        for win in [subject_win, operator_win]:
          fixation_cross.draw(win)
          if win == operator_win:
            gaussian_circle.draw(win) # Draw the Gaussian circle
          win.flip() # Switch drawing buffer to the screen
        start = time.perf_counter()
        while time.perf_counter() - start < fix1_timeout:
          # assessing the Euclidean distance to the cross at (0,0)
          oculomatic = oculomatic_tool.value
          # my last point of work!!!
          eye_pos.xys = np.vstack((eye_pos.xys, np.array([[oculomatic.x, oculomatic.y]])))  # Combine old and new positions
          eye_pos.draw
          fixation_cross.draw
          win.flip()
          if (oculomatic.x**2  + oculomatic.y**2)**.5 < 2:
            print(time.perf_counter() - start, oculomatic, (oculomatic.x**2  + oculomatic.y**2)**.5)
          else:
            start = time.perf_counter()
          core.wait(INTERVAL)
  
        # core.wait(fix1_timeout)
        print('2. Target presentation')
        for win in [subject_win]:
          # for circle in circles:    # Draw spatial position grid circles
          #   circle.draw(win)
          # for line in lines: # Draw all the lines
          #   line.draw(win)
          fixation_cross.draw(win) # Draw the fixation cross
          gaussian_circle.draw(win) # Draw the Gaussian circle
          rectangle.draw(win) # draw the rectangle
          win.flip() # Switch drawing buffer to the screen
        core.wait(blink_timeout) # show target for 200ms
        
        print('3. Fixate 2')
        for win in [subject_win]:
          fixation_cross.draw(win)
          win.flip() # Switch drawing buffer to the screen
        start = time.perf_counter()
        while time.perf_counter() - start < fix2_timeout:
          # assessing the Euclidean distance to the cross at (0,0)
          oculomatic = oculomatic_tool.value
          if (oculomatic.x**2  + oculomatic.y**2)**.5 < 2:
            print(time.perf_counter() - start, oculomatic, (oculomatic.x**2  + oculomatic.y**2)**.5)
          else:
            start = time.perf_counter()
          core.wait(INTERVAL)
        
        print('4. Decision: cross disappears and gaze moves to target')
        for win in [subject_win]:
          win.flip() # Switch drawing buffer to the screen
        start_dec = time.perf_counter()
        while time.perf_counter() - start_dec < decision_timeout:
          oculomatic = oculomatic_tool.value
          print(time.perf_counter() - start_dec, oculomatic, ((oculomatic.x-rand_pos[i][0])**2  + (oculomatic.y-rand_pos[i][1])**2)**.5)
          if ((oculomatic.x-rand_pos[i][0])**2  + (oculomatic.y-rand_pos[i][1])**2)**.5 < 2:
            start = time.perf_counter()
            while time.perf_counter() - start < fix2_timeout:
              print('5. Hold the target')
              # assessing the Euclidean distance to the cross at (0,0) 
              oculomatic = oculomatic_tool.value
              if ((oculomatic.x-rand_pos[i][0])**2  + (oculomatic.y-rand_pos[i][1])**2)**.5 < 2:
                print(time.perf_counter() - start, oculomatic, ((oculomatic.x-rand_pos[i][0])**2  + (oculomatic.y-rand_pos[i][1])**2)**.5)
              else:
                start = time.perf_counter()
              core.wait(INTERVAL)
              if time.perf_counter() - start_dec > decision_timeout:
                # generate FAIL auditory que, penalty delay?? and restart the task!!
                break
            # generate SUCCESS auditory que, reward and restart the task!!
            break
          else:
            core.wait(INTERVAL)

        task_queue.put(task_controller_pb2.TaskResult(success=True))
        print(f"Trial # {i} ended.")

        i += 1
        core.wait(1) # remove later after adding appropriate inter-trial and penalty delays!!
  finally:
    print('finally')
    running = False
    thalamus_thread.stop()

if __name__ == '__main__':
  main()
