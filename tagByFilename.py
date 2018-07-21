# -*- coding: utf-8 -*-
import argparse
from os import listdir
from sys import stdout
from eyed3 import id3
from eyed3.id3 import ID3_DEFAULT_VERSION

parser = argparse.ArgumentParser()
parser.add_argument("folderName", type=str, help="Folder name where MP3 files are")
args = parser.parse_args()

fileTypeSuffix = '.mp3'

# count relevant files in folder
nFiles = 0
for fname in listdir(args.folderName):
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

for i, fname in enumerate(listdir(args.folderName)):
    if fname.endswith(fileTypeSuffix) is False:
        continue

    stdout.write('\r')
    stdout.write('Progress: [%-20s] %d%%    File:[%s]' % (progress, percent, fname))
    stdout.flush()

    songFname = fname[:-len(fileTypeSuffix)].decode(ENCODING)
    songFname = songFname.rstrip().lstrip()
    idx = songFname.find('-')
    if idx <= 0:
        continue

    # load current file tag
    tag = id3.Tag()
    tag.parse('{}/{}'.format(args.folderName, fname))

    # update tag
    tag.artist = songFname[:idx].rstrip()
    tag.album_artist = tag.artist
    tag.album = unicode('{} - Single'.format(tag.artist))
    tag.title = songFname[idx + 1:].lstrip()

    # remove comments
    for c in tag.comments:
        tag.comments.remove(c.description)

    if 'IPLS' in tag.frame_set:
        while len(tag.frame_set['IPLS']) > 0:
            del tag.frame_set['IPLS'][0]

    tag.save('{}/{}'.format(args.folderName, fname), version=ID3_DEFAULT_VERSION, encoding='utf-8')

    if i % nFilesPerPercent == 0:
        percent += percentIncrement
    if i % nFilesPerProgressChar == 0:
        progress += ('=' * progressIncrement)

print('Done!')
