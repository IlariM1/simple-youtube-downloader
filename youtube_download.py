from pytube import (
    YouTube,
    exceptions,
    Stream,
)
import tkinter as tk
from tkinter import simpledialog

from pytube.innertube import InnerTube


class YoutubeWorking(YouTube):
    """
    Incredible bug fix by overwriting the buggy method with almost a copy of itself
    ´client='ANDROID_EMBED'´´does not work with age restricted videos, but you cannot submit
    it via argument so fixing it here, so I don't have to modify library code itself.
    https://github.com/pytube/pytube/issues/1712. A bit old at the time of writing....
    """

    def bypass_age_gate(self):
        """Attempt to update the vid_info by bypassing the age gate."""
        innertube = InnerTube(
            client='ANDROID',
            use_oauth=self.use_oauth,
            allow_cache=self.allow_oauth_cache
        )
        innertube_response = innertube.player(self.video_id)

        playability_status = innertube_response['playabilityStatus'].get('status', None)

        # If we still can't access the video, raise an exception
        # (tier 3 age restriction)
        if playability_status == 'UNPLAYABLE':
            raise exceptions.AgeRestrictedError(self.video_id)

        self._vid_info = innertube_response


def _parse_resolution(stream: Stream) -> int:
    try:
        return int(stream.resolution.replace('p', ''))
    except AttributeError:
        return 0  # Just some number to use for sorting that does not mix actual resolutions


def download_file(url: str) -> None:
    youtube_video = YoutubeWorking(
        url,
        use_oauth=True,
        allow_oauth_cache=True,
    )
    video_streams = youtube_video.streams.filter(progressive=True).all()

    best_quality_stream = sorted(
        video_streams,
        key=lambda x: _parse_resolution(x),
        reverse=True,
    )[0]

    best_quality_stream.download()


if __name__ == '__main__':
    ROOT = tk.Tk()
    ROOT.withdraw()
    video_url = simpledialog.askstring(
        title='Youtube video downloader',
        prompt='Youtube video url:',
    )

    download_file(video_url)
