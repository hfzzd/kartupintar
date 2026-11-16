"""Ekspor dan impor deck KartuPintar sebagai CSV.

Format CSV (dengan baris judul):
    depan,belakang,ease,interval,repetisi,jatuh_tempo
"""

import csv
from datetime import date

from . import model

KOLOM = ["depan", "belakang", "ease", "interval", "repetisi", "jatuh_tempo"]


def ekspor_csv(deck, path):
    """Tulis semua kartu deck ke berkas CSV. Kembalikan jumlah kartu yang ditulis."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        tulis = csv.DictWriter(f, fieldnames=KOLOM)
        tulis.writeheader()
        for kartu in sorted(deck["kartu"], key=lambda k: k["id"]):
            tulis.writerow({kolom: kartu[kolom] for kolom in KOLOM})
    return len(deck["kartu"])


def _baris_valid(baris):
    """Validasi satu baris CSV. Kembalikan (dict kartu, None) atau (None, pesan galat)."""
    depan = (baris.get("depan") or "").strip()
    belakang = (baris.get("belakang") or "").strip()
    if not depan or not belakang:
        return None, "depan/belakang kosong"
    try:
        ease = float(baris.get("ease"))
        interval = int(baris.get("interval"))
        repetisi = int(baris.get("repetisi"))
    except (TypeError, ValueError):
        return None, "ease/interval/repetisi bukan angka"
    if ease < 1.3 or interval < 0 or repetisi < 0:
        return None, "ease < 1,3 atau interval/repetisi negatif"
    jatuh_tempo = (baris.get("jatuh_tempo") or "").strip()
    try:
        date.fromisoformat(jatuh_tempo)
    except ValueError:
        return None, "jatuh_tempo bukan tanggal YYYY-MM-DD"
    return {
        "depan": depan,
        "belakang": belakang,
        "ease": ease,
        "interval": interval,
        "repetisi": repetisi,
        "jatuh_tempo": jatuh_tempo,
    }, None


def impor_csv(data, nama_deck, path):
    """Impor kartu dari CSV ke deck (deck dibuat otomatis bila belum ada).

    Baris tak valid dilewati dengan peringatan, bukan gagal total.
    Kembalikan (deck, jumlah_diimpor, daftar_peringatan).
    """
    deck = model.cari_deck(data, nama_deck)
    if deck is None:
        deck = model.tambah_deck(data, nama_deck)
    peringatan = []
    diimpor = 0
    with open(path, "r", encoding="utf-8", newline="") as f:
        baca = csv.DictReader(f)
        for nomor, baris in enumerate(baca, start=2):
            kartu, galat = _baris_valid(baris)
            if galat is not None:
                peringatan.append(f"Baris {nomor}: {galat} — dilewati.")
                continue
            baru = model.tambah_kartu(data, nama_deck, kartu["depan"], kartu["belakang"])
            baru.update({k: kartu[k] for k in ("ease", "interval", "repetisi", "jatuh_tempo")})
            diimpor += 1
    return deck, diimpor, peringatan
