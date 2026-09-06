"""Rebuild the pinned native WIE runtime, without downloading game content."""
from pathlib import Path
import subprocess

REVISION = "91c367031624cb7f52184d72496e95d57cf363ce"
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "build" / "wie"


def run(*args: str, cwd: Path = ROOT) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def main() -> None:
    if SOURCE.exists():
        raise FileExistsError(f"Use a fresh build directory: {SOURCE}")
    SOURCE.parent.mkdir(exist_ok=True)
    run("git", "clone", "https://github.com/dlunch/wie.git", str(SOURCE))
    run("git", "checkout", "--detach", REVISION, cwd=SOURCE)
    run("git", "apply", str(ROOT / "patches" / "macos-native.patch"), cwd=SOURCE)
    run("cargo", "fmt", "--check", cwd=SOURCE)
    run("cargo", "test", "-p", "wie", "-p", "wie-backend", "-p", "wie-lgt", cwd=SOURCE)
    probe = SOURCE.parent / "synth-render-test"
    run("clang", "-Wall", "-Wextra", "-Werror", str(ROOT / "tests" / "synth_render.c"),
        "-I", str(SOURCE / "src"), "-framework", "AudioToolbox", "-framework", "AudioUnit",
        "-framework", "CoreServices", "-o", str(probe))
    run(str(probe))
    run("cargo", "clippy", "--workspace", cwd=SOURCE)
    run("cargo", "build", "--release", "--locked", "-p", "wie", cwd=SOURCE)


if __name__ == "__main__":
    main()
