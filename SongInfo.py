# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from googleapiclient.discovery import build


class SongInfo:
    __metaclass__ = ABCMeta

    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    DEVELOPER_KEY = 'AIzaSyAizLaFmMUZe-EJJQ7JQ6LoyRFnVQbHS-M'
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=DEVELOPER_KEY)

    ENCODING = 'UTF-8'

    def __init__(self):
        self.artist = self.findArtist()
        self.title = self.findTitle()
        self.album = self.findAlbum()
        self.year = self.findYear()
        self.genre = self.findGenre()
        self.imageURL = self.findImageURL()

    def findYoutubeImageURL(self):
        search_response = self.youtube.search().list(
            type='video',
            q='{} - {}'.format(self.artist.encode(self.ENCODING), self.title.encode(self.ENCODING)),
            part='snippet',
            maxResults=1
        ).execute()

        for item in search_response['items']:
            if (self.year is None) or (self.year == ''):
                self.year = item['snippet']['publishedAt'][0:4]

            return item['snippet']['thumbnails']['high']['url']

        return None

    @abstractmethod
    def findImageURL(self):
        return NotImplemented

    @abstractmethod
    def findAlbum(self):
        return NotImplemented

    @abstractmethod
    def findArtist(self):
        return NotImplemented

    @abstractmethod
    def findTitle(self):
        return NotImplemented

    @abstractmethod
    def findYear(self):
        return NotImplemented

    @abstractmethod
    def findGenre(self):
        return NotImplemented

    def getImageURL(self):
        return self.imageURL

    def getAlbum(self):
        return self.album

    def getTitle(self):
        return self.title

    def getArtist(self):
        return self.artist

    def getYear(self):
        return self.year

    def getGenre(self):
        return self.genre
