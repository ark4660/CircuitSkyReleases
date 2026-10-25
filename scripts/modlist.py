#!/usr/bin/env python3
"""Regenerate MODS.md from a pack export.

    python3 scripts/modlist.py CircuitSky.mrpack
    python3 scripts/modlist.py ~/.local/share/PrismLauncher/instances/<instance>/minecraft/mods

Mods are looked up on Modrinth by file hash. Anything not found there is listed as "bundled".
"""
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
import zipfile

UA = {"User-Agent": "ark4660/CircuitSkyReleases modlist"}

# Section for each Modrinth slug. Unknown slugs go under "Other".
SECTIONS = {
    "Create": [
        "create", "create-aeronautics", "createaddition", "create-central-kitchen", "create-connected",
        "create-deco", "create-diesel-generators", "create-dragons-plus", "create-dreams-and-desires",
        "create-jetpack", "create-new-age", "create-power-loader", "create-steam-n-rails-1.21.1", "sable",
    ],
    "Performance": [
        "sodium", "distanthorizons", "modernfix", "ferrite-core", "immediatelyfast", "entityculling",
        "badoptimizations", "dynamic-fps",
    ],
    "Visuals & HUD": ["better-clouds", "fullbright-forge", "fancymenu", "xaeros-minimap", "jei"],
    "Building & Exploring": ["forgematica", "pro-placer", "natures-compass"],
    "Libraries": [
        "architectury-api", "badpackets", "puzzles-lib", "kotlin-for-forge", "mafglib", "konkrete",
        "melody", "yacl",
    ],
}
SIDE = {"required": "✔", "optional": "optional", "unsupported": "—", "unknown": "?"}


def get(url, data=None):
    headers = dict(UA, **({"Content-Type": "application/json"} if data else {}))
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def read_pack(path):
    """Returns ({sha1: filename}, pack name, version, dependencies)."""
    if os.path.isdir(path):
        files = {}
        for f in sorted(os.listdir(path)):
            if f.endswith(".jar"):
                with open(os.path.join(path, f), "rb") as fh:
                    files[hashlib.sha1(fh.read()).hexdigest()] = f
        return files, None, None, {}
    with zipfile.ZipFile(path) as z:
        index = json.loads(z.read("modrinth.index.json"))
        files = {f["hashes"]["sha1"]: os.path.basename(f["path"]) for f in index["files"] if f["path"].startswith("mods/")}
        for name in z.namelist():
            if name.startswith(("overrides/mods/", "client-overrides/mods/")) and name.endswith(".jar"):
                files[hashlib.sha1(z.read(name)).hexdigest()] = os.path.basename(name)
    return files, index.get("name"), index.get("versionId"), index.get("dependencies", {})


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    files, name, version, deps = read_pack(os.path.expanduser(sys.argv[1]))
    versions = get("https://api.modrinth.com/v2/version_files", {"hashes": list(files), "algorithm": "sha1"})
    ids = sorted({v["project_id"] for v in versions.values()})
    projects = {p["id"]: p for p in get("https://api.modrinth.com/v2/projects?ids=" + urllib.parse.quote(json.dumps(ids)))}

    slug_section = {s: sec for sec, slugs in SECTIONS.items() for s in slugs}
    rows = {sec: [] for sec in [*SECTIONS, "Other"]}
    bundled = []
    for sha, filename in files.items():
        v = versions.get(sha)
        if not v:
            bundled.append(filename)
            continue
        p = projects[v["project_id"]]
        rows[slug_section.get(p["slug"], "Other")].append((p, v))

    out = ["# Mods", ""]
    if name:
        out += [f"Generated from **{name} {version}**"
                + (f" · Minecraft {deps['minecraft']} · NeoForge {deps['neoforge']}" if "neoforge" in deps else ""), ""]
    out += [f"{len(files)} mods. Client/Server shows whether a mod is needed on each side.", ""]
    for sec, items in rows.items():
        if not items:
            continue
        out += [f"## {sec}", "", "| Mod | Version | What it does | Client | Server | License |", "|---|---|---|---|---|---|"]
        for p, v in sorted(items, key=lambda pv: pv[0]["title"].lower()):
            desc = p["description"].replace("|", "\\|").strip()
            lic = (p.get("license") or {}).get("id", "").replace("LicenseRef-", "")
            out.append(f"| [{p['title']}](https://modrinth.com/mod/{p['slug']}) | {v['version_number']} | {desc} "
                       f"| {SIDE.get(p['client_side'], '?')} | {SIDE.get(p['server_side'], '?')} | {lic} |")
        out.append("")
    if bundled:
        out += ["## Bundled (not on Modrinth)", ""] + [f"- `{f}`" for f in sorted(bundled)] + [""]

    with open(os.path.join(os.path.dirname(__file__), "..", "MODS.md"), "w") as fh:
        fh.write("\n".join(out))
    print(f"MODS.md: {len(files)} mods, {len(bundled)} bundled")


if __name__ == "__main__":
    main()
