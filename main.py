#! /usr/bin/python
# -*- coding: utf-8 -*-

from vlc import *

try:
    from msvcrt import getch
except ImportError:
    import termios
    import tty

    def getch():  # getchar(), getc(stdin)  #PYCHOK flake
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch

def end_callback(event):
    print('End of media stream (event %s)' % event.type)
    sys.exit(0)

echo_position = False
def pos_callback(event, player):
    if echo_position:
        sys.stdout.write('\r%s to %.2f%% (%.2f%%)' % (event.type,
                                                      event.u.new_position * 100,
                                                      player.get_position() * 100))
        sys.stdout.flush()

def print_version():
    """Print version of this vlc.py and of the libvlc"""
    try:
        print('Build date: %s (%#x)' % (build_date, hex_version()))
        print('LibVLC version: %s (%#x)' % (bytes_to_str(libvlc_get_version()), libvlc_hex_version()))
        print('LibVLC compiler: %s' % bytes_to_str(libvlc_get_compiler()))
        if plugin_path:
            print('Plugin path: %s' % plugin_path)
    except:
        print('Error: %s' % sys.exc_info()[1])

if sys.argv[1:] and '-h' not in sys.argv[1:] and '--help' not in sys.argv[1:]:

    movie = os.path.expanduser(sys.argv.pop())
    if not os.access(movie, os.R_OK):
        print('Error: %s file not readable' % movie)
        sys.exit(1)

    # Need --sub-source=marq in order to use marquee below
    instance = Instance(["--sub-source=marq"] + sys.argv[1:])
    try:
        media = instance.media_new(movie)
    except (AttributeError, NameError) as e:
        print('%s: %s (%s %s vs LibVLC %s)' % (e.__class__.__name__, e,
                                               sys.argv[0], __version__,
                                               libvlc_get_version()))
        sys.exit(1)
    player = instance.media_player_new()
    player.set_media(media)
    player.play()

    # Some event manager examples.  Note, the callback can be any Python
    # callable and does not need to be decorated.  Optionally, specify
    # any number of positional and/or keyword arguments to be passed
    # to the callback (in addition to the first one, an Event instance).
    event_manager = player.event_manager()
    event_manager.event_attach(EventType.MediaPlayerEndReached,      end_callback)
    event_manager.event_attach(EventType.MediaPlayerPositionChanged, pos_callback, player)

    def mspf():
        """Milliseconds per frame"""
        return int(1000 // (player.get_fps() or 25))

    def print_info():
        """Print information about the media"""
        try:
            print_version()
            media = player.get_media()
            print('State: %s' % player.get_state())
            print('Media: %s' % bytes_to_str(media.get_mrl()))
            print('Track: %s/%s' % (player.video_get_track(), player.video_get_track_count()))
            print('Current time: %s/%s' % (player.get_time(), media.get_duration()))
            print('Position: %s' % player.get_position())
            print('FPS: %s (%d ms)' % (player.get_fps(), mspf()))
            print('Rate: %s' % player.get_rate())
            print('Video size: %s' % str(player.video_get_size(0)))  # num=0
            print('Scale: %s' % player.video_get_scale())
            print('Aspect ratio: %s' % player.video_get_aspect_ratio())
           #print('Window:' % player.get_hwnd()
        except Exception:
            print('Error: %s' % sys.exc_info()[1])

    def sec_forward():
        """Go forward one sec"""
        player.set_time(player.get_time() + 1000)

    def sec_backward():
        """Go backward one sec"""
        player.set_time(player.get_time() - 1000)

    def frame_forward():
        """Go forward one frame"""
        player.set_time(player.get_time() + mspf())

    def frame_backward():
        """Go backward one frame"""
        player.set_time(player.get_time() - mspf())

    def print_help():
        """Print help"""
        print('Single-character commands:')
        for k, m in sorted(keybindings.items()):
            m = (m.__doc__ or m.__name__).splitlines()[0]
            print('  %s: %s.' % (k, m.rstrip('.')))
        print('0-9: go to that fraction of the movie')

    def quit_app():
        """Stop and exit"""
        sys.exit(0)

    def toggle_echo_position():
        """Toggle echoing of media position"""
        global echo_position
        echo_position = not echo_position

    calcActive = True
    def calcDuration():
        """Calculates the current time in video and duration"""

        # This solution makes it lag a tad
        # Sometimes it skips seconds
        # TODO
        while calcActive:
            dur_hours = ((media.get_duration() / 1000) / 60) / 60
            dur_minutes = (((media.get_duration() / 1000) / 60) - (dur_hours * 60))
            dur_seconds = (media.get_duration() / 1000) - (((dur_hours * 60) * 60) + (dur_minutes * 60))

            cur_hours = ((player.get_time() / 1000) / 60) / 60
            cur_minutes = ((player.get_time() / 1000) / 60) - (cur_hours * 60)
            cur_seconds = (player.get_time() / 1000) - (((cur_hours * 60) * 60) + (cur_minutes * 60))

            # Formatting to make it look consistent
            if dur_hours < 10:
                dur_hours = "0" + str(dur_hours)
            if dur_minutes < 10:
                dur_minutes = "0" + str(dur_minutes)

            if dur_seconds < 10:
                dur_seconds = "0" + str(dur_seconds)

            if cur_hours < 10:
                cur_hours = "0" + str(cur_hours)
            if cur_minutes < 10:
                cur_minutes = "0" + str(cur_minutes)
            if cur_seconds < 10:
                cur_seconds = "0" + str(cur_seconds)

            mTime = "%s:%s:%s / %s:%s:%s" % (cur_hours, cur_minutes, cur_seconds, dur_hours, dur_minutes, dur_seconds)

            player.video_set_marquee_string(VideoMarqueeOption.Text, mTime)


    def set_playbacktime():
        """Asks for what time to set playback to"""
        set_hours = input('Enter hours: ')
        set_minutes = input('Enter minutes: ')

        set_hours = ((set_hours * 60) * 60) * 1000
        set_minutes = (set_minutes * 60) * 1000

        # Sets the time in milliseconds
        player.set_time(set_hours + set_minutes)

    def decrease_volume():
        """Decreases the volume by 10%"""
        player.audio_set_volume(player.audio_get_volume() - 10)
        print("Volume: %s" % (str(player.audio_get_volume()) + "%"))

    def increase_volume():
        """Increases the volume by 10%"""
        player.audio_set_volume(player.audio_get_volume() + 10)
        print("Volume: %s" % (str(player.audio_get_volume()) + "%"))


    keybindings = {
        ' ': player.pause,
        'z': decrease_volume,
        'x': increase_volume,
        '+': sec_forward,
        '-': sec_backward,
        't': set_playbacktime,
        '.': frame_forward,
        ',': frame_backward,
        'f': player.toggle_fullscreen,
        'i': print_info,
        'p': toggle_echo_position,
        'q': quit_app,
        'h': print_help
        }

    # Some marquee examples.  Marquee requires '--sub-source marq' in the
    # Instance() call above, see <http://www.videolan.org/doc/play-howto/en/ch04.html>
    player.video_set_marquee_int(VideoMarqueeOption.Size, 14)  # pixels
    player.video_set_marquee_int(VideoMarqueeOption.marquee_X, 15)
    player.video_set_marquee_int(VideoMarqueeOption.marquee_Y, 15)

    # Wow very shit solution with threading
    # but hey :>
    mThread = Thread(target=calcDuration)
    mThread.start()

    print('Press q to quit, ? to get help.%s' % os.linesep)
    while True:
        k = getch()
        print('> %s' % k)
        if k in keybindings:
            if k == 'q':
                calcActive = False

            keybindings[k]()
        elif k.isdigit():
             # jump to fraction of the movie.
            player.set_position(float('0.'+k))

else:
    print('Usage: %s [options] <movie_filename>' % sys.argv[0])
    print('Once launched, type ? for help.')
    print('')
    print_version()
