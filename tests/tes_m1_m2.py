import random
import unittest

from backend.m1_pesanan import Pesanan, Array, LinkList
from backend.m2_antrean import (Tumpukan, AntreanNaif, AntreanMelingkar,
                                PengelolaAntrean, proses_struk, pecah_token)


def buat_pesanan(nomor, status="ANTRE"):
    oid = "O-" + str(nomor).zfill(6)
    return Pesanan(oid, "x", "resto", "menu", 10000, 3, 0, None, status)


def isi_ke_teks(struktur):
    teks = ""
    for i in range(struktur.panjang):
        teks += struktur.get(i).oid + " "
    return teks.strip()


class Bungkus:
    def __init__(self, antrean):
        self.antrean = antrean
        self.panjang = antrean.panjang()

    def get(self, i):
        return self.antrean.get(i)


class TesM1(unittest.TestCase):

    def test_array_melebar_dua_kali_lipat(self):
        a = Array(4)
        for n in range(1, 11):
            a.append(n)
        self.assertEqual(a.panjang, 10)
        self.assertEqual(a.kapasitas, 16)
        self.assertEqual(a.jumlah_salin, 4 + 8)
        self.assertEqual(a.get(9), 10)

    def test_array_append_tidak_kuadratik(self):
        a = Array(4)
        n = 100000
        for i in range(n):
            a.append(i)
        self.assertLess(a.jumlah_salin, 2 * n)

    def test_tiga_jenis_pesanan(self):
        for struktur in (Array(), LinkList()):
            for nomor in (1, 2, 3, 4):
                struktur.tambah_reguler(buat_pesanan(nomor))
            struktur.tambah_prioritas(buat_pesanan(5))
            struktur.tambah_vip(buat_pesanan(6))
            self.assertEqual(isi_ke_teks(struktur),
                             "O-000006 O-000001 O-000002 O-000005 O-000003 O-000004")

    def test_hapus_semua_posisi(self):
        for struktur in (Array(), LinkList()):
            for nomor in range(1, 6):
                struktur.append(buat_pesanan(nomor))
            struktur.hapus(0)
            struktur.hapus(struktur.panjang - 1)
            struktur.hapus(1)
            self.assertEqual(isi_ke_teks(struktur), "O-000002 O-000004")

    def test_tail_benar_setelah_hapus_belakang(self):
        ll = LinkList()
        for nomor in (1, 2, 3):
            ll.append(buat_pesanan(nomor))
        ll.hapus(2)
        ll.append(buat_pesanan(9))
        self.assertEqual(isi_ke_teks(ll), "O-000001 O-000002 O-000009")

    def test_hapus_sampai_kosong_lalu_isi_lagi(self):
        ll = LinkList()
        ll.append(buat_pesanan(1))
        ll.hapus(0)
        self.assertEqual(ll.panjang, 0)
        self.assertIsNone(ll.head)
        self.assertIsNone(ll.tail)
        ll.append(buat_pesanan(2))
        self.assertEqual(isi_ke_teks(ll), "O-000002")

    def test_indeks_di_luar_batas(self):
        for struktur in (Array(), LinkList()):
            struktur.append(buat_pesanan(1))
            with self.assertRaises(IndexError):
                struktur.get(1)
            with self.assertRaises(IndexError):
                struktur.hapus(-1)

    def test_acak_array_dan_linklist_sama(self):
        random.seed(42)
        a, ll = Array(), LinkList()
        nomor = 0
        for _ in range(3000):
            pilihan = random.randint(0, 3)
            if pilihan == 3:
                if a.panjang > 0:
                    i = random.randint(0, a.panjang - 1)
                    a.hapus(i)
                    ll.hapus(i)
                continue
            nomor += 1
            if pilihan == 0:
                a.tambah_reguler(buat_pesanan(nomor))
                ll.tambah_reguler(buat_pesanan(nomor))
            elif pilihan == 1:
                a.tambah_prioritas(buat_pesanan(nomor))
                ll.tambah_prioritas(buat_pesanan(nomor))
            else:
                a.tambah_vip(buat_pesanan(nomor))
                ll.tambah_vip(buat_pesanan(nomor))
        self.assertEqual(a.panjang, ll.panjang)
        self.assertEqual(isi_ke_teks(a), isi_ke_teks(ll))


