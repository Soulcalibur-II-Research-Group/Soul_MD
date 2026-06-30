class LayerObjectEntryXbox(object):
    class BufferStaticVertex(object):
        def __init__(self):
            self.Position = [0.0] * 3
            self.Normal = [0.0] * 3
            self.RGBA = [255]*4
            self.UV = [0.0]*2
            self.pad = 0
        def read(self,f):
            self.Position = f.f32_3()
            self.Normal = f.f32_3()
            self.RGBA = f.u8_4()
            self.UV = f.f32_2()
            self.pad = f.u32()
        def write(self,f):
            f.f32_3(self.Position)
            f.f32_3(self.Normal)
            f.u8_4(self.RGBA)
            f.f32_2(self.UV)
            f.u32(self.pad)
    def __init__(self):
        self.materialOffset = 0
        self.materixOffset = 0
        self.ObjectType = 0
        self.PrimitiveType = 0
        self.FaceCount = 0
        self.MatrixIndex = 0
        self.MaterialIndex = 0
        self.FaceOffset = 0
        self.Buffer1Offset = 0
        self.Buffer2Offset = 0
        self.Buffer3Offset = 0
        self.Buffer4Offset = 0
        self.CenterRadiusOffset = 0
        self.Mesh = []
        self.StaticVerts = [] 
        self.CenterRadius = [0.0]*4
    def calc_material_index(self,offset):
        rel = offset - self.materialOffset
        idx = int(rel/0x50)
        return idx
    def calc_materix_index(self,offset):
        rel = offset - self.materixOffset
        idx = int(rel/400)
        return idx
    def findmaxVerts(self):
        maxi = 0
        for x in self.Mesh:
            if(x == 0xFFFF):
                pass
            elif(maxi < x):
                maxi = x
        return maxi + 1
    def read(self,f):
            self.ObjectType = f.u16()
            self.PrimitiveType = f.u16()
            self.FaceCount = f.u32()
            MatrixOffset = f.u32()
            self.MatrixIndex = self.calc_materix_index(MatrixOffset)
            MaterialOffset = f.u32()
            self.MaterialIndex = self.calc_material_index(MaterialOffset)
            self.FaceOffset = f.u32()
            self.Buffer1Offset = f.u32()
            self.Buffer2Offset = f.u32()
            self.Buffer3Offset = f.u32()
            self.Buffer4Offset = f.u32()
            self.CenterRadiusOffset = f.u32()
            fret = f.tell()
            f.seek(self.FaceOffset)
            for x in range(self.FaceCount):
                self.Mesh.append(f.u16())
            vertCount = self.findmaxVerts()
            if(self.ObjectType == 4):
                pass #All Dyna meshes share the same buffer
            else:
                f.seek(self.Buffer1Offset)
                for x in range(vertCount):
                    vert = self.BufferStaticVertex()
                    vert.read(f)
                    self.StaticVerts.append(vert)
                f.seek(self.CenterRadiusOffset)
                self.CenterRadius = f.f32_4()
            f.seek(fret)
    def write(self,f):
        f.u16(self.ObjectType)
        f.u16(self.PrimitiveType)
        f.u32(self.FaceCount)
        f.u32(self.materixOffset + (self.MatrixIndex*400))
        f.u32(self.materialOffset + (self.MaterialIndex*0x50))
        f.u32(self.FaceOffset)
        f.u32(self.Buffer1Offset)
        f.u32(self.Buffer2Offset)
        f.u32(self.Buffer3Offset)
        f.u32(self.Buffer4Offset)
        f.u32(self.CenterRadiusOffset)
    def __str__(self):
        rt = ""

        if(self.ObjectType == 0):
            rt += "STATIC\n"
        elif(self.ObjectType == 4):
            rt += "SKINNED\n"
        else:
            rt += str("UNK %i\n" % self.ObjectType)

        if(self.PrimitiveType == 0):
            rt += "TRIANGLESTRIP\n"
        elif(self.PrimitiveType == 1):
            rt += "TRIANGLELIST\n"
        else:
            rt += str("UNK %i\n" % self.PrimitiveType)
        rt += str("Face Count: %i @ %s\n" % (self.FaceCount,hex(self.FaceOffset)))
        return rt
