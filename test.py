import Lib.Model
import Lib.FormatRW as FRW
import sys

test = Lib.Model.VM()
f = open(sys.argv[1],'rb')
inFile = FRW.FRead(f,True)
test.read(inFile)
f.close()
del(inFile)

o = open(sys.argv[1]+".rewrote",'wb')
outFile = FRW.FWrite(o,True)

test.write(outFile)