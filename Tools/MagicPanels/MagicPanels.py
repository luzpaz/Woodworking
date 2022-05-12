# ###################################################################################################################

__doc__ = "This is FreeCAD library for Magic Panels"
__author__ = "Darek L (aka dprojects)"

# ###################################################################################################################

import FreeCAD, FreeCADGui
from PySide import QtGui
from PySide import QtCore


# ###################################################################################################################
# For this library purposes
# ###################################################################################################################


# ###################################################################################################################
def getSizes(iObj):
	'''
	Allow to get sizes for object (iObj), according to the object type. The values are not sorted.
	
	getSizes(iObj)
	
	Args:
	
		iObj: object to get sizes
	
	Usage:
	
		[ size1, size2, size3 ] = getSizes(obj)
		
	Result:
	
		Returns [ Length, Width, Height ] for Cube.
	'''

	if iObj.isDerivedFrom("Part::Box"):

		return [ iObj.Length.Value, iObj.Width.Value, iObj.Height.Value ]
			
	if iObj.isDerivedFrom("PartDesign::Pad"):

		for c in iObj.Profile[0].Constraints:
			if c.Name == "SizeX":
				sizeX = c.Value
			if c.Name == "SizeY":
				sizeY = c.Value
				
		return [ sizeX, sizeY, iObj.Length.Value ]

	else:
				
		return [ iObj.Base_Width.Value, iObj.Base_Height.Value, iObj.Base_Length.Value ]


# ###################################################################################################################
def getDirection(iObj):
	'''
	Allow to get Cube object direction (iType).
	
	getDirection(iObj)
	
	Args:
	
		iObj: selected object
	
	Usage:
	
		getDirection(obj)
		
	Result:
	
		Returns iType: "XY", "YX", "XZ", "ZX", "YZ", "ZY"
	'''

	if iObj.isDerivedFrom("Part::Box"):
		
		if (
			iObj.Height.Value < iObj.Width.Value and iObj.Height.Value < iObj.Length.Value and 
			iObj.Width.Value <= iObj.Length.Value
			):
			return "XY"
		
		if (
			iObj.Height.Value < iObj.Width.Value and iObj.Height.Value < iObj.Length.Value and 
			iObj.Width.Value > iObj.Length.Value
			):
			return "YX"
		
		if (
			iObj.Width.Value < iObj.Height.Value and iObj.Width.Value < iObj.Length.Value and 
			iObj.Height.Value <= iObj.Length.Value
			):
			return "XZ"
			
		if (
			iObj.Width.Value < iObj.Height.Value and iObj.Width.Value < iObj.Length.Value and 
			iObj.Height.Value > iObj.Length.Value
			):
			return "ZX"
			
		if (
			iObj.Length.Value < iObj.Height.Value and iObj.Length.Value < iObj.Width.Value and 
			iObj.Height.Value <= iObj.Width.Value
			):
			return "YZ"
			
		if (
			iObj.Length.Value < iObj.Height.Value and iObj.Length.Value < iObj.Width.Value and 
			iObj.Height.Value > iObj.Width.Value
			):
			return "ZY"

	else:
		
		ref = iObj.Profile[0].Support[0][0]
		[ sX, sY, thick ] = getSizes(iObj)
		
		if ref.Label.startswith("XY"):
			
			if sX >= sY:
				return "XY"
			
			if sX < sY:
				return "YX"
			
		if ref.Label.startswith("XZ"):
			
			if sX >= sY:
				return "XZ"
			
			if sX < sY:
				return "ZX"
			
		if ref.Label.startswith("YZ"):
			
			if sX >= sY:
				return "YZ"
			
			if sX < sY:
				return "ZY"


# ###################################################################################################################
def getVertex(iFace, iEdge, iVertex):
	'''
	Get vertex position.
	
	getVertex(iFace, iEdge, iVertex)
	
	Args:
	
		iFace: face object
		iEdge: edge array index
		iVertex: vertex array index (0 or 1)
	
	Usage:
	
		[ x, y, z ] = getVertex(gFace, 0, 1)
		
	Result:
	
		Return vertex position.
	'''
	
	# I like such typos, I would make the same ;-)
	typo = "Vertex"+"es"
	vertexArr = getattr(iFace.Edges[iEdge], typo)

	return [ vertexArr[iVertex].X, vertexArr[iVertex].Y, vertexArr[iVertex].Z ]


