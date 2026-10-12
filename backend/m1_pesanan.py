import csv


class Pesanan:
    def __init__(self, oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = harga
        self.prioritas = prioritas  # 1 vip, 2 prioritas, 3 reguler
        self.t_masuk = t_masuk
        self.t_selesai = t_selesai
        self.status = status


def format_waktu(detik):
    if detik is None:
        return "-"
    jam = detik // 3600
    menit = detik % 3600 // 60
    sisa = detik % 60
    return f"{jam:02d}:{menit:02d}:{sisa:02d}"


class Array:
    def __init__(self, kapasitas=4):
        self.kapasitas = kapasitas
        self.data = [None] * kapasitas
        self.panjang = 0
        self.jumlah_geser = 0
        self.jumlah_salin = 0

    def lebarkan(self):
        baru = [None] * (self.kapasitas * 2)  # kapasitas 2x
        for i in range(self.panjang):
            baru[i] = self.data[i]
        self.jumlah_salin += self.panjang
        self.data = baru
        self.kapasitas = self.kapasitas * 2

    def append(self, v):
        if self.panjang == self.kapasitas:
            self.lebarkan()
        self.data[self.panjang] = v
        self.panjang += 1

    def get(self, i):
        if i < 0 or i >= self.panjang:
            raise IndexError("indeks di luar batas")
        return self.data[i]

    def insert(self, i, v):
        if i < 0 or i > self.panjang:
            raise IndexError("indeks di luar batas")
        if self.panjang == self.kapasitas:
            self.lebarkan()
        for j in range(self.panjang, i, -1):  # dari belakang
            self.data[j] = self.data[j - 1]  # geser kanan
            self.jumlah_geser += 1
        self.data[i] = v
        self.panjang += 1

    def hapus(self, i):
        if i < 0 or i >= self.panjang:
            raise IndexError("indeks di luar batas")
        nilai = self.data[i]
        for j in range(i, self.panjang - 1):
            self.data[j] = self.data[j + 1]  # geser kiri
            self.jumlah_geser += 1
        self.data[self.panjang - 1] = None
        self.panjang -= 1
        return nilai

    def tambah_reguler(self, p):
        self.append(p)  # belakang

    def tambah_prioritas(self, p):
        self.insert(self.panjang // 2, p)  # tengah

    def tambah_vip(self, p):
        self.insert(0, p)  # depan

    def stats(self):
        return f"panjang={self.panjang} kapasitas={self.kapasitas} geser={self.jumlah_geser} salin={self.jumlah_salin}"


class Simpul:
    def __init__(self, nilai):
        self.nilai = nilai
        self.berikutnya = None


class LinkList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.panjang = 0
        self.jumlah_telusur = 0

    def append(self, v):
        baru = Simpul(v)
        if self.head is None:
            self.head = baru
        else:
            self.tail.berikutnya = baru
        self.tail = baru  # tail maju
        self.panjang += 1

    def tambah_depan(self, v):
        baru = Simpul(v)
        baru.berikutnya = self.head
        self.head = baru
        if self.tail is None:
            self.tail = baru
        self.panjang += 1

    def cari(self, i):
        now = self.head
        for k in range(i):
            now = now.berikutnya
            self.jumlah_telusur += 1
        return now

    def get(self, i):
        if i < 0 or i >= self.panjang:
            raise IndexError("indeks di luar batas")
        return self.cari(i).nilai

    def insert(self, i, v):
        if i < 0 or i > self.panjang:
            raise IndexError("indeks di luar batas")
        if i == 0:
            self.tambah_depan(v)
        elif i == self.panjang:
            self.append(v)
        else:
            sebelum = self.cari(i - 1)  # simpul sebelum i
            baru = Simpul(v)
            baru.berikutnya = sebelum.berikutnya
            sebelum.berikutnya = baru
            self.panjang += 1

    def hapus(self, i):
        if i < 0 or i >= self.panjang:
            raise IndexError("indeks di luar batas")
        if i == 0:
            nilai = self.head.nilai
            self.head = self.head.berikutnya
            if self.head is None:
                self.tail = None
        else:
            sebelum = self.cari(i - 1)
            target = sebelum.berikutnya
            nilai = target.nilai
            sebelum.berikutnya = target.berikutnya
            if target is self.tail:
                self.tail = sebelum  # tail mundur
        self.panjang -= 1
        return nilai

    def tambah_reguler(self, p):
        self.append(p)

    def tambah_prioritas(self, p):
        self.insert(self.panjang // 2, p)

    def tambah_vip(self, p):
        self.tambah_depan(p)

    def stats(self):
        return f"panjang={self.panjang} telusur={self.jumlah_telusur}"


def muat_pesanan(path):
    hasil = Array()
    with open(path, newline="", encoding="utf-8") as f:
        baca = csv.reader(f)
        next(baca)  # lewati judul
        for baris in baca:
            if len(baris) < 9:
                continue
            t_selesai = None
            if baris[7] != "":
                t_selesai = int(baris[7])
            p = Pesanan(baris[0], baris[1], baris[2], baris[3], int(baris[4]),
                        int(baris[5]), int(baris[6]), t_selesai, baris[8])
            hasil.append(p)
    return hasil
