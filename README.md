# Geometry-Generation-of-Overflow-and-Venting-Systems-in-Salome-for-Die-Casting-and-Thixomolding

The included scripts (one is for testing creating overflows) generate typical overflows and venting lines in Salome. The function create_overflow creates an overflow with a connector attached to it. The connector is just a straight extruded trapezoid with a draft angle, of course its dimensions may be altered. Tool designers want the metal flow inside the overflow as bad a possible, meaning metal entering the overflow via the connector should not pass directly to the exit of the overflow (the exit of the overflow is the position of venting line), because it would prematurely close the venting line. This way, venting of the tool is very ineffective, thus we want the metal to enter the overflow in such a way it directly 'crashes' into a wall of the overflow. This is what the offset is for, here called of_offset. Running test_overflow.py in Salome illustrates what of_offset can do. Seven different overflows are created, they look like this (for the image below, they were translated to -Y to separate them from the origin):

![Bildschirmfoto vom 2024-01-18 13-41-29](https://github.com/emefff/Geometry-Generation-of-Overflow-and-Venting-Systems-in-Salome-for-Die-Casting-and-Thixomolding/assets/89903493/1e62e905-b724-4cea-8719-9bcca49d4e33)

For the blue overflow of1_offset1 = [-1, 0, 0], it is centered behind its connector the second of1_offset[1] = 0. Nevertheless, of1_offset1[0] = -1, it means there is an overlap of 1mm. Because the overflow must have a draft angle, you should always use an overlap. Due to the coordinate system used, the overlap must be entered as a negative number (if we had reversed the sign, this might confuse the user). The second number in of1_offset is = 0, which makes a centered overflow. Similarly, the purple overflow features of1_offset1 = [-1, -2, 0] with the same overlap but an overflow shifted to the right. 
The red overflow shows an erroneous input, here of1_offset1 = [-1, 10, 0], the lateral shift of the overflow exceeds its dimensions. Naturally, this is an unusable result, thus the shell will show a "[ValueError] of_offset in y is too large! It can't be larger than  3.5". The maximum offset possible is also printed to the shell. 
The green and the yellow show lateral offsets with this maximum value of +-3.5mm. The last example in this script shows an overlap < 0. This, again, will print an error "[ValueError] con_overlap cannot be smaller than 0." to the shell. However, we do not want to raise a ValueError, because it would interrupt the script.
