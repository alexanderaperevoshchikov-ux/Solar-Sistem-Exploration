import pygame as pg

pg.init()

pg.display.set_caption("Кебрал спейс программ")

screen = pg.display.set_mode((1500,1000))


x = 525
y = 450

c = 0

while True:
    screen.fill(pg.Color("black"))
    pg.draw.circle(screen,pg.Color("blue"),(750,500),200)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
    keys = pg.key.get_pressed()
    if keys[pg.K_a]:
        c -= 0.0001
    if keys[pg.K_d]:
        c += 0.0001
    y -= 0.1
    x += c
    pg.draw.rect(screen,pg.Color("grey"),(x, y, 25, 25))
    pg.display.flip()
