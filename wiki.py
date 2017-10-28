from SongInfo import SongInfo
from eyed3 import id3
from eyed3.id3.frames import ImageFrame
import urllib

song = SongInfo("Shawn Mendes - Treat You Better")
print(song.getArtist())
print(song.getTitle())
print(song.getAlbum())
print(song.getYear())
print(song.getGenre())

tag = id3.Tag()
fname = "/media/yiz/385AA21F5AA1D9C0/Users/Zur/Desktop/EEE/Cranberries - Zombie.mp3"
tag.parse(fname)
tag.artist = unicode('e32')
for img in tag.images:
    tag.images.remove(img.description)

imgData = urllib.urlopen(song.getImageURL()).read()
tag.images.set(ImageFrame.FRONT_COVER,imgData,"image/jpeg")

tag.save(fname)

