# CustomVLC - A custom VLC media player
A custom VLC player for my own needs

## API Documentation
[https://www.olivieraubert.net/vlc/python-ctypes/doc/](https://www.olivieraubert.net/vlc/python-ctypes/doc/)

## Dependencies

* Have VLC installed
* Python2

## Usage  
```sh
$ python main.py <MEDIA_FILE>
```

```
Single-character commands:
   : Toggle pause (no effect if there is no media).
  +: Go forward one sec.
  ,: Go backward one frame.
  -: Go backward one sec.
  .: Go forward one frame.
  d: Toggles the duration displayed.
  f: Toggle fullscreen status on non-embedded video outputs.
  h: Print help.
  i: Print information about the media.
  p: Toggle echoing of media position.
  q: Stop and exit.
  t: Asks for what time to set playback to.
  x: Increases the volume by 10%.
  z: Decreases the volume by 10%.
0-9: go to that fraction of the movie
```

## TODO

* Move main-function out of module-file 'vlc.py'
* Transition the code to python3
