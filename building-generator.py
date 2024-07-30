#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import maya.cmds as cmds
import maya.mel as mel

# Creates a GUI that allows the user to choose building specifications
def create_building_gui():
    global floor_depth_field, floor_width_field, floor_height_field
    global division_quantity_field, floor_quantity_field, gfloor_divisions_field, gfloor_height_field
    
    if cmds.window("buildingWindow", exists=True):
        cmds.deleteUI("buildingWindow")

    # Define the dimensions of the GUI window
    window = cmds.window("buildingWindow", title="Building Generator", widthHeight=(400, 200), s=False)
    main_layout = cmds.columnLayout(adjustableColumn=True, parent=window)
    cmds.text(label="Building Attributes")
    
    # Create sliders for building specifications and call update_building when they are adjusted
    floor_depth_field = cmds.intSliderGrp(field=True, label="Floor Depth", minValue=1, maxValue=50, value=5, step=1, parent=main_layout, dragCommand=update_building)
    floor_width_field = cmds.intSliderGrp(field=True, label="Floor Width", minValue=1, maxValue=50, value=5, step=1, parent=main_layout, dragCommand=update_building)
    floor_height_field = cmds.intSliderGrp(field=True, label="Floor Height", minValue=1, maxValue=5, value=1, step=1, parent=main_layout, dragCommand=update_building)
    division_quantity_field = cmds.intSliderGrp(field=True, label="Window Divisions", minValue=1, maxValue=20, value=8, step=1, parent=main_layout, dragCommand=update_building)
    floor_quantity_field = cmds.intSliderGrp(field=True, label="Floor Quantity", minValue=1, maxValue=100, value=8, step=1, parent=main_layout, dragCommand=update_building)
    gfloor_divisions_field = cmds.intSliderGrp(field=True, label="Ground Floor Divisions", minValue=1, maxValue=20, value=5, step=1, parent=main_layout, dragCommand=update_building)
    gfloor_height_field = cmds.intSliderGrp(field=True, label="Ground Floor Height", minValue=1, maxValue=5, value=2, step=1, parent=main_layout, dragCommand=update_building)

    # Initialize the building object with the default values from the sliders
    generate_building(
        cmds.intSliderGrp(floor_depth_field, query=True, value=True),
        cmds.intSliderGrp(floor_width_field, query=True, value=True),
        cmds.intSliderGrp(floor_height_field, query=True, value=True),
        cmds.intSliderGrp(division_quantity_field, query=True, value=True),
        cmds.intSliderGrp(floor_quantity_field, query=True, value=True),
        cmds.intSliderGrp(gfloor_divisions_field, query=True, value=True), 
        cmds.intSliderGrp(gfloor_height_field, query=True, value=True)
    )
    
    cmds.showWindow(window)

# Updates the building model when the GUI sliders are adjusted
def update_building(*args):
    # Store the current camera position and orientation
    panel = cmds.getPanel(withFocus=True)
    if cmds.modelEditor(panel, query=True, exists=True):
        cam = cmds.modelEditor(panel, query=True, camera=True)
        cam_position = cmds.xform(cam, query=True, translation=True, worldSpace=True)
        cam_rotation = cmds.xform(cam, query=True, rotation=True, worldSpace=True)
        cam_center_of_interest = cmds.camera(cam, query=True, worldCenterOfInterest=True)
    
    floor_depth = cmds.intSliderGrp(floor_depth_field, query=True, value=True)
    floor_width = cmds.intSliderGrp(floor_width_field, query=True, value=True)
    floor_height = cmds.intSliderGrp(floor_height_field, query=True, value=True)
    division_quantity = cmds.intSliderGrp(division_quantity_field, query=True, value=True)
    floor_quantity = cmds.intSliderGrp(floor_quantity_field, query=True, value=True)
    gfloor_divisions = cmds.intSliderGrp(gfloor_divisions_field, query=True, value=True)
    ground_floor_height = cmds.intSliderGrp(gfloor_height_field, query=True, value=True)
    
    generate_building(floor_depth, floor_width, floor_height, division_quantity, floor_quantity, gfloor_divisions, ground_floor_height)
    
    # Restore the camera position and orientation
    if cmds.modelEditor(panel, query=True, exists=True):
        cmds.xform(cam, translation=cam_position, worldSpace=True)
        cmds.xform(cam, rotation=cam_rotation, worldSpace=True)
        cmds.camera(cam, edit=True, worldCenterOfInterest=cam_center_of_interest)

