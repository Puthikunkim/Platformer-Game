# Accesses the script from another Python file/module.
import math
import os
import arcade
import arcade.gui

# Constants used to determine the screen size.
SCREEN_WIDTH = 1110
SCREEN_HEIGHT = 550
SCREEN_TITLE = "Andre's Realm"

# Constants used to scale assets including tiles, sprites and grids.
TILE_SCALING = 1
CHARACTER_SCALING = 0.5
SPRITE_PIXEL_SIZE = 64
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Constants used to scale bullets such as speed, size, and damage.
SPRITE_SCALING_LASER = 0.8
SHOOT_SPEED = 15
BULLET_SPEED = 30
BULLET_DAMAGE = 5

# Constants used to set the player movement speed, gravity and jump 
# speed in pixels per frame.
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1.2
PLAYER_JUMP_SPEED = 15

# Constants used to determine the minimum margin in pixels to keep 
# between the player character and the edge of the screen including the 
# top, bottom, left, and right before it needs scrolling.
LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

# Constants used to set the player starting position on the map 
# including the x and y coordinates.
PLAYER_START_X = 610
PLAYER_START_Y = 30

# Constants used to determine if the player is facing left or right.
RIGHT_FACING = 0
LEFT_FACING = 1

# Constants used to store the layers of the Tiled map.
LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND1 = "Background1"
LAYER_NAME_BACKGROUND2 = "Background2"
LAYER_NAME_BACKGROUND3 = "Background3"
LAYER_NAME_BACKGROUND4 = "Background4"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMIES = "Enemies"
LAYER_NAME_BULLETS = "Bullets"
LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_DONT_TOUCH = "Don't Touch"
LAYER_NAME_CHECKPOINTS = "Checkpoints"
LAYER_NAME_DOOR = "Door"

# Constant that stores the file directory to the assets used in the 
# game.
ASSET_PATH = "C:/Users/Tiger/Documents/game/DTP/assets/"



def load_texture_pair(filename):
    """
    Function used to load texture pairs for sprites to change textures 
    when the sprites faces left or right, essentially loading a mirror 
    image of the initial texture with the intial texture.
    """

    # Returns the initial texture facing direction for sprites and 
    # creates a mirror image which essentially makes it face left and 
    # right.
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class Entity(arcade.Sprite):
    """
    Class used to store methods that handles operations for the textures 
    of sprites essentially making it "animated" and this functionality 
    is made using the Arcade Python Module library for "arcade.Sprite".
    """

    # __init__() function to assign values to handle textures for 
    # sprites when created, including where the files to update 
    # animations for sprites will be.
    def __init__(self, name_folder, name_file):
        
        # super() function used to create a parent class to handle 
        # textures where the child classes for enemy and player sprites 
        # will inherit the functionality for changing textures.
        super().__init__()

        # Sets the direction that the sprite faces to the right as a 
        # default when the game begins.
        self.facing_direction = RIGHT_FACING

        # Variables used for sprite animations, "self.cur_texture" 
        # stores which "animation stage" or picture the sprite is on 
        # when they are moving and "self.scale" scales the sprite.
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Constant used to store the file directory for the sprite 
        # assets.
        main_path = f"{ASSET_PATH}/{name_folder}/{name_file}"

        # Constant used to store the file directory for different 
        # textures for the sprites including where the idle, jump, 
        # and fall textures will be.
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # List to store the different walking textures for the sprites 
        # ingame and for loop to cycle through the different walking 
        # textures and add them to the list.
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # List to store the different climbing textures for the sprites 
        # ingame and adds the different textures into the list, using 
        # Arcade Python Library it is loading in the textures.
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        # This sets the initial texture for the sprites when the game 
        # begins.
        self.texture = self.idle_texture_pair[0]

        # This sets the hit box for the sprites.
        self.set_hit_box(self.texture.hit_box_points)


