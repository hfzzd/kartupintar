"""Antarmuka baris perintah KartuPintar.

Contoh:
    python3 -m kartupintar.cli deck buat --nama JST
    python3 -m kartupintar.cli deck daftar
    python3 -m kartupintar.cli kartu tambah --deck JST --depan "Apa itu perceptron?" --belakang "..."
    python3 -m kartupintar.cli kartu daftar --deck JST
    python3 -m kartupintar.cli kartu hapus --deck JST --nomor 1
    python3 -m kartupintar.cli review --deck JST
    python3 -m kartupintar.cli jatuh-tempo
    python3 -m kartupintar.cli statistik --deck JST
    python3 -m kartupintar.cli ekspor --deck JST --keluar jst.csv
    python3 -m kartupintar.cli impor --deck JST --berkas jst.csv
"""

import argparse
import sys

from . import __version__
from . import export
from . import model
from . import sm2


def _parser():
    p = argparse.ArgumentParser(
        prog="kartupintar",
        description="Flashcard CLI berbahasa Indonesia dengan spaced repetition (SM-2).",
    )
    p.add_argument("--data", default=model.NAMA_BERKAS_BAWAAN,
                   help="Berkas data JSON (bawaan: kartupintar.json).")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="perintah", required=True)

    p_deck = sub.add_parser("deck", help="Kelola deck.")
    sub_deck = p_deck.add_subparsers(dest="aksi_deck", required=True)
    b = sub_deck.add_parser("buat", help="Buat deck baru.")
    b.add_argument("--nama", required=True, help="Nama deck.")
    b.add_argument("--deskripsi", default="", help="Deskripsi deck (opsional).")
    sub_deck.add_parser("daftar", help="Tampilkan semua deck.")

    p_kartu = sub.add_parser("kartu", help="Kelola kartu dalam deck.")
    sub_kartu = p_kartu.add_subparsers(dest="aksi_kartu", required=True)
    t = sub_kartu.add_parser("tambah", help="Tambah kartu ke deck.")
    t.add_argument("--deck", required=True, help="Nama deck.")
    t.add_argument("--depan", required=True, help="Sisi depan kartu (pertanyaan).")
    t.add_argument("--belakang", required=True, help="Sisi belakang kartu (jawaban).")
    d = sub_kartu.add_parser("daftar", help="Tampilkan kartu dalam deck.")
    d.add_argument("--deck", required=True, help="Nama deck.")
    h = sub_kartu.add_parser("hapus", help="Hapus kartu dari deck.")
    h.add_argument("--deck", required=True, help="Nama deck.")
    h.add_argument("--nomor", required=True, help="Nomor kartu yang dihapus.")

    r = sub.add_parser("review", help="Sesi review interaktif kartu yang jatuh tempo.")
    r.add_argument("--deck", required=True, help="Nama deck yang direview.")

    sub.add_parser("jatuh-tempo", help="Tampilkan semua kartu yang jatuh tempo (semua deck).")
    s = sub.add_parser("statistik", help="Tampilkan statistik sebuah deck.")
    s.add_argument("--deck", required=True, help="Nama deck.")

    e = sub.add_parser("ekspor", help="Ekspor deck ke berkas CSV.")
    e.add_argument("--deck", required=True, help="Nama deck.")
    e.add_argument("--keluar", default=None, help="Berkas CSV tujuan (bawaan: <nama-deck>.csv).")
    i = sub.add_parser("impor", help="Impor kartu dari berkas CSV ke deck.")
    i.add_argument("--deck", required=True, help="Nama deck tujuan (dibuat bila belum ada).")
    i.add_argument("--berkas", required=True, help="Berkas CSV sumber.")
    return p


def _tampil_deck(data):
    if not data["deck"]:
        print("Belum ada deck. Buat dulu dengan: kartupintar deck buat --nama <nama>")
        return
    print(f"{'Nama':<20} {'Kartu':>5}  Deskripsi")
    print("-" * 60)
    for deck in data["deck"]:
        print(f"{deck['nama']:<20} {len(deck['kartu']):>5}  {deck['deskripsi']}")


def _tampil_kartu(data, nama_deck):
    kartu_list = model.daftar_kartu(data, nama_deck)
    if not kartu_list:
        print(f'Deck "{nama_deck}" belum punya kartu.')
        return
    for k in kartu_list:
        print(f"[{k['id']}] {k['depan']}")
        print(f"      -> {k['belakang']}")
        print(f"      jatuh tempo {k['jatuh_tempo']} (interval {k['interval']} hari, ease {k['ease']})")


def _minta_nilai():
    """Minta nilai kualitas 0-5 dari pengguna; kembalikan None bila sesi dibatalkan."""
    while True:
        try:
            jawaban = input("Nilai (0-5, q untuk berhenti): ").strip().lower()
        except EOFError:
            print()
            return None
        if jawaban == "q":
            return None
        try:
            nilai = int(jawaban)
        except ValueError:
            print("Masukkan angka 0-5.")
            continue
        if 0 <= nilai <= 5:
            return nilai
        print("Nilai harus 0-5.")


