# working on extracting audio from shit video so i can later on combine audio with clean video to get clean package
# figure out how to get filename of downloaded file, maybe save ls pre-download then post download find the diff and work with that???

import pytube
from subprocess import call, run, PIPE
import os
import copy

def saveAndGetFilename(stream, start, end):
	lsPreSave = os.listdir()
	saveVideo(stream)
	lsPostSave = os.listdir()
	filename = ''
	for file in lsPostSave:
		if file not in lsPreSave:
			filename = file

	if start != None or end != None:
		assert(start != None)
		assert(end != None)
		filename = crop(filename, start, end)

	return filename
def getStreams(url, mime_type = '', vcodec = ''):
	streams = pytube.YouTube(url).streams
	if mime_type != '':
		old_streams = copy.copy(streams)
		streams = []
		for stream in old_streams:
			if mime_type in stream.mime_type:
				streams.append(stream)

	if vcodec != '':
		old_streams = copy.copy(streams)
		streams = []
		for stream in old_streams:
			if vcodec in stream.video_codec:
				streams.append(stream)

	return streams

def getHighestResStream(url):
	return pytube.YouTube(url).streams.order_by('resolution').last()

def saveVideo(stream):
	return stream.download()

def crop(filename, start, end):
	start = str(start)
	end = str(end)
	betterCommand = f'ffmpeg -y -i "{filename}" -vf trim={start}:{end} "{filename}"'
	command = f'ffmpeg -y -ss {start} -to {end} -i "{filename}" "Cropped_{filename}"'
	print(command)
	run(command, capture_output = False)

	return f'Cropped_{filename}'

def convert(filename, newExtension, newName = ''):
	x = filename.split('.')[0] if newName == '' else newName
	call(f'ffmpeg -i "{filename}" "{x}.{newExtension}"')
	return f"{x}.{newExtension}"

# def convertAllInFolderToMP4(streams, folderDir = os.getcwd()):
# 	extensions = set()
# 	for i in streams:
# 		extensions.add("." + i.mime_type.split('/')[-1])

# 	for file in os.listdir(folderDir):
# 		for extension in extensions:
# 			if file.endswith(extension):
# 				x = file.replace(extension, '')
# 				call(f'ffmpeg -i "{file}" "{x}.mp4"') 
# 				os.remove(file)

def displayStreams(streams):
	for i, stream in enumerate(streams):
		print(f'{i} >> {stream.mime_type} --- {stream.resolution} --- {stream.video_codec}')

def mergeVideoAudio(videoStream, audioStream, filename, start, end, videoConvert = 'mp4', audioConvert = 'aac'):
	savedDirectory = os.listdir()

	videoFilename = saveAndGetFilename(videoStream, start, end)
	audioFilename = saveAndGetFilename(audioStream, start, end)

	if videoConvert != '':
		videoFilename = convert(videoFilename, videoConvert, newName = "Converted_Video")

	if audioConvert != '':
		audioFilename = convert(audioFilename, audioConvert, newName = "Converted_Audio")

	command = f'ffmpeg -y -i "{videoFilename}" -i "{audioFilename}" "{filename}.mp4"'
	output = run(command, capture_output = False)

	savedDirectory.append(f'{filename}.mp4')

	for file in os.listdir():
		if file not in savedDirectory:
			os.remove(file)
			print(f'removed "{file}"')


def downloadVideo(url, filename, start = None, end = None):
	audioStream = getStreams(url, mime_type = 'audio/mp4')[0]
	videoStream = getHighestResStream(url)
	mergeVideoAudio(videoStream, audioStream, filename, start, end)

if __name__ == "__main__":
	url = input('Enter url: ')
	if input('y if u have a start and end, n if u dont: ') == 'y':
		start = input('start: ')
		end = input('end: ')
	else:
		start = None
		end = None
	title = input('enter title: ')
	downloadVideo(url, 
		title, start = start, end = end)