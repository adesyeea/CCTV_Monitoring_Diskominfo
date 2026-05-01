import os, cv2, time, numpy as np
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

CCTV_FEEDS = {
    "CCTV1": "https://cctv.jogjaprov.go.id/cctv-proxy/atcs/DemenGlagah_TC.stream/playlist.m3u8",
    "CCTV2": "https://cctv.jogjaprov.go.id/cctv-proxy/atcs/Prambanan_TC.stream/playlist.m3u8",
    "CCTV3": "https://cctv.jogjaprov.go.id/cctv-proxy/cctv-kominfogk/TuguSelamatDatangPatuk.stream/playlist.m3u8",
    "CCTV4": "https://mam.jogjaprov.go.id:1937/cctv-kominfosleman/Perempatan_Beran1.stream/playlist.m3u8"
}

AREA_MASUK = {
    "CCTV1": [(517,50),(572,77),(198,169),(179,129)], "CCTV2": [(623,73),(628,182),(356,169),(428,48)],
    "CCTV3": [(381,77),(438,91),(324,146),(270,116)], "CCTV4": [(587,130),(407,102),(525,42),(632,69)]
}
AREA_KELUAR = {
    "CCTV1": [(414,129),(474,182),(637,103),(616,68)], "CCTV2": [(619,193),(632,354),(48,352),(62,165)],
    "CCTV3": [(295,170),(492,259),(354,350),(136,230)], "CCTV4": [(61,127),(168,168),(472,37),(414,31)]
}

stats = {name: {"masuk": {c:0 for c in VEHICLE_CLASSES}, "keluar": {c:0 for c in VEHICLE_CLASSES}} for name in CCTV_FEEDS}
counted_ids = {name: set() for name in CCTV_FEEDS}

def process_cctv(name, url):
    global STOP_PROGRAM
    cap = cv2.VideoCapture(url)
    while not STOP_PROGRAM:
        ret, frame = cap.read()
        if not ret: 
            cap.release(); time.sleep(2); cap = cv2.VideoCapture(url); continue
        frame = cv2.resize(frame, (640, 360))
        cv2.polylines(frame, [np.array(AREA_MASUK[name], np.int32)], True, (0, 255, 0), 2)
        cv2.polylines(frame, [np.array(AREA_KELUAR[name], np.int32)], True, (0, 0, 255), 2)
        
        results = model.predict(frame, conf=0.4, verbose=False)
        for box in results[0].boxes:
            label = model.names[int(box.cls[0])]
            if label not in VEHICLE_CLASSES: continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx, cy = (x1+x2)//2, (y1+y2)//2
            track_id = f"{label}_{cx//30}_{cy//30}"

            if cv2.pointPolygonTest(np.array(AREA_MASUK[name], np.int32), (cx,cy), False) >= 0:
                if f"{track_id}_in" not in counted_ids[name]:
                    stats[name]["masuk"][label] += 1
                    counted_ids[name].add(f"{track_id}_in")
                    save_to_db(label, 1, name)
            elif cv2.pointPolygonTest(np.array(AREA_KELUAR[name], np.int32), (cx,cy), False) >= 0:
                if f"{track_id}_out" not in counted_ids[name]:
                    stats[name]["keluar"][label] += 1
                    counted_ids[name].add(f"{track_id}_out")
                    save_to_db(label, 2, name)

        cv2.imshow(name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): STOP_PROGRAM = True; break
    cap.release(); cv2.destroyWindow(name)

def display_rekap():
    while not STOP_PROGRAM:
        time.sleep(15)
        with PRINT_LOCK:
            print("\n" + "="*50 + f"\n REKAP DETAIL - {datetime.now().strftime('%H:%M:%S')}\n" + "="*50)
            for name in CCTV_FEEDS:
                for arah in ["masuk", "keluar"]:
                    detail = ", ".join([f"{k.upper()}:{v}" for k,v in stats[name][arah].items() if v > 0])
                    print(f" {name} {arah.upper():6} -> {detail if detail else 'Kosong'}")
            print("="*50)

def on_press(key):
    global STOP_PROGRAM
    try:
        if key.char == 'q': STOP_PROGRAM = True; return False
    except: pass

for name, url in CCTV_FEEDS.items():
    Thread(target=process_cctv, args=(name, url), daemon=True).start()
Thread(target=display_rekap, daemon=True).start()
with keyboard.Listener(on_press=on_press) as listener: listener.join()