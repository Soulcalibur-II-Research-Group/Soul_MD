class Header(object):
        def __init__(self):
            tmpOnC = {"offset":0,"count":0} #Intended to quick n dirty offset & count
            self.MAGIC = b'VMX.'
            self.Version = 4
            self.Endian = False #False LITTLE, True BIG
            #if(self.Version == 3):#(GC)PPC is Big Endian, (PS2)Mips & (Xbox)x86 is Little Endian
            self.textureOffsetPoint = 0x10
            self.textureCount = 0x13
            self.isLoaded = 0
            self.unk0 = 0
            self.ModelContent = 0
            self.MatricesInfo = tmpOnC.copy()
            self.Layer0Info = tmpOnC.copy()
            self.Layer1Info = tmpOnC.copy()
            self.Layer2Info = tmpOnC.copy()
            self.BoneInfo = tmpOnC.copy()
            self.MaterialsInfo = tmpOnC.copy()
            self.WeightTableCount = 0
            self.TextureTableOffset = 0
            self.TextureMapOffset = 0
            self.ukn_MatrixTableOffset = 0
            self.WeightTableOffset = 0
            self.ukn01_offset = 0
            self.BoneNameOffset = 0
            self.BoneHeaderOffset = 0
        def read(self,f):
            self.MAGIC = f.read(4)
            if(self.MAGIC == b'VMG.'):
                f.swapEndian()
                isCube = True
                self.Endian = True
            self.Version = f.u8()
            self.textureOffsetPoint = f.u8()
            self.textureCount = f.u8()
            self.isLoaded = f.u8()
            self.unk0 = f.u8()
            self.modelContent = f.u8()
            self.MatricesInfo['count'] = f.u16()
            self.Layer0Info['count'] = f.u16()
            self.Layer1Info['count'] = f.u16()
            self.Layer2Info['count'] = f.u16()
            self.BoneInfo['count'] = f.u16()
            self.MaterialsInfo['count'] = f.u16()
            self.WeightTableCount = f.u16()
            self.TextureTableOffset = f.u32()
            self.MaterialsInfo['offset'] = f.u32()
            self.TextureMapOffset = f.u32()
            self.MatricesInfo['offset'] = f.u32()
            self.ukn_MatrixTableOffset = f.u32()
            self.Layer0Info['offset'] = f.u32()
            self.Layer1Info['offset'] = f.u32()
            self.Layer2Info['offset'] = f.u32()
            self.WeightTableOffset = f.u32()
            self.ukn01_offset = f.u32()
            self.BoneInfo['offset'] = f.u32()
            self.BoneNameOffset = f.u32()
            self.BoneHeaderOffset = f.u32()
        def write(self,f):
            f.write(self.MAGIC)
            f.u8(self.Version)
            f.u8(self.textureOffsetPoint)
            f.u8(self.textureCount)
            f.u8(self.isLoaded)
            f.u8(self.unk0)
            f.u8(self.modelContent)
            f.u16(self.MatricesInfo['count'])
            f.u16(self.Layer0Info['count'])
            f.u16(self.Layer1Info['count'])
            f.u16(self.Layer2Info['count'])
            f.u16(self.BoneInfo['count'])
            f.u16(self.MaterialsInfo['count'])
            f.u16(self.WeightTableCount)
            f.u32(self.TextureTableOffset)
            f.u32(self.MaterialsInfo['offset'])
            f.u32(self.TextureMapOffset)
            f.u32(self.MatricesInfo['offset'])
            f.u32(self.ukn_MatrixTableOffset)
            f.u32(self.Layer0Info['offset'])
            f.u32(self.Layer1Info['offset'])
            f.u32(self.Layer2Info['offset'])
            f.u32(self.WeightTableOffset)
            f.u32(self.ukn01_offset)
            f.u32(self.BoneInfo['offset'])
            f.u32(self.BoneNameOffset)
            f.u32(self.BoneHeaderOffset)
        def __str__(self):
            rt = ""
            rt += str("Magic: %s\n" % self.MAGIC)
            rt += str("Ver: %i\n" % self.Version)
            rt += str("ModelContent: %i\n"%self.ModelContent)
            rt += str("Matrix count %i @ %s\n"%(self.MatricesInfo['count'],hex(self.MatricesInfo['offset'])))
            rt += str("Layer0Info count %i @ %s\n"%(self.Layer0Info['count'],hex(self.Layer0Info['offset'])))
            rt += str("Layer1Info count %i @ %s\n"%(self.Layer1Info['count'],hex(self.Layer1Info['offset'])))
            rt += str("Layer2Info count %i @ %s\n"%(self.Layer2Info['count'],hex(self.Layer2Info['offset'])))
            rt += str("BoneInfo count %i @ %s\n"%(self.BoneInfo['count'],hex(self.BoneInfo['offset'])))
            rt += str("MaterialsInfo count %i @ %s\n"%(self.MaterialsInfo['count'],hex(self.MaterialsInfo['offset'])))
            return rt
    