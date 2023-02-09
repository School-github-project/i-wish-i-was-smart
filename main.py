import pygame
import random
import os
import sys
import mysql.connector

# sql connection for stats
import mysql.connector

sqlobj = mysql.connector.connect(host="localhost", user="root", password="1234")
pyobj = sqlobj.cursor()
pyobj.execute('create database if not exists zzap')
pyobj.execute('use zzap')
pyobj.execute('create table if not exists zapping (highscores integer primary key,bomb integer, games integer, '
              'virus integer,shots_fired integer, shots_hit integer)')
# noinspection PyBroadException
try:
    pyobj.execute('insert into zapping values (0,0,0,0,0,0)')

except:
    pass
# -----------------------------------------------------------------------------------------
# Gets the path of the file used
GamePath = os.path.dirname(__file__)
# -----------------------------------------------------------------------------------------
# for centering screen
os.environ['SDL_VIDEO_CENTERED'] = '1'
# initializing pygame
pygame.init()
# -----------------------------------------------------------------------------------------
# for display info
display_info = pygame.display.Info()
# for max size
screen_width = display_info.current_w - 10
screen_length = display_info.current_h - 50
screen = pygame.display.set_mode((screen_width, screen_length), pygame.RESIZABLE)
# getting title name
pygame.display.set_caption('ZAP!')
# getting icon path
IconPath = GamePath + r"\\download.jpg"  # Creates the path of the icon
icon = pygame.image.load(IconPath)
pygame.display.set_icon(icon)
# -----------------------------------------------------------------------------------------
# for fps
clock = pygame.time.Clock()
# while loop running so i can constantly keep bliting onto screen
running = True
# for removal of bullet after asteroid death and knowing whether the asteroid collides with bullet's
collision_asteroid_bullet = False
# for attack of spaceship and asteroids so I can end game
collision_spaceship_asteroid = False
# for removal of multiple spaceships
col_spaceship = False
# for noticing if laser and spaceship collide so laser can be removed
col = False
# for noticing if bomb and laser collide so laser can be removed
collision_bomb_laser = False
# for noticing if lightning and laser collide so laser can be removed
collision_lightning_laser = False
# for noticing if lightning and spaceship collide
collision_lightning_spaceship = False
# for noticing if bomb and spaceship collide
collision_bomb_spaceship = False
# for rest
HasReset = False
# -----------------------------------------------------------------------------------------
# for multiple enemy timer
spawn_enemy = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_enemy, 1000)
# for increasing speed of the asteroids
asteroid_speed = pygame.USEREVENT + 1
pygame.time.set_timer(asteroid_speed, 3000)
# -----------------------------------------------------------------------------------------
# getting font path
FontPath = GamePath + r'\Graphics\ARCADECLASSIC.ttf'
# for score and game over purposes
Text = pygame.font.Font(FontPath, 50)
# getting background path
bgPath = GamePath + r"\\ok_proper.jpg"
bg = pygame.image.load(bgPath)
# transforming the background to screen size
bg_pic = pygame.transform.scale(bg, (screen_width, screen_length))
# -----------------------------------------------------------------------------------------
# multiple enemies list
Asteroid_rect_list = []
isGameOver = False
# for score
score_value = 0
# for pause purposes
paused = False
# for removing the code
leave = True
# for increasing speed of the asteroid as time progresses
speed_inc = False
just_to_change_speed = True
# -----------------------------------------------------------------------------------------
# bomb path
bomb_path = GamePath + r'\Graphics\bomb.png'
# lighning path
speed_down_path = GamePath + r'\Graphics\speed down.png'


# -----------------------------------------------------------------------------------------


