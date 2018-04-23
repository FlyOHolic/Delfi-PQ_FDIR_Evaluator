from controllerInterface import controllerInterface
import time
import numpy
from matplotlib import pyplot

controllerPort = '/dev/ttyACM1'
resetPort = '/dev/ttyACM2'
ctr = controllerInterface(controllerPort, resetPort)

markerbegin = 536870912

searchspace = 1048576
searchspace = 64000
looprange = 20

locnumber = 5
numpy.random.seed(5)
floatarray = numpy.around(markerbegin + searchspace * numpy.random.rand(1, locnumber))
randloc = floatarray.astype(int).tolist()[0]
randloc.append( markerbegin )   #Include start of memory to search -> known failure locations
randloc.append( 536875136 )     #Include know data location to search
randloc.sort()
fulllist = []

for i in randloc:
    for j in range(0, looprange * 4, 4):
        addition = i + j
        fulllist.append(addition)

flipLocations = [3]

starttime = time.time()

resultList = []
print "Start FDIR verification"
for markerloc in fulllist:
    for flipLocation in flipLocations:
        print markerloc - markerbegin, flipLocation

        m1 = ctr.move( markerloc )
        o1 = ctr.output()
        f1 = ctr.flip( flipLocation )
        o2 = ctr.output()
        time.sleep(0.1)

        dataVerified = ctr.verifyData()

        if ( not m1 ):
            faultType = 3
        elif ( not f1 ):
            faultType = 1
        elif ( markerloc != o1[2] or markerloc != o2[2] ):
            faultType = 4
        elif ( not dataVerified ):
            faultType = 2
            #ctr.flip( flipLocation )
            ctr.reset()
        else:
            faultType = 0
        ##faultType:
        #   0: No error detected
        #   1: Lockup - no reaction from controller after a flip
        #   2: Data corruption - reference states do not equal their preset values
        #   3: Move failure -> Locks controller state when moving to specific pointers
        #   4: Move fault -> pointer is not moved to the correct state

        resultList.append( (markerloc, flipLocation, faultType) )
        print m1, o1, f1, o2, dataVerified
        #print ctr.serialLog
#print resultList

print "FDIR-Verification done. Runtime: " + str(time.time() - starttime) + " s"
print resultList
numberOfFailureTypes = 5
thefile = open('output.txt', 'w')
failureCount = [0 for i in range(numberOfFailureTypes)]
for result in resultList:
    thefile.write( str(result[0]) + ', ' + str(result[1]) + ', ' + str(result[2]) + '\n' )
    failureCount[ result[2] ] += 1

thefile.close()

legend = ['None', 'Lockup', 'Data corruption', 'Move failure', 'Move fault']
legend = [legend[i] + " " + str( failureCount[i]) for i in range(numberOfFailureTypes)]
pyplot.pie(failureCount, labels = legend)
pyplot.title("Failure distributions")
pyplot.show()