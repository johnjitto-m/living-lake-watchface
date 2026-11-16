# Installing Living Lake

Watch faces from outside the Play Store are installed over Wi-Fi with **adb** (Android Debug Bridge). There are two ways to do it:

- **[Option A – phone only](#option-a--phone-only-no-computer)**: an Android phone and a free app. Easiest.
- **[Option B – computer](#option-b--computer-windows-macos-linux)**: Windows, macOS or Linux with adb.

Either way, the phone or computer must be on the **same Wi-Fi** as your watch.

**Your watch needs Wear OS 6 or newer** (on Samsung: One UI 8 Watch). Check under Settings › About watch › Software information.

## Prepare the watch (one time, both options)

1. Connect the watch to **Wi-Fi** (Settings › Connections › Wi-Fi). Set Wi-Fi to **On**, not Auto.
2. **Unlock Developer options:** Settings › About watch › Software information → tap **Software version** about 7 times.
3. Settings › **Developer options** → turn on **ADB debugging** and **Wireless debugging**.

Keep the watch screen on while you install: the watch drops off Wi-Fi when it goes to sleep.

---

## Option A – phone only (no computer)

1. On your phone, install **[Bugjaeger Mobile ADB](https://play.google.com/store/apps/details?id=eu.sisik.hackendebug)** from the Play Store.
2. On your phone, download **`LivingLake-watchface-v1.7.apk`** from the [latest release](https://github.com/johnjitto-m/living-lake-watchface/releases/latest).
3. On the watch: **Wireless debugging › Pair new device**. It shows a **6-digit code** and an **IP:port**.
4. In Bugjaeger: tap the connect/pair option for wireless debugging, enter that IP, port and code, and pair. Then connect to the watch.
5. In Bugjaeger, open the **Packages** tab → tap **+** (install) → pick the APK you downloaded. Wait for it to finish.
6. Jump to **[Use it](#use-it)**.

**Pairing keeps failing?** Codes expire fast, so tap *Pair new device* again and enter the new code right away. Some people also need to turn **Bluetooth off on the watch** while pairing, then back on afterwards.

---

## Option B – computer (Windows, macOS, Linux)

### 1. Install adb

| System | How |
|---|---|
| **Windows** | Download [Platform Tools](https://developer.android.com/tools/releases/platform-tools), unzip, open a terminal in that folder (use `.\adb` instead of `adb`) |
| **macOS** | `brew install android-platform-tools` (or download Platform Tools) |
| **Linux** | Download [Platform Tools](https://developer.android.com/tools/releases/platform-tools) and unzip it (for example into your home folder, then use `~/platform-tools/adb`). Distribution packages can be too old to pair: if pairing says *protocol fault*, use Google's Platform Tools |

Check it works: `adb version`

### 2. Pair and connect

1. On the watch: **Wireless debugging › Pair new device**. Note the **6-digit code** and **IP:port**.
2. On the computer:
   ```bash
   adb pair 192.168.1.42:41235 123456     # your pairing IP:port and code
   ```
3. Back out one screen on the watch. The main Wireless debugging screen shows **another IP:port** (the port changes every time):
   ```bash
   adb connect 192.168.1.42:37011          # your connect IP:port
   adb devices                              # watch should show as "device"
   ```

### 3. Install

```bash
adb -s 192.168.1.42:37011 install -r LivingLake-watchface-v1.7.apk     # same IP:port as in "connect"
```
Wait for **Success**.

---

## Use it

Touch and hold your watch face → swipe left → **+ Add watch face** → **Living Lake**.
On a Galaxy Watch you can also pick it in the **Galaxy Wearable** app on your phone → Watch faces.
Give it a few seconds after the first install while it loads the artwork.

Touch and hold → **Customize** to turn heart rate, lake life or the drooping tree on and off, and to fill the two edge bars.

**Turn Wireless debugging off** when you're done: it uses battery.

## Updating

Install the new APK the same way. It replaces the old version and keeps it selected.

## Troubleshooting

| Message | What to do |
|---|---|
| **No route to host** | The watch is off Wi-Fi. Wake it, check Wi-Fi is connected, or briefly turn off Bluetooth on your phone so the watch stays on Wi-Fi |
| **Connection refused** / **device not found** | The port changed. Read the IP:port on the Wireless debugging screen again and use the same one in both `connect` and `install` |
| **more than one device** | Add `-s IP:port` after `adb`, as in the install command above |
| **protocol fault** (when pairing) | Your adb is too old. Use the latest Platform Tools from Google |
| **Steps tree never grows** | Set a daily step target in Samsung Health / your fitness app |
| **No weather** | Make sure location and the weather app are set up on your phone and watch |

**Uninstall:** in Bugjaeger's **Packages** tab, or on a computer run `adb uninstall com.livinglake.watchface`.
