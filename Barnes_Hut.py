import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Point:
    """Properties of a point."""
    def __init__(self, x, y, vx=0, vy=0, m=1):
        self.velocity = np.array([vx, vy])
        self.position = np.array([x, y])
        self.mass = m
        self.f_net = np.array([0.0, 0.0])

    def __repr__(self):
        return f"(x,y,m): ({self.position[0]:.2f}, {self.position[1]:.2f}, {self.mass})"

class Rectangle:
    """Creating a Rectangle."""
    def __init__(self, w, h, x=0, y=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.bodies = []
        self.total_mass = 0
        self.com = np.array([0.0, 0.0])

    def __repr__(self):
        return f'(Bodies: {len(self.bodies)}, COM: ({self.com[0]:.2f}, {self.com[1]:.2f}), Mass: {self.total_mass})'

    def update_total_mass(self):
        if self.bodies:
            self.total_mass = sum(body.mass for body in self.bodies)
            return True
        return False

    def update_COM(self):
        if self.bodies:
            com = np.sum([body.mass * body.position for body in self.bodies], axis=0)
            self.com = com / self.total_mass
            return True
        return False

    def contains(self, point):
        return (self.x <= point.position[0] < self.x + self.w and
                self.y <= point.position[1] < self.y + self.h)

    def insert(self, point):
        if not self.contains(point):
            return False
        self.bodies.append(point)
        self.update_total_mass()
        self.update_COM()
        return True

class Quadtree:
    """Creating a quadtree."""
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.divided = False
        self.northeast = None
        self.southeast = None
        self.northwest = None
        self.southwest = None

    def subdivide(self):
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.w, self.boundary.h
        half_w, half_h = w / 2, h / 2

        ne = Rectangle(half_w, half_h, x + half_w, y)
        self.northeast = Quadtree(ne, self.capacity)

        se = Rectangle(half_w, half_h, x + half_w, y + half_h)
        self.southeast = Quadtree(se, self.capacity)

        sw = Rectangle(half_w, half_h, x, y + half_h)
        self.southwest = Quadtree(sw, self.capacity)

        nw = Rectangle(half_w, half_h, x, y)
        self.northwest = Quadtree(nw, self.capacity)

        self.divided = True

        for body in self.boundary.bodies:
            self.northeast.insert(body)
            self.southeast.insert(body)
            self.southwest.insert(body)
            self.northwest.insert(body)

    def insert(self, point):
        if not self.boundary.contains(point):
            return False

        if len(self.boundary.bodies) < self.capacity or not self.divided:
            self.boundary.insert(point)
            return True

        if not self.divided:
            self.subdivide()

        return (self.northeast.insert(point) or
                self.southeast.insert(point) or
                self.southwest.insert(point) or
                self.northwest.insert(point))

    def compute_force(self, point):
        if not self.boundary.bodies:
            return

        com_point = Point(self.boundary.com[0], self.boundary.com[1], m=self.boundary.total_mass)
        d = np.linalg.norm(com_point.position - point.position)

        if d == 0:
            return

        s = self.boundary.w
        theta = s / d

        if theta <= 0.5:  # Threshold for approximation
            f = self.calculate_force(com_point, point)
            point.f_net += f
        elif self.divided:
            self.northeast.compute_force(point)
            self.southeast.compute_force(point)
            self.southwest.compute_force(point)
            self.northwest.compute_force(point)
        else:
            for body in self.boundary.bodies:
                if body is not point:
                    f = self.calculate_force(body, point)
                    point.f_net += f

    @staticmethod
    def calculate_force(p1, p2):
        G = 5000
        r = p1.position - p2.position
        distance = np.linalg.norm(r) + 1e-10  # Avoid division by zero
        force_magnitude = G * p1.mass * p2.mass / (distance ** 2)
        return force_magnitude * r / distance

def main_loop():
    width = int(input('Suggest a width: '))
    height = int(input('Suggest a height: '))
    n_bodies = int(input('How many masses to start with? '))
    run_time = int(input('For how many time steps should it run? '))
    dt = float(input('What time step? '))
    capacity = int(input('Capacity of each quadrant: '))
    x, y = -width / 2, -height / 2
    boundary = Rectangle(width, height, x, y)
    quadtree = Quadtree(boundary, capacity)

    # Initialize bodies and random colors
    bodies = []
    colors = []
    for _ in range(n_bodies):
        px = random.uniform(x + 10, -x - 10)
        py = random.uniform(y + 10, -y - 10)
        vx = random.uniform(-60, 60)
        vy = random.uniform(-60, 60)
        mass = random.uniform(5,100)
        body = Point(px, py, vx, vy, mass)
        bodies.append(body)
        quadtree.insert(body)
        colors.append(np.random.rand(3,))  # Random RGB color

    # Set up visualization
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(x, x + width)
    ax.set_ylim(y, y + height)
    ax.set_title("Barnes-Hut Simulation")
    scat = ax.scatter([body.position[0] for body in bodies],
                      [body.position[1] for body in bodies],
                      s=[body.mass for body in bodies],
                      c=colors,
                      alpha=0.7)

    def update(frame):
        nonlocal quadtree, bodies

        for body in bodies:
            body.f_net = np.array([0.0, 0.0])

        quadtree = Quadtree(Rectangle(width, height, x, y), capacity)
        for body in bodies:
            quadtree.insert(body)

        for body in bodies:
            quadtree.compute_force(body)

        for body in bodies:
            body.velocity += body.f_net * dt
            body.position += body.velocity * dt
            body.position[0] = np.clip(body.position[0], x, x + width)
            body.position[1] = np.clip(body.position[1], y, y + height)

        scat.set_offsets(np.array([[body.position[0], body.position[1]] for body in bodies]))
        return scat,

    ani = FuncAnimation(fig, update, frames=run_time, interval=25, blit=True)
    plt.show()

if __name__ == "__main__":
    main_loop()

