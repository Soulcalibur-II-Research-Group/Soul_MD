class WeightTable(object):
        class BufferColorUV(object):
            def __init__(self):
                self.RGBA = [255]*4
                self.UV = [0.0]*2
            def read(self,f):
                self.RGBA = f.u8_4()
                self.UV = f.f32_2()
            def write(self,f):
                f.u8_4(self.RGBA)
                f.f32_2(self.UV)
        class BufferScaleVertex(object):
            def __init__(self):
                self.Position = [0.0] * 3
                self.PositionScale = 1.0
                self.Normal = [0.0] * 3
                self.NormalScale = 1.0
            def read(self,f):
                self.Position = f.f32_3()
                self.PositionScale = f.f32()
                self.Normal = f.f32_3()
                self.NormalScale = f.f32()
            def gc_read_pos(self,f):
                self.Position = f.f32_3()
                self.PositionScale = f.f32()
            def gc_read_nor(self,f):
                self.Normal = f.f32_3()
            def write(self,f):
                f.f32_3(self.Position)
                f.f32(self.PositionScale)
                f.f32_3(self.Normal)
                f.f32(self.NormalScale)
        class WeightDef(object):
            def __init__(self):
                self.Pos = [0.0]*3
                self.bWgt = 1.0
                self.Nor = [0.0]*3
                self.bIdx = 0
                self.stat = 0
            def read(self,f):
                self.Pos = f.f32_3()
                self.bWgt = f.f32()
                self.Nor = f.f32_3()
                self.bIdx = f.u8()
                self.stat = f.u8()
                f.seek(2,1)
            def read_gc(self,f):
                self.Pos = f.g16_3()
                self.bWgt = f.g16()
                self.Nor = f.g16_3()
                self.stat = f.u8()
                self.bIdx = f.u8()
            def as_bytes(self):
                return struct.pack('fffffffBBH',self.Pos[0],self.Pos[1],self.Pos[2],self.bWgt,self.Nor[0],self.Nor[1],self.Nor[2],self.bIdx,self.stat,0)
            def write(self,f):
                f.f32_3(self.Pos)
                f.f32(self.bWgt)
                f.f32_3(self.Nor)
                f.u8(self.bIdx)
                f.u8(self.stat)
                f.u16(0)
        def __init__(self):
            self.VertCounts = [0]*4
            self.WeightBufferOffset = 0
            self.VertBuffer1Offset = 0
            self.VertBuffer2Offset = 0
            self.VertBuffer0Offset = 0 # Not found in this originaly(Bringing it in from outside)
            self.WeightBuffer = [] #Flat with dynamic sizing 1,2,3,4,5,6, .......
            self.VertexBuff0 = [] # Color and UV
            self.VertexBuff1 = [] # IDK yet
            self.VertexBuff2 = [] # ^
        def dynaSize(self):
                totalSize = 0
                for x in self.WeightBuffer:
                    for y in x:
                        totalSize+=0x20
                return totalSize
        def read_gc(self,f):
            totalVertCount = 0
            for x in range(4):
                self.VertCounts[x] = f.u32()
                totalVertCount += self.VertCounts[x]
            WeightBufferOffset = f.u32()
            VertPosBuffer1Offset = f.u32()
            VertPosBuffer2Offset = f.u32()
            VertNorBuffer1Offset = f.u32()
            VertNorBuffer2Offset = f.u32()
            f.seek(WeightBufferOffset)
            high = 1
            for x in range(self.VertCounts[0]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read_gc(f)
                    arr.append(a)
                self.WeightBuffer.append(arr)
            high = 2
            for x in range(self.VertCounts[1]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read_gc(f)
                    arr.append(a)
                self.WeightBuffer.append(arr)
            high = 3
            for x in range(self.VertCounts[2]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read_gc(f)
                    arr.append(a)

                self.WeightBuffer.append(arr)
            high = 4
            for x in range(self.VertCounts[3]):
                arr = []
                total_unbinded = 0
                where_zero = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read_gc(f)
                    if(a.bWgt<=0.0):
                        total_unbinded += 1
                        where_zero.append(y)
                    arr.append(a)
                    if(a.stat == 1):
                        high +=1
                for y in where_zero:
                    sharedWgt = 0.0
                    for z in range(len(arr[y:])):
                        valy = arr[y+z]
                        if(valy.bWgt>0):
                            arr[y+z].bWgt *= 0.5
                            arr[y].bWgt = arr[y+z].bWgt
                            break
                        print(valy.bWgt)


                    print("Zero Bind at %i" % y)

                self.WeightBuffer.append(arr)
            posStride = 0
            norStride = 0
            for x in range(totalVertCount):
                f.seek(VertPosBuffer1Offset+posStride)
                a = self.BufferScaleVertex()
                a.gc_read_pos(f)
                posStride+= 0x10
                f.seek(VertNorBuffer1Offset+posStride)
                a.gc_read_nor(f)
                norStride+= 0x10
                self.VertexBuff1.append(a)
            posStride = 0
            norStride = 0
            for x in range(totalVertCount):
                f.seek(VertPosBuffer2Offset+posStride)
                a = self.BufferScaleVertex()
                a.gc_read_pos(f)
                posStride+= 0x10
                f.seek(VertNorBuffer2Offset+norStride)
                a.gc_read_nor(f)
                norStride+= 0x10
                self.VertexBuff2.append(a)
        def read(self,f):
            totalVertCount = 0
            for x in range(4):
                self.VertCounts[x] = f.u32()
                totalVertCount += self.VertCounts[x] 
            self.WeightBufferOffset = f.u32()
            self.VertBuffer1Offset = f.u32()
            self.VertBuffer2Offset = f.u32()
            sizeOfColor = (totalVertCount * 0xC) +(0x10 - ((totalVertCount * 0xC) % 0x10))
            #self.VertBuffer0Offset = self.VertBuffer1Offset - sizeOfColor
            f.seek(self.WeightBufferOffset)
            high = 1
            for x in range(self.VertCounts[0]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read(f)
                    arr.append(a)
                self.WeightBuffer.append(arr)
            high = 2
            for x in range(self.VertCounts[1]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read(f)
                    arr.append(a)
                self.WeightBuffer.append(arr)
            high = 3
            for x in range(self.VertCounts[2]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read(f)
                    arr.append(a)

                self.WeightBuffer.append(arr)
            high = 4
            for x in range(self.VertCounts[3]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read(f)
                    arr.append(a)
                    if(a.stat == 1):
                        high +=1
                self.WeightBuffer.append(arr)
            f.seek(self.VertBuffer1Offset)
            for x in range(totalVertCount):
                a = self.BufferScaleVertex()
                a.read(f)
                self.VertexBuff1.append(a)
                
            f.seek(self.VertBuffer2Offset)
            for x in range(totalVertCount):
                a = self.BufferScaleVertex()
                a.read(f)
                self.VertexBuff2.append(a)
            if(self.VertBuffer0Offset):
                f.seek(self.VertBuffer0Offset)
                for x in range(totalVertCount):
                    a = self.BufferColorUV()
                    a.read(f)
                    self.VertexBuff0.append(a)
        def write(self,f):
            for x in self.VertCounts:
                f.u32(x)
            f.u32(self.WeightBufferOffset )
            f.u32(self.VertBuffer1Offset)
            f.u32(self.VertBuffer2Offset)
    