import threading
from picamera2 import Picamera2
import cv2
import numpy as np


class ObjectDetector:
    def __init__(self, scene_manager, pookie):
        self.scene_manager = scene_manager
        self.pookie = pookie
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (1920, 1080)}))
        self.picam2.start()

        # Load YOLO model
        self.net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")
        with open("coco.names", "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        # State
        self.running = True
        self.current_scene = self.scene_manager.current_scene

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
            # learn room
            "book": "LearnScene",
            "laptop": "LearnScene",
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

        # Track detection state
        self.cell_phone_detected = False
        self.tiktok_mode_active = False

    def detect_objects(self):
        """Continuously capture frames and detect objects."""
        while self.running:
            print("Detect objects thread is running")
            frame = self.picam2.capture_array()

            # Preprocess frame
            frame = self.preprocess_frame(frame)

            # Perform object detection
            detections = self.perform_detection(frame)

            # Process detections
            detected_objects = self.process_detections(detections)

            # Handle detected objects
            self.handle_detected_objects(detected_objects, frame)

    def preprocess_frame(self, frame):
        """Preprocess the frame for YOLO."""
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_equalized = cv2.equalizeHist(frame_gray)
        return cv2.cvtColor(frame_equalized, cv2.COLOR_GRAY2BGR)

    def perform_detection(self, frame):
        """Run the YOLO model and get detections."""
        blob = cv2.dnn.blobFromImage(frame, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        self.net.setInput(blob)
        return self.net.forward(self.output_layers)

    def process_detections(self, detections):
        """Process detections and apply Non-Max Suppression (NMS)."""
        boxes, confidences, class_ids = [], [], []

        for detection in detections:
            for object_detection in detection:
                scores = object_detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if class_id == 0:
                    continue

                if confidence > 0.3:  # Threshold for detection
                    center_x, center_y, width, height = (
                            object_detection[0:4] * np.array([640, 480, 640, 480])
                    ).astype(int)
                    x = int(center_x - width / 2)
                    y = int(center_y - height / 2)
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.4)
        detected_objects = [
            {"label": self.class_names[class_ids[i]], "confidence": confidences[i], "box": boxes[i]}
            for i in indexes
        ]

        return detected_objects

    def handle_detected_objects(self, detected_objects, frame):
        """Handle detected objects and trigger actions."""
        cell_phone_detected = False  # Track whether the cell phone is detected in this frame

        for obj in detected_objects:
            label = obj["label"]
            confidence = obj["confidence"]
            x, y, w, h = obj["box"]
            print(f"Detected {label} with confidence {confidence:.2f}")

            # Highlight detected objects
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Handle specific object detections
            if label == "cell phone" or label == "remote":
                cell_phone_detected = True
                if not self.tiktok_mode_active:
                    self.tiktok_mode_active = True  # Mark TikTok mode as active
                    print(f"Cell phone detected! Activating TikTok mode. +++ {self.tiktok_mode_active}")
                    self.pookie.handy += 1
                    self.activate_tiktok_mode()

            if label == "book" or label == "laptop":
                self.pookie.learn += 1
                self.handle_book_detection()

            #self.execute_object_action(label)

        # Reset if cell phone is no longer detected
        if not cell_phone_detected and self.tiktok_mode_active:
            self.tiktok_mode_active = False  # Reset TikTok mode flag
            print("Cell phone no longer detected. Resetting to normal mode.")
            self.reset_to_normal()

    def handle_book_detection(self):
        self.pookie.walk_to_learnroom = True
        self.pookie.handle_walk_to_learnroom()


    def activate_tiktok_mode(self):
        self.pookie.perform_animation("handy_modus", (448, 303), self.pookie.tikTokMessage())


    def reset_to_normal(self):
        """Reset to normal behavior."""
        try:
            from scenes.wohnzimmer_scene import Wohnzimmer
        except ImportError as e:
            print(f"ImportError occurred: {e}")
            return
        if isinstance(self.scene_manager.current_scene, Wohnzimmer):
            self.scene_manager.current_scene.initialize_state() #reset animation

    def stop(self):
        """Stop the detection."""
        self.running = False
        self.picam2.stop()