import socket
import select
import re

# KONFIGURASI SERVER
HEADER_LENGTH = 10
IP = "0.0.0.0"  # Listen di semua interface
PORT = 9999     # Port yang kita izinkan di Firewall Ubuntu

# Daftar kata kasar untuk di-sensor
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

# Setup Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

# List untuk menampung socket yang aktif
sockets_list = [server_socket]

# Dictionary untuk menyimpan data user: {socket: {'header': ..., 'data': username}}
clients = {}

print(f"Server Chat berjalan di {IP}:{PORT}...")

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        return False

while True:
    # SELECT: Inti dari tugas Distributed System kamu
    # Memantau socket mana yang mengirim data (read_sockets)
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # 1. Jika ada koneksi baru masuk ke Server Socket
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            
            sockets_list.append(client_socket)
            clients[client_socket] = user
            
            username = user['data'].decode('utf-8')
            print(f"[LOG] Koneksi baru dari {client_address[0]}:{client_address[1]} username: {username}")
            
            # Broadcast info user baru join
            msg_content = f"{username} telah bergabung!".encode('utf-8')
            msg_header = f"{len(msg_content):<{HEADER_LENGTH}}".encode('utf-8')
            
            for client_sock in clients:
                if client_sock != client_socket:
                    client_sock.send(user['header'] + user['data'] + msg_header + msg_content)

        # 2. Jika ada pesan dari Client yang sudah terhubung
        else:
            message = receive_message(notified_socket)

            if message is False:
                print(f"[LOG] Koneksi ditutup oleh {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            msg_text = message['data'].decode('utf-8')
            username = user['data'].decode('utf-8')

            print(f"[CHAT] {username}: {msg_text}")

            # --- FITUR LIST USER (@list) ---
            if msg_text.strip() == "@list":
                online_users = ", ".join([c['data'].decode('utf-8') for c in clients.values()])
                system_msg = f"User Online: {online_users}".encode('utf-8')
                sys_header = f"{len(system_msg):<{HEADER_LENGTH}}".encode('utf-8')
                # Kirim balik hanya ke pengirim
                sender_name = "SERVER".encode('utf-8')
                sender_header = f"{len(sender_name):<{HEADER_LENGTH}}".encode('utf-8')
                notified_socket.send(sender_header + sender_name + sys_header + system_msg)
                continue

            # --- FITUR PRIVATE MESSAGE (@username) atau @(username) ---
            if msg_text.startswith("@") and msg_text != "@list":
                try:
                    # Handle format @username atau @(username)
                    rest_text = msg_text[1:].strip()
                    
                    # Cek apakah ada kurung
                    if rest_text.startswith("(") and ")" in rest_text:
                        # Format @(username)
                        close_paren = rest_text.index(")")
                        target_username = rest_text[1:close_paren].strip()
                        private_msg = rest_text[close_paren+1:].strip()
                    else:
                        # Format @username (tanpa kurung)
                        parts = rest_text.split(" ", 1)
                        if len(parts) < 2:
                            raise ValueError("Format salah")
                        target_username = parts[0]
                        private_msg = parts[1]
                    
                    if not private_msg:
                        raise ValueError("Pesan kosong")
                    
                    # Sensor kata kasar dalam private message
                    censored_msg, is_profane = sensor_kata_kasar(private_msg)
                    
                    target_socket = None
                    # Cari socket berdasarkan username
                    for sock, client_data in clients.items():
                        if client_data['data'].decode('utf-8') == target_username:
                            target_socket = sock
                            break
                    
                    if target_socket:
                        # Kirim pesan private yang sudah di-sensor
                        if is_profane:
                            priv_content = f"(Private) {censored_msg} [⚠️ Pesan mengandung kata kasar]".encode('utf-8')
                        else:
                            priv_content = f"(Private) {censored_msg}".encode('utf-8')
                        
                        priv_header = f"{len(priv_content):<{HEADER_LENGTH}}".encode('utf-8')
                        target_socket.send(user['header'] + user['data'] + priv_header + priv_content)
                        
                        # Kirim konfirmasi ke pengirim
                        if is_profane:
                            confirm_msg = f"Pesan terkirim ke {target_username}: {censored_msg} [⚠️ Kata kasar disensor]".encode('utf-8')
                        else:
                            confirm_msg = f"Pesan terkirim ke {target_username}".encode('utf-8')
                        
                        confirm_header = f"{len(confirm_msg):<{HEADER_LENGTH}}".encode('utf-8')
                        sender_name = "SERVER".encode('utf-8')
                        sender_header = f"{len(sender_name):<{HEADER_LENGTH}}".encode('utf-8')
                        notified_socket.send(sender_header + sender_name + confirm_header + confirm_msg)
                    else:
                        # User tidak ditemukan
                        err_msg = f"User {target_username} tidak ditemukan. Gunakan @list untuk melihat user online.".encode('utf-8')
                        err_header = f"{len(err_msg):<{HEADER_LENGTH}}".encode('utf-8')
                        sender_name = "SERVER".encode('utf-8')
                        sender_header = f"{len(sender_name):<{HEADER_LENGTH}}".encode('utf-8')
                        notified_socket.send(sender_header + sender_name + err_header + err_msg)
                    continue
                except (ValueError, IndexError):
                    # Format salah
                    err_msg = "Format private message salah. Gunakan: @(username) pesan atau @username pesan".encode('utf-8')
                    err_header = f"{len(err_msg):<{HEADER_LENGTH}}".encode('utf-8')
                    sender_name = "SERVER".encode('utf-8')
                    sender_header = f"{len(sender_name):<{HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send(sender_header + sender_name + err_header + err_msg)
                    continue

            # --- SENSOR KATA KASAR UNTUK BROADCAST ---
            censored_msg, is_profane = sensor_kata_kasar(msg_text)
            
            # Update message data dengan teks yang sudah di-sensor
            if is_profane:
                final_msg = f"{censored_msg} [⚠️ Pesan mengandung kata kasar]".encode('utf-8')
            else:
                final_msg = censored_msg.encode('utf-8')
            
            final_header = f"{len(final_msg):<{HEADER_LENGTH}}".encode('utf-8')

            # --- FITUR BROADCAST (Default) ---
            for client_sock in clients:
                if client_sock != notified_socket:
                    client_sock.send(user['header'] + user['data'] + final_header + final_msg)