# 25 Oct – Insta360 × phone IMU

The phone's orientation (IMU) steers the view inside 360 footage from the Insta360, so a remote photographer can "point" the phone like a camera and look around the body double's 360 view.

```
phone (/phone)  --deviceorientation-->  server.js (wss relay)  -->  viewer (/)  --> yaw / pitch / roll on the 360 sphere
```

## Run

```bash
cd experiments/25oct-insta360
npm install
npm start
```

The terminal prints two URLs:

- **Viewer (laptop):** `https://localhost:8443/`
- **Phone:** `https://<laptop-ip>:8443/phone`. The phone has to be on the same Wi-Fi as the laptop.

Both pages use a self-signed certificate, so accept the browser warning once on each device. On iPhone that's *Show Details → visit this website*. Phones only expose motion sensors on HTTPS pages, which is why the server uses HTTPS.

On the phone, tap **Start sensors** (iOS will ask for motion permission). Hold the phone like you're taking a photo and tap **Recenter** to make that direction the front of the footage.

## 360 sources

- **Recorded footage:** export from Insta360 Studio as a **360° equirectangular** MP4 (2:1), then drop it on the viewer or use *Choose File*. Equirectangular stills also work.
- **Live:** put the Insta360 in **USB webcam mode** and pick it in *live camera*. The X3 sends its two raw lenses stacked top and bottom, and the viewer stitches them live in a shader. *Frame layout* switches to **Dual fisheye — top / bottom** automatically.

### Lens calibration (dual fisheye)

Tick **Show raw camera frame** to see what the camera is actually sending. Then:

1. Look straight ahead. If you see behind you instead, tick **Swap lenses**.
2. If the image is tilted or upside down, turn **Front lens rotation** / **Back lens rotation**. Usually it's 0, ±90 or 180.
3. Look 90° to the side, at the seam between the lenses. If objects are doubled or there's a gap, adjust **Lens field of view** (X3 ≈ 200°) and **Lens circle size** until they line up. **Seam blend** softens what's left.

The settings are saved in the browser.

Without footage loaded you get a labelled FRONT / LEFT / RIGHT / BACK grid for sanity-checking directions.

## Viewer controls

| | |
|---|---|
| Recenter (`R`, or the phone button) | current phone heading becomes the front of the footage |
| Heading offset | rotate which part of the footage counts as front |
| Smoothing | 0 = raw sensor, higher = calmer view (adds lag) |
| Lock roll | keeps the horizon level whatever the wrist does |
| Follow phone | turn off to drag with the mouse instead |
| Record IMU log | saves a CSV of `t_ms, yaw, pitch, roll, video_time_s, source` |
| `Space` / `H` / `F` | play-pause / hide panel / fullscreen |

## Conventions

- Yaw: + means turning left. Pitch: + means looking up. Roll: + means the phone is tilted counter-clockwise. All are in degrees, from a YXZ Euler decomposition, the same as three.js.
- The phone→view mapping follows three.js `DeviceOrientationControls`, so the view looks out of the **back** of the phone and compensates for portrait/landscape.
- Alpha (compass yaw) drifts on most phones and on iOS starts relative to wherever the page loaded. Recenter fixes both.

## Tested

Simulated phone poses fed through the relay into the viewer: upright → front 0/0/0, turn left 90° → yaw 90, tilt up 30° → pitch 30, 20° camera-axis roll → roll 20, recenter → back to 0. Not yet tried on a physical phone or with real Insta360 footage.

## Next ideas

- Send yaw/pitch/roll on to the wheeled base / gimbal (the server already has every orientation message).
- Show the photographer's view on the body double's side.
- Tag shutter moments in the log.
