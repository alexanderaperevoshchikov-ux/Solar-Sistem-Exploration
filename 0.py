import pygame as pg
import math

pg.init()
pg.display.set_caption("Кебрал спейс программ")
screen = pg.display.set_mode((1500, 1000))
clock = pg.time.Clock()
ship_x = 700
ship_y = 500
angle = 0
move_speed = 3
rotation_speed = 0.05
running = True

while running:
    screen.fill(pg.Color("black"))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    angle -= rotation_speed
    ship_x += move_speed * math.cos(angle)
    ship_y += move_speed * math.sin(angle)
    pg.draw.circle(screen, pg.Color("blue"), (750, 500), 20)
    pg.draw.rect(screen, pg.Color("grey"), (int(ship_x), int(ship_y), 25, 25))
    pg.display.flip()
    clock.tick(60)
pg.quit()
