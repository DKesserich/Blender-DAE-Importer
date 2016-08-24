import bpy
import xml.etree.ElementTree as ET
import math
from mathutils import *

C = bpy.context
D = bpy.data

#############
#DAE Schemas#
#############

#Just defining all the DAE attributes here so the processing functions are more easily readable

#Utility Schemas
DAENode = "{http://www.collada.org/2005/11/COLLADASchema}node"
DAETranslation = "{http://www.collada.org/2005/11/COLLADASchema}translate"
DAEInit = "{http://www.collada.org/2005/11/COLLADASchema}init_from"
DAEInput = "{http://www.collada.org/2005/11/COLLADASchema}input"
DAEFloats = "{http://www.collada.org/2005/11/COLLADASchema}float_array"
DAESource = "{http://www.collada.org/2005/11/COLLADASchema}source"
DAEInstance = "{http://www.collada.org/2005/11/COLLADASchema}instance_geometry"

##Material Schemas
DAELibMaterials = "{http://www.collada.org/2005/11/COLLADASchema}library_materials"
DAEMaterials = "{http://www.collada.org/2005/11/COLLADASchema}material"
DAELibEffects = "{http://www.collada.org/2005/11/COLLADASchema}library_effects"
DAEfx = "{http://www.collada.org/2005/11/COLLADASchema}effect"
DAELibImages = "{http://www.collada.org/2005/11/COLLADASchema}library_images"
DAEimage = "{http://www.collada.org/2005/11/COLLADASchema}image"
DAETex = "{http://www.collada.org/2005/11/COLLADASchema}texture"
DAEProfile = "{http://www.collada.org/2005/11/COLLADASchema}profile_COMMON"
DAETechnique = "{http://www.collada.org/2005/11/COLLADASchema}technique"
DAEPhong = "{http://www.collada.org/2005/11/COLLADASchema}phong"

#Geometry Schemas
DAEGeo = "{http://www.collada.org/2005/11/COLLADASchema}geometry"
DAEMesh = "{http://www.collada.org/2005/11/COLLADASchema}mesh"
DAEVerts = "{http://www.collada.org/2005/11/COLLADASchema}vertices"
DAETris = "{http://www.collada.org/2005/11/COLLADASchema}triangles"
DAEp = "{http://www.collada.org/2005/11/COLLADASchema}p"

#Animation Schemas
DAELibAnims = "{http://www.collada.org/2005/11/COLLADASchema}library_animations"
DAEAnim = "{http://www.collada.org/2005/11/COLLADASchema}animation"
DAEChannel = "{http://www.collada.org/2005/11/COLLADASchema}channel"

###########
#Functions#
###########
DAEPath = "F:\\Program Files\\Steam\\steamapps\\workshop\\content\\244160\\426296252\\Kus_SupportFrigate\\"

def makeTextures(name, path):
	D.textures.new(name, 'IMAGE')	
	D.textures[name].image = D.images.load(DAEPath+path)
	
def makeMaterials(name, textures):
	D.materials.new(name)
	
	if len(textures) > 0:	
	   D.materials[name].texture_slots.add()
	   D.materials[name].texture_slots[0].texture = D.textures[textures[0]]
		

