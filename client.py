import socket
import sys
import threading
import re

HEADER_LENGTH = 10
IP = "127.0.0.1"  # IP Server Chat
PORT = 9999        # Port Aplikasi

# Daftar kata kasar (sama dengan server)
KATA_KASAR = ['anjing', 'bego', 'goblok', 'bangsat', 'bajingan', 'tolol', 'idiot']

def sensor_kata_kasar(text):
    """
    Fungsi untuk menyensor kata kasar dalam teks.
    Returns: (censored_text, is_profane)
    """
    is_profane = False
    censored_text = text
    
    for kata in KATA_KASAR:
        # Pattern untuk match kata (case-insensitive, dengan boundary)
        pattern = re.compile(r'\b' + re.escape(kata) + r'\b', re.IGNORECASE)
        if pattern.search(censored_text):
            is_profane = True
            # Sensor: huruf pertama + bintang + huruf terakhir
            if len(kata) > 2:
                replacement = kata[0] + '*' * (len(kata) - 2) + kata[-1]
            else:
                replacement = '*' * len(kata)
            censored_text = pattern.sub(replacement, censored_text)
    
    return censored_text, is_profane

my_username = input("Masukkan Username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((IP, PORT))
except Exception as e:
    print(f"Gagal koneksi ke {IP}:{PORT}. Error: {e}")
    sys.exit()

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

print(f"Terhubung ke {IP}. Ketik pesan dan tekan Enter.")
print("=" * 60)
print("FITUR CHAT:")
print("  • @(username) pesan  - Kirim private message")
print("  • @list              - Lihat daftar user online")
print("  • Ketik biasa        - Broadcast ke semua user")
print("=" * 60)
print("\n⚠️  PERINGATAN: Kata kasar akan otomatis disensor!\n")

# Flag untuk menandakan koneksi masih aktif
running = True

def receive_messages():
    """Thread untuk menerima pesan dari server"""
    global running
    while running:
        try:
            # Terima header username
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print("\n[SYSTEM] Koneksi diputus oleh server")
                running = False
                break
            
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            
            # Terima header message
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            
            # Tampilkan pesan
            print(f"\r\033[K{username} > {message}")
            print(f"{my_username} > ", end='', flush=True)
            
        except Exception as e:
            if running:
                print(f"\n[ERROR] Koneksi terputus: {e}")
                running = False
            break

def send_messages():
    """Thread untuk mengirim pesan ke server"""
    global running
    while running:
        try:
            print(f"{my_username} > ", end='', flush=True)
            message = input()
            
            if not running:
                break
                
            if message.strip():
                # Sensor kata kasar sebelum dikirim
                censored_msg, is_profane = sensor_kata_kasar(message)
                
                # Kirim pesan asli ke server (server yang akan sensor untuk user lain)
                message_encoded = message.encode('utf-8')
                message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(message_header + message_encoded)
                
                # Tampilkan pesan tersensor di client sendiri jika mengandung kata kasar
                if is_profane:
                    print(f"\033[A\033[K{my_username} > {censored_msg} [⚠️ Kata kasar disensor]")
                
        except KeyboardInterrupt:
            print("\n[SYSTEM] Keluar dari chat...")
            running = False
            break
        except Exception as e:
            if running:
                print(f"\n[ERROR] Gagal mengirim pesan: {e}")
                running = False
            break

# Mulai thread untuk menerima pesan
receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

# Jalankan fungsi kirim pesan di main thread
try:
    send_messages()
except KeyboardInterrupt:
    print("\n[SYSTEM] Keluar dari chat...")
finally:
    running = False
    client_socket.close()
    sys.exit()