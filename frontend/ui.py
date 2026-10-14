import os
import time
import tkinter as tk

from backend.m1_pesanan import Pesanan, Array, LinkList, muat_pesanan, format_waktu
from backend.m2_antrean import PengelolaAntrean, proses_struk
from backend.m3_laporan import (Pencacah, BATAS_INSERTION, ambil_awal, insertion_sort,
                                merge_sort, linear_search, binary_search)

FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JALUR_CSV = os.path.join(FOLDER, "data", "pesanan.csv")

# (kode, label, judul, info, isian)  kode "" = judul bagian
MENU = [
    ("", "DATA", "", "", ()),
    ("load", "Load", "Muat data pesanan", "Baca data/pesanan.csv, isi array, linked list, dan antrean.", ()),

    ("", "M1 - DATA PESANAN", "", "", ()),
    ("array_lihat", "ARRAY - LIHAT PESANAN", "Array: lihat pesanan ke-i",
     "Alamat bisa dihitung langsung. O(1).", (("Nomor pesanan ke-", "1"),)),
    ("array_reguler", "ARRAY - TAMBAH PESANAN REGULER", "Array: REGULER, masuk belakang",
     "append. O(1) amortized.", (("Nama pelanggan", "Pelanggan Baru"),)),
    ("array_prioritas", "ARRAY - TAMBAH PESANAN PRIORITAS", "Array: PRIORITAS, masuk tengah",
     "insert di tengah, separuh isi digeser. O(n).", (("Nama pelanggan", "Pelanggan Baru"),)),
    ("array_vip", "ARRAY - TAMBAH PESANAN VIP", "Array: VIP, masuk paling depan",
     "insert di indeks 0, semua isi digeser. O(n).", (("Nama pelanggan", "Pelanggan Baru"),)),
    ("array_hapus", "ARRAY - HAPUS PESANAN", "Array: hapus pesanan ke-i",
     "Isi di kanan digeser ke kiri. O(n).", (("Nomor pesanan ke-", "1"),)),
    ("link_lihat", "LINKEDLIST - LIHAT PESANAN", "Linked list: lihat pesanan ke-i",
     "Jalan dari head satu per satu. O(n).", (("Nomor pesanan ke-", "1"),)),
    ("link_reguler", "LINKEDLIST - TAMBAH PESANAN REGULER", "Linked list: REGULER, masuk belakang",
     "Lewat tail. O(1).", (("Nama pelanggan", "Pelanggan Baru"),)),
    ("link_prioritas", "LINKEDLIST - TAMBAH PESANAN PRIORITAS", "Linked list: PRIORITAS, masuk tengah",
     "Telusur sampai tengah O(n), sambung O(1).", (("Nama pelanggan", "Pelanggan Baru"),)),
    ("link_vip", "LINKEDLIST - TAMBAH PESANAN VIP", "Linked list: VIP, masuk paling depan",
     "Cukup ubah head. O(1).", (("Nama pelanggan", "Pelanggan Baru"),)),
    ("link_hapus", "LINKEDLIST - HAPUS PESANAN", "Linked list: hapus pesanan ke-i",
     "Telusur lalu sambung ulang. O(n).", (("Nomor pesanan ke-", "1"),)),

    ("", "M2 - STACK DAN QUEUE", "", "", ()),
    ("stack_postfix", "STACK - POSTFIX (MESIN KASIR)", "Stack: hitung struk lewat postfix",
     "Tahap 1 infix ke postfix, tahap 2 hitung. Keduanya pakai stack.",
     (("Struk belanja (infix)", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000"),)),
    ("stack_undo", "STACK - UNDO", "Stack: batalkan aksi antrean terakhir",
     "Ambil catatan teratas tumpukan undo, jalankan kebalikannya.", ()),
    ("stack_redo", "STACK - REDO", "Stack: ulangi aksi yang dibatalkan",
     "Ambil catatan teratas tumpukan redo, kerjakan aksi aslinya.", ()),
    ("queue_enqueue", "QUEUE - ENQUEUE", "Queue: pesanan baru masuk belakang",
     "Masuk ke kedua antrean (naif dan melingkar).", (("Nama pelanggan", "Pelanggan Baru"),)),
    ("queue_naif", "QUEUE - DEQUEUE NAIF", "Queue naif: ambil depan, isi digeser",
     "Ambil indeks 0, sisa digeser ke kiri. O(n). Hanya pembanding, tidak masuk undo.",
     (("Berapa kali dequeue", "1"),)),
    ("queue_circular", "QUEUE - DEQUEUE CIRCULAR", "Queue circular: ambil depan, front maju",
     "Hanya front yang maju, tidak ada yang digeser. O(1).", (("Berapa kali dequeue", "1"),)),

    ("", "M3 - SORT DAN SEARCH", "", "", ()),
    ("sort_insertion", "SORT - INSERTION SORT", "Insertion sort: urutkan n baris pertama",
     "Stabil, O(n^2). Dibatasi 20.000 baris. Melaporkan perbandingan dan pemindahan.",
     (("Jumlah baris", "10"), ("Kunci", ("harga", "oid", "selesai")))),
    ("sort_merge", "SORT - MERGE SORT", "Merge sort: urutkan n baris pertama",
     "Stabil, O(n log n). Sanggup mengurutkan seluruh data.",
     (("Jumlah baris", "4000"), ("Kunci", ("oid", "harga", "selesai")))),
    ("search_linear", "SEARCH - LINEAR SEARCH", "Linear search: cari oid",
     "Telusur satu per satu, data tidak perlu terurut. O(n).", (("oid yang dicari", "O-137442"),)),
    ("search_binary", "SEARCH - BINARY SEARCH", "Binary search: cari oid",
     "Butuh daftar terurut oid (dibangun sekali dengan merge sort). O(log n).",
     (("oid yang dicari", "O-137442"),)),
]


def ribuan(n):
    return f"{n:,}".replace(",", ".")  # 12345 -> 12.345


def rupiah(x):
    if x == int(x):
        x = int(x)
    return "Rp " + ribuan(x)


class Aplikasi:
    def __init__(self, root):
        self.root = root
        root.title("2EZ4U Food Delivery")
        root.geometry("1180x720")
        self.data = None
        self.array_m1 = None
        self.link_m1 = None
        self.pengelola = None
        self.urut_oid = None  # daftar terurut oid untuk binary search
        self.nomor_baru = 0
        self.menu_aktif = None
        self.entri = []
        self.buat_tampilan()
        self.daftar.selection_set(1)
        self.pilih_menu(1)

    def buat_tampilan(self):
        tk.Label(self.root, text="2EZ4U Food Delivery", bg="#2c3e5a", fg="white",
                 font=("Helvetica", 14, "bold"), anchor="w", padx=12, pady=8).pack(fill="x")
        isi = tk.Frame(self.root)
        isi.pack(fill="both", expand=True)

        # kiri: daftar menu
        kiri = tk.Frame(isi, width=300)
        kiri.pack(side="left", fill="y")
        kiri.pack_propagate(False)
        gulung = tk.Scrollbar(kiri)
        gulung.pack(side="right", fill="y")
        self.daftar = tk.Listbox(kiri, yscrollcommand=gulung.set, exportselection=False)
        self.daftar.pack(side="left", fill="both", expand=True)
        gulung.config(command=self.daftar.yview)
        for m in MENU:
            if m[0] == "":
                self.daftar.insert("end", m[1])
                self.daftar.itemconfig("end", bg="#e8ecf2")
            else:
                self.daftar.insert("end", "  " + m[1])
        self.daftar.bind("<<ListboxSelect>>", self.klik_menu)

        # kanan: form dan hasil
        kanan = tk.Frame(isi, padx=12, pady=8)
        kanan.pack(side="left", fill="both", expand=True)
        self.label_judul = tk.Label(kanan, font=("Helvetica", 12, "bold"), anchor="w")
        self.label_judul.pack(fill="x")
        self.label_info = tk.Label(kanan, fg="#555555", anchor="w", justify="left", wraplength=800)
        self.label_info.pack(fill="x", pady=(0, 6))
        self.frame_form = tk.Frame(kanan)
        self.frame_form.pack(fill="x")
        tk.Button(kanan, text="JALANKAN", bg="#2c3e5a", fg="white", padx=20,
                  command=self.jalankan_menu).pack(anchor="w", pady=6)
        area = tk.Frame(kanan)
        area.pack(fill="both", expand=True)
        sb_y = tk.Scrollbar(area)
        sb_y.pack(side="right", fill="y")
        sb_x = tk.Scrollbar(area, orient="horizontal")
        sb_x.pack(side="bottom", fill="x")
        self.hasil = tk.Text(area, wrap="none", font="TkFixedFont", state="disabled",
                             yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.hasil.pack(side="left", fill="both", expand=True)
        sb_y.config(command=self.hasil.yview)
        sb_x.config(command=self.hasil.xview)

        # bawah: command
        bawah = tk.Frame(self.root, padx=12)
        bawah.pack(fill="x")
        tk.Label(bawah, text="COMMAND", font=("Helvetica", 8, "bold"), anchor="w").pack(fill="x")
        self.log = tk.Text(bawah, height=6, font="TkFixedFont", state="disabled")
        self.log.pack(fill="x")
        self.status = tk.Label(self.root, text="siap", bg="#2c3e5a", fg="white", anchor="w", padx=12)
        self.status.pack(fill="x", pady=(6, 0))

    def klik_menu(self, event):
        pilih = self.daftar.curselection()
        if len(pilih) > 0:
            self.pilih_menu(pilih[0])

    def pilih_menu(self, indeks):
        m = MENU[indeks]
        if m[0] == "":  # judul bagian, kembalikan pilihan
            self.daftar.selection_clear(0, "end")
            if self.menu_aktif is not None:
                self.daftar.selection_set(self.menu_aktif)
            return
        self.menu_aktif = indeks
        self.label_judul.config(text=m[2])
        self.label_info.config(text=m[3])
        for w in self.frame_form.winfo_children():
            w.destroy()
        self.entri = []
        for nama, awal in m[4]:
            tk.Label(self.frame_form, text=nama, anchor="w", font=("Helvetica", 9, "bold")).pack(fill="x")
            if isinstance(awal, tuple):  # pilihan
                pilihan = tk.StringVar(value=awal[0])
                tk.OptionMenu(self.frame_form, pilihan, *awal).pack(anchor="w", pady=(0, 4))
                self.entri.append(pilihan)
            else:
                kotak = tk.Entry(self.frame_form, width=60)
                kotak.insert(0, awal)
                kotak.pack(anchor="w", pady=(0, 4))
                kotak.bind("<Return>", self.jalankan_menu)
                self.entri.append(kotak)

    def jalankan_menu(self, event=None):
        if self.menu_aktif is None:
            return
        kode = MENU[self.menu_aktif][0]
        mulai = time.perf_counter()
        try:
            teks, modul = self.kerjakan(kode)
        except (ValueError, IndexError) as e:
            teks, modul = "GALAT: " + str(e), "error"
        waktu = self.waktu_teks((time.perf_counter() - mulai) * 1000)

        self.hasil.config(state="normal")
        self.hasil.delete("1.0", "end")
        self.hasil.insert("1.0", teks)
        self.hasil.config(state="disabled")
        self.log.config(state="normal")
        self.log.insert("1.0", f"{kode:<18}-> {modul:<22}{waktu}\n")  # terbaru di atas
        self.log.config(state="disabled")
        self.status.config(text=f"[{modul}] {waktu}")

    def waktu_teks(self, ms):
        if ms >= 1000:
            return f"{ms / 1000:.2f} s"
        return f"{ms:.2f} ms"

    def angka(self, nomor, nama):
        teks = self.entri[nomor].get().strip()
        if not teks.isdigit():
            raise ValueError(nama + " harus angka bulat positif")
        return int(teks)

    def kerjakan(self, kode):
        if kode == "load":
            return self.load()
        if kode == "stack_postfix":
            return self.postfix()
        if self.data is None:
            raise ValueError("Data belum dimuat. Klik menu Load dulu.")
        if kode == "array_lihat":
            return self.lihat(self.array_m1, "M1 - array")
        if kode == "link_lihat":
            return self.lihat(self.link_m1, "M1 - linked list")
        if kode == "array_reguler":
            return self.tambah(self.array_m1, "reguler", "M1 - array")
        if kode == "array_prioritas":
            return self.tambah(self.array_m1, "prioritas", "M1 - array")
        if kode == "array_vip":
            return self.tambah(self.array_m1, "vip", "M1 - array")
        if kode == "link_reguler":
            return self.tambah(self.link_m1, "reguler", "M1 - linked list")
        if kode == "link_prioritas":
            return self.tambah(self.link_m1, "prioritas", "M1 - linked list")
        if kode == "link_vip":
            return self.tambah(self.link_m1, "vip", "M1 - linked list")
        if kode == "array_hapus":
            return self.hapus(self.array_m1, "M1 - array")
        if kode == "link_hapus":
            return self.hapus(self.link_m1, "M1 - linked list")
        if kode == "stack_undo":
            return self.undo()
        if kode == "stack_redo":
            return self.redo()
        if kode == "queue_enqueue":
            return self.enqueue()
        if kode == "queue_naif":
            return self.dequeue_naif()
        if kode == "queue_circular":
            return self.dequeue_circular()
        if kode == "sort_insertion":
            return self.urutkan("insertion")
        if kode == "sort_merge":
            return self.urutkan("merge")
        if kode == "search_linear":
            return self.cari("linear")
        if kode == "search_binary":
            return self.cari("binary")
        raise ValueError("menu belum dikenal: " + kode)

    def load(self):
        if not os.path.exists(JALUR_CSV):
            raise ValueError("File tidak ditemukan: " + JALUR_CSV)
        self.data = muat_pesanan(JALUR_CSV)
        self.array_m1 = Array()
        self.link_m1 = LinkList()
        for i in range(self.data.panjang):  # data yang sama, dua struktur
            p = self.data.get(i)
            self.array_m1.append(p)
            self.link_m1.append(p)
        self.pengelola = PengelolaAntrean()
        self.pengelola.muat(self.data)
        self.urut_oid = None
        self.nomor_baru = self.data.panjang + 1
        self.array_m1.jumlah_geser = 0  # reset pencacah
        self.array_m1.jumlah_salin = 0
        self.link_m1.jumlah_telusur = 0
        q = self.pengelola
        teks = f"Data dimuat: {ribuan(self.data.panjang)} pesanan.\n"
        teks += "Array: " + self.array_m1.stats() + "\n"
        teks += "LinkList: " + self.link_m1.stats() + "\n"
        teks += f"Antrean (ANTRE): naif={ribuan(q.naif.panjang())}, melingkar={ribuan(q.melingkar.panjang())}, "
        teks += f"kapasitas={ribuan(q.melingkar.kapasitas)}"
        return teks, "M1 - muat"

    def detail(self, p):
        return (f"oid       : {p.oid}\npelanggan : {p.pelanggan}\nresto     : {p.resto}\n"
                f"menu      : {p.menu}\nharga     : {ribuan(p.harga)}\nprioritas : {p.prioritas}\n"
                f"masuk     : {format_waktu(p.t_masuk)}\nselesai   : {format_waktu(p.t_selesai)}\n"
                f"status    : {p.status}")

    def lihat(self, struktur, modul):
        nomor = self.angka(0, "Nomor pesanan")
        if nomor < 1 or nomor > struktur.panjang:
            raise ValueError("Nomor harus 1 sampai " + ribuan(struktur.panjang))
        teks = f"Pesanan ke-{ribuan(nomor)} dari {ribuan(struktur.panjang)}\n"
        if isinstance(struktur, LinkList):
            sebelum = struktur.jumlah_telusur
            p = struktur.get(nomor - 1)
            teks += "Simpul yang dilewati: " + ribuan(struktur.jumlah_telusur - sebelum) + "\n"
        else:
            p = struktur.get(nomor - 1)
            teks += "Langsung ke alamat, tidak ada yang dilewati.\n"
        return teks + "\n" + self.detail(p), modul

    def pesanan_baru(self, nama, jenis):
        if nama == "":
            raise ValueError("Nama pelanggan tidak boleh kosong")
        oid = "O-" + str(self.nomor_baru).zfill(6)
        self.nomor_baru += 1
        if jenis == "vip":
            prio = 1
        elif jenis == "prioritas":
            prio = 2
        else:
            prio = 3
        return Pesanan(oid, nama, "kafe-teknik", "roti-bakar", 12000, prio, 8 * 3600, None, "ANTRE")

    def tambah(self, struktur, jenis, modul):
        p = self.pesanan_baru(self.entri[0].get().strip(), jenis)
        geser = struktur.jumlah_geser if isinstance(struktur, Array) else 0
        salin = struktur.jumlah_salin if isinstance(struktur, Array) else 0
        telusur = struktur.jumlah_telusur if isinstance(struktur, LinkList) else 0
        if jenis == "reguler":
            struktur.tambah_reguler(p)
            posisi = struktur.panjang
        elif jenis == "prioritas":
            struktur.tambah_prioritas(p)
            posisi = (struktur.panjang - 1) // 2 + 1
        else:
            struktur.tambah_vip(p)
            posisi = 1
        teks = f"{p.oid} ({jenis.upper()}) masuk di urutan ke-{ribuan(posisi)} dari {ribuan(struktur.panjang)}.\n"
        if isinstance(struktur, Array):
            teks += "Elemen digeser : " + ribuan(struktur.jumlah_geser - geser) + "\n"
            teks += "Elemen disalin : " + ribuan(struktur.jumlah_salin - salin) + "\n"
            teks += "Kapasitas array: " + ribuan(struktur.kapasitas)
        else:
            teks += "Simpul ditelusuri: " + ribuan(struktur.jumlah_telusur - telusur)
        return teks + "\n\n" + self.detail(p), modul

    def hapus(self, struktur, modul):
        nomor = self.angka(0, "Nomor pesanan")
        if nomor < 1 or nomor > struktur.panjang:
            raise ValueError("Nomor harus 1 sampai " + ribuan(struktur.panjang))
        geser = struktur.jumlah_geser if isinstance(struktur, Array) else 0
        telusur = struktur.jumlah_telusur if isinstance(struktur, LinkList) else 0
        p = struktur.hapus(nomor - 1)
        teks = f"Pesanan {p.oid} (urutan ke-{ribuan(nomor)}) dihapus. Sisa: {ribuan(struktur.panjang)}\n"
        if isinstance(struktur, Array):
            teks += "Elemen digeser : " + ribuan(struktur.jumlah_geser - geser)
        else:
            teks += "Simpul ditelusuri: " + ribuan(struktur.jumlah_telusur - telusur)
        return teks, modul

    def postfix(self):
        ekspresi = self.entri[0].get().strip()
        postfix_teks, total, langkah = proses_struk(ekspresi)
        teks = f"Struk  : {ekspresi}\nPostfix: {postfix_teks}\nTOTAL  : {rupiah(total)}\n\n"
        teks += f"{'langkah':<9}{'token':<8}{'tindakan':<46}{'stack':<26}output\n"
        teks += "-" * 110 + "\n"
        for i in range(langkah.panjang):
            l = langkah.get(i)
            teks += f"{l[0]:<9}{l[1]:<8}{l[2]:<46}{l[3]:<26}{l[4]}\n"
        return teks, "M2 - stack"

    def ringkas(self):
        q = self.pengelola
        return (f"Panjang antrean: naif {ribuan(q.naif.panjang())}, circular {ribuan(q.melingkar.panjang())}.\n"
                f"Tumpukan undo {q.undo.ukuran()}, redo {q.redo.ukuran()}.")

    def undo(self):
        if self.pengelola is None:
            raise ValueError("Data belum dimuat. Klik menu Load dulu.")
        pesan = self.pengelola.undo_last()
        if pesan is None:
            return "Tumpukan undo kosong.", "M2 - stack"
        return "Pembatalan: " + pesan + "\n" + self.ringkas(), "M2 - stack"

    def redo(self):
        pesan = self.pengelola.redo_last()
        if pesan is None:
            return "Tumpukan redo kosong.", "M2 - stack"
        return "Pengulangan: " + pesan + "\n" + self.ringkas(), "M2 - stack"

    def enqueue(self):
        p = self.pesanan_baru(self.entri[0].get().strip(), "reguler")
        self.pengelola.enqueue(p)
        return f"{p.oid} masuk ke belakang KEDUA antrean.\n" + self.ringkas() + "\n\n" + self.detail(p), "M2 - queue"

    def tabel(self, keluar):
        teks = f"{'#':>4}  {'oid':<10}{'pelanggan':<30}{'resto':<16}masuk\n"
        for i in range(min(keluar.panjang, 15)):
            p = keluar.get(i)
            teks += f"{i + 1:>4}  {p.oid:<10}{p.pelanggan:<30}{p.resto:<16}{format_waktu(p.t_masuk)}\n"
        if keluar.panjang > 15:
            teks += f"... dan {ribuan(keluar.panjang - 15)} pesanan lainnya\n"
        return teks

    def dequeue_naif(self):
        n = self.angka(0, "Jumlah dequeue")
        if n < 1:
            raise ValueError("Jumlah dequeue minimal 1")
        keluar, geser = self.pengelola.dequeue_naif(n)
        teks = f"{keluar.panjang} pesanan keluar dari antrean naif.\n"
        teks += f"Total {ribuan(geser)} elemen digeser"
        if keluar.panjang > 0:
            teks += f", rata-rata {ribuan(geser // keluar.panjang)} per pesanan"
        teks += f".\nSisa antrean naif: {ribuan(self.pengelola.naif.panjang())}\n\n"
        return teks + self.tabel(keluar), "M2 - queue naif"

    def dequeue_circular(self):
        n = self.angka(0, "Jumlah dequeue")
        if n < 1:
            raise ValueError("Jumlah dequeue minimal 1")
        keluar, geser = self.pengelola.dequeue_melingkar(n)
        q = self.pengelola.melingkar
        teks = f"{keluar.panjang} pesanan keluar dari antrean circular.\n"
        teks += f"Tidak ada yang digeser. front {ribuan(q.front)}, rear {ribuan(q.rear)}, kapasitas {ribuan(q.kapasitas)}.\n"
        teks += f"Sisa antrean circular: {ribuan(q.panjang())}\n\n"
        return teks + self.tabel(keluar), "M2 - queue circular"

    def urutkan(self, jenis):
        n = self.angka(0, "Jumlah baris")
        kunci = self.entri[1].get()
        modul = "M3 - " + jenis + " sort"
        if n < 1 or n > self.data.panjang:
            raise ValueError("Jumlah baris harus 1 sampai " + ribuan(self.data.panjang))
        if jenis == "insertion" and n > BATAS_INSERTION:
            return "DITOLAK: batasnya 20.000 baris, pakai merge sort untuk data penuh", modul
        data = ambil_awal(self.data, n)  # salinan, data asli aman
        hitung = Pencacah()
        if jenis == "insertion":
            hasil = insertion_sort(data, kunci, hitung)
        else:
            hasil = merge_sort(data, kunci, hitung)
        teks = f"{ribuan(n)} pesanan terurut | {ribuan(hitung.perbandingan)} perbandingan"
        teks += f" | {ribuan(hitung.pemindahan)} pemindahan\n\n"
        teks += f"{'#':>4}  {'oid':<10}{'pelanggan':<30}{'harga':>8}  {'selesai':<10}\n"
        for i in range(min(hasil.panjang, 10)):
            p = hasil.get(i)
            teks += f"{i + 1:>4}  {p.oid:<10}{p.pelanggan:<30}{ribuan(p.harga):>8}  {format_waktu(p.t_selesai):<10}\n"
        if hasil.panjang > 10:
            teks += f"... dan {ribuan(hasil.panjang - 10)} baris lainnya\n"
        return teks, modul

    def cari(self, jenis):
        target = self.entri[0].get().strip()
        if target == "":
            raise ValueError("oid tidak boleh kosong")
        hitung = Pencacah()
        teks = ""
        if jenis == "linear":
            modul = "M3 - linear"
            daftar = self.data
            i = linear_search(daftar, target, hitung)
        else:
            modul = "M3 - binary"
            if self.urut_oid is None:
                mulai = time.perf_counter()
                bangun = Pencacah()
                self.urut_oid = merge_sort(self.data, "oid", bangun)
                ms = (time.perf_counter() - mulai) * 1000
                teks += f"Daftar terurut oid dibangun sekali (merge sort): {self.waktu_teks(ms)}\n"
            else:
                teks += "Memakai daftar terurut oid yang sudah dibangun.\n"
            daftar = self.urut_oid
            i = binary_search(daftar, target, hitung)
        if i == -1:
            teks += f"{target} tidak ditemukan | {ribuan(hitung.perbandingan)} perbandingan"
        else:
            teks += f"ditemukan di indeks {ribuan(i)} | {ribuan(hitung.perbandingan)} perbandingan\n\n"
            teks += self.detail(daftar.get(i))
        return teks, modul


def jalankan():
    root = tk.Tk()
    Aplikasi(root)
    root.mainloop()
