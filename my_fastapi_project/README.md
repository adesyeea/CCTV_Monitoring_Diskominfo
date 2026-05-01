# 🚦 AI Traffic Monitoring System — CCTV Vehicle API

FastAPI application untuk monitoring lalu lintas kendaraan via CCTV.

## Struktur Proyek

```
my_fastapi_project/
├── app/
│   ├── api/endpoints/     # Route handlers
│   ├── core/              # Config & security
│   ├── db/                # Database engine & models (SQLAlchemy)
│   ├── schemas/           # Pydantic response/request schemas
│   ├── services/          # Business logic & ORM queries
│   └── main.py            # Entry point
├── tests/                 # Unit & integration tests
├── .env                   # Environment variables
└── pyproject.toml         # Dependencies
```

## Setup

```bash
# 1. Install dependencies
pip install -e .

# 2. Pastikan MySQL berjalan dan database cctv_vehicle tersedia
# 3. Sesuaikan konfigurasi di file .env

# 4. Jalankan server
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Path                | Deskripsi                     |
|--------|---------------------|-------------------------------|
| GET    | `/`                 | Dashboard                     |
| GET    | `/vehicles`         | Semua data kendaraan          |
| GET    | `/vehicles/masuk`   | Total kendaraan masuk         |
| GET    | `/vehicles/keluar`  | Total kendaraan keluar        |
| GET    | `/vehicles/today`   | Data kendaraan hari ini       |
| GET    | `/vehicles/cctv`    | Data per CCTV (device)        |
| GET    | `/vehicles/hourly`  | Data per jam                  |
| GET    | `/vehicles/realtime`| Data realtime (10 terbaru)    |

## API Docs

Buka `http://127.0.0.1:8000/docs` untuk Swagger UI.
