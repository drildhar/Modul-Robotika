# Robot Pengikut Garis

Program untuk Tantangan Robot Pengikut Garis, ditulis untuk hub LEGO
MINDSTORMS Robot Inventor dengan firmware Pybricks sudah terpasang.

Materi asalnya ada di folder `../Pybricks/`. Baca urut:

1. `../Pybricks/instalasi-pybricks.md` — memasang firmware dan `pybricksdev`
2. `../Pybricks/dasar-pybricks.md` — motor, sensor, DriveBase, kalibrasi
3. `../Pybricks/pengikut-garis.md` — pengikut garis dari nol, PID, tuning

Ketentuan tantangannya ada di `../Tantangan/buku-panduan.pdf`.

## Berkas

| Berkas | Isi |
|---|---|
| `config.py` | Semua angka setelan. Angka bertanda UKUR harus kalian ukur sendiri |
| `linefollow.py` | Kelas `LineFollower`: PD, kecepatan adaptif, penanganan garis hilang. Juga `find_line()` untuk mencari garis lagi setelah berputar |
| `calibrate.py` | Enam tugas pengukuran, dijalankan dengan tombol hub |
| `main.py` | Program tantangan: mesin keadaan FOLLOW, APPROACH, READ, TURN, REACQUIRE |

`linefollow.py` dan `config.py` tidak berjalan sendiri. Yang dikirim ke hub
adalah `main.py` atau `calibrate.py`; `pybricksdev` ikut mengirim berkas yang
diimpor.

## Menyiapkan lingkungan

Dari akar repositori:

```bash
uv venv
uv pip install pybricksdev pybricks
```

Paket `pybricksdev` yang mengirim program ke hub. Paket `pybricks` cuma
daftar fungsi untuk VS Code, supaya kode dilengkapi otomatis. Keduanya
dipasang di laptop, bukan di hub.

Di VS Code, pilih interpreter `.venv` lewat `Ctrl` + `Shift` + `P`, lalu
Python: Select Interpreter.

## Menjalankan

Hub kalian bernama `Marin Kitagawa`. Kalau kalian mengganti namanya, ubah di
tiga tempat: contoh perintah di bawah, `pybricks.hubName` di
`.vscode/settings.json`, dan tidak ada tempat lain.

```bash
./.venv/bin/pybricksdev run ble --name "Marin Kitagawa" robot/main.py
```

Tanda kutipnya wajib karena namanya mengandung spasi.

Nyalakan hub dulu sampai lampu di sekeliling tombol tengah berkedip biru.
Jangan menyambungkan hub lewat menu Bluetooth sistem operasi; `pybricksdev`
mencarinya sendiri. Tutup juga tab `code.pybricks.com` kalau masih terbuka,
karena hub hanya menerima satu sambungan Bluetooth pada satu waktu.

Selama menyetel, pakai `--stay-connected` supaya tidak mencari hub dari awal
setiap kali:

```bash
./.venv/bin/pybricksdev run ble --name "Marin Kitagawa" --stay-connected robot/main.py
```

Kalau `.vscode/tasks.json` sudah diisi namanya, cukup buka berkasnya di
editor lalu tekan `Ctrl` + `Shift` + `B`.

## Yang harus dikerjakan sebelum tantangan

Urutannya penting. Setiap langkah memberi angka yang dipakai langkah
berikutnya.

### 1. Periksa rakitan

Tiga uji di `pengikut-garis.md` bagian 2.4. Robot yang rangkanya goyang tidak
bisa diselamatkan oleh penguatan sehebat apa pun. Kalau uji ini gagal,
perbaiki rakitan dulu, jangan menyetel angka.

### 2. Ukur dengan `calibrate.py`

| Tugas | Mengisi di `config.py` |
|---|---|
| 1. Sapu hitam dan putih | `BLACK`, `WHITE` |
| 2. Uji jalan lurus | `WHEEL_DIAMETER` |
| 3. Uji berputar | `AXLE_TRACK` |
| 4. Ukur warna dinding | `WALL_READ_MM` |
| 5. Kecepatan loop | periksa `LOOP_MS` |
| 6. Catat jarak sensor | tidak ada, cuma melihat derau |

Tugas 1 sampai 3 boleh dikerjakan lebih dulu tanpa memikirkan tantangan.
Tugas 4 khusus untuk CP2, lihat bagian berikutnya.

Selesaikan tugas 2 sebelum tugas 3, karena `WHEEL_DIAMETER` ikut
mempengaruhi hasil putaran.

### 3. Setel pengikut garis

Ikuti urutan di `pengikut-garis.md` bagian 10. Ringkasnya:

