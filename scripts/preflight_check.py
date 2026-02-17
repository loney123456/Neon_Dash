"""Cross-platform preflight checks for Neon Dash runtime."""

from __future__ import annotations

import platform
import sys
from importlib import metadata
from typing import Optional


REQUIRED_PACKAGES = {
    "ursina": "5.2.0",
    "panda3d": "1.10.16",
}

PYTHON_MIN = (3, 9)
PYTHON_MAX = (3, 11)


def _status(tag: str, message: str) -> None:
    print(f"[{tag}] {message}")


def check_python_version() -> bool:
    current = sys.version_info[:3]
    min_ok = current >= PYTHON_MIN
    max_ok = current <= PYTHON_MAX
    if min_ok and max_ok:
        _status("OK", f"Python {current[0]}.{current[1]}.{current[2]} is supported.")
        return True

    _status(
        "FAIL",
        (
            "Python version is outside tested range "
            f"{PYTHON_MIN[0]}.{PYTHON_MIN[1]} - {PYTHON_MAX[0]}.{PYTHON_MAX[1]} "
            f"(current: {current[0]}.{current[1]}.{current[2]})."
        ),
    )
    return False


def check_dependency_versions() -> bool:
    ok = True
    for package_name, expected_version in REQUIRED_PACKAGES.items():
        try:
            installed_version = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            _status("FAIL", f"{package_name} is not installed.")
            ok = False
            continue

        if installed_version == expected_version:
            _status("OK", f"{package_name}=={installed_version}")
        else:
            _status(
                "WARN",
                f"{package_name} version mismatch (installed {installed_version}, expected {expected_version})",
            )
    return ok


def check_opengl() -> bool:
    base: Optional[object] = None
    try:
        from panda3d.core import loadPrcFileData
        from direct.showbase.ShowBase import ShowBase

        loadPrcFileData("", "window-type offscreen")
        loadPrcFileData("", "audio-library-name null")
        loadPrcFileData("", "notify-level warning")

        base = ShowBase(windowType="offscreen")
        if not base.win:
            _status("FAIL", "OpenGL context could not be created (no Panda3D window).")
            return False

        gsg = base.win.getGsg()
        vendor = gsg.getDriverVendor() if gsg else "unknown"
        renderer = gsg.getDriverRenderer() if gsg else "unknown"
        version = gsg.getDriverVersion() if gsg else "unknown"
        _status("OK", f"OpenGL renderer detected: {vendor} | {renderer} | {version}")
        return True
    except Exception as exc:  # pragma: no cover - diagnostic path
        _status("FAIL", f"OpenGL preflight failed: {exc}")
        return False
    finally:
        if base is not None:
            try:
                base.destroy()
            except Exception:
                pass


def main() -> int:
    _status("INFO", f"Platform: {platform.platform()}")
    _status("INFO", f"Executable: {sys.executable}")

    all_ok = True
    all_ok = check_python_version() and all_ok
    all_ok = check_dependency_versions() and all_ok
    all_ok = check_opengl() and all_ok

    if all_ok:
        _status("DONE", "Preflight passed. You can run: python main.py")
        return 0

    _status("DONE", "Preflight has failures. Check messages above before running.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
