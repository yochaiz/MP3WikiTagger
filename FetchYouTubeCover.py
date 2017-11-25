import argparse
import os
import sys
from eyed3 import id3
from googleapiclient.discovery import build
import urllib
from eyed3.id3.frames import ImageFrame
from eyed3.id3 import ID3_DEFAULT_VERSION
from eyed3.core import Date

parser = argparse.ArgumentParser()
parser.add_argument("folderName", type=str, help="Folder name where MP3 files are")
parser.add_argument("--missing", action="store_true", help="Fetch only for MP3 without cover")
args = parser.parse_args()

fileTypeSuffix = '.mp3'
ENCODING = 'UTF-8'

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
DEVELOPER_KEY = 'AIzaSyAizLaFmMUZe-EJJQ7JQ6LoyRFnVQbHS-M'

youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=DEVELOPER_KEY)

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

        tag = id3.Tag()
        tag.parse('{}/{}'.format(args.folderName, fname))

        fetchFlag = (args.missing is True) and (len(tag.images) == 0)
        fetchFlag = fetchFlag or (args.missing is False)

        if fetchFlag is True:
            search_response = youtube.search().list(
                type='video',
                q='{} - {}'.format(tag.artist.encode(ENCODING), tag.title.encode(ENCODING)),
                part='snippet',
                maxResults=1
            ).execute()

            imgURL = None
            for item in search_response['items']:
                if (tag.recording_date is None) or (tag.recording_date == ''):
                    year = item['snippet']['publishedAt'][0:4]
                    tag.recording_date = Date(int(year))

                imgURL = item['snippet']['thumbnails']['high']['url']

            if imgURL is not None:
                # update image
                # remove existing images
                for img in tag.images:
                    tag.images.remove(img.description)

                imgData = urllib.urlopen(imgURL).read()
                tag.images.set(ImageFrame.FRONT_COVER, imgData, "image/jpeg")

                tag.save('{}/{}'.format(args.folderName, fname), version=ID3_DEFAULT_VERSION, encoding=ENCODING.lower())

        if i % nFilesPerPercent == 0:
            percent += percentIncrement
        if i % nFilesPerProgressChar == 0:
            progress += ('=' * progressIncrement)

print('Done!')
