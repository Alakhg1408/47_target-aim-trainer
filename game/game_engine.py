import pygame
import random
from .target import Target
from .sound_manager import SoundManager

# Game Engine

WHITE = (255, 255, 255)
RED = (220, 60, 60)

DIFFICULTIES = {
    "Easy": {
        "base_radius": 50,
        "min_radius": 16,
        "lifespan_frames": 120,
        "color": (46, 175, 95),
        "hover_color": (65, 210, 115),
        "label": "Easy",
        "sub": "50px • 2.0s",
        "key_hint": "1",
    },
    "Medium": {
        "base_radius": 40,
        "min_radius": 12,
        "lifespan_frames": 90,
        "color": (215, 150, 35),
        "hover_color": (245, 175, 45),
        "label": "Medium",
        "sub": "40px • 1.5s",
        "key_hint": "2",
    },
    "Hard": {
        "base_radius": 28,
        "min_radius": 8,
        "lifespan_frames": 60,
        "color": (215, 55, 55),
        "hover_color": (245, 75, 75),
        "label": "Hard",
        "sub": "28px • 1.0s",
        "key_hint": "3",
    },
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60
        self.difficulty = "Medium"
        self.sound_mgr = SoundManager()
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
        self.tiny_font = pygame.font.SysFont("Arial", 14)
        self.btn_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.game_over = False

        self.diff_btn_rects = {}
        self.exit_btn_rect = pygame.Rect(0, 0, 0, 0)

    def reset(self, difficulty=None):
        if difficulty and difficulty in DIFFICULTIES:
            self.difficulty = difficulty
        self.target = self._spawn_target()
        self.time_left_frames = self.round_seconds * 60
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.game_over = False
        self._game_over_logged = False

    def _spawn_target(self):
        settings = DIFFICULTIES[self.difficulty]
        margin = max(self.margin, settings["base_radius"] + 10)
        x = random.randint(margin, self.width - margin)
        y = random.randint(margin + self.hud_height, self.height - margin)
        return Target(
            x,
            y,
            base_radius=settings["base_radius"],
            min_radius=settings["min_radius"],
            lifespan_frames=settings["lifespan_frames"],
        )

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1, pygame.K_e):
                    self.reset("Easy")
                elif event.key in (pygame.K_2, pygame.K_KP2, pygame.K_m):
                    self.reset("Medium")
                elif event.key in (pygame.K_3, pygame.K_KP3, pygame.K_h):
                    self.reset("Hard")
                elif event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                    self.reset(self.difficulty)
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for diff_name, rect in self.diff_btn_rects.items():
                    if rect.collidepoint(event.pos):
                        self.reset(diff_name)
                        return
                if self.exit_btn_rect.collidepoint(event.pos):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        x, y = pos
        if self.target.contains_point(x, y):
            self.hits += 1
            self.score += 1
            self.sound_mgr.play("hit")
            self.target = self._spawn_target()
        else:
            self.misses += 1
            self.sound_mgr.play("miss")

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
            self.sound_mgr.play("game_over")
            return

        self.target.update()
        if self.target.expired():
            self.misses += 1  # letting a target time out counts as a miss too
            self.sound_mgr.play("miss")
            self.target = self._spawn_target()


    def accuracy(self):
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round(100 * self.hits / total, 1)

    def _draw_game_over_screen(self, screen):
        # Translucent backdrop overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((15, 15, 20, 220))
        screen.blit(overlay, (0, 0))

        # Main Card Panel
        card_w, card_h = 540, 410
        card_x = (self.width - card_w) // 2
        card_y = (self.height - card_h) // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(screen, (26, 28, 38), card_rect, border_radius=16)
        pygame.draw.rect(screen, (220, 60, 60), card_rect, width=2, border_radius=16)

        # Title: GAME OVER
        title_surf = self.title_font.render("GAME OVER", True, (240, 70, 70))
        screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, card_y + 35)))

        subtitle_surf = self.small_font.render("Round Complete!", True, (170, 175, 190))
        screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(self.width // 2, card_y + 68)))

        # Stat cards (Score and Accuracy)
        stat_box_w, stat_box_h = 190, 70
        box_y = card_y + 92

        # Score Box
        score_box_rect = pygame.Rect(self.width // 2 - stat_box_w - 15, box_y, stat_box_w, stat_box_h)
        pygame.draw.rect(screen, (36, 39, 52), score_box_rect, border_radius=10)
        lbl_score = self.small_font.render("FINAL SCORE", True, (160, 165, 180))
        screen.blit(lbl_score, lbl_score.get_rect(center=(score_box_rect.centerx, box_y + 18)))
        val_score = self.stat_font.render(str(self.score), True, (255, 255, 255))
        screen.blit(val_score, val_score.get_rect(center=(score_box_rect.centerx, box_y + 46)))

        # Accuracy Box
        acc_box_rect = pygame.Rect(self.width // 2 + 15, box_y, stat_box_w, stat_box_h)
        pygame.draw.rect(screen, (36, 39, 52), acc_box_rect, border_radius=10)
        lbl_acc = self.small_font.render("ACCURACY", True, (160, 165, 180))
        screen.blit(lbl_acc, lbl_acc.get_rect(center=(acc_box_rect.centerx, box_y + 18)))
        acc_color = (70, 215, 130) if self.accuracy() >= 70 else (240, 190, 60) if self.accuracy() >= 40 else (240, 80, 80)
        val_acc = self.stat_font.render(f"{self.accuracy()}%", True, acc_color)
        screen.blit(val_acc, val_acc.get_rect(center=(acc_box_rect.centerx, box_y + 46)))

        # Breakdown: Hits & Misses
        breakdown_text = f"Hits: {self.hits}   •   Misses: {self.misses}"
        breakdown_surf = self.small_font.render(breakdown_text, True, (190, 195, 210))
        screen.blit(breakdown_surf, breakdown_surf.get_rect(center=(self.width // 2, card_y + 180)))

        # Prompt for difficulty selection
        prompt_surf = self.small_font.render("PLAY AGAIN — CHOOSE DIFFICULTY:", True, (220, 225, 235))
        screen.blit(prompt_surf, prompt_surf.get_rect(center=(self.width // 2, card_y + 215)))

        # 3 Difficulty Buttons
        mouse_pos = pygame.mouse.get_pos()
        btn_w, btn_h = 150, 52
        gap = 15
        total_w = 3 * btn_w + 2 * gap
        start_x = (self.width - total_w) // 2
        btn_y = card_y + 238

        self.diff_btn_rects = {}
        for i, (name, cfg) in enumerate(DIFFICULTIES.items()):
            bx = start_x + i * (btn_w + gap)
            btn_rect = pygame.Rect(bx, btn_y, btn_w, btn_h)
            self.diff_btn_rects[name] = btn_rect

            hovered = btn_rect.collidepoint(mouse_pos)
            is_current = (name == self.difficulty)
            btn_bg = cfg["hover_color"] if hovered else cfg["color"]

            pygame.draw.rect(screen, btn_bg, btn_rect, border_radius=8)
            if is_current:
                pygame.draw.rect(screen, (255, 255, 255), btn_rect, width=2, border_radius=8)

            btn_label = self.btn_font.render(f"[{cfg['key_hint']}] {name}", True, (255, 255, 255))
            screen.blit(btn_label, btn_label.get_rect(center=(btn_rect.centerx, btn_rect.centery - 9)))

            sub_label = self.tiny_font.render(cfg["sub"], True, (240, 245, 255))
            screen.blit(sub_label, sub_label.get_rect(center=(btn_rect.centerx, btn_rect.centery + 12)))

        # Exit Button
        exit_w, exit_h = 160, 36
        self.exit_btn_rect = pygame.Rect((self.width - exit_w) // 2, card_y + 308, exit_w, exit_h)
        exit_hovered = self.exit_btn_rect.collidepoint(mouse_pos)
        exit_bg = (195, 55, 55) if exit_hovered else (145, 40, 40)
        pygame.draw.rect(screen, exit_bg, self.exit_btn_rect, border_radius=6)
        exit_txt = self.small_font.render("[ESC] Exit Game", True, (255, 255, 255))
        screen.blit(exit_txt, exit_txt.get_rect(center=self.exit_btn_rect.center))

        # Keyboard Hints
        hint_surf = self.tiny_font.render("Keys: [1] Easy  [2] Medium  [3] Hard  [R] Replay  [ESC] Exit", True, (130, 135, 150))
        screen.blit(hint_surf, hint_surf.get_rect(center=(self.width // 2, card_y + 372)))

    def render(self, screen):
        r = int(self.target.visual_radius())
        pygame.draw.circle(screen, RED, (self.target.x, self.target.y), r)
        pygame.draw.circle(screen, WHITE, (self.target.x, self.target.y), r, 2)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        diff_badge = self.small_font.render(f"Mode: {self.difficulty}", True, DIFFICULTIES[self.difficulty]["color"])
        screen.blit(diff_badge, (10, 38))

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


