import os
# Optimasi agar CPU tidak terlalu berat
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import cv2, time, numpy as np
from datetime import datetime
from threading import Thread, Lock
from ultralytics import YOLO
from pynput import keyboard
from database import save_to_db

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
model = YOLO("yolov8n.pt")

VEHICLE_CLASSES = ["car", "motorcycle", "bus", "truck"]
STOP_PROGRAM = False
PRINT_LOCK = Lock()

# --- KONFIGURASI RESOLUSI ---
# Menggunakan 480x270 agar ringan tapi tetap presisi untuk sensor
DISP_W, DISP_H = 480, 270 

# --- DATA CCTV & AREA (Koordinat Berbasis 640x360) ---
CCTV_NAME = "PRAMBANAN"
CCTV_URL = "https://cctv.jogjaprov.go.id/cctv-proxy/atcs/Prambanan_TC.stream/playlist.m3u8"

# Koordinat Raw (Jika terbalik, tukar isi AREA_MASUK dan AREA_KELUAR di sini)
AREA_MASUK_RAW = [(623,73),(628,182),(356,169),(428,48)]
AREA_KELUAR_RAW = [(619,193),(632,354),(48,352),(62,165)]

# Fungsi Scaling Polygon agar pas dengan resolusi window
def scale_area(area, target_w, target_h):
    pts = np.array(area, np.float32)
    pts[:, 0] *= (target_w / 640)
    pts[:, 1] *= (target_h / 360)
    return pts.astype(np.int32)

AREA_MASUK = scale_area(AREA_MASUK_RAW, DISP_W, DISP_H)
AREA_KELUAR = scale_area(AREA_KELUAR_RAW, DISP_W, DISP_H)

# Stats & Tracker
stats = {"masuk": {c:0 for c in VEHICLE_CLASSES}, "keluar": {c:0 for c in VEHICLE_CLASSES}}
counted_ids = set()

def process_cctv():
    global STOP_PROGRAM
    cap = cv2.VideoCapture(CCTV_URL)
    frame_idx = 0

    while not STOP_PROGRAM:
        ret, frame = cap.read()
        if not ret:
            cap.release(); time.sleep(2)
            cap = cv2.VideoCapture(CCTV_URL); continue

        frame_idx += 1
        # Skip frame (Ambil 1 tiap 5 frame) agar tidak ngelag
        if frame_idx % 5 != 0: continue

        # Resize tampilan
        frame_disp = cv2.resize(frame, (DISP_W, DISP_H))
        
        # Gambar Area (Hijau=Masuk, Merah=Keluar)
        cv2.polylines(frame_disp, [AREA_MASUK], True, (0, 255, 0), 1)
        cv2.polylines(frame_disp, [AREA_KELUAR], True, (0, 0, 255), 1)

        # Deteksi AI
        results = model.predict(frame_disp, conf=0.15, verbose=False)

        for box in results[0].boxes:
            label = model.names[int(box.cls[0])]
            if label not in VEHICLE_CLASSES: continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # --- TWEAK VALIDITAS: Sensor di Titik Ban (Bottom Center) ---
            cx = int((x1 + x2) / 2)
            cy = y2 # Titik paling bawah objek (ban kendaraan)
            
            # Visualisasi Titik Putih
            cv2.circle(frame_disp, (cx, cy), 3, (255, 255, 255), -1)
            cv2.rectangle(frame_disp, (x1, y1), (x2, y2), (255, 255, 0), 1)

            # ID Unik sementara untuk mencegah double count
            track_id = f"{label}_{cx//20}_{cy//20}"

            # Cek Area Masuk
            if cv2.pointPolygonTest(AREA_MASUK, (cx, cy), False) >= 0:
                if f"{track_id}_in" not in counted_ids:
                    stats["masuk"][label] += 1
                    counted_ids.add(f"{track_id}_in")
                    print(f"[!] {label.upper()} Masuk Area Hijau")
                    Thread(target=save_to_db, args=(label, 1, CCTV_NAME), daemon=True).start()

            # Cek Area Keluar
            elif cv2.pointPolygonTest(AREA_KELUAR, (cx, cy), False) >= 0:
                if f"{track_id}_out" not in counted_ids:
                    stats["keluar"][label] += 1
                    counted_ids.add(f"{track_id}_out")
                    print(f"[!] {label.upper()} Masuk Area Merah")
                    Thread(target=save_to_db, args=(label, 2, CCTV_NAME), daemon=True).start()

        cv2.imshow(f"Monitoring {CCTV_NAME}", frame_disp)
        if cv2.waitKey(1) & 0xFF == ord('q'): STOP_PROGRAM = True; break

    cap.release(); cv2.destroyAllWindows()

def display_rekap():
    while not STOP_PROGRAM:
        time.sleep(15)
        with PRINT_LOCK:
            now = datetime.now().strftime('%H:%M:%S')
            print(f"\n--- REKAP {CCTV_NAME} | {now} ---")
            for arah in ["masuk", "keluar"]:
                detail = ", ".join([f"{k.upper()}:{v}" for k,v in stats[arah].items() if v > 0])
                print(f" {arah.upper():6} -> {detail if detail else 'Menunggu...'}")

def on_press(key):
    global STOP_PROGRAM
    try:
        if key.char == 'q': STOP_PROGRAM = True; return False
    except: pass

# --- EKSEKUSI ---
print("Sistem Dimulai. Tekan 'Q' untuk berhenti.")
Thread(target=process_cctv, daemon=True).start()
Thread(target=display_rekap, daemon=True).start()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

print("Program Berhenti.")