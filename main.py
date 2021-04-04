# Drag and drop Mac app to save video frames
# at full size and a half size backup images
# ----------------------------------------------------
# REFERENCES: https://trac.ffmpeg.org/wiki/FFprobeTips
# ----------------------------------------------------

# TODO: Check if app was launched. If so, show UI
# TODO: Add menu option for app
# TODO: check for ffmpeg installation

import os, sys, subprocess
import tkMessageBox
from Tkinter import Tk

# requires ffmpeg to be installed
FFPROBE = '/usr/local/bin/ffprobe'
FFMPEG = '/usr/local/bin/ffmpeg'


def ProcessFiles():
    # process all files dropped onto the app
    for i in range(1, len(sys.argv)):
        filePath = sys.argv[i]
        SaveFirstFrame(filePath)
        SaveLastFrame(filePath)


# RETURNS METADATA FOR INPUT FILE
def Get_Video_Info(filePath):
    command = [FFPROBE,
               '-v', 'fatal', '-select_streams', 'v:0',
               '-show_entries', 'stream=width, height, r_frame_rate, duration, nb_frames',
               '-of', 'default=noprint_wrappers=1:nokey=1',
               filePath, '-sexagesimal']

    result = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = result.communicate()
    if (err): print(err)
    out = out.split('\n')
    return {'file': filePath,
            'width': int(out[0]),
            'height': int(out[1]),
            'fps': float(out[2].split('/')[0])/float(out[2].split('/')[1]),
            'duration': out[3],
            'frames': out[4]
            }



# SAVE FIRST FRAME
def SaveFirstFrame(filePath):
    # save first frame at full size
    rootPath = os.path.dirname(filePath)
    videoInfo = Get_Video_Info(filePath)

    command = [FFMPEG, '-i', filePath,
               '-y',  # overwrite file if it exists
               '-frames:v', '1',
               '-vf', 'select=eq(n\,0)',
               rootPath + '/startframe.jpg']

    subprocess.Popen(command)


# SAVE LAST FRAME AND BACKUP IMAGE & HALF SIZE
def SaveLastFrame(filePath):
    # save last frame at full size
    rootPath = os.path.dirname(filePath)
    videoInfo = Get_Video_Info(filePath)

    totalFrames = videoInfo['frames']
    lastFrame = int(totalFrames) -1

    # backup image settings
    backupWidth  = videoInfo['width'] /2
    backupHeight = videoInfo['height'] /2
    sizeString = str(backupWidth) + 'x' + str(backupHeight)

    command = [FFMPEG, '-i', filePath,
               '-y',  # overwrite file if it exists
               '-frames:v', '1',
               '-vf', 'select=eq(n\,' + str(lastFrame) + ')',
               rootPath + '/endframe.jpg',
               '-frames:v', '1',
               '-vf', 'select=eq(n\,' + str(lastFrame) + ')',
               '-s', sizeString,
               rootPath + '/backup.jpg']

    subprocess.Popen(command)


if __name__ == "__main__":
    ProcessFiles()
