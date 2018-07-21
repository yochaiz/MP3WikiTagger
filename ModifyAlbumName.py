# -*- coding: utf-8 -*-
import argparse
import os
import sys
from eyed3 import id3
from eyed3.id3 import ID3_DEFAULT_VERSION
from random import randint

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

ENCODING = 'UTF-8'

albumsDict = {}

for i, fname in enumerate(os.listdir(args.folderName)):
    if fname.endswith(fileTypeSuffix) is False:
        continue

    sys.stdout.write('\r')
    sys.stdout.write('Reading tags: [%-20s] %d%%    File:[%s]' % (progress, percent, fname))
    sys.stdout.flush()

    tag = id3.Tag()
    tag.parse('{}/{}'.format(args.folderName, fname))

    if tag.album not in albumsDict:
        albumsDict[tag.album] = []

    albumsDict[tag.album].append((tag, fname))

    if i % nFilesPerPercent == 0:
        percent += percentIncrement
    if i % nFilesPerProgressChar == 0:
        progress += ('=' * progressIncrement)

nFiles = len(albumsDict)
progress = ''
nFilesPerProgressChar = max(1, nFiles / progressBarLength)
progressIncrement = max(1, progressBarLength / nFiles)
percent = 0
nFilesPerPercent = max(1, nFiles / 100)
percentIncrement = max(1, 100 / nFiles)

for album in albumsDict:
    if len(albumsDict[album]) > 1:
        i = 0
        for item in albumsDict[album]:
            tag = item[0]
            fname = item[1]

            if tag.album is None:
                continue

            tag.album = tag.album + unichr((i % 31) + 1)

            if 'IPLS' in tag.frame_set:
                while len(tag.frame_set['IPLS']) > 0:
                    del tag.frame_set['IPLS'][0]

            if 'RGAD' in tag.frame_set:
                while len(tag.frame_set['RGAD']) > 0:
                    del tag.frame_set['RGAD'][0]

            tag.save('{}/{}'.format(args.folderName, fname), version=ID3_DEFAULT_VERSION, encoding='utf-8')

    sys.stdout.write('\r')
    sys.stdout.write('Modifying tags: [%-20s] %d%%    Album:[%s]' % (progress, percent, album))
    sys.stdout.flush()

    if i % nFilesPerPercent == 0:
        percent += percentIncrement
    if i % nFilesPerProgressChar == 0:
        progress += ('=' * progressIncrement)

print('\nDone !')
