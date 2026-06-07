"""Dev test: inject a real photo into the pipeline and check findings.

Usage:
    python test_inject.py <image_path> [rover_id]

Example:
    python test_inject.py ~/Desktop/backpack.jpg rover1

Steps:
    1. Start a mission in the UI first (sets mission:criteria in Redis).
    2. Run this script with a real photo.
    3. Watch the Findings screen in the UI for the result.
"""
import base64
import json
import sys
import time
import urllib.request

BACKEND = "http://localhost:8000"


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_inject.py <image_path> [rover_id]")
        sys.exit(1)

    image_path = sys.argv[1]
    rover_id = sys.argv[2] if len(sys.argv) > 2 else "rover1"

    # --- Read + encode image ---
    with open(image_path, "rb") as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode("ascii")
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    data_uri = f"data:{mime};base64,{b64}"

    # --- Check mission criteria is set ---
    try:
        with urllib.request.urlopen(f"{BACKEND}/mission/status") as r:
            mission = json.loads(r.read())
        criteria = mission.get("criteria") or mission.get("goal") or ""
        if not criteria or criteria == "idle":
            print("⚠️  No active mission criteria found in Redis.")
            print("   Start a mission in the UI first, then re-run this script.")
            sys.exit(1)
        print(f"✓ Mission criteria: {criteria!r}")
    except Exception as e:
        print(f"✗ Could not reach backend at {BACKEND}: {e}")
        sys.exit(1)

    # --- Push the frame ---
    payload = json.dumps({
        "photo": data_uri,
        "caption": f"test inject: {image_path}",
        "coord": {"x": 10, "y": 10},
    }).encode()
    req = urllib.request.Request(
        f"{BACKEND}/rovers/{rover_id}/images",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())
        print(f"✓ Frame pushed to {rover_id} (ts={resp.get('frame', {}).get('ts', '?'):.1f})")
    except Exception as e:
        print(f"✗ Failed to push frame: {e}")
        sys.exit(1)

    # --- Wait for vision pipeline to run ---
    print("  Waiting for vision pipeline (up to 30s)...")
    deadline = time.time() + 30
    found = []
    while time.time() < deadline:
        time.sleep(3)
        try:
            with urllib.request.urlopen(f"{BACKEND}/findings?limit=5") as r:
                data = json.loads(r.read())
            found = data.get("findings", [])
            if found:
                break
        except Exception:
            pass
        print("  ... still waiting")

    # --- Report ---
    if not found:
        print("\n✗ No findings after 30s.")
        print("  Possible reasons:")
        print("  - AGENTS_AUTORUN=false in .env")
        print("  - OPENAI_API_KEY not set")
        print("  - GPT-4o found nothing matching the criteria in your photo")
        print(f"  - Check backend logs for errors")
    else:
        print(f"\n✓ {len(found)} finding(s) detected:\n")
        for f in found:
            conf = f.get("confidence")
            conf_str = f"{conf*100:.0f}%" if isinstance(conf, (int, float)) else "n/a"
            print(f"  [{f.get('rover_id')}] {f.get('label')} — {conf_str} confidence")
            print(f"  criteria matched: {f.get('criteria')}")
            print(f"  {f.get('summary')}")
            print()


if __name__ == "__main__":
    main()
