#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.8.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/home/mario/pythonProjects/SALOME_MESH_PYTHON')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS
from salome.geom.geomtools import GeomStudyTools as gst

geompy = geomBuilder.New()

print(50*"*")
print("dir(geompy) = ", dir(geompy), "\n")
print(50*"*")
print("dir(gst) = ", dir(gst), "\n")
print(50*"*")

# origin and axes
O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )


def create_nozzle_exit(base_center, base_radius, nozzle_height, part_thickness,\
                       scale_factor):
    """
    Creates a typical nozzle exit used in Thixomolding that connects part and 
    nozzle (direct gating) or runner and nozzle. It is part of the fixed
    die. base_center denotes the position of the exit, it is the center of the
    base circle, where base_radius creates the exit face. Additionally, a circle
    with base_radius is created, it is shifted to -Z by thickness_part. scale_factor
    is used to create the smalle top face of the nozzle exit. 

    Parameters
    ----------
    base_center : TYPE list of floats
        DESCRIPTION. center of base_circle that denotes the position of the
                     nozzle exit.
    base_radius : TYPE float
        DESCRIPTION. radius of the base_circle of the nozzle exit.
    nozzle_height : TYPE float
        DESCRIPTION. height of the nozzle exit from base to top. 
    part_thickness : TYPE float
        DESCRIPTION. part thickness in the nozzle exit area. Only used for 
                     creating an additional cylinder with base_radius and 
                     thickness_part directly below the nozzle exit.
    scale_factor : TYPE float
        DESCRIPTION. scale_factor is used to scale the top face of the nozzle
                     exit. Usually this value is below < 1 because the nozzle
                     exit needs a draft angle in the tool, if scale_factor = 1
                     or > 1, the part is not deformable.

    Returns
    -------
    None.

    """
    Vertex_1 = geompy.MakeVertex(0, 0, nozzle_height)
    Disk_1 = geompy.MakeDiskR(base_radius, 1)
    Extrusion_1 = geompy.MakePrism(Disk_1, O, Vertex_1, scale_factor)
    Cylinder_1 = geompy.MakeCylinderRH(base_radius, part_thickness)
    Translation_1 = geompy.MakeTranslation(Cylinder_1, 0, 0, -part_thickness)
    ##geompy.addToStudy( Disk_1, 'Disk_1' )
    ##geompy.addToStudy( Cylinder_1, 'Cylinder_1' )
    ##geompy.addToStudy( Vertex_1, 'Vertex_1' )
    ##geompy.addToStudy( Extrusion_1, 'Extrusion_1' )
    Translation_2 = geompy.MakeTranslation(Translation_1, base_center[0], \
                                           base_center[1], base_center[2]+part_thickness)
    Translation_3 = geompy.MakeTranslation(Extrusion_1, base_center[0], \
                                           base_center[1], base_center[2]+part_thickness)
    Limit_tolerance_1 = geompy.LimitTolerance(Translation_2, 0.001)
    Limit_tolerance_2 = geompy.LimitTolerance(Translation_3, 0.001)
    geompy.addToStudy( Limit_tolerance_1, 'Disk_in_part_1' )
    geompy.addToStudy( Limit_tolerance_2, 'Nozzle_exit_1' )


