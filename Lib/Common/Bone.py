class BoneInfo(object):
    def __init__(self):
        self.EndPositionXYZScale = []
        self.swing_backup = bytearray()
        self.StartPositionXYZScale = []
        self.Rotation = []
        self.BoneNameOffset = 0
        self.unk0 = []
        self.rotfix = []
        self.rotfix2 = bytearray()
        self.unk1 = 0
        self.BoneParentIdx = -1
        self.BoneIdx = 0
        self.boneType = 1
        self.Name = ""
    def to_dict(self):
        return {'Name' : self.Name,'EndPositionXYZScale' : self.EndPositionXYZScale,
                'StartPositionXYZScale' : self.StartPositionXYZScale,
                'Rotation' : self.Rotation,
                'Unk0':self.unk0, 'unk1' : self.unk1,'BoneParentIdx':self.BoneParentIdx,
                'BoneIdx':self.BoneIdx,'boneType':self.boneType}
    def read(self,f,isSC3=False):
        start = f.tell()
        self.EndPositionXYZScale = f.f32_4()
        self.StartPositionXYZScale = f.f32_4()
        self.Rotation = f.f32_3()
        self.BoneNameOffset = f.u32()
        rotstart = f.tell()
        self.unk0 = f.f32_3()
        self.unk1 = f.u8()
        self.BoneParentIdx = f.u8()
        self.BoneIdx = f.u8()
        self.boneType = f.u8()
        end = f.tell()
        if(self.boneType == 11):#Some silly stuff with GC (NO ENDIAN SWAPIN)
            f.seek(start+4)
            self.swing_backup = f.read(12)
            f.seek(rotstart)
            for x in range(2):
                self.rotfix.append(f.u16())
            self.rotfix2 = f.read(8)
            f.seek(end)
        if(self.BoneNameOffset):
            if(isSC3):
                self.Name = f.getStringSpecal(self.BoneNameOffset)
            else:
                self.Name = f.getString(self.BoneNameOffset)
    def write(self,f):
        if(self.boneType == 11):
            f.f32(self.EndPositionXYZScale[0])
            f.write(self.swing_backup)
        else:
            f.f32_4(self.EndPositionXYZScale)
        f.f32_4(self.StartPositionXYZScale)
        f.f32_3(self.Rotation)
        f.u32(self.BoneNameOffset)
        if(self.boneType == 11):
            for x in self.rotfix:
                f.u16(x)
            f.write(self.rotfix2)
        else:
            f.f32_3(self.unk0)
        f.u8(self.unk1)
        f.u8(self.BoneParentIdx)
        f.u8(self.BoneIdx)
        f.u8(self.boneType)
    