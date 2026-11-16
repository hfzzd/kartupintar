"""Model data KartuPintar: deck dan kartu, disimpan sebagai JSON lokal.

Struktur data:
    {
      "deck": [
        {
          "nama": "JST",
          "deskripsi": "Istilah jaringan syaraf tiruan",
          "dibuat": "2026-11-16",
          "kartu": [
            {
              "id": 1,
              "depan": "Apa itu perceptron?",
              "belakang": "Model neuron tiruan paling sederhana.",
              "ease": 2.5,
              "interval": 0,
              "repetisi": 0,
              "jatuh_tempo": "2026-11-16",
              "dibuat": "2026-11-16",
            }
          ],
        }
      ]
    }

Kartu baru langsung jatuh tempo di hari dibuat, supaya bisa direview hari itu juga.
"""

import json
import os
from datetime import date

NAMA_BERKAS_BAWAAN = "kartupintar.json"


def hari_ini():
    """Tanggal hari ini sebagai string YYYY-MM-DD."""
    return date.today().isoformat()


def data_kosong():
    return {"deck": []}


def muat_data(path):
    """Muat data dari berkas JSON; berkas belum ada berarti data kosong."""
    if not os.path.exists(path):
        return data_kosong()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "deck" not in data:
        raise ValueError(f"Berkas {path} bukan data KartuPintar yang valid.")
    return data


def simpan_data(path, data):
    """Simpan data ke berkas JSON (tulis atomik via berkas sementara)."""
    sementara = path + ".tmp"
    with open(sementara, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(sementara, path)


def cari_deck(data, nama):
    """Kembalikan dict deck bernama `nama`, atau None bila tidak ada."""
    for deck in data["deck"]:
        if deck["nama"] == nama:
            return deck
    return None


def tambah_deck(data, nama, deskripsi="", tanggal=None):
    """Buat deck baru. Nama deck tidak boleh kosong atau duplikat."""
    nama = nama.strip()
    if not nama:
        raise ValueError("Nama deck tidak boleh kosong.")
    if cari_deck(data, nama) is not None:
        raise ValueError(f'Deck "{nama}" sudah ada.')
    deck = {
        "nama": nama,
        "deskripsi": deskripsi.strip(),
        "dibuat": tanggal or hari_ini(),
        "kartu": [],
    }
    data["deck"].append(deck)
    return deck


def _id_kartu_berikutnya(deck):
    return max((k["id"] for k in deck["kartu"]), default=0) + 1


def tambah_kartu(data, nama_deck, depan, belakang, tanggal=None):
    """Tambah kartu ke deck. Kartu baru jatuh tempo hari ini (siap direview)."""
    deck = cari_deck(data, nama_deck)
    if deck is None:
        raise ValueError(f'Deck "{nama_deck}" tidak ditemukan.')
    depan = depan.strip()
    belakang = belakang.strip()
    if not depan or not belakang:
        raise ValueError("Sisi depan dan belakang kartu tidak boleh kosong.")
    tanggal = tanggal or hari_ini()
    kartu = {
        "id": _id_kartu_berikutnya(deck),
        "depan": depan,
        "belakang": belakang,
        "ease": 2.5,
        "interval": 0,
        "repetisi": 0,
        "jatuh_tempo": tanggal,
        "dibuat": tanggal,
    }
    deck["kartu"].append(kartu)
    return kartu


def cari_kartu(deck, kartu_id):
    for kartu in deck["kartu"]:
        if kartu["id"] == kartu_id:
            return kartu
    return None


def hapus_kartu(data, nama_deck, kartu_id):
    """Hapus kartu dari deck berdasarkan nomor id. Kembalikan kartu yang dihapus."""
    deck = cari_deck(data, nama_deck)
    if deck is None:
        raise ValueError(f'Deck "{nama_deck}" tidak ditemukan.')
    kartu = cari_kartu(deck, kartu_id)
    if kartu is None:
        raise ValueError(f"Kartu nomor {kartu_id} tidak ada di deck \"{nama_deck}\".")
    deck["kartu"].remove(kartu)
    return kartu


def daftar_kartu(data, nama_deck):
    """Kembalikan daftar kartu dalam deck (urut nomor id)."""
    deck = cari_deck(data, nama_deck)
    if deck is None:
        raise ValueError(f'Deck "{nama_deck}" tidak ditemukan.')
    return sorted(deck["kartu"], key=lambda k: k["id"])


def statistik_deck(deck, tanggal=None):
    """Ringkasan deck: total, jatuh tempo, sudah direview, rata-rata ease, distribusi interval."""
    tanggal = tanggal or hari_ini()
    kartu_list = deck["kartu"]
    total = len(kartu_list)
    jatuh = sum(1 for k in kartu_list if k["jatuh_tempo"] <= tanggal)
    direview = sum(1 for k in kartu_list if k["repetisi"] > 0)
    rata_ease = round(sum(k["ease"] for k in kartu_list) / total, 2) if total else 0.0
    distribusi = {}
    for k in kartu_list:
        distribusi[k["interval"]] = distribusi.get(k["interval"], 0) + 1
    return {
        "total": total,
        "jatuh_tempo": jatuh,
        "sudah_direview": direview,
        "rata_rata_ease": rata_ease,
        "distribusi_interval": dict(sorted(distribusi.items())),
    }
