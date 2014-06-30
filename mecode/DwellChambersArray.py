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
; Blob Array G Code
; Daniel Fitzgerald
; 06-29-2014
; Array of blob-like pressure chambers made by extruding in place while submerged in matrix material.

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
$pressure=85

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
    outfile=r"H:\User Files\Fitzgerald\SoftRobots\PressureChamber\gcode\dwellChamberArray.pgm",
    aerotech_include=False,
)

g.write(start_script_string)

#specific to the mold
mold_z_zero = -45#-53.44#-78.85#-69
mold_depth = 12.5
mold_zero_offset = 3.0 #extra space on the bottom

#misc printer parameters
com_port = 9
z_axis = "A"

#other dimensions
stem_length = 5    # connection to needle insertion from CENTER of blob
pad_length = 3     # needle insertion pad (thicker stem)
travel_height = mold_z_zero+mold_depth + 5   # safe travel height (abs)
mold_top_clearence_height = mold_z_zero+mold_depth + 3

mold_top = mold_z_zero + mold_depth
needle_connector_end_height = mold_top - 1
needle_connector_start_height = needle_connector_end_height-pad_length

#feeds and speeds
pressure = 95 # (psi) line pressure to ink nozzle
matrix_travel_speed = 0.75 # (in mm/s) travel in matrix speed
stem_print_speed = 0.5 # (in mm/s) stem (needle insertion) print speed
air_travel_speed = 10 # (in mm/s) air travel
print_speed = 1 # (in mm/s)

g.write(
"""
; start pressure chamber (Blob from drelling and extruding in place)

;-----------------------------------------------------------------------
; Begin the script
;-----------------------------------------------------------------------


VELOCITY ON ; interpolate velocities instead of starting and stopping
"""
)

g.set_pressure(com_port, pressure)

#array parameters
n_rows = 4
n_cols = 4

#blob Parameters
dwell_times= range(10,10+10*n_rows*n_cols,10)
print str(len(dwell_times)) + " pressure chamber array"

#array parameters
spacing =  9 # mm between points on the array grid
length_per_row = n_rows * spacing
length_per_col = n_cols * spacing
center_height = mold_z_zero+0.5*mold_depth #mold_z_zero + mold_zero_offset+0.5*(mold_depth-stem_length-pad_length-mold_zero_offset)
print "Center height is " + str(center_height-mold_z_zero) + " above mold zero and " + str(mold_z_zero+mold_depth - center_height) + " from the top of the mold."

#state variables
going_foreward = 0 # start going back in Y
dwell_time_index = 0

for col in range(n_cols):             #loop through columns (right, posative in X)
#    print "Col: " + str(col)
    going_foreward = (not going_foreward)
    
    for row in range(n_rows): #loop through rows (down, negative in Y)
#        print "\tRow: " + str(row)
               
        #go to mold zero
        g.absolute();
        g.write("ABSOLUTE")
        g.feed(air_travel_speed)
        g.abs_move(**{z_axis:mold_top_clearence_height})
        g.feed(matrix_travel_speed) # safe immersion speed
        g.move(**{z_axis:(center_height)}) #height of centers of blobs
        g.relative();
#        g.write("Incremental")
        g.dwell(0.5) # wait for matrix to settle a little
            
        #make a blob by extruding and dwelling
        g.toggle_pressure(com_port) # start extrusion
        dwell_time_index = col*n_cols+row
#        print "\t\tindex: " + str(dwell_time_index)
        g.dwell(dwell_times[dwell_time_index]) # dwell in place to make the blob
            
        #top connector
#        g.move(**{z_axis:stem_length}) # print the connection to the stem
        g.abs_move(**{z_axis:needle_connector_start_height})
                       
        #needle insertion stem
        g.feed(stem_print_speed)
#        g.move(**{z_axis:pad_length})
        g.abs_move(**{z_axis:needle_connector_end_height}) 
                                   
        #stop extrusion
        g.toggle_pressure(com_port)
        g.dwell(1)
        
        #clear the surface of the mold (absolute) 
#        g.absolute()
        g.feed(matrix_travel_speed)
        g.abs_move(**{z_axis:mold_top_clearence_height})
               
        #get to travel height     
        g.feed(air_travel_speed)
        g.abs_move(**{z_axis:travel_height})
        g.relative()    
        
        #go foreward or backward to next row, unless we've reached the end of a row
        if (row <= n_rows-2):
            #move down to next col
            g.feed(air_travel_speed)
            dist_to_next_row = spacing*(1 if going_foreward else -1)
            g.move(y=dist_to_next_row)
                
    #move back up in Y and over in x for the next col  
    g.move(x=spacing, y=0)#length_per_row*(1 if going_foreward else -1)) #y=-n_rows*col_spacing
    
g.write(end_script_string)    
    
g.view()

g.teardown()

    