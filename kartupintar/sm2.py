"""Algoritma SM-2 (spaced repetition) untuk KartuPintar.

Setiap kartu punya ease (awal 2,5, minimum 1,3), interval (hari),
repetisi (jawaban benar berturut-turut), dan jatuh_tempo.

Aturan (berdasarkan SM-2 klasik):
- Saat review, beri nilai kualitas 0-5.
- Ease baru = ease + (0,1 - (5 - q) * (0,08 + (5 - q) * 0,02)), minimum 1,3.
- q < 3: repetisi kembali 0, interval 1 hari (ulang dari awal).
- q >= 3: repetisi + 1; interval 1 hari (repetisi 1), 6 hari (repetisi 2),
  lalu interval sebelumnya x ease (dibulatkan).
- jatuh_tempo = tanggal review + interval hari.
"""

from datetime import date, timedelta

EASE_AWAL = 2.5
EASE_MINIMUM = 1.3


def _tanggal(string_tanggal):
    return date.fromisoformat(string_tanggal)


def hitung_ease(ease, kualitas):
    """Ease baru setelah review dengan kualitas 0-5 (minimum 1,3)."""
    ease_baru = ease + (0.1 - (5 - kualitas) * (0.08 + (5 - kualitas) * 0.02))
    return max(EASE_MINIMUM, round(ease_baru, 2))


def review_kartu(kartu, kualitas, tanggal=None):
    """Terapkan satu review SM-2 ke kartu (diubah di tempat). Kembalikan kartu."""
    if not 0 <= kualitas <= 5:
        raise ValueError("Kualitas harus 0-5.")
    tanggal = tanggal or date.today().isoformat()
    hari = _tanggal(tanggal)
    kartu["ease"] = hitung_ease(kartu["ease"], kualitas)
    if kualitas < 3:
        kartu["repetisi"] = 0
        kartu["interval"] = 1
    else:
        kartu["repetisi"] += 1
        if kartu["repetisi"] == 1:
            kartu["interval"] = 1
        elif kartu["repetisi"] == 2:
            kartu["interval"] = 6
        else:
            kartu["interval"] = max(1, round(kartu["interval"] * kartu["ease"]))
    kartu["jatuh_tempo"] = (hari + timedelta(days=kartu["interval"])).isoformat()
    return kartu


def kartu_jatuh_tempo(deck, tanggal=None):
    """Kartu dalam deck yang jatuh tempo pada/sebelum tanggal (urut tanggal, lalu id)."""
    tanggal = tanggal or date.today().isoformat()
    jatuh = [k for k in deck["kartu"] if k["jatuh_tempo"] <= tanggal]
    return sorted(jatuh, key=lambda k: (k["jatuh_tempo"], k["id"]))
