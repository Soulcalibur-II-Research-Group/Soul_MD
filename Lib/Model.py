from Lib.FormatRW import *
from Lib.Common.Bone import *
from Lib.Common.Credits import *
from Lib.VM.GCLayer import *
from Lib.VM.Header import *
from Lib.VM.Material import *
from Lib.VM.Matrix import *
from Lib.VM.WeightTable import *
from Lib.VM.XboxLayer import *

textureOffset = 0
materixOffset = 0
materialOffset = 0
isCube = False

class VM(object): #Vertex Model, Xbox = X GC = G (Example VMX,VMG so on)
    def __init__(self):
        self.f = None
        self.header = Header()
        self.unkMtx = MatrixUnk()
        self.wgtTbl = WeightTable()
        self.matrix_table = []
        self.materials = []
        self.boneInfo = []
        self.Object_0 = []
        self.Object_1 = []
        self.Object_2 = []
        self.texture = b''
        self.unkArray = b'\x00'*40
        self.credits = Credit()
        self.textureOffset = 0
        self.materixOffset = 0
        self.materialOffset = 0
    def read(self,f):
        self.f = FRead(f)
        self.header.read(self.f)
        self.textureOffset = self.header.TextureTableOffset
        textureSize = self.header.BoneHeaderOffset - self.textureOffset
        self.f.seek(self.textureOffset)
        self.texture = self.f.read(textureSize)
        self.f.seek(self.header.BoneHeaderOffset)
        aeu = f.tell()
        self.unkArray = f.read(40)
        f.seek(aeu)
        self.credits.read(self.f)
        self.f.seek(self.header.ukn_MatrixTableOffset)
        self.unkMtx.read(self.f)

        self.materixOffset = self.header.MatricesInfo['offset']
        self.f.seek(self.header.MatricesInfo['offset'])
        skipAmount = 320
        if(self.header.Endian):
            skipAmount = 256
        for x in range(self.header.MatricesInfo['count']):
            a = MatrixTable()
            a.read(self.f)
            self.matrix_table.append(a)
            self.f.seek(skipAmount,1)
        self.materialOffset = self.header.MaterialsInfo['offset']
        self.f.seek(self.header.MaterialsInfo['offset'])
        for x in range(self.header.MaterialsInfo['count']):
            a = Material(self.header.Endian)
            a.textureOffset = self.textureOffset
            a.read(self.f)
            self.materials.append(a)
        self.f.seek(self.header.BoneInfo['offset'])
        for x in range(self.header.BoneInfo['count']):
            a = BoneInfo()
            a.read(self.f)
            self.boneInfo.append(a)
        
        
        
        layerType = LayerObjectEntryXbox
        if(self.header.Endian):
            layerType = LayerObjectEntryGC
        self.f.seek(self.header.Layer0Info['offset'])
        
        for x in range(self.header.Layer0Info['count']):
            Layer = layerType()
            Layer.materialOffset = self.materialOffset
            Layer.materixOffset = self.materixOffset
            Layer.read(self.f)
            self.Object_0.append(Layer)
        self.f.seek(self.header.Layer1Info['offset'])
        for x in range(self.header.Layer1Info['count']):
            Layer = layerType()
            Layer.materialOffset = self.materialOffset
            Layer.materixOffset = self.materixOffset
            Layer.read(self.f)
            self.Object_1.append(Layer)
        self.f.seek(self.header.Layer2Info['offset'])
        for x in range(self.header.Layer2Info['count']):
            Layer = layerType()
            Layer.materialOffset = self.materialOffset
            Layer.materixOffset = self.materixOffset
            Layer.read(self.f)
            self.Object_2.append(Layer)
        if(not self.header.Endian):
            for x in self.Object_0:
                if(x.ObjectType == 4):
                    self.wgtTbl.VertBuffer0Offset = x.Buffer1Offset
            if(self.header.WeightTableCount):
                self.f.seek(self.header.WeightTableOffset)
                self.wgtTbl.read(self.f)
        else:
            if(self.header.WeightTableCount):
                self.f.seek(self.header.WeightTableOffset)
                self.wgtTbl.read_gc(self.f)
    def calcObj(self,x,head):
        x.materixOffset = self.materixOffset
        x.materialOffset = self.materialOffset
        if(x.ObjectType == 4):
            x.Buffer1Offset = self.wgtTbl.VertBuffer0Offset
            x.Buffer2Offset = self.wgtTbl.VertBuffer1Offset
            x.Buffer3Offset = self.wgtTbl.VertBuffer2Offset
            if(head % 0x10):
                head += 0x10 - (head % 0x10)
            x.FaceOffset = head
            x.FaceCount = len(x.Mesh)
            head += len(x.Mesh)*2
        if(x.ObjectType == 0):
            x.Buffer1Offset = head
            head += len(x.StaticVerts) * 40
            if(head % 0x10):
                head += 0x10 - (head % 0x10)
            x.CenterRadiusOffset = head
            head += 0x10
    def recalc(self):
        head = 0x4C # Most stuff start here... after header
        self.header.Layer0Info['offset'] = head
        self.header.Layer0Info['count'] = len(self.Object_0)
        head += len(self.Object_0)*56

        self.header.Layer1Info['offset'] = head
        self.header.Layer1Info['count'] = len(self.Object_1)
        head += len(self.Object_1)*56

        self.header.Layer2Info['offset'] = head
        self.header.Layer2Info['count'] = len(self.Object_2)
        head += len(self.Object_2)*56
        self.header.TextureMapOffset = head
        
        for x in self.materials:
            if x.TextureMap0 is not None:
                x.TextureMap0.size = 4*len(x.TextureMap0.value)+4
                x.TextureMap0.offset = head
                head += x.TextureMap0.size
            if x.TextureMap1 is not None:
                 x.TextureMap1.size = 4*len(x.TextureMap1.value)+4
                 x.TextureMap1.offset = head
                 head += x.TextureMap1.size
            if x.TextureMap2 is not None:
                 x.TextureMap2.size = len(x.TextureMap2.value)+4
                 x.TextureMap2.offset = head
                 head += x.TextureMap2.size
        
        head += 4#That part where 0xFFFFFFFF comes in... still dont know yet but we respect it
        self.header.WeightTableOffset = head
        if(self.header.WeightTableCount):
            head += 28

        self.header.ukn_MatrixTableOffset = head
        head += 8
        if(head % 0x10):
            head += 0x10 - (head % 0x10)

        self.header.MatricesInfo['offset'] = head
        self.materixOffset = head
        self.header.MatricesInfo['count'] = len(self.matrix_table)
        head += len(self.matrix_table) * 336

        self.unkMtx.Offset = head
        self.materialOffset = head
        self.header.MaterialsInfo['offset'] = head
        self.header.MaterialsInfo['count'] = len(self.materials)
        head += len(self.materials) * 80
        if(self.header.WeightTableCount):
            self.wgtTbl.VertBuffer0Offset = head
            head += len(self.wgtTbl.VertexBuff0)*12
            if(head % 0x10):
                head += 0x10 - (head % 0x10)
            self.wgtTbl.VertBuffer1Offset = head
            head += len(self.wgtTbl.VertexBuff1)*0x20
            head += 0x400 #You know your guess is as good as mine
            self.wgtTbl.VertBuffer2Offset = head
            head += len(self.wgtTbl.VertexBuff2)*0x20
            head += 0x400 #Again!
            self.wgtTbl.WeightBufferOffset = head
            head += self.wgtTbl.dynaSize()
            head += 0x10 # 0XF gang attacks again!
            for x in self.Object_0:
                if(x.ObjectType == 4):
                    x.Buffer1Offset = self.wgtTbl.VertBuffer0Offset
                    x.Buffer2Offset = self.wgtTbl.VertBuffer1Offset
                    x.Buffer3Offset = self.wgtTbl.VertBuffer2Offset
                    if(head % 0x10):
                        head += 0x10 - (head % 0x10)
                    x.FaceOffset = head
                    x.FaceCount = len(x.Mesh)
                    head += len(x.Mesh)*2
            for x in self.Object_1:
                if(x.ObjectType == 4):
                    x.Buffer1Offset = self.wgtTbl.VertBuffer0Offset
                    x.Buffer2Offset = self.wgtTbl.VertBuffer1Offset
                    x.Buffer3Offset = self.wgtTbl.VertBuffer2Offset
                    if(head % 0x10):
                        head += 0x10 - (head % 0x10)
                    x.FaceOffset = head
                    x.FaceCount = len(x.Mesh)
                    head += len(x.Mesh)*2
            for x in self.Object_2:
                if(x.ObjectType == 4):
                    x.Buffer1Offset = self.wgtTbl.VertBuffer0Offset
                    x.Buffer2Offset = self.wgtTbl.VertBuffer1Offset
                    x.Buffer3Offset = self.wgtTbl.VertBuffer2Offset
                    if(head % 0x10):
                        head += 0x10 - (head % 0x10)
                    x.FaceOffset = head
                    x.FaceCount = len(x.Mesh)
                    head += len(x.Mesh)*2
        if(head % 0x10):
            head += 0x10 - (head % 0x10)
        for x in self.Object_0:
            x.materixOffset = self.materixOffset
            x.materialOffset = self.materialOffset
            if(x.ObjectType == 0):
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
                x.Buffer1Offset = head
                x.Buffer4Offset = head
                head += len(x.StaticVerts) * 40
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
               
                x.CenterRadiusOffset = head
                head += 0x10
                x.FaceOffset = head
                x.FaceCount = len(x.Mesh)
                head += len(x.Mesh)*2
        for x in self.Object_1:
            x.materixOffset = self.materixOffset
            x.materialOffset = self.materialOffset
            if(x.ObjectType == 0):
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
                x.Buffer1Offset = head
                x.Buffer4Offset = head
                head += len(x.StaticVerts) * 40
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
                x.CenterRadiusOffset = head
                head += 0x10
                x.FaceOffset = head
                x.FaceCount = len(x.Mesh)
                head += len(x.Mesh)*2
        for x in self.Object_2:
            x.materixOffset = self.materixOffset
            x.materialOffset = self.materialOffset
            if(x.ObjectType == 0):
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
                x.Buffer1Offset = head
                x.Buffer4Offset = head
                head += len(x.StaticVerts) * 40
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
                x.CenterRadiusOffset = head
                head += 0x10
                x.FaceOffset = head
                x.FaceCount = len(x.Mesh)
                head += len(x.Mesh)*2

        self.header.BoneInfo['offset'] = head
        self.header.BoneInfo['count'] = len(self.boneInfo)
        head += len(self.boneInfo)*0x40
        if(head % 0x80):
            head += 0x80 - (head % 0x80)
            
        self.header.TextureTableOffset = head
        self.textureOffset = head+0x14
        for x in self.materials:
            x.textureOffset = head+0x14
        head += len(self.texture)
        if(head % 0x10):
            head += 0x10 - (head % 0x10)
        self.header.BoneHeaderOffset = head
        head += 40
        self.header.BoneNameOffset = head
        for x in self.boneInfo:
            if(len(x.Name)>0):
                x.BoneNameOffset = head
                head += len(x.Name)+1
            else:
                x.BoneNameOffset = 0
    def write(self,ff):
        f = FWrite(ff)
        self.recalc()
        self.header.write(f)
        for x in self.Object_0:
            x.write(f)
        for x in self.Object_1:
            x.write(f)
        for x in self.Object_2:
            x.write(f)
        for x in self.materials:
            if x.TextureMap0 is not None:
                x.TextureMap0.write(f)
            if x.TextureMap1 is not None:
                 x.TextureMap1.write(f)
            if x.TextureMap2 is not None:
                 x.TextureMap2.write(f)
        f.write(b'\xFF\xFF\xFF\xFF')
        if(self.header.WeightTableCount > 0):
            self.wgtTbl.write(f)
        self.unkMtx.write(f)
        alighnment = f.tell() % 0x10
        if(alighnment):
            for y in range(0x10-alighnment):
                f.u8(0)
        for x in self.matrix_table:
            x.write(f)
            f.write(b'\x00'*320)
        for x in self.materials:
            x.write(f)
        if(self.header.WeightTableCount > 0):
            for x in self.wgtTbl.VertexBuff0:
                x.write(f)
            alighnment = f.tell() % 0x10
            if(alighnment):
                for y in range(0x10-alighnment):
                    f.u8(0)
            for x in self.wgtTbl.VertexBuff1:
                x.write(f)
            f.write(b'\x00'*0x400)
            for x in self.wgtTbl.VertexBuff2:
                x.write(f)
            f.write(b'\x00'*0x400)
            for x in self.wgtTbl.WeightBuffer:
                for y in x:
                    y.write(f)
            f.write(b'\xFF'*0x10)
            for x in self.Object_0:
                if x.ObjectType == 0x4:
                    alighnment = f.tell() % 0x10
                    if(alighnment):
                        for y in range(0x10-alighnment):
                            f.u8(0)
                    for y in x.Mesh:
                        f.u16(y)
            for x in self.Object_1:
                if x.ObjectType == 0x4:
                    alighnment = f.tell() % 0x10
                    if(alighnment):
                        for y in range(0x10-alighnment):
                            f.u8(0)
                    for y in x.Mesh:
                        f.u16(y)
            for x in self.Object_2:
                if x.ObjectType == 0x4:
                    alighnment = f.tell() % 0x10
                    if(alighnment):
                        for y in range(0x10-alighnment):
                            f.u8(0)
                    for y in x.Mesh:
                        f.u16(y)
            alighnment = f.tell() % 0x10
            if(alighnment):
                for y in range(0x10-alighnment):
                    f.u8(0)
        for x in self.Object_0:
            if x.ObjectType == 0:
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                for y in x.StaticVerts:
                    y.write(f)
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                f.f32_4(x.CenterRadius)
                for y in x.Mesh:
                    f.u16(y)
        for x in self.Object_1:
            if x.ObjectType == 0:
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                for y in x.StaticVerts:
                    y.write(f)
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                f.f32_4(x.CenterRadius)
                for y in x.Mesh:
                    f.u16(y)
        for x in self.Object_2:
            if x.ObjectType == 0:
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                for y in x.StaticVerts:
                    y.write(f)
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                f.f32_4(x.CenterRadius)
                for y in x.Mesh:
                    f.u16(y)
        
        
        for x in self.Object_2:
            if x.ObjectType == 0:
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                for y in x.Mesh:
                    f.u16(y)
        for x in self.boneInfo:
            x.write(f)
        alighnment = f.tell() % 0x80
        if(alighnment):
            for y in range(0x80-alighnment):
                f.u8(0)
        f.write(self.texture)
        alighnment = f.tell() % 0x10
        if(alighnment):
            for y in range(0x10-alighnment):
                f.u8(0)
        f.write(self.unkArray)
        for x in self.boneInfo:
            if(len(x.Name)>0):
                f.write(x.Name.encode())
                f.u8(0)
        alighnment = f.tell() % 0x80
        if(alighnment):
            for y in range(0x80-alighnment):
                f.u8(0)
    def toXbox(self):
        if(self.header.Endian):
            global isCube
            isCube = False
            largest = 0
            newObj_0 = []
            for x in self.Object_0:
                obj = self.LayerObjectEntryXbox()
                isStatic = x.Position2Offset == 0
                obj.ObjectType = 0 if isStatic else 4
                
                isTristrip = x.Mesh[0].Type == 0x98
                obj.PrimitiveType = 0 if isTristrip else 1
                
                big = 0
                for y in x.Mesh:
                    if(big < max(y.large)):
                        big = max(y.large)
                
                newMesh = []
                if(isStatic):
                    newVert = [LayerObjectEntryXbox.BufferStaticVertex()] * big
                else:
                    newVert = [WeightTable.BufferColorUV()] * big
                
                isStart = True
                prev = 0
                for y in x.Mesh:
                    if(not isStart):
                        if(isTristrip):
                            newMesh.append(prev)
                            newMesh.append(y.IdxArr[0][0])
                    for z in y.IdxArr:
                        if(isStatic):
                            nVert = LayerObjectEntryXbox.BufferStaticVertex()
                            nVert.Position = x.PositionStorage.values[z[0]]
                            nVert.Normal = x.NormalStorage.values[z[1]]
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        else:
                            nVert = WeightTable.BufferColorUV()
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        newMesh.append(z[0])
                        prev = z[0]
                    isStart = False
                obj.Mesh = newMesh
                if(isStatic):
                    obj.StaticVerts = newVert
                    obj.CenterRadius = x.CenterRadius
                else:
                    if(largest < big):
                        self.wgtTbl.VertexBuff0 = newVert
                obj.MatrixIndex = x.MatrixIndex
                obj.MaterialIndex = x.MaterialIndex
                newObj_0.append(obj)

            newObj_1 = []
            for x in self.Object_1:
                obj = self.LayerObjectEntryXbox()
                isStatic = x.Position2Offset == 0
                obj.ObjectType = 0 if isStatic else 4
                
                isTristrip = x.Mesh[0].Type == 0x98
                obj.PrimitiveType = 0 if isTristrip else 1
                
                big = 0
                for y in x.Mesh:
                    if(big < max(y.large)):
                        big = max(y.large)
                
                newMesh = []
                if(isStatic):
                    newVert = [LayerObjectEntryXbox.BufferStaticVertex()] * big
                else:
                    newVert = [WeightTable.BufferColorUV()] * big
                
                isStart = True
                prev = 0
                for y in x.Mesh:
                    if(not isStart):
                        if(isTristrip):
                            newMesh.append(prev)
                            newMesh.append(y.IdxArr[0][0])
                    for z in y.IdxArr:
                        if(isStatic):
                            nVert = LayerObjectEntryXbox.BufferStaticVertex()
                            nVert.Position = x.PositionStorage.values[z[0]]
                            nVert.Normal = x.NormalStorage.values[z[1]]
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        else:
                            nVert = WeightTable.BufferColorUV()
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        newMesh.append(z[0])
                        prev = z[0]
                    isStart = False
                obj.Mesh = newMesh
                if(isStatic):
                    obj.StaticVerts = newVert
                    obj.CenterRadius = x.CenterRadius
                else:
                    if(largest < big):
                        self.wgtTbl.VertexBuff0 = newVert
                obj.MatrixIndex = x.MatrixIndex
                obj.MaterialIndex = x.MaterialIndex
                newObj_1.append(obj)
            newObj_2 = []
            for x in self.Object_2:
                obj = self.LayerObjectEntryXbox()
                isStatic = x.Position2Offset == 0
                obj.ObjectType = 0 if isStatic else 4
                
                isTristrip = x.Mesh[0].Type == 0x98
                obj.PrimitiveType = 0 if isTristrip else 1
                
                big = 0
                for y in x.Mesh:
                    if(big < max(y.large)):
                        big = max(y.large)
                
                newMesh = []
                if(isStatic):
                    newVert = [LayerObjectEntryXbox.BufferStaticVertex()] * big
                else:
                    newVert = [WeightTable.BufferColorUV()] * big
                
                isStart = True
                prev = 0
                for y in x.Mesh:
                    if(not isStart):
                        if(isTristrip):
                            newMesh.append(prev)
                            newMesh.append(y.IdxArr[0][0])
                    for z in y.IdxArr:
                        if(isStatic):
                            nVert = LayerObjectEntryXbox.BufferStaticVertex()
                            nVert.Position = x.PositionStorage.values[z[0]]
                            nVert.Normal = x.NormalStorage.values[z[1]]
                            
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        else:
                            nVert = WeightTable.BufferColorUV()
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        newMesh.append(z[0])
                        prev = z[0]
                    isStart = False
                obj.Mesh = newMesh
                if(isStatic):
                    obj.StaticVerts = newVert
                    obj.CenterRadius = x.CenterRadius
                else:
                    if(largest < big):
                        self.wgtTbl.VertexBuff0 = newVert
                obj.MatrixIndex = x.MatrixIndex
                obj.MaterialIndex = x.MaterialIndex
                newObj_2.append(obj)
            self.Object_0 = newObj_0
            self.Object_1 = newObj_1
            self.Object_2 = newObj_2
            #change matrix order
            for x in self.matrix_table:
                x.Matrix.matrix = rotateMtx(x.Matrix.matrix)
            #at the end we change endian
            self.header.Endian = False
            self.header.MAGIC = b'VMX.'
            self.header.Version = 4
            self.f.swapEndian()
        else:
            print("We are Xbox!")