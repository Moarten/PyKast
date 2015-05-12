from nrf24 import NRF24
import MySQLdb as mdb
import sys
import time
from time import gmtime, strftime

charsToRemove = ['*','#']
sensors = {'T': 0, 'H': 1}
radio = NRF24()
#DB stuff
con = mdb.connect('localhost','koelkast','amstelbier','koelkast');

def radioSetup():
    pipes = [[0xf0, 0xf0, 0xf0, 0xf0, 0xe1], [0xf0, 0xf0, 0xf0, 0xf0, 0xd2]]    
    radio.begin(0, 0,25,18)
    radio.setRetries(15,15)
    radio.setPayloadSize(32)
    radio.setChannel(0x4c)
    radio.setDataRate(NRF24.BR_250KBPS)
    radio.setPALevel(NRF24.PA_MAX)
    radio.openWritingPipe(pipes[0])
    radio.openReadingPipe(1, pipes[1])
    radio.startListening()
    radio.stopListening()
    radio.write("*OK#")
    radio.printDetails()
    radio.startListening()
    return
	
def explodeString(received):
    received = received.translate(None, ''.join(charsToRemove))
    exploded = received.split("&")
    print received
    with con:
        cur = con.cursor()
        for x in xrange(len(exploded)/2):
            cur.execute("INSERT INTO sensor_data(sensorID, value) VALUES(%s, %s)",(sensors[exploded[x+x]],exploded[x+x+1]))
            print exploded[x+x+1]
    return

def callBack(msg):
    radio.stopListening()
    radio.write(msg)
    radio.startListening()
    return

def updateDB():
    return

def main():   
    radioSetup()
    explodeString("*T&26.00&H&33.00#")
    while True:
        pipe = [0]
        radio.startListening()
        time.sleep(1)
        recv_buffer = []
        radio.read(recv_buffer)
        out = ''.join(chr(i) for i in recv_buffer)
        test = str(recv_buffer)
        test.strip()
        print out;
        if ((out[0] == '*') and ((out[len(test) - 97]) == '#') and ('&' in out)):
           explodeString(out)
           callBack("*OK#")
   #    else:
   #       callBack("*slagroomsoesjses#")
    
    if con:
        con.close()

if __name__ == "__main__":
    main()
