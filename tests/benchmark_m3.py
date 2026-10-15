# Cara pakai (dari folder utama 2ez4u):
#   python -m tests.benchmark_m3
# Hasilnya tabel siap tempel ke README.md. Grafik disimpan ke docs/grafik_m3.png
# kalau matplotlib terpasang (pip install matplotlib).

import os
import time

from backend.m1_pesanan import muat_pesanan
from backend.m3_laporan import Pencacah, ambil_awal, insertion_sort, merge_sort, linear_search, binary_search

FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(FOLDER, "data", "pesanan.csv")


def ribuan(n):
    return f"{n:,}".replace(",", ".")


def ukur_sort(data, n):
    hasil = []
    for nama in ("insertion", "merge"):
        salinan = ambil_awal(data, n)
        hitung = Pencacah()
        mulai = time.perf_counter()
        if nama == "insertion":
            insertion_sort(salinan, "harga", hitung)
        else:
            merge_sort(salinan, "harga", hitung)
        ms = (time.perf_counter() - mulai) * 1000
        hasil.append((hitung.perbandingan, ms))
    return hasil


data = muat_pesanan(CSV)
print(f"Data: {ribuan(data.panjang)} baris\n")

# ----- tabel 1: insertion sort vs merge sort -----
daftar_n = [500, 1000, 2000, 4000, 8000, 16000]
baris = []
for n in daftar_n:
    ins, mer = ukur_sort(data, n)
    baris.append((n, ins, mer))

print("### Insertion sort vs merge sort (kunci harga)\n")
print("| n | insertion: perbandingan | insertion: waktu | merge: perbandingan | merge: waktu |")
print("|---:|---:|---:|---:|---:|")
for n, ins, mer in baris:
    print(f"| {ribuan(n)} | {ribuan(ins[0])} | {ins[1]:.1f} ms | {ribuan(mer[0])} | {mer[1]:.1f} ms |")

print("\nRasio saat n dilipatduakan (insertion ~ 4x, merge ~ 2x):\n")
print("| n | rasio insertion | rasio merge |")
print("|---:|---:|---:|")
for i in range(1, len(baris)):
    r_ins = baris[i][1][0] / baris[i - 1][1][0]
    r_mer = baris[i][2][0] / baris[i - 1][2][0]
    print(f"| {ribuan(baris[i][0])} | {r_ins:.2f}x | {r_mer:.2f}x |")

# merge sort pada data penuh
penuh = ambil_awal(data, data.panjang)
hitung = Pencacah()
mulai = time.perf_counter()
merge_sort(penuh, "harga", hitung)
ms = (time.perf_counter() - mulai) * 1000
print(f"\nMerge sort data penuh ({ribuan(data.panjang)} baris): {ribuan(hitung.perbandingan)} perbandingan, {ms / 1000:.2f} s")

# ----- tabel 2: linear vs binary search -----
mulai = time.perf_counter()
urut = merge_sort(data, "oid", Pencacah())
bangun = (time.perf_counter() - mulai) * 1000
print(f"\nDaftar terurut oid dibangun sekali dengan merge sort: {bangun:.0f} ms\n")

target = [("awal", data.get(0).oid), ("tengah", data.get(data.panjang // 2).oid),
          ("akhir", data.get(data.panjang - 1).oid), ("tidak ada", "O-999999")]
print("### Linear search vs binary search\n")
print("| target | linear: perbandingan | binary: perbandingan |")
print("|---|---:|---:|")
for nama, oid in target:
    h1 = Pencacah()
    linear_search(data, oid, h1)
    h2 = Pencacah()
    binary_search(urut, oid, h2)
    print(f"| {nama} ({oid}) | {ribuan(h1.perbandingan)} | {ribuan(h2.perbandingan)} |")

# ----- grafik -----
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xs = []
    y_ins = []
    y_mer = []
    for n, ins, mer in baris:
        xs.append(n)
        y_ins.append(ins[0])
        y_mer.append(mer[0])
    plt.figure(figsize=(7, 4))
    plt.plot(xs, y_ins, marker="o", label="insertion sort")
    plt.plot(xs, y_mer, marker="o", label="merge sort")
    plt.xlabel("n (jumlah baris)")
    plt.ylabel("jumlah perbandingan")
    plt.title("Insertion sort vs merge sort")
    plt.legend()
    plt.grid(True)
    os.makedirs(os.path.join(FOLDER, "docs"), exist_ok=True)
    jalur = os.path.join(FOLDER, "docs", "grafik_m3.png")
    plt.savefig(jalur, dpi=120, bbox_inches="tight")
    print(f"\nGrafik disimpan: {jalur}")
except ImportError:
    print("\nGrafik dilewati: matplotlib belum terpasang. Jalankan: pip install matplotlib")
