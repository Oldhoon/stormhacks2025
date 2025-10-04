import pygame
import sys
from pygame.locals import *
from knight import Knight
import struct
import threading
import socket
import time
import random
import string

class QuickGame:
    def __init__(self):
        pygame.init()
        
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Leetcode Arena")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        self.background = pygame.image.load(r"assets/cyberpunk-street-files/cyberpunk-street-files/Assets/Version 1/PNG/cyberpunk-street.png").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        
        self.knight = Knight()
        
        self.big_font = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        
        self.is_host = None
        self.opponent_conn = None
        self.server_socket = None
        self.game_port = 65470
        self.connected = False
        self.kill = False
        self.running = True
        
        self.state = "MENU"  # MENU, HOST, JOIN, GAME
        self.room_code = ""
        self.input_text = ""
        self.input_mode = None  # "room", "host", "port"
        self.host_input = ""
        self.port_input = ""
        self.status_message = ""
        
        self.host_button = pygame.Rect(self.screen_width//2 - 200, 300, 400, 80)
        self.join_button = pygame.Rect(self.screen_width//2 - 200, 420, 400, 80)
        self.back_button = pygame.Rect(50, 50, 150, 60)
        
    def draw_button(self, rect, text, color=(50, 50, 100)):
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            color = tuple(min(c + 30, 255) for c in color)
        
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 3, border_radius=10)
        
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def draw_menu(self):
        self.screen.blit(self.background, (0, 0))
        
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        title = self.big_font.render("LEETCODE ARENA", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.screen_width//2, 150))
        self.screen.blit(title, title_rect)
        
        self.draw_button(self.host_button, "HOST GAME")
        self.draw_button(self.join_button, "JOIN GAME")
        
        pygame.display.flip()
    
    def draw_host_screen(self):
        self.screen.blit(self.background, (0, 0))
        
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        self.draw_button(self.back_button, "BACK", (100, 50, 50))
        
        title = self.font.render("ROOM CODE:", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width//2, 200))
        self.screen.blit(title, title_rect)
        
        code = self.big_font.render(self.room_code, True, (100, 255, 100))
        code_rect = code.get_rect(center=(self.screen_width//2, 280))
        self.screen.blit(code, code_rect)
        
        instructions = [
            "Share this code with your friend!",
            "",
            "They need to:",
            "1. Click 'JOIN GAME'",
            "2. Enter this room code",
            "3. Enter your connection info"
        ]
        
        y = 380
        for line in instructions:
            text = self.small_font.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(center=(self.screen_width//2, y))
            self.screen.blit(text, text_rect)
            y += 35
        
        if self.connected:
            status = self.font.render("CONNECTED!", True, (100, 255, 100))
        else:
            status = self.font.render("Waiting for opponent...", True, (255, 255, 100))
        status_rect = status.get_rect(center=(self.screen_width//2, 600))
        self.screen.blit(status, status_rect)
        
        pygame.display.flip()
    
    def draw_join_screen(self):
        self.screen.blit(self.background, (0, 0))
        
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        self.draw_button(self.back_button, "BACK", (100, 50, 50))
        
        title = self.font.render("JOIN GAME", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width//2, 100))
        self.screen.blit(title, title_rect)
        
        fields = [
            ("ROOM CODE:", self.input_text, 220, "room"),
            ("HOST (local IP):", self.host_input, 340, "host"),
            ("PORT:", self.port_input or "65470", 460, "port"),
        ]
        
        for label, value, y, mode in fields:
            label_surf = self.small_font.render(label, True, (200, 200, 200))
            self.screen.blit(label_surf, (self.screen_width//2 - 300, y - 30))
            
            input_rect = pygame.Rect(self.screen_width//2 - 300, y, 600, 50)
            color = (100, 100, 150) if self.input_mode == mode else (50, 50, 100)
            pygame.draw.rect(self.screen, color, input_rect, border_radius=5)
            pygame.draw.rect(self.screen, (200, 200, 200), input_rect, 2, border_radius=5)
            
            text_surf = self.small_font.render(value, True, (255, 255, 255))
            self.screen.blit(text_surf, (input_rect.x + 10, input_rect.y + 10))
            
            if self.input_mode == mode and int(time.time() * 2) % 2:
                cursor_x = input_rect.x + 15 + text_surf.get_width()
                pygame.draw.line(self.screen, (255, 255, 255), 
                               (cursor_x, input_rect.y + 10),
                               (cursor_x, input_rect.y + 40), 2)
        
        # Connect button
        connect_button = pygame.Rect(self.screen_width//2 - 150, 560, 300, 60)
        self.draw_button(connect_button, "CONNECT", (50, 100, 50))
        
        # Status message
        if self.status_message:
            color = (100, 255, 100) if "Connected" in self.status_message else (255, 100, 100)
            status = self.small_font.render(self.status_message, True, color)
            status_rect = status.get_rect(center=(self.screen_width//2, 650))
            self.screen.blit(status, status_rect)
        
        pygame.display.flip()
    
    def handle_menu_click(self, pos):
        if self.host_button.collidepoint(pos):
            self.start_hosting()
        elif self.join_button.collidepoint(pos):
            self.state = "JOIN"
            self.input_mode = "room"
    
    def handle_host_click(self, pos):
        if self.back_button.collidepoint(pos) and not self.connected:
            self.state = "MENU"
            if self.server_socket:
                self.server_socket.close()
    
    def handle_join_click(self, pos):
        if self.back_button.collidepoint(pos):
            self.state = "MENU"
            self.input_text = ""
            self.host_input = ""
            self.port_input = ""
            self.status_message = ""
            return
        
        # Check input field clicks
        fields = [
            (pygame.Rect(self.screen_width//2 - 300, 220, 600, 50), "room"),
            (pygame.Rect(self.screen_width//2 - 300, 340, 600, 50), "host"),
            (pygame.Rect(self.screen_width//2 - 300, 460, 600, 50), "port"),
        ]
        
        for rect, mode in fields:
            if rect.collidepoint(pos):
                self.input_mode = mode
                return
        
        # Connect button
        connect_button = pygame.Rect(self.screen_width//2 - 150, 560, 300, 60)
        if connect_button.collidepoint(pos):
            self.attempt_join()
    
    def handle_text_input(self, event):
        if self.input_mode is None:
            return
        
        if event.key == K_BACKSPACE:
            if self.input_mode == "room":
                self.input_text = self.input_text[:-1]
            elif self.input_mode == "host":
                self.host_input = self.host_input[:-1]
            elif self.input_mode == "port":
                self.port_input = self.port_input[:-1]
        
        elif event.key == K_RETURN or event.key == K_TAB:
            if self.input_mode == "room":
                self.input_mode = "host"
            elif self.input_mode == "host":
                self.input_mode = "port"
            elif self.input_mode == "port":
                self.attempt_join()
        
        elif event.unicode.isprintable():
            if self.input_mode == "room":
                self.input_text = (self.input_text + event.unicode).upper()[:8]
            elif self.input_mode == "host":
                self.host_input = (self.host_input + event.unicode)[:100]
            elif self.input_mode == "port":
                if event.unicode.isdigit():
                    self.port_input = (self.port_input + event.unicode)[:5]
    
    def start_hosting(self):
        self.state = "HOST"
        self.is_host = True
        self.room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        # Start server in background
        threading.Thread(target=self.host_game, daemon=True).start()
    
    def host_game(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            self.server_socket.bind(('0.0.0.0', self.game_port))
            self.server_socket.listen(1)
            self.server_socket.settimeout(300)  # 5 min
            
            conn, addr = self.server_socket.accept()
            
            self.opponent_conn = conn
            self.opponent_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            self.connected = True
            
            # Start game after short delay
            time.sleep(2)
            self.state = "GAME"
            threading.Thread(target=self.run_listener, daemon=True).start()
            
        except Exception as e:
            print(f"Host error: {e}")
    
    def attempt_join(self):
        if not self.input_text or not self.host_input:
            self.status_message = "Fill in room code and host!"
            return
        
        port = int(self.port_input) if self.port_input else 65470
        self.status_message = "Connecting..."
        
        # Connect in background
        threading.Thread(target=self.join_game, args=(self.host_input, port), daemon=True).start()
    
    def join_game(self, host, port):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(10)
            client.connect((host, port))
            
            self.opponent_conn = client
            self.opponent_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            self.connected = True
            self.status_message = "Connected! Starting game..."
            
            time.sleep(2)
            self.state = "GAME"
            threading.Thread(target=self.run_listener, daemon=True).start()
            
        except Exception as e:
            self.status_message = f"Connection failed: {str(e)[:40]}"
    
    def send_move(self, move_data):
        if self.opponent_conn and self.connected:
            try:
                self.opponent_conn.send(move_data)
            except:
                self.connected = False
    
    def run_listener(self):
        if not self.opponent_conn:
            return
        
        self.opponent_conn.settimeout(1)
        while not self.kill and self.connected:
            try:
                data = self.opponent_conn.recv(4096)
                if len(data):
                    # Handle opponent move
                    self.handle_opponent_move(data)
                else:
                    self.connected = False
            except socket.timeout:
                pass
            except:
                self.connected = False
            time.sleep(0.001)
    
    def handle_opponent_move(self, data):
        pass
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.kill = True
                self.running = False
                if self.opponent_conn:
                    self.opponent_conn.close()
                if self.server_socket:
                    self.server_socket.close()
                pygame.quit()
                sys.exit()
            
            if event.type == MOUSEBUTTONDOWN:
                if self.state == "MENU":
                    self.handle_menu_click(event.pos)
                elif self.state == "HOST":
                    self.handle_host_click(event.pos)
                elif self.state == "JOIN":
                    self.handle_join_click(event.pos)
            
            if event.type == KEYDOWN and self.state == "JOIN":
                self.handle_text_input(event)
    
    def update(self):
        if self.state == "GAME":
            self.knight.update()
    
    def draw(self):
        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "HOST":
            self.draw_host_screen()
        elif self.state == "JOIN":
            self.draw_join_screen()
        elif self.state == "GAME":
            # Your actual game rendering
            self.screen.blit(self.background, (0, 0))
            self.knight.draw(self.screen)
            
            # Connection status indicator
            if self.connected:
                status = self.small_font.render("CONNECTED", True, (100, 255, 100))
            else:
                status = self.small_font.render("DISCONNECTED", True, (255, 100, 100))
            self.screen.blit(status, (10, 10))
            
            pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)

if __name__ == '__main__':
    QuickGame().run()