# ###################################################################################################################
def convertPosition(iObj, iX, iY, iZ):
	'''
	Convert given position vector to correct position values according to the direction (Plane).
	
	convertPosition(iObj, iX, iY, iZ)
	
	Args:
	
		iObj: object
		iX: x position
		iY: y position
		iZ: z position
	
	Usage:
	
		convertPosition(obj, 0, 400, 0)
		
	Result:
	
		For Pad object in XZ direction return the AttachmentOffset order [ 0, 0, -400 ]
	'''

	if iObj.isDerivedFrom("Part::Box"):
		return [ iX, iY, iZ ]
	
	else:
		
		direction = getDirection(iObj)
		
		if direction == "XY" or direction == "YX":
			return [ iX, iY, iZ ]
		
		if direction == "XZ" or direction == "ZX":
			return [ iX, iZ, -iY ]

		if direction == "YZ" or direction == "ZY":
			return [ iY, iZ, iX ]
			

# ###################################################################################################################
def sizesToCubePanel(iObj, iType):
	'''
	Convert selected object (iObj) sizes to Cube panel sizes into given direction (iType). 
	So, the returned values can be directly assigned to Cube object in order to create 
	panel in exact direction.

	sizesToCubePanel(iObj, iType)

	Args:

		iObj: selected object
		iType direction: "XY", "YX", "XZ", "ZX", "YZ", "ZY"

	Usage:

		[ Length, Width, Height ] = sizesToCubePanel(obj, "YZ")
		
	Result:

		Returns [ Length, Width, Height ] for YZ object placement".
	'''


	if iObj.isDerivedFrom("Part::Box"):

		sizes = [ iObj.Length.Value, iObj.Width.Value, iObj.Height.Value ]
		
	elif iObj.isDerivedFrom("PartDesign::Pad"):
		
		for c in iObj.Profile[0].Constraints:
			if c.Name == "SizeX":
				sizeX = c.Value
			if c.Name == "SizeY":
				sizeY = c.Value
		
		sizes = [ iObj.Length.Value, sizeX, sizeY ]
	
	else:
		
		sizes = [ iObj.Base_Length.Value, iObj.Base_Width.Value, iObj.Base_Height.Value ]

	sizes.sort()

	if iType == "XY":
		Length = sizes[2]
		Width = sizes[1]
		Height = sizes[0]

	if iType == "YX":
		Length = sizes[1]
		Width = sizes[2]
		Height = sizes[0]

	if iType == "XZ":
		Length = sizes[2]
		Width = sizes[0]
		Height = sizes[1]

	if iType == "ZX":
		Length = sizes[1]
		Width = sizes[0]
		Height = sizes[2]

	if iType == "YZ":
		Length = sizes[0]
		Width = sizes[2]
		Height = sizes[1]

	if iType == "ZY":
		Length = sizes[0]
		Width = sizes[1]
		Height = sizes[2]


	return [ Length, Width, Height ]


