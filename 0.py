import pygame as pg
import math
import random

# --- Инициализация ---
pg.init()
WIDTH, HEIGHT = 1500, 1000
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Real-Scale Space Program")
clock = pg.time.Clock()
font = pg.font.SysFont("Consolas", 20, bold=True)

G = 60000
dt_base = 0.02
time_warp = 1
zoom = 0.00005

sun_mass = 990000000
sun_radius = 9900000
sun_x, planet_y = 0, 0

earth_mass = 800000000
earth_radius = 450000
earth_dist = 180000000
earth_angle = 0
earth_orbit_speed = 0.00000005

moon_mass = 800000000
moon_radius = 450000
moon_dist = 99000000000
moon_angle = 0
moon_orbit_speed = 0.00000005

ship_x = sun_radius + 500000.0
ship_y = 0.0
vx = 0.0
vy = -math.sqrt(G * sun_mass / ship_x)
angle = -math.pi / 2
rotation_speed = 0.06
rocket_mass = 100.0
thrust_power = 60000

stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(300)]


def get_physics_for_earth(x, y, m_angle):
    mx = math.cos(m_angle) * earth_dist
    my = math.sin(m_angle) * earth_dist


    dxp, dyp = sun_x - x, planet_y - y
    dist_p = math.sqrt(dxp ** 2 + dyp ** 2)
    accel_p = (G * sun_mass) / (dist_p ** 2) if dist_p > 1000 else 0


    dxm, dym = mx - x, my - y
    dist_m = math.sqrt(dxm ** 2 + dym ** 2)
    accel_m = (G * earth_mass) / (dist_m ** 2) if dist_m > 1000 else 0

    ax = (accel_p * dxp / dist_p) + (accel_m * dxm / dist_m)
    ay = (accel_p * dyp / dist_p) + (accel_m * dym / dist_m)
    return ax, ay, dist_p, dist_m, mx, my

def get_physics_for_moon(x, y, m_angle):
    mx = math.cos(m_angle) * moon_dist
    my = math.sin(m_angle) * moon_dist


    dxp, dyp = sun_x - x, planet_y - y
    dist_p = math.sqrt(dxp ** 2 + dyp ** 2)
    accel_p = (G * sun_mass) / (dist_p ** 2) if dist_p > 1000 else 0


    dxm, dym = mx - x, my - y
    dist_m = math.sqrt(dxm ** 2 + dym ** 2)
    accel_m = (G * earth_mass) / (dist_m ** 2) if dist_m > 1000 else 0

    ax = (accel_p * dxp / dist_p) + (accel_m * dxm / dist_m)
    ay = (accel_p * dyp / dist_p) + (accel_m * dym / dist_m)
    return ax, ay, dist_p, dist_m, mx, my


def to_scr(wx, wy):
    sx = (wx - ship_x) * zoom + WIDTH // 2
    sy = (wy - ship_y) * zoom + HEIGHT // 2
    return int(sx), int(sy)


show_orbit = True
running = True

while running:
    sim_dt = dt_base * time_warp

    screen.fill((3, 3, 10))
    for s in stars: pg.draw.circle(screen, (120, 120, 120), s, 1)

    for event in pg.event.get():
        if event.type == pg.QUIT: running = False
        if event.type == pg.MOUSEWHEEL:
            zoom = max(1e-8, min(0.1, zoom + event.y * (zoom * 0.4)))
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE: show_orbit = not show_orbit
            if event.key == pg.K_PERIOD: time_warp = min(100, time_warp * 2)
            if event.key == pg.K_COMMA: time_warp = max(1, time_warp // 2)


    earth_angle += earth_orbit_speed * time_warp
    ax, ay, dist_p, dist_m, cur_mx, cur_my = get_physics_for_earth(ship_x, ship_y, earth_angle)
    ax_m, ay_m, dist_p_m, dist_m_m, cur_mx_m, cur_my_m = get_physics_for_moon(ax, ay, earth_angle)
    moon_angle += moon_orbit_speed * time_warp
    keys = pg.key.get_pressed()
    if keys[pg.K_a] or keys[pg.K_LEFT]:  angle -= rotation_speed
    if keys[pg.K_d] or keys[pg.K_RIGHT]: angle += rotation_speed

    thrust_active = keys[pg.K_w] or keys[pg.K_UP]
    if thrust_active:
        ax += (math.cos(angle) * thrust_power) / rocket_mass
        ay += (math.sin(angle) * thrust_power) / rocket_mass




    vx += ax * sim_dt
    vy += ay * sim_dt
    ship_x += vx * sim_dt
    ship_y += vy * sim_dt

    for d, rad in [(dist_p, sun_radius), (dist_m, earth_radius)]:
        if d < rad:
            if math.sqrt(vx ** 2 + vy ** 2) < 500:  # Посадка
                vx, vy = 0, 0
                time_warp = 1
            else:
                ship_x, ship_y = sun_radius + 500000, 0
                vx, vy = 0, -math.sqrt(G * sun_mass / ship_x)
                time_warp = 1

    if show_orbit:
        tx, ty, tvx, tvy, tma = ship_x, ship_y, vx, vy, earth_angle
        orbit_pts = []
        pred_dt = sim_dt * 100 if time_warp < 50 else sim_dt * 20
        for i in range(1500):
            tax, tay, _, _, _, _ = get_physics_for_earth(tx, ty, tma)
            tvx += tax * pred_dt;
            tvy += tay * pred_dt
            tx += tvx * pred_dt;
            ty += tvy * pred_dt
            tma += earth_orbit_speed * pred_dt
            if i % 10 == 0: orbit_pts.append(to_scr(tx, ty))
        if len(orbit_pts) > 1:
            pg.draw.lines(screen, (0, 255, 150), False, orbit_pts, 1)

    p_scr = to_scr(0, 0)
    pg.draw.circle(screen, (255, 255, 255), p_scr, int(sun_radius * zoom))
    pg.draw.circle(screen, (255, 255, 255), p_scr, int((sun_radius + 100000) * zoom), 1)  # Атмосфера
    e_scr = to_scr(cur_mx, cur_my)
    m_scr = to_scr(cur_mx, cur_my_m)
    pg.draw.circle(screen, (30, 80, 200), e_scr, int(earth_radius * zoom))
    pg.draw.circle(screen, (255, 255, 255), m_scr, int((moon_radius * zoom)))
    # pg.draw.circle(screen, (255, 255, 255), )
    sx, sy = WIDTH // 2, HEIGHT // 2
    sz = max(5, int(40 * zoom * 200))
    pts = [(sx + math.cos(angle + a) * sz, sy + math.sin(angle + a) * sz) for a in [0, 2.5, -2.5]]
    pg.draw.polygon(screen, (255, 255, 255), pts)
    if thrust_active:
        fx, fy = sx - math.cos(angle) * sz, sy - math.sin(angle) * sz
        pg.draw.circle(screen, (255, 100, 0), (int(fx), int(fy)), int(sz / 2))

    # --- UI ---
    speed = math.sqrt(vx ** 2 + vy ** 2)
    ui_data = [
        f"SPEED: {int(speed)} m/s",
        f"ALTITUDE: {int((dist_p - sun_radius) / 1000)} km",
        f"TIME WARP: {time_warp}x (Keys < >)",
        f"DIST TO earth: {int(dist_m / 1000)} km"
    ]
    for i, t in enumerate(ui_data):
        screen.blit(font.render(t, True, (0, 255, 150)), (20, 20 + i * 25))

    pg.display.flip()
    clock.tick(60)

pg.quit()
