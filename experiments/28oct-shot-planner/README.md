# Shot Planner — phone booth + studio (scan 27 Oct 2026)

A dimensioned floorplan of the room, built from `glb/room.glb` (the RoomPlan scan `10_27_2026.glb`). You use it to plan shots: each shot pins where the **model** stands and where the **camera** goes.

**Open `index.html` in a browser.** There's nothing to install and no server to run. The 3D camera view loads three.js from a CDN, so it needs internet the first time. The floorplan works offline.

## Room (interior, from the scan)
| | |
|---|---|
| Interior | 3.12 m × 2.12 m (10′ 3″ × 6′ 11″) |
| Ceiling | 2.54 m |
| Door / glass front | 2.99 m wide, 2.51 m high, along the front wall |
| Table | 1.42 m × 0.85 m, 0.76 m high |
| Other furniture | 4 chairs, 1 shelf on the left wall |

Plan coordinates are in metres. The origin is the room centre, x points right and z points toward the door. The editor shows positions as distances **from the left wall** and **from the back wall**, which you can measure with a tape on set.

## Outdoor: mural wall at 56 Bogart St (scan 31 Oct 2026)
`glb/56-bogart-outdoor.glb` is a LiDAR scan of the wall: skull graffiti on corrugated metal (left) and the Hershey's mural (right). Only the wall side could be scanned, because parked cars blocked the street side, so the scan is patchy past the curb.

| | |
|---|---|
| Planning area (crop) | 13.35 m along the wall × 6.45 m out from it |
| Wall | skull graffiti 6.0 m long (scanned only up to about 2–3 m high) + Hershey's mural 7.35 m long, 5.7 m high |
| Sidewalk | 4.45 m from the wall to the curb, about 12 cm curb, slopes about 20 cm down toward the curb |
| Parking lane | the 2 m strip past the curb (`ROAD_STRIP`) |
| Obstacles | tree pit with shrubs along the curb (6.1 × 1.6 m), a low round object (35 cm) near the left end |

On the outdoor plan, "from back wall" means the distance from the wall face, and "from left wall" means the distance along the wall from the left end of the skull graffiti. The crop is `ROOMS.outdoor.interior` in `index.html`. For a tighter set on the mural only, change `x0` to `-3.0`, which makes the area 7.35 m wide. The 3D views always show the whole scan.

After a rescan, replace the GLB and run `python3 scan-prep.py` (it needs numpy and pillow). This regenerates `outdoor-glb.js` and the two `ref/56-bogart-scan-*.jpg` renders. If the wall or ground moved, update `WALL_X` and `GROUND_Y` in the script and in `ROOMS.outdoor.scan`.

## Using it
1. Click **+ Add shot**. Then click the plan where the model stands (step 1), and click where the camera goes (step 2). The model turns to face the camera, and the camera aims at the model.
2. **Drag** a pin to move it. Drag the small round handle to rotate the model. To rotate the camera by hand, untick "Always point at the model" first.
3. In the side panel, set the model height, pose, lens height, focal length (full-frame), orientation, tilt and notes.
4. The readout gives the camera-to-model distance, the field of view, the frame size at the model, and whether the full body fits. It also warns when a pin overlaps furniture.
5. **Camera view** gives an approximate render of the frame from the pinned camera, using the scanned room.
   **Plan / 3D** (top bar) switches the main view to a 3D view of the location that you can orbit (drag), pan (right-drag) and zoom (scroll). It shows every shot's model, camera and field of view. Pins are placed and moved on the plan.
6. **Shot sheet** opens print / save as PDF, with one page per shot (plan, measurements, camera view). **Export** / **Import** save and load all shots as JSON.

Shots are saved automatically in your browser's local storage. Use Export to keep them in the repo.

## Files
- `index.html`: the app
- `glb/room.glb`: the original booth scan
- `room-glb.js`: the same scan embedded as base64, so the 3D view works when you open the file straight from disk
- `glb/56-bogart-outdoor.glb`: the original outdoor scan
- `outdoor-glb.js`: the outdoor scan embedded as base64 (textures downscaled to 2048 px)
- `ref/56-bogart-scan-top.jpg`, `ref/56-bogart-scan-wall.jpg`: top-down and face-on renders of the scan (the outdoor plan background and the Reference image)
- `scan-prep.py`: builds the three outdoor files above from the GLB
