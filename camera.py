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
    def __init__(self):
        self.stop_event = threading.Event()
        self.detection_thread = threading.Thread(target=self.detect_objects)

        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (640, 480)}))
        self.picam2.start()

        # COCO-Klassennamen laden
        class_file = "neural/frozen/coco.names"
        with open(class_file, "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]

        # SSD MobileNet-Modell laden
        self.net = cv2.dnn_DetectionModel(
            "neural/frozen/frozen_inference_graph.pb",
            "neural/frozen/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
        )
        self.net.setInputSize(320, 320)
        self.net.setInputScale(1.0 / 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)

    def start_detection(self):
        if not self.detection_thread.is_alive():
            self.detection_thread = threading.Thread(target=self.detect_objects)
            self.detection_thread.start()

    def stop_detection(self):
        self.stop_event.set()
        self.detection_thread.join()
        print("Detection stopped.")

    def detect_objects(self):
        """ Kontinuierliches Erfassen von Frames und Objekterkennung."""
        while not self.stop_event.is_set():
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            print("Suche nach Objekten...")

            # Objekterkennung durchführen
            result, detected_objects = self.perform_detection(frame)

            # Ergebnisse anzeigen
            self.display_results(frame, detected_objects)

    def perform_detection(self, frame, threshold=0.5, nms=0.1):
        """ Führt das SSD MobileNet-Modell aus und erhält Erkennungen."""
        class_ids, confidences, boxes = self.net.detect(frame, confThreshold=threshold, nmsThreshold=nms)
        detected_objects = []

        if len(class_ids) != 0:
            for class_id, confidence, box in zip(class_ids.flatten(), confidences.flatten(), boxes):
                class_name = self.class_names[class_id - 1]
                detected_objects.append({"label": class_name, "confidence": confidence, "box": box})

        return frame, detected_objects

    def display_results(self, frame, detected_objects):
        """ Zeigt das Bild mit den erkannten Objekten im Fenster an."""
        for obj in detected_objects:
            x, y, w, h = obj["box"]
            label = obj["label"]
            confidence = obj["confidence"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = f"{label} {confidence:.2f}"
            cv2.putText(frame, text, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        timestamp = int(time.time())
        filename = f"{SAVE_DIR}/detection_{timestamp}.jpg"
        cv2.imwrite(filename, frame)

        cv2.imshow("Object Detection", frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    detector = ObjectDetector()
    detector.start_detection()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        detector.stop_detection()
        cv2.destroyAllWindows()

