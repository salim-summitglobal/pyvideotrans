import os
import requests
import re
import time
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

API_URL = f"http://{HOST}:{PORT}/trans_video"
API_URL_STATUS = f"http://{HOST}:{PORT}/task_status"
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.flv')
TARGET_LANGUAGE = "en"
SOURCE_LANGUAGE = "auto"



def find_video_files(directory: str) -> list[str]:
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Folder not found: {directory}")

    videos = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.lower().endswith(VIDEO_EXTENSIONS)
    ]

    return videos

def clear_line():
    print("\r" + " " * 80, end="")
    print("\r", end="")
    sys.stdout.flush()

def process_video(filepath: str) -> None:
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

        print(f"Submitting {os.path.basename(filepath)}...", end='')
        sys.stdout.flush()

        response = requests.post(API_URL, json=data)
        response.raise_for_status()
        result = response.json()
        status = False

        if result.get('code') == 0:
            task_id = result.get('task_id', 'unknown')
            clear_line()
            print(f"Success: {os.path.basename(filepath)} -> Task ID: {task_id}")
        else:
            error_msg = result.get('msg', 'Unknown error')
            clear_line()
            print(f"Error: {os.path.basename(filepath)} -> {error_msg}")
            return None

        if not task_id:
            clear_line()
            print(f"✗ Failed: {os.path.basename(filepath)} -> No task ID received")
            return None

        print(f"Starting status checks for task {task_id}...")

        count = 0
        while not status:
            try:
                spinner = ["-", "\\", "|", "/"][count % 4]
                count += 1

                clear_line()
                print(f"Checking status: {spinner} Task: {task_id}", end="")
                sys.stdout.flush()

                status_msg = requests.get(f"{API_URL_STATUS}?task_id={task_id}")
                status_msg.raise_for_status()

                try:
                    status_data = status_msg.json()
                except ValueError as json_err:
                    clear_line()
                    print(f"JSON error: {str(json_err)[:30]}... Retrying...", end="")
                    sys.stdout.flush()
                    time.sleep(2)
                    continue

                if status_data.get('code') == 0:
                    status = True
                    clear_line()
                    print(f"Task {task_id} completed successfully")

                    if 'data' in status_data and 'absolute_path' in status_data['data']:
                        print(f"Output path: {status_data['data']['absolute_path']}")
                    else:
                        print("Output path not found in response")

                elif status_data.get('code') == 3:
                    status = True
                    clear_line()
                    print(f"Task {task_id} Error: {status_data.get('msg', 'Unknown error')}")

                else:
                    status_msg_text = status_data.get('msg', 'Processing...')
                    if len(status_msg_text) > 40:
                        status_msg_text = status_msg_text[:37] + "..."

                    clear_line()
                    print(f"Status: {spinner} {status_msg_text}", end="")
                    sys.stdout.flush()
                    time.sleep(2)

            except Exception as req_err:
                clear_line()
                print(f"Connection error: {str(req_err)[:30]}... Retrying...", end="")
                sys.stdout.flush()
                time.sleep(5)
                continue

        return task_id
    except Exception as e:
        clear_line()
        print(f"✗ Failed: {os.path.basename(filepath)} -> {e}")
        return None

if __name__ == "__main__":
    video_files = find_video_files(VIDEO_DIR)
    total_videos = len(video_files)

    if total_videos == 0:
        print(f"No videos found in {VIDEO_DIR}")
        exit(0)

    print(f"Found {total_videos} video(s) to process:")
    for video in video_files:
        print(f"  - {os.path.basename(video)}")

    print("\nStarting audio detection and processing...")

    successful = 0
    task_ids = []

    for idx, video in enumerate(video_files):
        print(f"\nProcessing video {idx+1}/{total_videos}...")
        task_id = process_video(video)

        if task_id:
            successful += 1
            task_ids.append(task_id)

        if idx < total_videos - 1:
            time.sleep(1)

    print(f"\nProcessing complete: {successful}/{total_videos} videos successfully submitted")

    if task_ids:
        print("\nTask IDs:")
        for task_id in task_ids:
            print(f"  -> {task_id}")