"""
Game Controller - Manages Arena and LeetCode surfaces and state transitions
"""
import pygame
import sys
from arena import Arena
from lc_screen import LCScreen


class GameController:
    """
    Main game controller that manages:
    - Arena game surface
    - LeetCode problem UI surface  
    - State transitions between them
    """
    
    def __init__(self):
        pygame.init()
        
        # Display configuration
        self.screen_width = 1280
        self.screen_height = 720
        self.display = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Leetcode Arena")
        
        # Create offscreen surfaces
        self.arena_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.leetcode_surface = pygame.Surface((self.screen_width, self.screen_height))
        
        # Initialize subsystems
        self.arena = Arena(screen=self.arena_surface)
        self.lc_screen = LCScreen(self.leetcode_surface, timer_duration=30000)  # 30 seconds
        
        # Game state: "ARENA", "LC", "ENDED"
        self.state = "ARENA"
        
        # Clock and control
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        # Track previous knight state for death detection
        self.knight_was_alive = True
        
        # Victory overlay font
        self.victory_font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 48)
        
    def check_knight_death(self):
        """Check if knight just died and transition to LC mode"""
        knight_alive = self.arena.knight.alive
        
        # Detect transition from alive to dead
        if self.knight_was_alive and not knight_alive:
            print("Knight died! Switching to LeetCode mode...")
            self.state = "LC"
            self.lc_screen.load_problem()
            self.lc_screen.start_timer()
            
        self.knight_was_alive = knight_alive
    
    def handle_events(self):
        """Handle events and route to appropriate subsystem"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                
                # Handle restart in ENDED state
                if event.key == pygame.K_r and self.state == "ENDED":
                    self.__init__()  # Restart entire game
                    return
                
                # Pass space key to arena for attack
                if self.state == "ARENA" and event.key == pygame.K_SPACE:
                    # Store this for arena processing
                    self._arena_attack = True
            
            # Route events to LC screen
            if self.state == "LC":
                self.lc_screen.handle_event(event)
        
        # Process arena input in ARENA state
        if self.state == "ARENA":
            keys = pygame.key.get_pressed()
            from arena import PlayerInput
            p1 = PlayerInput(
                left=keys[pygame.K_a],
                right=keys[pygame.K_d],
                attack=getattr(self, '_arena_attack', False) or keys[pygame.K_SPACE]
            )
            self.arena.samurai.apply_input(p1)
            self._arena_attack = False  # Reset after use
    
    def update(self):
        """Update the active game mode"""
        if self.state == "ARENA":
            if not self.arena.game_over:
                self.arena.update()
                # Check if knight died
                self.check_knight_death()
                
        elif self.state == "LC":
            self.lc_screen.update(1/60.0)
            
            # Check if problem was solved
            if self.lc_screen.problem_solved:
                print("Problem solved! Victory!")
                self.state = "ENDED"
            
            # Check if timer expired
            elif self.lc_screen.is_timer_expired():
                print("Timer expired! Reviving knight and returning to arena...")
                self.arena.knight.revive()
                self.knight_was_alive = True
                self.state = "ARENA"
    
    def draw(self):
        """Draw the active surface to the display"""
        if self.state == "ARENA":
            # Draw arena to its surface
            self.arena.draw()
            # Blit arena surface to display
            self.display.blit(self.arena_surface, (0, 0))
            
        elif self.state == "LC":
            # Draw LC screen to its surface
            self.lc_screen.draw()
            # Blit LC surface to display
            self.display.blit(self.leetcode_surface, (0, 0))
            
        elif self.state == "ENDED":
            # Draw a victory overlay
            self.display.fill((0, 20, 40))
            
            victory_text = self.victory_font.render("VICTORY!", True, (100, 255, 100))
            victory_rect = victory_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            self.display.blit(victory_text, victory_rect)
            
            subtitle = self.small_font.render("You solved the problem in time!", True, (200, 200, 255))
            subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 30))
            self.display.blit(subtitle, subtitle_rect)
            
            restart_text = self.small_font.render("Press R to Restart or ESC to Quit", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
            self.display.blit(restart_text, restart_rect)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)


def main():
    """Entry point for the game"""
    controller = GameController()
    controller.run()


if __name__ == "__main__":
    main()
