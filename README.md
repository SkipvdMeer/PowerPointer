# Slide Remote

**Turn your phone into a presentation clicker. Leave the USB dongle wherever you usually forget it.**

A while ago, I had to give a presentation. Once again, I'd forgotten the little adapter that gives my Mac a USB port. Which meant my clicker was useless, and I got to spend the presentation standing behind my laptop instead of walking around and talking with my hands.

The reasonable thing to do would have been to keep the adapter in my bag. Or put a reminder in my Teams calendar.

So naturally, I wrote an entire program.

Slide Remote runs on your Mac or Windows PC and shows a QR code. Scan it with your phone, and your browser becomes the clicker. No phone app, account, or cloud service involved.

Forgetful? Like cool stuff? Welcome.

## What it does

- **Next and back:** tap the big yellow area to advance. Swipe right or tap Back for the previous slide.
- **Blank:** toggle a black screen when you want people to look at you. A bold move, but sometimes necessary.
- **Laser / pointer:** toggle your presentation's laser mode, then drag on the phone to move the laptop's mouse pointer.
- **Start, From here, End:** control the slideshow without making the walk of shame back to your laptop.
- **Timer:** starts when you advance or start the show. Tap the timer to reset it.
- **Slide counter:** keeps track of the slides you advance through on the phone.

The app sends keyboard shortcuts and mouse movements to the **currently focused application**. PowerPoint is the main target. Other presentation apps may support some of the same shortcuts, but aren't guaranteed to support every button.

The slide counter is an estimate based on your phone's actions; it doesn't read your presentation. Keyboard clicks, skipped slides, animations, and reconnecting can put it out of sync.

## Get started

Download this repository using **Code → Download ZIP** on GitHub and extract it, or clone it. Build the desktop app on the computer you'll present from. Python is needed to build it; the resulting app includes its own Python runtime.

### Mac

1. Install Python 3 with Tk support. The installer from [python.org](https://www.python.org/downloads/macos/) is a straightforward option.
2. Open the extracted project folder and double-click **`build_mac.command`**. You can also run `bash build_mac.command` in Terminal from that folder.
3. The script creates a local `.venv`, installs the dependencies, builds **Slide Remote.app**, and copies it to `/Applications` (or `~/Applications` if necessary).
4. Open **System Settings → Privacy & Security → Accessibility**. Add Slide Remote and enable it so it can send keyboard and mouse input. Quit and reopen the app afterward.
5. Open Slide Remote from Applications.

This is a locally built app that is not notarized by Apple. If macOS blocks it, use the system's **Open Anyway** option in Privacy & Security after reviewing the source. A rebuild may require granting Accessibility permission again.

### Windows

1. Install Python 3 from [python.org](https://www.python.org/downloads/), with **Add Python to PATH** enabled.
2. Open the extracted project folder and double-click **`build_windows.bat`**.
3. The script creates a local `.venv`, installs the dependencies, and builds `dist\Slide Remote.exe`. It also creates Desktop and Start menu shortcuts.
4. Open Slide Remote using either shortcut. Keep the project folder where it is: the shortcuts point to the executable inside it.
5. If Windows Firewall asks, allow access on **Private networks** for your trusted Wi-Fi or hotspot.

Build on Windows for the Windows app, and on macOS for the Mac app. The first build needs internet access to download the Python packages. If a build fails, check `build.log` in the project folder.

## Present without being attached to your laptop

1. Connect your phone and computer to the **same Wi-Fi network**, or a hotspot that lets them communicate.
2. Open Slide Remote on your computer.
3. Scan the QR code with your phone's camera and open the link in its browser. No installation on the phone.
4. Open your presentation and click into it so it receives keyboard input.
5. Start the slideshow and use your phone to control it.

Keep the phone page open and the screen awake while presenting. Automatic screen wake support depends on the browser and may be unavailable over the local HTTP connection.

**New code** disconnects the previous pairing links. **Copy link** gives you the address if scanning isn't convenient. If the desktop app offers a Wi-Fi **(switch)** button, use it to try another detected network address, then scan again.

## How it works

The desktop app starts a small HTTP server on your computer, normally on port **8765**. If that port is busy, it tries up to **8784**. The QR code contains a local address and a randomly generated pairing token.

Your phone loads the remote page from that server and sends button presses back to it. Python and PyAutoGUI turn those requests into keyboard shortcuts and mouse movements. Tkinter draws the desktop window; Pillow and qrcode handle the images and QR code.

The presentation stays on your computer. The app doesn't upload your slides or use a cloud backend. Once built, it only needs a working local connection between the phone and computer.

### Keyboard shortcuts

| Control | Mac | Windows |
| --- | --- | --- |
| Next / Back | Right / Left arrow | Right / Left arrow |
| Blank | B | B |
| Laser | Command + L | Ctrl + L |
| Start | Command + Shift + Enter | F5 |
| From here | Command + Enter | Shift + F5 |
| End | Escape | Escape |

Shortcut support depends on the presentation app. The pointer moves your actual mouse, and all shortcuts go to the active window, so make sure your slides have focus.

## A small security note

Treat the QR code and link like a temporary remote-control password. Anyone who has the current link and can reach your computer can send the supported keyboard and mouse commands. Don't include a live code in public screenshots or your presentation.

Use a trusted network. The server listens on all IPv4 interfaces and uses **unencrypted HTTP**, so this is intended for local use. Don't port-forward it to the internet. A fresh token is created when you launch the app or click **New code**; closing the desktop app stops the remote.

## Run from source

If you'd rather skip building an app, create an environment and run the script directly.

**Mac:**

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python SlideRemote.pyw
```

Grant Accessibility permission to the application running Python, such as Terminal, if input doesn't work.

**Windows (Command Prompt):**

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe SlideRemote.pyw
```

To use a different starting port, append `--port 9000` to the run command.

## When the room's Wi-Fi has other plans

- **The QR link won't open:** check that both devices are on the same network. Guest and conference Wi-Fi can block connections between devices; try a trusted hotspot instead. Check your firewall and try the Wi-Fi switch button if available.
- **Connected, but nothing happens:** click your presentation window. On Mac, check Accessibility permission and restart the app.
- **Some buttons work, others don't:** your presentation app may use different shortcuts. Check the table above.
- **The phone says to scan again:** the desktop app was restarted or someone clicked New code. Scan the current QR code.
- **The timer or slide counter looks wrong:** these are tracked in the phone page, not read from the presentation. Reloading the page resets them.

## Project files

- `SlideRemote.pyw` — desktop app, local server, and phone interface.
- `build_mac.command` / `build_windows.bat` — build and install helpers.
- `requirements.txt` / `requirements-build.txt` — runtime and build dependencies.
- `icon.icns` / `icon.ico` — desktop app icons.
- `Slide Remote.spec` — existing macOS PyInstaller configuration; the build helpers generate their own configuration under `build/`.

Generated apps, build files, logs, and local environments are excluded by `.gitignore`. Share source through the repository; packaged apps can be distributed separately as release downloads.

## Development checks

Run the server regression tests without opening the GUI or sending keyboard input:

```sh
python -m unittest discover -s tests -v
```

The tests cover authentication, token rotation, malformed requests, request size limits, and pointer movement bounds. Desktop permissions, actual slideshow behavior, and packaged apps still need testing on each operating system.

Built by a person who could have just packed an adapter.
