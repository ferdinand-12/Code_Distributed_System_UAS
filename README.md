# Python Chat Application (Socket + Select + Multithreading)

## 🧩 Deskripsi Proyek
Aplikasi ini adalah program chat sederhana berbasis **socket** yang terdiri dari:

- **server.py** — menggunakan `select` untuk menangani banyak client
- **client.py** — menggunakan `threading` supaya bisa kirim & terima pesan bersamaan

Proyek ini dibuat sebagai implementasi dasar **Distributed System**, dengan fitur real-time messaging, private chat, dan sensor kata kasar.

---

## 🚀 Fitur Utama

### 🔹 1. Broadcast Message  
Semua pesan yang dikirim user akan dikirim ke seluruh user lain yang online.

### 🔹 2. Private Message  
Kirim pesan langsung ke user tertentu:

@username pesan

nginx
Salin kode

atau

@(username) pesan

yaml
Salin kode

### 🔹 3. List User Online  
Menampilkan daftar user yang sedang aktif:

@list

yaml
Salin kode

### 🔹 4. Sensor Kata Kasar  
Server & client otomatis menyensor kata kasar:

anjing → a*g
goblok → g**k

yaml
Salin kode

### 🔹 5. Notifikasi Join/Leave  
User lain akan diberi tahu ketika seseorang bergabung atau keluar.

### 🔹 6. Arsitektur Distributed System  
- Server → menggunakan **select** (non-blocking I/O, tanpa threading)  
- Client → menggunakan **thread terpisah** untuk menerima pesan

---

## 📁 Struktur Folder

📦 project-chat
│
├── server.py # Program server utama (select)
├── client.py # Program client (threading)
└── README.md # Dokumentasi


Semua komunikasi berjalan melalui protokol TCP
