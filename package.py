"""Build a local native app from a compiled WIE binary and a supplied game archive."""
import argparse
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import zipfile


def package(binary: Path, game: Path, output: Path, license_file: Path) -> None:
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")
    with zipfile.ZipFile(game) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"Corrupt game archive entry: {bad}")
        icon = archive.read("big.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        app = Path(temp) / output.name
        contents = app / "Contents"
        resources = contents / "Resources"
        macos = contents / "MacOS"
        resources.mkdir(parents=True)
        macos.mkdir()
        shutil.copy2(binary, macos / "HeroesLore4")
        # The supplied phone backup contains a serialized legacy database,
        # not the raw record stream expected by the desktop storage adapter.
        # Start with a fresh local save; preserve the user's original archive.
        with zipfile.ZipFile(game) as source, zipfile.ZipFile(resources / "game.zip", "w", zipfile.ZIP_DEFLATED) as target:
            for entry in source.infolist():
                if entry.filename != "P/kickass":
                    target.writestr(entry, source.read(entry.filename))
        shutil.copy2(license_file, resources / "WIE-LICENSE.txt")
        iconset = Path(temp) / "Game.iconset"
        iconset.mkdir()
        original = Path(temp) / "original.png"
        original.write_bytes(icon)
        for size in (16, 32, 128, 256, 512):
            for scale in (1, 2):
                suffix = "@2x" if scale == 2 else ""
                target = iconset / f"icon_{size}x{size}{suffix}.png"
                subprocess.run(["sips", "-z", str(size * scale), str(size * scale), str(original), "--out", str(target)], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(resources / "Game.icns")], check=True)
        info = {
            "CFBundleIdentifier": "local.heroeslore.HeroesLore4",
            "CFBundleName": "영웅서기 4",
            "CFBundleDisplayName": "영웅서기 4",
            "CFBundleExecutable": "HeroesLore4",
            "CFBundlePackageType": "APPL",
            "CFBundleShortVersionString": "1.0",
            "CFBundleVersion": "1",
            "CFBundleIconFile": "Game",
            "NSHighResolutionCapable": True,
            "LSApplicationCategoryType": "public.app-category.role-playing-games",
        }
        with (contents / "Info.plist").open("wb") as stream:
            plistlib.dump(info, stream)
        subprocess.run(["codesign", "--force", "--sign", "-", str(app)], check=True)
        subprocess.run(["codesign", "--verify", "--deep", "--strict", str(app)], check=True)
        app.rename(output)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("game", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--license", required=True, type=Path)
    args = parser.parse_args()
    package(args.binary, args.game, args.output, args.license)
