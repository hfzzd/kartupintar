"""Unit test model deck & kartu KartuPintar."""

import unittest

from kartupintar import model
from kartupintar import sm2

TANGGAL = "2026-11-16"


def _data_dengan_deck(nama="JST"):
    data = model.data_kosong()
    model.tambah_deck(data, nama, "Istilah jaringan syaraf tiruan", TANGGAL)
    return data


class TestDeck(unittest.TestCase):
    def test_tambah_deck(self):
        data = model.data_kosong()
        deck = model.tambah_deck(data, "JST", "Istilah JST", TANGGAL)
        self.assertEqual(deck["nama"], "JST")
        self.assertEqual(deck["deskripsi"], "Istilah JST")
        self.assertEqual(deck["kartu"], [])
        self.assertIs(model.cari_deck(data, "JST"), deck)

    def test_deck_duplikat_ditolak(self):
        data = _data_dengan_deck()
        with self.assertRaises(ValueError):
            model.tambah_deck(data, "JST")

    def test_deck_nama_kosong_ditolak(self):
        data = model.data_kosong()
        with self.assertRaises(ValueError):
            model.tambah_deck(data, "   ")

    def test_cari_deck_tidak_ada(self):
        self.assertIsNone(model.cari_deck(model.data_kosong(), "JST"))


class TestKartu(unittest.TestCase):
    def test_tambah_kartu_baru_jatuh_tempo_hari_ini(self):
        data = _data_dengan_deck()
        kartu = model.tambah_kartu(data, "JST", "Apa itu perceptron?",
                                   "Model neuron tiruan paling sederhana.", TANGGAL)
        self.assertEqual(kartu["id"], 1)
        self.assertEqual(kartu["ease"], 2.5)
        self.assertEqual(kartu["interval"], 0)
        self.assertEqual(kartu["repetisi"], 0)
        self.assertEqual(kartu["jatuh_tempo"], TANGGAL)

    def test_tambah_kartu_id_berurutan(self):
        data = _data_dengan_deck()
        k1 = model.tambah_kartu(data, "JST", "Q1", "A1", TANGGAL)
        k2 = model.tambah_kartu(data, "JST", "Q2", "A2", TANGGAL)
        self.assertEqual((k1["id"], k2["id"]), (1, 2))

    def test_tambah_kartu_deck_hilang_ditolak(self):
        with self.assertRaises(ValueError):
            model.tambah_kartu(model.data_kosong(), "JST", "Q", "A", TANGGAL)

    def test_tambah_kartu_sisi_kosong_ditolak(self):
        data = _data_dengan_deck()
        with self.assertRaises(ValueError):
            model.tambah_kartu(data, "JST", "   ", "A", TANGGAL)
        with self.assertRaises(ValueError):
            model.tambah_kartu(data, "JST", "Q", "", TANGGAL)

    def test_hapus_kartu(self):
        data = _data_dengan_deck()
        model.tambah_kartu(data, "JST", "Q1", "A1", TANGGAL)
        kartu = model.tambah_kartu(data, "JST", "Q2", "A2", TANGGAL)
        dihapus = model.hapus_kartu(data, "JST", kartu["id"])
        self.assertEqual(dihapus["depan"], "Q2")
        self.assertEqual(len(model.cari_deck(data, "JST")["kartu"]), 1)

    def test_hapus_kartu_tidak_ada_ditolak(self):
        data = _data_dengan_deck()
        with self.assertRaises(ValueError):
            model.hapus_kartu(data, "JST", 99)

    def test_daftar_kartu_urut_id(self):
        data = _data_dengan_deck()
        model.tambah_kartu(data, "JST", "Q1", "A1", TANGGAL)
        model.tambah_kartu(data, "JST", "Q2", "A2", TANGGAL)
        model.tambah_kartu(data, "JST", "Q3", "A3", TANGGAL)
        self.assertEqual([k["id"] for k in model.daftar_kartu(data, "JST")], [1, 2, 3])

    def test_daftar_kartu_deck_hilang_ditolak(self):
        with self.assertRaises(ValueError):
            model.daftar_kartu(model.data_kosong(), "JST")


class TestStatistik(unittest.TestCase):
    def test_statistik_deck(self):
        data = _data_dengan_deck()
        model.tambah_kartu(data, "JST", "Q1", "A1", TANGGAL)
        model.tambah_kartu(data, "JST", "Q2", "A2", TANGGAL)
        deck = model.cari_deck(data, "JST")
        sm2.review_kartu(deck["kartu"][0], 5, TANGGAL)
        stat = model.statistik_deck(deck, TANGGAL)
        self.assertEqual(stat["total"], 2)
        # Kartu yang direview jatuh tempo besok, jadi tinggal 1 yang jatuh tempo.
        self.assertEqual(stat["jatuh_tempo"], 1)
        self.assertEqual(stat["sudah_direview"], 1)
        self.assertEqual(stat["rata_rata_ease"], 2.55)  # (2,6 + 2,5) / 2
        self.assertEqual(stat["distribusi_interval"], {0: 1, 1: 1})

    def test_statistik_deck_kosong(self):
        data = _data_dengan_deck()
        stat = model.statistik_deck(model.cari_deck(data, "JST"), TANGGAL)
        self.assertEqual(stat, {
            "total": 0,
            "jatuh_tempo": 0,
            "sudah_direview": 0,
            "rata_rata_ease": 0.0,
            "distribusi_interval": {},
        })


if __name__ == "__main__":
    unittest.main()
