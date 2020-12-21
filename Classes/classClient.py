import socket
import threading
import wave
import pyaudio
import time
import logging

# logging.basicConfig(filename = 'server.log', level = logging.DEBUG)

class client:
    #class vars
    dictPort = {"0":0}

    def __init__(self, id, client_socket, client_address, ip ,port):
        '''Constructor function, reset all vars'''

        self.isExit = False
        self.isLogout = False
        self.ID = id
        self.client_socket = client_socket
        self.client_address = client_address

        self.IP_TCP_SERVER = ip
        self.PORT_TCP_SERVER = port
        self.UDP_SERVE = 0

        self.nameSong = ""
        self.channelsSong = 0
        self.rateSong = 0
        self.allFramesSong = 0
        self.lengthSong = 0

        self.serverUDP_thread = 0

        self.frames = []
        self.save = []


    def GetPort(self):
        '''Brings port and sends to client'''

        client.dictPort[self.ID] = self.PORT_TCP_SERVER + self.ID
        self.client_socket.send(("110" + str(client.dictPort[self.ID])).encode())
        return client.dictPort[self.ID]

    def recvClient(self):
        '''Listens to client requests (TCP)'''

        data = ""
        while not self.isExit and not self.isLogout:
            try:
                data = self.client_socket.recv(1).decode()
            except:
                print("logout")
                self.isLogout = True

            if data == "":
                print("logout")
                self.isLogout = True
            else:
                if data == "2":
                    data += self.client_socket.recv(2).decode()
                    if data == "200":
                        lenName = int(self.client_socket.recv(3).decode())
                        filename = self.client_socket.recv(lenName).decode()
                        self.nameSong = filename
                        # print("uuu")
                        self.MyPortUDP = client.GetPort(self)
                        client.GetSongClient(self)

                elif data == "3":
                    pass


    def start(self):
        '''Enables client listening'''

        self.recvClientThread = threading.Thread(target = client.recvClient, args = (self,))
        self.recvClientThread.start()

        # while True:
        # self.MyPortUDP = client.GetPort(self)
        # client.GetSongClient(self)

    def GetSongClient(self):
        '''Sending song information to client'''

        while self.nameSong == "":
            pass

        wf = wave.open(self.nameSong + ".wav", 'rb')
        self.channelsSong = wf.getnchannels()
        self.rateSong = wf.getframerate()
        self.allFramesSong = wf.getnframes()

        msgStr = str(len(str(self.rateSong))) + str(self.rateSong)
        msgStr += str(len(str(self.channelsSong))) + str(self.channelsSong)
        msgStr += str(len(str(self.allFramesSong))).zfill(2) + str(self.allFramesSong)
        self.client_socket.send(msgStr.encode())

        self.serverUDP_thread = threading.Thread(target = client.SendDataSong, args = (self,))
        self.serverUDP_thread.setDaemon(True)
        self.serverUDP_thread.start()

    def SendDataSong(self):
        '''Sends the song to a client'''

        p = pyaudio.PyAudio()
        filename = self.nameSong + ".wav"

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        self.allFramesSong
        #
        # wf = wave.open(filename, 'rb')
        #


        loadDataThread = threading.Thread(target = client.loadData, args = (self, CHUNK, filename))
        loadDataThread.setDaemon(True)
        loadDataThread.start()

        client.openServerUDP(self)

    def openServerUDP(self):
        '''Opens the udp server'''

        self.UDP_SERVE = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UDP_SERVE.bind((self.IP_TCP_SERVER, self.MyPortUDP))
        message, address = self.UDP_SERVE.recvfrom(1)

        sum = 0
        sum1 = 0

        isEnd = False

        p = pyaudio.PyAudio()
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        stream = p.open(format = FORMAT,
                        channels = self.channelsSong,
                        rate = self.rateSong,
                        output = True,
                        frames_per_buffer = CHUNK,
                        )

        max = self.allFramesSong // self.rateSong
        secondSong = 0
        while secondSong < max:

            # logging.debug(f'{len(self.frames)}, {sum}, {time.time()}')
            if len(self.frames) > 0:
                data = self.frames.pop(0)
                # stream.write(data, CHUNK)

                for i in range(200000):
                    pass

                self.UDP_SERVE.sendto(data, address)#???

                sum += len(data)
                secondSong = sum / (self.channelsSong * self.rateSong * 2)
                sum1 += 1
                print(secondSong, sum1)

        # self.UDP_SERVE.close()
        print("aka1")

    def loadData(self, CHUNK, filename):
        '''Loading song to server'''

        isEnd = False
        sum = 0
        wf = wave.open(filename, 'rb')
        secondSong = 0

        max = self.allFramesSong // self.rateSong

        while secondSong < max:
            data = wf.readframes(CHUNK)
            self.frames.append(data)
            sum += len(data)
            secondSong = sum / (self.channelsSong * self.rateSong * 2)
