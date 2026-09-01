#!/usr/bin/env python3
"""Draw the opacity-micromap classification for a real cutout triangle from the test scene.

Section 3.3 explains micromaps in prose: a cutout triangle is subdivided, each microtriangle is
classified opaque / transparent / unknown against the material's alpha, and traversal then resolves
the first two in hardware so the any-hit alpha test runs only on the third. That is a spatial idea
and hard to hold from a paragraph, so this renders it.

Nothing here is drawn by hand. The alpha comes from the scene's own cutout texture, the triangle is a
real triangle of the Sponza mesh with that material (UVs read out of the glTF buffer), and the
classification repeats OmmBake.comp exactly: SamplesPerEdge = 4 << level barycentric samples, a
sample is opaque at alpha >= cutoff, and a microtriangle is OPAQUE or TRANSPARENT only if every
sample in it agrees, mixed or unsampled falling to UNKNOWN_OPAQUE (conservative, so the any-hit test
resolves it and the extension never changes what a ray finds).

Writes latex/figures/omm_classify.png and prints the state counts the caption quotes.

    py gen_omm_figure.py [--material 20] [--triangle auto]
"""
import argparse
import base64
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image

THESIS_DIR = Path(__file__).resolve().parents[1]
ENGINE = THESIS_DIR.parent / "Snowstorm-Engine"
MESH_DIR = ENGINE / "Projects/Sandbox/assets/meshes/Sponza"
GLTF = MESH_DIR / "Sponza.gltf"
OUT = THESIS_DIR / "latex" / "figures" / "omm_classify.png"

# TlasBuildSystem.cpp:130 kOmmSubdivisionLevel, and VulkanMicromap.cpp:213 SamplesPerEdge.
LEVEL = 3
SAMPLES_PER_EDGE = 4 << LEVEL
CUTOFF = 0.5

COMP_SIZE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
COMP_FMT = {5121: "B", 5123: "H", 5125: "I", 5126: "f"}
NUM_COMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}


def read_accessor(gltf, buffers, index):
    acc = gltf["accessors"][index]
    view = gltf["bufferViews"][acc["bufferView"]]
    data = buffers[view.get("buffer", 0)]
    n = NUM_COMP[acc["type"]]
    csize = COMP_SIZE[acc["componentType"]]
    stride = view.get("byteStride") or n * csize
    base = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    fmt = COMP_FMT[acc["componentType"]]
    out = np.empty((acc["count"], n), dtype=np.float64 if fmt == "f" else np.int64)
    for i in range(acc["count"]):
        off = base + i * stride
        out[i] = struct.unpack_from("<" + fmt * n, data, off)
    return out