def create_overflow(base_center, rot_angle_XY, overflow_dimensions, connector_dimensions,\
                     of_offset, overflow_radius, connector_radius, counter):
    """
    Creates a typical overflow and a connector to the part for die-casting 
    and Thixomolding in Salome. base_center is the center of the base trapezoid
    of the connector not the overflow. Thus base_center should be near the edge
    of the part. The overflow can (and should!) have an offset of_offset to 
    its connector, the first coordinate is used for an overlap between the 
    two bodies. The overlap is entered in negative numbers, e.g. 
    of_offset = [-1, 3, 0] will give an overlap of 1mm to the connector and 
    3mm of lateral offset. If nonsensical values are entered in of_offset, 
    ValueErrors are printed to the shell. It prints some useful design 
    parameters to the Salome Python shell for the user.

    Parameters
    ----------
    base_center : TYPE list of floats
        DESCRIPTION. coordinates of the base center, that is the center of the 
                     first trapezoid of the connector. It denotes the starting 
                     point of the connector and the overflow.
    rot_angle_XY : TYPE float
        DESCRIPTION. Rotation angle of the connector+overflow in degrees.
    overflow_dimensions : TYPE list of floats
        DESCRIPTION. dimensions of the overflow at the base (length, width, height).
                     the top face will be scaled, the side faces will have a
                     draft angle (scaling of top_face currently hardcoded). 
    connector_dimensions : TYPE list of floats
        DESCRIPTION. dimensions of the connecor at the base (length, width, height).
                     the top face will be scaled, the side faces will have a
                     draft angle (scaling of top_face currently hardcoded).
    of_offset : TYPE list of floats
        DESCRIPTION. the overflow offset determines the relative position of the
                     overflow to its connector. of_offset[0] should always be < 0. 
                     of_offset[1] sets the lateral offset, abs(of_offset[1]) 
                     cannot be larger than offset_max, otherwise the connection 
                     between the two bodies is lost. In both cases, ValueError
                     is printed to the shell, but not raised
    overflow_radius : TYPE float
        DESCRIPTION. radius that is applied to the top edges of the overflow
    connector_radius : TYPE float
        DESCRIPTION. radius that is applied to the top edges of the connector
    counter : TYPE int
        DESCRIPTION. number used for naming the bodies in Salome. Very useful
                     if you have a lot of bodies and need to correct errors.

    Returns
    -------
    None.

    """
    min_distance_to_part = 2
    con_overlap = -of_offset[0] # generally the offset will be in x because we
                                # rotate the overflow and translate it to base_center
                                # later. of_offset is set when con and of are rotated
                                # to the orientation depicted below (connector along x-axis)
    
    of_length = overflow_dimensions[0]
    of_width = overflow_dimensions[1]
    of_height = overflow_dimensions[2]
    of_stretch_factor = 0.65 # length by which the top face of the extrusion is smaller 
                             # than the base
    con_length = connector_dimensions[0] # will be shorter by con_overlap
    con_width = connector_dimensions[1]
    con_height = connector_dimensions[2]
    
    offset_max = of_length/2-con_width/2-2*connector_radius
        
    # first create a crude version of the overflow
    Face_1 = geompy.MakeFaceHW(of_width, of_length, 1)
    Vertex_1 = geompy.MakeVertex(0, 0, of_height)
    Extrusion_1 = geompy.MakePrism(Face_1, O, Vertex_1, of_stretch_factor)

    # create a basic version of the connector to the overflow
    diff_base_top = 0.3 * con_width
    Vertex_1 = geompy.MakeVertex(0, -con_width/2, 0)
    Vertex_2 = geompy.MakeVertex(0, con_width/2, 0)
    Vertex_3 = geompy.MakeVertex(0, con_width/2 - diff_base_top/2, con_height)
    Vertex_4 = geompy.MakeVertex(0, diff_base_top/2 - con_width/2, con_height)
    Line_1 = geompy.MakeLineTwoPnt(Vertex_1, Vertex_2)
    Line_2 = geompy.MakeLineTwoPnt(Vertex_2, Vertex_3)
    Line_3 = geompy.MakeLineTwoPnt(Vertex_3, Vertex_4)
    Line_4 = geompy.MakeLineTwoPnt(Vertex_4, Vertex_1)
    Face_2 = geompy.MakeFaceWires([Line_1, Line_2, Line_3, Line_4], 1)
    vector_x = geompy.MakeVectorDXDYDZ(1, 0,0) 
    Extrusion_2 = geompy.MakePrismVecH(Face_2, vector_x, con_length, 1) # length_factor is always one in a connector and we always extrude along x-axis
    Translation_1 = geompy.MakeTranslation(Extrusion_2, of_width/2, 0, 0)
    
    # add some fillets to our bodies
    Fillet_1 = geompy.MakeFillet(Extrusion_1, overflow_radius, geompy.ShapeType["EDGE"], [8, 10, 12, 17, 19, 24, 26, 30])
    Fillet_2 = geompy.MakeFillet(Translation_1, connector_radius, geompy.ShapeType["EDGE"], [17, 24])
    
    # rotate both bodies and translate base_center of connector to 0,0,0 and translate to base_center
    con_base_center = [of_width/2+con_length, 0, 0]
    ##Vertex_3 = geompy.MakeVertex(con_base_center[0], con_base_center[1], con_base_center[2]) #this in the base_center on the connector
    # it will be our new reference point, 
    ## geompy.addToStudy( Vertex_3, 'Overflow_connector_'+str(counter)+'base_center')
    # first we translate both in such a way that con_base_center is in 0,0,0
    Translation_2 = geompy.MakeTranslation(Fillet_1, -con_base_center[0], \
                                           -con_base_center[1], -con_base_center[2]  )
    Translation_3 = geompy.MakeTranslation(Fillet_2, -con_base_center[0], \
                                           -con_base_center[1], -con_base_center[2])
    # then we rotate both by 180° degrees, such that the overflow is somewhere in +X
    Rotation_1 = geompy.MakeRotation(Translation_2, OZ, 180*math.pi/180.0)
    Rotation_2 = geompy.MakeRotation(Translation_3, OZ, 180*math.pi/180.0)

    ###########################################################################
    # Both are now in the 'standard orientation' with the base_center of the connector in the origin
    # and the connector oriented along the x-axis
    #       |y-axis
    #       |
    #       |         #####  
    #       |  con    ##### overflow
    #       ###############---------->
    #       O         #####      x-axis
    #                 #####
    #
    ###########################################################################
    
    # we apply the of_offset to the overlow which also includes the overlap
    Translation_4 = geompy.MakeTranslation(Rotation_1, -con_overlap, \
                                           of_offset[1], of_offset[2]) # -con_overlap = of_offset[0]
    
    # now we can rotate both to the desired rot_angle_XY
    Rotation_3 = geompy.MakeRotation(Translation_4, OZ, rot_angle_XY*math.pi/180.0)
    Rotation_4 = geompy.MakeRotation(Rotation_2, OZ, rot_angle_XY*math.pi/180.0)
    
    # we translate both to base_center
    Translation_4 = geompy.MakeTranslation(Rotation_3, base_center[0], \
                                            base_center[1], base_center[2]  )
    Translation_5 = geompy.MakeTranslation(Rotation_4, base_center[0], \
                                            base_center[1], base_center[2])
    # limit the tolerance of the bodies
    Limit_tolerance_1 = geompy.LimitTolerance(Translation_4, 0.001)
    Limit_tolerance_2 = geompy.LimitTolerance(Translation_5, 0.001)
    
    # add the two bodies to our study
    geompy.addToStudy( Limit_tolerance_1, 'Overflow_'+str(counter) )
    geompy.addToStudy( Limit_tolerance_2, 'Overflow_connector_'+str(counter) )
    
    # print some parameters for verification
    print("Generating overflow nr ", counter, ".....")
    print("Overflow dimensions  (L/W/H) = ", of_length," ", of_width, " ", of_height)
    print("Overflow offset (X/Y/Z) = ", of_offset[0], " ", of_offset[1], " ", of_offset[2], " refers to standard orientation.")
    
    
    # measure the volume of the overflow, a very important design parameter
    of_props = geompy.BasicProperties(Translation_4)
    print("Overflow volume = ", of_props[2])
    
    print("Overflow connector dimensions  (L/W/H) = ", con_length," ", con_width, " ", con_height)
    # get the cross-section of the connector, the designer needs this value
    # make a wire from the connector cross-section
    of_con_edge_5 = geompy.GetSubShape(Translation_5, [5])
    of_con_edge_15 = geompy.GetSubShape(Translation_5, [15])
    of_con_edge_17 = geompy.GetSubShape(Translation_5, [17])
    of_con_edge_19 = geompy.GetSubShape(Translation_5, [19])
    of_con_edge_21 = geompy.GetSubShape(Translation_5, [21])
    of_con_edge_23 = geompy.GetSubShape(Translation_5, [23])
    Wire_1 = geompy.MakeWire([of_con_edge_5, of_con_edge_15, of_con_edge_17, of_con_edge_19, of_con_edge_21, of_con_edge_23], 0.001)
    geompy.ExtractShapes(Wire_1, geompy.ShapeType["EDGE"], False)
    Face_1 = geompy.MakeFaceWires([Wire_1], 1)
    con_props = geompy.BasicProperties(Face_1)
    print("Overflow connector cross-section = ", con_props[1])
       
    if con_overlap > con_length-min_distance_to_part:
        print("[ValueError] con_overlap cannot be larger than ", con_length-min_distance_to_part)
    if con_overlap <= 0:
        print("[ValueError] con_overlap cannot be smaller than 0.")
    if abs(of_offset[1]) > (offset_max):
        print("[ValueError] of_offset in y is too large! It can't be larger than ", offset_max)
    print(50*"*","\n")
    

