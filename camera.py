import threading
from picamera2 import Picamera2
import cv2
import numpy as np
import time

class ObjectDetector:
    def __init__(self, scene_manager, pookie):
        self.stop_event = threading.Event()
        self.detection_thread = threading.Thread(target=self.detect_objects, daemon=True)

        self.scene_manager = scene_manager
        self.pookie = pookie
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (640, 480)}))
        self.picam2.start()  # Start streaming video

        # Load YOLO model
        self.net = cv2.dnn.readNet("neural/yolov7-tiny.weights", "neural/yolov7-tiny.cfg")
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        with open("coco.names", "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        # Track detection state
        self.tiktok_mode_active = False
        self.book_mode_active = False

    def start_detection(self):
        """Start the object detection in a separate thread."""
        if not self.detection_thread.is_alive():
            self.detection_thread = threading.Thread(target=self.detect_objects, daemon=True)
            self.detection_thread.start()

    def stop_detection(self):
        """Stop object detection."""
        self.stop_event.set()
        self.detection_thread.join()
        print("Detection stopped.")

    def detect_objects(self):
        """Continuously process frames from the video stream."""
        print("Starting video stream processing...")
        for frame in self.picam2.capture_video_frames():  # Capture video stream
            if self.stop_event.is_set():
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # Ensure correct color format
            detections = self.perform_detection(frame)
            detected_objects = self.process_detections(detections)
            self.handle_detected_objects(detected_objects)

    def perform_detection(self, frame):
        """Run the YOLO model on a frame."""
        blob = cv2.dnn.blobFromImage(frame, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        self.net.setInput(blob)
        return self.net.forward(self.output_layers)

    def process_detections(self, detections):
        """Extract detected objects with confidence scores."""
        boxes, confidences, class_ids = [], [], []

        for detection in detections:
            for object_detection in detection:
                scores = object_detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.3:  # Detection threshold
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

    def handle_detected_objects(self, detected_objects):
        """Handle detected objects without displaying video."""
        cell_phone_detected = False
        book_detected = False

        for obj in detected_objects:
            label = obj["label"]
            confidence = obj["confidence"]

            print(f"Detected {label} with confidence {confidence:.2f}")

            # Handle specific detections
            if label == "cell phone" or label == "remote":
                cell_phone_detected = True
                if not self.tiktok_mode_active:
                    self.tiktok_mode_active = True
                    print("Cell phone detected! Activating TikTok mode.")
                    self.pookie.handy += 1
                    if isinstance(self.scene_manager.current_scene, self.scene_manager.scenes[0]):
                        self.activate_tiktok_mode()
                    elif isinstance(self.scene_manager.current_scene, self.scene_manager.scenes[1]):
                        self.scene_manager.current_scene.setUsingHandy(True)

            if label == "book" or label == "laptop":
                book_detected = True
                if not self.book_mode_active:
                    self.book_mode_active = True
                    print("Book/Laptop detected! Activating learn mode.")
                    self.pookie.learn += 1
                    self.pookie.isLearning = True
                    self.handle_book_detection()

        # Reset states if objects are no longer detected
        if not cell_phone_detected and self.tiktok_mode_active:
            self.tiktok_mode_active = False
            print("Cell phone no longer detected. Resetting to normal mode.")
            self.reset_to_normal()
            if isinstance(self.scene_manager.current_scene, self.scene_manager.scenes[1]):
                self.scene_manager.current_scene.setUsingHandy(False)

        if not book_detected and self.book_mode_active:
            self.pookie.walk_to_learnroom = False
            self.book_mode_active = False
            print("Book/Laptop no longer detected. Resetting to normal mode.")
            self.pookie.isLearning = False
            self.reset_to_normal()

    def handle_book_detection(self):
        self.pookie.walk_to_learnroom = True
        self.pookie.handle_walk_to_learnroom()

    def activate_tiktok_mode(self):
        self.pookie.perform_animation("handy_modus", (448, 303), self.pookie.tikTokMessage())

    def reset_to_normal(self):
        """Reset to normal behavior."""
        self.scene_manager.current_scene.initialize_state()

