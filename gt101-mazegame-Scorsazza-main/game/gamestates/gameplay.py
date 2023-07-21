import numpy as np
import pyasge
from game.gamedata import GameData
from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID


class GamePlay(GameState):
    """ The game play state is the core of the game itself.

    The role of this class is to process the game logic, update
    the players positioning and render the resultant game-world.
    The logic for deciding on victory or loss should be handled by
    this class and its update function should return GAME_OVER or
    GAME_WON when the end game state is reached.
    """

    def bf_pathfinding(self, start_tile, target_tile):
        queue = [[start_tile]]
        visited = set()

        while queue:
            path = queue.pop(0)
            current_tile = path[-1]  # Corrected variable name to current_tile

            if current_tile == target_tile:
                return path

            if current_tile not in visited:
                visited.add(current_tile)

                # Get neighbors of the current tile and add them to the queue
                neighbours = self.data.game_map.get_neighbors(current_tile)
                for neighbour in neighbours:
                    queue.append(path + [neighbour])

        return None



    def __init__(self, data: GameData) -> None:
        """ Creates the game world

        Use the constructor to initialise the game world in a "clean"
        state ready for the player. This includes resetting of player's
        health and the enemy positions.

        Args:
            data (GameData): The game's shared data
        """
        super().__init__(data)
        self.player_position = pyasge.Point2D(0, 0)
        self.id = GameStateID.GAMEPLAY
        self.data.renderer.setClearColour(pyasge.COLOURS.CORAL)
        self.init_ui()

        # sets up the camera and points it at the player
        map_mid = [
            self.data.game_map.width * self.data.game_map.tile_size[0] * 0.5,
            self.data.game_map.height * self.data.game_map.tile_size[1] * 0.5
        ]

        self.camera = pyasge.Camera(map_mid, self.data.game_res[0], self.data.game_res[1])
        self.camera.zoom = 1
        self.ui_label = pyasge.Text(self.data.renderer.getDefaultFont(), "UI Label", 10, 50)
        self.ui_label.z_order = 120



    def init_ui(self):
        """Initialises the UI elements"""
        pass

    def click_handler(self, event: pyasge.ClickEvent) -> None:
        if event.button is pyasge.MOUSE.MOUSE_BTN1 and event.action is pyasge.MOUSE.BUTTON_PRESSED:
            target_pos = pyasge.Point2D(event.x, event.y)
            target_tile = self.data.game_map.tile(target_pos)
            print("Clicked Position:", target_pos)
            print("Target Tile:", target_tile)

            if not self.data.game_map.is_tile_passable(target_tile):
                return

            if not self.data.path:
                player_tile = self.data.game_map.tile(pyasge.Point2D(self.data.player.x, self.data.player.y))


                print("Calculating new path to target tile:", target_tile)
                print("Costs Map:")
                for row in self.data.game_map.costs:
                    print(row)

                self.data.path = self.bf_pathfinding(player_tile, target_tile)




        pass
    def move_handler(self, event: pyasge.MoveEvent) -> None:
        """ Listens for mouse movement events from the game engine """
        pass

    def key_handler(self, event: pyasge.KeyEvent) -> None:
        """ Listens for key events from the game engine """
        if event.action == pyasge.KEYS.KEY_PRESSED and event.key == pyasge.KEYS.KEY_D:
            pass

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        """ Simulates deterministic time steps for the game objects"""
        pass

    def update(self, game_time: pyasge.GameTime) -> None:


        if self.data.path:
            next_tile = self.data.path[0]

            if not self.data.game_map.is_tile_passable(next_tile):
                self.data.path = None
            else:

                new_pos = self.data.game_map.world(next_tile)
                self.data.player.x = new_pos.x
                self.data.player.y = new_pos.y
                print("New pos X:", new_pos.x)
                print("new_pos.y:", new_pos.y)
                self.data.path.pop(0)





    def update_camera(self):
        """ Updates the camera based on gamepad input"""
        if self.data.gamepad.connected:
            self.camera.translate(
                self.data.inputs.getGamePad().AXIS_LEFT_X * 10,
                self.data.inputs.getGamePad().AXIS_LEFT_Y * 10, 0.0)

    def update_inputs(self):
        """ This is purely example code to show how gamepad events
        can be tracked """
        if self.data.gamepad.connected:
            if self.data.gamepad.A and not self.data.prev_gamepad.A:
                # A button is pressed
                pass
            elif self.data.gamepad.A and self.data.prev_gamepad.A:
                # A button is being held
                pass
            elif not self.data.gamepad.A and self.data.prev_gamepad.A:
                # A button has been released
                pass

    def render(self, game_time: pyasge.GameTime) -> None:
        """ Renders the game world and the UI """
        self.data.renderer.setViewport(pyasge.Viewport(0, 0, self.data.game_res[0], self.data.game_res[1]))
        self.data.renderer.setProjectionMatrix(self.camera.view)
        self.data.shaders["example"].uniform("rgb").set([1.0, 1.0, 0])
        self.data.renderer.shader = self.data.shaders["example"]
        self.data.game_map.render(self.data.renderer, game_time)
        self.data.renderer.render(self.data.player)
        self.render_ui()


    def render_ui(self) -> None:
        """ Render the UI elements and map to the whole window """
        # set a new view that covers the width and height of game
        camera_view = pyasge.CameraView(self.data.renderer.resolution_info.view)
        vp = self.data.renderer.resolution_info.viewport
        self.data.renderer.setProjectionMatrix(0, 0, vp.w, vp.h)
        self.data.renderer.render(self.ui_label)

        # this restores the original camera view
        self.data.renderer.setProjectionMatrix(camera_view)

    def to_world(self, pos: pyasge.Point2D) -> pyasge.Point2D:
        """
        Converts from screen position to world position
        :param pos: The position on the current game window camera
        :return: Its actual/absolute position in the game world
        """
        view = self.camera.view
        x = (view.max_x - view.min_x) / self.data.game_res[0] * pos.x
        y = (view.max_y - view.min_y) / self.data.game_res[1] * pos.y
        x = view.min_x + x
        y = view.min_y + y

        return pyasge.Point2D(x, y)
