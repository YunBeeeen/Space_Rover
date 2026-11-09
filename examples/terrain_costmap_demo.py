#!/usr/bin/env python3
"""Create terrain layers and a costmap using the existing mapping modules."""
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mapping"))
from experiments.handheld_mapping.terrain import GridSpec, TerrainGrid
from experiments.handheld_mapping.costmap import RoverLimits, build_costmap


def main():
    resolution = 0.1
    x, y = np.meshgrid(np.arange(20) * resolution + 0.05,
                       np.arange(20) * resolution + 0.05)
    points = np.column_stack((x.ravel(), y.ravel(), (0.1 * x).ravel()))
    terrain = TerrainGrid(GridSpec((0.0, 2.0, 0.0, 2.0), resolution))
    for stamp in (1, 2):
        terrain.update(points, stamp)
    layers = terrain.layers()
    costs = build_costmap(layers, resolution, RoverLimits(safety_radius_m=0.0))
    valid = costs < 254
    print(json.dumps({
        "grid_shape": list(costs.shape),
        "valid_cells": int(valid.sum()),
        "blocked_cells": int((costs == 254).sum()),
        "unknown_cells": int((costs == 255).sum()),
        "mean_slope_deg": round(float(np.nanmean(layers["slope_deg"][valid])), 3),
    }, indent=2))


if __name__ == "__main__":
    main()
