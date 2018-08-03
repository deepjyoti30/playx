
#!/usr/bin/env python3

"""
    Main function for playx.
"""

import argparse

from cache import (
    Cache, search_locally
)

from utility import (
    direct_to_play, run_mpv_dir
)

from youtube import (
    grab_link, get_youtube_title
)

from songfinder import search
from stringutils import is_song_url


def parse():
    """Parse the arguments."""
    parser = argparse.ArgumentParser(description="playx - Search and play\
                                     any song that comes to your mind.\n\
                                     If you have any issues, raise an issue in\
                                     the github\
                                     (https://github.com/NISH1001/playx) page")
    parser.add_argument('song',
                        help="Name or youtube link of song to download",
                        default=None, type=str, nargs="*")
    parser.add_argument('-p', '--play-cache',
                        action='store_true',
                        help="Play all songs from the cache.")
    parser.add_argument('-n', '--no-cache',
                        action='store_true',
                        help="Don't download the song for later use.")
    parser.add_argument('-d', '--dont-cache-search',
                        action='store_true',
                        help="Don't search the song in the cache.")
    parser.add_argument('-l', '--lyrics',
                        action='store_true',
                        help="Show lyircs of the song.")
    args = parser.parse_args()
    return parser, args


def online_search(value, no_cache):
    """Search the song online."""
    result = search(value)
    if result is None:
        return print("No results found")
    result.display()
    title = result.title
    value = grab_link(result.url, title, no_cache)
    return value


def get_value(value, no_cache):
    """Get the value of the song."""
    value = online_search(value, no_cache)
    if value is None:
        print("No audio attached to video")
        exit(-1)
    else:
        return value


def stream_from_name(value=None, show_lyrics=False, no_cache=False,
                     dont_cache_search=False):
    """Start streaming the song.

    First search in the local cache.
    If no song is found in the cache, search in the youtube.
    """
    # Need to check if searching locally is forbidden
    if not dont_cache_search:
        match = search_locally(value)
        if match:
            value = match[1]
            title = match[0]
        else:
            value = get_value(value, no_cache)
    else:
        value = get_value(value, no_cache)

    direct_to_play(value, show_lyrics, title, 'local')


def stream_from_url(url, show_lyrics=False, no_cache=False,
                    dont_cache_search=False):
    """Stream the song using the url.

    Before searching the stream, get the title of the song
    If local search is not forbidden, search it locally
    """
    result = search(url)
    if result is None:
        return print("No results found")
    result.display()
    title = result.title

    # Now search the song locally
    if not dont_cache_search:
        match = search_locally(title)
        if match:
            # Change the value to local path
            value = match[1]
        else:
            value = grab_link(result.url, title, no_cache)
    else:
        value = grab_link(result.url, title, no_cache)

    direct_to_play(value, show_lyrics, title, 'url')


def stream_cache_all(cache):
    run_mpv_dir(cache.dir)


def main():
    """Search the song in youtube and stream through mpd."""
    parser, args = parse()
    args.song = ' '.join(args.song)
    if not args.song and args.play_cache:
        cache = Cache("~/.playx/")
        stream_cache_all(cache)
    if is_song_url(args.song):
        # In case the song is a url
        stream_from_url(args.song, args.lyrics, args.no_cache,
                        args.dont_cache_search)
    elif not args.song:
        parser.print_help()
    else:
        stream_from_name(args.song, args.lyrics, args.no_cache,
                         args.dont_cache_search)


if __name__ == "__main__":
    main()
