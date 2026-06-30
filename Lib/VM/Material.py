class Material(object):
    class MaterialMap(object):
        def __init__(self):
            self.offset = 0
            
            self.type = 1
            self.size = 36
            self.value = [0.0]*8
        def read(self,f):
            self.offset = f.tell()
            self.type = f.u16()
            self.size = f.u16()
            self.value = []
            for x in range(int((self.size - 4)/4)):
                self.value.append(f.f32())
        def write(self,f):
            f.u16(self.type)
            f.u16(self.size)
            for x in self.value:
                f.f32(x)
    def __init__(self):
        self.textureOffset = 0

        self.Type = 0
        self.unk1 = 0
        self.unk2 = 0
        self.CullMode = 0
        self.OpacitySrc = 0
        self.TextureIdx0 = 0
        self.TextureIdx1 = None
        self.TextureIdx2 = None
        self.TextureMap0 = None
        self.TextureMap1 = None
        self.TextureMap2 = None
        self.AmbientRGBA = [0.0]*4
        self.DiffuseRGBA = [1.0]*4
        self.SpecularRGBA = [0.2,0.2,0.2,20.0]
    def calc_texture_index(self,offset,isCube=False):
        idx = None
        if(offset>self.textureOffset):#0 just means there is no index
            rel = offset - (self.textureOffset + 0x14)#Skip to where the vxt is and the header
            div = 0x24
            if(isCube):
                rel-=4
                div = 0x44
            idx = int(rel/div)
        return idx
    def write_texture_offset(self,indx,isCube=False):
        if(indx is None):
            return 0
        else:
            muit = 0x24
            if(isCube):
                muit = 0x44
            return (self.textureOffset + (indx * muit))
    
    def read(self,f):
        value = f.u32()
        self.Type = value & 0xFF
        self.unk1 = (value>>8) & 0xFF
        self.unk2 = (value>>16) & 0xFF
        self.CullMode = (value>>24) & 0xFF
        self.OpacitySrc = f.u32()
        self.TextureIdx0 = self.calc_texture_index(f.u32())
        self.TextureIdx1 = self.calc_texture_index(f.u32())
        self.TextureIdx2 = self.calc_texture_index(f.u32())
        map0 = f.u32()
        if(map0>0):
            self.TextureMap0 = self.MaterialMap()
            ret = f.tell()
            f.seek(map0)
            self.TextureMap0.read(f)
            f.seek(ret)
        map1 = f.u32()
        if(map1>0):
            self.TextureMap1 = self.MaterialMap()
            ret = f.tell()
            f.seek(map1)
            self.TextureMap1.read(f)
            f.seek(ret)
        map2 = f.u32()
        if(map2>0):
            self.TextureMap2 = self.MaterialMap()
            ret = f.tell()
            f.seek(map2)
            self.TextureMap2.read(f)
            f.seek(ret)
        self.AmbientRGBA = f.f32_4()
        self.DiffuseRGBA = f.f32_4()
        self.SpecularRGBA = f.f32_4()
    def write(self,f):
        value = self.Type | (self.unk1 << 8) | (self.unk2 << 16) | (self.CullMode<<24)
        f.u32(value)
        f.u32(self.OpacitySrc)
        f.u32(self.write_texture_offset(self.TextureIdx0))
        f.u32(self.write_texture_offset(self.TextureIdx1))
        f.u32(self.write_texture_offset(self.TextureIdx2))
        if self.TextureMap0 is  None:
            f.u32(0)
        else:
            f.u32(self.TextureMap0.offset)

        if self.TextureMap1 is  None:
            f.u32(0)
        else:
            f.u32(self.TextureMap1.offset)
        
        if self.TextureMap2 is  None:
            f.u32(0)
        else:
            f.u32(self.TextureMap2.offset)
        f.f32_4(self.AmbientRGBA)
        f.f32_4(self.DiffuseRGBA)
        f.f32_4(self.SpecularRGBA)
