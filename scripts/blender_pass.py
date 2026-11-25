#!/usr/bin/env python3
"""Portable Blender 4.2+/5.x dual-pass (Beauty + Clay-Wireframe) hero-camera orbit renderer.

Orbits smoothly around a .blend file's existing Hero camera so the hero angle is preserved,
renders synchronized Beauty and Clay+Gold Wireframe passes with auto-detected GPU (OptiX/CUDA/
Metal/HIP/oneAPI/CPU), and encodes crisp raw MP4s via FFmpeg.

Usage:
  blender --background --python blender_pass.py -- \
    --blend path/to/model.blend --out raw_clips/hero \
    --res 1920x1080 --frames 54 --fps 24 --samples 36 --wire-samples 14 \
    --zoom-start 1.06 --zoom-end 0.90 --orbit-start -14 --orbit-end 14
"""

import argparse
import math
import os
import shutil
import subprocess
import sys

import bpy
from mathutils import Vector, Matrix


def enable_gpu():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for backend in ("OPTIX", "CUDA", "METAL", "HIP", "ONEAPI"):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == backend]
            if gpus:
                for d in prefs.devices:
                    d.use = (d.type == backend)
                scene.cycles.device = "GPU"
                return backend
        except Exception:
            continue
    scene.cycles.device = "CPU"
    return "CPU"


def compute_subject_center():
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    found = False
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render:
            continue
        nl = o.name.lower()
        if any(k in nl for k in ("studio_", "scrim_", "cyclorama", "floor", "backdrop", "ground", "plinth")):
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mn.x = min(mn.x, w.x); mn.y = min(mn.y, w.y); mn.z = min(mn.z, w.z)
            mx.x = max(mx.x, w.x); mx.y = max(mx.y, w.y); mx.z = max(mx.z, w.z)
            found = True
    return ((mn + mx) * 0.5) if found else Vector((0.0, 0.0, 0.5))


def find_hero_camera(preferred=None):
    if preferred and preferred in bpy.data.objects and bpy.data.objects[preferred].type == "CAMERA":
        return bpy.data.objects[preferred]
    for name in ("Cam_01_Hero3Q", "Camera_Hero3Q", "Cam_Hero3Q", "Camera"):
        if name in bpy.data.objects and bpy.data.objects[name].type == "CAMERA":
            return bpy.data.objects[name]
    if bpy.context.scene.camera and bpy.context.scene.camera.type == "CAMERA":
        return bpy.context.scene.camera
    for o in bpy.data.objects:
        if o.type == "CAMERA":
            return o
    raise RuntimeError("No camera found in .blend file.")


def create_orbit_camera(hero_cam, center, args):
    cd = hero_cam.data.copy()
    cd.name = "Cam_Showreel_Orbit"
    co = bpy.data.objects.new("Cam_Showreel_Orbit", cd)
    bpy.context.scene.collection.objects.link(co)

    base_offset = hero_cam.matrix_world.translation - center
    dist_base = base_offset.length
    n_frames = args.frames

    for f in range(1, n_frames + 1):
        t = (f - 1) / max(1, n_frames - 1)
        s = t * t * (3.0 - 2.0 * t)
        ang = math.radians(args.orbit_start + (args.orbit_end - args.orbit_start) * s)
        zoom = args.zoom_start + (args.zoom_end - args.zoom_start) * s
        elev = (args.elev_start + (args.elev_end - args.elev_start) * s) * dist_base

        pos = center + (Matrix.Rotation(ang, 3, "Z") @ (base_offset * zoom)) + Vector((0.0, 0.0, elev))
        co.location = pos
        co.rotation_euler = (center - pos).to_track_quat("-Z", "Y").to_euler()
        co.keyframe_insert("location", frame=f)
        co.keyframe_insert("rotation_euler", frame=f)

    bpy.context.scene.camera = co
    return co