# ###################################################################################################################
def makePad(iSize1, iSize2, iSize3, iX, iY, iZ, iType, iPadName="Pad"):
	'''
	Allow to create Part, Plane, Body, Pad, Sketch objects.
	
	makePad(iSize1, iSize2, iSize3, iX, iY, iZ, iType, iPadName="Pad"):
	
	Args:
	
		iSize1: SizeX
		iSize2: SizeY
		iSize3: Pad Length
		iX: Sketch AttachmentOffset X
		iY: Sketch AttachmentOffset Y
		iZ: Sketch AttachmentOffset Z
		iPadName="Pad": Label for created Pad and other parts
		iType: "XY", "YX", "XZ", "ZX", "YZ", "ZY"
	
	Usage:
	
		import MagicPanels
		
		MagicPanels.makePad("600", "300", "18", 0, 0, 0, "XY", iPadName="Pad"):
		
	Result:
	
		Created Pad with correct placement.
	'''

	import Part, PartDesign
	import Sketcher
	import PartDesignGui

	doc = FreeCAD.ActiveDocument
	part = doc.addObject('App::Part', 'Part')
	part.Label = "Part, "+iPadName
	body = doc.addObject('PartDesign::Body', 'Body')
	body.Label = "Body, "+iPadName
	part.addObject(body)
	sketch = body.newObject('Sketcher::SketchObject', 'Sketch')
	sketch.Label = "Pattern, "+iPadName
	
	if iType == "XY" or iType == "YX":
		sketch.Support = (body.Origin.OriginFeatures[3])
	if iType == "XZ" or iType == "ZX":
		sketch.Support = (body.Origin.OriginFeatures[4])
	if iType == "YZ" or iType == "ZY":
		sketch.Support = (body.Origin.OriginFeatures[5])
		
	sketch.MapMode = 'FlatFace'

	geoList = []
	geoList.append(Part.LineSegment(FreeCAD.Vector(115.695488,159.435455,0),FreeCAD.Vector(274.784485,159.435455,0)))
	geoList.append(Part.LineSegment(FreeCAD.Vector(274.784485,159.435455,0),FreeCAD.Vector(274.784485,53.166523,0)))
	geoList.append(Part.LineSegment(FreeCAD.Vector(274.784485,53.166523,0),FreeCAD.Vector(115.695488,53.166523,0)))
	geoList.append(Part.LineSegment(FreeCAD.Vector(115.695488,53.166523,0),FreeCAD.Vector(115.695488,159.435455,0)))
	sketch.addGeometry(geoList,False)
	
	conList = []
	conList.append(Sketcher.Constraint('Coincident',0,2,1,1))
	conList.append(Sketcher.Constraint('Coincident',1,2,2,1))
	conList.append(Sketcher.Constraint('Coincident',2,2,3,1))
	conList.append(Sketcher.Constraint('Coincident',3,2,0,1))
	conList.append(Sketcher.Constraint('Horizontal',0))
	conList.append(Sketcher.Constraint('Horizontal',2))
	conList.append(Sketcher.Constraint('Vertical',1))
	conList.append(Sketcher.Constraint('Vertical',3))
	sketch.addConstraint(conList)
	del geoList, conList

	sketch.addConstraint(Sketcher.Constraint('Coincident',2,2,-1,1))
	sketch.addConstraint(Sketcher.Constraint('DistanceX',0,1,0,2,274.784485))
	sketch.setDatum(9,FreeCAD.Units.Quantity(iSize1))
	sketch.renameConstraint(9, u'SizeX')
	sketch.addConstraint(Sketcher.Constraint('DistanceY',3,1,3,2,159.435455))
	sketch.setDatum(10,FreeCAD.Units.Quantity(iSize2))
	sketch.renameConstraint(10, u'SizeY')

	position = FreeCAD.Vector(iX, iY, iZ)
	rotation = FreeCAD.Rotation(FreeCAD.Vector(0.00, 0.00, 1.00), 0.00)
	sketch.AttachmentOffset = FreeCAD.Placement(position, rotation)

	pad = body.newObject('PartDesign::Pad', iPadName)
	pad.Profile = sketch
	pad.Length = FreeCAD.Units.Quantity(iSize3)
	sketch.Visibility = False

	doc.recompute()


# ###################################################################################################################
def showInfo(iCaller, iInfo):
	'''
	Allow to show Gui info box for all available function and multiple calls.
	
	showInfo(iCaller, iInfo)
	
	Args:
	
		iCaller: window title
		iInfo: HTML text to show
	
	Usage:
	
		showInfo("panel"+iType, info)
		
	Result:
	
		Show info Gui.
	'''

	info = iInfo

	info += '<br><br><br><br>'
	info += 'For more details please see:' + ' '
	info += '<a href="https://github.com/dprojects/Woodworking">Woodworking workbench documentation.</a>'
	
	msg = QtGui.QMessageBox()
	msg.setWindowTitle(iCaller)
	msg.setTextFormat(QtCore.Qt.TextFormat.RichText)
	msg.setText(info)
	msg.exec_()


# ###################################################################################################################
# For external usage
# ###################################################################################################################