class Bullet(pygame.sprite.Sprite):
    """
    A class to represent the Bullet
    Has 2 methods
        -> __init__ :
                1) takes 2 parameters
                    -> position of the bullet
                    -> speed of the bullet, on default to be 5
                2) initiates the following attributes when the class is automatically called
                    -> image
                    -> rect
                    -> speed
                    -> pos
        -> update :
                1) This function helps in moving the bullets
                2) Checks if it goes out of bounds or collides with any object so as to Delete the bullet from screen

    """

    def __init__(self, pos, speed=5):
        # initializing the sprite function
        super().__init__()
        # creating the texture for the bullet
        self.image = pygame.Surface((4, 20))
        self.image.fill('White')
        # getting the rectangle
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.pos = pos

    def update(self):
        global collision_asteroid_bullet, col, collision_bomb_laser, collision_lightning_laser, HasReset
        # moving the bullets
        self.rect.y -= self.speed
        screen.blit(self.image, self.rect)
        # if it goes out of bounds, if it goes out of screen length, if it collides with the asteroids,
        # if it collides with multiple asteroids
        if self.rect.y <= -50 or self.rect.y >= screen_length + 50 or collision_asteroid_bullet or col or \
                collision_lightning_laser or collision_bomb_laser or HasReset:
            self.kill()
            # making it false so the next one can take care
            collision_asteroid_bullet = False
            # making it false so the next one can take care
            col = False
            # making it false so the next one can take care
            collision_bomb_laser = False
            # making it false so the next one can take care
            collision_lightning_laser = False
            HasReset = False


class Spaceship(pygame.sprite.Sprite):
    """
    This is a Class for the spaceship/player
    There are 5 methods
        -> __init__ :
            1) Initialises the game with the following attributes:
                -> image
                -> rectangle
                -> speed
                -> laser time
                -> laser cooldown
                -> ready to shoot
                -> shoot to put it in a Group
        -> movement:
            1) Used for movement of the ship
        -> shoot laser:
            1) Adding the Bullet Class to the shoot attribute which already behaves as an List
        -> recharge:
            1) Used for setting a limit for shooting the bullet. Here is where laser time and the cooldown is used
        -> update:
            1) Calls all the functions in one function to make it easier to call the function
    """
    # getting the spaceship path
    SpaceshipPath = GamePath + r"\Graphics\spaceship.png"

    def __init__(self):
        # initializing the sprite function
        super().__init__()

        # loading the image
        self.image = pygame.image.load(Spaceship.SpaceshipPath)
        self.rect = self.image.get_rect(bottomleft=(screen_width - 100, screen_length))
        self.speed = 15
        self.laser_time = 0
        # laser_time and laser_cooldown both are used for the purpose of recharging the bullet
        # if u don't understand see def recharge
        self.laser_cool_down = 500
        # for shooting the bullet
        self.ready = True
        # for creating the Group so we can add Bullet class onto it and make it a list, so it becomes easier to find
        # the collision
        self.shoot = pygame.sprite.Group()

    def movement(self):
        global paused
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right + self.speed < screen_width:
            # moving it right
            self.rect.x += self.speed
        elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.x - self.speed > 0:
            # moving it left
            self.rect.x -= self.speed
        elif keys[pygame.K_SPACE] and self.ready:
            # space to shoot
            self.shoot_laser()
            self.ready = False
            # after the above command laser_time will be called only once since this block wont run anymore
            self.laser_time = pygame.time.get_ticks()
            pyobj.execute('update zapping set shots_fired = shots_fired + 1')
        elif keys[pygame.K_p] or keys[pygame.K_ESCAPE]:
            # for the pause(i.e p or esc)
            paused = True

    def shoot_laser(self):
        # adding the Bullet Class
        self.shoot.add(Bullet(self.rect.center))

    def recharge(self):
        # if its not ready
        if not self.ready:
            # time_of_laser will be called multiple times
            time_of_laser = pygame.time.get_ticks()
            # checking the difference below so cooldown can be made
            if time_of_laser - self.laser_time >= self.laser_cool_down:
                # making the shot ready
                self.ready = True

    def update(self):
        # using multiple functions so as to call them all at once
        self.movement()
        self.recharge()
        self.shoot.update()


