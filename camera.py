import cv2

# Load a pre-trained model for person detection
net = cv2.dnn.readNet('yolov4.weights', 'yolov4.cfg')
layer_names = net.getUnconnectedOutLayersNames()

# Initialize the camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to blob
    blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward(layer_names)

    # Process detections
    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = scores.argmax()
            confidence = scores[class_id]
            if class_id == 0 and confidence > 0.5:  # Class ID 0 is 'person' in YOLO
                print("Person detected!")
                # Add additional actions (e.g., alert)

    # Display the frame
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