# ###################################################################################################################
def panelDefault(iType):
	'''
	Allow to create default panel 600 x 300 x 18 into exact direction (iType).

	panelDefault(iType)

	Args:

		iType: "XY", "YX", "XZ", "ZX", "YZ", "ZY"

	Usage:

		import MagicPanels
		
		MagicPanels.panelDefault("XY")
		
	Result:

		Created panel 600 x 300 x 18 with correct direction XY.
	'''


	try:

		panel = FreeCAD.activeDocument().addObject("Part::Box", "panel"+iType)

		if iType == "XY":
			panel.Length = 600
			panel.Width = 300
			panel.Height = 18

		if iType == "YX":
			panel.Length = 300
			panel.Width = 600
			panel.Height = 18

		if iType == "XZ":
			panel.Length = 600
			panel.Width = 18
			panel.Height = 300

		if iType == "ZX":
			panel.Length = 300
			panel.Width = 18
			panel.Height = 600

		if iType == "YZ":
			panel.Length = 18
			panel.Width = 600
			panel.Height = 300

		if iType == "ZY":
			panel.Length = 18
			panel.Width = 300
			panel.Height = 600

		FreeCAD.activeDocument().recompute()
	
	except:
	
		info = ""
		
		info += '<b>Please create active document to create default panel 600 mm x 300 mm and thickness of 18 mm.</b>' + ' '
		info += '<br>'
		
		showInfo("panelDefault"+iType, info)


# ###################################################################################################################
def panelCopy(iType):
	'''
	Allow to copy selected panel into exact direction (iType).

	panelCopy(iType)

	Args:

		iType: "XY", "YX", "XZ", "ZX", "YZ", "ZY"

	Usage:

		import MagicPanels
		
		MagicPanels.panelCopy("XY")
		
	Result:

		Created panel with correct direction XY.
	'''


	try:

		gObj = FreeCADGui.Selection.getSelection()[0]

		panel = FreeCAD.activeDocument().addObject("Part::Box", "panel"+iType)
		[ panel.Length, panel.Width, panel.Height ] = sizesToCubePanel(gObj, iType)

		FreeCAD.activeDocument().recompute()

	except:

		info = ""
		
		info += '<b>If you have active document, please select correct panel you want to copy to exact direction.</b>' + ' '
		info += '<br><br>'
		
		info += '<ul>'
		info += '<li>By default you can copy any panel based on FreeCAD Cube object. </li>'
		info += '<li>If you want to copy Pad, you need to have Constraints named "SizeX" and "SizeY" at the Sketch. </li>' 
		info += '<li>For other object types you need to have Length, Width, Height properties at object. '
		info += 'Group: "Base", Type: "App::PropertyLength". </li>'
		info += '</ul>'
	
		showInfo("panelCopy"+iType, info)


# ###################################################################################################################
def panelMove(iType):
	'''
	Allow to move panel in given direction.
	
	panelMove(iType)
	
	Args:
	
		iType: "Xp", "Xm", "Yp", "Ym", "Zp", "Zm"
	
	Usage:
	
		import MagicPanels
		
		MagicPanels.panelMove("Xp")
		
	Result:
	
		Panel will be moved into X+ direction.
	'''

	try:

		gObj = FreeCADGui.Selection.getSelection()[0]

		sizes = []
		sizes = getSizes(gObj)
		sizes.sort()

		x = 0
		y = 0
		z = 0
		
		if iType == "Xp":
			x = sizes[0]
		
		if iType == "Xm":
			x = - sizes[0]

		if iType == "Yp":
			y = sizes[0]

		if iType == "Ym":
			y = - sizes[0]

		if iType == "Zp":
			z = sizes[0]

		if iType == "Zm":
			z = - sizes[0]

		[ x, y, z ] = convertPosition(gObj, x, y, z)

		if gObj.isDerivedFrom("Part::Box"):
			ref = gObj.Placement
		else:
			ref = gObj.Profile[0].AttachmentOffset
		
		x = ref.Base.x + x
		y = ref.Base.y + y
		z = ref.Base.z + z

		if gObj.isDerivedFrom("Part::Box"):
			gObj.Placement = FreeCAD.Placement(FreeCAD.Vector(x, y, z), FreeCAD.Rotation(0, 0, 0))
		
		else:

			v = FreeCAD.Vector(x, y, z)
			r = FreeCAD.Rotation(FreeCAD.Vector(0.00,0.00,1.00), 0.00)
			gObj.Profile[0].AttachmentOffset = FreeCAD.Placement(v, r)
		
		FreeCAD.activeDocument().recompute()

	except:
		
		info = ""
		
		info += '<b>If you have active document, please select correct panel to move.</b>' + ' '
		info += '<br><br>'
		
		info += '<b>Note:</b>' + ' '
		info += 'Panel is moved into direction described by the icon. However, in some cases the panel may move '
		info += 'into opposite direction, if the panel type is not supported.'
		
		showInfo("panelMove"+iType, info)


