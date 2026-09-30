# Sumber berkas gambar

Semua screenshot di folder ini diambil sendiri dari `https://code.pybricks.com` pada 30 September 2026, memakai Chrome headless. Kotak merah bernomor ditambahkan saat pengambilan.

Aplikasi Pybricks Code berasal dari repositori https://github.com/pybricks/pybricks-code.

Tampilan Pybricks Code bisa berubah saat aplikasinya diperbarui. Kalau gambar sudah tidak cocok, ambil ulang dengan skrip `ambil-screenshot.js`:

```bash
npm i playwright-core
node ambil-screenshot.js <folder-tujuan>
```

Skrip memakai Chrome yang terpasang di `C:/Program Files/Google/Chrome/Application/chrome.exe`. Ubah `executablePath` di skrip kalau lokasinya berbeda.

Popup pemilihan perangkat dari Chrome saat Install tidak bisa diambil gambarnya tanpa hub sungguhan, jadi tidak ada di folder ini.
