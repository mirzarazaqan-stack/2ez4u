from backend.m1_pesanan import Array

BATAS_INSERTION = 20000


class Pencacah:
    def __init__(self):
        self.perbandingan = 0
        self.pemindahan = 0


def nilai_kunci(p, kunci):
    if kunci == "oid":
        return p.oid
    if kunci == "harga":
        return p.harga
    if kunci == "selesai":
        if p.t_selesai is None:
            return 10 ** 9  # belum selesai, taruh di belakang
        return p.t_selesai
    raise ValueError("kunci tidak dikenal: " + kunci)


def ambil_awal(A, n):
    hasil = Array()
    for i in range(n):
        hasil.append(A.get(i))
    return hasil


def bungkus(A, kunci):
    b = [None] * A.panjang
    for i in range(A.panjang):
        p = A.data[i]
        b[i] = (nilai_kunci(p, kunci), p)  # (kunci, pesanan)
    return b


def buka(b):
    hasil = Array()
    for t in b:
        hasil.append(t[1])
    return hasil


def insertion_sort(A, kunci, hitung):
    b = bungkus(A, kunci)
    for i in range(1, len(b)):
        x = b[i]
        j = i - 1
        while j >= 0:
            hitung.perbandingan += 1
            if b[j][0] > x[0]:  # > supaya stabil
                b[j + 1] = b[j]  # geser kanan
                hitung.pemindahan += 1
                j -= 1
            else:
                break
        b[j + 1] = x
        hitung.pemindahan += 1
    for i in range(len(b)):
        A.data[i] = b[i][1]  # tulis balik, di tempat
    return A


def merge_sort(A, kunci, hitung):
    b = bungkus(A, kunci)
    return buka(urutkan(b, hitung))


def urutkan(b, hitung):
    if len(b) <= 1:
        return b
    tengah = len(b) // 2
    kiri = urutkan(b[:tengah], hitung)
    kanan = urutkan(b[tengah:], hitung)
    return gabung(kiri, kanan, hitung)


def gabung(kiri, kanan, hitung):
    hasil = [None] * (len(kiri) + len(kanan))
    i = 0
    j = 0
    k = 0
    while i < len(kiri) and j < len(kanan):
        hitung.perbandingan += 1
        if kiri[i][0] <= kanan[j][0]:  # <= supaya stabil
            hasil[k] = kiri[i]
            i += 1
        else:
            hasil[k] = kanan[j]
            j += 1
        k += 1
        hitung.pemindahan += 1
    while i < len(kiri):  # sisa kiri
        hasil[k] = kiri[i]
        i += 1
        k += 1
        hitung.pemindahan += 1
    while j < len(kanan):  # sisa kanan
        hasil[k] = kanan[j]
        j += 1
        k += 1
        hitung.pemindahan += 1
    return hasil


def linear_search(A, target, hitung):
    for i in range(A.panjang):
        hitung.perbandingan += 1
        if A.data[i].oid == target:
            return i
    return -1


def binary_search(A, target, hitung):
    lo = 0
    hi = A.panjang - 1
    while lo <= hi:  # <= bukan <
        mid = (lo + hi) // 2
        hitung.perbandingan += 1
        if A.data[mid].oid == target:
            return mid
        if A.data[mid].oid < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
