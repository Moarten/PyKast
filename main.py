#!/usr/bin/python
"""Main python file."""

from nrf24 import NRF24
import MySQLdb as mdb
import time
#import sys
#from time import gmtime, strftime

CHARS_TO_REMOVE = ['*', '#']
SENSORS = {'A': 0, 'O': 1}
RADIO = NRF24()
CON = mdb.connect('localhost', 'koelkast', 'amstelbier', 'koelkast')

def radio_setup():
    pipes = [[0xf0, 0xf0, 0xf0, 0xf0, 0xe1], [0xf0, 0xf0, 0xf0, 0xf0, 0xd2]]
    RADIO.begin(0, 0, 25, 18)
    RADIO.setRetries(15, 15)
    RADIO.setPayloadSize(64)
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

def mysql_execute(sql):
    with CON:
        cur = CON.cursor()
        result = cur.execute(sql)
        return cur.rowcount

def call_back(msg):
    RADIO.stopListening()
    RADIO.write(msg)
    RADIO.startListening()

def update_database(received):
    """komt nog wel"""
    received = received.split("#")
    received = received[0].translate(None, ''.join(CHARS_TO_REMOVE))
    exploded = received.split("@")
    for i in range(0, len(exploded)):
        values = exploded[i].split("&")
        if (values[0] == "A") or (values[0] == "O"):
            #ambient or object temp
            print values[1]
            print len(values[1])
            mysql_execute("INSERT INTO sensor_data SET sensorID = " + str(SENSORS[values[0]]) + ", value = " + values[1])
            call_back("*OK#")
        elif values[0] == "P":
            #product id
            if (len(exploded) > (i + 2)) and (exploded[i + 1][0] == "D") and (exploded[i + 2][0] == "U"):
                product_id = '-'.join(exploded[i].split("&")[1:])
                exp_date = '-'.join(exploded[i + 1].split("&")[1:])
                unique_id = '-'.join(exploded[i + 2].split("&")[1:])
                print product_id
                print exp_date
                print unique_id
                i += 2

                product_exists = mysql_execute("SELECT id FROM products WHERE rfid_key = '" + product_id + "'")
                if (product_exists == 0):
                    call_back("*NOTINDATABASE#")
                    continue
                if (exp_date == "0-0-0"):
                    exp_date = "NULL" 

                product_already_in_db = mysql_execute("SELECT id FROM productsFridge WHERE unique_id = '" + unique_id +"'")
                if (product_already_in_db > 0):
                    mysql_execute("DELETE FROM productsFridge WHERE unique_id = '" + unique_id + "'")
                else:
                    mysql_execute("INSERT INTO productsFridge SET product_id = (SELECT id FROM products WHERE rfid_key = '" + product_id + "'), exp_date = '" + exp_date + "', unique_id = '" + unique_id + "'")
                call_back("*OK#")
            else:
                print "ERROR, EXPECTING EXPIRATION DATE AFTER PRODUCT ID"
                call_back("*INCORRECTSTRING#")

def main():
    """The main function."""
    radio_setup()
    update_database("*P&6&0&0@D&15&10&15@U&3#")
    update_database("*A&12.34@O&26.59#")
    while True:
        RADIO.startListening()
        time.sleep(1)
        recv_buffer = []
        RADIO.read(recv_buffer)
        out = ''.join(chr(i) for i in recv_buffer)
        test = str(recv_buffer)
        test.strip()
        if (out[0] == '*') and ((out[len(test) - 97]) == '#') and ('&' in out):
            update_database(out)
   #         call_back("*OK#")
   #    else:
   #       call_back("*slagroomsoesjses#")

    if CON:
        CON.close()

if __name__ == "__main__":
    main()
