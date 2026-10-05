"""Setelan bersama untuk Tantangan Robot Pengikut Garis.

Dua kelompok angka di bawah ini sengaja dipisah, seperti dijelaskan di
`pengikut-garis.md` bagian 9:

  bertanda UKUR  -> hasil pengukuran kalian di lintasan. Berubah kalau
                    lintasan, ruangan, atau rakitan berubah.
  bertanda SETEL -> pilihan kalian. Berubah kalau kalian menyetelnya.

Setiap angka UKUR yang masih memakai angka contoh dari dokumen HARUS
diganti dengan hasil pengukuran sendiri. Pakai `robot/calibrate.py`.
"""

from pybricks.parameters import Color, Direction, Port

# ---------------------------------------------------------------------------
# 1. Peta port
# ---------------------------------------------------------------------------
# Cocokkan dengan huruf yang tercetak di badan hub. Ingat bahwa hurufnya
# berselang-seling: A, C, E di satu sisi dan B, D, F di sisi seberang.
# Lihat `dasar-pybricks.md` bagian 2.
PORT_LEFT = Port.A
PORT_RIGHT = Port.B
PORT_EYES = Port.C
PORT_LINE = Port.D

# Dua motor yang dipasang berhadapan harus dibalik salah satunya, kalau tidak
# robot berputar di tempat saat disuruh maju. Lihat bagian 6.
DIR_LEFT = Direction.COUNTERCLOCKWISE
DIR_RIGHT = Direction.CLOCKWISE

# ---------------------------------------------------------------------------
# 2. Geometri drivetrain (UKUR)
# ---------------------------------------------------------------------------
WHEEL_DIAMETER = 56     # mm, angka di sisi ban. Bagian 7.
AXLE_TRACK = 114        # mm, jarak antar titik sentuh roda. Kalibrasi bagian 8.

# ---------------------------------------------------------------------------
# 3. Acuan Color Sensor untuk garis (UKUR)
# ---------------------------------------------------------------------------
# Hasil `calibrate.py` tugas 1. Ukur ulang setiap ganti ruangan atau lintasan.
BLACK = 9               # pantulan di atas garis hitam
WHITE = 85              # pantulan di atas permukaan putih

THRESHOLD = (BLACK + WHITE) / 2.0
SCALE = 200.0 / (WHITE - BLACK)

# Ambang "garis terlihat" saat mencari garis lagi. Ditaruh di antara ambang
# tengah dan putih, supaya hanya garis yang jelas yang dianggap ketemu.
LINE_SEEN_REFLECTION = (WHITE + THRESHOLD) / 2.0

# ---------------------------------------------------------------------------
# 4. Penguatan pengikut garis (SETEL)
# ---------------------------------------------------------------------------
# Urutan menyetelnya ada di `pengikut-garis.md` bagian 10. Ubah satu angka
# setiap percobaan, dan ukur hasilnya dengan waktu putaran.
BASE_SPEED = 150        # mm/s di jalan lurus
MIN_SPEED = 60          # mm/s saat koreksi paling besar
KP = 0.8
KD = 3.0
LOOP_MS = 10            # periode loop. Kunci dulu sebelum menyetel KD.
LOST_MS = 300           # selama ini dianggap garis benar-benar hilang
LOST_TURN_RATE = 90     # deg/s saat menyapu mencari garis
LOST_ERROR = 80         # error di atas ini dianggap "di atas putih"

# Membaca sensor jarak dan menulis ke layar sama-sama memakan waktu. Kalau
# keduanya dikerjakan setiap siklus, loop tidak lagi berjalan tiap LOOP_MS,
# dan nilai KD yang sudah kalian setel jadi salah. Karena itu keduanya
# dikerjakan sesekali saja. Lihat catatan di `main.py`.

# Lintasan selesai kalau garis hilang selama ini setelah semua dinding
# ditangani. Ini tebakan awal, sesuaikan dengan bentuk lintasan kalian.
FINISH_LOST_MS = 1500

