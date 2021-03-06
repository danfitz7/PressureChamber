# -*- coding: utf-8 -*-
from mecode import G
from math import sqrt

import numpy as np
import matplotlib.pyplot as plt

g = G(
    print_lines=False,
    outfile=r"H:\User Files\Fitzgerald\SoftRobots\PressureChamber\gcode\helix.pgm",
    aerotech_include=False,
)

g.write("""
; Helix G Code
; Daniel Fitzgerald
; 06-20-2014
; helix conforming to the surface of a sphere to act as a pressure chamber with a large surface area.
  

DVAR $hFile        
DVAR $cCheck
DVAR $press
DVAR $length
DVAR $lame  

DVAR $COM
DVAR $pressure
DVAR $moveSpeed
DVAR $printSpeedXY
DVAR $printSpeedZ
DVAR $printHeight
DVAR $edgeLength
Primary
FILECLOSE

$COM=9
$pressure=90

; Below, we call several required GCode commands; these commands begin with a G:
G71            ; Standard GCode command for metric units
G76            ; Standard GCode command for time base seconds
G68            
G65 F3000        ; Sets an acceleration speed in mm/s^2
G66 F3000        ; Sets a deceleration speed in mm/s^2

; The “ENABLE” command allows us to enable axes on the printer; this is required for printing
ENABLE X Y A B C D U     ; enables all the axis 


Incremental                ; “Incremental” tells the printer to referring to relative coordinates

""")

#specific to the mold
mold_z_zero = -76
mold_zero_offset = 1.0


#misc. printing parameters
com_port = 9
z_axis = "A"
pressure = 90

#starting position to offset helix in absolute cooridnates
#x_start = 100
#y_start = 100
#z_start = 10

#spiral parameters
N_points = 1000 #number of points to discretize the helix in to
radius = 2.5
N_spirals = 36
factor=1 # discretization factor. Influences the effect of the arctan scaling of discretization.

#theta = np.linspace(-np.pi/4, np.pi/4, N_points)
theta = np.linspace(-np.arctan(factor),np.arctan(factor), N_points)

#theta_discretized = (1+np.tan(theta))*(np.pi/2)
theta_discretized = (factor+np.tan(theta))*(np.pi/(2*factor))

#spherical archemeded spiral
phi = N_spirals*2*theta_discretized
x = radius*np.sin(theta_discretized) * np.cos(phi)
y = radius*np.sin(theta_discretized) * np.sin(phi)
z = -radius*np.cos(theta_discretized)

pts = np.vstack((x, y, z))
pts = pts.T

#height of each point
#heights = ((2*sphere_radius)*(i/N_points)) for i in range(N_points)

#radius in the XY plane to the perimeter of the sphere from the vertical line through its center
#radii = (x*(2*sphere_radius-x) for x in range(N_points)

#other dimensions
stem_length = 1 # connection to needle insertion
pad_length = 2 # needle insertion
lift_height = 10

#feeds and speeds
matrix_travel_speed = 1 # (in mm/s) travel in matrix speed
stem_print_speed = 1 # (in mm/s) stem (needle insertion) print speed
air_travel_speed = 20 # (in mms) air travel
print_speed = 0.5 #in (mm/s) helix print speed

g.write(
"""
; start pressure chamber (spherical Archimedes spiral)

;-----------------------------------------------------------------------
; Begin the script
;-----------------------------------------------------------------------


VELOCITY ON ; interpolate velocities instead of starting and stopping
"""
)

g.set_pressure(com_port, pressure)

#go to mold zero
g.absolute();
g.write("ABSOLUTE")
g.feed(matrix_travel_speed) # safe immersion speed
g.move(**{z_axis:(mold_z_zero+mold_zero_offset)})
g.relative();
g.write("Incremental")

#relative coordinates

#g.move(**{z_axis:(-2*radius-stem_length-pad_length)}) # go to bottom of sphere