def create_venting_line(base_center, rot_angle_XY, vent_dimensions, vent_radius, \
                        connector_at_begin, counter):
    """
    Creates a typical venting line and a connector (frustum) at its end for 
    die-casting and Thixomolding in Salome. Optionally, an additional connector
    can be created at the beginning of the venting line with connector_at_begin.    
    The final position and direction can be controlled by base_center and 
    rot_angle_XY. vent_dimensions and vent_radius control the shape of the vent.    
    It prints some useful design parameters to the Salome Python shell for the user.
    
    Parameters
    ----------
    base_center : TYPE list of floats
        DESCRIPTION. coordinates of the base center, that is the center of the 
                     first trapezoid (the 'inlet' of the venting line). It 
                     denotes the starting point of the venting line.
    rot_angle_XY : TYPE float
        DESCRIPTION. Rotation angle of the venting line in degrees.
    vent_dimensions : TYPE list of floats
        DESCRIPTION. list of 3 numbers that are the vent_length, vent_width (width
                     of the trapezoid base) and vent_height
    vent_radius : TYPE float
        DESCRIPTION. radius that is applied to the top edges of the trapezoid
    connector_at_begin : TYPE boolean
        DESCRIPTION. if True, an additional connector is created at base_center.
                     This connector is identical to the one at the end. Is useful
                     for connecting vents, but some of the frustums being twice
                     in the tree. However, that doesn't matter because a design
                     engineer would fuse bodies before sharing files anyway.
    counter : TYPE int
        DESCRIPTION. number used for naming the bodies in Salome. Very useful
                     if you have a lot of bodies and need to correct errors.

    Returns
    -------
    None. 

    """
    # radius for fillet edge for vent and vent_connector
    # connector_at_vegin = True creates a connecting frustum also at the beginning of the line
    # create a basic version of the vent
    vent_length = vent_dimensions[0] 
    vent_width = vent_dimensions[1]
    vent_height = vent_dimensions[2]
  
    diff_base_top = 0.3 * vent_width
    Vertex_1 = geompy.MakeVertex(0, -vent_width/2, 0)
    Vertex_2 = geompy.MakeVertex(0, vent_width/2, 0)
    Vertex_3 = geompy.MakeVertex(0, vent_width/2 - diff_base_top/2, vent_height)
    Vertex_4 = geompy.MakeVertex(0, diff_base_top/2 - vent_width/2, vent_height)
    Line_1 = geompy.MakeLineTwoPnt(Vertex_1, Vertex_2)
    Line_2 = geompy.MakeLineTwoPnt(Vertex_2, Vertex_3)
    Line_3 = geompy.MakeLineTwoPnt(Vertex_3, Vertex_4)
    Line_4 = geompy.MakeLineTwoPnt(Vertex_4, Vertex_1)
    Face_1 = geompy.MakeFaceWires([Line_1, Line_2, Line_3, Line_4], 1)
        
    # from the face we also create a frustum which we will put at the end of the line
    Box_1 = geompy.MakeBoxDXDYDZ(200, 200, 200)
    Face_1_Cut = geompy.MakeCutList(Face_1, [Box_1], True)
    Revolution_1 = geompy.MakeRevolution(Face_1_Cut, OZ, 360*math.pi/180.0) # this is the 'raw' frustum
    Revolution_2 = geompy.MakeTranslation(Revolution_1, vent_length, 0, 0)                 # we move it to the end of the vent line
    # we also create a Vertex that will mark the end of the vent line, we need it later   
    Vertex_1 = geompy.MakeVertex(vent_length, 0, 0)
    
    # we extrude the Face_1 along the x-axis
    vector_x = geompy.MakeVectorDXDYDZ(1, 0, 0) 
    Extrusion_1 = geompy.MakePrismVecH(Face_1, vector_x, vent_length, 1) # length_factor is always one in a vent and we always extrude along x-axis
        
    # add some fillets to our bodies
    Fillet_1 = geompy.MakeFillet(Extrusion_1, vent_radius, geompy.ShapeType["EDGE"], [17, 24])
    Fillet_2 = geompy.MakeFillet(Revolution_2, vent_radius, geompy.ShapeType["EDGE"], [5])

    ###########################################################################
    # Vent is now in the 'standard orientation' with the base_center of the vent in the origin
    # and the end-connector oriented along the x-axis
    #       |y-axis
    #       |
    #       |
    #       |  vent    end-connector
    #       O#############O-------------------->
    #       O                         x-axis
    #                 
    ###########################################################################
    
    # now we can rotate both to the desired rot_angle_XY, also Vertex_1
    Rotation_3 = geompy.MakeRotation(Fillet_1, OZ, rot_angle_XY*math.pi/180.0)
    Rotation_4 = geompy.MakeRotation(Fillet_2, OZ, rot_angle_XY*math.pi/180.0)
    Rotation_5 = geompy.MakeRotation(Vertex_1, OZ, rot_angle_XY*math.pi/180.0)

    # we translate all three to base_center
    Translation_4 = geompy.MakeTranslation(Rotation_3, base_center[0], \
                                            base_center[1], base_center[2]  )
    Translation_5 = geompy.MakeTranslation(Rotation_4, base_center[0], \
                                            base_center[1], base_center[2])
    Translation_6 = geompy.MakeTranslation(Rotation_5, base_center[0], \
                                            base_center[1], base_center[2])

    # limit the tolerance of the two bodies
    Limit_tolerance_1 = geompy.LimitTolerance(Translation_4, 0.001)
    Limit_tolerance_2 = geompy.LimitTolerance(Translation_5, 0.001)
        
    # add the two bodies to our study
    geompy.addToStudy( Limit_tolerance_1, 'Vent_'+str(counter) )
    geompy.addToStudy( Limit_tolerance_2, 'Vent_connector1_'+str(counter) )
    
    if connector_at_begin == True: # the frustrum at the beginning of the line, we use only one if and do all in one go
        Fillet_3 = geompy.MakeFillet(Revolution_1, vent_radius, geompy.ShapeType["EDGE"], [5])
        Translation_7 = geompy.MakeTranslation(Fillet_3, base_center[0], \
                                            base_center[1], base_center[2])
        Limit_tolerance_3 = geompy.LimitTolerance(Translation_7, 0.001)
        geompy.addToStudy( Limit_tolerance_3, 'Vent_connector2_'+str(counter) )
        
    # print some parameters for verification
    print("Generating vent nr ", counter, ".....")
    print("Vent dimensions  (L/W/H) = ", vent_length," ", vent_width, " ", vent_height)
    # get the cross-section of the vent, the designer needs this value
    # make a wire from the vent cross-section
    vent_edge_5 = geompy.GetSubShape(Translation_4, [5])
    vent_edge_15 = geompy.GetSubShape(Translation_4, [15])
    vent_edge_17 = geompy.GetSubShape(Translation_4, [17])
    vent_edge_19 = geompy.GetSubShape(Translation_4, [19])
    vent_edge_21 = geompy.GetSubShape(Translation_4, [21])
    vent_edge_23 = geompy.GetSubShape(Translation_4, [23])
    Wire_1 = geompy.MakeWire([vent_edge_5, vent_edge_15, vent_edge_17, \
                              vent_edge_19, vent_edge_21, vent_edge_23], 0.001)
    geompy.ExtractShapes(Wire_1, geompy.ShapeType["EDGE"], False)
    Face_1 = geompy.MakeFaceWires([Wire_1], 1)
    con_props = geompy.BasicProperties(Face_1)
    print("Vent cross-section = ", con_props[1])
    print("Vent start at (X/Y/Z) = ", base_center[0], base_center[1], base_center[2])
    end_coords = geompy.PointCoordinates(Translation_6)
    print("Vent end at (X/Y/Z) = ", end_coords[0], end_coords[1], end_coords[2])
    print(50*"*","\n")

    
