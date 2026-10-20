"""Render a PNG preview of the exported SynRM baseline cross-section.

Usage: .venv/bin/python simulation/scripts/preview_geometry.py [config.json] [out.png]
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main(cfg="simulation/configs/synrm_baseline_v0.json",
         out="simulation/results/synrm_baseline_v0_preview.png"):
    d = json.load(open(cfg))
    fig, ax = plt.subplots(figsize=(7, 7))

    outer = d["stator"]["outer"]
    ax.plot(*zip(*outer), "k-", lw=1)
    inner = d["stator"]["inner"]
    ax.plot(*zip(*inner), "k-", lw=1)

    for b in d["barriers"]:
        pts = b["points"]
        ax.fill(*zip(*pts), color="0.6", ec="k", lw=0.3)

    for r_frac, lbl in [(d["parameters"]["stator_od"] / 2, "stator OD"),
                        (d["parameters"]["stator_bore"] / 2, "bore"),
                        (d["derived"]["rotor_od"] / 2, "rotor OD")]:
        ax.plot(*zip(*[(r_frac * __import__("math").cos(a), r_frac * __import__("math").sin(a))
                       for a in [i * 6.2832 / 200 for i in range(201)]]), "r--", lw=0.5)

    ax.set_aspect("equal")
    ax.set_title(f"SynRM baseline v0 — {d['parameters']['n_slots']} slots / 4 poles / "
                 f"{d['parameters']['n_barriers']} barriers per pole")
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print(f"preview -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
