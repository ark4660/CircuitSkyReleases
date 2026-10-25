#!/usr/bin/env python3
"""Build CircuitSky.mrpack from a Prism Launcher instance (instead of Prism's Export dialog).

    python3 scripts/build_mrpack.py ~/.local/share/PrismLauncher/instances/<instance> 1.1.0

Mods found on Modrinth (by hash) are linked; anything else is packed into overrides/mods.
Configs and other pack files go into overrides/, minus the personal folders in SKIP.
"""
import configparser
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
import zipfile

UA = {"User-Agent": "ark4660/CircuitSkyReleases build_mrpack"}
OUT = "CircuitSky.mrpack"

# Top-level folders/files in minecraft/ that are personal or generated at runtime.
SKIP = {
    "mods", "saves", "logs", "crash-reports", "screenshots", "schematics", "downloads", "xaero", "journeymap",
    "Distant_Horizons_server_data", ".mixin.out", ".sable", ".fabric", ".cache", "servers.dat", "servers.dat_old",
    "usercache.json", "usernamecache.json", "ponders_watched.json", "imgui.ini", "command_history.txt",
    "patchouli_books", "local", "fancymenu_data",
}
# Files inside config/ that are per-player.
SKIP_CONFIG = {"sodium-fingerprint.json", "xaeropatreon.txt"}


def post(url, data):
    req = urllib.request.Request(url, json.dumps(data).encode(), dict(UA, **{"Content-Type": "application/json"}))
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r:
        return json.load(r)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    inst, version = os.path.expanduser(sys.argv[1]), sys.argv[2]
    mc = os.path.join(inst, "minecraft")

    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(os.path.join(inst, "instance.cfg"))
    name = cfg.get("General", "ExportName", fallback="") or cfg.get("General", "name", fallback="Circuit and Sky")
    with open(os.path.join(inst, "mmc-pack.json")) as fh:
        comps = {c["uid"]: c["version"] for c in json.load(fh)["components"]}
    deps = {"minecraft": comps["net.minecraft"]}
    for uid, key in [("net.neoforged", "neoforge"), ("net.minecraftforge", "forge"), ("net.fabricmc.fabric-loader", "fabric-loader")]:
        if uid in comps:
            deps[key] = comps[uid]

    jars = {}
    mods_dir = os.path.join(mc, "mods")
    for f in sorted(os.listdir(mods_dir)):
        if f.endswith(".jar"):
            with open(os.path.join(mods_dir, f), "rb") as fh:
                data = fh.read()
            jars[hashlib.sha1(data).hexdigest()] = (f, data)
    versions = post("https://api.modrinth.com/v2/version_files", {"hashes": list(jars), "algorithm": "sha1"})
    ids = sorted({v["project_id"] for v in versions.values()})
    projects = {p["id"]: p for p in get("https://api.modrinth.com/v2/projects?ids=" + urllib.parse.quote(json.dumps(ids)))}

    files, bundled = [], []
    for sha1, (fname, data) in jars.items():
        v = versions.get(sha1)
        if not v:
            bundled.append((fname, data))
            continue
        f = next(x for x in v["files"] if x["hashes"]["sha1"] == sha1)
        server = projects[v["project_id"]]["server_side"]
        files.append({
            "path": "mods/" + f["filename"],
            "hashes": {"sha1": sha1, "sha512": f["hashes"]["sha512"]},
            "env": {"client": "required", "server": server if server in ("optional", "unsupported") else "required"},
            "downloads": [f["url"]],
            "fileSize": f["size"],
        })
    files.sort(key=lambda x: x["path"].lower())

    index = {"formatVersion": 1, "game": "minecraft", "versionId": version, "name": name,
             "summary": "A Create-focused NeoForge modpack.", "files": files, "dependencies": deps}
    overrides = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(index, indent=1))
        for fname, data in bundled:
            z.writestr("overrides/mods/" + fname, data)
        for root, dirs, names in os.walk(mc):
            rel = os.path.relpath(root, mc)
            top = rel.split(os.sep)[0]
            if top in SKIP:
                dirs[:] = []
                continue
            dirs.sort()
            for n in sorted(names):
                if rel == "." and n in SKIP or rel == "config" and (n in SKIP_CONFIG or n.endswith(".bak")):
                    continue
                path = os.path.join(root, n)
                z.write(path, "overrides/" + os.path.relpath(path, mc).replace(os.sep, "/"))
                overrides += 1
    print(f"{OUT}: {name} {version}, {len(files)} Modrinth mods, {len(bundled)} bundled jars, "
          f"{overrides} override files, {os.path.getsize(OUT) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
