# Shot Planner — phone booth + studio (scan 27 Oct 2026)

A dimensioned floorplan of the room, built from `room.glb` (the RoomPlan scan `10_27_2026.glb`). You use it to plan shots: each shot pins where the **model** stands and where the **camera** goes.

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

## Using it
1. Click **+ Add shot**. Then click the plan where the model stands (step 1), and click where the camera goes (step 2). The model turns to face the camera, and the camera aims at the model.
2. **Drag** a pin to move it. Drag the small round handle to rotate the model. To rotate the camera by hand, untick "Always point at the model" first.
3. In the side panel, set the model height, pose, lens height, focal length (full-frame), orientation, tilt and notes.
4. The readout gives the camera-to-model distance, the field of view, the frame size at the model, and whether the full body fits. It also warns when a pin overlaps furniture.
5. **Camera view** gives an approximate render of the frame from the pinned camera, using the scanned room.
6. **Shot sheet** opens print / save as PDF, with one page per shot (plan, measurements, camera view). **Export** / **Import** save and load all shots as JSON.

Shots are saved automatically in your browser's local storage. Use Export to keep them in the repo.

## Files
- `index.html`: the app
- `room.glb`: the original scan
- `room-glb.js`: the same scan embedded as base64, so the 3D view works when you open the file straight from disk
