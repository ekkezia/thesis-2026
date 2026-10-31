"""Prepare the outdoor scan (glb/56-bogart-outdoor.glb) for index.html.

Writes
  outdoor-glb.js                  the scan embedded as base64 (texture downscaled to 2048 px) so the 3D view
                                  works when index.html is opened straight from disk
  ref/56-bogart-scan-top.jpg      top-down orthophoto in plan coordinates (drawn under the floorplan)
  ref/56-bogart-scan-wall.jpg     the wall seen face-on from the sidewalk (the Reference image)

Scan → plan mapping (keep in sync with SCAN in index.html):
  plan x = scan z            (along the wall, left → right as you face it)
  plan z = WALL_X - scan x   (distance out from the wall face, toward the street)
  plan y = scan y - GROUND_Y (the scan is gravity-aligned, so no levelling)

usage: python3 scan-prep.py        (needs numpy + pillow)
"""
import base64, copy, io, json, struct
import numpy as np
from PIL import Image

SRC = "glb/56-bogart-outdoor.glb"
WALL_X = 3.32      # scan x of the mural's wall face (the skull-graffiti section sits ~15 cm further back)
GROUND_Y = -2.18   # scan y of the sidewalk, mid-way between wall and curb
TEX_MAX = 2048
RES = 0.02         # metres per pixel for the orthophotos

d = open(SRC, "rb").read()
jl = struct.unpack("<I", d[12:16])[0]
j = json.loads(d[20:20+jl]); b0 = 20+jl+8
bin_ = d[b0:b0+struct.unpack("<I", d[20+jl:24+jl])[0]]

def view(i):
    bv = j["bufferViews"][i]; o = bv.get("byteOffset", 0); return bin_[o:o+bv["byteLength"]]
def acc(i):
    a = j["accessors"][i]; n = {"SCALAR":1, "VEC2":2, "VEC3":3}[a["type"]]
    dt = {5126:np.float32, 5125:np.uint32, 5123:np.uint16}[a["componentType"]]
    r = np.frombuffer(view(a["bufferView"]), dt, a["count"]*n, a.get("byteOffset", 0)); return r.reshape(-1, n) if n > 1 else r
def image(i): return Image.open(io.BytesIO(view(j["images"][i]["bufferView"]))).convert("RGB")

# ---- embedded GLB with smaller textures ----
e = copy.deepcopy(j); views = [view(i) for i in range(len(j["bufferViews"]))]
for k, im in enumerate(e["images"]):
    pic = image(k)
    if max(pic.size) > TEX_MAX:
        pic.thumbnail((TEX_MAX, TEX_MAX), Image.LANCZOS)
        buf = io.BytesIO(); pic.save(buf, "JPEG", quality=85); views[im["bufferView"]] = buf.getvalue()
blob = b""
for i, v in enumerate(views):
    blob += b"\0" * (-len(blob) % 4)
    e["bufferViews"][i]["byteOffset"] = len(blob); e["bufferViews"][i]["byteLength"] = len(v); blob += v
blob += b"\0" * (-len(blob) % 4)
e["buffers"][0]["byteLength"] = len(blob)
js = json.dumps(e, separators=(",", ":")).encode(); js += b" " * (-len(js) % 4)
glb = struct.pack("<III", 0x46546C67, 2, 12+8+len(js)+8+len(blob)) + struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(blob), 0x004E4942) + blob
with open("outdoor-glb.js", "w") as f:
    f.write("// Embedded copy of glb/56-bogart-outdoor.glb (textures downscaled to %d px) so index.html works when opened\n" % TEX_MAX)
    f.write("// directly from disk (no server). Regenerate with scan-prep.py.\n")
    f.write('window.OUTDOOR_GLB_B64="%s";\n' % base64.b64encode(glb).decode())
print("outdoor-glb.js  %.1f MB (glb %.1f MB)" % (len(glb)*4/3/1e6, len(glb)/1e6))

# ---- orthophotos: splat points sampled on every triangle into a z-buffer ----
rng = np.random.default_rng(0); pts = []; cols = []
for m in j["meshes"]:
    p = m["primitives"][0]
    V = acc(p["attributes"]["POSITION"]).astype(np.float64); UV = acc(p["attributes"]["TEXCOORD_0"]).astype(np.float64)
    I = acc(p["indices"]).reshape(-1, 3)
    tex = np.asarray(image(j["textures"][j["materials"][p["material"]]["pbrMetallicRoughness"]["baseColorTexture"]["index"]]["source"]))
    a, b, c = V[I[:,0]], V[I[:,1]], V[I[:,2]]
    n = np.clip((np.linalg.norm(np.cross(b-a, c-a), axis=1)/2/(RES*0.45)**2).astype(int), 1, 4000)
    t = np.repeat(np.arange(len(I)), n); r1 = np.sqrt(rng.random(len(t))); r2 = rng.random(len(t))
    w = np.c_[1-r1, r1*(1-r2), r1*r2]
    pts.append(np.einsum("nk,nkd->nd", w, V[I[t]])); T = np.einsum("nk,nkd->nd", w, UV[I[t]])
    h, wd, _ = tex.shape
    cols.append(tex[np.clip(((T[:,1] % 1)*h).astype(int), 0, h-1), np.clip(((T[:,0] % 1)*wd).astype(int), 0, wd-1)])
P = np.vstack(pts); C = np.vstack(cols)
X, Y, Z = P[:,2], P[:,1]-GROUND_Y, WALL_X-P[:,0]     # plan coordinates

def ortho(u, v, near, mask, name, bg=255):
    u, v, near, c = u[mask], v[mask], near[mask], C[mask]
    u0, v0 = np.floor(u.min()/RES)*RES, np.floor(v.min()/RES)*RES
    iu = ((u-u0)/RES).astype(int); iv = ((v-v0)/RES).astype(int); W, H = iu.max()+1, iv.max()+1
    o = np.lexsort((-near, iv*W+iu)); k = (iv*W+iu)[o]; first = np.r_[True, k[1:] != k[:-1]]
    im = np.full((H*W, 3), bg, np.uint8); im[k[first]] = c[o][first]
    Image.fromarray(im.reshape(H, W, 3)).save(name, quality=82)
    print("%s  x %.2f → %.2f, %s %.2f → %.2f" % (name, u0, u0+W*RES, "z" if "top" in name else "-y", v0, v0+H*RES))

ortho(X, Z, Y, np.ones(len(X), bool), "ref/56-bogart-scan-top.jpg", bg=128)   # seen from above; grey = not scanned
ortho(X, -Y, -Z, (Z < 0.8) & (X < 5), "ref/56-bogart-scan-wall.jpg")                  # the wall, seen from the sidewalk