class Asteroid(pygame.sprite.Sprite):
    """
    This is a class for the Asteroid/Rock/Enemy.
    It has 6 methods
        -> __init__ :
            1) Initialises the game with the following attributes:
                -> image
                -> rectangle
                -> speed
        -> Collizion:
            1) This is to check if the singular Asteroid is being collided
        -> spawn_more_enemies :
            1) This is to make sure that more enemies can be spawned in the screen to make the game difficult for the
            player
        -> moving :
            1) This is to move the Asteroid/Rock/Enemy across the screen
        -> inc_screen :
            1) To increase the speed as time goes
        -> update :
            1) Since we will be using it as a Group/GroupSingle which has an inbuilt update function, we are overriding
            it so as to use it later
            2) Calls all the functions in one function to make it easier to call the function
    """
    # getting the path of the asteroid
    AsteroidPath = GamePath + r"\Graphics\mass.png"

    def __init__(self):
        # initializing the sprite function
        super().__init__()
        # getting image
        self.image = pygame.image.load(Asteroid.AsteroidPath)
        # creating the rect
        self.rect = self.image.get_rect(bottomleft=(random.randrange(20, screen_width - 100), 0))
        self.speed = 2

    def collizion(self):
        global isGameOver, score_value
        # checking if bullet collided
        if collision_asteroid_bullet or HasReset:
            if collision_asteroid_bullet:
                # if collided, then changing the position of it completely
                score_value = score_value + 10
                pyobj.execute('update zapping set shots_hit= shots_hit + 1')
            self.rect.bottomleft = (random.randrange(20, screen_width - 100), 0)
        # checking if spaceship collided
        if collision_spaceship_asteroid:
            # if collided, then making isGameOver true
            isGameOver = True

    def spawn_more_enemies(self):
        global running, isGameOver
        # checking if Asteroid_rect_list is not empty
        if Asteroid_rect_list:
            for Asteroid_rect in Asteroid_rect_list:
                # moving the asteroid
                Asteroid_rect.y += self.speed
                screen.blit(self.image, Asteroid_rect)
                if Asteroid_rect.y > screen_length:
                    isGameOver = True

    def moving(self):
        global isGameOver
        self.rect.y += self.speed
        if self.rect.y > screen_length:
            isGameOver = True
        screen.blit(self.image, self.rect)

    def inc_speed(self):
        global speed_inc
        if speed_inc:
            self.speed += 0.3
            speed_inc = False

    def update(self):
        global just_to_change_speed
        # using update since sprite already has an update function and we're overriding it so in times of
        # grouped sprites we'll be able to call all the functions plus this helps in combining everything so we
        # can make it easier
        self.collizion()
        self.spawn_more_enemies()
        self.inc_speed()
        self.moving()
        if self.speed != 2 and just_to_change_speed:
            self.speed = 2
            just_to_change_speed = False


