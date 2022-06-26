
import pygame as pg
from pygame.locals import *
import sys
import random
import copy

pg.init()

'''Game works only on python 3.6 and higher, because I make use sprite group ordered
   feature that don't exist in before pygame 1.80 and below Python 3.6'''


class Text:

    def __init__(self, text, pos, font_size=40, fontcolor=Color('black')):
        self.text = text
        self.pos = pos
        self.fontname = 'verdana.ttf'
        self.fontsize = font_size
        self.fontcolor = fontcolor
        self.set_font()
        self.render(self.text)

    def set_font(self):
        """Set the Font object from name and size."""
        self.font = pg.font.SysFont(self.fontname, self.fontsize)

    def render(self, text='Default'):
        # """Render custom text into an image."""
        self.img = self.font.render(text, True, self.fontcolor)
        self.rect = self.img.get_rect()
        self.rect.topleft = self.pos

    def draw(self):
        """Draw the text image to the screen."""
        Game.screen.blit(self.img, self.rect)


class Food(pg.sprite.Sprite):
    def __init__(self, picture, pos_x, pos_y, timer=4):
        super().__init__()
        self.x, self.y = pos_x, pos_y
        self.image = pg.image.load(picture).convert_alpha()
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y
        self.pos = self.rect.x, self.rect.y
        self.food_sound = pg.mixer.Sound('slash.wav')
        self.food_time_counter = 0
        self.timer = timer

    def food_timer(self):
        if self.food_time_counter >= self.timer:
            return True
        else:
            self.food_time_counter += 1
            return False

    def food_eaten(self):
        self.food_sound.play()

    @classmethod
    def create_food(cls, picture, pos_x, pos_y, timer):
        return cls(picture, pos_x, pos_y, timer)


# TODO remove scren from Snake class
class Snake(pg.sprite.Sprite):

    def __init__(self, screen_rect, picture, pos_x, pos_y, cell):
        super().__init__()
        self.screen_rect = screen_rect
        self.picture = picture
        # self.screen_rect = self.screen.get_rect()
        self.image = pg.image.load(picture).convert_alpha()
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos_x, pos_y
        self.snake_sound = pg.mixer.Sound('slash.wav')
        self.cell = cell
        self.count_frames = 0  # counting for frames
        self.old_pos = copy.copy(self.rect)
        self.f_moves = {'up': 'down', 'down': 'up',
                        'left': 'right', 'right': 'left'}
        self.last_move = None
        self.k = None

    def __irshift__(self, other):
        if not self.picture == 'snake_head.png':
            self.old_pos = self.rect.copy()
            self.rect = other.old_pos
        return self

    def oposite_direction(self, move):
        pass

    def move(self, event, speed, group, gameend):
        # self.rect.clamp_ip(self.screen_rect)
        sprite_list = group.sprites()
        self.shortcuts = {
            (K_w): 'self.move_up(self.last_move, group)',
            (K_s): 'self.move_down(self.last_move, group)',
            (K_d): 'self.move_right(self.last_move, group)',
            (K_a): 'self.move_left(self.last_move, group)'
        }

        if event:
            self.k = event.key
            if not self.count_frames % speed:  # using mod to reduce movment and have 60 fps
                if self.k in self.shortcuts and not gameend:
                    # print(speed)
                    self.old_pos = self.rect.copy()
                    exec(self.shortcuts[self.k])
                    self.last_move = copy.copy(self.k)
                    # print(k)
                    # print(self.k)
                    Game.move_tail_fun(group)
                elif gameend:
                    pass
            self.count_frames += 1

    def move_right(self, last_move, group):
        # if there is no tail, and last move isn-t oposite
        if len(group) == 1 or not last_move == K_a:
            self.rect[0] += self.cell
        else:
            self.k = last_move
            self.move_left(last_move, group)

    def move_left(self, last_move, group):
        # if there is no tail, and last move isn-t oposite
        if len(group) == 1 or not last_move == K_d:
            self.rect[0] -= self.cell
        else:
            self.k = last_move
            self.move_right(last_move, group)

    def move_up(self, last_move, group):
        if len(group) == 1 or not last_move == K_s:
            self.rect[1] -= self.cell
        else:
            self.k = last_move
            self.move_down(last_move, group)

    def move_down(self, last_move, group):
        if len(group) == 1 or not last_move == K_w:
            self.rect[1] += self.cell
        else:
            self.k = last_move
            self.move_up(last_move, group)

    def print_alive(self):
        print('IM a alive')