# ---------------------------------------------------------------------------
# 5. Manuver dinding (SETEL, kecuali yang ditandai UKUR)
# ---------------------------------------------------------------------------
WALL_DETECT_MM = 200    # jarak yang memicu keadaan APPROACH
WALL_CHECK_EVERY = 5    # periksa dinding tiap sekian loop, lihat catatan di main.py
WALL_READ_MM = 45       # UKUR: jarak berhenti untuk membaca warna
WALL_SETTLE_MS = 250    # jeda setelah berhenti, sebelum mulai membaca
APPROACH_SPEED = 80     # mm/s, pelan saja supaya tidak menabrak
APPROACH_TIMEOUT_MS = 6000
BACKOFF_MM = 60         # mundur dulu sebelum berputar supaya tidak menyangkut
TURN_ANGLE = 90         # derajat belokan di tiap dinding
WALLS_TO_HANDLE = 2     # nilai penuh CP2 butuh dua dinding
WALL_COOLDOWN_MS = 800  # abaikan dinding sesaat setelah selesai manuver

# ---------------------------------------------------------------------------
# 6. Membaca warna dinding (SETEL)
# ---------------------------------------------------------------------------
WALL_COLORS = (Color.RED, Color.GREEN, Color.YELLOW)

# Batasi warna yang dikenali sensor. Ini membuat `color()` tidak membuang
# waktu menebak biru atau ungu, tapi `WHITE` tetap ikut supaya dinding putih
# dilaporkan sebagai WHITE dan ditolak, bukan dipaksa jadi merah atau hijau.
DETECTABLE = [Color.RED, Color.GREEN, Color.YELLOW, Color.WHITE]

WALL_SAMPLES = 12       # jumlah pembacaan per percobaan
WALL_SAMPLE_MS = 40
MIN_VOTES = 5           # minimal suara terbanyak supaya dianggap sah
WALL_READ_ATTEMPTS = 3  # kalau gagal, maju sedikit dan coba lagi
WALL_NUDGE_MM = 15      # jarak maju di antara percobaan
FALLBACK_COLOR = Color.YELLOW   # kuning boleh ke mana saja, jadi aman

# `hsv()` untuk dinding yang terlalu pudar atau terlalu gelap. Saturation
# rendah berarti hampir putih atau abu-abu, bukan warna.
MIN_SATURATION = 25
MIN_VALUE = 12

# Rentang hue 0 sampai 359. Perhatikan bahwa merah melingkar di ujung.
HUE_RED = ((0, 30), (330, 359))
HUE_YELLOW = ((38, 75),)
HUE_GREEN = ((85, 165),)

# ---------------------------------------------------------------------------
# 7. Aturan warna dinding -> arah belok
# ---------------------------------------------------------------------------
# Dilihat dari atas, sudut positif berputar searah jarum jam, jadi kanan.
# Lihat `dasar-pybricks.md` bagian 7.
TURN_LEFT = -TURN_ANGLE
TURN_RIGHT = TURN_ANGLE

WALL_TURN = {
    Color.RED: TURN_LEFT,       # merah  -> wajib kiri
    Color.GREEN: TURN_RIGHT,    # hijau  -> wajib kanan
    Color.YELLOW: TURN_LEFT,    # kuning -> bebas, tim memilih kiri
}

# ---------------------------------------------------------------------------
# 8. Mencari garis lagi setelah berputar (SETEL)
# ---------------------------------------------------------------------------
REACQUIRE_SPEED = 120           # mm/s, maju pelan dulu
REACQUIRE_FORWARD_MS = 2500
REACQUIRE_TURN_RATE = 70        # deg/s saat menyapu
# Durasi sapuan dalam ms. Tanda bergantian, besar melebar, supaya robot
# menyapu makin jauh ke kedua sisi.
REACQUIRE_SWEEP_MS = (400, -800, 1200, -1600)

# ---------------------------------------------------------------------------
# 9. Batas keselamatan (SETEL)
# ---------------------------------------------------------------------------
# Juri memberi batas 10 menit. Berhenti sendiri satu menit lebih awal supaya
# robot tidak menabrak apa pun setelah waktu habis.
MAX_RUNTIME_MS = 9 * 60 * 1000
