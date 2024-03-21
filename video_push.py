import subprocess
import time

import cv2
import librosa
import numpy as np

push_url_video = "rtmp://127.0.0.1:1935/live/video"
push_url_audio = "rtmp://127.0.0.1:1935/live/audio"
cap = cv2.VideoCapture("output_1710743841513.mp4")
fps = float(cap.get(5))
width = int(cap.get(3))
height = int(cap.get(4))


def video_push():
    command = ['ffmpeg',
               '-y',
               '-an',
               '-f', 'rawvideo',
               '-vcodec', 'rawvideo',
               '-pix_fmt', 'bgr24',  # 像素格式
               '-s', "{}x{}".format(width, height),
               '-r', str(fps),
               '-i', '-',
               '-vcodec', "libx264",
               '-pix_fmt', 'yuv420p',
               '-g', '1',
               '-b:v', "4000k",
               '-bf', '0',
               "-rtmp_buffer", "100",
               '-f', 'flv',
               push_url_video]  # rtsp rtmp

    pipe1 = subprocess.Popen(command, shell=False, stdin=subprocess.PIPE)

    try:
        while True:  # 循环播放
            for _ in range(int(cap.get(7))):
                t0 = time.time()
                ret, img = cap.read()
                if not ret:
                    break
                pipe1.stdin.write(img.tobytes())
                wait = 1 / fps - (time.time() - t0)
                if wait > 0:
                    time.sleep(1 / fps - (time.time() - t0))  # 需要根据帧率进行等待
    finally:
        pipe1.terminate()


def audio_push():
    speech_array = librosa.load("aud_1710743841513.wav", sr=44100)  # 对于rtmp, 音频速率是有要求的，这里采用了44100
    speech_array = (np.array(speech_array[0]) * 32767).astype(np.int16)  # 转为整型

    command = ['ffmpeg',  # linux不用指定
               '-f', 's16le',
               '-y',
               '-vn',
               '-acodec', 'pcm_s16le',
               '-i', '-',
               '-ac', '1',
               '-ar', '44100',
               "-rtmp_buffer", '100',
               '-acodec', 'aac',
               '-f', 'flv',  # flv rtsp
               push_url_audio]  # rtsp rtmp

    pipe2 = subprocess.Popen(command, shell=False, stdin=subprocess.PIPE)

    wav_frame_num = int(44100 / fps)  # 这里需要注意的是，fps要保证能被整除，不然后续需要做额外处理
    try:
        while True:  # 循环播放
            for i in range(int(cap.get(7))):
                speech = speech_array[i * wav_frame_num:(i + 1) * wav_frame_num]
                pipe2.stdin.write(speech.tobytes())
    finally:
        pipe2.terminate()


if __name__ == '__main__':
    audio_push()