1. Kunci letak sensor dan `LOOP_MS`
2. Ukur `BLACK` dan `WHITE`
3. `KD` nol, kecepatan pelan, naikkan `KP` sampai robot berkelok dengan irama tetap
4. Turunkan `KP` ke 60 sampai 70 persen nilai itu
5. Naikkan `KD` sampai kelokannya teredam
6. Naikkan `BASE_SPEED` sampai robot mulai lepas dari garis
7. Turunkan `MIN_SPEED` supaya tikungan patah tetap aman

Ubah satu angka setiap percobaan. Ukur hasilnya dengan waktu putaran, bukan
dengan kesan. Catat setiap percobaan, termasuk yang gagal.

## Soal membaca warna dinding

Ini bagian yang tidak ada di materi, dan yang paling mungkin membuat
kehilangan nilai CP2 sebesar 30 persen. Bacalah sebelum menyetel apa pun.

Sensor warna menghadap ke lantai. Supaya bisa membaca dinding yang tegak,
robot harus maju sampai permukaan dinding masuk ke jangkauan sensornya, dan
itu hanya beberapa milimeter. Dua syaratnya:

1. Sensor cukup dekat sehingga pantulan lampunya sendiri lebih kuat daripada
   cahaya ruangan.
2. Tidak ada bagian lain yang lebih dulu menyentuh dinding: bumper, kabel,
   atau badan robot.

Tugas 4 di `calibrate.py` mengukur syarat pertama. Yang kalian cari adalah
rentang jarak tempat `color()` melaporkan warna dinding dengan benar dan
stabil. Kalau rentang itu kosong, artinya sensornya tidak bisa melihat
dinding dari posisi terpasang sekarang, dan penyelesaiannya mekanis:

- putar dudukan sensor supaya menghadap ke depan, lalu pakai sensor kedua
  yang menghadap lantai untuk mengikuti garis, atau
- geser sensor ke tepi depan robot supaya bisa menjulur lebih dekat ke dinding.

Yang perlu diubah di kode cuma fungsi `read_wall_color()` di `main.py`.
Sisa program, termasuk mesin keadaannya, tidak ikut berubah. Itu sebabnya
pembacaan sensor sengaja dikumpulkan di satu tempat.

Satu hal lagi yang perlu kalian putuskan: robot berhenti mengikuti garis
selama membaca warna, jadi tidak ada umpan balik posisi saat itu. Kalau
dindingnya menyudut, `BACKOFF_MM` dan `WALL_COOLDOWN_MS` yang menolong.

## Cara program mengambil keputusan

| Keadaan | Yang dikerjakan | Selesai kalau |
|---|---|---|
| FOLLOW | `LineFollower.step()` | ada dinding, atau jatah manuver habis dan garis hilang |
| APPROACH | maju pelan sampai `WALL_READ_MM` | sudah dekat, bumper tertekan, atau waktu habis |
| READ | 12 sampel, suara terbanyak, minimal 5 suara | warna dikenali, atau 3 percobaan habis |
| TURN | mundur `BACKOFF_MM`, lalu `robot.turn()` | putaran selesai |
| REACQUIRE | `find_line()`: maju pelan, lalu menyapu melebar | garis ketemu |

Aturan warnanya ada di `WALL_TURN` di `config.py`. Merah ke kiri, hijau ke
kanan, kuning pilihan tim. Ganti pilihan kuning di situ kalau kalian mau
ke kanan.

Kalau warna tidak dikenali setelah tiga percobaan, robot memakai
`FALLBACK_COLOR`, yaitu kuning, karena kuning boleh ke arah mana saja.
Kehilangan satu dinding lebih baik daripada berhenti dan kehilangan sisa
lintasan.

## Batas keselamatan

- `MAX_RUNTIME_MS` membuat robot berhenti sendiri satu menit sebelum batas
  10 menit juri.
- Tombol tengah hub menghentikan program kapan saja.
- Bumper tombol kiri dan kanan menangkap dinding yang tidak terbaca sensor
  ultrasonik, misalnya dinding menyudut atau kaki meja.

## Bukti yang dikumpulkan

Untuk laporan dan penilaian, catat:

- Nilai akhir `WHEEL_DIAMETER` dan `AXLE_TRACK`, jenis lantainya
- `BLACK`, `WHITE`, dan kecepatan loop sebenarnya
- Tabel percobaan tuning: `KP`, `KD`, `BASE_SPEED`, waktu putaran
- Rentang jarak tempat warna dinding terbaca
- Waktu tempuh lima percobaan berturut-turut yang selesai