# ###################################################################################################################
def panelResize(iType):
	'''
	Allow to resize panel in given direction.
	
	panelResize(iType)
	
	Args:
	
		iType 1: make bigger long side of panel
		iType 2: make smaller long side of panel
		iType 3: make bigger short side of panel
		iType 4: make smaller short side of panel
	
	Usage:
	
		import MagicPanels
		
		MagicPanels.panelResize("1")
		
	Result:
	
		Make bigger long side of panel.
	'''

	try:

		gObj = FreeCADGui.Selection.getSelection()[0]

		sizes = []
		sizes = getSizes(gObj)
		sizes.sort()
		
		thick = sizes[0]

		if gObj.isDerivedFrom("Part::Box"):

			if iType == "1":
				if gObj.Length.Value == sizes[2]:
					gObj.Length = gObj.Length.Value + thick
					return
					
				if gObj.Width.Value == sizes[2]:
					gObj.Width = gObj.Width.Value + thick
					return
					
				if gObj.Height.Value == sizes[2]:
					gObj.Height = gObj.Height.Value + thick
					return

			if iType == "2":
				if gObj.Length.Value == sizes[2]:
					gObj.Length = gObj.Length.Value - thick
					return
					
				if gObj.Width.Value == sizes[2]:
					gObj.Width = gObj.Width.Value - thick
					return
					
				if gObj.Height.Value == sizes[2]:
					gObj.Height = gObj.Height.Value - thick
					return

			if iType == "3":
				if gObj.Length.Value == sizes[1]:
					gObj.Length = gObj.Length.Value + thick
					return
					
				if gObj.Width.Value == sizes[1]:
					gObj.Width = gObj.Width.Value + thick
					return
					
				if gObj.Height.Value == sizes[1]:
					gObj.Height = gObj.Height.Value + thick
					return

			if iType == "4":
				if gObj.Length.Value == sizes[1]:
					gObj.Length = gObj.Length.Value - thick
					return
					
				if gObj.Width.Value == sizes[1]:
					gObj.Width = gObj.Width.Value - thick
					return
					
				if gObj.Height.Value == sizes[1]:
					gObj.Height = gObj.Height.Value - thick
					return

		else:
		
			direction = getDirection(gObj)
		
			if iType == "1":
				
				if direction == "XY" or direction == "XZ" or direction == "YZ":
					gObj.Profile[0].setDatum(9, FreeCAD.Units.Quantity(sizes[2] + thick))
				else:
					gObj.Profile[0].setDatum(10, FreeCAD.Units.Quantity(sizes[2] + thick))
			
			if iType == "2":
				
				if direction == "XY" or direction == "XZ" or direction == "YZ":
					gObj.Profile[0].setDatum(9, FreeCAD.Units.Quantity(sizes[2] - thick))
				else:
					gObj.Profile[0].setDatum(10, FreeCAD.Units.Quantity(sizes[2] - thick))
			
			if iType == "3":
				
				if direction == "XY" or direction == "XZ" or direction == "YZ":
					gObj.Profile[0].setDatum(10, FreeCAD.Units.Quantity(sizes[1] + thick))
				else:
					gObj.Profile[0].setDatum(9, FreeCAD.Units.Quantity(sizes[1] + thick))
				
			if iType == "4":
				
				if direction == "XY" or direction == "XZ" or direction == "YZ":
					gObj.Profile[0].setDatum(10, FreeCAD.Units.Quantity(sizes[1] - thick))
				else:
					gObj.Profile[0].setDatum(9, FreeCAD.Units.Quantity(sizes[1] - thick))

		FreeCAD.activeDocument().recompute()

	except:
		
		info = ""
		
		info += '<b>If you have active document, please select correct panel to resize.</b>' + ' '
		info += '<br><br>'
		
		info += '<b>Note:</b>' + ' '
		info += 'Panel is resized into direction described by the icon for XY panel. However, in some cases the '
		info += 'panel may be resized into opposite direction, if the panel is not supported or the sides are equal.'
	
		showInfo("panelResize"+iType, info)