class Enemy(Entity):
    """
    Child class used to store methods that will handle how the enemy 
    sprites will operate and inherit methods from the parent class 
    "Entity" handling how sprites should operate in general.
    """

    # __init__() function to assign values to handle how enemy sprites 
    # operate, and where the files to update animations for enemy 
    # sprites will be.
    def __init__(self, name_folder, name_file):

        # super() function used to create a parent class to handle how 
        # enemy sprites operate, where the child classes for different 
        # enemy sprites will inherit the functionality for enemy sprite 
        # operation, including file locations for updating animation.
        super().__init__(name_folder, name_file)

        # Variables used to determine the health of the enemies and 
        # whether walk textures should be updated. 
        self.should_update_walk = 0
        self.health = 0

    def update_animation(self, delta_time: float = 1 / 60):
        """
        Method to update the animation for enemy sprites, whether 
        they need to face left, right, be idle or walk.
        """

        # Determines whether the enemy sprite should face left or right 
        # based on how they are moving, if they are moving right they
        # will face right and vice versa.
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # Determines whether the enemy sprite should be idle based on if 
        # they are moving or not.
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Handles the execution for the walk animation if the enemy 
        # sprite is moving, "should_update_walk" detects and stores 
        # movement, if the enemy sprite has moved a certain amount of 
        # times which is 3 it will make the sprite walking texture the 
        # next picture in the sequence.
        if self.should_update_walk == 3:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = (
                self.walk_textures[self.cur_texture][self.facing_direction])
            self.should_update_walk = 0
            return
        self.should_update_walk += 1

class GuardianEnemy(Enemy):
    """
    Child class used to inherit from the enemy sprite parent class that 
    will handle how the enemy sprite will operate.
    """

    # __init__() function to assign values to handle how this 
    # particular enemy sprites operate, and where the files to update 
    # animations for this enemy sprite will be.
    def __init__(self):
        
        # super() function used to pass on the file location for this 
        # enemy sprite to update animations, handle how enemy sprites 
        # operate and inherit the functionality for enemy sprite 
        # operation.
        super().__init__("guardian", "guardian")

        # Variable to store the health for this particular sprite.
        self.health = 50


class PlayerCharacter(Entity):
    """
    Child class used to store methods that will handle how the player 
    sprite will operate such as textures for walking, jumping etc.
    and inherit methods from how sprites should operate in general from 
    the "Entity" parent class.
    """

    # __init__() function to assign values to handle how the player 
    # sprite will operate, and where the files to update animations 
    # for the player sprite will be.
    def __init__(self):
        
        # super() function used to pass on the file location for the 
        # player sprite to update animations, handle how the player 
        # sprite will operate and inherit the functionality for sprite 
        # operation.
        super().__init__("cloak", "hero")

        # Variables to track whether the player sprite is jumping, 
        # climbing or on a ladder.
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

    def update_animation(self, delta_time: float = 1 / 60):
        """
        Method to update the animation for the player sprite, whether 
        they need to face left, right, be idle, walk, jump or climb.
        """

        # Determines whether the player sprite should face left or right 
        # based on how they are moving, if they are moving right they
        # will face right and vice versa.
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # Determines whether the player sprite should have the climbing 
        # animation based on how they are moving, if the player is on 
        # a ladder it will set the variable tracking whether the player 
        # is on a ladder or not to True and vice versa. If the player
        # is already climbing it will update the texture by increasing
        # "cur_texture" which changes to the next image in the character
        # "animation sequence" and resets the "animation" when it 
        # reaches the last image in the sequence.
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # Determines whether the player sprite should have the jumping 
        # animation based on how they are moving, if the player is not
        # on any ladder and they have either a positive change in y
        # direction which is jumping it will update the player texture 
        # to the jumping image, if they have a negative change in y
        # direction which is falling it will update the plyaer texture 
        # to the falling image.
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.facing_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.facing_direction]
            return

        # Determines whether the player sprite should have the idle 
        # animation based on how they are moving, basically if they are
        # not moving at all which is no change in x.
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Handles the execution for the walk animation if the player 
        # sprite is moving and the direction to be facing, to make
        # the walking "animated" it will cycle to the next image in the
        # sequence and when it gets to the last image it will go back to
        # the first one.
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = (
            self.walk_textures[self.cur_texture][self.facing_direction])


