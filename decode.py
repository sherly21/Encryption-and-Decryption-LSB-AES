from tkinter import Tk, Label, Button, filedialog
from PIL import Image
from Crypto.Cipher import AES

KEY = b'YourEncryptionKey'  # Kunci enkripsi AES

# Fungsi untuk mendekripsi pesan dari gambar menggunakan LSB
def decrypt_message_lsb(image_file):
    img = Image.open(image_file)
    width, height = img.size
    pixel_count = width * height

    # Baca panjang pesan dari 32 bit pertama (4 byte)
    length_bin = ""
    i = 0
    while i < 32:
        if i >= pixel_count:
            raise ValueError("Pesan terlalu pendek untuk diekstraksi dari gambar.")
        x, y = i % width, i // width
        pixel = img.getpixel((x, y))
        length_bin += str(pixel[3] & 1)
        i += 1
    message_length = int(length_bin, 2)

    # Baca pesan dari bit LSB setelah panjang pesan
    message_bin = ""
    j = 0
    while j < message_length:
        if i >= pixel_count:
            raise ValueError("Pesan terlalu pendek untuk diekstraksi dari gambar.")
        x, y = i % width, i // width
        pixel = img.getpixel((x, y))
        message_bin += str(pixel[0] & 1)
        i += 1
        j += 1

    # Konversi pesan biner ke bytes
    message_bytes = bytearray()
    for k in range(0, len(message_bin), 8):
        byte = message_bin[k:k+8]
        message_bytes.append(int(byte, 2))

    return message_bytes

# Fungsi untuk mendekripsi file menggunakan AES
def decrypt_file_aes(key, input_file, decrypted_file):
    with open(input_file, 'rb') as file:
        encrypted_data = file.read()

    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(encrypted_data)

    with open(decrypted_file, 'wb') as file:
        file.write(decrypted_data)

# Fungsi untuk melakukan proses dekripsi dan ekstraksi pesan dari gambar
def decrypt_and_extract(image_file, output_file):
    # Dekripsi file gambar menggunakan AES
    decrypt_file_aes(KEY, image_file, output_file)

    # Ekstraksi pesan dari gambar menggunakan LSB
    message_bytes = decrypt_message_lsb(output_file)

    return message_bytes

# Fungsi untuk mengatur tampilan GUI
def create_gui():
    def browse_image():
        file_path = filedialog.askopenfilename(filetypes=[('Image files', '*.png;*.jpg;*.jpeg')])
        image_path.set(file_path)

    def decrypt_and_save():
        image_file = image_path.get()
        if image_file == "":
            result_label.config(text="Pilih gambar terenkripsi terlebih dahulu.")
            return

        try:
            output_file = filedialog.asksaveasfilename(defaultextension=".txt")
            decrypted_data = decrypt_and_extract(image_file, output_file)
            result_label.config(text="Pesan terdekripsi telah disimpan.")
        except Exception as e:
            result_label.config(text="Terjadi kesalahan saat dekripsi: " + str(e))

    root = Tk()
    root.title("Dekripsi Gambar")

    browse_button = Button(root, text="Pilih Gambar", command=browse_image)
    browse_button.pack(pady=10)

    image_path = Label(root, text="")
    image_path.pack()

    decrypt_button = Button(root, text="Dekripsi & Simpan", command=decrypt_and_save)
    decrypt_button.pack(pady=10)

    result_label = Label(root, text="")
    result_label.pack()

    root.mainloop()

# Jalankan tampilan GUI
create_gui()
