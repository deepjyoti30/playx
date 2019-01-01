"""Simple API to access Billboard charts."""


import requests
from bs4 import BeautifulSoup
import re
import os

from playx.playlist.playlistmodder import (
    PlaylistBase
)

"""
__author__ = Deepjyoti Barman
__github__ = github.com/deepjyoti30

"""


class song():
    """Class to store song details."""

    def __init__(self):
        self.title = ""
        self.artist = ""
        self.rank = 0


class BillboardIE():
    """Class to store billboard charts."""

    def __init__(self, URL):
        """Initiate the basic stuff."""
        self.baseurl = "https://www.billboard.com/charts/"
        self.URL = self.baseurl + URL
        self.soup = self.get_soup()
        self.chart = []
        self.chart_name = ""
        self.get_name_of_chart()
        self.get_number_one()
        self.get_remaining_list()
        self.replace_symbols()

    def get_soup(self):
        """Return the soup for the response."""
        response = requests.get(self.URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def replace_symbols(self):
        """Replace symbols like &amp with &"""
        for i in self.chart:
            i.title = re.sub(r'&amp', '&', i.title)
            i.artist = re.sub(r'&amp', '&', i.artist)

    def get_name_of_chart(self):
        """Get the name of the chart from the webpage."""
        name = self.soup.findAll('h1',
                                attrs={'class': 'chart-detail-header__chart-name'})
        name = re.sub(r'\n', '', str(name))
        try:
            name = re.sub(
                        r'img alt=|"', '',
                        re.findall(r'img alt=".*?"', str(name))[0]
                        )
        except IndexError:
            name = re.sub(
                        r'[></]', '',
                        re.findall(r'>.*?</', str(name))[0]
                        )
        self.chart_name = name

    def get_number_one(self):
        """The number one of the chart needs to be extracted seperately."""
        number_one = song()
        soup = self.soup

        # Some extraction related to number one
        chart_number_one_title = soup.findAll(
                                    'div',
                                    attrs={'class': 'chart-number-one__title'}
                                    )[0]
        number_one.title = re.sub(
                            r'[<>]', '',
                            re.findall(r'>.*?<', str(chart_number_one_title))[0]
                            )

        chart_number_one_artist = str(soup.findAll(
                                    'div',
                                    attrs={'class': 'chart-number-one__artist'}
                                    )[0])
        chart_number_one_artist = chart_number_one_artist.replace("\n", '')
        chart_number_one_artist = re.findall(
                                    r'a href=.*?>.*?</a',
                                    str(chart_number_one_artist)
                                    )[0]
        number_one.artist = re.sub(
                                r'[<>/]', '',
                                re.findall(r'>.*?</', chart_number_one_artist)[0]
                                )

        number_one.rank = 1

        self.chart.append(number_one)

    def get_remaining_list(self):
        soup = self.soup.findAll('div', attrs={'class': 'chart-list-item'})
        for i in soup:
            songObj = song()
            songObj.artist = re.sub(
                                r'data-artist=|["]', '',
                                re.findall(r'data-artist=".*?"', str(i))[0]
                                )
            songObj.title = re.sub(
                                r'data-title=|["]', '',
                                re.findall(r'data-title=".*?"', str(i))[0]
                                )
            songObj.rank = re.sub(
                                r'data-rank=|["]', '',
                                re.findall(r'data-rank=".*?"', str(i))[0]
                                )
            self.chart.append(songObj)


class BillboardPlaylist(PlaylistBase):
    """Class to store Billboards Charts data."""

    def __init__(self, playlist_name, pl_start=None, pl_end=None):
        """Init the chart name."""
        super().__init__(pl_start, pl_end)
        self.playlist_name = playlist_name
        self.list_content_tuple = []

    def _add_artist_name(self):
        """Add the artist name to the song seperating by a 'by'

        eg: If the song name is thank u, next
        It should be changed to thank u, next by Ariana Grande."""

        for i in self.list_content_tuple:
            i.title = i.title + ' by ' + i.artist

    def extract_list_contents(self):
        """Extract the playlist data."""
        Chart = BillboardIE(self.playlist_name)
        self.list_content_tuple = Chart.chart
        PlaylistBase.update_end(self, len(self.list_content_tuple))
        PlaylistBase.list_content_tuple = self.list_content_tuple
        PlaylistBase.strip_to_start_end(self)
        self._add_artist_name()
        self.playlist_name = Chart.chart_name


def get_chart_names_online(url="https://www.billboard.com/charts"):
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=re.compile(r'.*/charts/.+'))
    chart_names = set()
    for link in links:
        href = link['href']
        name = href.split("/")[-1]
        if name:
            chart_names.add(name.lower())
    return chart_names


def get_chart_names(filename):
    """Get the chart names from the local chart file."""
    path = os.path.expanduser(filename)
    return [name.strip() for name in open(path).readlines()]


def dump_to_file(names):
    """Dump the billboard chart names to a local file."""
    path = '~/.playx/logs/billboard'
    path = os.path.expanduser(path)
    with open(path, 'w') as f:
        f.write('\n'.join(names).strip())


def get_data(URL, pl_start, pl_end):
    """Generic function. Should be called only when
    it is checked if the URL is a billboard chart.

    Returns a tuple containing the songs and name of
    the chart.
    """

    billboard_playlist = BillboardPlaylist(
                                            URL,
                                            pl_start,
                                            pl_end
                                        )
    billboard_playlist.extract_list_contents()

    return billboard_playlist.list_content_tuple, billboard_playlist.playlist_name


if __name__ == "__main__":
    # Chart = Billboard("youtube")
    # for i in Chart.chart:
    #     # print(i.title)
    #     print("{}: {} by {}".format(i.rank, i.title, i.artist))
    chart_names = get_chart_names_online()
    dump_to_file(chart_names)
    print(get_chart_names('~/.playx/logs/billboard'))
