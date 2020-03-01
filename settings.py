# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# GENERAL settings
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 672  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Pacman 2.0"
LEVEL_LIST = ['map1.txt','map2.txt']
BGCOLOR = DARKGREY
FONT_NAME = 'arial'
TILESIZE = 32
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# GAME settings
PLAYER_SPEED = 200
GHOST_SPEED = 180
FOOTPRINT_LIFETIME = 3000 #in ms
GHOSTS_THAT_FOLLOW = 3
CHASE_TIME = 3000
BOOSTS_TIME = 10000

#sounds
# "fastsong"
# by Betz Music
# http://friedrich-betz.de/
EATPOINTS_SOUND = 'Eat4.wav'
EATGHOST_SOUND = 'Eat3.wav'
DIE_SOUND = 'Die1.wav'
GAINLIFE_SOUND = 'gainHealth.wav'
POWERUP_SOUND = 'powerup.wav'
CHASE_SOUND = 'eating.wav'
MUSIC = 'fastsong.ogg'

# images
SPRITESHEET = "alienYellow.png"
SPAWN_IMAGE = "liquidLava.png"
BOOST_IMAGES = ['hud_heartFull.png','hud_heartEmpty.png','star.png','boxAlt.png','gemBlue.png','gemRed.png','gemYellow.png','gemGreen.png']
POINTS_IMAGES = ['coinGold.png','coinSilver.png','coinBronze.png']
GHOSTS_IMAGES = ['ghost.png', 'ghost_normal.png','ghost_hit.png','ghost2.png','ghost_dead.png']
WALL_IMAGES={}
# level 1
WALL_IMAGES['map1.txt'] = ['houseDark.png','houseDarkAlt.png','houseDarkAlt2.png']
# level 2
WALL_IMAGES['map2.txt'] = ['houseBeige.png','houseBeigeAlt.png','houseBeigeAlt2.png']
