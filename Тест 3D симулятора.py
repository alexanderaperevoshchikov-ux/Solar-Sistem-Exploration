from __future__ import annotations

from math import cos, sin, pi
from pathlib import Path

from ursina import (
    Ursina, Entity, Vec3, color, time, Text,
    AmbientLight, PointLight, Mesh,
    window, application
)
from ursina.prefabs.editor_camera import EditorCamera


def file_exists(path: str) -> bool:
    return Path(path).is_file()


def texture_if_exists(path: str | None):
    if not path:
        return None
    return path if file_exists(path) else None


def clamp(x: float, a: float, b: float) -> float:
    return max(a, min(b, x))


def orbit_ring(radius: float, segments: int = 180, line_color=color.rgba(255, 255, 255, 70)) -> Entity:
    # Рисуем орбиту линией (без заливки)
    verts = []
    for i in range(segments + 1):
        t = (i / segments) * 2 * pi
        verts.append(Vec3(cos(t) * radius, 0, sin(t) * radius))

    mesh = Mesh(vertices=verts, mode="line", thickness=1)
    return Entity(model=mesh, color=line_color)


class Planet:
    def __init__(
        self,
        name: str,
        orbit_radius: float,
        period: float,
        size: float,
        body_color=color.azure,
        texture: str | None = None,
        orbit_tilt_deg: float = 0.0,
        spin_speed: float = 40.0,
        show_orbit: bool = True,
    ):
        self.name = name
        self.r = orbit_radius
        self.period = max(0.0001, period)
        self.size = size
        self.spin_speed = spin_speed
        self.theta = 0.0

        # Пивот нужен для наклона плоскости орбиты
        self.pivot = Entity(rotation=(orbit_tilt_deg, 0, 0))

        tex = texture_if_exists(texture)
        self.body = Entity(
            parent=self.pivot,
            model="sphere",
            scale=size,
            color=color.white if tex else body_color,
            texture=tex,
            position=(orbit_radius, 0, 0),
        )

        # Подпись рядом с планетой
        self.label = Text(
            text=name,
            parent=self.body,
            position=(0.9, 0.9),
            scale=1.1,
            color=color.white,
            billboard=True,
        )

        # Линия орбиты для наглядности
        self.orbit = orbit_ring(orbit_radius)
        self.orbit.parent = self.pivot
        self.orbit.enabled = show_orbit

    def update(self, time_scale: float):
        # Обновляем положение по окружности и вращение вокруг оси
        w = (2 * pi) / self.period
        self.theta += w * time.dt * time_scale

        x = self.r * cos(self.theta)
        z = self.r * sin(self.theta)
        self.body.position = Vec3(x, 0, z)

        self.body.rotation_y += self.spin_speed * time.dt * time_scale