# ###################################################################################################################
def panelFace(iType):
	'''
	Allow to create simple panel based on selected face and object.
	
	panelFace(iType)
	
	Args:
	
		iType: "XY", "YX", "XZ", "ZX", "YZ", "ZY"
	
	Usage:
	
		import MagicPanels
		
		MagicPanels.panelFace("XY")
		
	Result:
	
		Created panel at selected face with correct placement.
	'''


	try:

		gObj = FreeCADGui.Selection.getSelection()[0]
		gFace = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]

		panel = FreeCAD.activeDocument().addObject("Part::Box", "panelFace"+iType)
		[ panel.Length, panel.Width, panel.Height ] = sizesToCubePanel(gObj, iType)

		if gObj.isDerivedFrom("Part::Box"):
			[ x, y, z ] = getVertex(gFace, 0, 1)
		else:
			[ x, y, z ] = getVertex(gFace, 1, 0)

		panel.Placement = FreeCAD.Placement(FreeCAD.Vector(x, y, z), FreeCAD.Rotation(0, 0, 0))
		FreeCAD.activeDocument().recompute()
		
	except:
		
		info = ""
		
		info += '<b>If you have active document, please select face at panel to create new panel at this selected face.</b>' + ' '
		info += '<br><br>'
		
		info += '<b>Note:</b>' + ' '
		info += 'Usually for the opposite direction to the coordinate axes there is thickness offset for the panel. '
		info += 'However, to move the panel quickly to the correct place, you can: '
		info += '<ul>'
		info += '<li>use dedicated Magic Panels to move panels,</li>'
		info += '<li>use dedicated Magic Panels for left furniture side creation.</li>'
		info += '</ul>'
		
		showInfo("panelFace"+iType, info)


# ###################################################################################################################
def panelBetween(iType):
	'''
	Allow to create simple panel between 2 selected faces.
	
	panelBetween(iType)
	
	Args:
	
		iType: "XY", "YX", "XZ", "ZX", "YZ", "ZY"
	
	Usage:
	
		import MagicPanels
		
		MagicPanels.panelBetween("XY")
		
	Result:
	
		Created panel between 2 selected faces with correct placement.
	'''

	try:

		gObj = FreeCADGui.Selection.getSelection()[0]
		gFace1 = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
		gFace2 = FreeCADGui.Selection.getSelectionEx()[1].SubObjects[0]
	
		[ x1, y1, z1 ] = getVertex(gFace1, 0, 1)
		[ x2, y2, z2 ] = getVertex(gFace2, 0, 1)

		x = abs(x2 - x1)
		y = abs(y2 - y1)
		z = abs(z2 - z1)

		panel = FreeCAD.activeDocument().addObject("Part::Box", "panelBetween"+iType)
		[ panel.Length, panel.Width, panel.Height ] = sizesToCubePanel(gObj, iType)

		z1 = z1 + gObj.Height.Value - panel.Height.Value
		
		if x > 0:
			panel.Length = x
		
		if y > 0:
			panel.Width = y
			
		if z > 0:
			panel.Height = z

		panel.Placement = FreeCAD.Placement(FreeCAD.Vector(x1, y1, z1), FreeCAD.Rotation(0, 0, 0))
		FreeCAD.activeDocument().recompute()

	except:
		
		info = ""
		
		info += '<b>If you have active document, please select 2 faces at 2 different panels to create new panel between these '
		info += '2 selected faces.</b>' + ' '
		info += '<br><br>'
		
		info += '<b>Note:</b>' + ' '
		info += 'To use the feature you have to keep exact face selection order. If you change selection order the '
		info += 'result will be different. You can also experiment with outside faces, move and resize panels. To select '
		info += 'more than 1 face you have to hold CTRL key.'

		showInfo("panelBetween"+iType, info)