###############################################################################
########################### CREATE SOME STUFF #################################
# create a dummy part
Box_1 = geompy.MakeBoxDXDYDZ(150, 80, 2)
geompy.addToStudy( Box_1, 'DUMMY_PART' )

# create a nozzle exit and a small disk in the part
base_center = [75, 40, 0]
create_nozzle_exit(base_center, 10, 50, 2, 0.7)

# OVERFLOW NR1
base_center_con_of = [150, 10, 0] # bc is the center of the connector base far away from overflow
of1_dimensions = [13, 8, 4] # length, width, height
con1_dimensions = [3, 4, 1.5] # length, width, height will be shorter by a small overlap
of1_offset1 = [-1, 2.4, 0] # 
of1_offset2 = [-1, -2.4, 0]
of1_offset3 = [-1, 0, 0]
create_overflow(base_center_con_of, 0, of1_dimensions, con1_dimensions, of1_offset1, 0.5, 0.5, 1)
base_center_vent = [base_center_con_of[0] + 7.5, base_center_con_of[1] + 7.9, 0]
vent1_dimensions = [4, 2.5, 1.]
create_venting_line(base_center_vent, 90, vent1_dimensions, 0.3, False, 10)
base_center_vent = [base_center_con_of[0] + 7.5, base_center_con_of[1] + 11.9, 0.0]
vent2_dimensions = [15, 2.5, 1.]
create_venting_line(base_center_vent, 0, vent2_dimensions, 0.3, False, 11)

