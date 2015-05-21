#!/usr/bin/python
"""Main python file."""

from nrf24 import NRF24
import MySQLdb as mdb
import sys
import time
#from time import gmtime, strftime

CHARS_TO_REMOVE = ['*', '#']
SENSORS = {'A': 0, 'O': 1}
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

def mysql_insert(sql):
    """The function that is no longer for exploding a string."""
    with CON:
        cur = CON.cursor()
        cur.execute(sql)
    return

def call_back(msg):
    """The function for calling back."""
    RADIO.stopListening()
    RADIO.write(msg)
    RADIO.startListening()
    return

def update_database(received):
    """The function not for updating the database."""
    received = received.translate(None, ''.join(CHARS_TO_REMOVE))
    exploded = received.split("@")
    for i in range(0, len(exploded)):
        values = exploded[i].split("&")
        if ((values[0] == "A") or (values[0] == "O")):
            #ambient or object temp
            print values[0] + values[1]
            mysql_insert("INSERT INTO sensor_data SET sensorID = " + str(SENSORS[values[0]]) + ", value = " + values[1])
        elif (values[0] == "P"):
            #product id
            if ( (len(exploded) > (i + 1)) and (exploded[i + 1][0] == "D")):
                product_id = '-'.join(exploded[i].split("&")[1:])
                print product_id
                i += 1
                exp_date = '-'.join(exploded[i].split("&")[1:])
                print exp_date
                mysql_insert("INSERT INTO productsFridge SET product_id = (SELECT id FROM products WHERE rfid_key = '" + product_id + "'), exp_date = '" + exp_date + "', unique_id = " + str(2))
            else:
                print "ERROR, EXPECTING EXPIRE DATE AFTER PRODUCT ID"
    return

def main():
    """The main function."""
    radio_setup()
    update_database("*P&1&0&0@D&15&10&15#")
    update_database("*A&12.34@O&98.76#")
    #index = 0
    while True: 
        RADIO.startListening()
        time.sleep(1)
        recv_buffer = []
        RADIO.read(recv_buffer)
        out = ''.join(chr(i) for i in recv_buffer)
        test = str(recv_buffer)
        test.strip()
        #index += 1
        if (out[0] == '*') and ((out[len(test) - 97]) == '#') and ('&' in out):
            update_database(out)
            call_back("*OK#")
   #    else:
   #       call_back("*slagroomsoesjses#")

    if CON:
        CON.close()

if __name__ == "__main__":
    main()
