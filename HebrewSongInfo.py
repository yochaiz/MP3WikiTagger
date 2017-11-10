# -*- coding: utf-8 -*-
from SongInfo import SongInfo
import requests
from xml.etree import ElementTree
from lxml import etree


class HebrewSongInfo(SongInfo):
    ENCODING = 'UTF-8'

    def __init__(self, songFname):
        idx = songFname.find('-')
        songName = songFname[idx + 1:].lstrip()
        songNameForURL = songName.replace(' ', '+')

        artistName = None
        if idx >= 0:
            artistName = songFname[:idx].rstrip()
            artistName = artistName.decode(self.ENCODING)

        self.artist = artistName

        self.xmlElement, self.imageElement, self.findAlbumFunc = self.__findXmlElement(songNameForURL, artistName)

        self.title = unicode(songName.decode(self.ENCODING))
        self.artistsList = []

        SongInfo.__init__(self)

    def __loadXML(self, url):
        resp = requests.get(url)
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(resp.content, parser)
        xmlRoot = ElementTree.fromstring(etree.tostring(root))

        return xmlRoot

    def __searchElement(self, url, artistName):
        xmlRoot = self.__loadXML(url)

        optimalElement = None
        imageElement = None

        elements = xmlRoot.findall(".//section[@class='entries cf']/section")
        for e in elements:
            artistsList = []
            info = e.find(".//div[@class='result-info right']")
            artists = info.findall(".//p/span/a")

            for a in artists:
                artistsList.append(a.text)
                # print(a.text)

            if artistName is not None:
                if artistName in artistsList:
                    self.artistsList = artistsList  # save song artists list
                    optimalElement = info  # save entry with earliest date
                    imageElement = e.find(".//a/img")
            else:  # we don't know who is the artist, therefore we take the 1st option
                self.artistsList = artistsList  # save song artists list
                return info, e.find(".//a/img")

        return optimalElement, imageElement

    def __findXmlElement(self, songName, artistName):
        url = 'http://www.disccenter.co.il/list?genre=&format=&langs=&search={}&type=0&kind=1'.format(songName)
        xmlElement, imageElement = self.__searchElement(url, artistName)
        albumFunc = self.__findAlbumType2

        if xmlElement is None:
            url = 'http://www.disccenter.co.il/list?genre=&format=&langs=&search={}&type=0&kind=-1'.format(songName)
            xmlElement, imageElement = self.__searchElement(url, artistName)
            albumFunc = self.__findAlbumType1

        return xmlElement, imageElement, albumFunc

    def findArtist(self):
        if len(self.artistsList) > 0:
            artist = self.artistsList[0]
            del self.artistsList[0]
            return artist

        return '' if self.artist is None else self.artist

    def __findAlbumType1(self):
        if self.xmlElement is not None:
            node = self.xmlElement.find(".//p/strong/a")
            if node is not None:
                return node.text

        return ''

    def __findAlbumType2(self):
        if self.xmlElement is not None:
            node = self.xmlElement.find(".//p/strong/a")
            if (node is not None) and (node.attrib['href'] is not None):
                xmlRoot = self.__loadXML(unicode('http://www.disccenter.co.il') + node.attrib['href'])
                node = xmlRoot.find(".//div[@class='product-info-top']/p/h1/strong")
                if node is not None:
                    return node.text

        return ''

    def findAlbum(self):
        value = self.findAlbumFunc()
        if value == '':
            value = self.artist
            value += ' - סינגל'.decode(self.ENCODING)

        return value

    def findTitle(self):
        title = self.title
        if len(self.artistsList) > 0:
            title += ' (עם '.decode(self.ENCODING)
            while len(self.artistsList) > 1:
                title += self.artistsList[0] + ' & '.decode(self.ENCODING)
                del self.artistsList[0]

            title += self.artistsList[0]
            del self.artistsList[0]

            title += ')'.decode(self.ENCODING)

        return title

    def findYear(self):
        if self.xmlElement is not None:
            span = self.xmlElement.findall(".//p/span")
            for sp in span:
                if (sp.text is not None) and ('תאריך יציאה'.decode(self.ENCODING) in sp.text):
                    return sp.text[-4:]

        return ''

    def findGenre(self):
        if self.xmlElement is not None:
            paragraphs = self.xmlElement.findall(".//p")
            for p in paragraphs:
                if (p.text is not None) and ('סגנון'.decode(self.ENCODING) in p.text):
                    aElements = p.findall(".//a")
                    for a in aElements:
                        if (a.text is not None) and (a.text != 'מוסיקה ישראלית'.decode(self.ENCODING)):
                            return a.text

        return ''

    def findImageURL(self):
        url = self.findYoutubeImageURL()
        if url is not None:
            return url
        elif self.imageElement is not None:
            return 'http://www.disccenter.co.il{}'.format(self.imageElement.attrib['src'])

        return ''
