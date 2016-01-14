import os
import random
import os.path
import math
import numpy as np
import pygame
from pygame.locals import *
try:
    import algo_complete as algo
except:
    import algo

# see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# game constants
MAX_SHOTS = 2  # most player bullets onscreen
ALIEN_ODDS = 22  # chances a new alien appears
BOMB_ODDS = 60  # chances a new bomb will drop
ALIEN_COOLDOWN = 12  # frames between new aliens
ALIEN_FIRST = 100
SCREENRECT = pygame.Rect(0, 0, 640, 480)

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pygame.get_error()))
    return surface.convert()


def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


class dummysound:
    def play(self): pass


def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()


# each type of game object gets an init and an
# update function. the update function is called
# once per frame, and it is when each object should
# change it's current position and state. the Player
# object actually gets a "move" function instead of
# update, since it is passed extra information about
# the keyboard

class Gun(pygame.sprite.Sprite):
    def __init__(self, side, player):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=SCREENRECT.center)
        self.angle = 0
        self.player = player
        self.side = side

    def update(self):
        mirror = 1 if self.side else -1
        self.image = pygame.transform.rotate(self.images[self.side], mirror*self.angle)
        pnt = self.player.rect.center
        self.rect = self.image.get_rect(center=(pnt[0] + (self.side*2-1)*50, pnt[1]))


class Player(pygame.sprite.Sprite):
    speed = 10
    bounce = 24
    gun_offset = -11
    images = []

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=SCREENRECT.center)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1
        self.aim_angles = [0, 0]

    def move(self, x, y):
        self.rect.move_ip(x * self.speed, y * self.speed)
        self.rect = self.rect.clamp(SCREENRECT)

    def setppos(self, x, y):
        self.rect = self.image.get_rect(center=(x, y))

    def gunpos(self, side):
        return self.guns[side].rect.center

    def aim_to(self, angle, side):
        self.aim_angles[side] = angle
        self.guns[0].angle = self.aim_angles[0]
        self.guns[1].angle = self.aim_angles[1]

    def aim_turn(self, direction, side):
        self.aim_angles[side] += direction*3
        self.guns[0].angle = self.aim_angles[0]
        self.guns[1].angle = self.aim_angles[1]

    def fire(self):
        x = math.cos(math.radians(self.aim_angles[0]))
        y = math.sin(math.radians(self.aim_angles[0]))
        Shot(self.gunpos(0), (x, y))

        x = math.cos(math.radians(self.aim_angles[1]))
        y = math.sin(math.radians(self.aim_angles[1]))
        Shot(self.gunpos(1), (-x, y))

        shoot_sound.play()


class Alien(pygame.sprite.Sprite):
    speed = 3
    animcycle = 12
    images = []

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(bottom=int(SCREENRECT.height*random.random()))
        self.facing = random.choice((-1, 1)) * Alien.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing;
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        self.image = self.images[self.frame // self.animcycle % 3]


class Explosion(pygame.sprite.Sprite):
    defaultlife = 12
    animcycle = 3
    images = []

    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0: self.kill()


class Shot(pygame.sprite.Sprite):
    speed = -11
    images = []

    def __init__(self, pos, direction):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)
        self.direction = direction

    def update(self):
        self.rect.move_ip(self.direction[0]*self.speed,
                          self.direction[1]*self.speed)
        if not SCREENRECT.contains(self.rect):
            self.kill()


class Bomb(pygame.sprite.Sprite):
    speed = 5
    images = []

    def __init__(self, pos, direction):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)
        self.direction = direction

    def update(self):
        self.rect.move_ip(self.direction[0]*self.speed,
                          self.direction[1]*self.speed)
        if not SCREENRECT.contains(self.rect):
            self.kill()


class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = Color('white')
        self.lastscore = -1
        self.score = 0
        self.update()
        self.rect = self.image.get_rect().move(10, 450)

    def update(self):
        if self.score != self.lastscore:
            self.lastscore = self.score
            msg = "Score: %d" % self.score
            self.image = self.font.render(msg, 0, self.color)


