import pygame as pg
import sys
import random
from settings import *
vec = pg.math.Vector2

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        #image = pg.transform.scale(image, (width // 2, height // 2))
        return image

class Ghost(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = 3
        self.groups = game.all_sprites, game.ghosts
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.ghost_images[0]
        self.image = pg.transform.scale(self.image, (24,32))
        self.rect = self.image.get_rect()
        self.pos = vec(x, y) * TILESIZE
        self.rect.topleft = self.pos
        self.startingpos = vec(x, y)
        self.pos.x +=4
        self.dest = vec(0, 0)
        self.vel = vec(0, 0)
        self.imagetimer = pg.time.get_ticks()
        self.imagecounter = 1
        self.dir = 0
        self.changedir_timer = pg.time.get_ticks()
        self.lastfootprint = 0
        self.firstfootprint = True

    def image_update(self):
        oldcenter = self.rect.center
        if self.game.player.chase ==0:
            if self.vel.x >= 0:
                self.image = pg.transform.flip(self.game.ghost_images[0], True, False)
                self.image = pg.transform.scale(self.image, (24,32))
            if self.vel.x < 0:
                self.image = self.game.ghost_images[0]
                self.image = pg.transform.scale(self.image, (24,32))
            self.mask = pg.mask.from_surface(self.image)
        else:
            if self.vel.x >= 0:
                self.image = pg.transform.flip(self.game.ghost_images[3], True, False)
                self.image = pg.transform.scale(self.image, (24,32))
            if self.vel.x < 0:
                self.image = self.game.ghost_images[3]
                self.image = pg.transform.scale(self.image, (24,32))
            self.mask = pg.mask.from_surface(self.image)
        now = pg.time.get_ticks()
        if self.game.player.chase == 1 and (now - self.game.player.chase_timer) < CHASE_TIME and (now - self.game.player.chase_timer) > (CHASE_TIME - 1200):
            if (now - self.game.player.chase_timer)%300 < 150:
                self.image = pg.Surface((24, 32))
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect()
                self.rect.center = oldcenter
                #self.mask = pg.mask.from_surface(self.image)


    def move(self):
        if self.vel.x > 0 and self.pos.x>=self.dest.x:
            self.vel.x, self.vel.y = 0, 0
            self.pos.x = self.dest.x
        elif self.vel.x < 0 and self.pos.x<=self.dest.x:
            self.vel.x, self.vel.y = 0, 0
            self.pos.x = self.dest.x
        elif self.vel.y > 0 and self.pos.y>=self.dest.y:
            self.vel.y, self.vel.y = 0, 0
            self.pos.y = self.dest.y
        elif self.vel.y < 0 and self.pos.y<=self.dest.y:
            self.vel.y, self.vel.y = 0, 0
            self.pos.y = self.dest.y

        #chase code 2.0 - footprints
        if self.game.player.chase == 0:
            hits = pg.sprite.spritecollideany(self, self.game.footprints)
            if hits:
                self.dir = hits.dir
                if not self.firstfootprint:
                    if self.lastfootprint != hits:
                        hits.lifes -=1
                        self.lastfootprint = hits
                self.firstfootprint = False

        #chase code 1.0 - dimensions
        # if self.dest.y == self.game.player.dest.y:
        #     if self.dest.x < self.game.player.dest.x:
        #         self.dir = 1
        #     if self.dest.x > self.game.player.dest.x:
        #         self.dir = 3
        # elif self.dest.x == self.game.player.dest.x:
        #     if self.dest.y < self.game.player.dest.y:
        #         self.dir = 2
        #     if self.dest.y > self.game.player.dest.y:
        #         self.dir = 0

        now = pg.time.get_ticks()
        if now - self.changedir_timer > 2000:
            self.changedir_timer = now
            self.dir=random.randrange(1,5)

        if self.vel.x==0 and self.vel.y==0:
            if (self.dir % 4) == 3:
                self.vel.x = -GHOST_SPEED
                self.dest.x = self.pos.x - 32
            elif (self.dir % 4) == 1:
                self.vel.x = GHOST_SPEED
                self.dest.x = self.pos.x + 32
            elif (self.dir % 4) == 0:
                self.vel.y = -GHOST_SPEED
                self.dest.y = self.pos.y - 32
            elif (self.dir % 4) == 2:
                self.vel.y = GHOST_SPEED
                self.dest.y = self.pos.y + 32



        if self.dest.x > WIDTH:
            self.pos.x = -32
            self.dest.x = 4
        if self.dest.x < 0:
            self.pos.x = WIDTH
            self.dest.x = WIDTH - 28
        if self.dest.y > HEIGHT:
            self.pos.y = -32
            self.dest.y = 0
        if self.dest.y < 0:
            self.pos.y = HEIGHT
            self.dest.y = HEIGHT - 32

        self.pos += self.vel * self.game.dt

        if self.vel.x != 0 and abs(self.pos.x-self.dest.x)<32:
            self.rect.topleft = self.pos
        elif self.vel.y != 0 and abs(self.pos.y-self.dest.y)<32:
            self.rect.topleft = self.pos
        elif self.vel.x==0 and self.vel.y==0:
            self.rect.topleft = self.pos

    def collide_with_walls(self, dir):
        if dir == 'x':
            self.rect.inflate_ip(4,0)
            hits = pg.sprite.spritecollide(self, self.game.walls_for_ghosts, False)
            self.rect.inflate_ip(-4,0)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - 28
                elif self.vel.x < 0:
                    self.pos.x = hits[0].rect.right + 4
                self.vel.x = 0
                self.rect.x = self.pos.x
                self.dir = random.randrange(1,5)
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls_for_ghosts, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                elif self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y
                self.dir = random.randrange(1,5)

    def update(self):
        self.move()
        self.collide_with_walls('x')
        self.collide_with_walls('y')
        self.image_update()

class Footprint(pg.sprite.Sprite):
    def __init__(self, game, x, y, directory):
        self._layer = 2
        self.groups = game.all_sprites, game.footprints
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((32, 32))
        if game.showfootprint == True:
            if directory == 3:
                self.image.fill(YELLOW)
            elif directory == 0:
                self.image.fill(RED)
            elif directory == 1:
                self.image.fill(BLUE)
            elif directory == 2:
                self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.game = game
        self.pos = vec(x, y)
        self.pos.x += 0
        self.pos.y += 0
        self.rect.topleft = self.pos
        self.creation_time = pg.time.get_ticks()
        self.dir = directory
        self.lifes = GHOSTS_THAT_FOLLOW + 1

    def update(self):
        now = pg.time.get_ticks()
        if (now - self.creation_time > FOOTPRINT_LIFETIME) or self.lifes <= 0:
            spawnboost = random.randrange(1,101)
            if spawnboost == 1:
                Boost(self.game, self.pos.x, self.pos.y, 'points')
            if spawnboost == 2:
                Boost(self.game, self.pos.x, self.pos.y, 'life')
            if spawnboost == 3:
                Boost(self.game, self.pos.x, self.pos.y, 'wall')
            self.kill()


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = 3
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.load_images()
        self.image = self.standing_frames[0]
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (24,32))
        self.rect = self.image.get_rect()
        self.pos = vec(x, y) * TILESIZE
        self.pos.x +=4
        self.dest = vec(1, 1) * TILESIZE
        self.dest.x +=4
        self.olddest = vec(0, 0)
        self.canscore = True
        self.vel = vec(0, 0)
        self.lasthit = 0
        self.firsttimecollide = True
        self.imagetimer = pg.time.get_ticks()
        self.imagecounter = 1
        self.chase=0
        self.chase_timer=pg.time.get_ticks()
        self.lasttime_dead=pg.time.get_ticks()
        self.creation=pg.time.get_ticks()




    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(69, 255, 66, 82)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)

        self.walk_frames_r = [self.game.spritesheet.get_image(0, 339, 68, 83),
                              self.game.spritesheet.get_image(0, 0, 70, 86)]
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))

        self.walk_frames_up = [self.game.spritesheet.get_image(69, 173, 66, 82),
                                self.game.spritesheet.get_image(70, 0, 66, 82)]
        for frame in self.walk_frames_up:
            frame.set_colorkey(BLACK)

    def changeimage(self):
        oldcenter = self.rect.center
        now1 = pg.time.get_ticks()
        if now1 - self.imagetimer > 200:
            self.imagetimer = now1
            if self.vel.y == 0 and self.vel.x == 0:
                    self.image = self.standing_frames[0]
            if self.vel.x < 0:
                if (self.imagecounter % 2) == 0:
                    self.image = self.walk_frames_l[1]
                else:
                    self.image = self.walk_frames_l[0]
            if self.vel.x > 0:
                if (self.imagecounter % 2) == 0:
                    self.image = self.walk_frames_r[1]
                else:
                    self.image = self.walk_frames_r[0]
            if self.vel.y > 0:
                self.image = self.standing_frames[0]
            if self.vel.y < 0:
                if (self.imagecounter % 2) == 0:
                    self.image = self.walk_frames_up[1]
                else:
                    self.image = self.walk_frames_up[0]
            if ((now1 - self.creation) < 2000) and (self.imagecounter % 2)==0:
                self.image = pg.Surface((24, 32))
            self.imagecounter +=1
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (24,32))
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
        self.mask = pg.mask.from_surface(self.image)

    def makefootprint(self, directory):
        if directory == 'left':
            direct = 3
        elif directory == 'up':
            direct = 0
        elif directory == 'right':
            direct = 1
        elif directory == 'down':
            direct = 2
        pg.sprite.spritecollide(self, self.game.footprints, True)
        now = pg.time.get_ticks()
        Footprint(self.game, self.dest.x-4, self.dest.y, direct)

    def move(self):
        if self.vel.x > 0 and self.pos.x>=self.dest.x:
            self.vel.x, self.vel.y = 0, 0
            self.pos.x = self.dest.x
        elif self.vel.x < 0 and self.pos.x<=self.dest.x:
            self.vel.x, self.vel.y = 0, 0
            self.pos.x = self.dest.x
        elif self.vel.y > 0 and self.pos.y>=self.dest.y:
            self.vel.y, self.vel.y = 0, 0
            self.pos.y = self.dest.y
        elif self.vel.y < 0 and self.pos.y<=self.dest.y:
            self.vel.y, self.vel.y = 0, 0
            self.pos.y = self.dest.y

        if self.vel.x==0 and self.vel.y==0:
            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                self.vel.x = -PLAYER_SPEED
                self.makefootprint('left')
                self.dest.x = self.pos.x - 32
                self.dest.y = self.pos.y
            elif keys[pg.K_RIGHT] or keys[pg.K_d]:
                self.vel.x = PLAYER_SPEED
                self.makefootprint('right')
                self.dest.x = self.pos.x + 32
                self.dest.y = self.pos.y
            elif keys[pg.K_UP] or keys[pg.K_w]:
                self.vel.y = -PLAYER_SPEED
                self.makefootprint('up')
                self.dest.y = self.pos.y - 32
                self.dest.x = self.pos.x
            elif keys[pg.K_DOWN] or keys[pg.K_s]:
                self.vel.y = PLAYER_SPEED
                self.makefootprint('down')
                self.dest.y = self.pos.y + 32
                self.dest.x = self.pos.x



        if self.dest.x > WIDTH:
            self.pos.x = -32
            self.dest.x = 4
        if self.dest.x < 0:
            self.pos.x = WIDTH
            self.dest.x = WIDTH - 28
        if self.dest.y > HEIGHT:
            self.pos.y = -32
            self.dest.y = 0
        if self.dest.y < 0:
            self.pos.y = HEIGHT
            self.dest.y = HEIGHT - 32

        self.pos += self.vel * self.game.dt
        self.rect.topleft = self.pos

    def collide_with_walls(self, dir):
        if dir == 'x':
            self.rect.inflate_ip(4,0)
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            self.rect.inflate_ip(-4,0)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - 28
                elif self.vel.x < 0:
                    self.pos.x = hits[0].rect.right + 4
                self.vel.x = 0
                self.rect.x = self.pos.x
                self.dest.x = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                elif self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y
                self.dest.y = self.pos.y

    def collide_with_points(self):
                hits = pg.sprite.spritecollideany(self, self.game.points)
                if not self.firsttimecollide:
                    if hits:
                        if self.lasthit != hits:
                            self.lasthit = hits
                            self.canscore = False
                            hits.pointlevel -= 1
                            self.game.score +=10
                            self.game.eatpoints_sound.stop()
                            self.game.eatpoints_sound.play()
                        elif self.canscore:
                            self.lasthit = hits
                            hits.pointlevel -= 1
                            self.game.score +=10
                            self.game.eatpoints_sound.stop()
                            self.game.eatpoints_sound.play()
                    else:
                        self.canscore=True
                if self.firsttimecollide and hits:
                    self.lasthit = hits
                    self.canscore = False
                    hits.pointlevel -= 1
                    self.game.score +=10
                    self.game.eatpoints_sound.stop()
                    self.game.eatpoints_sound.play()
                    self.firsttimecollide = False

    def collide_with_ghosts(self):
        hits = pg.sprite.spritecollideany(self, self.game.ghosts)
        if hits:
            hit = pg.sprite.spritecollideany(self, self.game.ghosts, pg.sprite.collide_mask)
            now = pg.time.get_ticks()
            if self.chase==0:
                if hit and now - self.game.lasttime_dead > 2000:
                    self.game.lifes -=1
                    self.game.die_sound.play()
                    self.game.lasttime_dead = now
                    self.creation=now
                    # self.kill()
                    # self.game.player = Player(self.game, self.game.playerpos.x, self.game.playerpos.y)
                    self.pos = self.game.playerpos * TILESIZE
                    self.pos.x +=4
                    self.vel.x = 0
                    self.vel.y = 0
            if self.chase==1:
                if hit:
                    self.game.eatghost_sound.play()
                    Ghost(self.game, hits.startingpos.x, hits.startingpos.y)
                    hits.kill()



        if self.game.lifes == 0:
            self.game.playing = False
            self.game.endgame = True

    def collide_with_boosts(self):
        hits = pg.sprite.spritecollideany(self, self.game.boosts)
        if hits:
            if hits.kind == 'eat':
                self.game.chase_sound.play()
                self.chase=1
                self.chase_timer = pg.time.get_ticks()
            elif hits.kind == 'points':
                self.game.powerup_sound.play()
                self.game.score += 200
            elif hits.kind == 'life':
                self.game.gainlife_sound.play()
                if self.game.lifes < 3:
                    self.game.lifes +=1
            hits.kill()


    def update(self):
        self.move()
        self.collide_with_walls('x')
        self.collide_with_walls('y')
        self.collide_with_points()
        self.collide_with_ghosts()
        self.collide_with_boosts()
        self.changeimage()
        now = pg.time.get_ticks()
        if now - self.chase_timer > CHASE_TIME:
            self.chase=0


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = 2
        self.groups = game.all_sprites, game.walls, game.walls_for_ghosts
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        number = random.randrange(1,101)
        if number < 10:
            self.image = game.wall_images[1]
        elif number < 30:
            self.image = game.wall_images[2]
        else:
            self.image = game.wall_images[0]
        self.image = pg.transform.scale(self.image, (32,32))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Spawn(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = 2
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        number = random.randrange(1,101)
        self.image = game.spawn_image
        self.image = pg.transform.scale(self.image, (32,32))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Point(pg.sprite.Sprite):
    def __init__(self, game, x, y, level):
        self._layer = 2
        self.groups = game.all_sprites, game.points
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.pointlevel = level
        self.image = game.points_images[self.pointlevel-1]
        self.image2 = game.points_images[1]
        self.image3 = game.points_images[0]
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (24,24))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE + 4
        self.rect.y = y * TILESIZE + 4

    def update(self):
        if self.pointlevel==0:
            self.kill()
        if self.pointlevel==2:
            self.image = self.image2
            self.image = pg.transform.scale(self.image, (24,24))
        if self.pointlevel==1:
            self.image = self.image3
            self.image = pg.transform.scale(self.image, (24,24))

class Boost(pg.sprite.Sprite):
    def __init__(self, game, x, y, kind):
        self._layer = 3
        if kind =='wall':
            self.groups = game.all_sprites, game.walls_for_ghosts, game.walls
        else:
            self.groups = game.all_sprites, game.boosts
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.pos = vec(x,y)
        if kind == 'points':
            self.image = game.boost_images[6]
            self.image = pg.transform.scale(self.image, (32,32))
        elif kind == 'life':
            self.image = game.boost_images[0]
            self.image = pg.transform.scale(self.image, (24,24))
            self.pos.x += 4
            self.pos.y += 4
        elif kind == 'eat':
            self.image = game.boost_images[4]
            self.image = pg.transform.scale(self.image, (32,32))
        elif kind == 'wall':
            self.image = game.boost_images[3]
            self.image = pg.transform.scale(self.image, (32,32))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.kind = kind
        self.creation_time = pg.time.get_ticks()

    def update(self):
        now = pg.time.get_ticks()
        if now - self.creation_time > BOOSTS_TIME and self.kind != 'eat':
            self.kill()