def make_clay_wire_material():
    m = bpy.data.materials.new("Mat_NexDark_ClayWire")
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")

    clay = nt.nodes.new("ShaderNodeBsdfPrincipled")
    clay.inputs["Base Color"].default_value = (0.075, 0.080, 0.090, 1.0)
    clay.inputs["Metallic"].default_value = 0.12
    clay.inputs["Roughness"].default_value = 0.56

    wire_em = nt.nodes.new("ShaderNodeEmission")
    wire_em.inputs["Color"].default_value = (0.94, 0.78, 0.45, 1.0)
    wire_em.inputs["Strength"].default_value = 3.4

    wf = nt.nodes.new("ShaderNodeWireframe")
    wf.use_pixel_size = True
    wf.inputs["Size"].default_value = 1.25

    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(wf.outputs["Fac"], mix.inputs["Fac"])
    nt.links.new(clay.outputs["BSDF"], mix.inputs[1])
    nt.links.new(wire_em.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return m


def apply_wire_override(wire_mat):
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render:
            continue
        nl = o.name.lower()
        if any(k in nl for k in ("studio_", "scrim_", "cyclorama", "floor", "backdrop", "ground", "plinth")):
            continue
        if o.data.materials:
            for i in range(len(o.data.materials)):
                o.data.materials[i] = wire_mat
        else:
            o.data.materials.append(wire_mat)


def encode_sequence(frames_dir, out_mp4, fps):
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "f_%04d.png"),
        "-c:v", "libx264", "-profile:v", "high", "-crf", "14",
        "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        out_mp4,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.rmtree(frames_dir, ignore_errors=True)


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(description="Render synchronized Blender Beauty + Clay-Wireframe orbit passes.")
    p.add_argument("--blend", required=True, help="Path to source .blend file")
    p.add_argument("--out", required=True, help="Output path stem (creates <stem>_beauty.mp4 and <stem>_wire.mp4)")
    p.add_argument("--camera", default=None, help="Optional camera object name to orbit from")
    p.add_argument("--res", default="1920x1080", help="Resolution WxH (e.g. 1920x1080 or 1080x1920)")
    p.add_argument("--frames", type=int, default=54)
    p.add_argument("--fps", type=int, default=24)
    p.add_argument("--samples", type=int, default=36)
    p.add_argument("--wire-samples", type=int, default=14)
    p.add_argument("--orbit-start", type=float, default=-14.0)
    p.add_argument("--orbit-end", type=float, default=14.0)
    p.add_argument("--zoom-start", type=float, default=1.06)
    p.add_argument("--zoom-end", type=float, default=0.90)
    p.add_argument("--elev-start", type=float, default=-0.03)
    p.add_argument("--elev-end", type=float, default=0.05)
    p.add_argument("--skip-wire", action="store_true", help="Only render beauty pass")
    return p.parse_args(argv)


def main():
    args = parse_args()
    w_str, h_str = args.res.lower().split("x")
    res_x, res_y = int(w_str), int(h_str)

    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(args.blend))
    backend = enable_gpu()

    scene = bpy.context.scene
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.fps = args.fps
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.025
    scene.cycles.max_bounces = 6
    scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 4
    scene.render.use_motion_blur = False

    scene.frame_set(1)
    hero_cam = find_hero_camera(args.camera)
    center = compute_subject_center()
    create_orbit_camera(hero_cam, center, args)

    out_stem = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_stem), exist_ok=True)

    # Pass 1: Beauty
    beauty_mp4 = f"{out_stem}_beauty.mp4"
    fdir_b = f"{out_stem}_tmp_beauty"
    shutil.rmtree(fdir_b, ignore_errors=True)
    os.makedirs(fdir_b, exist_ok=True)
    scene.cycles.samples = args.samples
    for f in range(1, args.frames + 1):
        scene.frame_set(f)
        scene.render.filepath = os.path.join(fdir_b, f"f_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    encode_sequence(fdir_b, beauty_mp4, args.fps)
    print(f"[blender_pass] Saved BEAUTY -> {beauty_mp4} [{backend}]", flush=True)

    # Pass 2: Clay + Wireframe
    if not args.skip_wire:
        wire_mp4 = f"{out_stem}_wire.mp4"
        fdir_w = f"{out_stem}_tmp_wire"
        shutil.rmtree(fdir_w, ignore_errors=True)
        os.makedirs(fdir_w, exist_ok=True)
        apply_wire_override(make_clay_wire_material())
        scene.cycles.samples = args.wire_samples
        for f in range(1, args.frames + 1):
            scene.frame_set(f)
            scene.render.filepath = os.path.join(fdir_w, f"f_{f:04d}.png")
            bpy.ops.render.render(write_still=True)
        encode_sequence(fdir_w, wire_mp4, args.fps)
        print(f"[blender_pass] Saved WIREFRAME -> {wire_mp4} [{backend}]", flush=True)


if __name__ == "__main__":
    main()
