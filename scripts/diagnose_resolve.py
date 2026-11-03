#!/usr/bin/env python3
"""Diagnóstico de lectura para Resolve en macOS; sin dependencias externas."""

import argparse
import json
from pathlib import Path
import plistlib
import subprocess
import sys


# Se ejecuta en el intérprete de Resolve, separado para limitar bloqueos nativos.
PROBE = r'''
import json
import sys
try:
    import DaVinciResolveScript as api
except Exception as exc:
    print(json.dumps({"status": "import_failed", "error_type": type(exc).__name__}))
    sys.exit(1)
try:
    resolve = api.scriptapp("Resolve")
    if resolve is None:
        result = {"status": "unreachable"}
    else:
        manager = resolve.GetProjectManager()
        result = {
            "status": "ok" if manager is not None else "project_manager_unavailable",
            "product": resolve.GetProductName(),
            "version": resolve.GetVersion(),
            "version_string": resolve.GetVersionString(),
            "project_manager_access": manager is not None,
            "python_version": sys.version.split()[0],
        }
    print(json.dumps(result))
    sys.exit(0 if result["status"] == "ok" else 1)
except Exception as exc:
    print(json.dumps({"status": "api_failed", "error_type": type(exc).__name__}))
    sys.exit(1)
'''


def diagnose(app, timeout):
    report = {"schema_version": 1, "read_only": True}
    if sys.platform != "darwin":
        return dict(report, status="unsupported_platform")
    try:
        with (app / "Contents/Info.plist").open("rb") as source:
            info = plistlib.load(source)
        report["installed_version"] = info.get("CFBundleShortVersionString")
    except (OSError, plistlib.InvalidFileException, ValueError):
        return dict(report, status="installation_unavailable")
    runtime = app / "Contents/Applications/ResolvePython"
    if not runtime.is_file():
        return dict(report, status="runtime_unavailable")
    try:
        process = subprocess.run(
            [str(runtime), "-c", PROBE], capture_output=True,
            text=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return dict(report, status="timeout")
    except OSError as exc:
        return dict(report, status="runtime_failed", error_type=type(exc).__name__)
    # No propagar stdout/stderr nativo: puede incluir datos privados o ruido.
    try:
        payload = json.loads(process.stdout.strip().splitlines()[-1])
        if not isinstance(payload, dict) or "status" not in payload:
            raise ValueError("invalid probe response")
    except (ValueError, IndexError):
        return dict(report, status="invalid_response", returncode=process.returncode)
    report.update(payload)
    report["returncode"] = process.returncode
    if process.returncode != 0 and report["status"] == "ok":
        report["status"] = "runtime_failed"
    return report


def positive_timeout(value):
    number = float(value)
    if not 0 < number <= 60:
        raise argparse.ArgumentTypeError("timeout debe estar entre 0 y 60 segundos")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, default=Path(
        "/Applications/DaVinci Resolve/DaVinci Resolve.app"))
    parser.add_argument("--timeout", type=positive_timeout, default=15)
    args = parser.parse_args()
    report = diagnose(args.app, args.timeout)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