class Button:
    """
    This is a class to make a button.
    It has 3 methods
        -> __init__:
            1) Takes the following parameters:
                -> x position of the button
                -> y position of the button
                -> width and length of the button picture
                -> text to place on the button, the default value will be ''
                -> text_colour for the colour of the text placed inside the button, takes only tuple values
                -> size of the text
            2) Initializes the game with the following attributes:
                -> x position of the button
                -> y position of the button
                -> width and length of the button picture
                -> Text for usage of adding text
                -> text to place on the button, the default value will be ''
                -> text_colour for the colour of the text placed inside the button, takes only tuple values
                -> size of the text
                -> rectangle of the button
        -> click:
            1) Returns True if the mouse clicks with the button
            2) Takes 1 parameter
                -> event is taken as a parameter instead of running a loop constantly
        -> showing:
            1) Shows the Button on the screen
    """

    # here having multiple parameters so I don't have to D.R.Y(don't repeat yourself)
    def __init__(self, x, y, width, length, text='', text_colour=(0, 0, 255), size=50):
        if not isinstance(text_colour, tuple):
            raise Exception('Text colour takes Tuple ')
        self.x = x
        self.y = y
        self.width = width
        self.length = length
        self.Text = pygame.font.Font(FontPath, size)
        self.text = Text.render(text, True, text_colour)
        imagepath = GamePath + r"\\Graphics\\button pic.png"
        gg = pygame.image.load(imagepath)
        self.image = pygame.transform.scale(gg, (self.width, self.length))
        # creating a canvas/surface to store the button on
        # self.surface = pygame.Surface((self.width, self.length))
        # self.surface.fill(colour)
        # creating the rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.length)

    # again same reason as above made it in multiple parameters so I don't have to D.R.Y
    def click(self, event):
        global isGameOver
        # get mouse position
        mouse_pos = pygame.mouse.get_pos()
        # see if Mouse Buttons are pressed
        mouse_press = pygame.mouse.get_pressed()
        # first to check if mouse button downwards
        if event.type == pygame.MOUSEBUTTONDOWN:
            # now for left click
            if mouse_press[0]:
                if self.rect.collidepoint(mouse_pos):
                    # returning True here so I can use this function as an if statement
                    return True

    def showing(self):
        # I did not use update here because click function will be used differently
        screen.blit(self.image, (self.x, self.y))
        screen.blit(self.text, (self.x + 12, self.y + 12))


class Bomb(pygame.sprite.Sprite):
    """
    This is a class for the bomb/lightning debuff which automatically kills you if touched or shot.
    It has 6 methods.
        -> __init__ :
            1) Initialises the game with the following attributes:
                -> image for the bomb
                -> rectangle of the bomb
                -> cooldown is taken to note difference from the 2 debuffs
                -> speed of the debuff
                -> ready to exit, which is used as a timer
                -> time at which it was sent for the use of a timer
            2) It takes 2 parameters
                -> image path of the bomb
                -> cooldown is taken to note difference from the 2 debuffs
        -> moving:
            1) moves the debuff
        -> send:
            1) sends the debuff across the screen using the timer
        -> collision_bomb:
            1) for the collision of bomb debuff
        -> collision_lightning
            1) collision of lighning debuff
    """

    # having multiple parameters here too so I don't have to have multiple D.R.Y
    def __init__(self, path, cooldown):
        # initializing Sprite Class inheritance
        super().__init__()
        gg = pygame.image.load(path)
        # transforming scale to have the pixels good enough
        self.image = pygame.transform.scale(gg, (80, 80))
        self.rect = self.image.get_rect(bottomleft=(random.randrange(20, screen_width - 100), 0))
        self.speed = 5
        # ready to go used as a timer
        self.ready_to_go = True
        # cooldown for the recharging
        self.cooldown = cooldown
        # time in which it was sent from the top
        self.sent_time = 0

    def moving(self):
        # after taking the shot it need to stay still so we know the ticks at which we needed it
        if self.ready_to_go:
            self.sent_time = pygame.time.get_ticks()
            self.rect.x = random.randrange(20, screen_width - 100)
            self.rect.y = -5
            self.ready_to_go = False
        # so as to kill the thingy
        if self.rect.y >= -5:
            self.rect.y += self.speed
            screen.blit(self.image, self.rect)
        if self.rect.y > screen_length:
            self.rect.y = -100
        if HasReset:
            self.rect.y = -100

    def send(self):
        # uses same ideology as bullet recharge (still don't know why I didn't just use a timer)
        if not self.ready_to_go:
            time_shot = pygame.time.get_ticks()
            if time_shot - self.sent_time >= self.cooldown:
                self.ready_to_go = True

    def collision_bomb(self):
        global isGameOver, collision_bomb_spaceship
        if self.cooldown == 10000:
            if collision_bomb_spaceship or collision_bomb_laser:
                self.rect.y = -100
                collision_bomb_spaceship = False
                isGameOver = True

    def collision_lighning(self):
        global isGameOver, collision_lightning_spaceship
        if self.cooldown == 8000:
            if collision_lightning_spaceship or collision_lightning_laser:
                self.rect.y = -100
                collision_lightning_spaceship = False
                isGameOver = True

    def update(self):
        global just_to_change_speed
        # using update since sprite already has an update function and we're overriding it so in times of
        # grouped sprites we'll be able to call all the functions plus this helps in combining everything so we
        # can make it easier
        self.moving()
        self.send()
        self.collision_bomb()
        self.collision_lighning()


