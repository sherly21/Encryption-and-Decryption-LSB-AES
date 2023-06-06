from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import io
import os

# Fungsi untuk mengenkripsi file menggunakan AES
def encrypt_file_aes(key, input_file, output_file):
    cipher = AES.new(key.encode(), AES.MODE_ECB)  # Mengonversi kunci ke bytes
    with open(input_file, 'rb') as file:
        plaintext = file.read()
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    with open(output_file, 'wb') as file:
        file.write(ciphertext)

# Fungsi untuk menyisipkan pesan rahasia ke dalam gambar menggunakan LSB
def embed_message_lsb(image_file, message, output_file):
    img = Image.open(image_file)
    width, height = img.size
    pixel_count = width * height

    # Konversi pesan menjadi biner
    message_bin = ''.join(format(byte, '08b') for byte in message)
    message_length = len(message_bin)

    # Pastikan pesan dapat disisipkan dalam gambar
    max_message_length = pixel_count * 3 - 32  # Maximum message length in bits
    if message_length > max_message_length:
        raise ValueError("Ukuran pesan terlalu besar untuk gambar yang diberikan.")

    # Sisipkan panjang pesan pada 32 bit pertama (4 byte)
    length_bin = format(message_length, '032b')
    i = 0
    for bit in length_bin:
        if i >= pixel_count:
            raise ValueError("Ukuran gambar tidak mencukupi untuk menyisipkan pesan.")
        x, y = i % width, i // width
        pixel = img.getpixel((x, y))
        new_pixel = tuple(list(pixel[:3]) + [((pixel[3] & 0xFE) | int(bit))])
        img.putpixel((x, y), new_pixel)
        i += 1

    # Sisipkan pesan pada bit LSB setelah panjang pesan
    j = 0
    for bit in message_bin:
        if i >= pixel_count:
            raise ValueError("Ukuran gambar tidak mencukupi untuk menyisipkan pesan.")
        x, y = i % width, i // width
        pixel = img.getpixel((x, y))
        new_pixel = tuple([(pixel[0] & 0xFE) | int(bit)] + list(pixel[1:]))
        img.putpixel((x, y), new_pixel)
        i += 1
        j += 1

    # Simpan gambar hasil
    img.save(output_file)


# Fungsi untuk mengenkripsi dan menyisipkan pesan ke dalam gambar saat tombol 'Encrypt' ditekan
def encrypt_and_embed():
    input_file = filedialog.askopenfilename(title="Pilih File Dokumen", filetypes=[("All Files", "*.*")])
    if input_file:
        output_file = filedialog.asksaveasfilename(title="Simpan Gambar Hasil", defaultextension=".png", filetypes=[("Image Files", "*.png")])
        if output_file:
            key = key_entry.get()

            # Memastikan panjang kunci sesuai dengan mode AES yang digunakan
            if len(key) not in [16, 24, 32]:
                result_label.config(text="Panjang kunci harus 16, 24, atau 32 byte.")
                return

            try:
                # Mengenkripsi file menggunakan AES
                encrypted_file = 'encrypted_file.tmp'
                encrypt_file_aes(key, input_file, encrypted_file)

                # Memilih gambar untuk penyisipan
                image_file = filedialog.askopenfilename(title="Pilih Gambar Penyisipan", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
                if image_file:
                    # Sisipkan file yang telah dienkripsi ke dalam gambar menggunakan LSB
                    with open(encrypted_file, 'rb') as file:
                        encrypted_data = file.read()
                    embed_message_lsb(image_file, encrypted_data, output_file)

                    # Hapus file sementara yang telah dienkripsi
                    os.remove(encrypted_file)

                    result_label.config(text="Pengamanan selesai. Gambar hasil disimpan sebagai 'output.png'.")
                else:
                    result_label.config(text="Pilih gambar penyisipan.")
            except ValueError as e:
                result_label.config(text=str(e))
        else:
            result_label.config(text="Pilih lokasi penyimpanan gambar hasil.")
    else:
        result_label.config(text="Pilih file dokumen.")

# Fungsi untuk membuka dialog pemilihan gambar saat tombol 'Browse' ditekan
def browse_image_file():
    image_file = filedialog.askopenfilename(title="Pilih Gambar", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if image_file:
        image_file_entry.delete(0, tk.END)
        image_file_entry.insert(tk.END, image_file)

# Membuat GUI menggunakan Tkinter
window = tk.Tk()
window.title("Pengamanan Dokumen")
window.geometry("400x200")

key_label = tk.Label(window, text="Kunci Rahasia:")
key_label.pack()

key_entry = tk.Entry(window, show="*")
key_entry.pack()

image_file_label = tk.Label(window, text="Gambar Penyisipan:")
image_file_label.pack()

image_file_entry = tk.Entry(window)
image_file_entry.pack()

browse_button = tk.Button(window, text="Browse", command=browse_image_file)
browse_button.pack()

encrypt_button = tk.Button(window, text="Encrypt", command=encrypt_and_embed)
encrypt_button.pack()

result_label = tk.Label(window, text="")
result_label.pack()

window.mainloop()