from mecode import G
from math import sqrt

import numpy as np
import matplotlib.pyplot as plt

g = G(
    print_lines=False,
    outfile=r"H:\User Files\Fitzgerald\SoftRobots\PressureChamber\gcode\helix.gcode",
    aerotech_include=True,
)

g.write("""
; Helix G Code
; Daniel Fitzgerald
; 06-20-2014
; helix conforming to the surface of a sphere to act as a pressure chamber with a large surface area.
""")

#starting position to offset helix in absolute cooridnates
#x_start = 100
#y_start = 100
#z_start = 10

#number of points to discretize the helix in to
N_points = 1000

r = 5 #radius

N_spirals = 36

factor=1

#theta = np.linspace(-np.pi/4, np.pi/4, N_points)
theta = np.linspace(-np.arctan(factor),np.arctan(factor), N_points)

#theta_original=np.linspace(0,np.pi, N_points)

#theta_discretized = (1+np.tan(theta))*(np.pi/2)
theta_discretized = (factor+np.tan(theta))*(np.pi/(2*factor))

phi = N_spirals*2*theta_discretized
x = r*np.sin(theta_discretized) * np.cos(phi)
y = r*np.sin(theta_discretized) * np.sin(phi)
z = -r*np.cos(theta_discretized)

pts = np.vstack((x, y, z))
pts = pts.T

#radius of the sphere which the helix will conform around
sphere_radius = 0.5

com_port=5

#height of each point
#heights = ((2*sphere_radius)*(i/N_points)) for i in range(N_points)

#radius in the XY plane to the perimeter of the sphere from the vertical line through its center
#radii = (x*(2*sphere_radius-x) for x in range(N_points)

g.write(
"""
G1 F1000 ; lower feedrate

; start pressure chamber (spherical Archimedes spiral)"""
)

#other dimensions
top_trace_length = 3
trace_print_speed = 800
connection_length =3

#feeds and speeds
matrix_travel_speed = 500
air_travel_speed = 1000
print_speed = 10

z_axis = "z"

#relative
g.feed(matrix_travel_speed) # safe immersion speed
g.move(-2*sphere_radius) # go to bottom of sphere
g.feed(print_speed) # set print speed
g.toggle_pressure(com_port) # start extrusion
relativePoints = pts[1:]-pts[:-1]
for relPoint in relativePoints:
    g.move(x=relPoint[0], y=relPoint[1],  **{z_axis:-relPoint[2]})
g.move(**{z_axis:top_trace_length})
g.feed(trace_print_speed)
g.move(**{z_axis:connection_length})
g.toggle_pressure(com_port)

#absolute
#g.absolute()
#for point in pts:
#    g.abs_move(x=point[0], y=point[1], Z=point[2])
    
#jog Z up
#g.feed(1000)
#g.relative()
g.move(z=(10))   # clear the print
#g.absolute() 
#g.write("G28 X0 ; home X axis")    
    
g.view()

g.teardown()