def pause():
    """
    This Function is used for making the pause ui along with it's functions
    """
    global paused, bg_pic, isGameOver, screen_length, screen_width, leave
    while paused and leave:
        # using the button class for this
        resume_button = Button(500, 300, 200, 80, 'resume')
        # using button class for this
        quit_button = Button(500, 500, 150, 80, 'quit')
        screen.blit(bg_pic, (0, 0))
        for event in pygame.event.get():
            # quitting when button is pressed
            if event.type == pygame.QUIT:
                leave = False
                sys.exit()
            # for resizing
            elif event.type == pygame.VIDEORESIZE:
                screen_length = event.h
                screen_width = event.w
                bg_pic = pygame.transform.scale(bg, (screen_width, screen_length))
            # this below is why I didn't add an update function in Button Class
            if resume_button.click(event):
                paused = False
                main()
            if quit_button.click(event):
                leave = False
                sys.exit()
        # adding the text for paused
        texting = Text.render('Paused', True, (0, 0, 255))
        # drawing the screen in the pic
        screen.blit(bg_pic, (0, 0))
        # drawing the text in the screen
        screen.blit(texting, (600, 30))
        # shows the button on screen
        resume_button.showing()
        # shows the button on screen
        quit_button.showing()
        if paused:
            score(10, 10)
        pygame.display.update()


# -----------------------------------------------------------------------------------------
# spaceship
spaceship = Spaceship()
# -----------------------------------------------------------------------------------------
# asteroid
Aster = pygame.sprite.Group()
Aster.add(Asteroid())
# -----------------------------------------------------------------------------------------
# debuffs
BigBomb = pygame.sprite.GroupSingle()
BigBomb.add(Bomb(bomb_path, 10000))
lightning = pygame.sprite.GroupSingle()
lightning.add(Bomb(speed_down_path, 8000))


def collision_checks():
    """
    This function is used for detecting the collision of the singular Asteroid created by the asteroid class.
    """
    global collision_asteroid_bullet, collision_spaceship_asteroid, collision_bomb_laser, collision_lightning_laser, \
        collision_bomb_spaceship, collision_lightning_spaceship
    # making sure the Group(list) is not empty
    if spaceship.shoot:
        # going through each iteration for multiple lasers
        for laser in spaceship.shoot:
            # collision with Asteroid Group
            if pygame.sprite.spritecollide(laser, Aster, False):
                collision_asteroid_bullet = True
            if pygame.sprite.spritecollide(laser, BigBomb, False):
                collision_bomb_laser = True
            if pygame.sprite.spritecollide(laser, lightning, False):
                collision_lightning_laser = True
    # spaceship collision with Asteroid group
    if pygame.sprite.spritecollide(spaceship, Aster, False):
        collision_spaceship_asteroid = True
    if pygame.sprite.spritecollide(spaceship, BigBomb, False):
        collision_bomb_spaceship = True
        pyobj.execute('update zapping set bomb = bomb + 1')
    if pygame.sprite.spritecollide(spaceship, lightning, False):
        collision_lightning_spaceship = True
        pyobj.execute('update zapping set virus = virus + 1')


