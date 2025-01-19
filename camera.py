import threading
from picamera2 import Picamera2
import cv2
import numpy as np
from scenes.joggen_scene import JoggenScene
from scenes.dachboden_scene import DachbodenScene

class ObjectDetector:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (640, 480)}))
        self.picam2.start()

        # Load YOLO model
        self.net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")
        with open("coco.names", "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        # State
        self.running = True
        self.current_scene = None

        # Object-to-scene mapping
        self.object_to_scene = {
            # Kitchen objects
            "banana": "KitchenScene",
            "apple": "KitchenScene",
            "sandwich": "KitchenScene",
            "orange": "KitchenScene",
            "broccoli": "KitchenScene",
            "carrot": "KitchenScene",
            "hot dog": "KitchenScene",
            "pizza": "KitchenScene",
            "donut": "KitchenScene",
            "cake": "KitchenScene",
            # Living room objects
            "chair": "LivingRoomScene",
            "sofa": "LivingRoomScene",
            "potted plant": "LivingRoomScene",
            "bed": "LivingRoomScene",
            # TikTok mode
            "cell phone": "TikTokMode",
            # Sport objects
            "frisbee": "SportMode",
            "skis": "SportMode",
            "snowboard": "SportMode",
            "sports ball": "SportMode",
            "kite": "SportMode",
            "baseball bat": "SportMode",
            "baseball glove": "SportMode",
            "skateboard": "SportMode",
            "surfboard": "SportMode",
            "tennis racket": "SportMode",
        }

    def detect_objects(self):
        """Continuously capture frames and detect objects."""
        while self.running:
            print("detect objects thread is running")
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Prepare frame for YOLO
            blob = cv2.dnn.blobFromImage(frame, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
            self.net.setInput(blob)
            detections = self.net.forward(self.output_layers)

            # Process detections
            for detection in detections:
                for object_detection in detection:
                    scores = object_detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]

                    if confidence > 0.5:  # Confidence threshold
                        detected_object = self.class_names[class_id]

                        # Check if object maps to a scene
                        if detected_object in self.object_to_scene:
                            print(f"Detected {detected_object} with confidence {confidence}")
                            new_scene = self.object_to_scene[detected_object]
                            if new_scene != self.current_scene:
                                self.current_scene = new_scene
                                print(f"Switching to {new_scene} due to detection of {detected_object}")
                                self.switch_scene(new_scene)

    def switch_scene(self, scene_name):
        """Switch to the appropriate scene."""
        if scene_name == "KitchenScene":
            self.scene_manager.set_scene(DachbodenScene(self.scene_manager))
        elif scene_name == "LivingRoomScene":
            self.scene_manager.set_scene(DachbodenScene(self.scene_manager))
        elif scene_name == "TikTokMode":
            self.scene_manager.set_scene(DachbodenScene(self.scene_manager))
        elif scene_name == "SportMode":
            self.scene_manager.set_scene(JoggenScene(self.scene_manager))

    def stop(self):
        """Stop the detection."""
        self.running = False
        self.picam2.stop()
