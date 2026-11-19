#!/usr/bin/env python3
"""Fail unless the example app's resolved Swift package graph links Mixpanel from the DLCT fork.

DayLight Creative Technologies fork. Run after `flutter build ios` of packages/mixpanel_flutter/example with Swift
Package Manager enabled. Exit 0 only when:
  - packages/mixpanel_flutter/ios/mixpanel_flutter/Package.swift depends on dlct_mixpanel_swift by a 40-hex revision;
  - the example's Package.resolved pins exactly one dlct_mixpanel_swift, at that revision;
  - no pin's location is github.com/mixpanel/mixpanel-swift (mixpanel-swift-common is a different package);
  - the example's Podfile.lock, if any, lists no Mixpanel-swift pod.
Exit 1 names each finding; exit 2 when an input cannot be read.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PKG = ROOT / "packages/mixpanel_flutter"
MANIFEST = PKG / "ios/mixpanel_flutter/Package.swift"
RESOLVED = PKG / "example/ios/Runner.xcworkspace/xcshareddata/swiftpm/Package.resolved"
PODFILE_LOCK = PKG / "example/ios/Podfile.lock"
FORK_RE = re.compile(
    r'url:\s*"https://github\.com/DayLight-Creative-Technologies/dlct_mixpanel_swift\.git",\s*revision:\s*"([0-9a-f]{40})"')
UPSTREAM_RE = re.compile(r"github\.com/mixpanel/mixpanel-swift(\.git)?/?$", re.IGNORECASE)


def main() -> int:
    try:
        manifest = MANIFEST.read_text()
        pins = json.loads(RESOLVED.read_text())["pins"]
    except (OSError, ValueError, KeyError) as exc:
        print(f"COULD NOT VERIFY: {exc}")
        return 2
    findings = []
    match = FORK_RE.search(manifest)
    if not match:
        findings.append(f"{MANIFEST.relative_to(ROOT)} does not depend on dlct_mixpanel_swift by a 40-hex revision")
    if "mixpanel/mixpanel-swift.git" in manifest:
        findings.append(f"{MANIFEST.relative_to(ROOT)} still names upstream mixpanel/mixpanel-swift")
    fork_pins = [p for p in pins if p.get("identity") == "dlct_mixpanel_swift"]
    if len(fork_pins) != 1:
        findings.append(f"Package.resolved holds {len(fork_pins)} dlct_mixpanel_swift pin(s), not exactly 1")
    elif match and fork_pins[0].get("state", {}).get("revision") != match.group(1):
        findings.append(f"Package.resolved pins dlct_mixpanel_swift at {fork_pins[0].get('state')}, "
                        f"not the manifest's revision {match.group(1)}")
    for pin in pins:
        if UPSTREAM_RE.search(pin.get("location", "")):
            findings.append(f"Package.resolved holds upstream {pin.get('identity')} at {pin.get('location')}")
    if PODFILE_LOCK.exists() and "Mixpanel-swift" in PODFILE_LOCK.read_text():
        findings.append(f"{PODFILE_LOCK.relative_to(ROOT)} lists the Mixpanel-swift pod (CocoaPods, not SwiftPM)")
    if findings:
        for finding in findings:
            print(f"FAIL: {finding}")
        return 1
    print(f"PASS: Mixpanel resolves from dlct_mixpanel_swift at {match.group(1)}; no upstream mixpanel-swift "
          f"among {len(pins)} pin(s): " + ", ".join(sorted(p["identity"] for p in pins)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
