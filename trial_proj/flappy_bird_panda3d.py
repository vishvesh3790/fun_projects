from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import Sequence, Parallel, LerpFunc
from panda3d.core import Point3, Vec3, TextNode, NodePath, CardMaker
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import CollisionTraverser, CollisionNode, CollisionBox
from panda3d.core import CollisionHandlerQueue
import random
import sys

class FlappyBird3D(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Basic scene setup
        base.setBackgroundColor(0.4, 0.6, 1.0)  # Sky blue
        base.disableMouse()  # Disable default mouse camera control
        
        # Game settings
        self.game_running = True
        self.score = 0
        
        # Initialize game state
        self.initialize_game()
        
        # Set up key controls
        self.accept("space", self.flap)
        self.accept("escape", sys.exit)
        self.accept("r", self.restart_game)

    def initialize_game(self):
        # Set up the camera
        self.camera.setPos(0, -15, 0)  # Moved camera closer
        self.camera.lookAt(Point3(0, 0, 0))
        
        # Set up lighting
        self.setup_lights()
        
        # Create the bird
        self.setup_bird()
        
        # Set up collision detection
        self.setup_collisions()
        
        # Create score display
        self.score_text = OnscreenText(
            text="Score: 0",
            pos=(-1.3, 0.9),
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            scale=0.07
        )
        
        # Game control variables
        self.bird_velocity = 0
        self.gravity = -9.8
        self.jump_strength = 5
        self.pipes = []
        self.pipe_creation_task = taskMgr.doMethodLater(2.0, self.create_pipe, 'CreatePipe')
        
        # Add game loop task
        self.gameTask = taskMgr.add(self.game_loop, "GameLoop")
    
    def setup_lights(self):
        # Ambient light
        alight = AmbientLight('ambient')
        alight.setColor((0.7, 0.7, 0.7, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Directional light
        dlight = DirectionalLight('directional')
        dlight.setColor((1, 1, 1, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)
    
    def setup_bird(self):
        # Create a simple bird using a sphere
        cm = CardMaker('bird')
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        self.bird = NodePath(cm.generate())
        self.bird.setColor(1, 1, 0)  # Yellow
        self.bird.reparentTo(self.render)
        self.bird.setPos(0, 0, 0)
        self.bird.setBillboardPointEye()
        
        # Create collision solid for bird
        collision_sphere = CollisionBox(Point3(0, 0, 0), 0.3, 0.3, 0.3)
        cnodePath = self.bird.attachNewNode(CollisionNode('bird'))
        cnodePath.node().addSolid(collision_sphere)
    
    def create_pipe(self, task):
        if not self.game_running:
            return task.done
        
        # Create pipe using CardMaker
        cm = CardMaker('pipe')
        height = random.uniform(2, 4)
        cm.setFrame(-0.5, 0.5, -height, height)
        pipe = NodePath(cm.generate())
        pipe.setColor(0, 0.8, 0)  # Green
        pipe.reparentTo(self.render)
        pipe.setPos(5, 0, random.uniform(-2, 2))
        pipe.setBillboardPointEye()
        
        # Create collision solid for pipe
        collision_box = CollisionBox(Point3(0, 0, 0), 0.5, 0.1, height)
        cnodePath = pipe.attachNewNode(CollisionNode('pipe'))
        cnodePath.node().addSolid(collision_box)
        
        # Move pipe
        pipe_movement = pipe.posInterval(
            3,
            Point3(-5, 0, pipe.getZ()),
            startPos=Point3(5, 0, pipe.getZ())
        )
        
        # Remove pipe when movement is done
        def remove_pipe():
            pipe.removeNode()
            self.pipes.remove(pipe)
            self.score += 1
            self.score_text.setText(f"Score: {self.score}")
        
        movement_sequence = Sequence(
            pipe_movement,
            Parallel(
                LerpFunc(lambda x: remove_pipe())
            )
        )
        movement_sequence.start()
        
        self.pipes.append(pipe)
        return task.again
    
    def setup_collisions(self):
        self.cTrav = CollisionTraverser()
        self.collisionHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.bird.find("**/bird"), self.collisionHandler)
    
    def flap(self):
        if self.game_running:
            self.bird_velocity = self.jump_strength
    
    def game_loop(self, task):
        dt = globalClock.getDt()
        
        if self.game_running:
            # Update bird physics
            self.bird_velocity += self.gravity * dt
            self.bird.setZ(self.bird.getZ() + self.bird_velocity * dt)
            
            # Rotate bird based on velocity
            self.bird.setP(max(-30, min(self.bird_velocity * 3, 30)))
            
            # Check collisions
            self.cTrav.traverse(self.render)
            
            if self.collisionHandler.getNumEntries() > 0 or \
               self.bird.getZ() > 10 or self.bird.getZ() < -10:
                self.game_over()
        
        return task.cont
    
    def game_over(self):
        self.game_running = False
        
        # Show game over text with restart instruction
        self.game_over_text = OnscreenText(
            text="Game Over!\nPress R to restart\nPress ESC to quit",
            pos=(0, 0),
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            scale=0.1
        )
    
    def restart_game(self):
        if not self.game_running:
            # Remove game over text
            self.game_over_text.destroy()
            
            # Remove all existing pipes
            for pipe in self.pipes:
                pipe.removeNode()
            self.pipes = []
            
            # Reset bird position and velocity
            self.bird.setPos(0, 0, 0)
            self.bird.setP(0)
            self.bird_velocity = 0
            
            # Reset score
            self.score = 0
            self.score_text.setText("Score: 0")
            
            # Reset game state
            self.game_running = True
            
            # Restart pipe creation
            self.pipe_creation_task = taskMgr.doMethodLater(2.0, self.create_pipe, 'CreatePipe')

game = FlappyBird3D()
game.run()
