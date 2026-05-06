import os, cv2, time, numpy as np
from datetime import datetime
from threading import Thread, Lock
from ultralytics import YOLO
from pynput import keyboard
from database import save_to_db

# --- OPTIMASI RESOURCE ---
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

# Load Model
model = YOLO("yolov8n.pt") 

# Mapping ID Kelas YOLO: 2=car, 3=motorcycle, 5=bus, 7=truck
VEHICLE_MAP = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
VEHICLE_CLASSES = list(VEHICLE_MAP.values())
STOP_PROGRAM = False
PRINT_LOCK = Lock()

CCTV_NAME = "PRAMBANAN"
CCTV_URL = "https://cctv.jogjaprov.go.id/cctv-proxy/atcs/Prambanan_TC.stream/playlist.m3u8"

# Area 
AREA_MASUK = np.array([(623,73),(628,182),(356,169),(428,48)], np.int32)
AREA_KELUAR = np.array([(619,193),(632,354),(48,352),(62,165)], np.int32)

stats = {"masuk": {c:0 for c in VEHICLE_CLASSES}, "keluar": {c:0 for c in VEHICLE_CLASSES}}
counted_ids = set()

def process_cctv():
    global STOP_PROGRAM
    cap = cv2.VideoCapture(CCTV_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    
    frame_idx = 0

    while not STOP_PROGRAM:
        ret, frame = cap.read()
        if not ret:
            cap.release(); time.sleep(2)
            cap = cv2.VideoCapture(CCTV_URL); continue

        frame_idx += 1
        if frame_idx % 4 != 0: continue

        frame = cv2.resize(frame, (640, 360))

        results = model.predict(frame, conf=0.2, iou=0.5, imgsz=640, classes=[2, 3, 5, 7], verbose=False, stream=True)

        # Gambar Area
        cv2.polylines(frame, [AREA_MASUK], True, (0, 255, 0), 2)
        cv2.polylines(frame, [AREA_KELUAR], True, (0, 0, 255), 2)

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = VEHICLE_MAP.get(cls_id, "unknown")
                
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # SENSOR: Titik ban (Tengah Bawah)
                cx = (x1 + x2) // 2
                cy = y2 

                # Visualisasi
                color = (255, 255, 0) if label == "car" else (0, 255, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
                cv2.putText(frame, f"{label}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                cv2.circle(frame, (cx, cy), 4, (255, 255, 255), -1)

                # ID Unik Grid (Mencegah Double Count)
                track_id = f"{label}_{cx//20}_{cy//20}"

                # Cek Area Masuk
                if cv2.pointPolygonTest(AREA_MASUK, (cx, cy), False) >= 0:
                    if f"{track_id}_in" not in counted_ids:
                        stats["masuk"][label] += 1
                        counted_ids.add(f"{track_id}_in")
                        print(f"[!] MASUK: {label.upper()} | Total: {sum(stats['masuk'].values())}")
                        Thread(target=save_to_db, args=(label, 1, CCTV_NAME), daemon=True).start()

                # Cek Area Keluar
                elif cv2.pointPolygonTest(AREA_KELUAR, (cx, cy), False) >= 0:
                    if f"{track_id}_out" not in counted_ids:
                        stats["keluar"][label] += 1
                        counted_ids.add(f"{track_id}_out")
                        print(f"[!] KELUAR: {label.upper()} | Total: {sum(stats['keluar'].values())}")
                        Thread(target=save_to_db, args=(label, 2, CCTV_NAME), daemon=True).start()

        cv2.imshow("Akurasi Motor Aktif", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): STOP_PROGRAM = True; break

    cap.release(); cv2.destroyAllWindows()

def display_rekap():
    while not STOP_PROGRAM:
        time.sleep(15)
        with PRINT_LOCK:
            now = datetime.now().strftime('%H:%M:%S')
            print(f"\n{'='*40}\n REKAP DATA PRAMBANAN | {now}\n{'='*40}")
            for arah in ["masuk", "keluar"]:
                detail = ", ".join([f"{k.upper()}:{v}" for k, v in stats[arah].items() if v > 0])
                print(f" {arah.upper():6} -> {detail if detail else 'Menunggu...'}")

def on_press(key):
    global STOP_PROGRAM
    try:
        if key.char == 'q': STOP_PROGRAM = True; return False
    except: pass

print("Sistem Dimulai. Tekan Q untuk berhenti.")
Thread(target=process_cctv, daemon=True).start()
Thread(target=display_rekap, daemon=True).start()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()