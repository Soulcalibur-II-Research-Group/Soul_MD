import Lib.Model
import Lib.FormatRW as FRW
import sys

test = Lib.Model.VM()
f = open(sys.argv[1],'rb')
inFile = FRW.FRead(f,True)
test.read(inFile)