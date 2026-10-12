from backend.m1_pesanan import Array


class Tumpukan:
    def __init__(self):
        self.isi = Array()

    def push(self, x):
        self.isi.append(x)

    def pop(self):
        if self.isi.panjang == 0:
            raise IndexError("tumpukan kosong")
        return self.isi.hapus(self.isi.panjang - 1)

    def peek(self):
        if self.isi.panjang == 0:
            raise IndexError("tumpukan kosong")
        return self.isi.get(self.isi.panjang - 1)

    def kosong(self):
        return self.isi.panjang == 0

    def ukuran(self):
        return self.isi.panjang


def gabung(array):
    if array.panjang == 0:
        return "kosong"
    teks = ""
    for i in range(array.panjang):
        teks += str(array.get(i)) + " "
    return teks.strip()


def adalah_angka(token):
    return token[0].isdigit() or token[0] == "."


def ke_angka(token):
    if "." in token:
        return float(token)
    return int(token)


def prioritas(op):
    if op == "*" or op == "/":
        return 2
    return 1


def pecah_token(teks):
    token = Array()
    angka = ""
    for c in teks:
        if c.isdigit() or c == ".":
            angka += c  # angka bersambung
        else:
            if angka != "":
                token.append(angka)
                angka = ""
            if c in "+-*/()":
                token.append(c)
            elif c != " ":
                raise ValueError("karakter tidak dikenal: " + c)
    if angka != "":
        token.append(angka)
    return token


def ke_postfix(ekspresi, langkah=None):
    token = pecah_token(ekspresi)
    if token.panjang == 0:
        raise ValueError("ekspresi kosong")
    keluaran = Array()
    ops = Tumpukan()

    for i in range(token.panjang):
        t = token.get(i)

        if adalah_angka(t):
            keluaran.append(t)
            tindakan = "angka, langsung keluar"
        elif t == "(":
            ops.push(t)
            tindakan = "push ("
        elif t == ")":
            ketemu = False
            while not ops.kosong():
                atas = ops.pop()
                if atas == "(":
                    ketemu = True  # ( dibuang
                    break
                keluaran.append(atas)
            if not ketemu:
                raise ValueError("kurung tutup tidak punya pasangan")
            tindakan = "pop sampai (, buang ("
        else:
            keluar = ""
            while not ops.kosong() and ops.peek() != "(" and prioritas(ops.peek()) >= prioritas(t):  # >= sama kuat
                x = ops.pop()
                keluaran.append(x)
                keluar += x + " "
            ops.push(t)
            tindakan = "push " + t
            if keluar != "":
                tindakan = "pop " + keluar + "(sama kuat), push " + t

        if langkah is not None:
            langkah.append((f"1.{i + 1}", t, tindakan, gabung(ops.isi), gabung(keluaran)))

    while not ops.kosong():
        atas = ops.pop()
        if atas == "(":
            raise ValueError("kurung buka tidak ditutup")
        keluaran.append(atas)
    if langkah is not None:
        langkah.append(("1.akhir", "-", "pop sisa stack", gabung(ops.isi), gabung(keluaran)))
    return keluaran


def hitung(postfix, langkah=None):
    stack = Tumpukan()
    for i in range(postfix.panjang):
        t = postfix.get(i)
        if adalah_angka(t):
            stack.push(ke_angka(t))
            tindakan = "push " + t
        else:
            if stack.ukuran() < 2:
                raise ValueError("ekspresi tidak valid")
            b = stack.pop()  # kanan dulu
            a = stack.pop()
            if t == "+":
                hasil = a + b
            elif t == "-":
                hasil = a - b
            elif t == "*":
                hasil = a * b
            else:
                if b == 0:
                    raise ValueError("pembagian dengan nol")
                hasil = a / b
            stack.push(hasil)
            tindakan = f"pop {b} dan {a} -> {a}{t}{b} = {hasil}"
        if langkah is not None:
            langkah.append((f"2.{i + 1}", t, tindakan, gabung(stack.isi), ""))
    if stack.ukuran() != 1:
        raise ValueError("ekspresi tidak valid")
    return stack.pop()


def proses_struk(ekspresi):
    langkah = Array()
    postfix = ke_postfix(ekspresi, langkah)
    total = hitung(postfix, langkah)
    return gabung(postfix), total, langkah


class AntreanNaif:
    def __init__(self):
        self.isi = Array()
        self.total_geser = 0

    def panjang(self):
        return self.isi.panjang

    def kosong(self):
        return self.isi.panjang == 0

    def enqueue(self, x):
        self.isi.append(x)

    def dequeue(self):
        if self.isi.panjang == 0:
            return None
        sebelum = self.isi.jumlah_geser
        x = self.isi.hapus(0)  # geser semua
        self.total_geser += self.isi.jumlah_geser - sebelum
        return x

    def get(self, i):
        return self.isi.get(i)

    def keluarkan_belakang(self):
        if self.isi.panjang == 0:
            return None
        return self.isi.hapus(self.isi.panjang - 1)


