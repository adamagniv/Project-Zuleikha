import csv
from subprocess import call, DEVNULL
from cv2 import VideoCapture, imwrite, CAP_DSHOW
from time import sleep
import os
from shutil import rmtree
from pathlib import Path

EMOTION_PROC = "../OpenFace_2.2.0_win_x64/FaceLandmarkVidMulti.exe"
FACE_RD = "faces"
AU_RD = "processed"
IMG_FORMAT = ".png"
CSV_FORMAT = ".csv"

# choose the right camera port index! (I disabled all webcams excluding the one I want)
CAM_PORT = 0
AU_LIST = [ "AU01", "AU02", "AU04", "AU05", "AU06", "AU07",
            "AU09", "AU12", "AU15", "AU17", "AU20", "AU23", "AU26" ]
EMOTION_ERR = "Error"

#   FEAR       = AU01 + AU02 + AU04 + AU05 + AU07 + AU20 + AU26
#   ANGER      = AU04 + AU05 + AU07 + AU23
#   SADNESS    = AU01 + AU04 + AU15
#   DISGUST    = AU09 + AU15 + AU17
#   HAPPINESS  = AU06 + AU12

class ZEmotion:
    def __init__(self, session_uuid, work=True):
        self.work = work
        self.uuid = session_uuid
        self.pic_n = 0
        self.au_exsist_l = []
        self.au_intensity_l = []
        if self.work:
            self.web_cam = VideoCapture(CAM_PORT, CAP_DSHOW)
            self.log = open("conv_logs/" + self.uuid + "_emotions.txt", "w")        

    def __del__(self):
        if self.work:
            if not self.log.closed:
                self.log.close()
            self.web_cam.release()

    def take_pic(self):
        result = None
        image = None
        dir_name = self.uuid + "_" + str(self.pic_n)
        Path(FACE_RD + "/" + dir_name).mkdir(parents=True, exist_ok=True)

        # Because the Y700 is slow to capture a good pic with the good camera
        # found out that taking a pic more than once with a sleep fixes it.
        for _ in range(10):
            result, image = self.web_cam.read()
            sleep(0.1)

        for i in range(10):
            result, image = self.web_cam.read()
            if not result:
                return None
            imwrite(FACE_RD + "/" + dir_name + "/" + str(i) + IMG_FORMAT, image)
            sleep(0.01)

        return dir_name

    def process_pic(self, dir_name):
        cmd = EMOTION_PROC + " -fdir " + FACE_RD + "/" + dir_name
        call(cmd , stdout=DEVNULL, shell=False)
        try:
            with open(AU_RD + "/" + dir_name + CSV_FORMAT) as csvfile:
                rows = csv.DictReader(csvfile, delimiter=",")
                for r in rows:
                    au_intensity = {}
                    au_exsist = {}
                    for au_name in AU_LIST:
                        au_intensity[au_name] = r[" " + au_name + "_r"].strip()
                        au_exsist[au_name] = float(r[" " + au_name + "_c"].strip())
                    self.au_intensity_l.append(au_intensity.copy())
                    self.au_exsist_l.append(au_exsist.copy())
        except:
            return False

        return True

    def process_emotion(self):
        emotion = None
        line = str(self.pic_n) + ": "
        
        for i in range(len(self.au_exsist_l)):
            if (self.au_exsist_l[i]["AU01"] == 1.0) and (self.au_exsist_l[i]["AU02"] == 1.0) and \
                (self.au_exsist_l[i]["AU04"] == 1.0) and (self.au_exsist_l[i]["AU05"] == 1.0) and \
                (self.au_exsist_l[i]["AU07"] == 1.0) and (self.au_exsist_l[i]["AU20"] == 1.0) and (self.au_exsist_l[i]["AU26"] == 1.0):
                emotion = "Fear"
                line += emotion + ": AU01= " + self.au_intensity_l[i]["AU01"] + ", AU02= " + self.au_intensity_l[i]["AU02"] + \
                        ", AU04= " + self.au_intensity_l[i]["AU04"] + ", AU05= " + self.au_intensity_l[i]["AU05"] + \
                        ", AU07= " + self.au_intensity_l[i]["AU07"] + ", AU20= " + self.au_intensity_l[i]["AU20"] + \
                        ", AU26= " + self.au_intensity_l[i]["AU26"]
                break
            elif (self.au_exsist_l[i]["AU04"] == 1.0) and (self.au_exsist_l[i]["AU05"] == 1.0) and \
                (self.au_exsist_l[i]["AU07"] == 1.0) and (self.au_exsist_l[i]["AU23"] == 1.0):
                emotion = "Anger"
                line += emotion + ": AU04= " + self.au_intensity_l[i]["AU04"] + ", AU05= " + self.au_intensity_l[i]["AU05"] + \
                        ", AU07= " + self.au_intensity_l[i]["AU07"] + ", AU23= " + self.au_intensity_l[i]["AU23"]
                break
            elif (self.au_exsist_l[i]["AU01"] == 1.0) and (self.au_exsist_l[i]["AU04"] == 1.0) and \
                (self.au_exsist_l[i]["AU15"] == 1.0):
                emotion = "Sadness"
                line += emotion + ": AU01= " + self.au_intensity_l[i]["AU01"] + ", AU04= " + self.au_intensity_l[i]["AU04"] + \
                        ", AU15= " + self.au_intensity_l[i]["AU15"]
                break
            elif (self.au_exsist_l[i]["AU09"] == 1.0) and (self.au_exsist_l[i]["AU15"] == 1.0) and \
                (self.au_exsist_l[i]["AU17"] == 1.0):
                emotion = "Disgust"
                line += emotion + ": AU09= " + self.au_intensity_l[i]["AU09"] + ", AU15= " + self.au_intensity_l[i]["AU15"] + \
                        ", AU17= " + self.au_intensity_l[i]["AU17"]
                break
            elif (self.au_exsist_l[i]["AU06"] == 1.0) and (self.au_exsist_l[i]["AU12"] == 1.0):
                emotion = "Happiness"
                line += emotion + ": AU06= " + self.au_intensity_l[i]["AU06"] + ", AU12= " + self.au_intensity_l[i]["AU12"]
                break
            
        if emotion is None:
            emotion = "Neutral"
            line += emotion

        self.log.write(line + "\n")
        return emotion

    def clean_data(self, dir_name):
        rmtree(os.path.join(FACE_RD, dir_name))
        file_list = [f for f in os.listdir(AU_RD) if not f.endswith(".avi") and not f.endswith(".csv")]
        for f in file_list:
            path = path = os.path.join(AU_RD,f)
            if os.path.isdir(path):
                rmtree(path)
            else:
                os.remove(path)

    def run(self):
        if not self.work:
            return EMOTION_ERR

        self.au_exsist_l = []
        self.au_intensity_l = []

        dir_name = self.take_pic()
        if dir_name is None:
            return EMOTION_ERR

        ret = self.process_pic(dir_name)
        self.clean_data(dir_name)
        if not ret:
            return EMOTION_ERR

        emotion = self.process_emotion()
        self.pic_n += 1

        return emotion
