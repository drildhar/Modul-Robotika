"""Alat ukur untuk mengisi `config.py`.

Jalankan sendiri, bukan diimpor. Kirim ke hub seperti program biasa:

    pybricksdev run ble --name <nama hub> robot/calibrate.py

Tombol kiri dan kanan hub memilih tugas, nomornya muncul di layar 5x5.
Tombol tengah menjalankan tugas. Tombol Bluetooth keluar.

Setiap tugas mencetak hasilnya ke terminal laptop, tempat `print()` muncul
lewat Bluetooth. Catat angkanya di kertas, jangan cuma dilihat sekilas.
"""

from pybricks.hubs import InventorHub
from pybricks.parameters import Button, Color
from pybricks.pupdevices import ColorSensor, Motor, UltrasonicSensor
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait

import config as cfg

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


def stop_now():
    """Hentikan semua motor. Dipanggil di akhir setiap tugas."""
    left.brake()
    right.brake()
    robot.stop()


# ---------------------------------------------------------------------------
# Tugas 1: sapu hitam dan putih
# ---------------------------------------------------------------------------
def task_reflection():
    """Isi BLACK dan WHITE di `config.py`.

    Robot berputar pelan di tempat di atas garis, jadi sensornya menyapu
    melewati hitam dan putih berkali-kali. Cara ini lebih jujur daripada
    menggeser robot dengan tangan, karena jarak sensor ke lantai tidak
    berubah selama pengukuran. Lihat `pengikut-garis.md` bagian 3.2.
    """
    print("letakkan sensor tepat di atas garis.")
    print("robot berputar pelan 5 detik, jangan dipegang.")
    wait(2000)

    timer = StopWatch()
    low = 100
    high = 0

    robot.drive(0, 60)

    while timer.time() < 5000:
        value = sensor.reflection()
        if value < low:
            low = value
        if value > high:
            high = value
        wait(10)

    robot.stop()

    if high - low < 30:
        print("PERINGATAN: selisih hitam dan putih cuma", high - low)
        print("kurang dari 30. Turunkan sensor, atau perbaiki kontras lintasan.")
    else:
        print("selisih:", high - low, "(bagus kalau minimal 30)")

    print("BLACK =", low)
    print("WHITE =", high)
    print("THRESHOLD =", (low + high) / 2.0)
    print("SCALE =", 200.0 / (high - low) if high != low else "tidak bisa dihitung")
    stop_now()


# ---------------------------------------------------------------------------
# Tugas 2: uji jalan lurus
# ---------------------------------------------------------------------------
def task_straight():
    """Kalibrasi WHEEL_DIAMETER. Lihat `dasar-pybricks.md` bagian 8."""
    left.reset_angle(0)
    right.reset_angle(0)
    robot.reset()

    print("maju 1000 mm. tandai titik berangkat dan titik berhenti.")
    wait(2000)

    robot.straight(1000)
    stop_now()

    print("encoder bilang:", robot.distance(), "mm")
    print("motor kiri:", left.angle(), "derajat")
    print("motor kanan:", right.angle(), "derajat")
    print("")
    print("Ukur jarak sebenarnya dengan meteran.")
    print("Kurang dari 1000 mm  -> kecilkan WHEEL_DIAMETER")
    print("Lebih dari 1000 mm   -> besarkan WHEEL_DIAMETER")
    print("Ukur juga simpangannya ke samping. Lebih dari 20 mm per 500 mm")
    print("berarti masalahnya di rakitan, bukan di kode.")


# ---------------------------------------------------------------------------
# Tugas 3: uji berputar
# ---------------------------------------------------------------------------
def task_turn():
    """Kalibrasi AXLE_TRACK. Kerjakan setelah tugas 2 benar."""
    robot.reset()

    print("berputar 360 derajat. robot harus kembali ke arah semula.")
    wait(2000)

    robot.turn(360)
    stop_now()

    print("encoder bilang:", robot.angle(), "derajat")
    print("")
    print("Kurang berputar -> besarkan AXLE_TRACK")
    print("Kelewat        -> kecilkan AXLE_TRACK")
    print("Selalu betulkan WHEEL_DIAMETER lebih dulu, karena nilai itu ikut")
    print("mempengaruhi hasil putaran.")


