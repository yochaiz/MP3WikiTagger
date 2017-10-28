from SongInfo import SongInfo
import eyed3

song = SongInfo("John Legend - All Of Me")
print(song.getArtist())
print(song.getTitle())
print(song.getAlbum())
print(song.getYear())
print(song.getGenre())

file = eyed3.load("C:\Users\Zur\Desktop\EEE\Cranberries - Zombie.mp3")
file.tag.artist = song.getArtist()
file.tag.save()