def collision_many():
    """
    This function is used for detecting the collisions of the multiple asteroids created in the spawn_more_enemies
    method in the Asteroid class
    """
    global col_spaceship, col, score_value
    # making sure the Group(list) is not empty
    if spaceship.shoot:
        # going through each laser in the spaceship
        for laser in spaceship.shoot:
            # going through each rectangle in the multiple enemies list
            for astteroid_rect in Asteroid_rect_list:
                # checking if the 2 rectangles collide with each other
                if laser.rect.colliderect(astteroid_rect):
                    # removing this rectangle from the list so while bliting too it gets removes
                    Asteroid_rect_list.remove(astteroid_rect)
                    # calling this so as to removing the laser fired
                    col = True
                    # adding score
                    score_value = score_value + 10
                # checking if spaceship and rect collides
                if spaceship.rect.colliderect(astteroid_rect):
                    col_spaceship = True


def score(x, y):
    """
    This function is used for showing the score on the screen.
    It takes 2 parameters
        1) x value for placement of score
        2) y value for placemet of score
    """
    scoring = Text.render('Score ' + str(score_value), True, (255, 255, 255))
    screen.blit(scoring, (x, y))


def game_over():
    """
    This function is used for creating the Game Over Ui and it's required functions
    """
    global isGameOver, screen_length, screen_width, bg_pic, HasReset
    # updating the games in the sql
    pyobj.execute('update zapping set games = games + 1')
    # creating a str score value
    new_score = str(score_value)
    # checking whether higscore already exists in the sql
    try:
        pyobj.execute(f'insert zapping(highscores) values({new_score})')
    except:
        score(10, 10)
    # while game still runs
    while isGameOver:
        main_menu_button = Button(300, 500, 220, 90, 'restart ')
        new_button = Button(300, 300, 265, 85, 'main menu')
        quit_button = Button(300, 100, 145, 75, 'quit')
        for event in pygame.event.get():
            # quitting
            if event.type == pygame.QUIT:
                isGameOver = False
                sys.exit()
            # resizing
            elif event.type == pygame.VIDEORESIZE:
                screen_length = event.h
                screen_width = event.w
                bg_pic = pygame.transform.scale(bg, (screen_width, screen_length))
            if main_menu_button.click(event):
                HasReset = True
                reset()
                main()
            if new_button.click(event):
                HasReset = True
                reset()
            # quitting game
            if quit_button.click(event):
                isGameOver = False
        texting = Text.render('GAME OVER', True, (0, 0, 255))
        screen.blit(bg_pic, (0, 0))
        screen.blit(texting, (600, 30))
        main_menu_button.showing()
        quit_button.showing()
        new_button.showing()
        if isGameOver:
            score(10, 10)
        pygame.display.update()


def reset():
    """
    This function is used in converting all the variables required to change when a player chooses to retry the game
    """
    global isGameOver, Asteroid_rect_list, collision_asteroid_bullet, collision_spaceship_asteroid, \
        col_spaceship, col, collision_bomb_laser, collision_lightning_laser, collision_lightning_spaceship, \
        collision_bomb_spaceship, paused, leave, score_value, just_to_change_speed
    isGameOver = False
    Asteroid_rect_list = []
    pygame.time.set_timer(spawn_enemy, 3000)
    collision_asteroid_bullet = False
    # for attack of spaceship and asteroids
    collision_spaceship_asteroid = False
    # for removal of multiple spaceships
    col_spaceship = False
    # for noticing if laser and spaceship collide so laser can be removed
    col = False
    # for noticing if bomb and laser collide so laser can be removed
    collision_bomb_laser = False
    # for noticing if lightning and laser collide so laser can be removed
    collision_lightning_laser = False
    # for noticing if lightning and spaceship collide
    collision_lightning_spaceship = False
    # for noticing if bomb and spaceship collide
    collision_bomb_spaceship = False
    paused = False
    leave = True
    score_value = 0
    just_to_change_speed = True


def statistics():
    """
    This function imports the stats python file for statistics.
    """
    import stats
    stats.f()