# OVERFLOW NR2
base_center_con_of = [150, 40, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 0, of1_dimensions, con1_dimensions, of1_offset3, 0.5, 0.5, 2)
base_center_vent = [base_center_con_of[0] + 7.5, base_center_con_of[1] + 5.5, 0]
create_venting_line(base_center_vent, 90, vent1_dimensions, 0.3, False, 20)
base_center_vent = [base_center_con_of[0] + 7.5, base_center_con_of[1] + 9.5, 0.0]
create_venting_line(base_center_vent, 0, vent2_dimensions, 0.3, False, 21)

# OVERFLOW NR3
base_center_con_of = [150, 70, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 0, of1_dimensions, con1_dimensions, of1_offset2, 0.5, 0.5, 3)
base_center_vent = [base_center_con_of[0] + 7.5, base_center_con_of[1] - 7.8, 0]
create_venting_line(base_center_vent, 270, vent1_dimensions, 0.3, False, 30)
base_center_vent = [base_center_con_of[0] + 7.5, base_center_con_of[1] - 11.8, 0.0]
create_venting_line(base_center_vent, 0, vent2_dimensions, 0.3, False, 31)

###############################################################################
# OVERFLOW NR4
base_center_con_of = [0, 10, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 180, of1_dimensions, con1_dimensions, of1_offset2, 0.5, 0.5, 4)
base_center_vent = [base_center_con_of[0] - 7.5, base_center_con_of[1] + 7.9, 0]
create_venting_line(base_center_vent, 90, vent1_dimensions, 0.3, False, 40)
base_center_vent = [base_center_con_of[0] - 7.5, base_center_con_of[1] + 11.9, 0.0]
create_venting_line(base_center_vent, 180, vent2_dimensions, 0.3, False, 41)