def meshBuilder(matName, Verts, Normals, UVCoords, vertOffset, normOffset, UVoffsets, pArray):
    print("Building "+matName)
    subMesh = D.meshes.new(matName)
    ob = bpy.data.objects.new(subMesh.name, subMesh)
    
    
    
    #split <p> array to get just the face data
    faceIndices = []
    for i in range(0, len(pArray)):
        faceIndices.append(pArray[i][vertOffset])
    faceTris = [faceIndices[i:i+3] for i in range(0,len(faceIndices),3)]
    #print(Verts)
    #print(faceTris)    
    subMesh.from_pydata(Verts,[],faceTris)
    if matName is not "None":
        subMesh.materials.append(D.materials[matName])
    
    normIndices = []
    for i in range(0, len(pArray)):
        normIndices.append(Vector(Normals[pArray[i][normOffset]]))
    
    #print(normIndices)
    #print(len(normIndices))
    #print(len(D.meshes[matName].loops))
    
    subMesh.normals_split_custom_set(normIndices)
    subMesh.use_auto_smooth = True
    
    #Add UVs
    if len(UVCoords) > 0:
        for coords in range(0,len(UVOffsets)):
            subMesh.uv_textures.new()
    
            meshUV = []
            for p in range(0, len(pArray)):
                meshUV.append(UVCoords[coords][pArray[p][UVoffsets[coords]]])
            #print(meshUV)
    
            for l in range(0,len(subMesh.uv_layers[coords].data)):
                subMesh.uv_layers[coords].data[l].uv = meshUV[l]
        
    
    #for i in range(0,len(UVCoords)):
    #    D.meshes[matName].uv_textures.new()
    #    for l in range(0,len(D.meshes[matName].loops)):
    #        D.meshes[matName].uv_layers[i].data[l].uv = Vector(UVCoords[i][pArray[i][UVoffsets[i]]])
    
    C.scene.objects.link(ob)
    
    return ob

#If it ain't broke don't fix it. This function written by Dom2
def CreateJoint(jnt_name,jnt_locn,jnt_rotn,jnt_context):
    #print("Creating joint" + jnt_name)
    this_jnt = bpy.data.objects.new(jnt_name, None)
    jnt_context.scene.objects.link(this_jnt)
    pi = math.pi
    this_jnt.rotation_euler.x = joint_rotation[0] * (pi/180.0)
    this_jnt.rotation_euler.y = joint_rotation[1] * (pi/180.0)
    this_jnt.rotation_euler.z = joint_rotation[2] * (pi/180.0)
    this_jnt.location.x = float(jnt_locn[0])
    this_jnt.location.y = float(jnt_locn[1])
    this_jnt.location.z = float(jnt_locn[2])
    
    if "dock" in jnt_name.lower():
        if jnt_name.lower() is not "hold_dock":
            jointProps = jnt_name.split("_")
            
            for p in jointProps:
                if "flags" in p.lower():
                    print(p)
                    this_jnt["Flags"] = p[6:].rstrip("]")
                if "link" in p.lower():
                    print(p)
                    this_jnt["Link"] = p[5:].rstrip("]")
                if "fam" in p.lower():
                    print(p)
                    this_jnt["Fam"] = p[4:].rstrip("]")
                    print(this_jnt["Fam"])
                if "mad" in p.lower():
                    print(p)
                    this_jnt["MAD"] = p.lstrip("MAD[").rstrip("]") 
            
    if "seg" in jnt_name.lower():
        jointProps = jnt_name.split("_")
        this_jnt.empty_draw_type = "SPHERE"
        
        for p in jointProps:
            if "flags" in p.lower():
                this_jnt["Flags"] = p[6:].rstrip("]")
            if "spd" in p.lower():
                this_jnt["Speed"] = int(p[4:].rstrip("]"))
            if "tol" in p.lower():
                this_jnt.empty_draw_size = float(p[4:].rstrip("]"))
                
            
    return this_jnt

def CheckForChildren(node,context):
    for item in node:
        
        if "node" in item.tag:                                
            if bpy.data.objects.get(item.attrib["name"][0:63]) is None:
                for i in item:
                    if "instance_geometry" in i.tag:
                        url = i.attrib["url"].lstrip("#")
                        for geo in root.iter(DAEGeo):
                            if geo.attrib["id"] == url:
                                child = D.objects[geo.attrib["name"]]
                                parent = D.objects[node.attrib["name"][0:63]]
                                child.parent = parent
                                CheckForChildren(item,context)
            else:
                child = D.objects[item.attrib["name"][0:63]]
                parent = D.objects[node.attrib["name"][0:63]]
                child.parent = parent
                CheckForChildren(item,context)
        