class TesKasir(unittest.TestCase):

    def total(self, ekspresi):
        return proses_struk(ekspresi)[1]

    def postfix(self, ekspresi):
        return proses_struk(ekspresi)[0]

    def test_contoh_dosen(self):
        teks, total, _ = proses_struk("( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        self.assertEqual(teks, "3 12000 * 2 8500 * + 5000 -")
        self.assertEqual(total, 48000)

    def test_tanpa_kurung(self):
        self.assertEqual(self.postfix("2 + 3 * 4"), "2 3 4 * +")
        self.assertEqual(self.total("2 + 3 * 4"), 14)

    def test_berkurung(self):
        self.assertEqual(self.total("( 2 + 3 ) * 4"), 20)

    def test_minus_beruntun(self):
        self.assertEqual(self.postfix("10 - 4 - 3"), "10 4 - 3 -")
        self.assertEqual(self.total("10 - 4 - 3"), 3)

    def test_kurung_bersarang(self):
        self.assertEqual(self.total("( ( 2 + 3 ) * ( 4 - 1 ) )"), 15)

    def test_urutan_pop(self):
        self.assertEqual(self.total("100 / 5 / 2"), 10)
        self.assertEqual(self.total("20 - 2 * 3 + 8 / 4"), 16)
        self.assertEqual(self.total("8 - 3"), 5)

    def test_tanpa_spasi_dan_angka_banyak_digit(self):
        self.assertEqual(self.total("(3*12000)+(2*8500)-5000"), 48000)
        self.assertEqual(pecah_token("12000+7").get(0), "12000")

    def test_ekspresi_salah(self):
        for buruk in ("", "( 2 + 3", "2 + 3 )", "2 +", "2 $ 3", "5 / 0"):
            with self.assertRaises(ValueError):
                proses_struk(buruk)

    def test_tumpukan_lifo(self):
        s = Tumpukan()
        s.push(1)
        s.push(2)
        self.assertEqual(s.peek(), 2)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 1)
        self.assertTrue(s.kosong())
        with self.assertRaises(IndexError):
            s.pop()


class TesAntrean(unittest.TestCase):

    def test_melingkar_berputar_k4(self):
        q = AntreanMelingkar(4)
        for n in (1, 2, 3):
            q.enqueue(n)
        self.assertEqual(q.dequeue(), 1)
        self.assertEqual(q.dequeue(), 2)
        for n in (4, 5, 6):
            q.enqueue(n)
        self.assertEqual(q.panjang(), 4)
        self.assertEqual(q.kapasitas, 4)
        urutan = []
        while not q.kosong():
            urutan.append(q.dequeue())
        self.assertEqual(urutan, [3, 4, 5, 6])

    def test_melingkar_tumbuh_urutan_tetap(self):
        q = AntreanMelingkar(4)
        for n in (1, 2, 3, 4):
            q.enqueue(n)
        q.dequeue()
        q.dequeue()
        for n in (5, 6, 7):
            q.enqueue(n)
        self.assertEqual(q.kapasitas, 8)
        urutan = []
        while not q.kosong():
            urutan.append(q.dequeue())
        self.assertEqual(urutan, [3, 4, 5, 6, 7])

    def test_dequeue_saat_kosong(self):
        self.assertIsNone(AntreanMelingkar(4).dequeue())
        self.assertIsNone(AntreanNaif().dequeue())

    def test_kosong_vs_penuh(self):
        q = AntreanMelingkar(2)
        q.enqueue("a")
        q.enqueue("b")
        self.assertFalse(q.kosong())
        q.dequeue()
        q.dequeue()
        self.assertTrue(q.kosong())

    def test_naif_dan_melingkar_urutan_sama(self):
        random.seed(7)
        naif, mel = AntreanNaif(), AntreanMelingkar(4)
        for n in range(500):
            if random.randint(0, 2) < 2:
                naif.enqueue(n)
                mel.enqueue(n)
            else:
                self.assertEqual(naif.dequeue(), mel.dequeue())
        self.assertEqual(naif.panjang(), mel.panjang())

    def test_selisih_hanya_di_dequeue(self):
        naif, mel = AntreanNaif(), AntreanMelingkar()
        for n in range(1000):
            naif.enqueue(n)
            mel.enqueue(n)
        self.assertEqual(naif.total_geser, 0)
        naif.dequeue()
        mel.dequeue()
        self.assertEqual(naif.total_geser, 999)
        self.assertEqual(mel.total_geser, 0)