class Game(object):

    def __init__(self):
        # Initialize pygame
        os.environ['SDL_VIDEO_CENTERED'] = 'center'
        pygame.init()
        #pygame.mixer = None
        if pygame.mixer and not pygame.mixer.get_init():
            print ('Warning, no sound')
            pygame.mixer = None

        # Set the display mode
        winstyle = 0  # |FULLSCREEN
        bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
        self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

        self.load_assets()

        self.alien_reload_cooldown = 0
        self.score = 0
        self.aliens = None
        self.shots = None
        self.bombs = None
        self.all = None
        self.lastalien = None
        self.kills = None
        self.clock = None
        self.nui_engine = None
        self.score_sprite = None

    def load_assets(self):
        # Load images, assign to sprite classes
        # (do this before the classes are used, after screen setup)
        img = load_image('player1.gif')
        Player.images = [img, pygame.transform.flip(img, 1, 0)]
        img = load_image('explosion1.gif')
        Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
        Alien.images = load_images('alien1.gif', 'alien2.gif', 'alien3.gif')
        Bomb.images = [load_image('bomb.gif')]
        Shot.images = [load_image('shot.gif')]
        img = load_image('gun.gif')
        Gun.images = [pygame.transform.flip(img, 1, 0), img]

        # decorate the game window
        icon = pygame.transform.scale(Alien.images[0], (32, 32))
        pygame.display.set_icon(icon)
        pygame.display.set_caption('Game with NUI Support')
        pygame.mouse.set_visible(0)

        # create the background, tile the bgd image
        bgdtile = load_image('background.gif')
        self.background = pygame.Surface(SCREENRECT.size)
        for x in range(0, SCREENRECT.width, bgdtile.get_width()):
            self.background.blit(bgdtile, (x, 0))

        # load the sound effects
        self.boom_sound = load_sound('boom.wav')
        global shoot_sound
        shoot_sound = load_sound('car_door.wav')
        #if pygame.mixer:
            #music = os.path.join(main_dir, 'data', 'house_lo.wav')
            #pygame.mixer.music.load(music)
            #pygame.mixer.music.play(-1)

    def reset_nui(self):
        self.nui_engine = algo.NUIEngine()

    def reset(self):
        random.seed(0)
        # Initialize Game Groups
        self.aliens = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.all = pygame.sprite.OrderedUpdates()  # Not RenderUpdates
        self.lastalien = pygame.sprite.GroupSingle()

        # assign default groups to each sprite class
        Player.containers = self.all
        Alien.containers = self.aliens, self.all, self.lastalien
        Shot.containers = self.shots, self.all
        Bomb.containers = self.bombs, self.all
        Explosion.containers = self.all
        Score.containers = self.all
        Gun.containers = self.all

        # Create Some Starting Values
        self.alien_reload_cooldown = ALIEN_COOLDOWN
        self.kills = 0
        self.clock = pygame.time.Clock()
        self.score = 0

        # initialize our starting sprites
        self.player = Player()
        self.guns = (Gun(0, self.player), Gun(1, self.player))
        self.player.guns = self.guns
        if pygame.font:
            self.score_sprite = Score()
            self.all.add(self.score_sprite)

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def level_loop(self):
        frame = 0
        while self.player.alive():

            # get input
            for event in pygame.event.get():
                if event.type == QUIT or \
                        (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return False
            keystate = pygame.key.get_pressed()

            # clear/erase the last drawn sprites
            self.all.clear(self.screen, self.background)

            # update all the sprites
            self.score_sprite.score = self.score
            self.all.update()

            # handle NUI input
            self.nui_engine.update()
            if self.nui_engine.face_position:
                self.player.setppos(int(self.nui_engine.face_position[0]*640),
                                    int(self.nui_engine.face_position[1]*480))
            if self.nui_engine.left_degrees is not None:
                self.player.aim_to(self.nui_engine.left_degrees, 0)
            if self.nui_engine.right_degrees is not None:
                self.player.aim_to(self.nui_engine.right_degrees, 1)

            # handle player input
            direction_x = keystate[K_RIGHT] - keystate[K_LEFT]
            direction_y = keystate[K_DOWN] - keystate[K_UP]
            self.player.move(direction_x, direction_y)

            if keystate[pygame.K_q]:
                self.player.aim_turn(1, 0)
            if keystate[pygame.K_a]:
                self.player.aim_turn(-1, 0)
            if keystate[pygame.K_w]:
                self.player.aim_turn(1, 1)
            if keystate[pygame.K_s]:
                self.player.aim_turn(-1, 1)

            if frame % 15 == 0:
                self.player.fire()

            if frame > ALIEN_FIRST:
                # Create new alien
                if self.alien_reload_cooldown:
                    self.alien_reload_cooldown -= 1
                elif not int(random.random() * ALIEN_ODDS):
                    Alien()
                    self.alien_reload_cooldown = ALIEN_COOLDOWN

            # Drop bombs
            if self.lastalien and not int(random.random() * BOMB_ODDS):
                vec = np.float32(self.player.rect.center) - np.float32(self.lastalien.sprite.rect.center)
                vec /= np.linalg.norm(vec)
                Bomb(self.lastalien.sprite.rect.center, vec)

            # Detect collisions
            for alien in pygame.sprite.spritecollide(self.player, self.aliens, 1):
                self.boom_sound.play()
                Explosion(alien)
                Explosion(self.player)
                self.score += 1
                self.player.kill()

            for alien in pygame.sprite.groupcollide(self.shots, self.aliens, 1, 1).keys():
                self.boom_sound.play()
                Explosion(alien)
                self.score += 1

            for bomb in pygame.sprite.spritecollide(self.player, self.bombs, 1):
                self.boom_sound.play()
                Explosion(self.player)
                Explosion(bomb)
                self.player.kill()

            for bomb in pygame.sprite.groupcollide(self.shots, self.bombs, 1, 1).keys():
                self.boom_sound.play()
                Explosion(bomb)
                bomb.kill()
                self.score += 1

            # draw the scene
            dirty = self.all.draw(self.screen)
            pygame.display.update(dirty)

            # cap the framerate
            self.clock.tick(40)
            frame += 1
        return True

    def main_loop(self):
        self.reset_nui()
        while True:
            self.reset()
            if not self.level_loop():
                break

    def __del__(self):
        if pygame.mixer:
            pygame.mixer.music.fadeout(1000)
        pygame.time.wait(1000)
        pygame.quit()

# call the "main" function if running this script
if __name__ == '__main__':
    game = Game()
    game.main_loop()
