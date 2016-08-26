import actool
import welford
import time
import struct
import threading

ac1 = '192.168.2.2'
ac2 = '192.168.3.2'
acip = '192.168.2.2'

print "Aircard IP:", acip
# OID = 'AIRCARD_SIG_STRENGTH'
OID = 'AIRCARD_ASP_FILTERED_SINR'
#OID = 'AIRCARD_PILOT_PN_ASP'

actool.setup()

def runtest(n, acip, wbl):
    third = acip.split('.')[2]
    fbe = open('ac.{}.BE.dat'.format(third), 'w')
    fle = open('ac.{}.LE.dat'.format(third), 'w')
    for i in range(n):
        d = actool.query_oids(acip, [actool.oids[OID]])[0]
        raw = bytes(d.get('raw', ''))
        if not raw:
            time.sleep(0.5)
            continue

        a1 = struct.unpack('<'+'H'*(len(raw)/2), raw) # little-endian
        w1 = welford.Welford()
        for x in a1:
            w1.update(x / 512.)
            print >>fle, x / 512.
    
        a2 = struct.unpack('>'+'H'*(len(raw)/2), raw) # big-endian
        w2 = welford.Welford()
        for x in a2:
            w2.update(x / 512.)
            print >>fbe, x / 512.

        wbl.update(w2.get_var() - w1.get_var())

        print acip, 'LE', ['{:04x}'.format(x) for x in a1], w1.get_var()
        print acip, 'BE', ['{:04x}'.format(x) for x in a2], w2.get_var()
        print acip, 'BE-LE =', w2.get_var() - w1.get_var()
        print
        time.sleep(0.5)
    return wbl.M

#N = 480
N = 120
wbl1 = welford.Welford() # use for avg of BE-LE, aircard 1
wbl2 = welford.Welford() # use for avg of BE-LE, aircard 2
t1 = threading.Thread(target=runtest, args=(N, ac1, wbl1))
time.sleep(0.25)
t2 = threading.Thread(target=runtest, args=(N, ac2, wbl2))
t1.start()
t2.start()
t1.join()
t2.join()
metric1 = wbl1.M
metric2 = wbl2.M
print "ac1 big-endian var - little-endian var:", metric1
print "ac2 big-endian var - little-endian var:", metric2
