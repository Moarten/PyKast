#!/usr/bin/python
"""Main python file."""

from nrf24 import NRF24
import MySQLdb as mdb
import sys
import time
#from time import gmtime, strftime

CHARS_TO_REMOVE = ['*', '#']
SENSORS = {'T': 1, 'H': 2}
RADIO = NRF24()
CON = mdb.connect('localhost', 'koelkast', 'amstelbier', 'koelkast')

def radio_setup():
    """The function for setting up the radio."""
    pipes = [[0xf0, 0xf0, 0xf0, 0xf0, 0xe1], [0xf0, 0xf0, 0xf0, 0xf0, 0xd2]]
    RADIO.begin(0, 0, 25, 18)
    RADIO.setRetries(15, 15)
    RADIO.setPayloadSize(32)
    RADIO.setChannel(0x4c)
    RADIO.setDataRate(NRF24.BR_250KBPS)
    RADIO.setPALevel(NRF24.PA_MAX)
    RADIO.openWritingPipe(pipes[0])
    RADIO.openReadingPipe(1, pipes[1])
    RADIO.startListening()
    RADIO.stopListening()
    RADIO.write("*OK#")
    RADIO.printDetails()
    RADIO.startListening()
    return

def explode_string(received):
    """The function for exploding a string."""
    received = received.translate(None, ''.join(CHARS_TO_REMOVE))
    exploded = received.split("&")
    print received
    with CON:
        cur = CON.cursor()
        for x in xrange(len(exploded)/2):
            sql = "INSERT INTO sensor_data SET sensorID = %s, value = %s"
            cur.execute(sql, (SENSORS[exploded[x+x]], exploded[x+x+1]))
    return

def call_back(msg):
    """The function for calling back."""
    RADIO.stopListening()
    RADIO.write(msg)
    RADIO.startListening()
    return

def update_database(received):
    """The function for updating the database."""
    received = received.translate(None, ''.join(CHARS_TO_REMOVE))
    exploded = received.split("@")
    for i in range(1, len(exploded)):
        values = exploded[i].split("&")
        if (values[0] == "A"):
            #ambient temp
            print "A"
        elif (values[0] == "O"):
            #object temp
            print "O"
        elif (values[0] == "P"):
            #product id
            print "P"
    return

def main():
    """The main function."""
    radio_setup()
    rvcd = explode_string("*T&26.00&H&33.00#", rvcd)
    index = 0
    while True:
        #pipe = [0]
        RADIO.startListening()
        time.sleep(1)
        recv_buffer = []
        RADIO.read(recv_buffer)
        out = ''.join(chr(i) for i in recv_buffer)
        test = str(recv_buffer)
        test.strip()
        index += 1
        if (out[0] == '*') and ((out[len(test) - 97]) == '#') and ('&' in out):
            update_database(out)
            call_back("*OK#")
   #    else:
   #       call_back("*slagroomsoesjses#")

    if CON:
        CON.close()

if __name__ == "__main__":
    main()
