import pygame
import math

# --- Constants ---
WIDTH, HEIGHT = 800, 800
# Attempt to set a video mode. This might still fail in a headless environment,
# but it's necessary for Pygame drawing functions.
try:
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulation des Lois de Kepler")
except pygame.error as e:
    print(f"Erreur lors de l'initialisation de Pygame : {e}")
    print("Assurez-vous d'avoir un environnement d'affichage valide (par exemple, en utilisant Xvfb).")
    # Exit gracefully if display initialization fails
    pygame.quit()
    exit()


# --- Colors ---
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)

# --- Simulation Parameters ---
AU = 149.6e9  # Astronomical Unit in meters
G = 6.67428e-11  # Gravitational Constant
SCALE = 200 / AU  # Pixels per Astronomical Unit
TIMESTEP = 3600 * 6  # 6 hours in seconds (reduced timestep for potentially smoother orbits)

# --- Visual Enhancement Parameters ---
# Factor to scale planet size based on distance from the sun
# Smaller factor means less variation in size
SIZE_SCALE_FACTOR = 0.5
BASE_PLANET_RADIUS = 5 # Base radius for visual scaling


# --- Planet Class ---
class Planet:
    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.base_radius = radius # Store original radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win):
        # Scale position for drawing and convert to integers
        # Access global constants explicitly to avoid Attribute Error in some environments
        x = int(self.x * SCALE + WIDTH / 2)
        y = int(self.y * SCALE + HEIGHT / 2)

        # Draw orbit path
        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                ox, oy = point
                # Scale orbit points and convert to integers
                # Access global constants explicitly
                ox = int(ox * SCALE + WIDTH / 2)
                oy = int(oy * SCALE + HEIGHT / 2)
                updated_points.append((ox, oy))
            # Ensure there are enough points to draw a line
            if len(updated_points) > 1:
                 pygame.draw.lines(win, self.color, False, updated_points, 1)

        # Calculate visual radius based on distance to the sun
        if self.sun:
            # Sun maintains its base radius
            visual_radius = self.base_radius
        else:
            # Scale planet radius based on distance from the sun
            # Using a simple inverse scaling with an offset to control variation
            # We use AU for a more intuitive scaling factor
            distance_in_au = self.distance_to_sun / AU
            visual_radius = int(self.base_radius / (1 + distance_in_au * SIZE_SCALE_FACTOR))
            # Ensure minimum radius
            visual_radius = max(visual_radius, 2) # Minimum size of 2 pixels

        # Draw the planet
        # Ensure center coordinates are integers and use the calculated visual_radius
        pygame.draw.circle(win, self.color, (x, y), visual_radius)


    def attraction(self, other):
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        # Avoid division by zero if planets are at the exact same position
        if distance == 0:
            return 0, 0

        if other.sun:
            self.distance_to_sun = distance

        # Access global constant G explicitly
        force = G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force

        return force_x, force_y

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        # Update velocity based on force and mass (F = ma => a = F/m)
        # v = v + a*dt
        # Access global constant TIMESTEP explicitly
        self.x_vel += total_fx / self.mass * TIMESTEP
        self.y_vel += total_fy / self.mass * TIMESTEP

        # Update position based on velocity
        # x = x + v*dt
        # Access global constant TIMESTEP explicitly
        self.x += self.x_vel * TIMESTEP
        self.y += self.y_vel * TIMESTEP

        # Store position for orbit drawing
        self.orbit.append((self.x, self.y))
        # Limit orbit path length to keep it manageable
        if len(self.orbit) > 750: # Increased orbit path length slightly
            self.orbit.pop(0)


# --- Main Simulation Loop ---
def main():
    run = True
    clock = pygame.time.Clock()

    sun = Planet(0, 0, 30, YELLOW, 1.989e31) # Mass of Sun
    sun.sun = True
    # The sun's initial distance_to_sun should be 0
    sun.distance_to_sun = 0

    # Initial velocities for planets to achieve roughly circular/elliptical orbits
    # These are approximate tangential velocities
    mercury_dist = 0.387 * AU
    mercury = Planet(mercury_dist, 0, 8, DARK_GREY, 3.301e23) # Mass of Mercury
    mercury.y_vel = math.sqrt(G * sun.mass / mercury_dist) # Approx orbital velocity

    venus_dist = 0.723 * AU
    venus = Planet(venus_dist, 0, 14, WHITE, 4.867e24) # Mass of Venus
    venus.y_vel = math.sqrt(G * sun.mass / venus_dist) # Approx orbital velocity

    earth_dist = 1 * AU # Start Earth on the left for visual variation
    earth = Planet(earth_dist, 0, 16, BLUE, 5.974e24) # Mass of Earth
    # For elliptical orbits, initial velocity needs to be adjusted.
    # For simplicity here, we'll use circular orbital velocity and place it at -1 AU
    earth.y_vel = math.sqrt(G * sun.mass / abs(earth_dist))


    mars_dist = 1.524 * AU # Start Mars on the left
    mars = Planet(mars_dist, 0, 12, RED, 6.417e23) # Mass of Mars
    mars.y_vel = math.sqrt(G * sun.mass / abs(mars_dist)) # Approx orbital velocity


    planets = [sun, mercury, venus, earth, mars]

    # Adjust initial velocities for a bit of eccentricity (more elliptical orbits)
    # This is a simplification; proper elliptical initial conditions are more complex
    mercury.y_vel *= 1.1 # Slightly faster for a more elliptical orbit
    venus.y_vel *= 0.95 # Slightly slower
    earth.y_vel *= 1.05 # Slightly faster
    mars.y_vel *= 0.9 # Slightly slower


    while run:
        clock.tick(60)  # Limit frame rate

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        WIN.fill((0, 0, 0))  # Black background

        # Sort planets by distance from the sun before drawing to handle overlapping
        # Draw further planets first. This is a basic z-ordering for the top-down view.
        planets_to_draw = sorted([p for p in planets if not p.sun], key=lambda p: p.distance_to_sun, reverse=True)

        # Draw sun first
        sun.draw(WIN)

        # Draw other planets based on distance
        for planet in planets_to_draw:
            planet.update_position(planets)
            planet.draw(WIN)


        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
