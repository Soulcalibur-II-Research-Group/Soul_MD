class VertexStorageGC(object):
    def __init__(self,stride,format,fraction):
        self.stride = stride
        self.format = format #Ubyte,Byte,UShort,Short,Float
        self.fraction = fraction
        self.values = []

    def read(self,f):
        numVal = 0
        reader = f.u8
        devisor = 1
        
        match(self.format):
            case 0:
                numVal = self.stride
                reader = f.u8
                devisor = (1<<self.fraction)
            case 1:
                numVal = self.stride
                reader = f.s8
                devisor = (1<<self.fraction)
            case 2:
                numVal = int(self.stride / 2)
                reader = f.u16
                devisor = (1<<self.fraction)
            case 3:
                numVal = int(self.stride / 2)
                reader = f.s16
                devisor = (1<<self.fraction)
            case _:
                numVal = int(self.stride / 4)
                reader = f.f32
        valz = []

        for x in range(numVal):
            valbefore = reader()
            valz.append(float(float(valbefore)/devisor))
        self.values.append(valz)        
class LayerObjectEntryGC(object):
    class PolyHead(object):
        def __init__(self,StrideArr,type):
            self.Type = 0x90
            self.StrideArr = StrideArr
            self.FaceType = type
            self.IdxArr = []
            self.large = [0,0,0,0]
        def read(self,f):
            sizeValue = 1
            if(self.FaceType == 2):
                f.u8()
                sizeValue+=1
            self.Type = f.u8()
            if(self.Type > 0):
                sizeValue += 2
                idxSize = f.u16()
                
                for x in range(idxSize):
                    idx = []
                    for y in range(4):
                        if(self.StrideArr[y] == 2):
                            sizeValue +=1
                            idx.append(f.u8())
                        elif(self.StrideArr[y] == 3):
                            sizeValue += 2
                            idx.append(f.u16())
                        if(self.large[y] < idx[y]+1):
                            self.large[y] = idx[y]+1
                    self.IdxArr.append(idx)
            return sizeValue
    def __init__(self):
        self.MeshType = 0
        self.PositionStorage = VertexStorageGC(12,4,0) #setup as static
        self.NormalStorage = VertexStorageGC(12,4,0) #setup as static
        self.UVStorage = VertexStorageGC(8,4,0)

        self.idxType = [2,2,2,2] # Index8 = 2 / Index16 = 3
        self.FaceCount = 0
        self.MatrixOffset = 0
        self.MatrixIndex = 0
        self.MaterialOffset = 0
        self.MaterialIndex = 0
        self.Position1Offset = 0
        self.Position2Offset = 0
        self.Normal1Offset = 0
        self.Normal2Offset = 0
        self.ColorOffset = 0
        self.TexCoordOffset = 0
        self.FaceOffset = 0
        self.BoundingOffset = 0
        self.Mesh = []
        self.topV = 0
        self.Possition = []
        self.Normal = []
        self.Color = []
        self.TexCords = []
        self.CenterRadius = [0.0]*4
    def calc_material_index(self,offset):
        rel = offset - self.materialOffset
        idx = int(rel/0x50)
        return idx
    def calc_materix_index(self,offset):
        rel = offset - self.materixOffset
        idx = int(rel/336)
        return idx
    def read(self,f):
        self.MeshType = f.u8()

        pStride = f.u8()
        pFormat = f.u8()
        pScale = f.u8()
        self.PositionStorage = VertexStorageGC(pStride,pFormat,pScale)

        nStride = f.u8()
        nFormat = f.u8()
        nScale = f.u8()
        self.NormalStorage = VertexStorageGC(nStride,nFormat,nScale)

        uStride = f.u8()
        uFormat = f.u8()
        uScale = f.u8()
        self.UVStorage = VertexStorageGC(uStride,uFormat,uScale)


        self.idxType = [f.u8(),f.u8(),f.u8(),f.u8()] # Index8 = 2 / Index16 = 3
        self.FaceCount = f.u16()
        MatrixOffset = f.u32()
        self.MatrixIndex = self.calc_materix_index(MatrixOffset)
        MaterialOffset = f.u32()
        self.MaterialIndex = self.calc_material_index(MaterialOffset)
        self.Position1Offset = f.u32()
        self.Position2Offset = f.u32()
        self.Normal1Offset = f.u32()
        self.Normal2Offset = f.u32()
        self.ColorOffset = f.u32()
        self.TexCoordOffset = f.u32()
        self.FaceOffset = f.u32()
        self.BoundingOffset = f.u32()
        ret = f.tell()
        f.seek(self.FaceOffset)
        toContinue = self.FaceCount * 32
        self.topV = 0
        topN = 0 
        topC = 0
        topT = 0
        
        while(toContinue>0):
            head = self.PolyHead(self.idxType,self.MeshType)
            size = head.read(f)
            if(size>1):
                toContinue -= size
                if(self.topV < head.large[0]):
                    self.topV = head.large[0]
                if(topN < head.large[1]):
                    topN = head.large[1]
                if(topC < head.large[2]):
                    topC = head.large[2]
                if(topT < head.large[3]):
                    topT = head.large[3]
                self.Mesh.append(head)
            else:
                toContinue = 0
        f.seek(self.Position1Offset)
        for x in range(self.topV):
            self.PositionStorage.read(f)
        f.seek(self.Normal1Offset)
        for x in range(topN):
            self.NormalStorage.read(f)
        f.seek(self.ColorOffset)
        for x in range(topC):
            self.Color.append(f.u8_4())
        f.seek(self.TexCoordOffset)
        for x in range(topT):
            self.UVStorage.read(f)
        f.seek(self.BoundingOffset)
        self.CenterRadius = f.f32_4()
        f.seek(ret)