class MainMenu(arcade.View):
    """
    Class used to store methods that manages the menu view/start screen.
    """

    # Used to initialize one variable for the UIManager for the view. 
    # The view class does not control the size of the window so there 
    # are no parameters needed in the super and only shows the view 
    # based on the window. 
    def __init__(self): 

        super().__init__() 

        # Setting the background image for the view. Basically loading
        # whatever image is in the that file directory using the Arcade
        # Python Library.
        self.texture = arcade.load_texture(f"{ASSET_PATH}/views/start.png") 

        # Creating a UI manager to handle the UI of the view using the 
        # Arcade Python Library and activating it.
        self.uimanager = arcade.gui.UIManager()
        self.uimanager.enable()

        # Creating the start game button using UIFlatButton from Arcade
        # Python Library, setting what text it should display and the
        # width.
        start_button = (
            arcade.gui.UIFlatButton(text = "Start Game", width = 200))

        # Assigns the on_buttonclick method when the user clicks on the 
        # start button which advances them to the instruction screen.
        start_button.on_click = self.on_buttonclick

        # Adding the start button into the uimanager to be displayed on 
        # screen using the Arcade Python Library.
        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x = "center_x", 
                anchor_y = "center_y", 
                child = start_button)
        ) 
    
    def on_buttonclick(self, event):
        """
        Method used to advance the user to the instruction view when 
        they click on the start button.
        """

        # Shows the InstructionView screen using the Arcade Python 
        # Library by creating a variable which stores the 
        # InstructionView class and displaying it.
        instruction_view = InstructionView()
        self.window.show_view(instruction_view)

    def on_draw(self): 
        """ 
        on_draw() method to draw the MainMenu view screen.
        """ 

        # Clears the window before displaying the screen using Arcade 
        # Python Library.
        arcade.start_render() 

        # Draws the background for the MainMenu view using Arcade 
        # Python Library.
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 
                                SCREEN_WIDTH, SCREEN_HEIGHT) 

        # Drawing the ui manager to display the MainMenu view including 
        # the start game button.                        
        self.uimanager.draw()


class InstructionView(arcade.View):
    """
    Class used to store methods that manages the instruction view 
    screen.
    """
    
    # Used to initialize one variable for the UIManager for this view, 
    # same as the main menu view. The view class does not control the 
    # size of the window so there are no parameters needed in the 
    # super and only shows the view based on the window. 
    def __init__(self): 

        super().__init__() 

        # Setting the background image for the view. Basically loading
        # whatever image is in the that file directory using the Arcade
        # Python Library.
        self.texture = (
            arcade.load_texture(f"{ASSET_PATH}/views/instruction.png")) 

        # Creating a UI manager to handle the UI of the view using the 
        # Arcade Python Library and activating it
        self.uimanager = arcade.gui.UIManager()
        self.uimanager.enable()

        # Creating the start game button using UIFlatButton from Arcade
        # Python Library, setting what text it should display and the
        # width.
        start_button = (
            arcade.gui.UIFlatButton(text = "Got It!", width = 200))

        # Assigns the on_buttonclick method when the user clicks on the 
        # start button which advances them to the game.
        start_button.on_click = self.on_buttonclick

        # Adding the start button into the uimanager to be displayed on 
        # screen using the Arcade Python Library.
        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x = "center_x", 
                anchor_y = "center_y", 
                child = start_button)
        )

    def on_buttonclick(self, event):
        """
        Method used to advance the user to the instruction view when 
        they click on the start button.
        """

        # Shows the InstructionView screen using the Arcade Python 
        # Library by creating a variable which stores the 
        # InstructionView class and displaying it.
        game_view = GameView()
        self.window.show_view(game_view)

    def on_draw(self): 
        """ 
        on_draw() method to draw the instruction view screen.
        """ 

        # Clears the window before displaying the screen using Arcade 
        # Python Library.
        arcade.start_render() 

        # Draws the background for the MainMenu view using Arcade 
        # Python Library.
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 
                                SCREEN_WIDTH, SCREEN_HEIGHT) 
        
        # Drawing the ui manager to display the instruction view 
        # including the start game button.
        self.uimanager.draw()

