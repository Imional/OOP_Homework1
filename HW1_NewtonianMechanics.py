class PhysicalObject:
    def __init__(self, name, mass, x0=0.0, v0=0.0):
        self.name = name
        self.mass = mass
        self.x = x0
        self.v = v0

    def update(self, dt):
        a = self.compute_force() / self.mass
        self.v += a * dt
        self.x += self.v * dt

    def describe(self):
        return f"{self.name}: position {self.x:.3f}, velocity {self.v:.3f}"

    def compute_force(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

class FallingObject(PhysicalObject):
    def __init__(self, name, mass, g=9.81):
        super().__init__(name, mass)
        self.g = g

    def compute_force(self):
        return -self.mass * self.g    
    
class FreeObject(PhysicalObject):
    def __init__(self, name, mass):
        super().__init__(name, mass)

    def compute_force(self):
        return 0.0

class SpringMass(PhysicalObject):
    def __init__(self, name, mass, k=10, x0=0.1, v0=0.0):
        super().__init__(name, mass, x0=x0, v0=v0)
        self.k = k

    def compute_force(self):
        return -self.k * self.x
    

if __name__ == "__main__":
    ball = FallingObject("ball", 1)
    dt = 0.01
    t = 0
    while t < 3:
        ball.update(dt)
        t += dt
    print(ball.describe())
    
    objects = [
        FreeObject("Glider", 1.0),
        FallingObject("Ball", 1.0),
        SpringMass("Oscillator", 1.0, k=10, x0=0.1)
    ]
    dt = 0.01
    for obj in objects:
        t = 0
        while t < 3:
            obj.update(dt)
            t += dt
        print(obj.describe())