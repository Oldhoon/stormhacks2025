# TY KING https://www.youtube.com/watch?v=VvwLXnY-mKk
import socket
import threading
import struct
import time

class Server:
    def __init__(self, host = '127.0.0.1', port=67695):
        self.host = host
        self.port = port
        
        self.kill = False
        self.thread_count = 0
        
    def connection_listen_loop(self):
        self.thread_count += 1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            s.bind((self.host, self.port))
            
            while not self.kill:
                s.settimeout(1)
                s.listen()
                try:
                    conn, addr = s.accept()
                    print('new connection:', conn, addr)
                    if len(self.players) < 2:
                        self.players.append(conn)
                        # TODO: spawn listener task 
                except socket.timeout:
                    continue
                time.sleep(0.01)
        self.thread_count -= 1
        
    def await_kill(self):
        self.kill = True
        while self.thread_count:
            time.sleep(0.01)
        print('killed')
    
    def run(self): 
        threading.Thread(target=self.connection_listen_loop).start()
        # Starts thread
        try:
            while True:
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.await_kill()
    
Server().run()