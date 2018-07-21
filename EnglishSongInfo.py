from SongInfo import SongInfo
import wikipedia
import requests
from xml.etree import ElementTree


class EnglishSongInfo(SongInfo):
    def __init__(self, songName):
        wikipedia.set_lang("en")
        # self.wikiObj = wikipedia.page(songName)
        results = wikipedia.search(songName, results=3)

        for res in results:
            self.wikiObj = wikipedia.page(res)
            resp = requests.get(self.wikiObj.url)
            self.xmlRoot = ElementTree.fromstring(resp.content)
            self.xmlRoot = self.xmlRoot.find(".//table[@class='infobox vevent']")

            if self.xmlRoot is not None:
                while self.xmlRoot.tag != 'tbody':
                    self.xmlRoot = self.xmlRoot._children[0]

                del resp
                break

        if self.xmlRoot is not None:
            SongInfo.__init__(self)

    def findImageURL(self):
        img = self.xmlRoot.find(".//a[@class='image']")
        if (img is not None) and (len(img._children) > 0):
            img = img.find(".//img")
            if img is not None:
                return 'http://{}'.format(img.attrib['src'][2:])

        return self.findYoutubeImageURL()

    def findGenre(self):
        for tr in self.xmlRoot:
            th = tr.find(".//th/a")
            if (th is not None) and (th.text == "Genre"):
                genre = tr.find(".//td")
                while len(genre._children) > 0:
                    genre = genre._children[0]

                return genre.text

        return ''

    def findYear(self):
        for tr in self.xmlRoot:
            th = tr.find(".//th")
            if th is not None:
                if th.text == "Recorded":
                    date = tr.find(".//td")
                    if date is not None:
                        return date.text
                elif th.text == "Released":
                    date = tr.find(".//td")
                    if date is not None:
                        return date.text[-4:]

        return ''

    def findTitle(self):
        if len(self.xmlRoot._children) > 0:
            titleTr = self.xmlRoot._children[0]
            if len(titleTr._children) > 0:
                titleTh = titleTr._children[0]
                title = titleTh.text
                title = title.replace('"', '')
                return title

        return ''

    def findArtist(self):
        # if len(self.xmlRoot._children) >= 3:
        #     artistTr = self.xmlRoot._children[2]

        artistTr = self.xmlRoot.find("./tr[@class='description']")
        if (artistTr is not None) and (len(artistTr._children) > 0):
            artistTh = artistTr._children[0]
            artistStr = ''
            for i in range(1, len(artistTh._children)):
                artist = artistTh._children[i]
                artistStr += artist.text
                if artist.tail is not None:
                    artistStr += artist.tail

            return artistStr

        return ''

    def findAlbum(self):
        trDesc = self.xmlRoot.findall(".//tr[@class='description']")
        for tr in trDesc:
            for trChild in tr._children:
                if trChild.text is not None:
                    if trChild.text.startswith('from the '):
                        for thChild in trChild._children:
                            if thChild.tag == 'i':
                                if len(thChild._children) > 0:
                                    for iChild in thChild._children:
                                        if iChild.tag == 'a':
                                            # albumElement = thChild._children[0]
                                            album = iChild.text
                                            return album
                                elif thChild.text is not None:
                                    return thChild.text

        return '{} - Single'.format(self.artist.encode('ascii', 'ignore'))