#start sphere
g.feed(print_speed) # set print speed
g.toggle_pressure(com_port) # start extrusion
relativePoints = pts[1:]-pts[:-1]
for relPoint in relativePoints:
    g.move(x=relPoint[0], y=relPoint[1],  **{z_axis:relPoint[2]})

#top connector
g.move(**{z_axis:stem_length}) # print the connection to the stem

#needle insertion stem
g.feed(stem_print_speed)
g.move(**{z_axis:pad_length})

#g.feed(matrix_travel_speed)
g.move(**{z_axis:lift_height})

#stop extrusion
g.toggle_pressure(com_port)

#absolute
#g.absolute()
#for point in pts:
#    g.abs_move(x=point[0], y=point[1], Z=point[2])
    
#jog Z up
#g.feed(1000)
#g.relative()
#g.move(z=(10))   # clear the print
#g.absolute() 
#g.write("G28 X0 ; home X axis")    
    
g.write(
"""
VELOCITY OFF

M2



;----------------------------------------------------------
; END OF CODE - Function definitions below
;----------------------------------------------------------
DFS setPress        
         
	$strtask1 = DBLTOSTR( $P, 0 )            
	$strtask1 = "COM" + $strtask1
	$hFile = FILEOPEN $strtask1, 2
	COMMINIT $hFile, "baud=115200 parity=N data=8 stop=1"
	COMMSETTIMEOUT $hFile, -1, -1, 1000
                             
	$press = $Q * 10.0                             
	$strtask2 = DBLTOSTR( $press , 0 )  
      
      
	$length = STRLEN( $strtask2 )      
	WHILE $length < 4.0
		$strtask2 = "0" + $strtask2    
		$length = STRLEN( $strtask2 ) 
	ENDWHILE

	$strtask2 = "08PS  " + $strtask2
                                    
	$cCheck = 0.00     
	$lame = STRTOASCII ($strtask2, 0)
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 1) 
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 2) 
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 3) 
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 4)
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 5) 
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 6) 
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 7) 
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 8) 
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 9)  
	$cCheck = $cCheck - $lame
                        
	WHILE( $cCheck) < 0
		$cCheck = $cCheck + 256
	ENDWHILE                        

	$strtask3 = makestring "{#H}" $cCheck   
	$strtask3 = STRUPR( $strtask3 )
	$strtask2 = "\x02" + $strtask2 + $strtask3 + "\x03"
            
	FILEWRITE $hFile "\x05"
	FILEWRITE $hFile $strtask2
	FILEWRITE $hFile "\x04"

	FILECLOSE $hFile

ENDDFS

DFS togglePress        
         
	$strtask1 = DBLTOSTR( $P, 0 )            
	$strtask1 = "COM" + $strtask1
	$hFile = FILEOPEN $strtask1, 2
	COMMINIT $hFile, "baud=115200 parity=N data=8 stop=1"
	COMMSETTIMEOUT $hFile, -1, -1, 1000

	$strtask2 = "04DI  "
                                    
	$cCheck = 0.00     
	$lame = STRTOASCII ($strtask2, 0)
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 1) 
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 2) 
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 3) 
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 4)
	$cCheck = $cCheck - $lame
	$lame = STRTOASCII( $strtask2, 5) 
	$cCheck = $cCheck - $lame
                        
	WHILE( $cCheck) < 0
		$cCheck = $cCheck + 256
	ENDWHILE                        

	$strtask3 = makestring "{#H}" $cCheck   
	$strtask3 = STRUPR( $strtask3 )
	$strtask2 = "\x02" + $strtask2 + $strtask3 + "\x03"
                  
	FILEWRITE $hFile "\x05"
	FILEWRITE $hFile $strtask2
	FILEWRITE $hFile "\x04"

	FILECLOSE $hFile

ENDDFS  
;----------------------------------------------------------
;----------------------------------------------------------
;----------------------------------------------------------
""")    
    
g.view()

g.teardown()