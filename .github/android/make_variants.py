#!/usr/bin/env python3
"""Builds startup-bisect variants of the game for tracking down launch crashes on a device.

usage: make_variants.py <workspace> <godot-binary> <out-dir>

Each variant is a copy of the project with a modified project.godot, exported with the
"Android arm64 no GIF" preset under its own package name so it installs next to the others.
"""
import os, re, shutil, subprocess, sys

ws, godot, out = sys.argv[1:4]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(out, exist_ok=True)

VARIANTS = [
    # name, autoloads to keep (None = all), replace main scene, log file path
    ("bisect0", [], True, None),
    ("bisect1", ["ModLoaderStore", "ModLoader", "OTAUpdater"], True, None),
    ("bisect2", None, True, None),
    ("logtest", None, False, "/storage/emulated/0/Download/SMBR-log.txt"),
]

def edit_autoloads(text, keep):
    m = re.search(r"(?ms)^\[autoload\]\n(.*?)(?=^\[)", text)
    lines = [l for l in m.group(1).splitlines() if l.strip()]
    kept = [l for l in lines if keep is None or l.split("=")[0] in keep]
    return text[:m.start(1)] + "\n" + "\n".join(kept) + "\n\n" + text[m.end(1):]

for name, keep, swap_main, log_path in VARIANTS:
    d = f"/tmp/smbr_variant_{name}"
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(ws, d, ignore=shutil.ignore_patterns(".git", "build", "variants"), symlinks=True)
    p = os.path.join(d, "project.godot")
    t = open(p, encoding="utf-8").read()
    if keep is not None:
        t = edit_autoloads(t, keep)
    if swap_main:
        t = re.sub(r'(?m)^run/main_scene=.*$', 'run/main_scene="res://bisect_main.tscn"', t)
        open(os.path.join(d, "bisect_main.gd"), "w").write(open(os.path.join(here, "bisect_main.gd")).read().replace("__VARIANT__", name))
        open(os.path.join(d, "bisect_main.tscn"), "w").write(
            '[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://bisect_main.gd" id="1"]\n\n'
            '[node name="Main" type="Control"]\nlayout_mode = 3\nanchors_preset = 15\nanchor_right = 1.0\nanchor_bottom = 1.0\nscript = ExtResource("1")\n')
    if log_path:
        t = re.sub(r"(?m)^\[debug\]\n", '[debug]\n\nfile_logging/enable_file_logging=true\nfile_logging/log_path="%s"\n' % log_path, t, count=1)
    open(p, "w", encoding="utf-8").write(t)

    pr = os.path.join(d, "export_presets.cfg")
    c = open(pr, encoding="utf-8").read()
    c = c.replace('package/unique_name="com.smb1r.remastered"', f'package/unique_name="com.smb1r.{name}"')
    c = c.replace('package/name="Super Mario Bros. Remastered"', f'package/name="SMBR {name}"')
    open(pr, "w", encoding="utf-8").write(c)

    # re-scan so the new scene is imported, then export
    subprocess.run([godot, "--headless", "--path", d, "--import"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    apk = os.path.join(out, f"test-{name}.apk")
    r = subprocess.run([godot, "--headless", "--path", d, "--export-release", "Android arm64 no GIF", apk], capture_output=True, text=True)
    ok = os.path.exists(apk) and os.path.getsize(apk) > 0
    print(f"{name}: {'OK' if ok else 'FAILED'}", flush=True)
    if not ok:
        print(r.stdout[-2000:], r.stderr[-2000:])
        sys.exit(1)
    if not os.environ.get("KEEP_VARIANT_DIRS"):
        shutil.rmtree(d, ignore_errors=True)
