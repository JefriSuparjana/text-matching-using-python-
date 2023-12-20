import tkinter as tk
from tkinter import ttk
import mysql.connector
import speech_recognition as sr
from fuzzywuzzy import fuzz
from nltk.tokenize import word_tokenize

class AplikasiPencarian(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Pencarian Data")
        self.geometry("400x200")

        self.teks_label = ttk.Label(self, text="Masukkan kata kunci:")
        self.teks_label.pack(pady=10)

        self.entry_kata_kunci = ttk.Entry(self)
        self.entry_kata_kunci.pack(pady=10)

        self.cari_button = ttk.Button(self, text="Cari", command=self.cari_teks_murni)
        self.cari_button.pack(pady=10)

        self.teks_hasil = ttk.Label(self, text="")
        self.teks_hasil.pack(pady=10)

        self.speak_button = ttk.Button(self, text="Gunakan Speak to Text", command=self.cari_speak_to_text)
        self.speak_button.pack(pady=10)

        # Koneksi ke database
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Ganti dengan username MySQL Anda
            password="",  # Ganti dengan password MySQL Anda
            database="cnnmail"  # Ganti dengan nama database Anda
        )

    def cari_teks_murni(self):
        kata_kunci = self.entry_kata_kunci.get()
        hasil_pencarian = self.cari_data(kata_kunci)

        threshold = 75
        self.tampilkan_hasil_pencarian(hasil_pencarian, threshold)

    def cari_speak_to_text(self):
        hasil_speak_to_text = self.speak_to_text()
        print(f"Hasil Speak to Text: {hasil_speak_to_text}")
        if hasil_speak_to_text:
            kata_kunci_speak = hasil_speak_to_text.lower()
            # Perbarui nilai entry_kata_kunci
            self.entry_kata_kunci.delete(0, tk.END)  # Hapus teks yang ada
            self.entry_kata_kunci.insert(0, kata_kunci_speak)  # Masukkan hasil Speak to Text
            # Lanjutkan dengan pencarian
            hasil_pencarian = self.cari_data(kata_kunci_speak)
            threshold = 75
            self.tampilkan_hasil_pencarian(hasil_pencarian, threshold)

    def cari_data(self, kata_kunci):
        print(f"Kata Kunci: {kata_kunci}")

        cursor = self.db_connection.cursor()

        # Tokenisasi kata kunci menggunakan NLTK (untuk bahasa Inggris)
        kata_kunci_tokens = word_tokenize(kata_kunci.lower())
        print(f"Sesudah Word Tokenization: {kata_kunci_tokens}")

        # Sesuaikan threshold sesuai kebutuhan
        threshold = 75

        # Ganti nama tabel dan kolom sesuai dengan struktur database Anda
        query = """
            SELECT 'articles' AS tipe, id AS kode, article, highlights
            FROM articles
            WHERE """ + ' OR '.join(['highlights LIKE %s']*len(kata_kunci_tokens)) + """
        """

        # Parameterized query untuk setiap token kata kunci
        params = ['%' + token + '%' for token in kata_kunci_tokens]

        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()

        if result:
            return result
        else:
            print("Tidak ada hasil dari database.")
            return []

    def speak_to_text(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Silakan ucapkan sesuatu...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            try:
                text = recognizer.recognize_google(audio, language="en-US")  # Ganti language ke "en-US"
                return text
            except sr.UnknownValueError:
                print("Maaf, tidak dapat mengenali ucapan.")
                return None



    def tampilkan_hasil_pencarian(self, hasil_pencarian, threshold):
        kata_kunci = self.entry_kata_kunci.get().lower()

        # Urutkan hasil_pencarian berdasarkan persentase kecocokan
        hasil_pencarian = sorted(hasil_pencarian, key=lambda x: fuzz.partial_ratio(kata_kunci, x[3].lower()), reverse=True)

        teks_hasil = ""
        for result in hasil_pencarian:
            tipe = result[0]
            highlights = result[3]

            persentase_kecocokan = fuzz.partial_ratio(kata_kunci, highlights.lower())

            if persentase_kecocokan >= threshold:
                teks_hasil += f"Tabel: {tipe}, Deskripsi: {highlights}, Persentase Kecocokan: {persentase_kecocokan}%\n"
                print(teks_hasil)  # Cetak ke terminal

        text_box = tk.Text(self, wrap="none", height=100, width=140)
        text_box.pack(pady=10)
        text_box.insert(tk.END, teks_hasil)  # Masukkan ke Text widget di program
        text_box.config(state="disabled")

        # Set scrollbar untuk scrolling vertikal
        scrollbar = tk.Scrollbar(self, command=text_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_box.config(yscrollcommand=scrollbar.set)

if __name__ == "__main__":
    aplikasi = AplikasiPencarian()
    aplikasi.mainloop()