# OVERFLOW NR5
base_center_con_of = [0, 40, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 180, of1_dimensions, con1_dimensions, of1_offset3, 0.5, 0.5, 5)
base_center_vent = [base_center_con_of[0] - 7.5, base_center_con_of[1] + 5.5, 0]
create_venting_line(base_center_vent, 90, vent1_dimensions, 0.3, False, 50)
base_center_vent = [base_center_con_of[0] - 7.5, base_center_con_of[1] + 9.5, 0.0]
create_venting_line(base_center_vent, 180, vent2_dimensions, 0.3, False, 51)

# OVERFLOW NR6
base_center_con_of = [0, 70, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 180, of1_dimensions, con1_dimensions, of1_offset1, 0.5, 0.5, 6)
base_center_vent = [base_center_con_of[0] - 7.5, base_center_con_of[1] - 7.8, 0]
create_venting_line(base_center_vent, 270, vent1_dimensions, 0.3, False, 60)

base_center_vent = [base_center_con_of[0] - 7.5, base_center_con_of[1] - 11.8, 0.0]
create_venting_line(base_center_vent, 180, vent2_dimensions, 0.3, False, 61)

###############################################################################
###############################################################################
# OVERFLOW NR7
base_center_con_of = [20, 0, 0] # bc is the center of the connector base far away from overflow
of2_dimensions = [15, 9, 4.5] # length, width, height
con2_dimensions = [3, 5, 1.5] # length, width, height will be shorter by a small overlap
of2_offset1 = [-1, 3.5, 0] # 
of2_offset2 = [-1, -3.5, 0]
of2_offset3 = [-1, 0, 0]

