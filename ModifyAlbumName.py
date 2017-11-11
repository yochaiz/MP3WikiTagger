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

for i, fname in enumerate(os.listdir(args.folderName)):
    if fname.endswith(fileTypeSuffix) is False:
        continue

    sys.stdout.write('\r')
    sys.stdout.write('Progress: [%-20s] %d%%    File:[%s]' % (progress, percent, fname))
    sys.stdout.flush()

    tag = id3.Tag()
    tag.parse('{}/{}'.format(args.folderName, fname))

    tag.album = tag.album + unichr(randint(1, 31))

    tag.save('{}/{}'.format(args.folderName, fname), version=ID3_DEFAULT_VERSION, encoding='utf-8')

    if i % nFilesPerPercent == 0:
        percent += percentIncrement
    if i % nFilesPerProgressChar == 0:
        progress += ('=' * progressIncrement)

print('Done !')