class Comet:
    def __init__(
        self,
        name: str,
        a: float,
        e: float,
        period: float,
        size: float,
        body_color=color.light_gray,
        texture: str | None = None,
        tilt_deg: float = 25.0,
        spin_speed: float = 20.0,
        show_orbit: bool = True,
        tail_enabled: bool = True,
    ):
        self.name = name
        self.a = a
        self.e = clamp(e, 0.0, 0.95)
        self.period = max(0.0001, period)
        self.size = size
        self.spin_speed = spin_speed
        self.theta = 0.0

        # Наклон плоскости орбиты кометы
        self.pivot = Entity(rotation=(tilt_deg, 0, 0))

        tex = texture_if_exists(texture)
        self.body = Entity(
            parent=self.pivot,
            model="sphere",
            scale=size,
            color=color.white if tex else body_color,
            texture=tex,
        )

        # Подпись рядом с кометой
        self.label = Text(
            text=name,
            parent=self.body,
            position=(0.9, 0.9),
            scale=1.1,
            color=color.white,
            billboard=True,
        )

        # Орбита кометы линией (по формуле r(theta))
        self.orbit = self._build_orbit_line()
        self.orbit.parent = self.pivot
        self.orbit.enabled = show_orbit

        # Хвост в виде точек, чтобы не было "вытянутой планеты"
        self.tail_enabled = tail_enabled
        self.tail: list[Entity] = []
        self.tail_max = 60
        self._last_tail_pos: Vec3 | None = None
        self.tail_min_step = 0.35  # добавляем точку, только если комета заметно сместилась

    def _r(self, theta: float) -> float:
        # Полярное уравнение эллипса с фокусом в Солнце:
        # r = a(1 - e^2) / (1 + e cos(theta))
        return (self.a * (1 - self.e * self.e)) / (1 + self.e * cos(theta))

    def _build_orbit_line(self) -> Entity:
        # Строим линию орбиты кометы по множеству точек
        seg = 260
        verts = []
        for i in range(seg + 1):
            t = (i / seg) * 2 * pi
            r = self._r(t)
            verts.append(Vec3(cos(t) * r, 0, sin(t) * r))
        mesh = Mesh(vertices=verts, mode="line", thickness=1)
        return Entity(model=mesh, color=color.rgba(200, 220, 255, 90))

    def _tail_push(self, world_pos: Vec3, strength: float):
        # Добавляем точку хвоста, но не чаще чем на заданный шаг
        if self._last_tail_pos is not None:
            if (world_pos - self._last_tail_pos).length() < self.tail_min_step:
                return
        self._last_tail_pos = world_pos

        dot = Entity(
            model="sphere",
            scale=0.04 + 0.07 * strength,
            position=world_pos,
            color=color.rgba(200, 220, 255, int(20 + 120 * strength)),
        )
        self.tail.insert(0, dot)

        if len(self.tail) > self.tail_max:
            self.tail[-1].disable()
            self.tail.pop()

    def _tail_decay(self, n: int):
        # Быстро "съедаем" хвост, когда комета далеко от Солнца
        for _ in range(n):
            if self.tail:
                self.tail[-1].disable()
                self.tail.pop()

    def update(self, time_scale: float):
        # Двигаем комету по эллипсу и обновляем хвост
        w = (2 * pi) / self.period
        self.theta += w * time.dt * time_scale

        r = self._r(self.theta)
        local_pos = Vec3(cos(self.theta) * r, 0, sin(self.theta) * r)
        self.body.position = local_pos
        self.body.rotation_y += self.spin_speed * time.dt * time_scale

        if not self.tail_enabled:
            return

        # Интенсивность хвоста зависит от расстояния до Солнца
        start = self.a * 0.95
        end = self.a * 1.9
        strength = 1 - clamp((r - start) / (end - start), 0.0, 1.0)

        if strength > 0:
            world_pos = self.pivot.world_position + local_pos
            self._tail_push(world_pos, strength)
        else:
            self._tail_decay(3)


app = Ursina()
application.title = "3D симулятор Солнечной системы (Ursina)"

# Отключаем счетчики справа сверху
application.development_mode = False
window.fps_counter.enabled = False
window.entity_counter.enabled = False
window.collider_counter.enabled = False

# Нейтральный фон
window.color = color.black

# Свет в сцене
AmbientLight(color=color.rgba(90, 90, 90, 255))
PointLight(color=color.white, position=(0, 0, 0))

# Солнце
sun_tex = texture_if_exists("assets/textures/sun.jpg")
sun = Entity(
    model="sphere",
    scale=3.2,
    color=color.white if sun_tex else color.yellow,
    texture=sun_tex,
)

# Камера: ПКМ - обзор, WASD - движение, колесо - зум
EditorCamera(rotation_smoothing=2, panning_speed=20, enabled=True)

# Подсказка (умещается по ширине)
hint = Text(
    text=(
        "Камера: ПКМ - обзор, WASD - движение, колесо - зум\n"
        "Симуляция: 1-5 - скорость, Space - пауза\n"
        "O - орбиты вкл-выкл, T - хвост кометы, H - подсказка"
    ),
    position=(-0.88, 0.46),
    origin=(0, 0),
    scale=0.85,
    color=color.white,
)

# Статусная строка
status = Text(
    text="",
    position=(-0.88, 0.34),
    origin=(0, 0),
    scale=0.9,
    color=color.white,
)

