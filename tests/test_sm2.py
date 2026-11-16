"""Unit test algoritma SM-2 KartuPintar."""

import unittest

from kartupintar import model
from kartupintar import sm2

TANGGAL = "2026-11-16"


def _kartu(ease=2.5, interval=0, repetisi=0, jatuh_tempo=TANGGAL):
    return {
        "id": 1,
        "depan": "Q",
        "belakang": "A",
        "ease": ease,
        "interval": interval,
        "repetisi": repetisi,
        "jatuh_tempo": jatuh_tempo,
        "dibuat": TANGGAL,
    }


class TestHitungEase(unittest.TestCase):
    def test_kualitas_5_naik(self):
        self.assertEqual(sm2.hitung_ease(2.5, 5), 2.6)

    def test_kualitas_4_tetap(self):
        self.assertEqual(sm2.hitung_ease(2.5, 4), 2.5)

    def test_kualitas_3_turun_sedikit(self):
        self.assertEqual(sm2.hitung_ease(2.5, 3), 2.36)

    def test_kualitas_2_turun(self):
        self.assertEqual(sm2.hitung_ease(2.5, 2), 2.18)

    def test_kualitas_0_turun_banyak(self):
        self.assertEqual(sm2.hitung_ease(2.5, 0), 1.7)

    def test_ease_tidak_di_bawah_minimum(self):
        self.assertEqual(sm2.hitung_ease(1.3, 0), 1.3)
        self.assertEqual(sm2.hitung_ease(1.4, 0), 1.3)


class TestReviewKartu(unittest.TestCase):
    def test_jawaban_benar_pertama_interval_1(self):
        kartu = _kartu()
        sm2.review_kartu(kartu, 5, TANGGAL)
        self.assertEqual(kartu["ease"], 2.6)
        self.assertEqual(kartu["repetisi"], 1)
        self.assertEqual(kartu["interval"], 1)
        self.assertEqual(kartu["jatuh_tempo"], "2026-11-17")

    def test_jawaban_benar_kedua_interval_6(self):
        kartu = _kartu()
        sm2.review_kartu(kartu, 5, "2026-11-16")
        sm2.review_kartu(kartu, 5, "2026-11-17")
        self.assertEqual(kartu["ease"], 2.7)
        self.assertEqual(kartu["repetisi"], 2)
        self.assertEqual(kartu["interval"], 6)
        self.assertEqual(kartu["jatuh_tempo"], "2026-11-23")

    def test_jawaban_benar_ketiga_interval_dikali_ease(self):
        kartu = _kartu()
        sm2.review_kartu(kartu, 5, "2026-11-16")
        sm2.review_kartu(kartu, 5, "2026-11-17")
        sm2.review_kartu(kartu, 5, "2026-11-23")
        self.assertEqual(kartu["ease"], 2.8)
        self.assertEqual(kartu["repetisi"], 3)
        self.assertEqual(kartu["interval"], 17)  # round(6 x 2,8)
        self.assertEqual(kartu["jatuh_tempo"], "2026-12-10")

    def test_kualitas_di_bawah_3_reset(self):
        kartu = _kartu(ease=2.7, interval=6, repetisi=2, jatuh_tempo="2026-11-23")
        sm2.review_kartu(kartu, 2, "2026-11-23")
        self.assertEqual(kartu["ease"], 2.38)
        self.assertEqual(kartu["repetisi"], 0)
        self.assertEqual(kartu["interval"], 1)
        self.assertEqual(kartu["jatuh_tempo"], "2026-11-24")

    def test_kualitas_0_ease_tetap_di_atas_minimum(self):
        kartu = _kartu(ease=1.3, interval=6, repetisi=2)
        sm2.review_kartu(kartu, 0, TANGGAL)
        self.assertEqual(kartu["ease"], 1.3)
        self.assertEqual(kartu["repetisi"], 0)

    def test_kualitas_di_luar_0_sampai_5_ditolak(self):
        with self.assertRaises(ValueError):
            sm2.review_kartu(_kartu(), 6, TANGGAL)
        with self.assertRaises(ValueError):
            sm2.review_kartu(_kartu(), -1, TANGGAL)


class TestKartuJatuhTempo(unittest.TestCase):
    def test_urut_tanggal_lalu_id(self):
        data = model.data_kosong()
        model.tambah_deck(data, "JST", "", TANGGAL)
        deck = model.cari_deck(data, "JST")
        for depan, jatuh in [("Q1", "2026-11-16"), ("Q2", "2026-11-14"),
                            ("Q3", "2026-11-15"), ("Q4", "2026-11-20")]:
            kartu = model.tambah_kartu(data, "JST", depan, "A", TANGGAL)
            kartu["jatuh_tempo"] = jatuh
        jatuh = sm2.kartu_jatuh_tempo(deck, TANGGAL)
        self.assertEqual([k["depan"] for k in jatuh], ["Q2", "Q3", "Q1"])

    def test_tidak_ada_kartu_jatuh_tempo(self):
        data = model.data_kosong()
        model.tambah_deck(data, "JST", "", TANGGAL)
        deck = model.cari_deck(data, "JST")
        kartu = model.tambah_kartu(data, "JST", "Q", "A", TANGGAL)
        kartu["jatuh_tempo"] = "2026-11-20"
        self.assertEqual(sm2.kartu_jatuh_tempo(deck, TANGGAL), [])


if __name__ == "__main__":
    unittest.main()
