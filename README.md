# Python Chat Application (Socket + Select + Multithreading)

## 🧩 Deskripsi Proyek
Aplikasi ini adalah program chat sederhana berbasis **socket** yang terdiri dari dua file utama:

- **server.py** — menggunakan `select` untuk menangani banyak client
- **client.py** — menggunakan `threading` untuk mengirim dan menerima pesan secara bersamaan

Proyek ini dibuat sebagai implementasi dasar **Distributed System**, dengan fitur real-time messaging, private chat, sensor kata kasar, dan fitur list user online.

## 🚀 Fitur Utama

### 🔹 1. Broadcast Message
Semua pesan yang dikirim user akan diteruskan ke seluruh user lain yang sedang online.

### 🔹 2. Private Message
Kirim pesan langsung ke user tertentu menggunakan format:

@username pesan

atau:

@(username) pesan

### 🔹 3. List User Online
Menampilkan daftar user yang sedang aktif:

@list

### 🔹 4. Sensor Kata Kasar
Server & client otomatis menyensor kata kasar:

anjing → a*g
goblok → g**k

### 🔹 5. Notifikasi Join/Leave
User lain akan menerima informasi ketika seseorang masuk atau keluar dari server.

### 🔹 6. Arsitektur Distributed System
- **Server** → menggunakan `select` (non-blocking I/O)
- **Client** → menggunakan thread terpisah untuk menerima pesan

---

## 📁 Struktur Folder

📦 project-chat
│
├── server.py # Program server utama (select)
├── client.py # Program client (threading)
└── README.md # Dokumentasi