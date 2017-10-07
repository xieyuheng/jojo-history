import jojo
import sys

m = jojo.load("./square.jo")
ds = jojo.run([4], [m.square])
print (ds)
