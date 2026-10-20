
import cv2

# Create the person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(
    cv2.HOGDescriptor_getDefaultPeopleDetector()
)

# Open webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open camera.")
else:
    print("Camera started. Press Q in the camera window to exit.")

    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read camera frame.")
            break

        # Detect people in the video
        boxes, weights = hog.detectMultiScale(
            frame,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05
        )

        # Draw boxes around detected people
        for (x, y, w, h) in boxes:
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

        # Display the detection count
        cv2.putText(
            frame,
            f"People detected: {len(boxes)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow("EduSense AI Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()
print("Camera closed.")
