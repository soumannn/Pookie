import threading
from picamera2 import Picamera2
import cv2
import numpy as np
import os

SAVE_DIR = "detections"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

class ObjectDetector:
    def __init__(self, scene_manager, pookie):
        self.stop_event = threading.Event()
        self.detection_thread = threading.Thread(target=self.detect_objects)

        self.scene_manager = scene_manager
        self.pookie = pookie
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (640, 480)}))
        self.picam2.start()

        # Load COCO class names
        class_file = "coco.names"
        with open(class_file, "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]

        # Load SSD MobileNet model
        self.net = cv2.dnn_DetectionModel(
            "neural/frozen_inference_graph.pb",
            "neural/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
        )
        self.net.setInputSize(320, 320)
        self.net.setInputScale(1.0 / 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)

        # Track detection state
        self.tiktok_mode_active = False
        self.book_mode_active = False

    def start_detection(self):
        if not self.detection_thread.is_alive():
            self.detection_thread = threading.Thread(target=self.detect_objects)
            self.detection_thread.start()

    def stop_detection(self):
        self.stop_event.set()
        self.detection_thread.join()
        print("Detection stopped.")

    def detect_objects(self):
        """Continuously capture frames and detect objects."""
        while not self.stop_event.is_set():
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Perform object detection
            result, detected_objects = self.perform_detection(frame)

            # Handle detected objects
            self.handle_detected_objects(detected_objects)

    def perform_detection(self, frame, threshold=0.45, nms=0.2):
        """Run the SSD MobileNet model and get detections."""
        class_ids, confidences, boxes = self.net.detect(frame, confThreshold=threshold, nmsThreshold=nms)
        detected_objects = []

        if len(class_ids) != 0:
            for class_id, confidence, box in zip(class_ids.flatten(), confidences.flatten(), boxes):
                class_name = self.class_names[class_id - 1]
                detected_objects.append({"label": class_name, "confidence": confidence, "box": box})

        return frame, detected_objects

    def handle_detected_objects(self, detected_objects):
        """Handle detected objects and trigger events."""
        cell_phone_detected = False
        book_detected = False

        for obj in detected_objects:
            label = obj["label"]
            confidence = obj["confidence"]
            print(f"Detected {label} with confidence {confidence:.2f}")

            # Handle specific detections
            if label in ["cell phone", "remote"]:
                cell_phone_detected = True
                if not self.tiktok_mode_active:
                    self.tiktok_mode_active = True
                    print("Cell phone detected! Activating TikTok mode.")
                    self.pookie.handy += 1
                    if isinstance(self.scene_manager.current_scene, self.scene_manager.scenes[0]):
                        self.activate_tiktok_mode()
                    elif isinstance(self.scene_manager.current_scene, self.scene_manager.scenes[1]):
                        self.scene_manager.current_scene.setUsingHandy(True)

            if label in ["book", "laptop"]:
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
        self.scene_manager.current_scene.initialize_state()  # Reset animation