class EndGame(arcade.View):
    """
    Class used to store methods that manages the end of game view 
    screen.
    """

    # Used to initialize one variable for the UIManager for this view, 
    # same as the other view. The view class does not control the size 
    # of the window so there are no parameters needed in the super and 
    # only shows the view based on the window. 
    def __init__(self): 

        super().__init__() 

        # Setting the background image for the view. Basically loading
        # whatever image is in the that file directory using the Arcade
        # Python Library.
        self.texture = (
            arcade.load_texture(f"{ASSET_PATH}/views/endgame.png"))

        # Creating a UI manager to handle the UI of the view using the 
        # Arcade Python Library and activating it.
        self.uimanager = arcade.gui.UIManager()
        self.uimanager.enable()

        # Creating a vertical box for the buttons to align it using 
        # Arcade Python Library.
        self.v_box = arcade.gui.UIBoxLayout()

        # Creating the restart and quit game button using UIFlatButton 
        # from Arcade Python Library, setting what text it should
        # display and the width.
        start_button = arcade.gui.UIFlatButton(text = "Go again", width = 200)
        quit_button = arcade.gui.UIFlatButton(text = "Quit", width = 200)
        

        # Adding the restart game quit game button to the vertical box 
        # to be aligned with space below the restart game button so the 
        # quit button doesn't stick to it, using a child class to handle 
        # events using Arcade Python Library.
        self.v_box.add(start_button.with_space_around(bottom=20))
        self.v_box.add(quit_button)

        # Assigns the on_buttonclick method when the user clicks on the 
        # start button which advances them to the game.
        start_button.on_click = self.start_on_buttonclick
        quit_button.on_click = self.quit_on_buttonclick


        # Creating a widget to hold the vertical box alignment widget 
        # which will center the restart game and quit game buttons using
        # the Arcade Python Library.
        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def start_on_buttonclick(self, event):
        """
        Method used to restart the game when they click on the restart 
        button.
        """

        # Shows the game using the Arcade Python Library by creating a 
        # variable which stores the game class and displaying it.
        game_view = GameView()
        self.window.show_view(game_view)

    def quit_on_buttonclick(self, event):
        """
        Method used to quit the game when they click on the quit button.
        """

        # Exits the program using Arcade Python Library.
        arcade.exit()
        
    def on_draw(self): 
        """ 
        on_draw() method to draw the end of game view screen.
        """ 

        # Clears the window before displaying the screen using Arcade 
        # Python Library.
        arcade.start_render() 	

        # Draws the background for the MainMenu view using Arcade 
        # Python Library.
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 	
                                SCREEN_WIDTH, SCREEN_HEIGHT) 
        
        # Drawing the ui manager to display the end of game view 
        # including the vertically aligned restart game and quit game 
        # buttons.
        self.uimanager.draw()
    


