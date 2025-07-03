# TR008W

This project helps us to controll the drone TR008W using our computer at the same time as we can see the video camera.

## Getting Started

In order to use this, we will use python 3.0. However, you can execute the process with mostly any version.

### Prerequisites
You might need to install some libraries:
- getkey
- enum
- socket
- struct
- numpy
- subprocess
- opencv

If you have already installed them, there won't be any problem. However, if you get an error like ```No module named <module name>``` then, you should install the library using pip or any other method.

It should work correctly without installing anything else. Although, it is possible that FFmpeg does not work correctly on your computer. If this was the case, please read the installing instructions, otherwise, you can skip this part. 
In order to know whether you need to install something or not, you can test it as it is say in testing. 

Also, this software is thought to be executed in windows, in any other OS, you might need to install the repository commented in Installing.

### Installing

1. Install MSYS2 in the following link: https://www.msys2.org/#installation
2. Open MSYS2 MINGW64
3. Execute the following code:
```
git clone https://github.com/MrMiracleMan111/FFmpeg FFmpeg-patched
cd FFmpeg-patched
make clean
./configure --disable-doc --disable-asm 
make -j$(nproc)
make install
```

4. You can test the code writing:
```
./ffmpeg -loglevel debug -i rtsp://192.168.1.1:7070/webcam -f matroska - 2> log.txt | ffplay -
```
If you want to see video in real time or
```
./ffmpeg -y -i rtsp://192.168.1.1:7070/webcam/ -vframes 1 do.jpg
```
If you want to generate a picture with a frame called do.jpg

5. Copy your ffmpeg.exe and paste it in the folder src/libs/camera_controller/ffmpeg of this project.

## Running the tests

In order to test the program, just execute:
```
python -m "dir/to/the/project/src/main.py"
```

### How to use the program

The way the drone moves is explained in this repository [Original code](https://github.com/Matchstic/mini-drone-lib/tree/main) which is my project mostly based on. Furthermore, I added a Flight Assistant which helps us to controll the drone easier.
Though, it is a infinite loop, so you may use a thead in order to execute the program. 

The camera will be started as soon as possible, although you can start the camera at any time using ```controller.IniciaCam()``` or close it pressing ESC.
The camera object in the flight assistant has a function which allows you to capture a frame, the frame will be in folder output. You can set any name, but it is set Frame as default.

Finally, you have functions ```StopControlTeclas()``` and ```InitControlTeclas()``` which allows you to use keys from your keyboard in order to use your drone. The instructions are the following:

Keyboard controls:
    ↑ / ↓: Throttle
    ← / →: Roll
    W / S: Pitch
    A / D: Yaw

## Deployment

This can be used in order to controll the dron TR008W using its camera for detecting fire or any other dangers. This drone would be able to arrive there and help in many ways.
This project may also be helpful to see how drones like this works. In fact, it will help with any drone commented in the following repository: https://github.com/Matchstic/mini-drone-lib/tree/main

## References

This project is an extension to the project from Matchstic in the link [Original code](https://github.com/Matchstic/mini-drone-lib/tree/main). From this project, I used entirely the way to controll the drone and from its example I made the flight controller file.
In addition, the camera had some troubles in order to use FFmpeg, so I added a patch commented in the following link [#8211](https://trac.ffmpeg.org/ticket/8211?cnum_hist=11&cversion=0) and implemented by MrMiracleMan111 [FFmpeg](https://github.com/MrMiracleMan111/FFmpeg)
Here, you can see the patch implemented:

```
diff --git a/libavcodec/mjpegdec.c b/libavcodec/mjpegdec.c
index 20f310fd70..9a4c1b8b2b 100644
--- a/libavcodec/mjpegdec.c
+++ b/libavcodec/mjpegdec.c
@@ -1802,6 +1802,7 @@ static int mjpeg_decode_dri(MJpegDecodeContext *s)
     if (get_bits(&s->gb, 16) != 4)
         return AVERROR_INVALIDDATA;
     s->restart_interval = get_bits(&s->gb, 16);
+s->restart_interval = 40;
     s->restart_count    = 0;
     av_log(s->avctx, AV_LOG_DEBUG, "restart interval: %d\n",
            s->restart_interval);
```
```
diff --git a/libavformat/rtpdec_jpeg.c b/libavformat/rtpdec_jpeg.c
index b32d074136..2ebe341236 100644
--- a/libavformat/rtpdec_jpeg.c
+++ b/libavformat/rtpdec_jpeg.c
@@ -242,6 +242,7 @@ static int jpeg_parse_packet(AVFormatContext *ctx, PayloadContext *jpeg,
             return AVERROR_INVALIDDATA;
         }
         dri = AV_RB16(buf);
+        av_log(ctx, AV_LOG_ERROR, "dri: %x F/L/Restart Count: %x \n", dri, AV_RB16(buf + 2));
         buf += 4;
         len -= 4;
         type &= ~0x40;
```
These were proposed by Cehoyos in the link said before, comments 18 and 19.

## Authors

* **Jesús Racero** - *Initial work* - [Marchstic](https://github.com/Matchstic)