def menu():
    """
    This function is used for the menu ui and it's respective required functions
    """
    global running, screen_length, screen_width, bg_pic
    while running:
        play_button = Button(80, 100, 130, 80, "Play")
        rules_button = Button(80, 300, 160, 80, "Stats")
        quit_button = Button(80, 500, 130, 90, "Quit")
        for event in pygame.event.get():
            # quitting when button is pressed
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            # for resizing
            elif event.type == pygame.VIDEORESIZE:
                screen_length = event.h
                screen_width = event.w
                bg_pic = pygame.transform.scale(bg, (screen_width, screen_length))
            # this below is why I didn't add an update function in Button Class
            if play_button.click(event):
                reset()
                main()
            if quit_button.click(event):
                running = False
            if rules_button.click(event):
                statistics()
        # bliting background
        screen.blit(bg_pic, (0, 0))
        # converting the spaceship image to make it big
        new_spaceship_image = pygame.transform.scale(spaceship.image, (300, 300))
        screen.blit(new_spaceship_image, (screen_width - 550, screen_length - 700))
        play_button.showing()
        rules_button.showing()
        quit_button.showing()
        new_Text = pygame.font.Font(FontPath, 32)
        AGJ = 'Aarya G J'
        APR = 'Arvind Prabhu'
        MVK = 'Madhav Venkat'
        SS = 'Sreekar S'
        LNS = 'L N Sudharshan'
        proper_BYtext = new_Text.render('ZAP Made By ', True, (0, 0, 255))
        proper_AGJtext = new_Text.render(AGJ, True, (0, 0, 255))
        proper_APRtext = new_Text.render(APR, True, (0, 0, 255))
        proper_MVKtext = new_Text.render(MVK, True, (0, 0, 255))
        proper_SStext = new_Text.render(SS, True, (0, 0, 255))
        proper_LNStext = new_Text.render(LNS, True, (0, 0, 255))
        screen.blit(proper_BYtext, (screen_width - 550, screen_length - 350))
        screen.blit(proper_AGJtext, (screen_width - 500, screen_length - 300))
        screen.blit(proper_APRtext, (screen_width - 500, screen_length - 250))
        screen.blit(proper_MVKtext, (screen_width - 500, screen_length - 200))
        screen.blit(proper_SStext, (screen_width - 500, screen_length - 150))
        screen.blit(proper_LNStext, (screen_width - 500, screen_length - 100))
        pygame.display.update()


def main():
    """
    This function is where the game runs for the most part.
    """
    global running, isGameOver, screen_length, screen_width, bg_pic, speed_inc
    # running is for closing the whole thing, pausing is for well pausing, and isGameOver so I can go to game over
    # screen
    while running and not isGameOver and not paused:
        # for framerate
        clock.tick(60)
        # background
        screen.blit(bg_pic, (0, 0))
        for event in pygame.event.get():
            # quitting
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            # resizing
            elif event.type == pygame.VIDEORESIZE:
                screen_length = event.h
                screen_width = event.w
                bg_pic = pygame.transform.scale(bg, (screen_width, screen_length))
            # for multiple enemy spawning timer
            elif event.type == spawn_enemy:
                # appending the list
                Asteroid_rect_list.append(
                    Asteroid().image.get_rect(bottomleft=(random.randrange(20, screen_width - 100), 0)))
                # multiple collisions
                if col_spaceship:
                    # removing the timer
                    pygame.time.set_timer(spawn_enemy, 0)
                    isGameOver = True
            # increasing the speed
            if event.type == asteroid_speed:
                speed_inc = True
        screen.blit(spaceship.image, spaceship.rect)
        # updating spaceship
        spaceship.update()
        # having the checking
        collision_checks()
        # for multiple asteroids
        collision_many()
        # bomb update
        BigBomb.update()
        # lightning update
        lightning.update()
        Aster.update()
        score(10, 10)
        pygame.display.update()

    else:
        # doing a while loop because else could be due to either running = False or paused = True or isGameOver is true
        while isGameOver:
            game_over()
        # doing a while loop because else could be due to either running = False or paused = True or isGameOver is true
        while paused:
            pause()


# calling the function
menu()
sqlobj.commit()
