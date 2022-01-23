import csv
from subprocess import call, DEVNULL
from cv2 import VideoCapture, imwrite, CAP_DSHOW
from time import sleep
import os
from shutil import rmtree

EMOTION_PROC = "../OpenFace_2.2.0_win_x64/FaceLandmarkImg.exe"
FACE_RD = "faces/"
AU_RD = "processed/"
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
        self.au_exsist = {}
        self.au_intensity = {}
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
        img_name = None

        # Because the Y700 is slow to capture a good pic with the good camera
        # found out that taking a pic more than once with a sleep fixes it.
        for _ in range(10):
            result, image = self.web_cam.read()
            sleep(0.1)

        if result:
            img_name = self.uuid + "_pic" + str(self.pic_n)
            imwrite(FACE_RD + img_name + IMG_FORMAT, image)

        return img_name

    def process_pic(self, img_name):
        cmd = EMOTION_PROC + " -root " + FACE_RD + " -f " + img_name + IMG_FORMAT
        call(cmd , stdout=DEVNULL, shell=False)
        try:
            with open(AU_RD + img_name + CSV_FORMAT) as csvfile:
                au_row0 = next(csv.DictReader(csvfile, delimiter=","))
                for au_name in AU_LIST:
                    self.au_intensity[au_name] = au_row0[" " + au_name + "_r"].strip()
                    self.au_exsist[au_name] = float(au_row0[" " + au_name + "_c"].strip())
        except:
            return False

        return True

    def process_emotion(self):
        emotion = "Neutral"
        line = str(self.pic_n) + ": "

        if (self.au_exsist["AU01"] == 1.0) and (self.au_exsist["AU02"] == 1.0) and \
            (self.au_exsist["AU04"] == 1.0) and (self.au_exsist["AU05"] == 1.0) and \
            (self.au_exsist["AU07"] == 1.0) and (self.au_exsist["AU20"] == 1.0) and (self.au_exsist["AU26"] == 1.0):
            emotion = "Fear"
            line += emotion + ": AU01= " + self.au_intensity["AU01"] + ", AU02= " + self.au_intensity["AU02"] + \
                    ", AU04= " + self.au_intensity["AU04"] + ", AU05= " + self.au_intensity["AU05"] + \
                    ", AU07= " + self.au_intensity["AU07"] + ", AU20= " + self.au_intensity["AU20"] + \
                    ", AU26= " + self.au_intensity["AU26"]
        elif (self.au_exsist["AU04"] == 1.0) and (self.au_exsist["AU05"] == 1.0) and \
            (self.au_exsist["AU07"] == 1.0) and (self.au_exsist["AU23"] == 1.0):
            emotion = "Anger"
            line += emotion + ": AU04= " + self.au_intensity["AU04"] + ", AU05= " + self.au_intensity["AU05"] + \
                    ", AU07= " + self.au_intensity["AU07"] + ", AU23= " + self.au_intensity["AU23"]
        elif (self.au_exsist["AU01"] == 1.0) and (self.au_exsist["AU04"] == 1.0) and \
            (self.au_exsist["AU15"] == 1.0):
            emotion = "Sadness"
            line += emotion + ": AU01= " + self.au_intensity["AU01"] + ", AU04= " + self.au_intensity["AU04"] + \
                    ", AU15= " + self.au_intensity["AU15"]
        elif (self.au_exsist["AU09"] == 1.0) and (self.au_exsist["AU15"] == 1.0) and \
            (self.au_exsist["AU17"] == 1.0):
            emotion = "Disgust"
            line += emotion + ": AU09= " + self.au_intensity["AU09"] + ", AU15= " + self.au_intensity["AU15"] + \
                    ", AU17= " + self.au_intensity["AU17"]
        elif (self.au_exsist["AU06"] == 1.0) and (self.au_exsist["AU12"] == 1.0):
            emotion = "Happiness"
            line += emotion + ": AU06= " + self.au_intensity["AU06"] + ", AU12= " + self.au_intensity["AU12"]
        else:
            line += emotion

        self.log.write(line + "\n")
        return emotion

    def clean_data(self):
        file_list = [f for f in os.listdir(AU_RD) if not f.endswith(".jpg") and not f.endswith(".csv")]
        for f in file_list:
            path = path = os.path.join("processed",f)
            if os.path.isdir(path):
                rmtree(path)
            else:
                os.remove(path)

    def run(self):
        if not self.work:
            return EMOTION_ERR

        self.au_exsist = {}
        self.au_intensity = {}

        img_name = self.take_pic()
        if img_name is None:
            return EMOTION_ERR

        ret = self.process_pic(img_name)
        self.clean_data()
        if not ret:
            return EMOTION_ERR

        emotion = self.process_emotion()
        self.pic_n += 1

        return emotion
