import socket
import threading
import wave
import pyaudio
import time
import logging

logging.basicConfig(filename = 'client.log', level = logging.DEBUG)

class user:
    def __init__(self, ip, port):
        '''Constructor function, reset all vars'''

        self.IP = ip
        self.PORT = port

        self.isExit = False

        self.my_socket = socket.socket()
        self.serverUDP = 0

        self.name = ""
        self.rate =  0
        self.channels = 0
        self.allFrames = 0

        self.frames = []
        self.save = []

        self.isEndLoad = False
        self.isEndPlay = False
        self.stopRun = False

    def start(self):
        '''Activate the client'''

        user.connectServer(self)

        while True:
            self.name = user.GetName(self)
            self.myPort = user.GetPortUDP(self)
            user.connectServerUDP(self)
            user.GetInfoSong(self)
            user.GetSong(self)


    def connectServer(self):
        '''Connecting to server (TCP)'''

        self.my_socket.connect((self.IP, self.PORT))

    def GetPortUDP(self):
        '''Getting from port to udp'''

        PORT_UDP = 0
        status = int(self.my_socket.recv(3).decode())
        PORT_UDP = int(self.my_socket.recv(5).decode())
        return PORT_UDP

    def GetInfoSong(self):
        '''Receives information about the song from the server'''

        lenRate = int(self.my_socket.recv(1).decode())
        self.rate = int(self.my_socket.recv(lenRate).decode()) * 1

        lenChannels = int(self.my_socket.recv(1).decode())
        self.channels = int(self.my_socket.recv(lenChannels).decode())

        lenFrames = int(self.my_socket.recv(2).decode())
        self.allFrames = int(self.my_socket.recv(lenFrames).decode())


    def GetName(self):
        '''Gets the song name from the user'''

        filename = input("Enter a name of song: ")
        # filename = "tg"
        Msg = str(len(filename)).zfill(3) + filename
        self.my_socket.send(("200" + Msg).encode('UTF-8'))
        self.stopRun = False

        return filename

    def connectServerUDP(self):
        '''Connecting to server (UDP)'''

        self.serverUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        t1 = time.time()
        t2 = t1 + 1

        while t1 < t2:
            t1 = time.time()

        # print("hhh")

        for i in range(1000):
            self.serverUDP.sendto(b'a', (self.IP, self.myPort))


    def GetSong(self):
        '''Gets and plays the song'''

        CHUNK = 1024
        FORMAT = pyaudio.paInt16

        p = pyaudio.PyAudio()

        stream = p.open(format = FORMAT,
                        channels = self.channels,
                        rate = self.rate,
                        output = True,
                        frames_per_buffer = CHUNK,
                        )

        threadGetDataSong = threading.Thread(target = user.GetDataSong, args=(self, CHUNK))
        threadPlaySong = threading.Thread(target = user.playSong, args=(self, stream, CHUNK))
        #
        # threadinput = threading.Thread(target = user.inputs, args=(self,))# stop the song
        # threadinput.start()

        threadPlaySong.setDaemon(True)
        threadGetDataSong.setDaemon(True)

        threadGetDataSong.start()
        threadPlaySong.start()

        threadGetDataSong.join()
        threadPlaySong.join()

    def inputs(self):
        '''Stops the song'''

        self.stopRun = False
        print("enter to stop: ")
        while True:
            input("")
            self.stopRun = not self.stopRun



    def GetDataSong(self, CHUNK):
        '''Getting the song from the server'''

        sums = 0
        max = self.allFrames // self.rate
        secondSong = 0
        sum1 = 0
        # while True:#???
        while secondSong < max:
            # print("ppp1")
            soundData, addr = self.serverUDP.recvfrom(CHUNK * self.channels * 2)
            # print("ppp2")
            sums += len(soundData)
            self.frames.append(soundData)
            self.save.append(soundData)

            logging.debug(f'{len(self.frames)}, {sums}, {time.time()}')
            secondSong = sums / (self.channels * self.rate * 2)
            sum1 += 1

            print("a", secondSong, sum1)
        print("bka2")



        self.serverUDP.close()

    def playSong(self, stream, CHUNK):
        '''Playing the song'''

        sums = 0
        secondSong = 0

        max = self.allFrames // self.rate
        while secondSong < max - 1:
        # while True:
            # logging.debug(f'{len(self.frames)}, {sums}, {time.time()}')
            if len(self.frames) > 0:
                data = self.frames.pop(0)
                sums += len(data)
                stream.write(data, CHUNK)

                while self.stopRun:
                    pass

                secondSong = sums / (self.channels * self.rate * 2)
        print("bka1")
