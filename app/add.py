from cryptography.fernet import Fernet
from flask import  current_app
from flask.ext.script import Command
import os,io
from models import SVSIpCamReg,SVSuserReg,SVSFaceTab,db
from manage import app
from PIL import Image
import base64,argparse,requests
import numpy as np
import cv2
import PIL.Image
import threading,time
from threading import ThreadError,Event,Thread
from flask import current_app



class Cam(object):
    def __init__(self,url,userid,camid):
        self.stream = requests.get(url,stream=True)
        self.thread_cancelled = False
        self.thread = Thread(target=self.run)
        self.count = 0
        self.imgret = Image
        self.strpath = str
        self.caid = camid
        self.usid = userid
        self.facecascade = cv2.CascadeClassifier("C:\\Users\\nirav\Envs\\svsapp\\app\\FD\\haarcascade-frontalface-alt.xml")
        print "Now camera Class initialized"






    def start(self):
       self.thread.start()
       print "Camera stream started"

    def run(self):
        bytes =''
        while not self.thread_cancelled:
            try:
                bytes+=self.stream.raw.read(1024)
                a = bytes.find('\xff\xd8')
                b = bytes.find('\xff\xd9')
                if a!=-1 and b!=-1:
                    jpg = bytes[a:b+2]
                    bytes= bytes[b+2:]
                    img = cv2.imdecode(np.fromstring(jpg,dtype=np.uint8),cv2.IMREAD_COLOR)
                    framenumber ='%08d' % (self.count)
                    screencolor = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                    faces = self.facecascade.detectMultiScale(screencolor,scaleFactor = 1.3,minNeighbors=3,minSize = (30,30),flags = cv2.CASCADE_SCALE_IMAGE)
                    if len(faces) == 0:
                        pass
                    elif len(faces) > 0:
                        print("Face Detected")
                        for (x,y,w,h) in faces:
                            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
                            self.strpath = "C:\\Users\\nirav\Envs\\svsapp\\app\\FD\\FaceCaps\\"
                            self.strpath+=framenumber+'_'+str(self.usid)+'_'+str(self.caid)
                            self.strpath+='.jpg'
                            print self.strpath
                            cv2.imwrite("C:\\Users\\nirav\Envs\\svsapp\\app\\FD\\FaceCaps\\" + framenumber+'_'+str(self.usid)+'_'+str(self.caid) + '.jpg',img)
                            self.imgret = Image.fromarray(img)
                            if self.imgret is None:
                                print 'its none'
                            else:
                                readbin = open(self.strpath,'rb').read()
                                with app.app_context():
                                    CamImgAdd =  SVSFaceTab(u_id = self.usid,cam_id= self.caid,Face_image = readbin)
                                    local_session = db.session()
                                    local_session.add(CamImgAdd)
                                    local_session.commit()
                                print("data is DB ")

                    self.count +=1

            except ThreadError:
                self.thread_cancelled = True

    def is_running(self):
        self.thread.isAlive()

    def shut_down(self):
        self.thread_cancelled = True
        while self.thread.isAlive():
            return True

def validateurl(url,userid,camid):

    try:
        response = requests.get(url,stream=True)
        return 1
    except requests.exceptions.ConnectTimeout as e:
        #print "Waited too long between bytes."
        #print "User %s for Camera ID %s Not Working %s." % (userid,camid,url)
        return 0

def CallFaceDetectSave():
        resultofallcam = []
        camtab = SVSIpCamReg.query.filter_by(FDstore=1).all()
        for recs in camtab:
            uid = recs.u_id
            camid = recs.id
            dkey = recs.key
            bdkey=bytes(dkey)
            f = Fernet(bdkey)
            bcamurl = bytes(recs.camurl_hash)
            camurl =f.decrypt(bcamurl)
            url=str(camurl)
            if validateurl(url,uid,camid) == 1:
                cam = Cam(url,uid,camid)
                cam.start()
                resultofallcam ="There are all cam started"
            else:
                resultofallcam.append("User %s for Camera ID %s Not Working %s." % (uid,camid,url))
        return resultofallcam




