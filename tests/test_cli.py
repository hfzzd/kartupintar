"""Unit test CLI KartuPintar (end-to-end lewat subprocess di direktori sementara)."""

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _jalankan(args, cwd, masukan=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "kartupintar.cli"] + args,
        input=masukan, text=True, capture_output=True, cwd=cwd, env=env,
    )


class TestCLI(unittest.TestCase):
    def test_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            hasil = _jalankan(["--version"], tmp)
            self.assertEqual(hasil.returncode, 0)
            self.assertIn("0.1.0", hasil.stdout)

    def test_alur_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            hasil = _jalankan(["deck", "buat", "--nama", "JST",
                               "--deskripsi", "Istilah JST"], tmp)
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            self.assertIn('Deck "JST" dibuat.', hasil.stdout)

            for depan, belakang in [
                ("Apa itu perceptron?", "Model neuron tiruan paling sederhana."),
                ("Apa itu epoch?", "Satu putaran penuh pelatihan atas seluruh data."),
            ]:
                hasil = _jalankan(["kartu", "tambah", "--deck", "JST",
                                   "--depan", depan, "--belakang", belakang], tmp)
                self.assertEqual(hasil.returncode, 0, hasil.stderr)

            hasil = _jalankan(["kartu", "daftar", "--deck", "JST"], tmp)
            self.assertIn("Apa itu perceptron?", hasil.stdout)
            self.assertIn("Apa itu epoch?", hasil.stdout)

            # Review 2 kartu: Enter lihat jawaban, lalu nilai 5 dan 4.
            hasil = _jalankan(["review", "--deck", "JST"], tmp, masukan="\n5\n\n4\n")
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            self.assertIn("Sesi review selesai: 2 kartu direview.", hasil.stdout)

            # Kedua kartu sudah direview: tidak ada lagi yang jatuh tempo hari ini.
            hasil = _jalankan(["jatuh-tempo"], tmp)
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            self.assertIn("Tidak ada kartu jatuh tempo", hasil.stdout)

            hasil = _jalankan(["statistik", "--deck", "JST"], tmp)
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            self.assertIn("Total kartu        : 2", hasil.stdout)
            self.assertIn("Sudah direview     : 2", hasil.stdout)

            # Ekspor lalu impor ke deck lain: semua kartu pindah utuh.
            hasil = _jalankan(["ekspor", "--deck", "JST", "--keluar", "jst.csv"], tmp)
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            with open(os.path.join(tmp, "jst.csv"), encoding="utf-8") as f:
                isi_csv = f.read()
            self.assertIn("depan,belakang,ease,interval,repetisi,jatuh_tempo", isi_csv)

            hasil = _jalankan(["impor", "--deck", "Salinan", "--berkas", "jst.csv"], tmp)
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            self.assertIn("2 kartu diimpor", hasil.stdout)
            hasil = _jalankan(["kartu", "daftar", "--deck", "Salinan"], tmp)
            self.assertIn("Apa itu perceptron?", hasil.stdout)
            self.assertIn("Apa itu epoch?", hasil.stdout)

    def test_retensi_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            _jalankan(["deck", "buat", "--nama", "JST"], tmp)
            for depan, belakang in [
                ("Apa itu perceptron?", "Model neuron tiruan paling sederhana."),
                ("Apa itu epoch?", "Satu putaran penuh pelatihan atas seluruh data."),
            ]:
                hasil = _jalankan(["kartu", "tambah", "--deck", "JST",
                                   "--depan", depan, "--belakang", belakang], tmp)
                self.assertEqual(hasil.returncode, 0, hasil.stderr)

            # Review 2 kartu: nilai 5 (benar) dan 2 (salah).
            hasil = _jalankan(["review", "--deck", "JST"], tmp, masukan="\n5\n\n2\n")
            self.assertEqual(hasil.returncode, 0, hasil.stderr)

            hasil = _jalankan(["retensi", "--deck", "JST"], tmp)
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            self.assertIn("Total review       : 2", hasil.stdout)
            self.assertIn("Benar (nilai >= 3) : 1", hasil.stdout)
            self.assertIn("Tingkat retensi    : 50.0%", hasil.stdout)
            self.assertIn("Streak             : 1 hari", hasil.stdout)

            # --hari bukan angka: ditolak ramah, exit 1.
            hasil = _jalankan(["retensi", "--deck", "JST", "--hari", "abc"], tmp)
            self.assertEqual(hasil.returncode, 1)
            self.assertIn("Error: --hari harus berupa angka", hasil.stderr)
            # --hari 0: ditolak ramah, exit 1.
            hasil = _jalankan(["retensi", "--deck", "JST", "--hari", "0"], tmp)
            self.assertEqual(hasil.returncode, 1)
            self.assertIn("Error: Jumlah hari harus minimal 1.", hasil.stderr)
            # Deck hilang: exit 1.
            hasil = _jalankan(["retensi", "--deck", "TidakAda"], tmp)
            self.assertEqual(hasil.returncode, 1)
            self.assertIn("Error:", hasil.stderr)

    def test_latihan_end_to_end_tidak_mengubah_berkas(self):
        with tempfile.TemporaryDirectory() as tmp:
            _jalankan(["deck", "buat", "--nama", "JST"], tmp)
            for depan, belakang in [
                ("Apa itu perceptron?", "Model neuron tiruan paling sederhana."),
                ("Apa itu epoch?", "Satu putaran penuh pelatihan atas seluruh data."),
            ]:
                hasil = _jalankan(["kartu", "tambah", "--deck", "JST",
                                   "--depan", depan, "--belakang", belakang], tmp)
                self.assertEqual(hasil.returncode, 0, hasil.stderr)
            berkas_data = os.path.join(tmp, "kartupintar.json")

            def _md5():
                with open(berkas_data, "rb") as f:
                    return hashlib.md5(f.read()).hexdigest()

            # Berhenti dengan q: exit 0, berkas data tidak berubah.
            sebelum = _md5()
            hasil = _jalankan(["latihan", "--deck", "JST"], tmp, masukan="q\n")
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            self.assertIn("Latihan dihentikan.", hasil.stdout)
            self.assertEqual(_md5(), sebelum)

            # Berhenti dengan EOF (stdin langsung habis): exit 0, berkas tetap sama.
            hasil = _jalankan(["latihan", "--deck", "JST"], tmp, masukan="")
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            self.assertIn("Latihan dihentikan.", hasil.stdout)
            self.assertEqual(_md5(), sebelum)

            # Lihat semua kartu (Enter dua kali): selesai rapi, berkas tetap sama.
            hasil = _jalankan(["latihan", "--deck", "JST"], tmp, masukan="\n\n")
            self.assertEqual(hasil.returncode, 0, hasil.stderr)
            self.assertIn("Latihan selesai: 2 kartu dilihat.", hasil.stdout)
            self.assertIn("Apa itu perceptron?", hasil.stdout)
            self.assertIn("Apa itu epoch?", hasil.stdout)
            self.assertEqual(_md5(), sebelum)

    def test_input_salah_exit_bukan_nol(self):
        with tempfile.TemporaryDirectory() as tmp:
            _jalankan(["deck", "buat", "--nama", "JST"], tmp)
            # Deck duplikat.
            hasil = _jalankan(["deck", "buat", "--nama", "JST"], tmp)
            self.assertNotEqual(hasil.returncode, 0)
            self.assertIn("Error:", hasil.stderr)
            # Deck tidak ada.
            hasil = _jalankan(["kartu", "tambah", "--deck", "TidakAda",
                               "--depan", "Q", "--belakang", "A"], tmp)
            self.assertNotEqual(hasil.returncode, 0)
            # Nomor kartu bukan angka: ditolak ramah, bukan error argparse.
            hasil = _jalankan(["kartu", "hapus", "--deck", "JST", "--nomor", "abc"], tmp)
            self.assertEqual(hasil.returncode, 1)
            self.assertIn("Error: --nomor harus berupa angka", hasil.stderr)
            # Kartu yang dihapus tidak ada.
            hasil = _jalankan(["kartu", "hapus", "--deck", "JST", "--nomor", "99"], tmp)
            self.assertNotEqual(hasil.returncode, 0)
            # Statistik deck tidak ada.
            hasil = _jalankan(["statistik", "--deck", "TidakAda"], tmp)
            self.assertNotEqual(hasil.returncode, 0)
            # Berkas impor tidak ada.
            hasil = _jalankan(["impor", "--deck", "JST", "--berkas", "hilang.csv"], tmp)
            self.assertNotEqual(hasil.returncode, 0)


if __name__ == "__main__":
    unittest.main()
