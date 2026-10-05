"""Program utama Tantangan Robot Pengikut Garis.

Alur keadaan:

    FOLLOW    ikuti garis dengan PD + kecepatan adaptif
       |
       |  sensor jarak membaca dinding
       v
    APPROACH  maju pelan sampai sensor warna bisa membaca dinding
       |
       v
    READ      baca warna dinding, tentukan arah belok
       |
       v
    TURN      mundur sedikit, lalu berputar sesuai aturan warna
       |
       v
    REACQUIRE cari garis lagi, lalu kembali ke FOLLOW

Setelah `WALLS_TO_HANDLE` dinding ditangani, robot mengikuti garis sampai
garis hilang dan menganggap lintasan selesai.

Dua hal sengaja tidak dikerjakan setiap siklus loop: menulis ke layar, dan
membaca sensor jarak. Keduanya memakan waktu beberapa milidetik, dan kalau
dikerjakan terus-menerus, loop tidak lagi berjalan dengan irama tetap. Nilai
`KD` yang kalian setel mengandaikan irama yang tetap itu. Lihat
`pengikut-garis.md` bagian 11.

Kirim ke hub, ganti nama hub dengan nama yang kalian beri saat memasang
firmware. Nama hub kalian mengandung spasi, jadi tanda kutipnya wajib:

    pybricksdev run ble --name "Marin Kitagawa" robot/main.py

atau tekan Ctrl+Shift+B kalau `.vscode/settings.json` sudah diisi. Nama hub
yang dipakai tugas VS Code ada di situ, pada `pybricks.hubName`.
"""

from pybricks.hubs import InventorHub
from pybricks.parameters import Button, Color, Icon
from pybricks.pupdevices import ColorSensor, Motor, UltrasonicSensor
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait

import config as cfg
from linefollow import LineFollower, find_line

# ---------------------------------------------------------------------------
# Perangkat
# ---------------------------------------------------------------------------
hub = InventorHub()
left = Motor(cfg.PORT_LEFT, cfg.DIR_LEFT)
right = Motor(cfg.PORT_RIGHT, cfg.DIR_RIGHT)
eyes = UltrasonicSensor(cfg.PORT_EYES)
sensor = ColorSensor(cfg.PORT_LINE)

robot = DriveBase(
    left,
    right,
    wheel_diameter=cfg.WHEEL_DIAMETER,
    axle_track=cfg.AXLE_TRACK,
)

follower = LineFollower(robot, sensor)

# ---------------------------------------------------------------------------
# Membaca warna dinding
# ---------------------------------------------------------------------------
# Sensor warna menghadap ke lantai. Supaya bisa membaca dinding, robot harus
# maju sampai permukaan dinding masuk ke jangkauan sensor, yaitu beberapa
# milimeter saja. Dua hal ini harus benar, dan keduanya soal rakitan, bukan
# kode:
#
#   1. Sensor cukup dekat sehingga pantulan lampunya sendiri lebih kuat dari
#      cahaya ruangan. Batas jaraknya perlu kalian ukur sendiri dengan
#      `calibrate.py` tugas 4.
#   2. Tidak ada yang lebih dulu menyentuh dinding: bumper, kabel, atau badan
#      robot. Kalau ada, robot berhenti sebelum sensor sempat membaca.
#
# Kalau pembacaan tetap tidak bisa dipercaya di jarak berapa pun, yang perlu
# diubah cuma fungsi `read_wall_color()` di bawah. Perbaikannya mekanis:
# putar dudukan sensor supaya menghadap depan, atau tambahkan sensor warna
# kedua yang menghadap dinding. Sisa program tidak perlu ikut berubah.
# ---------------------------------------------------------------------------


def classify_hsv(hsv):
    """Ubah (hue, saturation, value) menjadi Color, atau None kalau pudar.

    Dipakai sebagai cadangan ketika `sensor.color()` tidak yakin. Berguna
    karena dinding yang tergores atau kena bayangan sering membuat
    `color()` mengembalikan Color.NONE.
    """
    if hsv is None:
        return None

    hue, saturation, value = hsv

    if saturation < cfg.MIN_SATURATION or value < cfg.MIN_VALUE:
        return None

    for low, high in cfg.HUE_RED:
        if low <= hue <= high:
            return Color.RED
    for low, high in cfg.HUE_YELLOW:
        if low <= hue <= high:
            return Color.YELLOW
    for low, high in cfg.HUE_GREEN:
        if low <= hue <= high:
            return Color.GREEN

    return None