def _sesi_review(data, nama_deck, path_data):
    """Jalankan sesi review interaktif: kartu jatuh tempo satu per satu."""
    deck = model.cari_deck(data, nama_deck)
    if deck is None:
        raise ValueError(f'Deck "{nama_deck}" tidak ditemukan.')
    jatuh = sm2.kartu_jatuh_tempo(deck)
    if not jatuh:
        print(f'Tidak ada kartu jatuh tempo di deck "{nama_deck}".')
        return
    print(f'Review deck "{nama_deck}": {len(jatuh)} kartu jatuh tempo.')
    direview = 0
    for kartu in jatuh:
        print(f"\n[{kartu['id']}] {kartu['depan']}")
        try:
            input("Tekan Enter untuk melihat jawaban...")
        except EOFError:
            print("\nSesi review dihentikan.")
            break
        print(f"  Jawaban: {kartu['belakang']}")
        nilai = _minta_nilai()
        if nilai is None:
            print("Sesi review dihentikan.")
            break
        sm2.review_kartu(kartu, nilai)
        model.simpan_data(path_data, data)
        direview += 1
        print(f"  -> interval {kartu['interval']} hari, jatuh tempo {kartu['jatuh_tempo']}, ease {kartu['ease']}")
    print(f"\nSesi review selesai: {direview} kartu direview.")


def _tampil_jatuh_tempo(data):
    """Tampilkan semua kartu jatuh tempo (semua deck), urut tanggal jatuh tempo."""
    semua = []
    for deck in data["deck"]:
        for kartu in sm2.kartu_jatuh_tempo(deck):
            semua.append((deck["nama"], kartu))
    semua.sort(key=lambda item: (item[1]["jatuh_tempo"], item[0], item[1]["id"]))
    if not semua:
        print("Tidak ada kartu jatuh tempo. Semua kartu sudah direview!")
        return
    print(f"{len(semua)} kartu jatuh tempo:")
    for nama_deck, k in semua:
        print(f"[{k['id']}] {nama_deck} — {k['depan']} (jatuh tempo {k['jatuh_tempo']})")


def _tampil_statistik(data, nama_deck):
    deck = model.cari_deck(data, nama_deck)
    if deck is None:
        raise ValueError(f'Deck "{nama_deck}" tidak ditemukan.')
    stat = model.statistik_deck(deck)
    print(f'Statistik deck "{nama_deck}":')
    print(f"  Total kartu        : {stat['total']}")
    print(f"  Jatuh tempo        : {stat['jatuh_tempo']}")
    print(f"  Sudah direview     : {stat['sudah_direview']}")
    print(f"  Rata-rata ease     : {stat['rata_rata_ease']}")
    print("  Distribusi interval:")
    if not stat["distribusi_interval"]:
        print("    (belum ada kartu)")
    for interval, jumlah in stat["distribusi_interval"].items():
        print(f"    {interval} hari: {jumlah} kartu")


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        data = model.muat_data(args.data)
        if args.perintah == "deck" and args.aksi_deck == "buat":
            deck = model.tambah_deck(data, args.nama, args.deskripsi)
            model.simpan_data(args.data, data)
            print(f'Deck "{deck["nama"]}" dibuat.')
        elif args.perintah == "deck" and args.aksi_deck == "daftar":
            _tampil_deck(data)
        elif args.perintah == "kartu" and args.aksi_kartu == "tambah":
            kartu = model.tambah_kartu(data, args.deck, args.depan, args.belakang)
            model.simpan_data(args.data, data)
            print(f"Kartu [{kartu['id']}] ditambahkan ke deck \"{args.deck}\" (jatuh tempo hari ini).")
        elif args.perintah == "kartu" and args.aksi_kartu == "daftar":
            _tampil_kartu(data, args.deck)
        elif args.perintah == "kartu" and args.aksi_kartu == "hapus":
            try:
                nomor = int(args.nomor)
            except ValueError:
                raise ValueError("--nomor harus berupa angka, contoh: --nomor 1.")
            kartu = model.hapus_kartu(data, args.deck, nomor)
            model.simpan_data(args.data, data)
            print(f"Kartu [{kartu['id']}] \"{kartu['depan']}\" dihapus dari deck \"{args.deck}\".")
        elif args.perintah == "review":
            _sesi_review(data, args.deck, args.data)
        elif args.perintah == "jatuh-tempo":
            _tampil_jatuh_tempo(data)
        elif args.perintah == "statistik":
            _tampil_statistik(data, args.deck)
        elif args.perintah == "ekspor":
            deck = model.cari_deck(data, args.deck)
            if deck is None:
                raise ValueError(f'Deck "{args.deck}" tidak ditemukan.')
            keluar = args.keluar or f"{args.deck}.csv"
            jumlah = export.ekspor_csv(deck, keluar)
            print(f"{jumlah} kartu dari deck \"{args.deck}\" diekspor ke {keluar}.")
        elif args.perintah == "impor":
            deck, jumlah, peringatan = export.impor_csv(data, args.deck, args.berkas)
            model.simpan_data(args.data, data)
            for p in peringatan:
                print(f"Peringatan: {p}")
            print(f"{jumlah} kartu diimpor ke deck \"{deck['nama']}\""
                  + (f" ({len(peringatan)} baris dilewati)." if peringatan else "."))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Error: tidak bisa membaca/menulis berkas data: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
