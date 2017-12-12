# Pacman
import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
import random

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.levelnr = 0
        self.game_folder= path.dirname(__file__)
        self.levellist = LEVEL_LIST
        self.endgame = False
        self.score = 0
        self.font_name = pg.font.match_font(FONT_NAME)
        self.playerpos = vec(0, 0)
        self.showstart = True
        self.lifes = 3
        self.showfootprint = True



    def load_data(self):
        #load images
        img_dir=path.join(self.game_folder, "img")
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        self.boost_images = []
        for img in BOOST_IMAGES:
            self.boost_images.append(pg.image.load(path.join(img_dir, img)).convert_alpha())
        self.ghost_images = []
        for img in GHOSTS_IMAGES:
            self.ghost_images.append(pg.image.load(path.join(img_dir, img)).convert_alpha())
        self.spawn_image = pg.image.load(path.join(img_dir, SPAWN_IMAGE)).convert()
        self.wall_images=[]
        for img in WALL_IMAGES[self.levellist[self.levelnr]]:
            self.wall_images.append(pg.image.load(path.join(img_dir, img)).convert())
        self.points_images=[]
        for img in POINTS_IMAGES:
            self.points_images.append(pg.image.load(path.join(img_dir, img)).convert_alpha())
        # load sounds
        snd_dir=path.join(self.game_folder, "snd")
        self.eatpoints_sound = pg.mixer.Sound(path.join(snd_dir,EATPOINTS_SOUND))
        self.eatpoints_sound.set_volume(0.05)
        self.eatghost_sound = pg.mixer.Sound(path.join(snd_dir,EATGHOST_SOUND))
        self.eatghost_sound.set_volume(0.2)
        self.gainlife_sound = pg.mixer.Sound(path.join(snd_dir,GAINLIFE_SOUND))
        self.gainlife_sound.set_volume(0.2)
        self.powerup_sound = pg.mixer.Sound(path.join(snd_dir,POWERUP_SOUND))
        self.powerup_sound.set_volume(0.2)
        self.die_sound = pg.mixer.Sound(path.join(snd_dir,DIE_SOUND))
        self.die_sound.set_volume(0.2)
        self.chase_sound = pg.mixer.Sound(path.join(snd_dir,CHASE_SOUND))
        self.chase_sound.set_volume(0.2)
        pg.mixer.music.load(path.join(snd_dir,MUSIC))
        pg.mixer.music.set_volume(0.5)

    def load_map(self):
        self.map_data = []
        levels = len(self.levellist)
        map = self.levellist[self.levelnr]
        if self.levelnr == (levels-1):
            self.endgame = True
        self.levelnr += 1
        with open(path.join(self.game_folder, map), 'rt') as f:
            for line in f:
                self.map_data.append(line)

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.boosts = pg.sprite.Group()
        self.ghosts = pg.sprite.Group()
        self.footprints = pg.sprite.Group()
        self.walls_for_ghosts = pg.sprite.Group()
        self.points = pg.sprite.Group()
        self.lasttime_dead = pg.time.get_ticks()
        self.load_data()
        self.load_map()
        # print map
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'P':
                    if self.showstart == True:
                        self.playerpos.x = col
                        self.playerpos.y = row
                        self.player = Player(self, -1, -1)
                    else:
                        self.playerpos.x = col
                        self.playerpos.y = row
                        self.player = Player(self, col, row)
                if tile == '.':
                    Point(self, col, row, 1)
                if tile == ':':
                    Point(self, col, row, 1)
                if tile == ';':
                    Point(self, col, row, 1)
                if tile == 'S':
                    Spawn(self, col, row)
                if tile == 'G':
                    Spawn(self, col, row)
                    Ghost(self, col, row)
                if tile == '$':
                    Boost(self, col*TILESIZE, row*TILESIZE, 'eat')


    def run(self):
        # game loop - set self.playing = False to end the game
        pg.mixer.music.play(loops=-1)
        self.playing = True
        self.lifes = 3
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()


    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BGCOLOR)
        #self.draw_grid()
        self.all_sprites.draw(self.screen)
        if self.showstart == True:
            self.show_start_screen()
        if self.showstart == False:
            self.draw_gui()
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if self.showstart == True:
                    self.player.pos = self.playerpos * TILESIZE
                    self.player.pos.x +=4
                    self.showstart = False
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_n:
                    self.playing = False
                if event.key == pg.K_b:
                    self.endgame = True
                    self.playing = False
                if event.key == pg.K_p:
                    if self.showfootprint == True:
                        self.showfootprint = False
                    else:
                        self.showfootprint = True
        # check for level complete
        if len(self.points)==0:
            self.playing = False


    def show_start_screen(self):
        # game splash/start screen
        s = pg.Surface((WIDTH,HEIGHT))  # the size of your rect
        s.set_alpha(128)                # alpha level
        s.fill((0,0,0))           # this fills the entire surface
        self.screen.blit(s, (0,0))
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)


    def show_go_screen(self):
        if self.endgame:# game over/continue
            pg.mixer.music.fadeout(1000)
            s = pg.Surface((WIDTH,HEIGHT))  # the size of your rect
            s.set_alpha(128)                # alpha level
            s.fill((0,0,0))           # this fills the entire surface
            self.screen.blit(s, (0,0))
            self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
            self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
            self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
            pg.display.flip()
            self.levelnr = 0
            self.endgame = False
            self.showstart = True
            self.score = 0
            self.lifes = 3
            self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    waiting = False

    def draw_text(self, text, size, color, x, y, align='mid'):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == 'mid':
            text_rect.midtop = (x, y)
        if align == 'right':
            text_rect.topright = (x, y)
        if align == 'left':
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_gui(self):
        self.draw_text("score: " + str(self.score), 20, WHITE, WIDTH-10, 4, 'right')
        for life in range(3):
            #self.draw_text("<3", 20, WHITE, 30*life+5, 5, 'left')
            if life <= self.lifes-1:
                image = self.boost_images[0]
            if life > self.lifes-1:
                image = self.boost_images[1]
            image = pg.transform.scale(image, (30,30))
            image.set_colorkey(BLACK)
            self.screen.blit(image, (35*life+1,1))

# create the game object
g = Game()
while True:
    g.new()
    g.run()
    g.show_go_screen()
