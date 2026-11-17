"""Statistik retensi KartuPintar: seberapa baik kartu diingat dari waktu ke waktu.

Setiap review yang dilakukan lewat perintah `review` dicatat di data["riwayat"]:
    {"tanggal": "2026-11-17", "deck": "JST", "kartu_id": 1, "nilai": 5}

Suatu review dihitung "benar" bila nilai >= 3 (kartu diingat, SM-2 menaikkan
repetisi). Tingkat retensi = benar / total review dalam jendela hari.
Streak = jumlah hari berturut-turut ada review, dihitung mundur dari hari ini
(bila hari ini belum ada review, streak dihitung sampai kemarin).
"""

from datetime import date, timedelta

NILAI_BENAR_MINIMUM = 3
HARI_BAWAAN = 30


def _tanggal(string_tanggal):
    return date.fromisoformat(string_tanggal)


def catat_review(data, nama_deck, kartu_id, kualitas, tanggal=None):
    """Catat satu review ke riwayat. Kembalikan entri yang dicatat."""
    if not 0 <= kualitas <= 5:
        raise ValueError("Kualitas harus 0-5.")
    entri = {
        "tanggal": tanggal or date.today().isoformat(),
        "deck": nama_deck,
        "kartu_id": kartu_id,
        "nilai": kualitas,
    }
    data.setdefault("riwayat", []).append(entri)
    return entri


def _riwayat_dalam_jendela(data, nama_deck, hari, tanggal):
    akhir = _tanggal(tanggal)
    awal = akhir - timedelta(days=hari - 1)
    hasil = []
    for entri in data.get("riwayat", []):
        t = _tanggal(entri["tanggal"])
        if awal <= t <= akhir and (nama_deck is None or entri["deck"] == nama_deck):
            hasil.append(entri)
    return hasil


def hitung_streak(data, nama_deck=None, tanggal=None):
    """Jumlah hari berturut-turut dengan minimal satu review, mundur dari hari ini."""
    tanggal = tanggal or date.today().isoformat()
    hari_ada_review = {
        entri["tanggal"]
        for entri in data.get("riwayat", [])
        if nama_deck is None or entri["deck"] == nama_deck
    }
    hari = _tanggal(tanggal)
    if hari.isoformat() not in hari_ada_review:
        hari -= timedelta(days=1)
    streak = 0
    while hari.isoformat() in hari_ada_review:
        streak += 1
        hari -= timedelta(days=1)
    return streak


def statistik_retensi(data, nama_deck=None, hari=30, tanggal=None):
    """Ringkasan retensi dalam `hari` terakhir: total, benar, tingkat retensi, per hari, streak."""
    if hari < 1:
        raise ValueError("Jumlah hari harus minimal 1.")
    tanggal = tanggal or date.today().isoformat()
    entri = _riwayat_dalam_jendela(data, nama_deck, hari, tanggal)
    total = len(entri)
    benar = sum(1 for e in entri if e["nilai"] >= NILAI_BENAR_MINIMUM)
    retensi = round(benar / total * 100, 1) if total else 0.0
    per_hari = {}
    for e in entri:
        h = per_hari.setdefault(e["tanggal"], {"total": 0, "benar": 0})
        h["total"] += 1
        if e["nilai"] >= NILAI_BENAR_MINIMUM:
            h["benar"] += 1
    return {
        "total": total,
        "benar": benar,
        "retensi_persen": retensi,
        "per_hari": dict(sorted(per_hari.items())),
        "streak": hitung_streak(data, nama_deck, tanggal),
    }
