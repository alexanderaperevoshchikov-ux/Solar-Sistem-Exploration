import pygame as pg
import math

pg.init()
pg.display.set_caption("Кебрал спейс программ")
screen = pg.display.set_mode((1500, 1000))
clock = pg.time.Clock()
ship_x = 750.0
ship_y = 500.0
angle = 0.0
move_speed = 5
rotation_speed = 0.07
running = True

while running:
    screen.fill(pg.Color("black"))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT] or keys[pg.K_a]:
        angle -= rotation_speed
    if keys[pg.K_RIGHT] or keys[pg.K_d]:
        angle += rotation_speed

    pg.draw.circle(screen, pg.Color("blue"), (750, 500), 20)
    ship_x += move_speed * math.cos(angle)
    ship_y += move_speed * math.sin(angle)
    pg.draw.rect(screen, pg.Color("grey"), (int(ship_x), int(ship_y), 25, 25))
    pg.display.flip()
    clock.tick(60)
pg.quit()
