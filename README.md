# ffmpeg-cut-helper
Automate cut parts of video using FFmpeg

Ussge:
```bash
$ ffmpeg-cut-helper.py -i input.mp4 -t timestamps.txt -o output.mp4
```

Inverse mode (join regions instead of cutting holes) and custom encoding parameters:
```bash
$ ffmpeg-cut-helper.py -i input.mp4 -t timestamps.txt -o output.mp4  -j -c "-c:a aac -b:a 128k -c:v libx264 -crf 18"
```

Timestamps file example (timestamps.txt):
```
47:59 49:00
17:25 18:20
```