class TesUndoRedo(unittest.TestCase):

    def siapkan(self, jumlah=10):
        data = Array()
        for n in range(1, jumlah + 1):
            data.append(buat_pesanan(n))
        p = PengelolaAntrean()
        p.muat(data)
        return p

    def isi(self, antrean):
        return isi_ke_teks(Bungkus(antrean))

    def test_muat_hanya_status_antre(self):
        data = Array()
        data.append(buat_pesanan(1, "DONE"))
        data.append(buat_pesanan(2, "ANTRE"))
        data.append(buat_pesanan(3, "CANCEL"))
        p = PengelolaAntrean()
        p.muat(data)
        self.assertEqual(p.naif.panjang(), 1)
        self.assertEqual(p.melingkar.panjang(), 1)

    def test_undo_redo_enqueue(self):
        p = self.siapkan(3)
        p.enqueue(buat_pesanan(99))
        self.assertEqual(p.naif.panjang(), 4)
        p.undo_last()
        self.assertEqual(p.naif.panjang(), 3)
        self.assertEqual(p.melingkar.panjang(), 3)
        self.assertEqual((p.undo.ukuran(), p.redo.ukuran()), (0, 1))
        p.redo_last()
        self.assertEqual(self.isi(p.melingkar), "O-000001 O-000002 O-000003 O-000099")
        self.assertEqual((p.undo.ukuran(), p.redo.ukuran()), (1, 0))

    def test_undo_dequeue_kembali_ke_depan(self):
        p = self.siapkan(10)
        awal = self.isi(p.melingkar)
        keluar, geser = p.dequeue_melingkar(4)
        self.assertEqual(keluar.panjang, 4)
        self.assertEqual(geser, 0)
        p.undo_last()
        self.assertEqual(self.isi(p.melingkar), awal)
        p.redo_last()
        self.assertEqual(self.isi(p.melingkar),
                         "O-000005 O-000006 O-000007 O-000008 O-000009 O-000010")

    def test_dequeue_naif_tidak_masuk_undo(self):
        p = self.siapkan(6)
        keluar, geser = p.dequeue_naif(3)
        self.assertEqual(keluar.panjang, 3)
        self.assertEqual(p.naif.panjang(), 3)
        self.assertEqual(p.undo.ukuran(), 0)

    def test_jumlah_geser_naif(self):
        p = self.siapkan(6)
        _, geser = p.dequeue_naif(3)
        self.assertEqual(geser, 5 + 4 + 3)

    def test_naif_tidak_mengganggu_undo_melingkar(self):
        p = self.siapkan(6)
        p.dequeue_melingkar(2)
        p.dequeue_naif(4)
        self.assertEqual(p.undo.ukuran(), 1)
        p.undo_last()
        self.assertEqual(p.melingkar.panjang(), 6)

    def test_aksi_baru_mengosongkan_redo(self):
        p = self.siapkan(5)
        p.dequeue_melingkar(2)
        p.undo_last()
        self.assertEqual(p.redo.ukuran(), 1)
        p.enqueue(buat_pesanan(50))
        self.assertEqual(p.redo.ukuran(), 0)
        self.assertIsNone(p.redo_last())

    def test_undo_redo_saat_kosong(self):
        p = self.siapkan(1)
        self.assertIsNone(p.undo_last())
        self.assertIsNone(p.redo_last())

    def test_history(self):
        p = self.siapkan(5)
        p.enqueue(buat_pesanan(20))
        p.dequeue_melingkar(2)
        h = p.history()
        self.assertEqual((h.get(0), h.get(1)), ("ENQUEUE O-000020", "DEQUEUE_CIRCULAR x2"))
        p.undo_last()
        h = p.history()
        self.assertEqual(h.panjang, 1)
        self.assertEqual(h.get(0), "ENQUEUE O-000020")

    def test_dequeue_lebih_banyak_dari_isi(self):
        p = self.siapkan(3)
        keluar, _ = p.dequeue_melingkar(100)
        self.assertEqual(keluar.panjang, 3)
        p.undo_last()
        self.assertEqual(p.melingkar.panjang(), 3)

    def test_dequeue_antrean_kosong_tidak_masuk_undo(self):
        p = self.siapkan(0)
        keluar, _ = p.dequeue_melingkar(5)
        self.assertEqual(keluar.panjang, 0)
        self.assertEqual(p.undo.ukuran(), 0)


if __name__ == "__main__":
    unittest.main()
