# -*- coding: utf-8 -*-
from mecode import G
from math import sqrt

import numpy as np
import matplotlib.pyplot as plt

end_script_string = """
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
"""

start_script_string = """
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

"""

g = G(
    print_lines=False,
    outfile=r"H:\User Files\Fitzgerald\SoftRobots\PressureChamber\gcode\helix.pgm",
    aerotech_include=False,
)

g.write(start_script_string)

#specific to the mold
mold_z_zero = -76
mold_zero_offset = 1.0

#misc printer parameters
com_port = 9
z_axis = "z"

#spiral parameters
n_points = 1000     #number of points to discretize the helix in to
start_radius = 0.5
n_spirals = 36
factor=1         # discretization factor. Influences the effect of the arctan scaling of discretization.

#other dimensions
stem_length = 1    # connection to needle insertion
pad_length = 2     # needle insertion
travel_height = mold_z_zero+10   # safe travel height (abs)

#feeds and speeds
pressure = 90             # (psi) line pressure to ink nozzle
matrix_travel_speed = 1   # (in mm/s) travel in matrix speed
stem_print_speed = 1      # (in mm/s) stem (needle insertion) print speed
air_travel_speed = 20     # (in mms) air travel
print_speed = 0.5         # (in mm/s) helix print speed

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

#array parameters
n_rows = 4
radius_decrease_per_row = 0.5

n_cols = 4
n_spirals_decrease_per_col = 10

spiral_sep_dist = 2 # separation between spiral edges
max_radius = start_radius+radius_decrease_per_row*(n_rows-1)
col_spacing = spiral_sep_dist + 2*(max_radius)
center_height = mold_z_zero+mold_zero_offset+max_radius

for col in range(n_cols):             #loop through columns (right, posative in X)
    n_spirals = n_spirals-n_spirals_decrease_per_col  #the number of spirals decreases across columns
    y_counter=0
    for row in range(n_rows): #loop through rows (down, negative in Y)
        radius=start_radius+radius_decrease_per_row*row    # decrease radius each row 

        #make the spiral
        theta = np.linspace(-np.arctan(factor),np.arctan(factor), n_points)
        theta_discretized = (factor+np.tan(theta))*(np.pi/(2*factor))
            
        #spherical archemeded spiral
        phi = n_spirals*2*theta_discretized
        x = radius*np.sin(theta_discretized) * np.cos(phi)
        y = radius*np.sin(theta_discretized) * np.sin(phi)
        z = -radius*np.cos(theta_discretized)
        
        #points array    
        pts = np.vstack((x, y, z))
        pts = pts.T
    
        #go to mold zero
        g.absolute();
        g.write("ABSOLUTE")
        g.feed(matrix_travel_speed) # safe immersion speed
        base_height=center_height-radius
        g.move(**{z_axis:(base_height)}) #safe height above bottom of mold
        g.relative();
        g.write("Incremental")
            
        #make a sphere helix
        g.feed(print_speed)         # set print speed
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
        g.absolute()
        g.abs_move(**{z_axis:travel_height})
        g.relative()    
            
        #stop extrusion
        g.toggle_pressure(com_port)
        
        #move down to next col
        dist_to_next_row = 2*radius+radius_decrease_per_row+spiral_sep_dist
        g.move(y=dist_to_next_row)
        y_counter=y_counter+dist_to_next_row
        
    #move back up in Y and over in x for the next col  
    g.move(x=col_spacing, y=-y_counter)
    
g.write(end_script_string)    
    
g.view()

g.teardown()

    