def read_wall_color():
    """Ambil beberapa sampel dan ambil suara terbanyak.

    Satu pembacaan terlalu berisik untuk dipakai mengambil keputusan, karena
    satu sampel yang salah membuat robot berbelok ke arah yang salah dan
    kehilangan nilai CP2. Mengembalikan (warna, suara).
    """
    votes = {}

    for _ in range(cfg.WALL_SAMPLES):
        color = sensor.color()

        # `color()` hanya mengembalikan warna yang ada di DETECTABLE. Kalau
        # hasilnya WHITE atau NONE, coba tebak dari nilai hue mentahnya.
        if color not in cfg.WALL_COLORS:
            color = classify_hsv(sensor.hsv())

        if color is not None:
            votes[color] = votes.get(color, 0) + 1

        wait(cfg.WALL_SAMPLE_MS)

    best = None
    best_count = 0
    for color in votes:
        if votes[color] > best_count:
            best = color
            best_count = votes[color]

    if best_count < cfg.MIN_VOTES:
        return None, votes

    return best, votes


# ---------------------------------------------------------------------------
# Tindakan
# ---------------------------------------------------------------------------


def wall_ahead():
    """Benar kalau ada dinding di depan.

    Dibaca dua kali dengan jeda pendek supaya satu pembacaan yang berisik
    tidak langsung memicu manuver. Sensor ultrasonik bergoyang beberapa
    milimeter walau robot diam, lihat `dasar-pybricks.md` bagian 13.
    """
    if eyes.distance() > cfg.WALL_DETECT_MM:
        return False

    wait(30)
    return eyes.distance() <= cfg.WALL_DETECT_MM


def handle_wall():
    """Maju mendekat, baca warna, mundur, lalu berputar.

    Mengembalikan pasangan (warna, sudut) yang dipakai, supaya bisa dicatat
    di terminal.
    """
    robot.brake()

    # ---Approach, maju pelan sampai cukup dekat--------------------------------
    timer = StopWatch()
    robot.drive(cfg.APPROACH_SPEED, 0)

    while True:
        pressed = hub.buttons.pressed()
        if Button.LEFT in pressed or Button.RIGHT in pressed:
            # Bumper menyentuh sesuatu. Dinding yang menyudut sering tidak
            # terbaca sensor ultrasonik, jadi bumper ini yang menangkapnya.
            print("bumper tertekan, berhenti mendekat")
            break

        if eyes.distance() <= cfg.WALL_READ_MM:
            break

        if timer.time() > cfg.APPROACH_TIMEOUT_MS:
            print("waktu mendekat habis, lanjut saja")
            break

        wait(10)

    robot.brake()
    wait(cfg.WALL_SETTLE_MS)
    print("berhenti pada jarak", eyes.distance(), "mm")

    # ---Read, baca warna dinding-----------------------------------------------
    color = None
    attempt = 0

    while color is None and attempt < cfg.WALL_READ_ATTEMPTS:
        attempt = attempt + 1
        color, votes = read_wall_color()
        print("percobaan", attempt, "warna:", color, "suara:", votes)

        if color is None and attempt < cfg.WALL_READ_ATTEMPTS:
            # Mungkin masih terlalu jauh dari dinding. Maju sedikit lagi.
            robot.straight(cfg.WALL_NUDGE_MM)

    # ---Turn, berputar sesuai aturan warna------------------------------------
    if cfg.BACKOFF_MM:
        # Mundur dulu, kalau tidak robot menyeret dirinya sendiri di sepanjang
        # dinding saat berputar dan sudutnya meleset.
        robot.straight(-cfg.BACKOFF_MM)

    if color is None:
        print("warna tidak dikenali, pakai pilihan tim")
        angle = cfg.WALL_TURN[cfg.FALLBACK_COLOR]
    else:
        angle = cfg.WALL_TURN[color]

    print("berputar", angle, "derajat")
    robot.turn(angle)

    return color, angle


