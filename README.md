# KartuPintar

Aplikasi flashcard CLI berbahasa Indonesia dengan **spaced repetition (algoritma SM-2)**.
Belajar lebih ingat, tanpa lupa: kartu yang sudah dikuasai muncul makin jarang,
kartu yang masih sulit muncul lagi besok.

Tanpa dependensi, tanpa akun, tanpa internet. Data tersimpan lokal sebagai JSON.
Cukup Python 3.10+ — tidak perlu `pip install` apa pun.

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

# Hapus kartu (nomor kartu dari daftar di atas)
python3 -m kartupintar.cli kartu hapus --deck JST --nomor 1

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
Lihat versi aplikasi dengan `python3 -m kartupintar.cli --version` (saat ini 0.1.0).

Pesan error selalu diawali `Error:` dan keluar dengan kode 1, misalnya
`Error: Deck "JST" tidak ditemukan.` atau
`Error: --nomor harus berupa angka, contoh: --nomor 1.`

## Data contoh

Berkas `contoh/kartupintar-contoh.json` berisi 1 deck JST dengan 5 kartu
tentang jaringan syaraf tiruan — 1 kartu sudah direview 1× (jatuh tempo
besok), 4 kartu baru jatuh tempo hari ini. Cara mencobanya:

```bash
cp contoh/kartupintar-contoh.json kartupintar.json
python3 -m kartupintar.cli jatuh-tempo
python3 -m kartupintar.cli statistik --deck JST
python3 -m kartupintar.cli review --deck JST
```

## Cara kerja SM-2 (review)

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
berikutnya → interval sebelumnya × ease (dibulatkan).
Ease baru = ease + (0,1 − (5 − nilai) × (0,08 + (5 − nilai) × 0,02)),
dan ease tidak pernah di bawah 1,3.

Contoh: kartu baru dinilai 5 tiga kali berturut-turut → ease 2,6 → 2,7 → 2,8,
interval 1 → 6 → 17 hari. Sekali dinilai di bawah 3, repetisi kembali 0 dan
interval kembali 1 hari.

## Jatuh tempo & statistik

`jatuh-tempo` menampilkan semua kartu yang jatuh tempo hari ini atau sebelumnya,
dari semua deck, urut tanggal jatuh tempo. `statistik --deck NAMA` merangkum
satu deck: total kartu, berapa yang jatuh tempo, berapa yang sudah direview,
rata-rata ease, dan distribusi interval.

Contoh keluaran untuk deck contoh di atas:

```
Statistik deck "JST":
  Total kartu        : 5
  Jatuh tempo        : 4
  Sudah direview     : 1
  Rata-rata ease     : 2.52
  Distribusi interval:
    0 hari: 4 kartu
    1 hari: 1 kartu
```

Angkanya cocok hitungan tangan: rata-rata ease = (2,6 + 2,5 + 2,5 + 2,5 + 2,5) / 5
= 2,52; 4 kartu baru berinterval 0 hari dan 1 kartu yang sudah direview 1×
berinterval 1 hari.

## Impor / ekspor CSV

`ekspor` menulis deck ke CSV dengan kolom
`depan,belakang,ease,interval,repetisi,jatuh_tempo`.
`impor` membaca CSV yang sama — deck tujuan dibuat otomatis bila belum ada,
baris yang tidak valid (sisi kosong, angka bukan bilangan, ease di bawah 1,3,
tanggal salah format) dilewati dengan peringatan, bukan menggagalkan semuanya.

Contoh CSV nyata dari deck contoh (`ekspor --deck JST --keluar jst.csv`):

```csv
depan,belakang,ease,interval,repetisi,jatuh_tempo
Apa itu perceptron?,Model neuron tiruan paling sederhana: y = f(sum(w*x) + b).,2.6,1,1,2026-11-17
Apa fungsi aktivasi step?,Mengubah jumlah terbobot z menjadi keluaran biner 0 atau 1.,2.5,0,0,2026-11-16
Apa itu epoch dalam pelatihan JST?,Satu putaran penuh pelatihan atas seluruh data latih.,2.5,0,0,2026-11-16
Apa beda supervised dan unsupervised learning?,"Supervised belajar dari data berlabel (ada target Y), unsupervised mencari pola tanpa label.",2.5,0,0,2026-11-16
Apa itu overfitting?,Model terlalu hafal data latih sehingga gagal pada data baru.,2.5,0,0,2026-11-16
```

Teks yang mengandung koma otomatis dikutip, jadi impor-ekspor bolak-balik
menghasilkan kartu yang sama persis, termasuk nilai SM-2-nya.

## Menjalankan test

```bash
python3 -m unittest discover -s tests
```

31 test, semua lolos: model deck & kartu (16), algoritma SM-2 (14),
dan CLI end-to-end (3) — termasuk alur lengkap buat deck → tambah kartu →
review → jatuh-tempo → statistik → ekspor/impor, serta input salah yang
ditolak dengan kode keluar bukan 0.

## Rencana

- [x] Deck & kartu (buat, daftar, tambah, hapus)
- [x] Review SM-2 + sesi interaktif
- [x] Kartu jatuh tempo & statistik deck
- [x] Ekspor / impor CSV
- [x] Test + data contoh
- [x] README lengkap + polish CLI
- [ ] Statistik retensi & mode latihan tanpa nilai

## Lisensi

MIT — lihat `LICENSE`.