def micro_index(u, v, level):
    """Which microtriangle a barycentric sample lands in, as (iu, iv, inverted).

    Uniform subdivision: scale by 2^level, the integer part picks the cell and the fractional parts
    decide which half of it. 4^level microtriangles per triangle, matching the bake.
    """
    n = 1 << level
    fu, fv = u * n, v * n
    iu, iv = np.floor(fu).astype(int), np.floor(fv).astype(int)
    iu = np.clip(iu, 0, n - 1)
    iv = np.clip(iv, 0, n - 1)
    inverted = (fu - iu) + (fv - iv) > 1.0
    return iu, iv, inverted


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--material", type=int, default=None, help="glTF material index (default: pick one)")
    args = ap.parse_args()

    gltf = json.loads(GLTF.read_text(encoding="utf-8"))
    buffers = []
    for b in gltf["buffers"]:
        uri = b["uri"]
        if uri.startswith("data:"):
            buffers.append(base64.b64decode(uri.split(",", 1)[1]))
        else:
            buffers.append((MESH_DIR / uri).read_bytes())

    masks = [i for i, m in enumerate(gltf["materials"]) if m.get("alphaMode") == "MASK"]
    if not masks:
        print("FAIL: no MASK material in the glTF")
        return 1
    mat_i = args.material if args.material is not None else masks[0]
    mat = gltf["materials"][mat_i]
    cutoff = float(mat.get("alphaCutoff", CUTOFF))
    tex_i = mat["pbrMetallicRoughness"]["baseColorTexture"]["index"]
    img_uri = gltf["images"][gltf["textures"][tex_i]["source"]]["uri"]
    alpha = np.asarray(Image.open(MESH_DIR / img_uri).convert("RGBA"))[..., 3].astype(np.float64) / 255.0
    th, tw = alpha.shape

    prim = next((p for m in gltf["meshes"] for p in m["primitives"] if p.get("material") == mat_i), None)
    if prim is None:
        print(f"FAIL: no primitive uses material {mat_i}")
        return 1
    uvs = read_accessor(gltf, buffers, prim["attributes"]["TEXCOORD_0"])
    idx = read_accessor(gltf, buffers, prim["indices"]).reshape(-1, 3)

    # Pick the triangle whose UV footprint straddles the alpha boundary most evenly, which is the one
    # that actually exercises all three states. A triangle wholly inside or outside shows nothing.
    best, best_score = None, -1.0
    for t in idx[: min(len(idx), 4000)]:
        tri_uv = uvs[t]
        cu, cv = tri_uv[:, 0].mean(), tri_uv[:, 1].mean()
        px, py = int(cu % 1.0 * tw), int(cv % 1.0 * th)
        r = 24
        patch = alpha[max(0, py - r):py + r, max(0, px - r):px + r]
        if patch.size == 0:
            continue
        frac = (patch >= cutoff).mean()
        e1, e2 = tri_uv[1] - tri_uv[0], tri_uv[2] - tri_uv[0]
        area = abs(e1[0] * e2[1] - e1[1] * e2[0]) / 2
        score = min(frac, 1 - frac) * (1.0 if area > 1e-5 else 0.0)
        if score > best_score:
            best_score, best = score, tri_uv
    if best is None:
        print("FAIL: no usable triangle")
        return 1
    tri_uv = best

    # Bake: SamplesPerEdge^2 barycentric samples, OR'd into a per-microtriangle accumulator.
    n = 1 << LEVEL
    acc = {}
    s = SAMPLES_PER_EDGE
    for a in range(s + 1):
        for b in range(s + 1 - a):
            u, v = a / s, b / s
            w = 1.0 - u - v
            uv = tri_uv[0] * w + tri_uv[1] * u + tri_uv[2] * v
            px = int(np.clip(uv[0] % 1.0 * (tw - 1), 0, tw - 1))
            py = int(np.clip(uv[1] % 1.0 * (th - 1), 0, th - 1))
            iu, iv, inv = micro_index(np.array([u]), np.array([v]), LEVEL)
            key = (int(iu[0]), int(iv[0]), bool(inv[0]))
            bit = 1 if alpha[py, px] >= cutoff else 2
            acc[key] = acc.get(key, 0) | bit

    # Classify exactly as the bake does.
    states = {}
    for iu in range(n):
        for iv in range(n - iu):
            for inv in (False, True):
                if inv and iu + iv >= n - 1:
                    continue
                a = acc.get((iu, iv, inv), 0)
                states[(iu, iv, inv)] = 1 if a == 1 else (0 if a == 2 else 3)

    counts = {0: 0, 1: 0, 3: 0}
    for st in states.values():
        counts[st] += 1
    total = sum(counts.values())
    print(f"material {mat_i}, cutoff {cutoff}, level {LEVEL} -> {total} microtriangles")
    print(f"  OPAQUE          {counts[1]:>3}")
    print(f"  TRANSPARENT     {counts[0]:>3}")
    print(f"  UNKNOWN (any-hit){counts[3]:>3}")
    hw = counts[0] + counts[1]
    print(f"  resolved in hardware: {hw}/{total} = {hw / total * 100:.0f}%")

    _render(alpha, tri_uv, states, n, OUT, cutoff)
    print(f"wrote {OUT}")

    # The caption quotes these four, so they are generated rather than typed: the figure and its
    # numbers come out of one run and cannot drift apart.
    macros = THESIS_DIR / "latex" / "data" / "omm-macros.tex"
    macros.write_text(
        f"\\newcommand{{\\ommTotal}}{{{total}}}\n"
        f"\\newcommand{{\\ommOpaque}}{{{counts[1]}}}\n"
        f"\\newcommand{{\\ommTransparent}}{{{counts[0]}}}\n"
        f"\\newcommand{{\\ommUnknown}}{{{counts[3]}}}\n"
        f"\\newcommand{{\\ommHwPct}}{{{hw / total * 100:.0f}}}\n", encoding="utf-8")
    print(f"wrote {macros}")
    return 0


def _render(alpha, tri_uv, states, n, out_path, cutoff):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.2, 4.4))

    th, tw = alpha.shape
    verts = np.column_stack([tri_uv[:, 0] % 1.0 * tw, tri_uv[:, 1] % 1.0 * th])
    pad = max(30, np.ptp(verts[:, 0]) * 0.25, np.ptp(verts[:, 1]) * 0.25)
    x0, x1 = int(max(0, verts[:, 0].min() - pad)), int(min(tw, verts[:, 0].max() + pad))
    y0, y1 = int(max(0, verts[:, 1].min() - pad)), int(min(th, verts[:, 1].max() + pad))

    # Both panels are the SAME crop in texture space with the SAME triangle, so the classification on
    # the right can be read directly against the alpha boundary on the left.
    for ax in (axL, axR):
        ax.imshow(alpha[y0:y1, x0:x1] >= cutoff, cmap="Greys_r", interpolation="nearest",
                  extent=[x0, x1, y1, y0])
        ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
        ax.set_xticks([]); ax.set_yticks([])
    axL.add_patch(Polygon(verts, closed=True, fill=False, edgecolor="#d62728", lw=2.0))
    axL.set_title("cutout alpha, thresholded, with one mesh triangle", fontsize=9)

    col = {1: "#3a3a3a", 0: "#ffffff", 3: "#e8a33d"}
    for (iu, iv, inv), st in states.items():
        bary = ([(iu, iv), (iu + 1, iv), (iu, iv + 1)] if not inv
                else [(iu + 1, iv), (iu + 1, iv + 1), (iu, iv + 1)])
        pts = [verts[0] * (1 - a / n - b / n) + verts[1] * (a / n) + verts[2] * (b / n)
               for a, b in bary]
        axR.add_patch(Polygon(pts, closed=True, facecolor=col[st], edgecolor="#8c8c8c", lw=0.35,
                              alpha=0.95))
    axR.set_title(f"its {len(states)} microtriangles, classified", fontsize=9)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=col[k], edgecolor="#8c8c8c")
               for k in (1, 0, 3)]
    axR.legend(handles, ["opaque: hardware", "transparent: hardware", "unknown: any-hit test"],
               loc="lower left", fontsize=8, framealpha=0.9)

    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