# ###################################################################################################################
def panelSide(iType):
	'''
	Allow to create back of the furniture with 3 selected faces.
	
	panelSide(iType)
	
	Args:
	
		"1": Left side of the furniture
		"2": Left side of the furniture but raised up
		"3": Right side of the furniture
		"4": Right side of the furniture but raised up
	
	Usage:
	
		import MagicPanels
		
		MagicPanels.panelSide("1")
		
	Result:
	
		Created side of the furniture.
	'''

	try:

		gObj = FreeCADGui.Selection.getSelection()[0]
		gFace = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]

		[ Length, Width, Height ] = sizesToCubePanel(gObj, "ZY")

		if gObj.isDerivedFrom("Part::Box"):
			[ x, y, z ] = getVertex(gFace, 0, 1)

		else:

			if iType == "1" or iType == "2":
				[ x, y, z ] = getVertex(gFace, 0, 0)

			if iType == "3" or iType == "4":
				[ x, y, z ] = getVertex(gFace, 1, 0)

		if iType == "1":
			x = x - Length
			panel = FreeCAD.activeDocument().addObject("Part::Box", "panelSideLeft")
		
		if iType == "2":
			z = z + Length
			panel = FreeCAD.activeDocument().addObject("Part::Box", "panelSideLeftUP")
		
		if iType == "3":
			panel = FreeCAD.activeDocument().addObject("Part::Box", "panelSideRight")
		
		if iType == "4":
			x = x - Length
			z = z + Length
			panel = FreeCAD.activeDocument().addObject("Part::Box", "panelSideRightUP")

		panel.Length = Length
		panel.Width = Width
		panel.Height = Height
		
		panel.Placement = FreeCAD.Placement(FreeCAD.Vector(x, y, z), FreeCAD.Rotation(0, 0, 0))
		FreeCAD.activeDocument().recompute()

	except:
		
		info = ""
		
		info += '<b>If you have active document, please select 1 face to create side of the furniture.</b>'
		info += '<br><br>'
		
		info += '<b>Note:</b>' + ' '
		info += 'The face should be selected at edge of the side you want to create new panel. '
		info += 'This feature is mostly designed to this specific situation. In other cases the result may be '
		info += 'different than expected. '

		showInfo("panelSide"+iType, info)


# ###################################################################################################################
def panelBackOut():
	'''
	Allow to create back of the furniture with 3 selected faces.
	
	panelCover(iType)
	
	Args:
	
		no args
	
	Usage:
	
		import MagicPanels
		
		MagicPanels.panelBackOut()
		
	Result:
	
		Created back of the furniture.
	'''

	try:

		gObj = FreeCADGui.Selection.getSelection()[0]

		gFace1 = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
		gFace2 = FreeCADGui.Selection.getSelectionEx()[1].SubObjects[0]
		gFace3 = FreeCADGui.Selection.getSelectionEx()[2].SubObjects[0]

		[ x, y, z ] = sizesToCubePanel(gObj, "ZX")

		[ x1, y1, z1 ] = getVertex(gFace1, 0, 1)
		[ x2, y2, z2 ] = getVertex(gFace2, 0, 0)
		[ x3, y3, z3 ] = getVertex(gFace3, 0, 1)

		x = abs(x2 - x1)
		z = z - z3

		if x > 0 and y > 0 and z > 0:

			panel = FreeCAD.activeDocument().addObject("Part::Box", "panelBackOut")
			panel.Length = x
			panel.Width = y
			panel.Height = z

			panel.Placement = FreeCAD.Placement(FreeCAD.Vector(x1, y1, z3), FreeCAD.Rotation(0, 0, 0))
			FreeCAD.activeDocument().recompute()
			
		else:
		
			raise
			
	except:
			
		info = ""
		
		info += '<b>If you have active document, please select 3 faces at 3 different panels to create back of the furniture.</b>'
		info += '<br><br>'
		
		info += '<b>Note:</b>' + ' '
		info += 'The 3rd selected face panel should be the bottom shelf of the furniture to resize the back panel to this place. '
		info += 'This feature is mostly designed to this specific situation. In other cases the result may be different than '
		info += 'expected. To use the feature you have to keep exact face selection order. If you change selection order the '
		info += 'result will be different. To select more than 1 face you have to hold CTRL key.'

		showInfo("panelBackOut", info)