time_scale = 1.0
paused = False
orbits_on = True

# Планеты
planets = [
    Planet("Меркурий", 4, 6, 0.25, body_color=color.orange, texture="assets/textures/mercury.jpg", orbit_tilt_deg=3, spin_speed=80, show_orbit=orbits_on),
    Planet("Венера", 6, 10, 0.35, body_color=color.rgb(255, 220, 180), texture="assets/textures/venus.jpg", orbit_tilt_deg=2, spin_speed=50, show_orbit=orbits_on),
    Planet("Земля", 8, 14, 0.38, body_color=color.azure, texture="assets/textures/earth.jpg", orbit_tilt_deg=0, spin_speed=90, show_orbit=orbits_on),
    Planet("Марс", 10, 18, 0.30, body_color=color.red, texture="assets/textures/mars.jpg", orbit_tilt_deg=1, spin_speed=70, show_orbit=orbits_on),
    Planet("Юпитер", 14, 30, 0.90, body_color=color.rgb(220, 180, 140), texture="assets/textures/jupiter.jpg", orbit_tilt_deg=1, spin_speed=60, show_orbit=orbits_on),
    Planet("Сатурн", 18, 42, 0.80, body_color=color.rgb(240, 220, 170), texture="assets/textures/saturn.jpg", orbit_tilt_deg=2, spin_speed=55, show_orbit=orbits_on),
    Planet("Уран", 22, 54, 0.65, body_color=color.cyan, texture="assets/textures/uranus.jpg", orbit_tilt_deg=4, spin_speed=45, show_orbit=orbits_on),
    Planet("Нептун", 26, 66, 0.62, body_color=color.blue, texture="assets/textures/neptune.jpg", orbit_tilt_deg=3, spin_speed=45, show_orbit=orbits_on),
]

# Луна вокруг Земли
earth = next(p for p in planets if p.name == "Земля")
moon_pivot = Entity(parent=earth.body)
moon = Planet("Луна", 0.9, 2.2, 0.12, body_color=color.light_gray, texture="assets/textures/moon.jpg", orbit_tilt_deg=10, spin_speed=0, show_orbit=orbits_on)
moon.pivot.parent = moon_pivot
moon.orbit.parent = moon_pivot

# Комета
comet = Comet(
    "Комета",
    a=16,
    e=0.65,
    period=38,
    size=0.18,
    texture="assets/textures/comet.jpg",
    tilt_deg=25,
    show_orbit=orbits_on,
    tail_enabled=True,
)


def set_orbits(enabled: bool):
    # Включаем или выключаем все орбиты
    for p in planets:
        p.orbit.enabled = enabled
    moon.orbit.enabled = enabled
    comet.orbit.enabled = enabled


def input(key):
    global time_scale, paused, orbits_on

    # Пауза
    if key == "space":
        paused = not paused

    # Скорость времени
    if key == "1":
        time_scale = 0.5
    if key == "2":
        time_scale = 1.0
    if key == "3":
        time_scale = 2.0
    if key == "4":
        time_scale = 4.0
    if key == "5":
        time_scale = 8.0

    # Подсказка
    if key == "h":
        hint.enabled = not hint.enabled

    # Орбиты
    if key == "o":
        orbits_on = not orbits_on
        set_orbits(orbits_on)

    # Хвост кометы
    if key == "t":
        comet.tail_enabled = not comet.tail_enabled
        if not comet.tail_enabled:
            for d in comet.tail:
                d.disable()
            comet.tail.clear()
            comet._last_tail_pos = None


def update():
    # Обновляем движение объектов, если не пауза
    if not paused:
        for p in planets:
            p.update(time_scale)
        moon.update(time_scale)
        comet.update(time_scale)

    # Обновляем строку статуса
    status.text = (
        f"Скорость: x{time_scale} | Пауза: {'Да' if paused else 'Нет'} | "
        f"Орбиты: {'Вкл' if orbits_on else 'Выкл'} | "
        f"Хвост: {'Вкл' if comet.tail_enabled else 'Выкл'}"
    )


app.run()
