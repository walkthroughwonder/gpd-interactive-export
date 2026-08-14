"""Numerical checks for the force-layout / camera-framing invariants.

These mirror the math in index.html so a hardcoded radius of
max(8, phases.length * 1.5) cannot silently return.
"""

import math
import random


def simulate_force(n=6, steps=300, seed=1):
    random.seed(seed)
    max_depth = n - 1
    spacing_x = 3.0
    positions = [
        [
            (i - max_depth / 2) * spacing_x + (random.random() - 0.5) * 0.3,
            (random.random() - 0.5) * 2,
            (random.random() - 0.5) * 2,
        ]
        for i in range(n)
    ]
    vel = [[0.0, 0.0, 0.0] for _ in range(n)]
    edges = [(i, i + 1) for i in range(n - 1)]
    repulsion, attraction, damping, rest = 4.0, 0.015, 0.85, 2.8
    origin_pull = 0.012

    def mag(v):
        return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 0.01

    for _ in range(steps):
        for i in range(n):
            for j in range(i + 1, n):
                d = [positions[i][k] - positions[j][k] for k in range(3)]
                dist = mag(d)
                force = [d[k] / dist * (repulsion / (dist * dist)) for k in range(3)]
                for k in range(3):
                    vel[i][k] += force[k]
                    vel[j][k] -= force[k]
        for fi, ti in edges:
            d = [positions[ti][k] - positions[fi][k] for k in range(3)]
            length = mag(d)
            force = [d[k] / length * ((length - rest) * attraction) for k in range(3)]
            for k in range(3):
                vel[fi][k] += force[k]
                vel[ti][k] -= force[k]
        for i, p in enumerate(positions):
            for k in range(3):
                vel[i][k] += -p[k] * origin_pull
                vel[i][k] *= damping
                p[k] += vel[i][k]
        cx = sum(p[0] for p in positions) / n
        cy = sum(p[1] for p in positions) / n
        cz = sum(p[2] for p in positions) / n
        for p in positions:
            p[0] -= cx
            p[1] -= cy
            p[2] -= cz
    return positions


def bounding_radius(positions, node_radius=0.35, pad=0.45):
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    zs = [p[2] for p in positions]
    size = (
        (max(xs) - min(xs)) + 2 * (node_radius + pad),
        (max(ys) - min(ys)) + 2 * (node_radius + pad),
        (max(zs) - min(zs)) + 2 * (node_radius + pad),
    )
    return max(math.sqrt(size[0] ** 2 + size[1] ** 2 + size[2] ** 2) * 0.5, node_radius * 4)


def fit_radius(radius, fov_deg=60, aspect=920 / 800, padding=1.3, node_radius=0.35):
    fov = fov_deg * math.pi / 180
    dist_y = radius / math.tan(fov / 2)
    dist_x = radius / (math.tan(fov / 2) * aspect)
    return max(dist_x, dist_y, node_radius * 12) * padding


class TestForceLayoutStaysFrameable:
    def test_centroid_stays_at_origin(self):
        positions = simulate_force()
        n = len(positions)
        cx = sum(p[0] for p in positions) / n
        cy = sum(p[1] for p in positions) / n
        cz = sum(p[2] for p in positions) / n
        assert abs(cx) < 1e-9 and abs(cy) < 1e-9 and abs(cz) < 1e-9

    def test_spread_is_compact(self):
        positions = simulate_force()
        radii = [math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2) for p in positions]
        assert max(radii) < 12

    def test_fit_radius_clears_the_cloud(self):
        positions = simulate_force()
        bounds_r = bounding_radius(positions)
        fit = fit_radius(bounds_r)
        hardcoded = max(8, 6 * 1.5)
        assert fit > bounds_r + 0.35 * 4
        assert hardcoded < bounds_r  # the old reset sat inside the cloud

    def test_zoom_floor_outside_bounding_sphere(self):
        positions = simulate_force()
        bounds_r = bounding_radius(positions)
        min_r = bounds_r + 0.35 * 4
        for p in positions:
            # Camera on +Z at min_r looking at origin cannot sit inside a node.
            cam = (0.0, 0.0, min_r)
            dist = math.sqrt((p[0] - cam[0]) ** 2 + (p[1] - cam[1]) ** 2 + (p[2] - cam[2]) ** 2)
            assert dist > 0.35 * 2

    def test_face_on_angles_map_to_positive_z(self):
        theta = phi = math.pi / 2
        radius = 10
        x = radius * math.sin(phi) * math.cos(theta)
        y = radius * math.cos(phi)
        z = radius * math.sin(phi) * math.sin(theta)
        assert abs(x) < 1e-9 and abs(y) < 1e-9 and abs(z - radius) < 1e-9

    def test_theta_zero_is_edge_on(self):
        theta = 0
        phi = math.pi / 2
        radius = 10
        x = radius * math.sin(phi) * math.cos(theta)
        z = radius * math.sin(phi) * math.sin(theta)
        assert abs(x - radius) < 1e-9 and abs(z) < 1e-9