################
#XML Processing#
################

#More Dom2 code here
tree = ET.parse("F:\\Program Files\\Steam\\steamapps\\workshop\\content\\244160\\426296252\\Kus_SupportFrigate\\Kus_SupportFrigate.dae")
root = tree.getroot()

print(" ")
print("CREATING JOINTS")
print(" ")

# Create joints
for joint in root.iter(DAENode): # find all <node> in the file
    # Joint name
    joint_name = joint.attrib["name"]
    print(joint_name)
    # Joint location
    joint_location = joint.find(DAETranslation)
    if joint_location == None:
        joint_location = ['0','0','0'] # If there is no translation specified, default to 0,0,0
    else:
        joint_location = joint_location.text.split()
    # Joint rotation
    joint_rotationX = 0.0
    joint_rotationY = 0.0
    joint_rotationZ = 0.0
    for rot in joint:
        if "rotate" in rot.tag:
            if "rotateX" in rot.attrib["sid"]:
                joint_rotationX = float(rot.text.split()[3])
            elif "rotateY" in rot.attrib["sid"]:
                joint_rotationY = float(rot.text.split()[3])
            elif "rotateZ" in rot.attrib["sid"]:
                joint_rotationZ = float(rot.text.split()[3])
    joint_rotation = [joint_rotationX,joint_rotationY,joint_rotationZ]
    # Joint or mesh?
    is_joint = True
    for item in joint:
        if "instance_geometry" in item.tag:
            print("this is a mesh:" + item.attrib["url"])
            is_joint = False
    # If this is a joint, make it!
    if is_joint:
        CreateJoint(joint_name, joint_location,joint_rotation,C)
		
#My code starts here - DL

#find textures and create them
for img in root.find(DAELibImages):
	#print(img.attrib["name"])
	#print(img.find(DAEInit).text)
	makeTextures(img.attrib["name"],img.find(DAEInit).text.lstrip("file://"))

#Make materials based on the Effects library
for fx in root.find(DAELibEffects).iter(DAEfx):
    matname = fx.attrib["name"]
    #print(matname)   
   
    matTextures = []
    
    for t in fx.iter(DAETex): 
        matTextures.append(t.attrib["texture"].rstrip("-image"))
	
        
    
    makeMaterials(matname, matTextures)

#Find the mesh data and split the coords into 2D arrays

for geo in root.iter(DAEGeo):
    meshName = geo.attrib["name"]
    mesh = geo.find(DAEMesh)
    
    blankMesh = D.meshes.new(meshName)
    ob = bpy.data.objects.new(meshName, blankMesh)
    C.scene.objects.link(ob)
    
    print(meshName)    
    
    UVs = []
    
    for source in mesh.iter(DAESource):
        #print("Source: " + source.attrib["id"])
        if "position" in source.attrib["id"].lower():
            rawVerts = [float(i) for i in source.find(DAEFloats).text.split()]
            #print(rawVerts)
        
        if "normal" in source.attrib["id"].lower():
            rawNormals = [float(i) for i in source.find(DAEFloats).text.split()]
        
        if "uv" in source.attrib["id"].lower():
            #print("Found UV: "+source.attrib["id"])
            rawUVs = [float(i) for i in source.find(DAEFloats).text.split()]
            coords = [rawUVs[i:i+2] for i in range(0, len(rawUVs),2)]
            UVs.append(coords)
        
    #print("Num of UVs: "+str(len(UVs)))        
    vertPositions = [rawVerts[i:i+3] for i in range(0, len(rawVerts),3)]
    meshNormals = [rawNormals[i:i+3] for i in range(0, len(rawNormals),3)]
    
    
    subMeshes = []
    
    for tris in mesh.iter(DAETris):
        if "material" in tris.attrib:
            material = tris.attrib["material"]
        else:
            material = "None"
            
        maxOffset = 0
        UVOffsets = []
        vertOffset = 0
        normOffset = 0
        for inp in tris.iter(DAEInput):
            if int(inp.attrib["offset"]) > maxOffset:
                maxOffset = int(inp.attrib["offset"])
            if inp.attrib["semantic"].lower() == "texcoord":
                UVOffsets.append(int(inp.attrib["offset"]))
            if inp.attrib["semantic"].lower() == "vertex":
                vertOffset = int(inp.attrib["offset"])
            if inp.attrib["semantic"].lower() == "normal":
                normOffset =  int(inp.attrib["offset"])
        if tris.find(DAEp).text is not None:
            splitPsoup = [int(i) for i in tris.find(DAEp).text.split()]
            pArray = [splitPsoup[i:i+(maxOffset+1)] for i in range(0, len(splitPsoup),(maxOffset+1))]
        #print(pArray)
        #print("Max Offset "+str(maxOffset))
        #print("UV Offsets "+str(len(UVOffsets)))
        
        subMeshes.append(meshBuilder(material, vertPositions, meshNormals, UVs, vertOffset, normOffset, UVOffsets, pArray))
    
    #Combines the material submeshes into one mesh
    for obs in subMeshes:
        obs.select = True
    
    ob.select = True
    C.scene.objects.active = ob
    bpy.ops.object.join()
    ob.data.use_auto_smooth = True
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.editmode_toggle()
    ob.select = False
    
