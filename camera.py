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
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (640, 480)}))
        self.picam2.start()

        # Load YOLO model
        self.net = cv2.dnn.readNet("neural/yolov7-tiny.weights", "neural/yolov7-tiny.cfg")
        # Set optimized backend for Raspberry Pi
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        with open("coco.names", "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        # State

        self.current_scene = self.scene_manager.current_scene

        # Track detection state
        self.tiktok_mode_active = False
        self.book_mode_active = False

    def start_detection(self):
        if not self.detection_thread.is_alive():
            self.detection_thread = threading.Thread(target=self.detect_objects)
            self.detection_thread.start()

    def stop_detection(self):
        self.stop_event.set()  # Stoppsignal setzen
        self.detection_thread.join()  # Warten, bis der Thread sauber beendet wurde
        print("Detection stopped.")

    def detect_objects(self):
        """Continuously capture frames and detect objects."""
        while not self.stop_event.is_set():
            print("Detect objects thread is running")
            frame = self.picam2.capture_array()

            # Preprocess frame
            #frame = self.preprocess_frame(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Perform object detection
            detections = self.perform_detection(frame)

            # Process detections
            detected_objects = self.process_detections(detections)

            # Handle detected objects
            self.handle_detected_objects(detected_objects, frame)

    def preprocess_frame(self, frame):
        """Preprocess the frame for YOLO."""
        if frame.shape[2] == 4:  # If it has 4 channels (RGBA)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        return frame

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
        """Handle detected objects and save images with bounding boxes."""
        cell_phone_detected = False
        book_detected = False

        for obj in detected_objects:
            label = obj["label"]
            confidence = obj["confidence"]
            x, y, w, h = obj["box"]
            print(f"Detected {label} with confidence {confidence:.2f}")

            # Draw bounding boxes
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Handle specific detections
            if label == "cell phone" or label == "remote":
                cell_phone_detected = True
                if not self.tiktok_mode_active:
                    self.tiktok_mode_active = True
                    print(f"Cell phone detected! Activating TikTok mode.")
                    self.pookie.handy += 1
                    if isinstance(self.scene_manager.current_scene, self.scene_manager.scenes[0]):
                        self.activate_tiktok_mode()
                    elif isinstance(self.scene_manager.current_scene, self.scene_manager.scenes[1]):
                        self.scene_manager.current_scene.setUsingHandy(True)

            if label == "book" or label == "laptop":
                book_detected = True
                if not self.book_mode_active:
                    self.book_mode_active = True
                    print(f"Book/Laptop detected! Activate learn mode.")
                    self.pookie.learn += 1
                    self.pookie.isLearning = True
                    self.handle_book_detection()

        # Save the image with detection results
        #timestamp = time.strftime("%Y%m%d-%H%M%S")
        #save_path = os.path.join(SAVE_DIR, f"detection_{timestamp}.jpg")
        #cv2.imwrite(save_path, frame)
        #print(f"Saved detection image: {save_path}")

        # Reset detection states if objects are no longer detected
        if not cell_phone_detected and self.tiktok_mode_active:
            self.tiktok_mode_active = False
            print("Cell phone no longer detected. Resetting to normal mode.")
            self.reset_to_normal()

        if not book_detected and self.book_mode_active:
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
        self.scene_manager.current_scene.initialize_state() #reset animation
