from panda3d.core import DirectionalLight, AmbientLight, Vec3, CardMaker, TransparencyAttrib, GraphicsPipe
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import DirectFrame
import numpy as np
import heapq
from random import randint


GRID_WIDTH = 50
GRID_HEIGHT = 50
CELL_SIZE = 2


class DroneSim3D(ShowBase):
    def __init__(self):
        super().__init__()

        self.disable_mouse()
        self.set_background_color(0.1, 0.1, 0.1)

        # Generate terrain grid
        self.terrain = self.generate_terrain(GRID_WIDTH, GRID_HEIGHT)

        # Place drone and SOS grid positions on cleared terrain
        self.place_drone_grid_pos()
        self.place_sos_grid_pos()

        # Clear area around SOS so search area is open
        self.clear_area_around(self.terrain, self.sos_grid_pos, radius=2)

        # Draw terrain ground
        self.draw_terrain()

        # Place 3D trees and rocks instead of billboard trees
        self.place_3d_scenery()

        # Place drone and SOS models after terrain and scenery drawn
        self.place_drone()
        self.place_sos_cube()

        self.setup_lighting()

        # Find path from drone to SOS
        self.path = self.find_path()
        print(f"Drone start: {self.drone_grid_pos}, SOS goal: {self.sos_grid_pos}")
        print(f"Path length: {len(self.path)}")
        if len(self.path) == 0:
            print("Warning: No path found from drone to SOS!")

        self.path_index = 0
        self.move_delay = 0.4
        self.last_move_time = 0

        self.drone_heading = 0

        # Setup minimap overlay
        self.setup_minimap()

        # Add tasks
        self.task_mgr.add(self.update_camera, "CameraFollowTask")
        self.task_mgr.add(self.move_drone_task, "MoveDroneTask")
        self.task_mgr.add(self.flash_sos_task, "FlashSOSTask")

    def generate_terrain(self, width, height):
        grid = np.zeros((height, width), dtype=int)
        num_obstacles = int(0.2 * width * height)
        for _ in range(num_obstacles):
            x = randint(0, width - 1)
            y = randint(0, height - 1)
            grid[y][x] = 1
        return grid

    def place_drone_grid_pos(self):
        while True:
            x = randint(0, GRID_WIDTH - 1)
            y = randint(0, GRID_HEIGHT - 1)
            if self.terrain[y][x] == 0:
                self.drone_grid_pos = (x, y)
                break

    def place_sos_grid_pos(self):
        while True:
            x = randint(0, GRID_WIDTH - 1)
            y = randint(0, GRID_HEIGHT - 1)
            if self.terrain[y][x] == 0 and (x, y) != self.drone_grid_pos:
                self.sos_grid_pos = (x, y)
                break

    def clear_area_around(self, grid, center, radius=2):
        cx, cy = center
        for y in range(max(0, cy - radius), min(GRID_HEIGHT, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(GRID_WIDTH, cx + radius + 1)):
                grid[y][x] = 0  # Clear obstacles

    def draw_terrain(self):
        dirt_tex = self.loader.load_texture("models/envir-ground.jpg")
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cm = CardMaker('ground_cell')
                cm.set_frame(-CELL_SIZE / 2, CELL_SIZE / 2, -CELL_SIZE / 2, CELL_SIZE / 2)
                card = self.render.attach_new_node(cm.generate())
                card.set_pos(x * CELL_SIZE, y * CELL_SIZE, 0)
                card.set_hpr(0, -90, 0)
                card.set_texture(dirt_tex)

    def place_3d_scenery(self):
        # Load the simple custom models you saved as tree.egg and rock.egg
        self.tree_model = self.loader.load_model("models/tree.egg")
        self.rock_model = self.loader.load_model("models/rock.egg")

        if not self.tree_model or not self.rock_model:
            print("Error loading 3D scenery models.")
            return

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.terrain[y][x] == 1:
                    # 70% chance tree, 30% rock
                    if randint(0, 100) < 70:
                        model = self.tree_model.copy_to(self.render)
                        # Scale tree taller, vary size slightly
                        model.set_scale(1.0 + 0.5 * np.random.rand())
                    else:
                        model = self.rock_model.copy_to(self.render)
                        # Smaller scale for rocks
                        model.set_scale(0.5 + 0.3 * np.random.rand())

                    model.set_pos(x * CELL_SIZE, y * CELL_SIZE, 0)
                    model.set_h(randint(0, 360))



    def place_drone(self):
        self.drone = self.loader.load_model("models/quadplane")
        if self.drone is None:
            print("Error: Could not load drone model.")
            return
        self.drone.reparent_to(self.render)
        self.drone.set_scale(2.0)
        self.drone.set_color(0.2, 0.2, 1, 1)
        self.prev_grid_pos = self.drone_grid_pos
        self.drone.set_pos(self.grid_to_world(*self.drone_grid_pos, z=0.8))  # low altitude

    def place_sos_cube(self):
        self.sos_cube = self.loader.load_model("models/rgbCube")
        if self.sos_cube is None:
            print("Error: Could not load SOS cube model.")
            return
        self.sos_cube.set_color(1, 1, 1, 1)
        self.sos_cube.set_scale(0.7, 0.7, 0.5)
        self.sos_cube.reparent_to(self.render)
        self.sos_cube.set_pos(self.grid_to_world(*self.sos_grid_pos, z=0.8))

    def grid_to_world(self, x, y, z=0):
        return Vec3(x * CELL_SIZE, y * CELL_SIZE, z)

    def update_camera(self, task):
        drone_pos = self.drone.get_pos()

        import math
        heading_rad = math.radians(self.drone_heading)
        forward = Vec3(math.sin(heading_rad), math.cos(heading_rad), 0)

        # Camera offset: behind drone by 4 units, 2 units above
        cam_offset = -forward * 4 + Vec3(0, 0, 2)
        cam_pos = drone_pos + cam_offset
        self.camera.set_pos(cam_pos)

        # Look at a point 10 units ahead, at drone altitude
        look_at_pos = drone_pos + forward * 10 + Vec3(0, 0, 0.8)
        self.camera.look_at(look_at_pos)

        # Pitch camera down about 15 degrees
        self.camera.set_p(-15)

        return Task.cont

    def move_drone_task(self, task):
        if not self.path or self.path_index >= len(self.path):
            return Task.cont

        current_time = task.time
        if current_time - self.last_move_time >= self.move_delay:
            next_pos = self.path[self.path_index]
            self.prev_grid_pos = self.drone_grid_pos

            dx = next_pos[0] - self.drone_grid_pos[0]
            dy = next_pos[1] - self.drone_grid_pos[1]

            import math
            if dx != 0 or dy != 0:
                self.drone_heading = (math.degrees(math.atan2(dx, dy))) % 360
                self.drone.set_h(self.drone_heading)

            self.drone_grid_pos = next_pos
            self.drone.set_pos(self.grid_to_world(*next_pos, z=0.8))
            self.path_index += 1
            self.last_move_time = current_time
            print(f"Drone moved to: {self.drone_grid_pos} Heading: {self.drone_heading}")

        return Task.cont

    def find_path(self):
        start = self.drone_grid_pos
        goal = self.sos_grid_pos
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if self.terrain[ny][nx] == 0:
                    neighbors.append((nx, ny))
        return neighbors

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def flash_sos_task(self, task):
        import math
        period = 1.0
        phase = task.time % period
        intensity = (math.sin(phase * 2 * math.pi) + 1) / 2

        self.sos_cube.set_color(1, 1, 1, intensity)
        if intensity < 0.1:
            self.sos_cube.hide()
        else:
            self.sos_cube.show()

        return Task.cont

    def setup_lighting(self):
        dlight = DirectionalLight("dlight")
        dlight.set_color((0.9, 0.9, 0.8, 1))
        dlnp = self.render.attach_new_node(dlight)
        dlnp.set_hpr(0, -60, 0)
        self.render.set_light(dlnp)

        alight = AmbientLight("alight")
        alight.set_color((0.3, 0.3, 0.3, 1))
        alnp = self.render.attach_new_node(alight)
        self.render.set_light(alnp)

    def setup_minimap(self):
        # Create a frame on the right side of the screen for the minimap
        self.minimap_frame = DirectFrame(frameColor=(0, 0, 0, 0.5),
                                        frameSize=(-0.2, 0.2, -0.2, 0.2),
                                        pos=(1 - 0.22, 0, 0.8))

        # Create an offscreen buffer for the minimap render
        win_props = self.win.get_properties()
        buffer_props = self.win.get_fb_properties()

        self.minimap_buffer = self.graphicsEngine.make_output(
            self.pipe, "minimap buffer", -2,
            buffer_props, win_props,
            GraphicsPipe.BF_refuse_window,
            self.win.get_gsg(), self.win)

        # Create a new camera for the minimap
        self.minimap_cam = self.make_camera(self.minimap_buffer)
        self.minimap_cam.reparent_to(self.render)

        # Position the camera high above, looking straight down
        self.minimap_cam.set_pos(self.drone.get_x(), self.drone.get_y(), 50)
        self.minimap_cam.set_hpr(0, -90, 0)

        # Attach the buffer texture to the frame
        tex = self.minimap_buffer.get_texture()
        self.minimap_frame.set_texture(tex)

        # Update minimap camera each frame
        self.task_mgr.add(self.update_minimap_camera, "UpdateMinimapCam")

    def update_minimap_camera(self, task):
        # Follow drone position on X,Y, keep altitude fixed
        drone_pos = self.drone.get_pos()
        self.minimap_cam.set_pos(drone_pos.x, drone_pos.y, 50)
        self.minimap_cam.set_hpr(0, -90, 0)
        return Task.cont


if __name__ == "__main__":
    app = DroneSim3D()
    app.run()
