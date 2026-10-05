"""Pengikut garis proporsional-turunan dengan kecepatan adaptif.

Modul ini tidak berjalan sendiri. Dipakai oleh `main.py`.

Algoritmanya dijelaskan bertahap di `pengikut-garis.md`:
  bagian 5   versi proporsional
  bagian 6   tambahan suku turunan
  bagian 6.1 kenapa suku integral tidak dipakai di sini
  bagian 7   kecepatan adaptif
  bagian 8   penanganan garis hilang
"""

from pybricks.tools import StopWatch, wait

import config as cfg


class LineFollower:
    """Menyimpan keadaan loop kendali di antara dua pemanggilan `step()`."""

    def __init__(self, robot, sensor):
        self.robot = robot
        self.sensor = sensor
        self.last_error = 0.0
        self.lost_time = 0

    def reset(self):
        """Lupakan riwayat. Panggil setiap kali robot mulai mengikuti garis."""
        self.last_error = 0.0
        self.lost_time = 0

    def error(self):
        """Simpangan dari tepi garis, -100 di hitam sampai +100 di putih.

        Dinormalisasi dengan `SCALE` supaya penguatan yang kalian setel di
        satu lintasan masih masuk akal di lintasan lain. Lihat bagian 3.3.
        """
        return (self.sensor.reflection() - cfg.THRESHOLD) * cfg.SCALE

    def step(self):
        """Satu siklus kendali: baca, hitung, gerakkan, tunggu.

        Mengembalikan error terakhir supaya bisa dicatat oleh pemanggil.
        """
        error = self.error()

        if error > cfg.LOST_ERROR:
            self.lost_time = self.lost_time + cfg.LOOP_MS
        else:
            self.lost_time = 0

        if self.lost_time > cfg.LOST_MS:
            # Garis hilang. Sapu ke arah kesalahan terakhir, dan jangan
            # perbarui `last_error`, supaya arah sapuan tetap mengacu pada
            # keadaan sebelum garis hilang. Lihat bagian 8.
            if self.last_error > 0:
                self.robot.drive(0, cfg.LOST_TURN_RATE)
            else:
                self.robot.drive(0, -cfg.LOST_TURN_RATE)
        else:
            derivative = error - self.last_error
            correction = cfg.KP * error + cfg.KD * derivative
            self.robot.drive(self._speed_for(error), correction)
            self.last_error = error

        wait(cfg.LOOP_MS)
        return error

    def _speed_for(self, error):
        """Turunkan kecepatan saat simpangan membesar. Bagian 7."""
        speed = cfg.BASE_SPEED - (cfg.BASE_SPEED - cfg.MIN_SPEED) * abs(error) / 100.0
        if speed < cfg.MIN_SPEED:
            speed = cfg.MIN_SPEED
        return speed


def line_seen(sensor):
    """Benar kalau sensor melihat sesuatu yang lebih gelap dari lantai putih."""
    return sensor.reflection() < cfg.LINE_SEEN_REFLECTION


def find_line(robot, sensor, follower):
    """Cari garis lagi setelah robot berputar di depan dinding.

    Dua tahap, sesuai `pengikut-garis.md` bagian 8. Pertama maju pelan, karena
    tikungan biasanya ada tepat di depan robot. Kalau tidak ketemu, robot
    menyapu berputar dengan sudut yang makin melebar.

    Mengembalikan True kalau garis ketemu.
    """
    follower.reset()

    timer = StopWatch()
    robot.drive(cfg.REACQUIRE_SPEED, 0)
    while timer.time() < cfg.REACQUIRE_FORWARD_MS:
        if line_seen(sensor):
            robot.stop()
            follower.reset()
            return True
        wait(10)

    for duration in cfg.REACQUIRE_SWEEP_MS:
        if duration > 0:
            rate = cfg.REACQUIRE_TURN_RATE
        else:
            rate = -cfg.REACQUIRE_TURN_RATE

        timer.reset()
        robot.drive(0, rate)
        while timer.time() < abs(duration):
            if line_seen(sensor):
                robot.stop()
                follower.reset()
                return True
            wait(10)

    robot.stop()
    return False
