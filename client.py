#!/usr/bin/python3

import math, os, time
import socket
import threading
from numpy import array
import pyaudio, audioop
from tkinter import *

chunk_size = 1024 # 512
audio_format = pyaudio.paInt16
channels = 1
rate = 48000

def CheckLoudHistory(hist):
    for i in hist: 
        if i > 30:
            return True
    return False

class Client:
    def __init__(self, ip, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        while 1:
            try:
                self.target_ip = ip
                self.target_port = port

                self.s.connect((self.target_ip, self.target_port))

                break
            except:
                print("Couldn't connect to server")

        # initialise microphone recording
        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True, frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)
        
        print("Connected to Server")

        # start threads
        receive_thread = threading.Thread(target=self.receive_server_data).start()
        sending_thread = threading.Thread(target=self.send_data_to_server).start()

    def receive_server_data(self):
        while True:
            try:
                if self.playing_stream.is_active():
                    try:
                        data = self.s.recv(512)
                        self.playing_stream.write(data)
                    except:
                        print('Lost connection')
            except OSError:
                print('restarting playing stream')
                time.sleep(0.3)
                self.playing_stream.close()
                self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)


    def send_data_to_server(self):
        loud_history = list()
        while True:
            try:
                if self.recording_stream.is_active():
                    try:
                        data = self.recording_stream.read(512)
                        rms = audioop.rms(data, 2)
                        loudness = 20 * math.log10(rms)
                        loud_history.append(loudness)
                        # os.system('cls')
                        print(round(loudness))
                        if loudness > 30 or CheckLoudHistory(loud_history[len(loud_history)-51:len(loud_history)-1]):
                            self.s.sendall(data)
                        if len(loud_history) > 5001: 
                            loud_history = loud_history[0:40]
                    except:
                        pass
            except OSError:
                print('restarting recording stream')
                time.sleep(0.3)
                self.recording_stream.close()
                self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)

if __name__ == '__main__':
    client = Client("37.143.12.148", 61616)