class AntreanMelingkar:
    def __init__(self, kapasitas=8):
        self.kapasitas = kapasitas
        self.data = [None] * kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0  # beda kosong dan penuh
        self.total_geser = 0

    def panjang(self):
        return self.count

    def kosong(self):
        return self.count == 0

    def tumbuh(self):
        baru = [None] * (self.kapasitas * 2)
        for i in range(self.count):
            baru[i] = self.data[(self.front + i) % self.kapasitas]
        self.data = baru
        self.kapasitas = self.kapasitas * 2
        self.front = 0
        self.rear = self.count

    def enqueue(self, x):
        if self.count == self.kapasitas:
            self.tumbuh()
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.kapasitas  # berputar
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.kapasitas
        self.count -= 1
        return x

    def get(self, i):
        if i < 0 or i >= self.count:
            raise IndexError("indeks di luar batas")
        return self.data[(self.front + i) % self.kapasitas]

    def tambah_depan(self, x):
        if self.count == self.kapasitas:
            self.tumbuh()
        self.front = (self.front - 1 + self.kapasitas) % self.kapasitas  # front mundur
        self.data[self.front] = x
        self.count += 1

    def keluarkan_belakang(self):
        if self.count == 0:
            return None
        self.rear = (self.rear - 1 + self.kapasitas) % self.kapasitas  # rear mundur
        x = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return x


# catatan undo: (jenis, isi)
# ENQUEUE -> pesanan, DEQUEUE_CIRCULAR -> Array pesanan
# dequeue naif hanya pembanding, tidak masuk undo
class PengelolaAntrean:
    def __init__(self):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar()
        self.undo = Tumpukan()
        self.redo = Tumpukan()

    def muat(self, daftar):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar()
        self.undo = Tumpukan()
        self.redo = Tumpukan()
        for i in range(daftar.panjang):
            p = daftar.get(i)
            if p.status == "ANTRE":
                self.naif.enqueue(p)
                self.melingkar.enqueue(p)

    def enqueue(self, pesanan):
        self.naif.enqueue(pesanan)
        self.melingkar.enqueue(pesanan)
        self.undo.push(("ENQUEUE", pesanan))
        self.redo = Tumpukan()  # aksi baru, redo kosong

    def dequeue_naif(self, n):
        keluar = Array()
        sebelum = self.naif.total_geser
        k = 0
        while k < n and not self.naif.kosong():
            keluar.append(self.naif.dequeue())
            k += 1
        return keluar, self.naif.total_geser - sebelum

    def dequeue_melingkar(self, n):
        keluar = self.ambil_melingkar(n)
        if keluar.panjang > 0:
            self.undo.push(("DEQUEUE_CIRCULAR", keluar))
            self.redo = Tumpukan()
        return keluar, 0

    def ambil_melingkar(self, n):
        keluar = Array()
        k = 0
        while k < n and not self.melingkar.kosong():
            keluar.append(self.melingkar.dequeue())
            k += 1
        return keluar

    def undo_last(self):
        if self.undo.kosong():
            return None
        jenis, isi = self.undo.pop()
        if jenis == "ENQUEUE":
            self.naif.keluarkan_belakang()
            self.melingkar.keluarkan_belakang()
            teks = f"enqueue {isi.oid} dibatalkan"
        else:
            for i in range(isi.panjang - 1, -1, -1):  # dari yang terakhir keluar
                self.melingkar.tambah_depan(isi.get(i))  # balik ke depan
            teks = f"{isi.panjang} pesanan dikembalikan ke DEPAN antrean melingkar"
        self.redo.push((jenis, isi))
        return teks

    def redo_last(self):
        if self.redo.kosong():
            return None
        jenis, isi = self.redo.pop()
        if jenis == "ENQUEUE":
            self.naif.enqueue(isi)
            self.melingkar.enqueue(isi)
            teks = f"enqueue diulang: {isi.oid} masuk lagi"
        else:
            self.ambil_melingkar(isi.panjang)  # aksi aslinya
            teks = f"{isi.panjang} pesanan keluar lagi dari antrean melingkar"
        self.undo.push((jenis, isi))  # redo tidak dikosongkan
        return teks

    def history(self):
        hasil = Array()
        for i in range(self.undo.isi.panjang):
            jenis, isi = self.undo.isi.get(i)
            if jenis == "ENQUEUE":
                hasil.append("ENQUEUE " + isi.oid)
            else:
                hasil.append(f"{jenis} x{isi.panjang}")
        return hasil

    def stats(self):
        return (f"queue_len naif={self.naif.panjang()} melingkar={self.melingkar.panjang()} | "
                f"queue_capacity={self.melingkar.kapasitas} | "
                f"total_geser naif={self.naif.total_geser} melingkar={self.melingkar.total_geser} | "
                f"undo_depth={self.undo.ukuran()} redo_depth={self.redo.ukuran()}")
