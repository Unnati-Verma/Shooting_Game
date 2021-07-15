import pygame
import os

pygame.init()  # initializing pygame

'''Variables for Creating Game Window'''
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# Game Window

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# set framerate
clock = pygame.time.Clock()
FPS = 60
# define game variables
GRAVITY = 0.75

# player action variable
moving_left = False
moving_right = False
shoot = False
# load images
# bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()

# defining colors

BG = (144, 201, 120)
RED = (255, 0, 0)


# adding background
def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))


class Solider(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)  # inheriting functionalities from Sprite class
        self.alive = True
        self.char_type = char_type
        self.speed = speed  # assigning the argument to instance
        self.shoot_cooldown = 0
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (
                    int(img.get_width() * scale), int(img.get_height() * scale)))  # scaling the image
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()  # takes the size of the image and creates a rectangle boundary
        self.rect.center = (x, y)  # positing the rectangle

    def update(self):
        self.update_animation()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variable
        dx = 0  # change in x
        dy = 0  # change in y
        # assign movement variable if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            var = self.vel_y
        dy += self.vel_y
        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False
        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery,
                        self.direction)
            bullet_group.add(bullet)


    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed)
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH - 100:
            self.kill()


# sprite groups
bullet_group = pygame.sprite.Group()

player = Solider('player', 200, 200, 3, 5)
enemy = Solider('enemy', 200, 200, 3, 5)

''' To keep running the game window'''
run = True
while run:
    clock.tick(FPS)

    draw_bg()
    # show image
    player.update_animation()
    player.draw()
    enemy.draw()

    # update and draw groups
    bullet_group.update()
    bullet_group.draw(screen)

    # update player actions
    if player.alive:
        # shoot bullets
        if shoot:
            player.shoot()
        if player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)  # 1: run
        else:
            player.update_action(0)  # 0: idle
        player.move(moving_left, moving_right)

    # event handler of pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # quit game
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # move left
                moving_left = True
            if event.key == pygame.K_d:  # move right
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:  # quit game
                run = False

        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()  # updating window with the images
pygame.quit()
