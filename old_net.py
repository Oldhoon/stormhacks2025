import pygame
import sys
from pygame.locals import *
from knight import Knight
import struct
import threading
import socket
import time

class Arena:
    def __init__(self, host='10.38.15.164', port=65469):
        pygame.init()
        self.host = host
        self.port = port
        self.kill = False
        
        self.socket = None
        
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Leetcode Arena")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.frames = self.fps / 12
        
        self.background = pygame.image.load(r"assets/cyberpunk-street-files/cyberpunk-street-files/Assets/Version 1/PNG/cyberpunk-street.png").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        
        # self.knight = Knight()
        
        self.running = True
        
        # self.
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.kill = True
                self.running = False
                pygame.quit()
                sys.exit()

    
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        
        
        pygame.display.update()
        pygame.display.flip()
        
    def deserialize(self, data):
        update_format = 'BB9s'
        if len(data) >= struct.calcsize(update_format):
            turn, winner, board = struct.unpack_from('BB9s', data, 0)
            
        
    def run_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            s.connect((self.host, self.port))
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            s.settimeout(1)
            print('connected', s)
            self.socket = s
            while not self.kill:
                try:
                    data = self.socket.recv(4096)
                    if len(data):
                        self.deserialize(data)
                except socket.timeout:
                    pass
                time.sleep(0.001)
            
            
    def update():
        pass
    
    def run(self):
        threading.Thread(target=self.run_listener).start()
        while self.running:
            self.handle_events()
            # self.update()
            self.draw() 
            self.clock.tick(self.fps)

Arena().run()