create_overflow(base_center_con_of, 270, of2_dimensions, con2_dimensions, of2_offset1, 0.5, 0.5, 7)
base_center_vent = [base_center_con_of[0] + 10, base_center_con_of[1] - 7.9, 0]
vent3_dimensions = [4, 3, 1.2]
create_venting_line(base_center_vent, 0, vent3_dimensions, 0.3, False, 70)
base_center_vent = [base_center_con_of[0] + 14, base_center_con_of[1] - 7.9, 0.0]
vent4_dimensions = [15, 3, 1.2]
create_venting_line(base_center_vent, 270, vent4_dimensions, 0.3, False, 71)

# OVERFLOW NR8
base_center_con_of = [50, 0, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 270, of2_dimensions, con2_dimensions, of2_offset1, 0.5, 0.5, 8)
base_center_vent = [base_center_con_of[0] + 10, base_center_con_of[1] -7.9, 0]
create_venting_line(base_center_vent, 0, vent3_dimensions, 0.3, False, 80)
base_center_vent = [base_center_con_of[0] + 14, base_center_con_of[1] -7.9, 0.0]
create_venting_line(base_center_vent, 270, vent4_dimensions, 0.3, False, 81)

###############################################################################
# OVERFLOW NR9
base_center_con_of = [20, 80, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 90, of2_dimensions, con2_dimensions, of2_offset2, 0.5, 0.5, 9)
base_center_vent = [base_center_con_of[0] + 10, base_center_con_of[1] + 7.9, 0]
create_venting_line(base_center_vent, 0, vent3_dimensions, 0.3, False, 90)
base_center_vent = [base_center_con_of[0] + 14, base_center_con_of[1] + 7.9, 0.0]
create_venting_line(base_center_vent, 90, vent4_dimensions, 0.3, False, 91)

# OVERFLOW NR10
base_center_con_of = [50, 80, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 90, of2_dimensions, con2_dimensions, of2_offset2, 0.5, 0.5, 10)
base_center_vent = [base_center_con_of[0] + 10, base_center_con_of[1] + 7.9, 0]
create_venting_line(base_center_vent, 0, vent3_dimensions, 0.3, False, 100)
base_center_vent = [base_center_con_of[0] + 14, base_center_con_of[1] +7.9, 0.0]
create_venting_line(base_center_vent, 90, vent4_dimensions, 0.3, False, 101)

###############################################################################
# OVERFLOW NR11
base_center_con_of = [130, 0, 0] # bc is the center of the connector base far away from overflow

create_overflow(base_center_con_of, 270, of2_dimensions, con2_dimensions, of2_offset2, 0.5, 0.5, 7)
base_center_vent = [base_center_con_of[0] - 10, base_center_con_of[1] - 7.9, 0]
create_venting_line(base_center_vent, 180, vent3_dimensions, 0.3, False, 70)
base_center_vent = [base_center_con_of[0] - 14, base_center_con_of[1] - 7.9, 0.0]
create_venting_line(base_center_vent, 270, vent4_dimensions, 0.3, False, 71)

# OVERFLOW NR12
base_center_con_of = [100, 0, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 270, of2_dimensions, con2_dimensions, of2_offset2, 0.5, 0.5, 8)
base_center_vent = [base_center_con_of[0] - 10, base_center_con_of[1] -7.9, 0]
create_venting_line(base_center_vent, 180, vent3_dimensions, 0.3, False, 80)
base_center_vent = [base_center_con_of[0] - 14, base_center_con_of[1] -7.9, 0.0]
create_venting_line(base_center_vent, 270, vent4_dimensions, 0.3, False, 81)