def countdown():
    """Jeda supaya kalian sempat meletakkan robot. Lihat bagian 12."""
    for number in (3, 2, 1):
        hub.display.number(number)
        hub.speaker.beep(600, 80)
        wait(1000)
    hub.display.off()


# ---------------------------------------------------------------------------
# Program
# ---------------------------------------------------------------------------

STATE_FOLLOW = 0
STATE_REACQUIRE = 1

# Menulis ke layar 5x5 dan membaca sensor jarak sama-sama memakan waktu
# beberapa milidetik. Kalau dikerjakan setiap siklus, loop tidak lagi berjalan
# tiap LOOP_MS, dan nilai KD yang sudah kalian setel jadi salah. Karena itu
# layar hanya ditulis kalau tulisannya berubah, dan dinding hanya diperiksa
# tiap WALL_CHECK_EVERY siklus.
#
# Kalau kalian mengubah angka-angka ini, ukur ulang kecepatan loop dengan
# `calibrate.py` tugas 5.
_last_label = [None]

def show(label):
    """Tulis satu huruf ke layar, tapi hanya kalau berubah."""
    if _last_label[0] != label:
        _last_label[0] = label
        hub.display.char(label)


def main():
    sensor.detectable_colors(cfg.DETECTABLE)
    robot.settings(straight_speed=cfg.BASE_SPEED)

    print("siap. tekan tombol tengah hub untuk mulai")
    show("R")
    while Button.CENTER not in hub.buttons.pressed():
        wait(20)

    countdown()

    follower.reset()

    watchdog = StopWatch()
    cooldown = StopWatch()
    cooldown.reset()

    walls_done = 0
    state = STATE_FOLLOW
    loop_count = 0

    while True:
        pressed = hub.buttons.pressed()

        if Button.CENTER in pressed:
            print("dihentikan manual")
            break

        if watchdog.time() > cfg.MAX_RUNTIME_MS:
            print("batas waktu habis, berhenti")
            break

        if state == STATE_FOLLOW:
            show("F")

            # Dinding hanya dicari selama jatah manuver belum habis, tidak
            # selama jeda sesudah manuver sebelumnya, dan tidak setiap siklus.
            wall = False
            loop_count = loop_count + 1
            if loop_count >= cfg.WALL_CHECK_EVERY:
                loop_count = 0
                wall = (
                    walls_done < cfg.WALLS_TO_HANDLE
                    and cooldown.time() > cfg.WALL_COOLDOWN_MS
                    and wall_ahead()
                )

            if wall:
                show("C")
                color, angle = handle_wall()
                walls_done = walls_done + 1
                print("dinding", walls_done, "warna", color, "belok", angle)
                cooldown.reset()
                loop_count = 0
                state = STATE_REACQUIRE
                continue

            follower.step()

            # Semua dinding sudah ditangani, jadi garis hilang sekarang berarti
            # lintasan sudah selesai. Ini tebakan dari bentuk lintasan, sesuaikan
            # kalau lintasan kalian berakhir dengan cara lain.
            if walls_done >= cfg.WALLS_TO_HANDLE and follower.lost_time > cfg.FINISH_LOST_MS:
                print("garis hilang setelah semua dinding, anggap selesai")
                break

        elif state == STATE_REACQUIRE:
            show("R")

            if find_line(robot, sensor, follower):
                print("garis ditemukan lagi")
            else:
                # Bukan jalan buntu. Kembali ke FOLLOW, dan penanganan garis
                # hilang di dalam `LineFollower.step()` yang menyapu mencari.
                print("garis belum ketemu, andalkan sapuan pengikut garis")

            state = STATE_FOLLOW

    robot.stop()
    hub.display.icon(Icon.HAPPY)
    hub.speaker.beep(880, 400)

    print("selesai")
    print("dinding ditangani:", walls_done)
    print("waktu berjalan:", watchdog.time(), "ms")


main()
