class MTX(object):
    def __init__(self):
        self.matrix = [[0.0,0.0,0.0,0.0]*4]
    def read(self,f):
        tmp = []
        for x in range(4):
            tmp.append(f.f32_4())
        self.matrix = tmp
    def write(self,f):
        for x in self.matrix:
            f.f32_4(x)
class MatrixUnk(object):
    def __init__(self):
        self.unk = 0
        self.Count = 0
        self.Offset = 0
    def read(self,f):
        self.unk = f.u16()
        self.Count = f.u16()
        self.Offset = f.u32()
    def write(self,f):
        f.u16(self.unk)
        f.u16(self.Count)
        f.u32(self.Offset)
class MatrixTable(object):
    def __init__(self):
        self.Type = 0
        self.ParentBoneIdx = 0
        self.unk1 = 0
        self.unk2 = 0 #stage file thingy
        self.unk3 = 0
        self.unk4 = 0
        self.Matrix = MTX()
    def read(self,f):
        self.Type = f.u8()
        self.ParentBoneIdx = f.u8()
        self.unk1 = f.u16()
        self.unk2 = f.u32()
        self.unk3 = f.u32()
        self.unk4 = f.u32()
        self.Matrix.read(f)
    def write(self,f):
        f.u8(self.Type)
        f.u8(self.ParentBoneIdx)
        f.u16(self.unk1)
        f.u32(self.unk2)
        f.u32(self.unk3)
        f.u32(self.unk4)
        self.Matrix.write(f)
