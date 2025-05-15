import cv2
import numpy as np
import time
from ultralytics import YOLO
from absl import app, flags
import sys
import logging
import subprocess
import threading
import queue

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

FLAGS = flags.FLAGS
if not FLAGS.is_parsed():
    flags.DEFINE_string("model", "./models/yolo11n_int8_openvino_model", "Path to YOLO11 OpenVINO model")
    flags.DEFINE_string("video", "./input_video/highway.mp4", "Input video file")
    flags.DEFINE_float("conf", 0.1, "Confidence threshold for detection")
    flags.DEFINE_string("rtsp_url", "rtsp://localhost:8554/mystream", "RTSP output URL for MediaMTX")

def show_counter(frame, title, class_names, vehicle_count, x_init):
    overlay = frame.copy()
    y_init = 100
    gap = 30
    alpha = 0.5

    cv2.rectangle(overlay, (x_init - 5, y_init - 35), (x_init + 200, 265), (0, 255, 0), -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    cv2.putText(frame, title, (x_init, y_init - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    for vehicle_id, count in vehicle_count.items():
        y_init += gap
        vehicle_name = class_names[vehicle_id]
        vehicle_count_str = f"{count:03d}"
        cv2.putText(frame, vehicle_name, (x_init, y_init), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(frame, vehicle_count_str, (x_init + 145, y_init), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

def read_ffmpeg_stderr(process, error_queue):
    while True:
        line = process.stderr.readline()
        if not line:
            break
        error_queue.put(line.strip())
        logger.error("FFmpeg stderr: %s", line.strip())

def start_ffmpeg_process(ffmpeg_command, error_queue):
    try:
        process = subprocess.Popen(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )
        stderr_thread = threading.Thread(target=read_ffmpeg_stderr, args=(process, error_queue))
        stderr_thread.daemon = True
        stderr_thread.start()
        logger.info("FFmpeg process started successfully")
        return process
    except Exception as e:
        logger.error("Failed to start FFmpeg process: %s", e)
        return None

def main(_argv):
    _argv = [sys.argv[0]]
    logger.info("Starting vehicle counting service...")

    # Load YOLO model
    logger.info("Loading YOLO model from %s", FLAGS.model)
    try:
        model = YOLO(FLAGS.model, task="detect")
    except Exception as e:
        logger.error("Failed to load YOLO model: %s", e)
        sys.exit(1)

    # Load class names
    classes_path = "coco.names"
    try:
        with open(classes_path, "r") as f:
            class_names = f.read().strip().split("\n")
        logger.info("Loaded %d class names", len(class_names))
    except Exception as e:
        logger.error("Failed to load class names: %s", e)
        sys.exit(1)

    # Generate random colors for classes
    np.random.seed(42)
    colors = np.random.randint(0, 255, size=(len(class_names), 3))

    # Vehicle counter setup
    entered_vehicle_ids = []
    exited_vehicle_ids = []
    vehicle_class_ids = [1, 2, 3, 5, 7]
    vehicle_entry_count = {1: 0, 2: 0, 3: 0, 5: 0, 7: 0}
    vehicle_exit_count = {1: 0, 2: 0, 3: 0, 5: 0, 7: 0}

    entry_line = {'x1': 160, 'y1': 558, 'x2': 708, 'y2': 558}
    exit_line = {'x1': 1155, 'y1': 558, 'x2': 1718, 'y2': 558}
    offset = 25

    batch_size = 2
    frames = []

    # FFmpeg command for RTSP streaming
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', '1920x1080',
        '-r', '30',
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-rtsp_transport', 'tcp',
        '-bufsize', '5000k',
        '-f', 'rtsp',
        FLAGS.rtsp_url
    ]
    logger.debug("FFmpeg command: %s", ' '.join(ffmpeg_command))

    # Queue for FFmpeg stderr
    error_queue = queue.Queue()
    max_retries = 3
    retry_delay = 2

    process = None
    for attempt in range(max_retries):
        process = start_ffmpeg_process(ffmpeg_command, error_queue)
        if process:
            break
        logger.warning("Retrying FFmpeg process start (%d/%d)...", attempt + 1, max_retries)
        time.sleep(retry_delay)
    if not process:
        logger.error("Failed to start FFmpeg after %d attempts", max_retries)
        sys.exit(1)

    # Video capture
    logger.info("Opening video source: %s", FLAGS.video)
    cap = cv2.VideoCapture(FLAGS.video)
    if not cap.isOpened():
        logger.error("Unable to open video source")
        process.terminate()
        sys.exit(1)

    start_time = time.time()
    while True:
        success, frame = cap.read()
        if not success:
            logger.info("End of video, looping...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frames.append(frame)

        # Draw counting line
        cv2.line(frame, (entry_line['x1'], entry_line['y1']), (exit_line['x2'], exit_line['y2']), (0, 127, 255), 3)

        if len(frames) == batch_size:
            try:
                results = model.track(frames, persist=True, tracker="bytetrack.yaml", conf=FLAGS.conf, verbose=False)
            except Exception as e:
                logger.error("Error during YOLO tracking: %s", e)
                frames = []
                continue

            frame = frames[-1]
            frames = []

            end_time = time.time()
            fps = batch_size / (end_time - start_time)
            fps = float(f"{fps:.2f}")
            start_time = end_time

            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.int().cpu().tolist()
                class_ids = results[0].boxes.cls.cpu().tolist()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                conf_scores = results[0].boxes.conf.cpu().tolist()

                for box, track_id, class_id, conf in zip(boxes, track_ids, class_ids, conf_scores):
                    x1, y1, x2, y2 = box
                    color = colors[int(class_id)]
                    B, G, R = map(int, color)
                    text = f"{class_names[int(class_id)]} {conf:.2f}"
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
                    cv2.rectangle(frame, (x1 - 1, y1 - 20), (x1 + len(text) * 12, y1), (B, G, R), -1)
                    cv2.putText(frame, text, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    if (center_x in range(entry_line['x1'], entry_line['x2'])) and (center_y in range(entry_line['y1'], entry_line['y1'] + offset)):
                        if int(track_id) not in entered_vehicle_ids and class_id in vehicle_class_ids:
                            vehicle_entry_count[class_id] += 1
                            entered_vehicle_ids.append(int(track_id))

                    if (center_x in range(exit_line['x1'], exit_line['x2'])) and (center_y in range(exit_line['y1'] - offset, exit_line['y1'])):
                        if int(track_id) not in exited_vehicle_ids and class_id in vehicle_class_ids:
                            vehicle_exit_count[class_id] += 1
                            exited_vehicle_ids.append(int(track_id))

            show_counter(frame, "Vehicle Enter", class_names, vehicle_entry_count, 10)
            show_counter(frame, "Vehicle Exit", class_names, vehicle_exit_count, 1710)

            try:
                process.stdin.write(frame.tobytes())
                logger.debug("Frame written to FFmpeg pipe")
                if process.poll() is not None:
                    logger.error("FFmpeg process terminated unexpectedly with return code %s", process.returncode)
                    while not error_queue.empty():
                        logger.error("FFmpeg error: %s", error_queue.get())
                    logger.info("Attempting to restart FFmpeg process...")
                    process = None
                    for attempt in range(max_retries):
                        process = start_ffmpeg_process(ffmpeg_command, error_queue)
                        if process:
                            logger.info("FFmpeg restarted successfully")
                            break
                        time.sleep(retry_delay)
                    if not process:
                        logger.error("Failed to restart FFmpeg process")
                        break
            except Exception as e:
                logger.error("Failed to write frame to FFmpeg pipe: %s", e)
                while not error_queue.empty():
                    logger.error("FFmpeg error: %s", error_queue.get())
                try:
                    process.terminate()
                except Exception:
                    pass
                time.sleep(retry_delay)
                process = start_ffmpeg_process(ffmpeg_command, error_queue)
                if not process:
                    logger.error("Failed to restart FFmpeg process")
                    break

    cap.release()
    if process:
        try:
            process.stdin.close()
            process.terminate()
        except Exception:
            pass
    while not error_queue.empty():
        logger.error("FFmpeg error: %s", error_queue.get())
    logger.info("Service terminated")

if __name__ == '__main__':
    app.run(main)