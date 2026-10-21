"""Meshing for the SynRM cross-section.

Uses a polar grid with uniform angular resolution, classifying elements by
centroid. High angular resolution in critical regions to minimize classification
error. Elements are triangulated as two triangles per quad.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from synrm_geometry import SynRMGeometry

SHAFT, ROTOR, BARRIER = "shaft", "rotor_iron", "barriers"
GAP, STATOR, SLOTS, AIR = "airgap", "stator_iron", "slots", "air"


def slot_angles(g: SynRMGeometry):
    r_bore = g.stator_bore / 2
    depth = 0.18 * r_bore if g.slot_depth is None else g.slot_depth
    a_open = math.asin(min(1.0, (g.slot_opening / 2) / r_bore))
    half_bot = (2 * math.pi / g.n_slots) / 2 * 0.55
    return r_bore, depth, a_open, half_bot


def barrier_bands(g: SynRMGeometry):
    r_ro = g.rotor_od / 2
    zone_out = r_ro - g.bridge
    t = g.barrier_radial_span * (1 - g.barrier_gap_frac) / g.n_barriers
    gap = (g.barrier_radial_span * g.barrier_gap_frac / (g.n_barriers - 1)
           if g.n_barriers > 1 else 0.0)
    out = []
    for j in range(g.n_barriers):
        r_o = zone_out - j * (t + gap)
        out.append((r_o - t, r_o))
    return list(reversed(out))


def _in_barrier(g: SynRMGeometry, x: float, y: float) -> bool:
    r = math.hypot(x, y)
    pole_pitch = 2 * math.pi / g.rotor_n_poles   # rotor-period basis for BOTH the
    a = math.atan2(y, x) % pole_pitch            # period and barrier width, so a
    c = g.barrier_center_angle % pole_pitch      # wrapped centre dist handles
    half_span = (g.barrier_angle_frac * pole_pitch) / 2  # centres in any window
    d = abs(a - c) % pole_pitch                  # barrier may straddle a=0 seam
    if min(d, pole_pitch - d) > half_span:
        return False
    for r_i, r_o in barrier_bands(g):
        if r_i < r <= r_o:
            return True
    return False


def _in_slot(g: SynRMGeometry, x: float, y: float) -> bool:
    r = math.hypot(x, y)
    r_bore, depth, a_open, half_bot = slot_angles(g)
    if r < r_bore or r >= r_bore + depth:
        return False
    pitch = 2 * math.pi / g.n_slots
    # stator_profile centres slot k's notch at angle k*pitch (mod pitch: a=0),
    # so distance to the nearest slot centre is min(a, pitch - a). (The old
    # version tested |a - pitch/2|, i.e. slots at (k+0.5)*pitch -- a half-pitch
    # mismatch that silently rotated the applied MMF by half a slot pitch and
    # made every d/q "alignment" torque nonzero. Found 2026-10-20 via the
    # anchor smoke run: T(d-alignment) was ~70% of peak instead of ~0.)
    a = math.atan2(y, x) % pitch
    frac = (r - r_bore) / depth
    half = a_open + (half_bot - a_open) * frac
    return min(a, pitch - a) <= half


def classify_point(g: SynRMGeometry, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    x = np.atleast_1d(np.asarray(x, float))
    y = np.atleast_1d(np.asarray(y, float))
    r = np.hypot(x, y)
    r_sh = g.shaft_od / 2
    r_ro = g.rotor_od / 2
    r_bore, depth, _, _ = slot_angles(g)
    r_out = g.stator_od / 2
    r_dom = 1.18 * r_out
    
    out = np.empty(x.shape, dtype=object)
    out[:] = AIR
    out[(r >= r_out) & (r < r_dom)] = AIR
    out[(r >= r_bore) & (r < r_out)] = STATOR
    out[(r < r_bore) & (r >= r_ro)] = GAP
    out[(r < r_ro) & (r >= r_sh)] = ROTOR
    out[r < r_sh] = SHAFT
    
    # slots in stator band
    in_slot_band = (r >= r_bore) & (r < r_bore + depth)
    mask = in_slot_band
    for i in np.where(mask)[0]:
        if _in_slot(g, float(x[i]), float(y[i])):
            out[i] = SLOTS
        else:
            out[i] = STATOR
    
    # barriers in rotor
    for i in np.where((r >= r_sh) & (r < r_ro))[0]:
        if _in_barrier(g, float(x[i]), float(y[i])):
            out[i] = BARRIER
    return out


def expected_areas(g: SynRMGeometry) -> dict[str, float]:
    r_sh = g.shaft_od / 2
    r_ro = g.rotor_od / 2
    r_bore, depth, a_open, half_bot = slot_angles(g)
    r_out = g.stator_od / 2
    r_dom = 1.18 * r_out
    rs = np.linspace(r_bore, r_bore + depth, 4000)
    frac = (rs - r_bore) / depth
    slot = g.n_slots * np.trapezoid(2 * (a_open + (half_bot - a_open) * frac) * rs, rs)
    half_span = (g.barrier_angle_frac * 2 * math.pi / g.rotor_n_poles) / 2
    bar = 0.0
    for r_i, r_o in barrier_bands(g):
        bar += 2 * half_span * (r_o ** 2 - r_i ** 2) * (g.rotor_n_poles / 2)
    return {
        SHAFT: math.pi * r_sh ** 2,
        ROTOR: math.pi * (r_ro ** 2 - r_sh ** 2) - bar,
        BARRIER: bar,
        GAP: math.pi * (r_bore ** 2 - r_ro ** 2),
        SLOTS: slot,
        STATOR: math.pi * (r_out ** 2 - r_bore ** 2) - slot,
        AIR: math.pi * (r_dom ** 2 - r_out ** 2),
    }


def build_mesh(g: SynRMGeometry, *, n_r=30, n_theta=768, n_gap_rows=2):
    """Polar-grid mesh of the machine cross-section.

    n_theta     number of uniformly spaced rays (all rings share them)
    n_gap_rows  element rows across the airgap (>=2); extra rows reduce the                element-wise-constant-B noise floor of the Maxwell torque
                integral, which samples element jumps inside the gap

    Rays are *aligned* to the slot and barrier boundary angles: a material
    edge lying exactly on a ray means element centroids never straddle it, so
    region assignment carries no staircase error at those edges. Without this
    the barrier effective width stair-steps with rotor rotation and the
    extracted torque is untrustworthy at the percent level.
    """
    from skfem import MeshTri
    r_sh = g.shaft_od / 2
    r_ro = g.rotor_od / 2
    r_bore, depth, a_open, half_bot = slot_angles(g)
    r_out = g.stator_od / 2
    r_dom = 1.18 * r_out
    pitch = 2 * math.pi / g.n_slots
    
    # rays: uniform base grid + material-boundary angles (slot edges, barrier
    # edges), merged; very close rays are dropped to avoid slivers
    base = 2 * math.pi * np.arange(n_theta) / n_theta
    extra = []
    for k in range(g.n_slots):
        c = k * pitch
        extra += [c - a_open, c + a_open, c - half_bot, c + half_bot]
    for k in range(g.rotor_n_poles):
        c = k * 2 * math.pi / g.rotor_n_poles + g.barrier_center_angle
        hs = (g.barrier_angle_frac * 2 * math.pi / g.rotor_n_poles) / 2
        extra += [c - hs, c + hs]
    th_ray = np.unique(np.concatenate([base, np.mod(np.array(extra), 2 * math.pi)]))
    th_ray = th_ray[np.r_[True, np.diff(th_ray) > 1e-4]]
    
    # radial breaks - refined in rotor/barrier bands
    r = np.concatenate([
        np.linspace(0, r_sh, 4),
        np.linspace(r_sh, r_ro - g.bridge - g.barrier_radial_span, 12),
        # barriers
        np.sort(np.unique([r for r_i,r_o in barrier_bands(g) for r in [r_i,r_o]])),
        np.linspace(r_ro - g.bridge, r_ro, 6),
        np.linspace(r_ro, r_bore, 2 * n_gap_rows + 1),
        np.linspace(r_bore, r_bore + depth, 12),
        np.linspace(r_bore + depth, r_out, 8),
        np.linspace(r_out, r_dom, 6),
    ])
    r = np.unique(np.round(r, 10))
    
    nodes = [(0.0, 0.0)]
    rings = []
    n_ray = len(th_ray)
    for rk in r:
        if rk < 1e-15:
            continue
        th = th_ray
        idx = np.arange(len(nodes), len(nodes) + n_ray)
        for i in range(n_ray):
            nodes.append((rk * math.cos(th_ray[i]), rk * math.sin(th_ray[i])))
        rings.append(idx)
    
    pts = np.array(nodes).T
    tris = []
    band_of_tri = []
    
    # fan from center
    if rings:
        r0f = r[1] if len(r) > 1 else r[0] if len(r) > 0 else 0
        reg0 = SHAFT if r0f <= r_sh + 1e-12 else ROTOR
        for i in range(n_ray):
            i2 = (i + 1) % n_ray
            tris.append((0, rings[0][i], rings[0][i2]))
            band_of_tri.append(reg0)
    
    # stitch rings
    for k in range(len(rings)-1):
        ia, ib = rings[k], rings[k+1]
        for i in range(n_ray):
            i2 = (i + 1) % n_ray
            tris.append((ia[i], ib[i], ia[i2]))
            band_of_tri.append(None)  # will classify
            tris.append((ib[i], ib[i2], ia[i2]))
            band_of_tri.append(None)
    
    t = np.array(tris).T
    mesh = MeshTri(pts, t)
    
    # classify
    ct = pts[:, t].mean(axis=1)
    regions = classify_point(g, ct[0], ct[1])
    subdomains = {name: np.flatnonzero(regions == name) for name in np.unique(regions)}
    return mesh, subdomains, r


if __name__ == "__main__":
    g = SynRMGeometry()
    mesh, sub, br = build_mesh(g)
    print(f"nodes={mesh.p.shape[1]} elems={mesh.t.shape[1]}")
    for k in sorted(sub):
        print(f"  {k}: {len(sub[k])}")