class Game():

    def __init__(self):
        self.x, self.y = 26, 16  # field size *snake can move on
        self.cell = 40  # individual cell size
        self.speed = 20  # movment spped *every n frames
        self.screen_width = self.x * self.cell
        self.screen_height = self.y * self.cell + 80  # screen space below main grid
        print(self.screen_width, self.screen_height)
        self.colors = {
            'BLACK': (0, 0, 0),
            'GREY': (180, 180, 180),
            'WHITE': (255, 255, 255)
        }
        Game.screen = pg.display.set_mode(
            (self.screen_width, self.screen_height))
        self.screen_rect = pg.Rect(
            0, 0, self.x * self.cell, self.y * self.cell)

        self.background = pg.Surface((self.screen_width, self.screen_height))
        self.background.fill(self.colors['WHITE'])
        self.score = 0

        # snake setup *game objects and sprite groups
        self.snake = Snake(self.screen_rect, 'snake_head.png',
                           200, 200, self.cell)
        self.snake_group = pg.sprite.Group()
        self.snake_group.add(self.snake)

        self.debugevent = self.food_time = pg.USEREVENT + 20
        pg.time.set_timer(self.food_time, 30000)

        self.food_time = pg.USEREVENT + 10
        pg.time.set_timer(self.food_time, 1000)
        self.speed_time = pg.USEREVENT + 20
        pg.time.set_timer(self.speed_time, 5000)

        self.food_group = pg.sprite.Group()
        # TODO
        self.pos = (self.cell * 1, self.y * self.cell + self.cell / 2)
        self.text_score = Text('Score', self.pos)
        self.text_end = ' '
        self.text_end_game = Text(' ', (self.screen_rect.centerx -
                                        4 * self.cell, self.screen_rect.centery - 4 * self.cell), 85, Color('red'))
        self.done = False  # bool to stop Game.run()
        self.gameend = False

    def make_tail(self):
        Tail = Snake(self.screen_rect, 'snake_tail.png',
                     self.snake.old_pos[0], self.snake.old_pos[1], self.cell)
        self.snake_group.add(Tail)

    @ staticmethod
    def move_tail_fun(group):
        sprite_list = group.sprites()
        for n in range(len(sprite_list)):
            sprite_list[n] >>= sprite_list[n - 1]

    def food_collide(self):
        contact = pg.sprite.spritecollide(
            self.snake, self.food_group, True, collided=pg.sprite.collide_mask)
        try:
            if contact[0]:
                self.score += 1
                contact[0].food_eaten()
                self.make_tail()
        except:
            pass

    def snake_collide(self):
        contact = pg.sprite.spritecollide(
            self.snake, self.snake_group, False, collided=pg.sprite.collide_mask)
        try:
            if contact[1]:
                self.snake.rect = self.snake.old_pos
                self.text_end = 'GAME END!'
                self.gameend = True
        except:
            pass

    def game_collide(self):
        x_side = self.snake.rect[0]
        y_side = self.snake.rect[1]
        if (x_side > (self.x - 1) * self.cell or x_side < 0) or (y_side > (self.y - 1) * self.cell or y_side < 0):
            self.snake.rect = self.snake.old_pos
            self.text_end = 'GAME END!'
            self.gameend = True
        self.food_collide()
        self.snake_collide()

    def grid(self):
        pg.draw.rect(self.background, (255, 255, 255), self.screen_rect)
        line_width = 3
        line_color = self.colors['GREY']
        for i in range(self.x + 1):
            for j in range(self.y + 1):
                pg.draw.line(self.background, line_color, [i, j * self.cell],
                             [self.x * self.cell, j * self.cell], line_width)
        for i in range(self.y + 1):
            for j in range(self.x + 1):
                pg.draw.line(self.background, line_color, [j * self.cell, i],
                             [j * self.cell, self.y * self.cell], line_width)

    def make_food(self, n):
        '''creates new food items with random screen time'''
        for i in range(n):
            self.food_group.add(Food.create_food('snake_food.png',
                                                 random.randrange(
                                                     0, self.x) * self.cell,
                                                 random.randrange(
                                                     0, self.y) * self.cell,
                                                 random.randrange(6, 15)))

    def food_pos(self):  # not used for now
        '''return a list with tuple (x, y) coordinates od every avalible food in sprite group'''
        return [(i.x, i.y) for i in self.food_group]

    def food_time_fun(self):
        for food in self.food_group:
            if food.food_timer():
                self.food_group.remove(food)
        if len(self.food_group) < 2:
            self.make_food(random.randrange(3, 6))

    def speed_time_fun(self):
        if self.speed > 6:
            self.speed -= 1
        else:
            self.speed = 6

    def text_render(self):
        self.text_score.render(text=f'Game score {str(self.score)}')
        self.text_score.draw()
        self.text_end_game.render(self.text_end)
        self.text_end_game.draw()

    def end_game(self):
        self.done = True
        pg.quit()
        sys.exit()

    def run(self):
        self.grid()
        self.make_food(4)
        clock = pg.time.Clock()
        event_send = {}
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_game()
                elif event.type == pg.KEYDOWN:
                    event_send = event
                # once is second event
                elif event.type == self.food_time:
                    self.food_time_fun()
                elif event.type == self.speed_time:
                    self.speed_time_fun()

            self.snake.move(event_send, self.speed,
                            self.snake_group, self.gameend)
            self.screen.blit(self.background, (0, 0))
            self.game_collide()
            self.food_group.draw(self.screen)
            self.snake_group.draw(self.screen)
            self.text_render()
            pg.display.flip()
            clock.tick(60)


if __name__ == '__main__':
    p = sys.version_info
    if int(f'{p[0]}' + f'{p[1]}') < 36:
        print('for Snake to work, you will need python 3.6 or higher')
    else:
        print('OK')
        Game().run()
