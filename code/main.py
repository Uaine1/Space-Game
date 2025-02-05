import pygame
from random import randint, uniform
from os.path import join


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join("images", "player.png")).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.speed = 300
        self.direction = pygame.math.Vector2()

        # Cooldown Timer
        self.can_atk =True          # atk = Attack
        self.shot_atk_timer = 0     # cd = Cooldown
        self.atk_cd_dur = 400       # dur = Duration

        # Mask
        #self.mask = pygame.mask.from_surface(self.image)
    

    def atk_timer(self):
        if not self.can_atk:
            current_time = pygame.time.get_ticks()
            if current_time - self.shot_atk_timer >= self.atk_cd_dur:
                self.can_atk = True
        

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        atk_btn = pygame.key.get_just_pressed()
        if atk_btn[pygame.K_SPACE] and self.can_atk:
            Laser(laser_surf, self.rect.midtop, (sprites, laser_sprites))
            self.can_atk = False
            self.shot_atk_timer = pygame.time.get_ticks()
            laser_sfx.play()

        self.atk_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surface):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.orig_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        #self.start_time = pygame.time.get_ticks()
        #self.life_time = 3000 
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400,500)

        # Transform
        self.rotation = 0
        self.rotation_speed = randint(70,200)

    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.bottom > WINDOW_HEIGHT:
            self.kill()
        """if pygame.time.get_ticks() - self.start_time >= self.life_time:
            self.kill()"""
            
        # Continuous rotation
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.orig_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_frect(midbottom = pos)
        #self.rect.y -= 0.1 I guess its not working here


    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
            
        else:
            self.kill()


def collisions():
    global running # not an ideal approach
     
    meteor_collided = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if meteor_collided:
        running = False

    for laser in laser_sprites:
        laser_collided = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if laser_collided:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, sprites)
            explosion_sfx.play()


def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(f"Score: {current_time}", True, "#d4d3cf")
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    pygame.draw.rect(screen_display, "#576d96", text_rect.inflate(20, 20).move(0, -5), 5, 10)
    screen_display.blit(text_surf, text_rect)


#General setup
pygame.init() #Initialize pygame

#Create window
WINDOW_WIDTH, WINDOW_HEIGHT = 1080, 680
pygame.display.set_caption("Space Dunno")
screen_display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
running = True
clock = pygame.time.Clock() # helps framerate

#Imports
star_surf = pygame.image.load(join("images", "star.png")).convert_alpha()
laser_surf = pygame.image.load(join("images", "laser.png")).convert_alpha()
meteor_surf = pygame.image.load(join("images", "meteor.png")).convert_alpha()
font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 30)
text_surf = font.render("Wassup", True, "#d4d3cf")
explosion_frames = [pygame.image.load(join("images", "explosion", f"{i}.png")).convert_alpha() for i in range(21)]

laser_sfx = pygame.mixer.Sound(join("audio", "laser.wav"))
laser_sfx.set_volume(0.2)

explosion_sfx = pygame.mixer.Sound(join("audio", "explosion.wav"))

game_music = pygame.mixer.Sound(join("audio", "game_music.wav"))
game_music.set_volume(0.1)
game_music.play(loops= -1) 

# Sprites - Draw order is a must
sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

# Helps on creating stars multiple times
for i in range(20):
    Star(sprites, star_surf)

player = Player(sprites)

# Meteor (Interval Timer)
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

while running:
    dt = clock.tick() / 1000 #framerate
    #print(clock.get_fps())

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x,y), (sprites, meteor_sprites))

    # Updates the game
    sprites.update(dt)

    collisions()
    
    # Draw the game
    screen_display.fill("#2f3036")
    sprites.draw(screen_display)
    display_score()

    pygame.display.update()

pygame.quit()