# TY KING https://www.youtube.com/watch?v=VvwLXnY-mKk
import socket
import threading
import struct
import time

class Server:
    def __init__(self, host = '0.0.0.0', port=65469):
        self.host = host
        self.port = port
        self.null_char = 'n'
        self.winner = self.null_char
        
        self.kill = False
        self.thread_count = 0
        self.players = []
        self.max_players = 2
        
    def serialize(self):
        return struct.pack()
    
    def run_listener(self, conn): 
        self.thread_count += 1
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        conn.settimeout(1)
        while conn:
            while not self.kill:
                try:
                    data = conn.recv(4096)
                    if len(data):
                        target_space = struct.unpack_from('B', data, 0)[0]
                        # self.place(conn, target_space)
                except socket.timeout:
                    pass
        self.thread_count -= 1
        
    def connection_listen_loop(self):
        self.thread_count += 1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            s.bind((self.host, self.port))
            s.listen(2)

            while not self.kill:
                if len(self.players) >= 2:
                    time.sleep(0.1)
                    continue

                s.settimeout(1)
                try:
                    conn, addr = s.accept()
                    print('new connection:', conn, addr)
                    self.players.append(conn)
                    threading.Thread(target=self.run_listener, args=(conn,), daemon=True).start()
                except socket.timeout:
                    continue

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