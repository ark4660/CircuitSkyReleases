# Circuit & Sky

A Create-focused modpack for **Minecraft 1.21.1** on **NeoForge**: airships, trains, electricity and diesel power,
plus a performance setup that keeps big factories smooth and Distant Horizons for long view distances.

[![Latest release](https://img.shields.io/github/v/release/ark4660/CircuitSkyReleases?label=latest&color=5fd068)](https://github.com/ark4660/CircuitSkyReleases/releases/latest)
![Minecraft 1.21.1](https://img.shields.io/badge/Minecraft-1.21.1-5ba8ff)
![NeoForge](https://img.shields.io/badge/NeoForge-21.1-ffc04d)

**[Download the latest pack](https://github.com/ark4660/CircuitSkyReleases/releases/latest/download/CircuitSky.mrpack)** ·
[Mod list](MODS.md) · [Changelog](CHANGELOG.md)

## What's inside

- **Create 6** and its add-ons: Aeronautics (planes, airships, cars), Steam 'n' Rails, New Age and Crafts & Additions
  (electricity), Diesel Generators, Power Loader (chunk loaders), Jetpack, Deco, Connected, Central Kitchen,
  Dreams & Desires
- **Performance:** Sodium, ModernFix, FerriteCore, ImmediatelyFast, Entity Culling, BadOptimizations, Dynamic FPS
- **View distance:** Distant Horizons
- **Quality of life:** JEI, Xaero's Minimap, Forgematica (Litematica), Pro Placer, Nature's Compass, Better Clouds,
  Fullbright, and a custom FancyMenu title screen

Full list with versions and licenses: [MODS.md](MODS.md)

## Install

### Circuit & Sky Launcher
The launcher installs and updates the pack on its own. Press **Play**.

### Prism Launcher
1. **Add Instance** → **Import**.
2. Paste `https://github.com/ark4660/CircuitSkyReleases/releases/latest/download/CircuitSky.mrpack` and press **OK**.
3. In the instance's **Settings** → **Java**, set the maximum memory to 6–8 GB.

### Modrinth App
Download the `.mrpack` from the [latest release](https://github.com/ark4660/CircuitSkyReleases/releases/latest),
then **Create instance** → **From file** and pick it.

### Updating
Download the new `.mrpack` and import it as a new instance. To keep your worlds, copy `saves/` across from the old
instance. (The Circuit & Sky Launcher does this for you and keeps your keybinds and settings.)

## Requirements

| | |
|---|---|
| Minecraft | Java Edition 1.21.1 |
| Loader | NeoForge 21.1 (installed automatically) |
| Java | 21 (Prism, the Modrinth App and the Circuit & Sky Launcher download it for you) |
| Memory | 6–8 GB for the game. More than about 10 GB can make stutter worse |
| Download | About 50 MB for the pack, then about 150 MB of mods from Modrinth on first install |

## Performance tips

- Keep the normal render distance at **8–12 chunks** and let Distant Horizons draw the far terrain.
- If the game stutters while flying or on trains, lower Distant Horizons' quality preset and CPU thread count in its
  settings.
- Dynamic FPS lowers the frame rate while the game is in the background, so alt-tabbing won't heat up your PC.

## Known issues

- Better Clouds doesn't support Distant Horizons 3 yet, so its clouds don't blend with far terrain.

## Credits

Circuit & Sky is a curated list of other people's mods. Every mod is downloaded from
[Modrinth](https://modrinth.com) when the pack is installed; no mod files are rehosted here. All credit goes to
each mod's authors (see [MODS.md](MODS.md) for links and licenses). The release files only contain the pack's
configs and menu assets.

## For maintainers: publishing a release

1. In Prism, right-click the instance → **Export** → **Modrinth (.mrpack)**. Untick `saves`, `logs`, `screenshots`
   and other personal folders. Bump the version number.
2. Name the file exactly `CircuitSky.mrpack`. The launcher and the download link above use that name.
3. Refresh the mod list: `python3 scripts/modlist.py CircuitSky.mrpack`, then add a section to `CHANGELOG.md`.
4. Commit, then create a release tagged `vX.Y.Z` with `CircuitSky.mrpack` attached, and paste the changelog section
   as its notes:
   `gh release create vX.Y.Z CircuitSky.mrpack --title "Circuit & Sky X.Y.Z" --notes-file notes.md`
