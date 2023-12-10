import pygame
import sys
import random

####################################################################################################

class FlappyBird:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((576, 1024))
        self.clock  = pygame.time.Clock()

        self.game_font = pygame.font.Font('assets/04B_19.ttf', 40)

        self.bg_surface    = pygame.transform.scale2x(pygame.image.load('assets/background-day.png').convert())
        self.floor_surface = pygame.transform.scale2x(pygame.image.load('assets/base.png').convert())

        self.bird_downflap     = pygame.transform.scale2x(pygame.image.load('assets/bluebird-downflap.png').convert_alpha())
        self.bird_midflap      = pygame.transform.scale2x(pygame.image.load('assets/bluebird-midflap.png').convert_alpha())
        self.bird_upflap       = pygame.transform.scale2x(pygame.image.load('assets/bluebird-upflap.png').convert_alpha())
        self.pipe_surface      = pygame.transform.scale2x(pygame.image.load('assets/pipe-green.png'))
        self.game_over_surface = pygame.transform.scale2x(pygame.image.load('assets/message.png').convert_alpha())

        self.flap_sound   = pygame.mixer.Sound('assets/sfx_wing.wav')
        self.death_sound  = pygame.mixer.Sound('assets/sfx_hit.wav')
        self.score_sound  = pygame.mixer.Sound('assets/sfx_point.wav')
        self.fall_sound   = pygame.mixer.Sound('assets/sfx_fall.wav')
        self.swoosh_sound = pygame.mixer.Sound('assets/sfx_swooshing.wav')

        self.gravity       = 0.25
        self.bird_movement = 0
        self.game_active   = True

        self.score      = 0
        self.high_score = 0
        self.can_score  = True

        self.floor_x_pos = 0

        self.bird_frames  = [self.bird_downflap, self.bird_midflap, self.bird_upflap]
        self.bird_index   = 0
        self.bird_surface = self.bird_frames[self.bird_index]
        self.bird_rect    = self.bird_surface.get_rect(center=(100, 512))

        self.BIRDFLAP = pygame.USEREVENT + 1
        pygame.time.set_timer(self.BIRDFLAP, 200)

        self.pipe_list = []
        self.SPAWNPIPE = pygame.USEREVENT
        pygame.time.set_timer(self.SPAWNPIPE, 1200)
        self.pipe_height = [400, 600, 800]

        self.game_over_rect = self.game_over_surface.get_rect(center=(288, 512))

        self.score_sound_countdown = 100
        self.SCOREEVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.SCOREEVENT, 100)

    def draw_floor(self):
        self.screen.blit(self.floor_surface, (self.floor_x_pos, 900))
        self.screen.blit(self.floor_surface, (self.floor_x_pos + 576, 900))

    def create_pipe(self):
        random_pipe_pos = random.choice(self.pipe_height)
        bottom_pipe = self.pipe_surface.get_rect(midtop=(700, random_pipe_pos))
        top_pipe    = self.pipe_surface.get_rect(midbottom=(700, random_pipe_pos - 300))
        return bottom_pipe, top_pipe

    def move_pipes(self, pipes):
        for pipe in pipes:
            pipe.centerx -= 5
        visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
        return visible_pipes

    def draw_pipes(self, pipes):
        for pipe in pipes:
            if pipe.bottom >= 1024:
                self.screen.blit(self.pipe_surface, pipe)
            else:
                flip_pipe = pygame.transform.flip(self.pipe_surface, False, True)
                self.screen.blit(flip_pipe, pipe)

    def check_collision(self, pipes):
        for pipe in pipes:
            if self.bird_rect.colliderect(pipe):
                self.death_sound.play()
                self.can_score = True
                return False

        if self.bird_rect.top <= -100:
            self.swoosh_sound.play()
            self.can_score = True
            return False

        if self.bird_rect.bottom >= 900:
            self.fall_sound.play()
            self.can_score = True
            return False

        return True

    def rotate_bird(self):
        new_bird = pygame.transform.rotozoom(self.bird_surface, -self.bird_movement * 3, 1)
        return new_bird

    def bird_animation(self):
        new_bird = self.bird_frames[self.bird_index]
        new_bird_rect = new_bird.get_rect(center=(100, self.bird_rect.centery))
        return new_bird, new_bird_rect

    def score_display(self, game_state):
        if game_state == 'main_game':
            score_surface = self.game_font.render(str(int(self.score)), True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(288, 100))
            self.screen.blit(score_surface, score_rect)

        if game_state == 'game_over':
            score_surface = self.game_font.render(f'Score: {int(self.score)}', True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(288, 100))
            self.screen.blit(score_surface, score_rect)

            high_score_surface = self.game_font.render(f'High score: {int(self.high_score)}', True, (255, 255, 255))
            high_score_rect = high_score_surface.get_rect(center=(288, 850))
            self.screen.blit(high_score_surface, high_score_rect)

    def update_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
        return self.high_score

    def pipe_score_check(self):
        if self.pipe_list:
            for pipe in self.pipe_list:
                if 95 < pipe.centerx < 105 and self.can_score:
                    self.score += 1
                    self.score_sound.play()
                    self.can_score = False
                if pipe.centerx < 0:
                    self.can_score = True

    def run_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_active:
                        self.bird_movement = 0
                        self.bird_movement -= 10
                        self.flap_sound.play()
                    if event.key == pygame.K_SPACE and not self.game_active:
                        self.game_active = True
                        self.pipe_list.clear()
                        self.bird_rect.center = (100, 512)
                        self.bird_movement = 0
                        self.score = 0

                if event.type == self.SPAWNPIPE:
                    self.pipe_list.extend(self.create_pipe())

                if event.type == self.BIRDFLAP:
                    if self.bird_index < 2:
                        self.bird_index += 1
                    else:
                        self.bird_index = 0

                    self.bird_surface, self.bird_rect = self.bird_animation()

            self.screen.blit(self.bg_surface, (0, 0))

            if self.game_active:
                # 鳥
                self.bird_movement += self.gravity
                self.rotated_bird = self.rotate_bird()
                self.bird_rect.centery += self.bird_movement
                self.screen.blit(self.rotated_bird, self.bird_rect)
                self.game_active = self.check_collision(self.pipe_list)

                # 土管
                self.pipe_list = self.move_pipes(self.pipe_list)
                self.draw_pipes(self.pipe_list)

                # スコア
                self.pipe_score_check()
                self.score_display('main_game')
            else:
                self.screen.blit(self.game_over_surface, self.game_over_rect)
                self.high_score = self.update_score()
                self.score_display('game_over')

            # 地面
            self.floor_x_pos -= 1
            self.draw_floor()
            if self.floor_x_pos <= -576:
                self.floor_x_pos = 0

            pygame.display.update()
            self.clock.tick(120)

####################################################################################################

if __name__ == "__main__":
    flappy_bird = FlappyBird()
    flappy_bird.run_game()
