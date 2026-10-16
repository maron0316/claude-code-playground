#!/usr/bin/env python3
"""MLX Whisper で、音声・動画をこの Mac の中だけで文字起こしする（AI が実行する道具）。

使い方（AI が実行する。使う人にターミナルを打たせない）:
  python3 transcribe.py check                 # 入っているか・入れられるかを調べる（何も変えない）
  python3 transcribe.py setup --yes           # 本人の OK をもらってから、専用の場所に入れる
  python3 transcribe.py run <ファイル> [--language ja] [--out <保存先フォルダ>]

入れる場所: ~/.my-video-editor/mlx-whisper/（このフォルダの外は変えない）
音声・動画はインターネットに送らない。最初の文字起こしのときだけ、モデル（約1.6GB）を
Hugging Face（mlx-community/whisper-large-v3-turbo）からダウンロードする。
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HOME_DIR = Path(os.environ.get("MVE_WHISPER_HOME", Path.home() / ".my-video-editor" / "mlx-whisper"))
VENV = HOME_DIR / ".venv"
VBIN = VENV / "bin"
DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo"
DEFAULT_OUT = Path.home() / ".my-video-editor" / "transcripts"
NEED_FREE_GB = 5
PY_CANDIDATES = [
    "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
    "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
    "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
    "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3",
    "/opt/homebrew/bin/python3.13", "/opt/homebrew/bin/python3.12",
    "/opt/homebrew/bin/python3.11", "/opt/homebrew/bin/python3.10",
    "/Library/Frameworks/Python.framework/Versions/Current/bin/python3",
    "/opt/homebrew/bin/python3", "/usr/local/bin/python3", "/usr/bin/python3",
]


def py_version(exe):
    try:
        out = subprocess.run([exe, "-c", "import sys,platform;print(sys.version_info[0],sys.version_info[1],platform.machine())"],
                             capture_output=True, text=True, timeout=30)
        major, minor, mach = out.stdout.split()
        return int(major), int(minor), mach
    except Exception:
        return None


def find_python():
    seen = set()
    for c in PY_CANDIDATES + [shutil.which("python3") or ""]:
        if not c or not os.path.exists(c):
            continue
        real = os.path.realpath(c)
        if real in seen:
            continue
        seen.add(real)
        v = py_version(c)
        if v and v[2] == "arm64" and (3, 10) <= (v[0], v[1]):
            return c, v
    return None, None


def installed():
    return (VBIN / "mlx_whisper").is_file() and (VBIN / "ffmpeg").exists()


def cmd_check(_args):
    mac = platform.system() == "Darwin"
    arm = platform.machine() == "arm64"
    free_gb = shutil.disk_usage(Path.home()).free / 1e9
    py, v = find_python()
    print(f"Mac: {'はい' if mac else 'いいえ'}")
    print(f"Apple シリコン（M1 以降）: {'はい' if arm else 'いいえ'}")
    print(f"空き容量: 約{free_gb:.0f}GB（目安 {NEED_FREE_GB}GB 以上）")
    print(f"使える Python（3.10 以上）: {py + '（' + str(v[0]) + '.' + str(v[1]) + '）' if py else 'なし'}")
    print(f"MLX Whisper: {'入っています（' + str(HOME_DIR) + '）' if installed() else 'まだ入っていません'}")
    if not (mac and arm):
        print("判定: このパソコンでは MLX Whisper を使えません（Apple シリコンの Mac だけで動きます）")
        return 2
    if installed():
        print("判定: すぐに文字起こしできます")
        return 0
    if not py:
        print("判定: 先に Python（3.10 以上）を入れる必要があります（references/transcribe-setup.md）")
        return 3
    if free_gb < NEED_FREE_GB:
        print("判定: 空き容量が足りないかもしれません")
        return 4
    print("判定: 入れられます（本人の OK をもらってから setup --yes）")
    return 0


def cmd_setup(args):
    if not args.yes:
        print("本人の OK をもらってから --yes を付けて実行してください。何も変えていません。")
        return 1
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        print("Apple シリコンの Mac ではないので入れられません。")
        return 2
    py, v = find_python()
    if not py:
        print("Python（3.10 以上）が見つかりません。references/transcribe-setup.md の手順で、先に本人に入れてもらってください。")
        return 3
    HOME_DIR.mkdir(parents=True, exist_ok=True)
    if not VENV.exists():
        print(f"専用の環境を作ります: {VENV}（Python {v[0]}.{v[1]}）", flush=True)
        subprocess.run([py, "-m", "venv", str(VENV)], check=True)
    pip = [str(VBIN / "python"), "-m", "pip", "install", "--disable-pip-version-check", "-q"]
    print("部品をダウンロードして入れます（1GB ほど。数分かかります）", flush=True)
    subprocess.run(pip + ["--upgrade", "pip"], check=True)
    subprocess.run(pip + ["mlx-whisper", "imageio-ffmpeg"], check=True)
    ff = subprocess.run([str(VBIN / "python"), "-c", "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"],
                        capture_output=True, text=True, check=True).stdout.strip()
    link = VBIN / "ffmpeg"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(ff)
    ok = installed()
    print("完了: MLX Whisper を入れました" if ok else "うまく入りませんでした。上のメッセージを本人に見せてください")
    return 0 if ok else 1


def cmd_run(args):
    if not installed():
        print("MLX Whisper がまだ入っていません。先に check と setup を行ってください。")
        return 1
    src = Path(args.media).expanduser().resolve()
    if not src.is_file():
        print(f"ファイルが見つかりません: {src}")
        return 1
    out_base = Path(args.out).expanduser().resolve() if args.out else DEFAULT_OUT
    out = out_base / f"{src.stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    out.mkdir(parents=True, exist_ok=False)
    cmd = [str(VBIN / "mlx_whisper"), str(src), "--model", args.model, "--output-dir", str(out),
           "--output-format", "all", "--verbose", "False", "--condition-on-previous-text", "False"]
    if args.language != "auto":
        cmd += ["--language", args.language]
    env = dict(os.environ, PATH=f"{VBIN}:{os.environ.get('PATH', '')}")
    print(f"文字起こし中: {src.name}（はじめての時は、モデル約1.6GBのダウンロードがあります）", flush=True)
    r = subprocess.run(cmd, env=env)
    txt = out / f"{src.stem}.txt"
    if r.returncode or not txt.is_file():
        print(f"うまくいきませんでした。保存先: {out}")
        return 1
    print(f"完了: {txt}")
    print(f"字幕ファイル: {out / (src.stem + '.srt')}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="MLX Whisper でこの Mac の中だけで文字起こし")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    s = sub.add_parser("setup")
    s.add_argument("--yes", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("media")
    r.add_argument("--language", choices=("auto", "ja", "en"), default="auto")
    r.add_argument("--out")
    r.add_argument("--model", default=DEFAULT_MODEL)
    a = ap.parse_args()
    return {"check": cmd_check, "setup": cmd_setup, "run": cmd_run}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
