import random
import unittest

from backend.m1_pesanan import Pesanan, Array
from backend.m3_laporan import (Pencacah, BATAS_INSERTION, nilai_kunci, insertion_sort,
                                merge_sort, linear_search, binary_search)


def buat(daftar_harga):
    A = Array()
    for i in range(len(daftar_harga)):
        oid = "O-" + str(i + 1).zfill(6)
        A.append(Pesanan(oid, "x", "resto", "menu", daftar_harga[i], 3, 0, None, "DONE"))
    return A


def buat_oid(daftar_nomor):
    A = Array()
    for nomor in daftar_nomor:
        oid = "O-" + str(nomor).zfill(6)
        A.append(Pesanan(oid, "x", "resto", "menu", 1000, 3, 0, None, "DONE"))
    return A


def cek_urut_stabil(tes, A, kunci):
    # kunci naik, dan kalau kunci sama oid harus tetap naik (stabil)
    for i in range(A.panjang - 1):
        a = A.get(i)
        b = A.get(i + 1)
        tes.assertLessEqual(nilai_kunci(a, kunci), nilai_kunci(b, kunci))
        if nilai_kunci(a, kunci) == nilai_kunci(b, kunci):
            tes.assertLess(a.oid, b.oid)


def cek_tidak_ada_yang_hilang(tes, A, n):
    ada = [False] * (n + 1)
    for i in range(A.panjang):
        nomor = int(A.get(i).oid[2:])
        tes.assertFalse(ada[nomor])  # tidak dobel
        ada[nomor] = True
    tes.assertEqual(A.panjang, n)


def daftar_oid(A):
    teks = ""
    for i in range(A.panjang):
        teks += A.get(i).oid + " "
    return teks.strip()


