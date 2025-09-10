import cv2
import mediapipe as mp
import socket

# === Wi-Fi TCP Connection ===
ESP_IP = "192.168.4.1"  # ESP32 IP
PORT = 80
esp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
esp.connect((ESP_IP, PORT))

# === Grid Configuration ===
GRID_ROWS, GRID_COLS = 1, 3  # 1 row, 3 columns
GRID_COLOR = (255, 0, 0)
LINE_THICKNESS = 2

# === MediaPipe Setup ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# === Helper Functions ===
def get_grid_cell(x, y, width, height):
    row = 0  # only one row
    col = int(x / (width / GRID_COLS))
    return (row, col, y)

# === Webcam Setup ===
cap = cv2.VideoCapture(0)
last_command = ""

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Failed to read frame from webcam")
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Draw grid lines (3 columns)
    for i in range(1, GRID_COLS):
        x = int(w * i / GRID_COLS)
        cv2.line(frame, (x, 0), (x, h), GRID_COLOR, LINE_THICKNESS)

    # Add middle column divider (for forward/back split)
    mid_x = int(w / 3)  # start of middle column
    mid_x_end = int(2 * w / 3)
    mid_y = int(h / 2)
    cv2.line(frame, (mid_x, mid_y), (mid_x_end, mid_y), (0, 0, 255), 1)  # thin red line

    # Process frame
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    command_to_send = None  # Only set when necessary

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Palm center point (landmark 9)
            cx = int(hand_landmarks.landmark[9].x * w)
            cy = int(hand_landmarks.landmark[9].y * h)
            cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

            # Get grid position
            row, col, y_pos = get_grid_cell(cx, cy, w, h)

            # Axis-based control (no closed-hand check)
            if col == 0:
                command_to_send = "go_lf"
            elif col == 2:
                command_to_send = "go_rf"
            elif col == 1:
                if y_pos < h / 2:
                    command_to_send = "go_forward"
                else:
                    command_to_send = "go_back"
    else:
        # No hand detected → STOP
        command_to_send = "stop"

    # Send to ESP32 if command changes
    if command_to_send is not None and command_to_send != last_command:
        try:
            esp.send((command_to_send + '\n').encode())
            print("Sent:", command_to_send)
            last_command = command_to_send
        except Exception as e:
            print("Error sending command:", e)

    # Show webcam feed
    cv2.imshow("ESP32 Hand Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
        break

# === Cleanup ===
cap.release()
cv2.destroyAllWindows()
esp.close()
