from ursina import *
import math

app = Ursina()

window.title = "Solar System 3D - Comet Tilt & Orbits"
window.color = color.black
EditorCamera()

PointLight(position=(0, 0, 0), color=color.white, range=100)
AmbientLight(color=color.rgba(80, 80, 80, 255))

scale = 1
speed = 1
CENTER_X = 0
CENTER_Z = 0
show_orbits = True


class Planet:
    def __init__(self, body_color, radius, orbit_radius, speed, Main_planet=None, angle=0, is_ring=False, tilt=0):
        self.color = body_color
        self.radius2 = radius / 5
        self.orbit_radius2 = orbit_radius / 10
        self.speed = speed
        self.angle = 0
        self.Main_planet = Main_planet
        self.angle2 = angle
        self.is_ring = is_ring
        self.tilt = tilt  # Наклон плоскости орбиты в градусах

        # Контейнер для наклона (Pivot)
        self.orbit_pivot = Entity(rotation_x=self.tilt)

        self.entity = Entity(
            parent=self.orbit_pivot,
            model='sphere',
            color=self.color,
            scale=self.radius2 if not is_ring else 0
        )

        self.create_orbit_line()
        self.is_comet = False
        self.trail_timer = 0

    def create_orbit_line(self):
        # Линия орбиты создается внутри pivot, чтобы она тоже наклонялась
        self.orbit_line = Entity(
            parent=self.orbit_pivot,
            model=Mesh(
                vertices=[
                    (math.cos(math.radians(i)) * self.orbit_radius2, 0, math.sin(math.radians(i)) * self.orbit_radius2)
                    for i in range(361)],
                mode='line',
                thickness=2
            ),
            color=color.rgba(self.color.r, self.color.g, self.color.b, 80),
            enabled=show_orbits
        )

    def update_logic(self, current_scale, global_speed):
        self.angle += self.speed * global_speed
        self.orbit_radius = self.orbit_radius2 * current_scale

        if not self.is_ring:
            self.entity.scale = self.radius2 * current_scale

        # Базовая позиция центра вращения
        base_pos = self.Main_planet.entity.world_position if self.Main_planet else Vec3(0, 0, 0)
        self.orbit_pivot.position = base_pos
        self.orbit_line.scale = current_scale


        lx = self.orbit_radius * math.cos(math.radians(self.angle + self.angle2))
        lz = self.orbit_radius * math.sin(math.radians(self.angle))

        self.entity.position = (lx, 0, lz)
        self.orbit_line.enabled = show_orbits

        if self.is_comet:
            self.draw_trail()

    def draw_trail(self):
        self.trail_timer += time.dt
        if self.trail_timer > 0.000005:
            # Частицы создаются в мировых координатах
            t = Entity(model='sphere', position=self.entity.world_position,
                       scale=self.entity.scale * 0.7, color=color.rgba(200, 200, 255, 100))
            t.animate_scale(0.5, duration=0.05)
            destroy(t, delay=0.1)
            self.trail_timer = 0


# Солнце
sun = Entity(model='sphere', color=color.yellow, scale=5, emissive_color=color.yellow)


mercury = Planet(color.gray, 1.2, 50, 1, tilt=7)
venus = Planet(color.orange, 1.45, 80, 1.5, tilt=3.4)
earth = Planet(color.blue, 2, 170, 0.7, tilt=0)
mars = Planet(color.red, 1.55, 230, 0.5, tilt=1.8)
jupiter = Planet(color.rgb(200, 150, 100), 10, 400, 0.3, tilt=1.3)

saturn_body = Planet(color.rgb(196, 176, 139), 8.2, 600, 0.2, tilt=2.5)
saturn_ring = Planet(color.rgb(196, 176, 139), 17, 0.1, 0, Main_planet=saturn_body, is_ring=True)

uranus = Planet(color.cyan, 3.7, 690, 0.15, tilt=0.8)
uranus_ring = Planet(color.gray, 8, 0.1, 0, Main_planet=uranus, is_ring=True)

neptune = Planet(color.rgb(65, 105, 225), 3.57, 750, 0.1, tilt=1.8)

# Комета
haley = Planet(color.rgb(1, 1, 1), 1, 800, 0.07, angle=50, tilt=18)
haley.is_comet = True

# Спутники
moon = Planet(color.light_gray, 1, 15, 3.0, Main_planet=earth)
io = Planet(color.yellow, 1.25, 18, 1.55, Main_planet=jupiter)
titanium = Planet(color.orange, 1.2, 22, 1.1, Main_planet=saturn_body)

planets = [mercury, venus, earth, mars, jupiter, saturn_body, saturn_ring,
           uranus, uranus_ring, neptune, haley, moon, io, titanium]


def input(key):
    global show_orbits
    if key == 'f':
        show_orbits = not show_orbits


def update():
    global scale, speed
    if held_keys['right arrow']: speed += 0.1
    if held_keys['left arrow']:  speed -= 0.1
    if held_keys['space']:       speed = 1

    for p in planets:
        p.update_logic(scale, speed)


app.run()