###############################################################################
# OVERFLOW NR13
base_center_con_of = [130, 80, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 90, of2_dimensions, con2_dimensions, of2_offset1, 0.5, 0.5, 13)
base_center_vent = [base_center_con_of[0] - 10, base_center_con_of[1] + 7.9, 0]
create_venting_line(base_center_vent, 180, vent3_dimensions, 0.3, False, 130)
base_center_vent = [base_center_con_of[0] - 14, base_center_con_of[1] + 7.9, 0.0]
create_venting_line(base_center_vent, 90, vent4_dimensions, 0.3, False, 131)

# OVERFLOW NR14
base_center_con_of = [100, 80, 0] # bc is the center of the connector base far away from overflow
create_overflow(base_center_con_of, 90, of2_dimensions, con2_dimensions, of2_offset1, 0.5, 0.5, 14)
base_center_vent = [base_center_con_of[0] - 10, base_center_con_of[1] + 7.9, 0]
create_venting_line(base_center_vent, 180, vent3_dimensions, 0.3, False, 140)
base_center_vent = [base_center_con_of[0] - 14, base_center_con_of[1] +7.9, 0.0]
create_venting_line(base_center_vent, 90, vent4_dimensions, 0.3, False, 141)


###############################################################################
############################## CONNECT THE VENTS ##############################
vent5_dimensions = [116-34, 7, 2.2]
base_center_vent = [116, -22.9, 0] 
create_venting_line(base_center_vent, 180, vent5_dimensions, 0.3, True, 150)

base_center_vent = [116, 22.9+80, 0] 
create_venting_line(base_center_vent, 180, vent5_dimensions, 0.3, True, 160)

###############################################################################
vent6_dimensions = [58.2-21.9, 5, 1.5]
base_center_vent = [-22.5, 21.9, 0] 
create_venting_line(base_center_vent, 90, vent6_dimensions, 0.3, True, 170)

base_center_vent = [22.5+150, 21.9, 0] 
create_venting_line(base_center_vent, 90, vent6_dimensions, 0.3, True, 180)

###############################################################################
################### CONNECT THE CONNECTED VENT TO THE ATMOSPHERE ##############
vent7_dimensions = [10, 7, 2.2]
base_center_vent = [75, 102.9, 0] 
create_venting_line(base_center_vent, 90, vent7_dimensions, 0.3, True, 190)

base_center_vent = [75, -(102.9-80), 0] 
create_venting_line(base_center_vent, 270, vent7_dimensions, 0.3, True, 200)

###############################################################################
vent8_dimensions = [10, 5, 1.5]
base_center_vent = [-22.5, 40.05, 0] 
create_venting_line(base_center_vent, 180, vent8_dimensions, 0.3, True, 210)

base_center_vent = [22.5+150, 40.05, 0] 
create_venting_line(base_center_vent, 0, vent8_dimensions, 0.3, True, 220)

###############################################################################
vent9_dimensions = [32.5+75, 7, 2.2]
base_center_vent = [75, -32.9, 0] 
create_venting_line(base_center_vent, 180, vent9_dimensions, 0.3, True, 230)
base_center_vent = [75, 112.9, 0] 
create_venting_line(base_center_vent, 0, vent9_dimensions, 0.3, True, 240)


vent10_dimensions = [32.9+40.05, 5, 1.5]
base_center_vent = [-32.5, 40.05, 0] 
create_venting_line(base_center_vent, 270, vent10_dimensions, 0.3, True, 250)
base_center_vent = [32.5+150, 40.05, 0] 
create_venting_line(base_center_vent, 90, vent10_dimensions, 0.3, True, 260)

###############################################################################
vent11_dimensions = [40, 10, 2.5]
base_center_vent = [-32.5, -32.9, 0] 
create_venting_line(base_center_vent, 180+45, vent11_dimensions, 0.3, True, 270)
base_center_vent = [182.5, 112.9, 0] 
create_venting_line(base_center_vent, 45, vent11_dimensions, 0.3, True, 280)


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
