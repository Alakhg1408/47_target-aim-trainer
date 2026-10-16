import pygame
import random
from .target import Target

# Game Engine

WHITE = (255, 255, 255)
RED = (220, 60, 60)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60
        self.target = self._spawn_target()

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.hits = 0
        self.misses = 0
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 26)
        self.title_font = pygame.font.SysFont("Arial", 44, bold=True)
        self.stat_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.btn_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.game_over = False

        self.play_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.exit_btn_rect = pygame.Rect(0, 0, 0, 0)

    def reset(self):
        self.target = self._spawn_target()
        self.time_left_frames = self.round_seconds * 60
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.game_over = False
        self._game_over_logged = False

    def _spawn_target(self):
        x = random.randint(self.margin, self.width - self.margin)
        y = random.randint(self.margin + self.hud_height, self.height - self.margin)
        return Target(x, y)

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                    self.reset()
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.play_btn_rect.collidepoint(event.pos):
                    self.reset()
                elif self.exit_btn_rect.collidepoint(event.pos):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        x, y = pos
        if self.target.contains_point(x, y):
            self.hits += 1
            self.score += 1
            self.target = self._spawn_target()
        else:
            self.misses += 1

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self.time_left_frames -= 1
        if self.time_left_frames <= 0:
            self.game_over = True
            return

        self.target.update()
        if self.target.expired():
            self.misses += 1  # letting a target time out counts as a miss too
            self.target = self._spawn_target()

    def accuracy(self):
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round(100 * self.hits / total, 1)

    def _draw_game_over_screen(self, screen):
        # Translucent backdrop overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((15, 15, 20, 215))
        screen.blit(overlay, (0, 0))

        # Main Card Panel
        card_w, card_h = 480, 350
        card_x = (self.width - card_w) // 2
        card_y = (self.height - card_h) // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(screen, (28, 30, 40), card_rect, border_radius=16)
        pygame.draw.rect(screen, (220, 60, 60), card_rect, width=2, border_radius=16)

        # Title: GAME OVER
        title_surf = self.title_font.render("GAME OVER", True, (240, 70, 70))
        screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, card_y + 42)))

        subtitle_surf = self.small_font.render("Round Complete!", True, (170, 175, 190))
        screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(self.width // 2, card_y + 75)))

        # Stat cards (Score and Accuracy)
        stat_box_w, stat_box_h = 180, 76
        box_y = card_y + 105

        # Score Box
        score_box_rect = pygame.Rect(self.width // 2 - stat_box_w - 15, box_y, stat_box_w, stat_box_h)
        pygame.draw.rect(screen, (38, 41, 54), score_box_rect, border_radius=10)
        lbl_score = self.small_font.render("FINAL SCORE", True, (160, 165, 180))
        screen.blit(lbl_score, lbl_score.get_rect(center=(score_box_rect.centerx, box_y + 20)))
        val_score = self.stat_font.render(str(self.score), True, (255, 255, 255))
        screen.blit(val_score, val_score.get_rect(center=(score_box_rect.centerx, box_y + 50)))

        # Accuracy Box
        acc_box_rect = pygame.Rect(self.width // 2 + 15, box_y, stat_box_w, stat_box_h)
        pygame.draw.rect(screen, (38, 41, 54), acc_box_rect, border_radius=10)
        lbl_acc = self.small_font.render("ACCURACY", True, (160, 165, 180))
        screen.blit(lbl_acc, lbl_acc.get_rect(center=(acc_box_rect.centerx, box_y + 20)))
        acc_color = (70, 215, 130) if self.accuracy() >= 70 else (240, 190, 60) if self.accuracy() >= 40 else (240, 80, 80)
        val_acc = self.stat_font.render(f"{self.accuracy()}%", True, acc_color)
        screen.blit(val_acc, val_acc.get_rect(center=(acc_box_rect.centerx, box_y + 50)))

        # Breakdown: Hits & Misses
        breakdown_text = f"Hits: {self.hits}   •   Misses: {self.misses}"
        breakdown_surf = self.small_font.render(breakdown_text, True, (190, 195, 210))
        screen.blit(breakdown_surf, breakdown_surf.get_rect(center=(self.width // 2, card_y + 208)))

        # Interactive Buttons
        mouse_pos = pygame.mouse.get_pos()
        btn_w, btn_h = 160, 42
        btn_y = card_y + 238

        # Play Again Button
        self.play_btn_rect = pygame.Rect(self.width // 2 - btn_w - 15, btn_y, btn_w, btn_h)
        play_hovered = self.play_btn_rect.collidepoint(mouse_pos)
        play_bg = (46, 175, 95) if play_hovered else (35, 140, 75)
        pygame.draw.rect(screen, play_bg, self.play_btn_rect, border_radius=8)
        play_txt = self.btn_font.render("Play Again", True, (255, 255, 255))
        screen.blit(play_txt, play_txt.get_rect(center=self.play_btn_rect.center))

        # Exit Button
        self.exit_btn_rect = pygame.Rect(self.width // 2 + 15, btn_y, btn_w, btn_h)
        exit_hovered = self.exit_btn_rect.collidepoint(mouse_pos)
        exit_bg = (215, 60, 60) if exit_hovered else (165, 45, 45)
        pygame.draw.rect(screen, exit_bg, self.exit_btn_rect, border_radius=8)
        exit_txt = self.btn_font.render("Exit", True, (255, 255, 255))
        screen.blit(exit_txt, exit_txt.get_rect(center=self.exit_btn_rect.center))

        # Keyboard Hints
        hint_surf = self.small_font.render("Press [R] to Restart  |  [ESC] to Exit", True, (130, 135, 150))
        screen.blit(hint_surf, hint_surf.get_rect(center=(self.width // 2, card_y + 310)))

    def render(self, screen):
        r = int(self.target.visual_radius())
        pygame.draw.circle(screen, RED, (self.target.x, self.target.y), r)
        pygame.draw.circle(screen, WHITE, (self.target.x, self.target.y), r, 2)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        seconds_left = max(0, self.time_left_frames // 60)
        timer_text = self.font.render(f"Time: {seconds_left}s", True, WHITE)
        screen.blit(timer_text, (self.width - 140, 10))

        acc_text = self.font.render(f"Accuracy: {self.accuracy()}%", True, WHITE)
        screen.blit(acc_text, (self.width // 2 - 90, 10))

        if self.game_over:
            if not getattr(self, "_game_over_logged", False):
                print(f"Time's up! Final score: {self.score}  Accuracy: {self.accuracy()}%")
                self._game_over_logged = True
            self._draw_game_over_screen(screen)

