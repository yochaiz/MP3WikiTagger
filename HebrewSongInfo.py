# coding=UTF-8
import requests
from xml.etree import ElementTree
from lxml import etree


class HebrewSongInfo:
    def __init__(self, songFname):
        idx = songFname.find('-')
        songName = songFname[idx + 1:].lstrip()
        songNameForURL = songName.replace(' ', '+')

        artistName = None
        if idx >= 0:
            artistName = songFname[:idx].rstrip()
            artistName = artistName.decode('UTF-8')

        self.xmlElement, self.imageElement, findAlbumFunc = self.__findXmlElement(songNameForURL, artistName)

        self.artist = self.__findArtist()
        self.album = findAlbumFunc()
        self.title = unicode(songName.decode('UTF-8'))
        self.title = self.__findTitle()
        self.year = self.__findYear()
        self.genre = self.__findGenre()
        self.imageURL = self.__findImageURL()

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
                print(a.text)

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
        url = 'http://www.disccenter.co.il/list?genre=&format=&langs=&search={}&type=0&kind=-1'.format(songName)
        xmlElement, imageElement = self.__searchElement(url, artistName)
        albumFunc = self.__findAlbumType1

        if xmlElement is None:
            url = 'http://www.disccenter.co.il/list?genre=&format=&langs=&search={}&type=0&kind=1'.format(songName)
            xmlElement, imageElement = self.__searchElement(url, artistName)
            albumFunc = self.__findAlbumType2

        return xmlElement, imageElement, albumFunc

    def __findArtist(self):
        if len(self.artistsList) > 0:
            artist = self.artistsList[0]
            del self.artistsList[0]
            return artist

    def __findAlbumType1(self):
        node = self.xmlElement.find(".//p/strong/a")
        if node is not None:
            return node.text

        return ''

    def __findAlbumType2(self):
        node = self.xmlElement.find(".//p/strong/a")
        if (node is not None) and (node.attrib['href'] is not None):
            xmlRoot = self.__loadXML(unicode('http://www.disccenter.co.il') + node.attrib['href'])
            node = xmlRoot.find(".//div[@class='product-info-top']/p/h1/strong")
            if node is not None:
                return node.text

        return ''

    def __findTitle(self):
        title = self.title
        if len(self.artistsList) > 0:
            title += ' (עם '.decode('UTF-8')
            while len(self.artistsList) > 1:
                title += self.artistsList[0] + ' & '.decode('UTF-8')
                del self.artistsList[0]

            title += self.artistsList[0]
            del self.artistsList[0]

            title += ')'.decode('UTF-8')

        return title

    def __findYear(self):
        span = self.xmlElement.findall(".//p/span")
        for sp in span:
            if (sp.text is not None) and ('תאריך יציאה'.decode('UTF-8') in sp.text):
                return sp.text[-4:]

        return ''

    def __findGenre(self):
        paragraphs = self.xmlElement.findall(".//p")
        for p in paragraphs:
            if (p.text is not None) and ('סגנון'.decode('UTF-8') in p.text):
                aElements = p.findall(".//a")
                for a in aElements:
                    if (a.text is not None) and (a.text != 'מוסיקה ישראלית'.decode('UTF-8')):
                        return a.text
        return ''

    def __findImageURL(self):
        return 'http://www.disccenter.co.il{}'.format(self.imageElement.attrib['src'])

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
