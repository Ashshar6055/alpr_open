import cv2
import numpy as np
import requests
from openalpr import Alpr

# --- CONFIGURATION ---
USE_VIDEO_FILE = True  # Set to False to use IP cam
VIDEO_PATH = "sample_video.mp4"

# For IP Camera - enable later
# IP_CAMERA_URL = "rtsp://username:password@ip_address:port/path"
# USE_VIDEO_FILE = False

FRAME_SKIP = 5
REGION = "in"

# --- API CONFIGURATION ---
USE_API = False  # ✅ Set to True to use API
API_MODE = "add"  # "add" or "mark"
ADD_API_URL = "http://seedoai.mietjmu.in/api/v1/vehicle/add"
MARK_API_URL = "http://seedoai.mietjmu.in/api/v1/vehicle/mark"

# --- ALPR INITIALIZATION ---
alpr = Alpr(REGION, "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
if not alpr.is_loaded():
    print("Error loading OpenALPR")
    exit(1)

alpr.set_top_n(1)

# --- CAPTURE STREAM ---
cap = cv2.VideoCapture(VIDEO_PATH if USE_VIDEO_FILE else IP_CAMERA_URL)
frame_count = 0

print("🚀 ALPR started... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("📛 Couldn't read frame.")
        break

    frame_count += 1
    if frame_count % FRAME_SKIP != 0:
        continue

    _, jpeg = cv2.imencode('.jpg', frame)
    results = alpr.recognize_array(jpeg.tobytes())

    for plate in results['plates']:
        candidate = plate['candidates'][0]
        plate_text = candidate['plate']
        confidence = candidate['confidence']
        coords = [(pt['x'], pt['y']) for pt in plate['coordinates']]

        # Draw bounding box and label
        cv2.polylines(frame, [np.array(coords, dtype=np.int32)], True, (0, 255, 0), 2)
        label = f"{plate_text} ({confidence:.1f}%)"
        cv2.putText(frame, label, (coords[0][0], coords[0][1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        print(f"[INFO] Plate: {plate_text} | Confidence: {confidence:.2f}%")

        # --- API INTEGRATION ---
        if USE_API:
            payload = {"vehicleNumber": plate_text}
            try:
                if API_MODE == "add":
                    response = requests.post(ADD_API_URL, json=payload)
                elif API_MODE == "mark":
                    response = requests.post(MARK_API_URL, json=payload)
                else:
                    raise ValueError("Invalid API_MODE")

                if response.status_code == 200:
                    print(f"[✅ API] {API_MODE.upper()} successful for {plate_text}")
                else:
                    print(f"[❌ API] {API_MODE.upper()} failed: {response.text}")
            except Exception as e:
                print(f"[⚠️ API ERROR] {e}")

    cv2.imshow("ALPR Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
alpr.unload()
cv2.destroyAllWindows()