# Calculate the number of edges and get the minimum and maximum coordinates of the object
def coordinate_calculator(object_name):
    object_edges = cmds.polyEvaluate(object_name, edge=True)
    min_x = float('inf')
    min_y = float('inf')
    min_z = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')
    max_z = float('-inf')
    for i in range(object_edges):
        vertex_xcoord = cmds.pointPosition(f'{object_name}.vtx[{i}]', w=True)[0]
        vertex_ycoord = cmds.pointPosition(f'{object_name}.vtx[{i}]', w=True)[1]
        vertex_zcoord = cmds.pointPosition(f'{object_name}.vtx[{i}]', w=True)[2]
        min_x = min(min_x, vertex_xcoord)
        min_y = min(min_y, vertex_ycoord)
        min_z = min(min_z, vertex_zcoord)
        max_x = max(max_x, vertex_xcoord)
        max_y = max(max_y, vertex_ycoord)
        max_z = max(max_z, vertex_zcoord)
    return object_edges, min_x, max_x, min_y, max_y, min_z, max_z

# Creates the building model based on the provided specifications
def generate_building(floor_depth, floor_width, floor_height, division_quantity, floor_quantity, gfloor_divisions, ground_floor_height):
    cmds.file(new=True, force=True)
    
    # This section creates the basic floor level shape
    floor_total = cmds.polyCube(d=floor_depth, w=floor_width, h=floor_height, name="floor_name")
    floor_name = floor_total[0]
    
    # Delete the upper and lower faces of the floor level
    cmds.delete('floor_name.f[1]', 'floor_name.f[3]')
    
    # Divide the front and back faces of the floor level by the number of specified windows
    cmds.select('floor_name.e[0:1]', r=True)
    cmds.polySplitRing(ch=True, splitType=2, divisions=division_quantity)
    cmds.select('floor_name.e[2:3]', r=True)
    cmds.polySplitRing(ch=True, splitType=2, divisions=division_quantity)
    
    # Divide the lateral faces of the floor level by the number of specified windows
    cmds.select('floor_name.e[6]', 'floor_name.e[10]', r=True)
    cmds.polySplitRing(ch=True, splitType=2, divisions=division_quantity)
    cmds.select('floor_name.e[7]', 'floor_name.e[11]', r=True)
    cmds.polySplitRing(ch=True, splitType=2, divisions=division_quantity)
    
    # This section adjusts the basic floor level shape to create windows and details

    # Select edges at the top and bottom of the floor level to extrude and elongate them
    upper_edges = []
    lower_edges = []
    floor_edges = coordinate_calculator('floor_name')[0]
    floor_ymin = coordinate_calculator('floor_name')[3]
    floor_ymax = coordinate_calculator('floor_name')[4]
    
    # Iterate through the edges to identify those located at the top and bottom of the floor level
    for i in range(floor_edges):
        edge_vertices = cmds.ls(cmds.polyListComponentConversion(f'{floor_name}.e[{i}]', toVertex=True), flatten=True)
        upper_edge = all(cmds.pointPosition(v, w=True)[1] == floor_ymax for v in edge_vertices)
        lower_edge = all(cmds.pointPosition(v, w=True)[1] == floor_ymin for v in edge_vertices)
        if upper_edge:
            upper_edges.append(f'{floor_name}.e[{i}]')
        elif lower_edge:
            lower_edges.append(f'{floor_name}.e[{i}]')
    
    # Select the previously separated edges
    if upper_edges or lower_edges:
        cmds.select(upper_edges + lower_edges)
        selected_edges = cmds.ls(selection=True, flatten=True)
    else:
        print("No top and bottom edges found")
    
    # Extrude the selected edges
    cmds.polyExtrudeEdge(selected_edges, constructionHistory=True, keepFacesTogether=True, pvx=0, pvy=0, pvz=0, divisions=1, twist=0, taper=1, offset=0, thickness=0, smoothingAngle=30)
    cmds.scale(1, 1.15, 1, r=True, p=(0, 0, 0))
    
    # Select faces at the upper and lower edges of the floor shape to be extruded forward
    floor_faces = cmds.polyEvaluate(floor_name, face=True)
    selected_faces = []
    
    # Get the minimum and maximum Y-coordinates of the floor shape
    floor_ymin2 = coordinate_calculator('floor_name')[3]
    floor_ymax2 = coordinate_calculator('floor_name')[4]
    
    # Iterate through all faces of the floor shape and retrieve their vertices
    for i in range(floor_faces):
        face_vertices = cmds.ls(cmds.polyListComponentConversion(f'{floor_name}.f[{i}]', toVertex=True), flatten=True)
        has_min_y = any(cmds.pointPosition(v, w=True)[1] == floor_ymin2 for v in face_vertices)
        has_max_y = any(cmds.pointPosition(v, w=True)[1] == floor_ymax2 for v in face_vertices)
        
        # If the face has vertices with the minimum or maximum Y-coordinate, add it to the selected_faces list
        if has_min_y or has_max_y:
            selected_faces.append(f'{floor_name}.f[{i}]')
    
    # If there are selected faces, extrude them forward
    if selected_faces:
        cmds.select(selected_faces)
        cmds.polyExtrudeFacet(thickness=0.1)
    else:
        print("No faces found at the specified Y-coordinates.")
    
    # Get midpoint of the floor level to select faces and create window shapes
    midpoint_edges = (floor_ymin2 + floor_ymax2) / 2
    faces_midpoint = cmds.polyEvaluate(floor_name, face=True)
    window_faces = []
    
    # Iterate through each face to find those crossing the midpoint Y-coordinate
    for i in range(faces_midpoint):
        face_vertices = cmds.ls(cmds.polyListComponentConversion(f'{floor_name}.f[{i}]', toVertex=True), flatten=True)
        y_coords = [cmds.pointPosition(v, w=True)[1] for v in face_vertices]
        face_ymin = min(y_coords)
        face_ymax = max(y_coords)
        
        if face_ymin < midpoint_edges < face_ymax:
            window_faces.append(f'{floor_name}.f[{i}]')
    
    # Extrude the selected faces inward to create window shapes
    if window_faces:
        cmds.select(window_faces)
        cmds.polyExtrudeFacet(thickness=-0.05, offset=0.1, xft=False)
    else:
        print("No faces found crossing the midpoint Y-coordinate.")
    
    # Move the basic floor shape to the position intended for the first floor
    floor_ymin3 = coordinate_calculator(floor_name)[3]
    floor_ymax3 = coordinate_calculator(floor_name)[4]
    cmds.move(0, floor_ymin3, 0, 'floor_name.scalePivot', 'floor_name.rotatePivot', r=True)
    
    floor_height = floor_ymax3 - floor_ymin3
    previous_floor = 'floor_name'
    
    # Duplicate and stack floors vertically based on the specified quantity
    for i in range(1, floor_quantity):
        new_floor = cmds.duplicate(previous_floor)[0]
        cmds.move(0, floor_height, 0, new_floor, relative=True)
        previous_floor = new_floor
    
    # This section creates the roof and canopy structure of the building
    
    # Create a roof based on the dimensions of the basic floor level
    floor_xmin = coordinate_calculator(floor_name)[1]
    floor_xmax = coordinate_calculator(floor_name)[2]
    floor_zmin = coordinate_calculator(floor_name)[5]
    floor_zmax = coordinate_calculator(floor_name)[6]
    
    roof_width = (floor_xmax - floor_xmin) + 1
    roof_depth = (floor_zmax - floor_zmin) + 1
    roof_height = 1
    roof_level = cmds.polyCube(d=roof_depth, w=roof_width, h=roof_height, name="roof_level")[0]
    
    # Retrieve the topmost floor from the list of floor levels
    floors_list = cmds.ls('floor_name*', type='transform')
    cmds.select(floors_list[-1], roof_level, r=True)
    selected_objects = cmds.ls(selection=True)
    top_floor = selected_objects[0]
    roof_level = selected_objects[1]
    
    # Retrieve dimensions of the topmost floor level and the roof
    last_floor_bbox = cmds.exactWorldBoundingBox(top_floor)
    roof_level_bbox = cmds.exactWorldBoundingBox(roof_level)
    
    # Move roof to be positioned right above the topmost floor level
    translation_y = last_floor_bbox[4] - roof_level_bbox[1]
    cmds.move(0, translation_y, 0, roof_level, relative=True)
    
    # Create a canopy and move it to a position below the first floor level
    base_canopy = cmds.duplicate('roof_level')
    canopy_ytranslation = floor_height*(floor_quantity)+roof_height
    cmds.move(0, -(canopy_ytranslation), 0, base_canopy, relative=True)

    # This section creates the ground floor
    
    # Create the ground floor shape
    ground_floor_total = cmds.polyCube(d=floor_depth, w=floor_width, h=ground_floor_height, name="ground_floor")
    ground_floor = ground_floor_total[0]

    # Moves the ground floor pivot point to align with its bottom face
    ground_floor_bbox = cmds.exactWorldBoundingBox(ground_floor)
    cmds.move(0, (ground_floor_bbox[4]), 0, 'ground_floor.scalePivot', 'ground_floor.rotatePivot', r=True)

    # Gets canopy coordinates to position the ground floor right below it
    canopy_bbox = cmds.exactWorldBoundingBox('roof_level1')

    # Moves ground floor to position right below canopy minimum Y
    ground_floor_ytranslation = canopy_bbox[1]-(ground_floor_height/2)
    cmds.move(0, ground_floor_ytranslation, 0, ground_floor, relative=True)

    # Deletes the upper and lower faces of the ground floor level
    cmds.delete('ground_floor.f[1]', 'ground_floor.f[3]')

    # Divides the ground floor according to specified values requested for dividers
    cmds.select('ground_floor.e[0:1]', r=True)
    cmds.polySplitRing(ch=True, splitType=2, divisions=gfloor_divisions)
    cmds.select('ground_floor.e[2:3]', r=True)
    cmds.polySplitRing(ch=True, splitType=2, divisions=gfloor_divisions)

    cmds.select('ground_floor.e[6]', 'ground_floor.e[10]', r=True)
    cmds.polySplitRing(ch=True, splitType=2, divisions=gfloor_divisions)
    cmds.select('ground_floor.e[7]', 'ground_floor.e[11]', r=True)
    cmds.polySplitRing(ch=True, splitType=2, divisions=gfloor_divisions)

    # This section creates the ground floor dividers
    
    # Generates dividers based on floor level dimensions
    divider_depth = floor_width*0.01
    divider_width = floor_width*0.01
    divider_height = ground_floor_height

    floor_divider_total = cmds.polyCube(d=divider_depth, w=divider_width, h=divider_height, name="floor_divider")
    floor_divider = floor_divider_total[0]

    # Get the y-coordinate position of the ground floor
    object_name = 'ground_floor'
    floor_y_coordinate = cmds.getAttr(f"{ground_floor}.translateY")

    # Move the ground floor divider to the right of the ground floor
    divider_translationx = -((floor_width/2)-(divider_width/2))
    divider_translationy = floor_y_coordinate
    divider_translationz = -((floor_depth/2)+divider_depth/2)
    cmds.move(divider_translationx, floor_y_coordinate, divider_translationz, floor_divider, relative=True)

    # Multiplies the floor dividers across four faces of the ground floor
    divider_quantity = (gfloor_divisions*4)+4
    previous_divider = 'floor_divider'
    
    # Calculate movement distances for moving the dividers across the ground floor faces
    divider_movex = ((floor_width)/(gfloor_divisions+1))
    divider_movez = ((floor_depth+divider_depth)/(gfloor_divisions+1))
    divider_movex2 = (divider_movex+(divider_depth/gfloor_divisions))
    
    # Iterate to duplicate and move dividers, creating sections along each face of the ground floor
    for i in range(1, divider_quantity):
        # Each block in the if loop moves dividers across one face of the ground floor
        if i < (divider_quantity * 0.25)+1:
            # Duplicate the previous floor divider
            new_divider = cmds.duplicate(previous_divider)[0]
            # Move the duplicated divider to new position
            cmds.move(divider_movex, 0, 0, new_divider, relative=True)
            # Update previous_divider variable for the next iteration
            previous_divider = new_divider
        elif i < (divider_quantity * 0.5)+1:
            new_divider = cmds.duplicate(previous_divider)[0]
            cmds.move(0, 0, divider_movez, new_divider, relative=True)
            previous_divider = new_divider
        elif i < (divider_quantity * 0.75)+1:
            new_divider = cmds.duplicate(previous_divider)[0]
            cmds.move(-divider_movex2, 0, 0, new_divider, relative=True)
            previous_divider = new_divider
        elif i < divider_quantity+1:
            new_divider = cmds.duplicate(previous_divider)[0]
            cmds.move(0, 0, -divider_movez, new_divider, relative=True)
            previous_divider = new_divider
    
    # Create a list of dividers to identify those located at the vertices of the ground floor
    dividers_to_delete = cmds.ls('floor_divider*', type='transform')

    # Iterate through the list of dividers and delete only those located at the vertices of the ground floor
    for i in range(1, divider_quantity):
        if i == int(divider_quantity * 0.25) or i == int(divider_quantity * 0.50) or i == int(divider_quantity * 0.75):
            cmds.delete(dividers_to_delete[i])
    
    # Deletes a face section between dividers to create space for an entrance
    cmds.delete('ground_floor.f[1]')

    # Group all building elements together into a single group
    building_elements = cmds.ls('floor_name*', 'roof_level*', 'ground_floor', 'floor_divider*', type='transform')
    building_group = cmds.group((building_elements), name="building_grp")

    # Move the pivot point of the building group to its minimum Y coordinate
    building_bbox = cmds.exactWorldBoundingBox(building_group)
    cmds.move(0, building_bbox[1], 0, 'building_grp.scalePivot', 'building_grp.rotatePivot', r=True, a=True)

    # Move the entire building to the origin point (0, 0, 0)
    cmds.move(0, -(building_bbox[1]), 0, building_group, a=True)

# Run the GUI to create the building
create_building_gui()