class GameView(arcade.View):
    """
    Class used to store methods that manages the main game. Methods 
    include updating game state, processing user input, and drawing 
    items on the screen.
    """

    # Game initializer which handles actions that should only be taken 
    # when the game first starts.
    def __init__(self):

        super().__init__()

        # Method returns the pathname to the path of the program and 
        # sets it to start with the program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)


        # Used to track if a key is pressed and its current state.
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shoot_pressed = False
        self.jump_needs_reset = False

        # Stores our TileMap object.
        self.tile_map = None

        # Stores our Scene Object.
        self.scene = None

        # Stores our player sprite.
        self.player_sprite = None

        # Stores the physics engine, used to manage movement and 
        # collisions.
        self.physics_engine = None

        # Stores our camera which is used for scrolling the screen.
        self.camera = None

        # Stores our camera which is used to draw GUI elements.
        self.gui_camera = None

        # Stores our score and keeps track of it.
        self.score = 0

        # Stores our deaths and keeps track of it.
        self.death = 0

        # Stores our level and keeps track of it.
        self.level = 1

        # Stores our checkpoints and keeps track of it.
        self.checkpoint = None

        # Stores our shooting mechanics.
        self.can_shoot = False
        self.shoot_timer = 0

        # Stores the sound effects for the game.
        self.collect_coin_sound = arcade.load_sound(
            f"{ASSET_PATH}/sound/coin.wav")
        self.jump_sound = arcade.load_sound(f"{ASSET_PATH}/sound/jump.wav")
        self.game_over = arcade.load_sound(f"{ASSET_PATH}/sound/dead.wav")
        self.shoot_sound = arcade.load_sound(f"{ASSET_PATH}/sound/shoot.wav")
        self.hit_sound = arcade.load_sound(f"{ASSET_PATH}/sound/dead.wav")
        self.background_music = arcade.Sound(
            f"{ASSET_PATH}/sound/background.mp3", streaming = True)
    
    def setup(self):
        """
        Sets up the game to begin playing and stores things that may 
        need to be repeated throughout the game without restarting the 
        program.
        """

        # Set up the background music for the game, the volume and 
        # loops it.
        background_music_volume = 0.1
        self.current_player = self.background_music.play(
            background_music_volume, loop=True)

        # Set up the cameras for the game using Arcade Python Library
        # by passing in the desired width and heights for them.
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.gui_camera = arcade.Camera(self.window.width, self.window.height)

        # Set up the level for the game by providing the file directory.
        map_name = f"C:/Users/Tiger/Documents/game/DTP/level_{self.level}.tmx"

        # Stores the layer specific options for the Tilemap, whether it 
        # should detect collisions or not.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_PLATFORMS: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_LADDERS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DONT_TOUCH: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_CHECKPOINTS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DOOR: {
                "use_spatial_hash": True,
            },
        }
        
        # Set up and load in the TileMap for the game, using Arcade 
        # Python Library, by passing in our map, scaling and layer 
        # specific options.
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, 
                                            layer_options)

        # Initiates new scene using the TileMap, which will add all 
        # layers in the same order as in the TileMap using Arcade Python
        # Library.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Stores and keeps track of the score.
        self.score = 0

        # Draws the Foreground layer after the player, meaning it 
        # will appear in front of the Player. Setting this after will 
        # also mean it appears in front of the other layers in the 
        # TileMap, using Arcade Python Library using the player and
        # foreground layer as the argument.
        self.scene.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Tracks shooting mechanics.
        self.can_shoot = True
        self.shoot_timer = 0

        # Set up the player sprite placing it at the x and y coordinates 
        # and adding it to the player sprite list to be added to the 
        # game scene using Arcade Python Library.
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Stores the enemy layer from the TileMap.
        enemies_layer = self.tile_map.object_lists[LAYER_NAME_ENEMIES]

        # Set up the enemies in the game using a for loop.
        for my_object in enemies_layer:

            # Stores the cartesian coordinates for the enemy.
            cartesian = self.tile_map.get_cartesian(
                my_object.shape[0], my_object.shape[1]
            )

            # Stores the enemy type.
            enemy_type = my_object.properties["type"]

            # Checks the enemy type and assigns the appropriate enemy 
            # type class which determines its health.
            if enemy_type == "guardian":
                enemy = GuardianEnemy()
            
            # Calculates and stores the enemy center x and y 
            # coordinates.
            enemy.center_x = math.floor(
                cartesian[0] * TILE_SCALING * self.tile_map.tile_width
            )
            enemy.center_y = math.floor(
                (cartesian[1] + 1) * (self.tile_map.tile_height * TILE_SCALING)
            )

            # Stores the different properties and movement of the enemy 
            # including its boundary left, right, and change in x 
            # coordinates.
            if "boundary_left" in my_object.properties:
                enemy.boundary_left = my_object.properties["boundary_left"]
            if "boundary_right" in my_object.properties:
                enemy.boundary_right = my_object.properties["boundary_right"]
            if "change_x" in my_object.properties:
                enemy.change_x = my_object.properties["change_x"]
            
            # Adding the enemy to the game scene using Arcade Python
            # Library.
            self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)

        # Add bullet spritelist to game Scene using Arcade Python 
        # Library.
        self.scene.add_sprite_list(LAYER_NAME_BULLETS)

        # Creating the physics engine. It allows basic movement, 
        # provides a gravity force and also allows the player to jump 
        # and climb ladders. Using the Arcade Python Library we pass
        # in the player sprite and the layers it will be interacting 
        # with such as moving platforms, platforms where the player
        # can't move through and ladder which the player is able to 
        # climb.
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=GRAVITY,
            ladders=self.scene[LAYER_NAME_LADDERS],
            walls=self.scene[LAYER_NAME_PLATFORMS]
        )


    def on_show(self):
        """
        Shows and calls on the setup for the game. 
        """

        self.setup()

    def on_draw(self):
        """
        Renders and draws the screen, used to draw everything displayed 
        in the game.
        """

        # Activates the camera for the game.
        self.camera.use()

        # Draws the game scene.
        self.scene.draw()

        # Activates the GUI camera for the game.
        self.gui_camera.use()

        # Draws the score text on the screen, and keeps it stationary 
        # on the screen, scrolling with the viewport, also with a shadow
        # effect and custom font Arcade Python Library.
        score_text = f"Skulls: {self.score}/3"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.BLACK,
            20,
            font_name = "Kenney Future"
        )
        arcade.draw_text(
            score_text,
            13,
            13,
            arcade.csscolor.WHITE,
            20,
            font_name = "Kenney Future"
        )

        # Draws the death text on the screen, and keeps it stationary 
        # on the screen, scrolling with the viewport, also with a shadow
        # effect and custom font using Arcade Python Library.
        death_text = f"Deaths: {self.death}"
        arcade.draw_text(
            death_text,
            10,
            50,
            arcade.csscolor.BLACK,
            20,
            font_name = "Kenney Future"
        )
        arcade.draw_text(
            death_text,
            13,
            53,
            arcade.csscolor.WHITE,
            20,
            font_name = "Kenney Future"
        )

    def process_keychange(self):
        """
        Processes the key changes when the user presses different keys.
        """

        # Processes when the user presses the up key.
        if self.up_pressed and not self.down_pressed:

            # If the player is on a ladder while pressing up it changes 
            # the y coordinate of the player making them move up the 
            # ladder according to the movement speed using Arcade Python 
            # Library.
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED

            # If the player is not on a ladder and there is a platform 
            # beneath the player, if they press up it changes the y 
            # coordinate of the player making them jump, according to 
            # the jump speed and resets the jump while also playing the 
            # jump sound effect using Arcade Python Library.
            elif (
                self.physics_engine.can_jump(y_distance=10)
                and not self.jump_needs_reset
            ):
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)

        # Processes when the user presses the down key.
        elif self.down_pressed and not self.up_pressed:

            # If the player is on a ladder while pressing down it 
            # changes the y coordinate of the player making them move 
            # down the ladder according to the movement speed using 
            # Arcade Python Library.
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process when the user does not press the up or down keys when 
        # on a ladder there will be no movement using Arcade Python 
        # Library.
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process when the user presses right key.
        if self.right_pressed and not self.left_pressed:
            # If they press right it changes the player x coordinate to 
            # the right according to the player movement speed.
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

        # Process when the user presses left key.
        elif self.left_pressed and not self.right_pressed:
            # If they press left it changes the player x coordinate to 
            # the left according to the player movement speed.
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED

        else:
            # If the player doesn't press right or left the player 
            # remains stationary along the x axis.
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """
        Processes key presses.
        """
        
        # If the user presses any of the keys it sets the variable that 
        # tracks if the key is pressed to True.
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        
        if key == arcade.key.Q:
            self.shoot_pressed = True

        # Processes the key changes when the user presses the keys.
        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """
        Processes key releases.
        """

        # If the user releases any of the keys after being pressed, it 
        # sets the variable that tracks if the key is pressed to False.
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        if key == arcade.key.Q:
            self.shoot_pressed = False

        # Processes the key changes when the user presses and releases 
        # the keys.
        self.process_keychange()

    def center_camera_to_player(self, speed = 0.2):
        """
        Method to keep viewport camera centered on the player.
        """

        # Calculates the screen center x and y coordinates in relation 
        # to the player. 
        screen_center_x = (self.camera.scale * 
        (self.player_sprite.center_x - (self.camera.viewport_width / 2)))
        screen_center_y = (self.camera.scale * 
        (self.player_sprite.center_y - (self.camera.viewport_height / 2)))
        
        # If the player moves up, down, left, right past the margin for 
        # where the camera is centered it sets it on the player.
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        
        # Stores the center of the camera coordinates.
        player_centered = (screen_center_x, screen_center_y)    

        # Sets the goal position of the camera of where it should move 
        # to based on the position provided, which is the 
        # player_centered variable, and moves to that position based on 
        # the speed using Arcade Python Library.
        self.camera.move_to(player_centered, speed)

    def on_update(self, delta_time):
        """
        Updates the position and state of game objects, such as 
        movement, game logic, movement, collisions, and animations.
        """

        # Updates player movement based on the physics engine and 
        # detects collision using Arcade Python Library.
        self.physics_engine.update()

        # Updates the player animation, if there is a platform under the 
        # player the player should jump or not so the player would not 
        # be able to jump infinitely using Arcade Python Library. 
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        # Updates the player animation, if the player is on a ladder and
        # there is no platform on the player the variable tracking 
        # whether the player is on the ladder or not to True and 
        # processes the key change and vice versa using Arcade Python 
        # Library. 
        if (self.physics_engine.is_on_ladder() 
        and not self.physics_engine.can_jump()):
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        # Updates shooting animation and mechanics.
        if self.can_shoot:

            # If the shoot key is pressed, play the shooting sound and 
            # create a bullet based on image provided and scale it 
            # according to bullet scaling constant using Arcade Python
            # Library.
            if self.shoot_pressed:
                shoot_volume = 0.1
                arcade.play_sound(self.shoot_sound, shoot_volume)
                bullet = arcade.Sprite(
                    f"{ASSET_PATH}/bullet/bullet.png",
                    SPRITE_SCALING_LASER,
                )

                # If the player is facing right, the bullet will travel 
                # to the right based on bullet speed.
                if self.player_sprite.facing_direction == RIGHT_FACING:
                    bullet.change_x = BULLET_SPEED

                # If the player is facing left, the bullet will travel 
                # to the left based on bullet speed.
                else:
                    bullet.change_x = -BULLET_SPEED

                # Calculates the bullet x and y coordinate, where it 
                # should spawn and travel from.
                bullet.center_x = self.player_sprite.center_x 
                bullet.center_y = self.player_sprite.center_y 

                # Adding the bullets to the bullet list to be added to 
                # the game scene using Arcade Python Library.
                self.scene.add_sprite(LAYER_NAME_BULLETS, bullet)

                # Resets the shot after shooting a bullet.
                self.can_shoot = False

        # If the player has shot create a timer based on how fast the 
        # player can shoot constant before they are able to shoot again, 
        # after the timer is done allow the player to shoot and reset 
        # the timer.
        else:
            self.shoot_timer += 1
            if self.shoot_timer == SHOOT_SPEED:
                self.can_shoot = True
                self.shoot_timer = 0

        # Update the different object layer list animations such as the 
        # player and enemy sprites.
        self.scene.update_animation(
            delta_time,
            [
                LAYER_NAME_PLAYER,
                LAYER_NAME_ENEMIES,
            ],
        )

        # Update the different object layer list movements, such as 
        # moving platforms, enemies, and bullets.
        self.scene.update(
            [
                LAYER_NAME_MOVING_PLATFORMS, 
                LAYER_NAME_ENEMIES, 
                LAYER_NAME_BULLETS
            ]
        )

        # Checks if the enemy sprite hits the set boundaryfor movement 
        # and reverses the direction of travel.
        for enemy in self.scene[LAYER_NAME_ENEMIES]:
            if (
                enemy.boundary_right
                and enemy.right > enemy.boundary_right
                and enemy.change_x > 0
            ):
                enemy.change_x *= -1

            if (
                enemy.boundary_left
                and enemy.left < enemy.boundary_left
                and enemy.change_x < 0
            ):
                enemy.change_x *= -1
        
        # Checks if the bullets hits any objects, including enemy 
        # sprites, platforms or moving platforms and stores it in a 
        # list using Arcade Python Library.
        for bullet in self.scene[LAYER_NAME_BULLETS]:
            hit_list = arcade.check_for_collision_with_lists(
                bullet,
                [
                    self.scene[LAYER_NAME_ENEMIES],
                    self.scene[LAYER_NAME_PLATFORMS],
                    self.scene[LAYER_NAME_MOVING_PLATFORMS],
                ],
            )

            # If the bullets hit those object layer lists, remove the 
            # bullets from the scene
            if hit_list:
                bullet.remove_from_sprite_lists()

                # Checks if any of the bullet collisions hits enemy 
                # sprites, if it does reduce the health points of the 
                # enemy sprites based on bullet damage.
                for collision in hit_list:
                    if (
                        self.scene[LAYER_NAME_ENEMIES]
                        in collision.sprite_lists
                    ):
                        collision.health -= BULLET_DAMAGE

                        # If the enemy sprites have no more health 
                        # points remove them from the enemy list layer 
                        # and the scene of the game.
                        if collision.health <= 0:
                            collision.remove_from_sprite_lists()

                        # Plays the enemy sprite taking damage sound 
                        # effect using Arcade Python Library.
                        arcade.play_sound(self.hit_sound)

                return

        # Checks if the player hits an enemy sprite, door or a don't 
        # touch object and stores it in a list using Arcade Python
        # Library.
        player_collision_list = arcade.check_for_collision_with_lists(
            self.player_sprite,
            [
                self.scene[LAYER_NAME_ENEMIES],
                self.scene[LAYER_NAME_DOOR],
                self.scene[LAYER_NAME_DONT_TOUCH],
            ],
        )

        # Checks through the collisions.
        for collision in player_collision_list:
            
            # If the player hits an enemy they are reset to the last 
            # checkpoint, playing the game over sound effect and 
            # increasing their death counter by 1 using Arcade Python
            # Library.
            if self.scene[LAYER_NAME_ENEMIES] in collision.sprite_lists:
                self.player_sprite.change_x = 0	
                self.player_sprite.change_y = 0	
                self.player_sprite.center_x = self.checkpoint.center_x		
                self.player_sprite.center_y = self.checkpoint.center_y	
                arcade.play_sound(self.game_over)
                self.death += 1

            # If the player hits a don't touch object they are reset to 
            # the last checkpoint, playing the game over sound effect 
            # and increasing their death counter by 1 using Arcade 
            # Python Library.
            elif self.scene[LAYER_NAME_DONT_TOUCH] in collision.sprite_lists:	
                self.player_sprite.change_x = 0	
                self.player_sprite.change_y = 0	
                self.player_sprite.center_x = self.checkpoint.center_x		
                self.player_sprite.center_y = self.checkpoint.center_y
                self.death += 1	
                arcade.play_sound(self.game_over)

            # If the player hits the door to the next level and has the 
            # correct amount of coins, it takes them to the next level 
            # by increasing the level counter and setting up the next 
            # level. 
            elif ((self.scene[LAYER_NAME_DOOR] in collision.sprite_lists) 
            and self.score >= 3 and self.level < 3):
                self.level += 1
                self.setup()

            # If the player hits the door to the next level and has the 
            # correct amount of coins, but is on level 3, it shows the 
            # end of game view screen using Arcade Python Library.
            elif ((self.scene[LAYER_NAME_DOOR] in collision.sprite_lists) 
                   and self.score >= 3 and self.level == 3):
                end_game = EndGame()
                self.window.show_view(end_game)

        # List to check if the player hits any coins, and loops through 
        # the list, if they do, remove the coins from the scene while 
        # increasing player score by 1 and playing the coin collection 
        # sound effect using Arcade Python Library.
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_COINS])
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            coin_volume = 1.2
            arcade.play_sound(self.collect_coin_sound, coin_volume)
            self.score += 1

        # List to check if the player hits any checkpoints using Arcade
        # Python Library.
        checkpoint_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_CHECKPOINTS]
        )

        # Loops through the checkpoint hit list, and stores the 
        # checkpoint coordinates.
        for i in checkpoint_hit_list:
            self.checkpoint = i
            self.check_level = self.level

        # Removes the checkpoint after going past it.
        for checkpoint in checkpoint_hit_list:
            checkpoint.remove_from_sprite_lists()

        # Keep viewport camera centered on player.
        self.center_camera_to_player()

def main():
    """
    Function to run the game.
    """

    # Creates an arcade.Window in which to display the views and game.
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    # Creates the MaineMenu object, and calls the .setup().
    menu_view = MainMenu()

    # This displays the view. 
    window.show_view(menu_view)

    # Runs the game and views.
    arcade.run()

# Checks if the pythom module file is the main program, preventing parts 
# of the code from being run when modules are imported.
if __name__ == "__main__":
    main()