class TesSort(unittest.TestCase):

    def jalankan(self, nama, A, kunci):
        h = Pencacah()
        if nama == "insertion":
            insertion_sort(A, kunci, h)
            return A, h
        return merge_sort(A, kunci, h), h

    def uji_semua(self, daftar_harga):
        for nama in ("insertion", "merge"):
            A = buat(daftar_harga)
            hasil, h = self.jalankan(nama, A, "harga")
            cek_urut_stabil(self, hasil, "harga")
            cek_tidak_ada_yang_hilang(self, hasil, len(daftar_harga))

    def test_acak(self):
        random.seed(3)
        data = []
        for i in range(500):
            data.append(random.randint(1, 100))
        self.uji_semua(data)

    def test_sudah_terurut(self):
        self.uji_semua([1, 2, 3, 4, 5, 6, 7])

    def test_terbalik(self):
        self.uji_semua([9, 8, 7, 6, 5, 4, 3, 2, 1])

    def test_banyak_duplikat(self):
        self.uji_semua([5, 5, 5, 1, 1, 5, 1, 5, 5, 1, 3, 3])

    def test_ukuran_ganjil_dan_kecil(self):
        for n in (1, 2, 3, 5, 7, 13):
            data = []
            for i in range(n):
                data.append((i * 7) % 4)
            self.uji_semua(data)

    def test_kosong(self):
        for nama in ("insertion", "merge"):
            hasil, h = self.jalankan(nama, buat([]), "harga")
            self.assertEqual(hasil.panjang, 0)
            self.assertEqual(h.perbandingan, 0)

    def test_dua_sort_hasilnya_identik(self):
        random.seed(11)
        data = []
        for i in range(300):
            data.append(random.randint(1, 20))
        a, _ = self.jalankan("insertion", buat(data), "harga")
        b, _ = self.jalankan("merge", buat(data), "harga")
        self.assertEqual(daftar_oid(a), daftar_oid(b))

    def test_stabil_contoh_harga_sama(self):
        for nama in ("insertion", "merge"):
            hasil, _ = self.jalankan(nama, buat([11000, 12000, 11000, 12000, 11000]), "harga")
            self.assertEqual(daftar_oid(hasil), "O-000001 O-000003 O-000005 O-000002 O-000004")

    def test_insertion_di_tempat_merge_salinan(self):
        A = buat([3, 1, 2])
        hasil, _ = self.jalankan("insertion", A, "harga")
        self.assertIs(hasil, A)
        B = buat([3, 1, 2])
        hasil, _ = self.jalankan("merge", B, "harga")
        self.assertEqual(daftar_oid(B), "O-000001 O-000002 O-000003")  # asli tidak berubah
        self.assertEqual(daftar_oid(hasil), "O-000002 O-000003 O-000001")

    def test_jumlah_perbandingan_insertion(self):
        n = 100
        _, h = self.jalankan("insertion", buat(list(range(n))), "harga")
        self.assertEqual(h.perbandingan, n - 1)  # sudah terurut
        _, h = self.jalankan("insertion", buat(list(range(n, 0, -1))), "harga")
        self.assertEqual(h.perbandingan, n * (n - 1) // 2)  # terbalik

    def test_jumlah_perbandingan_merge(self):
        _, h = self.jalankan("merge", buat([1, 2, 3, 4, 5, 6, 7, 8]), "harga")
        self.assertEqual(h.perbandingan, 12)  # (n/2) * log2(n)
        self.assertEqual(h.pemindahan, 24)  # n * log2(n)

    def test_pola_kuadratik_vs_n_log_n(self):
        random.seed(5)
        hasil = []
        for n in (1000, 2000):
            data = []
            for i in range(n):
                data.append(random.randint(1, 100000))
            _, hi = self.jalankan("insertion", buat(data), "harga")
            _, hm = self.jalankan("merge", buat(data), "harga")
            hasil.append((hi.perbandingan, hm.perbandingan))
        self.assertGreater(hasil[1][0] / hasil[0][0], 3.5)  # insertion kira-kira 4x
        self.assertLess(hasil[1][1] / hasil[0][1], 2.3)  # merge kira-kira 2x

    def test_kunci_selesai_kosong_di_belakang(self):
        A = Array()
        A.append(Pesanan("O-000001", "x", "r", "m", 1, 3, 0, None, "ANTRE"))
        A.append(Pesanan("O-000002", "x", "r", "m", 1, 3, 0, 500, "DONE"))
        A.append(Pesanan("O-000003", "x", "r", "m", 1, 3, 0, 100, "DONE"))
        hasil = merge_sort(A, "selesai", Pencacah())
        self.assertEqual(daftar_oid(hasil), "O-000003 O-000002 O-000001")

    def test_kunci_tidak_dikenal(self):
        with self.assertRaises(ValueError):
            merge_sort(buat([1, 2]), "warna", Pencacah())

    def test_batas_insertion(self):
        self.assertEqual(BATAS_INSERTION, 20000)


class TesSearch(unittest.TestCase):

    def test_linear_ketemu_dan_jumlah_perbandingan(self):
        A = buat_oid([5, 3, 9, 1, 7])
        h = Pencacah()
        self.assertEqual(linear_search(A, "O-000009", h), 2)
        self.assertEqual(h.perbandingan, 3)  # indeks + 1

    def test_linear_tidak_ada(self):
        A = buat_oid([5, 3, 9])
        h = Pencacah()
        self.assertEqual(linear_search(A, "O-000099", h), -1)
        self.assertEqual(h.perbandingan, 3)  # semua disentuh

    def test_linear_kosong(self):
        self.assertEqual(linear_search(buat_oid([]), "O-000001", Pencacah()), -1)

    def terurut(self):
        return buat_oid([2, 4, 6, 8, 10, 12, 14])

    def test_binary_empat_kasus(self):
        A = self.terurut()
        self.assertEqual(binary_search(A, "O-000008", Pencacah()), 3)  # tengah
        self.assertEqual(binary_search(A, "O-000002", Pencacah()), 0)  # paling kiri
        self.assertEqual(binary_search(A, "O-000014", Pencacah()), 6)  # paling kanan
        self.assertEqual(binary_search(A, "O-000007", Pencacah()), -1)  # tidak ada

    def test_binary_di_luar_rentang(self):
        A = self.terurut()
        self.assertEqual(binary_search(A, "O-000001", Pencacah()), -1)
        self.assertEqual(binary_search(A, "O-000099", Pencacah()), -1)

    def test_binary_kosong_dan_satu(self):
        self.assertEqual(binary_search(buat_oid([]), "O-000001", Pencacah()), -1)
        self.assertEqual(binary_search(buat_oid([4]), "O-000004", Pencacah()), 0)
        self.assertEqual(binary_search(buat_oid([4]), "O-000005", Pencacah()), -1)

    def test_binary_semua_elemen_ketemu(self):
        nomor = []
        for i in range(1, 101):
            nomor.append(i * 3)
        A = buat_oid(nomor)
        for i in range(A.panjang):
            self.assertEqual(binary_search(A, A.get(i).oid, Pencacah()), i)

    def test_binary_sedikit_perbandingan(self):
        A = buat_oid(list(range(1, 1001)))
        h = Pencacah()
        binary_search(A, "O-000777", h)
        self.assertLessEqual(h.perbandingan, 10)  # log2(1000) sekitar 10

    def test_binary_dan_linear_menemukan_baris_sama(self):
        random.seed(8)
        acak = []
        for i in range(1, 201):
            acak.append(i)
        for i in range(len(acak) - 1, 0, -1):  # acak urutan
            j = random.randint(0, i)
            acak[i], acak[j] = acak[j], acak[i]
        A = buat_oid(acak)
        urut = merge_sort(A, "oid", Pencacah())
        for target in (1, 50, 200):
            oid = "O-" + str(target).zfill(6)
            baris = binary_search(urut, oid, Pencacah())
            self.assertEqual(urut.get(baris).oid, oid)
            self.assertEqual(A.get(linear_search(A, oid, Pencacah())).oid, oid)


if __name__ == "__main__":
    unittest.main()
