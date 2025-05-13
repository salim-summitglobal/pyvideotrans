import os
import requests
import re
import time
import threading
import concurrent.futures
from pathlib import Path
import sys

from videotrans.configure import config

# Configuration
ROOT_DIR = config.ROOT_DIR
VIDEO_DIR = f"{ROOT_DIR}/video"
HOST = "127.0.0.1"
PORT = 9011

if Path(ROOT_DIR+'/host.txt').is_file():
    host_str = Path(ROOT_DIR+'/host.txt').read_text(encoding='utf-8').strip()
    host_str = re.sub(r'https?://','', host_str).split(':')
    if len(host_str) > 0:
        HOST = host_str[0]
    if len(host_str) == 2:
        PORT = int(host_str[1])

API_URL = f"http://{HOST}:{PORT}/trans_video"
API_URL_STATUS = f"http://{HOST}:{PORT}/task_status"
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.flv')
TARGET_LANGUAGE = "id"
SOURCE_LANGUAGE = "auto"

print_lock = threading.Lock()
task_statuses = {}
task_file_map = {}
stop_event = threading.Event()

def find_video_files(directory: str) -> list[str]:
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Folder not found: {directory}")

    videos = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.lower().endswith(VIDEO_EXTENSIONS)
    ]

    return videos

def thread_safe_print(message, end='\n'):
    with print_lock:
        print(message, end=end)
        sys.stdout.flush()

def submit_video(filepath: str) -> str:
    try:
        data = {
            "name": filepath,
            "recogn_type": 0,
            "split_type": "overall",
            "model_name": "tiny",
            "detect_language": "auto",
            "translate_type": 0,
            "source_language": SOURCE_LANGUAGE,
            "target_language": TARGET_LANGUAGE,
            "tts_type": 0,
            "voice_role": "No",
            "voice_rate": "+0%",
            "volume": "+0%",
            "pitch": "+0Hz",
            "back_audio": "origin",
            "subtitle_type": 1,
            "append_video": False,
            "is_cuda": False,
        }

        thread_safe_print(f"Submitting {os.path.basename(filepath)}...", end='')

        response = requests.post(API_URL, json=data)
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 0:
            task_id = result.get('task_id', 'unknown')
            thread_safe_print(f"\rSuccess: {os.path.basename(filepath)} -> Task ID: {task_id}")
            task_statuses[task_id] = "Submitted"
            task_file_map[task_id] = os.path.basename(filepath)
            return task_id
        else:
            error_msg = result.get('msg', 'Unknown error')
            thread_safe_print(f"\rError: {os.path.basename(filepath)} -> {error_msg}")
            return None

    except requests.exceptions.RequestException as e:
        thread_safe_print(f"\r✗ Failed: {os.path.basename(filepath)} -> {e}")
        return None

def monitor_task_status(task_id: str):
    if not task_id:
        return

    count = 0
    filename = task_file_map.get(task_id, "Unknown")
    spinner = ["-", "\\", "|", "/"][count % 4]

    while not stop_event.is_set():
        try:
            count += 1

            status_msg = requests.get(f"{API_URL_STATUS}?task_id={task_id}")
            status_msg.raise_for_status()

            try:
                status_data = status_msg.json()
            except ValueError:
                task_statuses[task_id] = f"JSON error... Retrying... {spinner}"
                time.sleep(2)
                continue

            if status_data.get('code') == 0:
                if 'data' in status_data and 'absolute_path' in status_data['data']:
                    output_path = status_data['data']['absolute_path']
                    task_statuses[task_id] = f"COMPLETED: {filename} -> {output_path}"
                else:
                    task_statuses[task_id] = f"COMPLETED: {filename} (path not found)"
                return
            elif status_data.get('code') == 3:
                task_statuses[task_id] = f"ERROR: {filename} -> {status_data.get('msg', 'Unknown error')}"
                return
            else:
                status_msg_text = status_data.get('msg', 'Processing...')
                if len(status_msg_text) > 40:
                    status_msg_text = status_msg_text[:37] + "..."
                task_statuses[task_id] = f"{spinner} {filename}: {status_msg_text}"

        except requests.exceptions.RequestException:
            task_statuses[task_id] = f"{spinner} {filename}: Connection error... Retrying..."

        time.sleep(2)

def display_status_board():
    while not stop_event.is_set() and task_statuses:
        completed = 0
        total = len(task_statuses)
        for status in task_statuses.values():
            if status.startswith("COMPLETED") or status.startswith("ERROR"):
                completed += 1

        with print_lock:
            os.system('cls' if os.name == 'nt' else 'clear')

            print(f"Processing {total} videos: {completed}/{total} completed\n")
            print("Status Board:")
            print("=" * 80)

            for task_id, status in task_statuses.items():
                print(f"{task_id}: {status}")

            print("\nPress Ctrl+C to stop...")
            sys.stdout.flush()

        if completed == total:
            stop_event.set()
            break

        time.sleep(1)

def process_videos_in_parallel(video_files, max_workers=3):
    task_ids = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_video = {executor.submit(submit_video, video): video for video in video_files}
        for future in concurrent.futures.as_completed(future_to_video):
            task_id = future.result()
            if task_id:
                task_ids.append(task_id)

    thread_safe_print(f"\nSubmitted {len(task_ids)} videos for processing.")

    monitor_threads = []
    for task_id in task_ids:
        thread = threading.Thread(target=monitor_task_status, args=(task_id,))
        thread.daemon = True
        thread.start()
        monitor_threads.append(thread)

    status_board_thread = threading.Thread(target=display_status_board)
    status_board_thread.daemon = True
    status_board_thread.start()

    try:
        status_board_thread.join()

        thread_safe_print("\nAll tasks completed!")
        thread_safe_print("\nTask Summary:")
        for task_id, status in task_statuses.items():
            thread_safe_print(f"  -> {task_id}: {status}")

    except KeyboardInterrupt:
        thread_safe_print("\nProcess interrupted by user.")
        stop_event.set()

    return task_ids

if __name__ == "__main__":
    try:
        video_files = find_video_files(VIDEO_DIR)
        total_videos = len(video_files)

        if total_videos == 0:
            print(f"No videos found in {VIDEO_DIR}")
            exit(0)

        print(f"Found {total_videos} video(s) to process:")
        for video in video_files:
            print(f"  - {os.path.basename(video)}")

        max_parallel = min(max(2, total_videos), 5)
        print(f"\nStarting parallel processing with up to {max_parallel} videos at once...")

        task_ids = process_videos_in_parallel(video_files, max_workers=max_parallel)

        print(f"\nProcessing complete: {len(task_ids)}/{total_videos} videos successfully processed")

    except KeyboardInterrupt:
        print("\nProcess terminated by user.")
        stop_event.set()
        sys.exit(0)