# ###################################################################################################################
def panelCover(iType):
	'''
	Allow to create simple panel on top of 3 selected faces.
	
	panelCover(iType)
	
	Args:
	
		iType: "XY", "YX", "XZ", "ZX", "YZ", "ZY"
	
	Usage:
	
		import MagicPanels
		
		MagicPanels.panelCover("XY")
		
	Result:
	
		Created panel on top of 3 selected faces with correct placement.
	'''


	try:

		gObj = FreeCADGui.Selection.getSelection()[0]
		
		gFace1 = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
		gFace2 = FreeCADGui.Selection.getSelectionEx()[1].SubObjects[0]
		gFace3 = FreeCADGui.Selection.getSelectionEx()[2].SubObjects[0]

		[ x, y, z ] = sizesToCubePanel(gObj, iType)

		[ x1, y1, z1 ] = getVertex(gFace1, 0, 1)
		[ x2, y2, z2 ] = getVertex(gFace2, 2, 1)
		[ x3, y3, z3 ] = getVertex(gFace3, 0, 1)

		x = abs(x2 - x1)
		y = y + z

		if x > 0 and y > 0 and z > 0:
		
			panel = FreeCAD.activeDocument().addObject("Part::Box", "panelCover"+iType)
			panel.Length = x
			panel.Width = y
			panel.Height = z

			panel.Placement = FreeCAD.Placement(FreeCAD.Vector(x1, y1, z3), FreeCAD.Rotation(0, 0, 0))
			FreeCAD.activeDocument().recompute()

	except:
		
		info = ""
		
		info += '<b>If you have active document, please select 3 faces at 3 different panels to create new panel on top of these '
		info += '3 selected faces.</b>' + ' '
		info += '<br><br>'
		
		info += '<b>Note:</b>' + ' '
		info += 'The 3rd selected object should be the back of the furniture to resize the new cover panel with the thickness. '
		info += 'This feature is mostly designed to this specific situation. In other cases the result may be different than '
		info += 'expected. To use the feature you have to keep exact face selection order. If you change selection order the '
		info += 'result will be different. To select more than 1 face you have to hold CTRL key.'

		showInfo("panelCover"+iType, info)


# ###################################################################################################################
def panelReplacePad():
	'''
	Allow to replace Cube panel with the same panel but Pad.

	panelReplacePad()

	Args:

		no args

	Usage:

		import MagicPanels
		
		MagicPanels.panelReplacePad()
		
	Result:

		Selected Cube panel will be replaced with Pad.
	'''


	try:

		gObj = FreeCADGui.Selection.getSelection()[0]

		sizes = getSizes(gObj)
		sizes.sort()
		
		direction = getDirection(gObj)
		
		if direction == "XY" or direction == "XZ" or direction == "YZ":
			s = [ sizes[2], sizes[1], sizes[0] ]
		
		if direction == "YX" or direction == "ZX" or direction == "ZY":
			s = [ sizes[1], sizes[2], sizes[0] ]

		X = gObj.Placement.Base.x
		Y = gObj.Placement.Base.y
		Z = gObj.Placement.Base.z
		
		if direction == "XY" or direction == "YX":
			[ x, y, z ] = [ X, Y, Z ]
		
		if direction == "XZ" or direction == "ZX":
			[ x, y, z ] = [ X, Z, -(Y+sizes[0]) ]

		if direction == "YZ" or direction == "ZY":
			[ x, y, z ] = [ Y, Z, X ]

		makePad(s[0], s[1], s[2], x, y, z, direction, "rpanelPad")

		FreeCAD.ActiveDocument.removeObject(gObj.Name)
		
	except:
		
		info = ""
		
		info += '<b>If you have active document, please select Cube panel you want to replace with the same Pad panel.</b>' + ' '
		info += '<br>'
	
		showInfo("rpanelPad", info)