# ---------------------------------------------------------------------------
# Tugas 4: ukur pada jarak berapa warna dinding bisa dibaca
# ---------------------------------------------------------------------------
def task_wall_probe():
    """Tugas paling penting untuk CP2.

    Robot maju sangat pelan ke arah dinding sambil mencetak jarak dan hasil
    pembacaan warna. Perhatikan pada jarak berapa `color()` mulai benar dan
    pada jarak berapa pembacaannya rusak lagi. Angka jarak itu yang dipakai
    untuk WALL_READ_MM di `config.py`.

    Yang kalian cari: rentang jarak tempat warna dinding terbaca stabil.
    Kalau rentangnya kosong, sensornya harus dipindah atau ditambah.
    """
    sensor.detectable_colors(cfg.DETECTABLE)

    print("maju pelan ke dinding. tekan tombol hub untuk berhenti.")
    print("jarak | color | hsv | ambient | reflection")
    wait(2000)

    timer = StopWatch()
    robot.drive(40, 0)
    last_printed = -100

    while True:
        distance = eyes.distance()

        # Cetak tiap 5 mm, jangan tiap loop, supaya terminalnya terbaca.
        # Sengaja tanpa format lebar kolom, karena MicroPython hanya
        # mendukung sebagian dari sintaks format Python.
        if abs(distance - last_printed) >= 5:
            print(
                "jarak",
                distance,
                "mm | color",
                sensor.color(),
                "| hsv",
                sensor.hsv(),
                "| ambient",
                sensor.ambient(),
                "| reflection",
                sensor.reflection(),
            )
            last_printed = distance

        pressed = hub.buttons.pressed()
        if (
            Button.LEFT in pressed
            or Button.RIGHT in pressed
            or Button.CENTER in pressed
        ):
            print("dihentikan")
            break

        if distance < 20:
            print("sudah terlalu dekat, berhenti")
            break

        if timer.time() > 15000:
            print("waktu habis, berhenti")
            break

        wait(30)

    stop_now()
    print("")
    print("Isi hasilnya ke WALL_READ_MM di config.py. Kalau warnanya tidak")
    print("pernah terbaca benar di jarak berapa pun, jangan setel angkanya:")
    print("dudukannya yang perlu diubah, lihat catatan di main.py.")


# ---------------------------------------------------------------------------
# Tugas 5: kecepatan loop sebenarnya
# ---------------------------------------------------------------------------
def task_loop_rate():
    """Angka ini menjelaskan kenapa `wait(10)` bukan berarti 10 ms.

    Kalau hasilnya jauh di bawah 1000 / LOOP_MS, besarkan LOOP_MS di
    `config.py` sampai mendekati irama sebenarnya, lalu setel ulang KD.
    Lihat `pengikut-garis.md` bagian 11.
    """
    print("mengukur berapa kali sensor bisa dibaca dalam 3 detik.")

    timer = StopWatch()
    count = 0

    while timer.time() < 3000:
        sensor.reflection()
        count = count + 1

    print("pembacaan per detik:", count / 3)
    print("yang diminta LOOP_MS:", 1000.0 / cfg.LOOP_MS)
    stop_now()


# ---------------------------------------------------------------------------
# Tugas 6: catat jarak ultrasonic
# ---------------------------------------------------------------------------
def task_distance_log():
    """Lihat sendiri seberapa berisik sensor jaraknya.

    Pegang robot pada jarak tetap dari dinding dan lihat goyangan angkanya.
    Goyangan itu yang membuat robot tidak berhenti persis di satu jarak.
    """
    print("mencatat jarak 8 detik. pegang robot pada jarak tetap.")

    timer = StopWatch()
    while timer.time() < 8000:
        print("jarak:", eyes.distance(), "mm")
        wait(250)

    stop_now()


TASKS = (
    ("sapu hitam dan putih", task_reflection),
    ("uji jalan lurus", task_straight),
    ("uji berputar", task_turn),
    ("ukur warna dinding", task_wall_probe),
    ("kecepatan loop", task_loop_rate),
    ("catat jarak sensor", task_distance_log),
)


def menu():
    """Kiri dan kanan memilih tugas, tengah menjalankan, Bluetooth keluar."""
    index = 0

    while True:
        hub.display.number(index + 1)

        pressed = hub.buttons.pressed()

        if Button.LEFT in pressed:
            index = (index - 1) % len(TASKS)
            wait(250)
        elif Button.RIGHT in pressed:
            index = (index + 1) % len(TASKS)
            wait(250)
        elif Button.CENTER in pressed:
            hub.display.off()
            name, function = TASKS[index]
            print("")
            print("=== tugas", index + 1, ":", name, "===")
            function()
            print("=== selesai ===")
            print("")
            robot.stop()
            wait(500)
        elif Button.BLUETOOTH in pressed:
            hub.display.off()
            print("keluar")
            break

        wait(20)


# ---------------------------------------------------------------------------
# Kalau perintah `pybricksdev run` dipakai bersama argumen tambahan, tugas
# bisa dijalankan langsung tanpa menu. Contoh untuk mencoba di simulator:
#     python calibrate.py 1
# Di hub, biarkan seperti ini dan pakai tombolnya.
# ---------------------------------------------------------------------------
menu()
