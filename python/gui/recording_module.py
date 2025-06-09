import os
import time
import re
import subprocess
from datetime import datetime
import threading

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def wait_until_file_closed(path, timeout=10):
    for _ in range(timeout * 10):
        try:
            with open(path, 'a'):
                return True
        except PermissionError:
            time.sleep(0.1)
    return False

def get_duration_by_ffprobe(ts_file, log_callback=None):
    try:
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            ts_file
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        return float(output)
    except Exception as e:
        if log_callback:
            log_callback(f"⚠️ ffprobe で長さ取得に失敗しました: {e}")
        return 3600

def ffmpeg_convert_with_progress(input_ts, output_mp4, duration_sec, log_callback=None):
    cmd = [
        "ffmpeg", "-hwaccel", "auto", "-i", input_ts,
        "-c:v", "libx264", "-preset", "medium",
        "-c:a", "aac", "-b:a", "128k", "-y", output_mp4
    ]

    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    time_regex = re.compile(r'time=(\d+):(\d+):(\d+)\.(\d+)')
    last_progress = -1

    for line in process.stderr:
        # ffmpegの詳細ログは表示しない（必要なら進捗のみ）
        # 進捗を抽出してログに出す
        match = time_regex.search(line)
        if match:
            h, m, s, ms = map(int, match.groups())
            elapsed = h * 3600 + m * 60 + s + ms / 100.0
            progress = int((elapsed / duration_sec) * 100)
            if progress > last_progress and progress <= 100:
                if log_callback:
                    # 先頭に改行や\rは付けず、ログの行末にスペースを入れて更新をわかりやすく
                    log_callback(f"🔄 エンコード進行度: {progress}% ")
                last_progress = progress
        # 進捗以外のffmpegログは無視

    process.wait()
    time.sleep(1)
    if log_callback:
        # 改行なしでエンコード完了ログを表示
        log_callback("✅ エンコード完了")




def run_streamlink_with_log(twitch_url, ts_file, log_callback):
    streamlink_cmd = [
        "streamlink", "--twitch-disable-ads", twitch_url, "best", "-o", ts_file
    ]
    proc = subprocess.Popen(streamlink_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in proc.stdout:
        if log_callback:
            log_callback(line.strip())

    proc.wait()
    return proc


def record_twitch_to_mp4(twitch_url, duration_seconds, log_callback=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ts_file = f"recording_{timestamp}.ts"
    mp4_file = f"recording_{timestamp}.mp4"

    if log_callback:
        log_callback("🎥 録画を開始します...")

    proc = subprocess.Popen(
        ["streamlink", "--twitch-disable-ads", twitch_url, "best", "-o", ts_file],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    def log_stream():
        for line in proc.stdout:
            if log_callback:
                log_callback(line.strip())

    threading.Thread(target=log_stream, daemon=True).start()

    if duration_seconds > 0:
        time.sleep(duration_seconds)
        subprocess.run("taskkill /IM streamlink.exe /T /F", shell=True)

    proc.wait()

    if log_callback:
        log_callback("\n🔄 MP4に変換中")

    duration_sec = get_duration_by_ffprobe(ts_file, log_callback)
    ffmpeg_convert_with_progress(ts_file, mp4_file, duration_sec, log_callback)

    if os.path.exists(ts_file):
        if wait_until_file_closed(ts_file):
            try:
                os.remove(ts_file)
            except Exception as e:
                if log_callback:
                    log_callback(f"⚠️ tsファイル削除失敗: {e}")
        else:
            if log_callback:
                log_callback(f"⚠️ tsファイルが使用中のため削除できませんでした: {ts_file}")

    if os.path.exists(mp4_file):
        if log_callback:
            log_callback(f"🎉 完成ファイル: {mp4_file}")
        return mp4_file
    else:
        if log_callback:
            log_callback("❌ MP4ファイル作成失敗")
        return None

