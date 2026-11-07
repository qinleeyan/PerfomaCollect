# Design Document: Terminal TUI Application for Dual-Model Dataset Generator

**Tanggal:** 2026-11-07  
**Status:** Menunggu Persetujuan (Pending Approval)  
**Target:** MVP TUI Terminal & Entrypoint  

---

## 1. Intent & Why
Pengguna ingin menjalankan aplikasi dengan perintah sederhana `python main.py` dari root direktori proyek, dan langsung disambut oleh antarmuka TUI interaktif di terminal. Pengguna dapat mengonfigurasi API model (Base URL, API Key, Model ID) secara langsung melalui form TUI saat aplikasi berjalan, tanpa harus mengutak-atik file kode atau file konfigurasi secara manual.

---

## 2. Goals, Non-Goals, & Anti-Goals

### Goals
- Menyediakan file entrypoint `main.py` di root direktori yang mengeksekusi TUI.
- Membangun antarmuka Textual TUI dengan navigasi multi-screen:
  - **Main Menu Screen:** Status konfigurasi kedua model, menu navigasi keyboard & mouse.
  - **Model Setup Screen:** Form input Base URL, Model ID, dan API Key (dengan masking password) untuk Question Model dan Answer Model secara terpisah.
  - **View Config Screen / Dialog:** Melihat konfigurasi yang tersimpan dengan API key ter-redact.
  - **Generation Setup Screen:** Form input topik, pilihan mode (Limited/Unlimited), pilihan format output (JSON, JSONL, CSV, XLSX), dan nama file.
  - **Progress Screen:** Tampilan visual progress bar, counter data, status stage, dan tombol/hotkey cancel (`Ctrl+C` atau `Esc`).
- Integrasi persistensi konfigurasi ke file lokal (`~/.dual-model-generator/config.json`) secara atomik.

### Non-Goals (Untuk Fase Ini)
- Mengirim pemanggilan API LLM nyata secara aktif (pada fase ini form menerima dan menyimpan konfigurasi API; mock feedback disiapkan sebelum integrasi pipeline LLM aktif).
- Ekspor dataset sebenarnya ke file disk (fokus pada arsitektur UI dan validasi form).

### Anti-Goals
- Tidak membekukan (*freeze*) TUI terminal saat aksi background atau submit form dijalankan.
- Tidak membocorkan API key dalam teks biasa di layar maupun log terminal.
- Tidak memaksa pengguna menghafal argumen CLI flag.

---

## 3. Constraints
- **Runtime:** Python 3.11+.
- **Framework UI:** Textual (`textual>=0.8.0`).
- **Penyimpanan:** Format JSON lokal standar dengan validasi Pydantic schema di `src/config/`.
- **Eksekusi:** Harus dapat dijalankan langsung dengan `python main.py` atau `python -m src.main`.

---

## 4. Architecture & Selected Approach

Dipilih **Pendekatan 1: Multi-Screen Textual App** dengan struktur modular:

```text
perfomaAgent/
├── main.py                     # Entrypoint root
├── src/
│   ├── main.py                 # Runner & app launcher
│   ├── app/                    # State management & app logic
│   ├── config/
│   │   ├── schema.py           # Pydantic schema model config
│   │   └── config_manager.py   # Loader, saver, masking utility
│   └── tui/
│       ├── app.py              # Textual App class & routing
│       ├── styles.tcss         # Styling & color theme terminal
│       ├── screens/
│       │   ├── main_menu.py
│       │   ├── model_setup.py
│       │   ├── generation_setup.py
│       │   ├── view_config.py
│       │   └── progress.py
│       └── widgets/
│           ├── header_card.py
│           └── model_status_badge.py
```

### Screen Flow
1. **Startup:** `main.py` -> `src.tui.app.DatasetGeneratorApp` memuat konfigurasi dari `config_manager`.
2. **Main Menu:** Menampilkan status `Question Model: Configured/Not Configured` dan `Answer Model: Configured/Not Configured`.
3. **Setup Model:** Pengguna memilih opsi [1] atau [2], mengisi URL, API Key, dan Model ID. Klik "Save" akan memvalidasi input via Pydantic dan menyimpan ke file JSON.
4. **Start Generation:** Opsi [3] aktif bila konfigurasi valid, mengarahkan ke form input topik, target count, dan format file.
5. **Progress Screen:** Menampilkan dashboard eksekusi interaktif dengan tombol kembali/berhenti yang aman.

---

## 5. Keputusan Teknis yang Diserahkan ke Builder
- Desain tata letak visual TCSS (warna aksen, border, padding) agar nyaman dan kontras di dark mode terminal.
- Shortcut keyboard (misal: `q` untuk quit, `esc` untuk back, `tab` untuk navigasi antar field input).
- Mekanisme dialog konfirmasi / toast notification saat konfigurasi berhasil disimpan.
