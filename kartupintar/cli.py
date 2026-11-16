"""Antarmuka baris perintah KartuPintar.

Contoh:
    python3 -m kartupintar.cli deck buat --nama JST
    python3 -m kartupintar.cli deck daftar
    python3 -m kartupintar.cli kartu tambah --deck JST --depan "Apa itu perceptron?" --belakang "..."
    python3 -m kartupintar.cli kartu daftar --deck JST
    python3 -m kartupintar.cli kartu hapus --deck JST --nomor 1
"""

import argparse
import sys

from . import __version__
from . import model


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
    h.add_argument("--nomor", required=True, type=int, help="Nomor kartu yang dihapus.")
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
            kartu = model.hapus_kartu(data, args.deck, args.nomor)
            model.simpan_data(args.data, data)
            print(f"Kartu [{kartu['id']}] \"{kartu['depan']}\" dihapus dari deck \"{args.deck}\".")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Error: tidak bisa membaca/menulis berkas data: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
