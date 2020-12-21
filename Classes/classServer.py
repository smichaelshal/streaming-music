import socket
import threading
import wave
import pyaudio
import time

from Classes.classClient import client

class server:
    #class vars

    def __init__(self, ip, port):
        '''Constructor function, reset all vars'''
        #Const
        self.IP = ip
        self.PORT = port

        #Vars
        self.isExit = False
        self.sumClient = 0
        self.dictClientId = {}
        self.dictThreadsId = {}


    def exit(self):
        '''Closes the server'''

        self.isExit = True

    def start(self):
        '''Start the server'''

        GetClientthread = threading.Thread(target = server.GetClient, args = (self,))
        GetClientthread.start()

    def GetClient(self):
        '''Listens and receives new clients'''

        serverTCP = socket.socket()
        serverTCP.bind((self.IP, self.PORT))
        serverTCP.listen(1)
        while not self.isExit:
            (client_socket, client_address) = serverTCP.accept()
            self.sumClient += 1

            self.dictThreadsId[self.sumClient] = threading.Thread(target = server.startClient, args = (self, client_socket, client_address))
            self.dictThreadsId[self.sumClient].setDaemon(True)
            self.dictThreadsId[self.sumClient].start()

    def startClient(self, client_socket, client_address):
        '''Operates clients'''

        tempClient = client(self.sumClient, client_socket, client_address, self.IP, self.PORT)
        self.dictClientId[self.sumClient] = tempClient
        tempClient.start()
