# KartuPintar

Aplikasi flashcard CLI berbahasa Indonesia dengan **spaced repetition (algoritma SM-2)**.
Belajar lebih ingat, tanpa lupa: kartu yang sudah dikuasai muncul makin jarang,
kartu yang masih sulit muncul lagi besok.

Tanpa dependensi, tanpa akun, tanpa internet. Data tersimpan lokal sebagai JSON.

## Cara memakai

```bash
# Buat deck baru
python3 -m kartupintar.cli deck buat --nama "JST" --deskripsi "Istilah jaringan syaraf tiruan"

# Lihat semua deck
python3 -m kartupintar.cli deck daftar

# Tambah kartu ke deck
python3 -m kartupintar.cli kartu tambah --deck JST --depan "Apa itu perceptron?" --belakang "Model neuron tiruan paling sederhana: y = f(sum(w*x) + b)."

# Lihat kartu dalam deck
python3 -m kartupintar.cli kartu daftar --deck JST

# Sesi review (kartu yang jatuh tempo hari ini)
python3 -m kartupintar.cli review --deck JST

# Kartu yang jatuh tempo + statistik deck
python3 -m kartupintar.cli jatuh-tempo
python3 -m kartupintar.cli statistik --deck JST

# Ekspor / impor deck sebagai CSV
python3 -m kartupintar.cli ekspor --deck JST --keluar jst.csv
python3 -m kartupintar.cli impor --deck JST --berkas jst.csv
```

Semua perintah memakai file data `kartupintar.json` di direktori kerja.
Pakai `--data berkas-lain.json` untuk memakai file data lain.

## Cara kerja SM-2

Setiap kartu punya **ease** (kemudahan, awal 2,5), **interval** (hari sampai review
berikutnya), dan **repetisi** (berapa kali berturut-turut dijawab benar).

Saat review, beri nilai 0–5 untuk tiap kartu:

| Nilai | Arti | Akibat |
|-------|------|--------|
| 5 | Sempurna, langsung ingat | Interval dikali ease |
| 4 | Benar, agak ragu | Interval dikali ease |
| 3 | Benar, susah payah | Interval dikali ease (ease sedikit turun) |
| 2 | Salah, tapi jawabannya terasa familiar | Ulang dari awal (interval 1 hari) |
| 1 | Salah, jawaban salah | Ulang dari awal (interval 1 hari) |
| 0 | Lupa total | Ulang dari awal (interval 1 hari) |

Aturan interval: jawaban benar pertama → 1 hari, kedua → 6 hari,
berikutnya → interval sebelumnya × ease. Ease tidak pernah di bawah 1,3.

## Menjalankan test

```bash
python3 -m unittest discover -s tests
```

## Rencana

- [x] Deck & kartu (buat, daftar, tambah, hapus)
- [x] Review SM-2 + sesi interaktif
- [x] Kartu jatuh tempo & statistik deck
- [x] Ekspor / impor CSV
- [ ] Test + data contoh
- [ ] Statistik retensi & mode latihan tanpa nilai

## Lisensi

MIT — lihat `LICENSE`.
