# -*- coding: utf-8 -*-
import argparse
import os
from HebrewSongInfo import HebrewSongInfo
from EnglishSongInfo import EnglishSongInfo
from eyed3 import id3
from eyed3.id3.frames import ImageFrame
from eyed3.id3 import ID3_DEFAULT_VERSION
from eyed3.core import Date
import urllib
import sys


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


parser = argparse.ArgumentParser()
parser.add_argument("folderName", type=str, help="Folder name where MP3 files are")
args = parser.parse_args()

fileTypeSuffix = '.mp3'

# count relevant files in folder
nFiles = 0
for fname in os.listdir(args.folderName):
    if fname.endswith(fileTypeSuffix):
        nFiles += 1

progress = ''
progressBarLength = 20
nFilesPerProgressChar = max(1, nFiles / progressBarLength)
progressIncrement = max(1, progressBarLength / nFiles)
percent = 0
nFilesPerPercent = max(1, nFiles / 100)
percentIncrement = max(1, 100 / nFiles)

for i, fname in enumerate(os.listdir(args.folderName)):
    if fname.endswith(fileTypeSuffix):
        sys.stdout.write('\r')
        sys.stdout.write('Progress: [%-20s] %d%%    File:[%s]' % (progress, percent, fname))
        sys.stdout.flush()

        songName = fname[:-len(fileTypeSuffix)]
        if songName[-1] == ')':
            songName = songName[:songName.rfind('(')]

        if is_ascii(songName):
            song = EnglishSongInfo(songName)
        else:
            song = HebrewSongInfo(songName)

        tag = id3.Tag()
        tag.parse('{}/{}'.format(args.folderName, fname))

        tag.artist = unicode(song.getArtist())
        tag.album_artist = unicode(song.getArtist())
        tag.title = unicode(song.getTitle())
        tag.album = unicode(song.getAlbum())
        tag.genre = unicode(song.getGenre())

        # remove comments
        for c in tag.comments:
            tag.comments.remove(c.description)

        if 'IPLS' in tag.frame_set:
            while len(tag.frame_set['IPLS']) > 0:
                del tag.frame_set['IPLS'][0]

        if song.getYear().isdigit():
            tag.recording_date = Date(int(song.getYear()))

        # update image
        # remove existing images
        for img in tag.images:
            tag.images.remove(img.description)

        # set new image
        imgURL = song.getImageURL()
        if imgURL is not None:
            imgData = urllib.urlopen(imgURL).read()
            tag.images.set(ImageFrame.FRONT_COVER, imgData, "image/jpeg")

        tag.save('{}/{}'.format(args.folderName, fname), version=ID3_DEFAULT_VERSION, encoding='utf-8')

        if i % nFilesPerPercent == 0:
            percent += percentIncrement
        if i % nFilesPerProgressChar == 0:
            progress += ('=' * progressIncrement)

print('Done!')