# Sort out hierarchy
for child in root:
	if "library_visual_scenes" in child.tag:
		for grandchild in child:
			if "visual_scene" in grandchild.tag:
				for node in grandchild:
					if "node" in node.tag:
						CheckForChildren(node,C)
		
#Animations	
animLib = root.find(DAELibAnims)
for anim in animLib.iter(DAEAnim):
    #print(animLib.getchildren().index(anim))
    if anim.find(DAESource):
        frames = []
        locs = []
        #D.objects[animLib[(animLib.getchildren().index(anim)-1)].attrib["name"]].select = True
        for source in anim.iter(DAESource):           
           # print(source.attrib["id"])
            if "input" in source.attrib["id"].lower():
                frames = [float(i) for i in source.find(DAEFloats).text.split()]
                #print(frames)
            elif "output" in source.attrib["id"].lower():
                locs = [float(i) for i in source.find(DAEFloats).text.split()]
                #print(locs)
        #D.objects[(anim.find(DAEChannel).attrib["target"].split("/")[0])].select = True
        channel = anim.find(DAEChannel).attrib["target"].split("/")[1]
        object = D.objects[anim.find(DAEChannel).attrib["target"].split("/")[0]]
        for f in range(0, len(frames)):
            currentFrame = (frames[f]*C.scene.render.fps)
            if "translate" in channel.lower():
                if "x" in channel.lower():
                    object.location.x =  locs[f]
                    object.keyframe_insert(data_path = 'location',index = 0, frame = currentFrame)
                elif "y" in channel.lower():
                    object.location.y =  locs[f]
                    object.keyframe_insert(data_path = 'location',index = 1, frame = currentFrame)
                elif "z" in channel.lower():
                    object.location.z =  locs[f]
                    object.keyframe_insert(data_path = 'location',index = 2, frame = currentFrame)
            elif "rotatex" in channel.lower():
                object.rotation_euler.x = locs[f]*(math.pi/180)
                object.keyframe_insert(data_path = 'rotation_euler',index = 0, frame = currentFrame)
            elif "rotatey" in channel.lower():
                object.rotation_euler.y = locs[f]*(math.pi/180)
                object.keyframe_insert(data_path = 'rotation_euler',index = 1, frame = currentFrame)
            elif "rotatez" in channel.lower():
                object.rotation_euler.z = locs[f]*(math.pi/180)
                object.keyframe_insert(data_path = 'rotation_euler',index = 2, frame = currentFrame)
            
                        

	
