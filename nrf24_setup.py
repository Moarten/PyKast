from nrf24 import NRF24
#NRF24 stuff
pipes = [[0xf0, 0xf0, 0xf0, 0xf0, 0xe1], [0xf0, 0xf0, 0xf0, 0xf0, 0xd2]]

radio = NRF24()
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

