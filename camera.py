import threading
from picamera2 import Picamera2
import cv2
import numpy as np
import os
import time

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
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (640, 480)}))
        self.picam2.start()

        self.trackFor = ["sports ball", "cell phone", "book"]

        # Load COCO class names
        class_file = "neural/frozen/coco.names"
        with open(class_file, "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]

        # Load SSD MobileNet model
        self.net = cv2.dnn_DetectionModel(
            "neural/frozen/frozen_inference_graph.pb",
            "neural/frozen/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
        )
        self.net.setInputSize(320, 320)
        self.net.setInputScale(1.0 / 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)

        # Track detection state
        self.tiktok_mode_active = False
        self.book_mode_active = False
        self.ball_mode_active = False

        self.last_cell_phone_detection = time.time()
        self.last_book_detection = time.time()

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
            print("Searching for clues..")

            # Perform object detection
            result, detected_objects = self.perform_detection(frame)

            # Handle detected objects
            self.handle_detected_objects(detected_objects, result)


    def perform_detection(self, frame, threshold=0.5, nms=0.1):
        """Run the SSD MobileNet model and get detections."""
        class_ids, confidences, boxes = self.net.detect(frame, confThreshold=threshold, nmsThreshold=nms)
        detected_objects = []

        if len(class_ids) != 0:
            for class_id, confidence, box in zip(class_ids.flatten(), confidences.flatten(), boxes):
                class_name = self.class_names[class_id - 1]
                if class_name in self.trackFor:
                    detected_objects.append({"label": class_name, "confidence": confidence, "box": box})

        return frame, detected_objects


    def handle_detected_objects(self, detected_objects, frame):
        """Handle detected objects and trigger events with reset on mode switch."""
        cell_phone_detected = False
        book_detected = False
        ball_detected = True
        current_time = time.time()

        for obj in detected_objects:
            label = obj["label"]
            confidence = obj["confidence"]


            print(f"Detected {label} with confidence {confidence:.2f}")


            # Handle cell phone detection
            if label == "cell phone":
                cell_phone_detected = True
                self.last_cell_phone_detection = current_time  # Update last detection time

                # If book mode was active, immediately reset before activating phone mode
                if self.book_mode_active:
                    print("Switching from book to phone! Resetting mode.")
                    self.reset_to_normal()
                    self.book_mode_active = False
                    self.pookie.isLearning = False

                if not self.tiktok_mode_active:
                    self.tiktok_mode_active = True
                    print("Cell phone detected! Activating TikTok mode.")
                    self.pookie.handy += 1
                    if isinstance(self.scene_manager.current_scene, self.scene_manager.scenes[0]):
                        self.activate_tiktok_mode()
                    elif isinstance(self.scene_manager.current_scene, self.scene_manager.scenes[1]):
                        self.scene_manager.current_scene.setUsingHandy(True)

            # Handle book detection
            if label == "book":
                book_detected = True
                self.last_book_detection = current_time  # Update last detection time

                # If phone mode was active, immediately reset before activating book mode
                if self.tiktok_mode_active:
                    print("Switching from phone to book! Resetting mode.")
                    self.reset_to_normal()
                    self.tiktok_mode_active = False

                if not self.book_mode_active:
                    self.book_mode_active = True
                    print("Book/Laptop detected! Activating learn mode.")
                    self.pookie.learn += 1
                    self.pookie.isLearning = True
                    self.handle_book_detection()

            if label == "sports ball":
                ball_detected = True
                self.last_ball_detection = current_time  # Update last detection time

                if not self.ball_mode_active:
                    self.ball_mode_active = True
                    print("Ball detected! Activating walk to door.")
                    self.pookie.walk_to_door = True

        # Reset states **only if 20 seconds pass without detection**
        if not cell_phone_detected and self.tiktok_mode_active:
            if current_time - self.last_cell_phone_detection > 20:  # 20 sec delay
                self.tiktok_mode_active = False
                print("Cell phone no longer detected for 20 seconds. Resetting to normal mode.")
                self.reset_to_normal()
                if isinstance(self.scene_manager.current_scene, self.scene_manager.scenes[1]):
                    self.scene_manager.current_scene.setUsingHandy(False)

        if not book_detected and self.book_mode_active:
            if current_time - self.last_book_detection > 20:  # 20 sec delay
                self.pookie.walk_to_learnroom = False
                self.book_mode_active = False
                print("Book/Laptop no longer detected for 20 seconds. Resetting to normal mode.")
                self.pookie.isLearning = False
                self.reset_to_normal()

        if not ball_detected and self.ball_mode_active:
            if current_time - self.last_ball_detection > 20:  # 20 sec delay
                self.ball_mode_active = False
                print("Ball no longer detected for 20 seconds. Resetting walk to door.")
                self.pookie.walk_to_door = False

        timestamp = int(time.time())
        filename = f"detections/detection_{timestamp}.jpg"
        cv2.imwrite(filename, frame)

    def handle_book_detection(self):
        self.pookie.walk_to_learnroom = True
        self.pookie.handle_walk_to_learnroom()

    def activate_tiktok_mode(self):
        self.pookie.perform_animation("handy_modus", (448, 303), self.pookie.tikTokMessage())

    def reset_to_normal(self):
        """Reset to normal behavior."""
        self.scene_manager.current_scene.initialize_state()  # Reset animation

