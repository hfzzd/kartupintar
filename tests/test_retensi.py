"""Unit test statistik retensi KartuPintar (retensi.py)."""

import unittest

from kartupintar import model
from kartupintar import retensi

HARI_INI = "2026-11-17"


def _data_dengan_riwayat(entri):
    """Data kosong dengan riwayat berisi (tanggal, deck, kartu_id, nilai)."""
    data = model.data_kosong()
    for tanggal, deck, kartu_id, nilai in entri:
        retensi.catat_review(data, deck, kartu_id, nilai, tanggal)
    return data


class TestCatatReview(unittest.TestCase):
    def test_entri_benar(self):
        data = model.data_kosong()
        entri = retensi.catat_review(data, "JST", 1, 5, HARI_INI)
        self.assertEqual(entri, {
            "tanggal": HARI_INI, "deck": "JST", "kartu_id": 1, "nilai": 5,
        })
        self.assertEqual(data["riwayat"], [entri])

    def test_kualitas_di_luar_0_sampai_5_ditolak(self):
        data = model.data_kosong()
        with self.assertRaises(ValueError):
            retensi.catat_review(data, "JST", 1, 6, HARI_INI)
        with self.assertRaises(ValueError):
            retensi.catat_review(data, "JST", 1, -1, HARI_INI)
        self.assertEqual(data["riwayat"], [])


class TestStatistikRetensi(unittest.TestCase):
    def test_total_benar_dan_persen_cocok_hitungan_tangan(self):
        # 5 review: nilai 5, 4, 2, 3, 1 -> benar (nilai >= 3) = 3 -> 60,0%.
        data = _data_dengan_riwayat([
            (HARI_INI, "JST", 1, 5),
            (HARI_INI, "JST", 2, 4),
            (HARI_INI, "JST", 1, 2),
            (HARI_INI, "JST", 2, 3),
            (HARI_INI, "JST", 1, 1),
        ])
        stat = retensi.statistik_retensi(data, hari=30, tanggal=HARI_INI)
        self.assertEqual(stat["total"], 5)
        self.assertEqual(stat["benar"], 3)
        self.assertEqual(stat["retensi_persen"], 60.0)
        self.assertEqual(stat["per_hari"], {
            HARI_INI: {"total": 5, "benar": 3},
        })
        self.assertEqual(stat["streak"], 1)

    def test_jendela_hari_memotong_entri_lama(self):
        data = _data_dengan_riwayat([
            ("2026-11-07", "JST", 1, 5),  # 10 hari lalu: di luar jendela 7 hari.
            ("2026-11-16", "JST", 1, 5),  # Kemarin: masih di dalam jendela.
            (HARI_INI, "JST", 2, 2),      # Hari ini.
        ])
        stat = retensi.statistik_retensi(data, hari=7, tanggal=HARI_INI)
        self.assertEqual(stat["total"], 2)
        self.assertEqual(stat["benar"], 1)
        self.assertEqual(stat["retensi_persen"], 50.0)
        self.assertNotIn("2026-11-07", stat["per_hari"])

    def test_filter_deck(self):
        data = _data_dengan_riwayat([
            (HARI_INI, "JST", 1, 5),
            (HARI_INI, "JST", 2, 2),
            (HARI_INI, "Kewirausahaan", 1, 5),
        ])
        stat = retensi.statistik_retensi(data, "JST", hari=30, tanggal=HARI_INI)
        self.assertEqual(stat["total"], 2)
        self.assertEqual(stat["benar"], 1)
        self.assertEqual(stat["retensi_persen"], 50.0)
        stat_semua = retensi.statistik_retensi(data, hari=30, tanggal=HARI_INI)
        self.assertEqual(stat_semua["total"], 3)
        self.assertEqual(stat_semua["benar"], 2)

    def test_tanpa_riwayat_semua_nol(self):
        stat = retensi.statistik_retensi(model.data_kosong(), hari=30, tanggal=HARI_INI)
        self.assertEqual(stat["total"], 0)
        self.assertEqual(stat["benar"], 0)
        self.assertEqual(stat["retensi_persen"], 0.0)
        self.assertEqual(stat["per_hari"], {})
        self.assertEqual(stat["streak"], 0)

    def test_hari_kurang_dari_1_ditolak(self):
        data = model.data_kosong()
        with self.assertRaises(ValueError):
            retensi.statistik_retensi(data, hari=0, tanggal=HARI_INI)
        with self.assertRaises(ValueError):
            retensi.statistik_retensi(data, hari=-3, tanggal=HARI_INI)


class TestHitungStreak(unittest.TestCase):
    def test_tiga_hari_berturut_turut(self):
        data = _data_dengan_riwayat([
            ("2026-11-15", "JST", 1, 5),
            ("2026-11-16", "JST", 1, 4),
            (HARI_INI, "JST", 1, 5),
        ])
        self.assertEqual(retensi.hitung_streak(data, tanggal=HARI_INI), 3)

    def test_hari_ini_kosong_dihitung_sampai_kemarin(self):
        data = _data_dengan_riwayat([
            ("2026-11-15", "JST", 1, 5),
            ("2026-11-16", "JST", 1, 4),
        ])
        self.assertEqual(retensi.hitung_streak(data, tanggal=HARI_INI), 2)

    def test_putus_bila_ada_hari_kosong(self):
        # Review hari ini dan 2 hari lalu, tapi kemarin kosong -> streak 1.
        data = _data_dengan_riwayat([
            ("2026-11-15", "JST", 1, 5),
            (HARI_INI, "JST", 1, 5),
        ])
        self.assertEqual(retensi.hitung_streak(data, tanggal=HARI_INI), 1)

    def test_tanpa_riwayat_streak_nol(self):
        self.assertEqual(retensi.hitung_streak(model.data_kosong(), tanggal=HARI_INI), 0)

    def test_streak_filter_deck(self):
        data = _data_dengan_riwayat([
            ("2026-11-16", "JST", 1, 5),
            (HARI_INI, "JST", 1, 5),
            ("2026-11-15", "Kewirausahaan", 1, 5),
            ("2026-11-16", "Kewirausahaan", 1, 5),
            (HARI_INI, "Kewirausahaan", 1, 5),
        ])
        self.assertEqual(retensi.hitung_streak(data, "JST", HARI_INI), 2)
        self.assertEqual(retensi.hitung_streak(data, "Kewirausahaan", HARI_INI), 3)


if __name__ == "__main__":
    unittest.main()
