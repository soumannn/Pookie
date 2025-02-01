from scenes.wohnzimmer_scene import Wohnzimmer
from scenes.lernzimmer_scene import Lernzimmer
from scenes.joggen_scene import JoggenScene
from scenes.gym_scene import Gym


class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.scenes = [Wohnzimmer, Lernzimmer, JoggenScene, Gym]

    def set_scene(self, scene):
        self.current_scene = scene
        print(f"Scene switched to: {type(scene).__name__}")
        print(f"current scene: {self.current_scene}")

    def handle_event(self, event):
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)

    def render(self, screen, debug_mode=False):
        if self.current_scene:
            self.current_scene.render(screen, debug_mode)

