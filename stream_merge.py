import subprocess
import threading

import video_push

if __name__ == '__main__':
    video_thread = threading.Thread(video_push.video_push())
    audio_thread = threading.Thread(video_push.audio_push())

    video_thread.start()
    audio_thread.start()
    command = ['ffmpeg',  # linux不用指定
               '-i', 'rtmp://127.0.0.1:1935/live/video',
               '-i', 'rtmp://127.0.0.1:1935/live/audio',
               '-map', '0:v',
               '-map', '1:a',
               '-acodec', 'copy',
               '-vcodec', 'copy',
               '-copyts',
               '-rtmp_buffer', '100',
               '-f', 'flv',  # flv rtsp
               'rtmp://127.0.0.1:1935/live/hls']  # rtsp rtmp
    pipe = subprocess.Popen(command, shell=False, stdin=subprocess.PIPE)
