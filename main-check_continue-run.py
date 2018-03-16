import sys
import os
import time
from time import ctime

global c_path,count
c_path=os.getcwd()
#print(c_path)
req_version=(3,0)
template1=""
template2=""
f_list=[]
f_len=0
m_res=[]
s_id=0
s_sts=""
count=0
constant_hamster_pro20_width = 300
constant_hamster_pro20_height = 400
constant_hamster_plus_width = 260
constant_hamster_plus_height = 300
constant_hamster_iv_width = 258
constant_hamster_iv_height = 336
constant_sg400_template_size = 400

if sys.version_info >=req_version:
    try:
        path="python/lib/"
        sys.path.insert(0,path)
        from pysgfplib import *
        from ctypes import *
        import tkinter as tk
        import pygame
        import MySQLdb as mysql

    except ImportError as e:
        print("Import failed ",e)
        exit()

elif (sys.version_info<=(2,8)):
    print("Need python intrepter greater than 3")
    exit()


def readfile(path,name):
    global c_path
    if os.getcwd()==c_path+"/"+path:
        f=open(name,"rb")
        t=f.read()
    else:
        os.chdir(path)
        f=open(name,"rb")
        t=f.read()
    return(t)

def capture(sgfplib):
    print("############### Start capturing finger print ###############")
    result = sgfplib.Create()
    finger_width=constant_hamster_plus_width
    finger_height=constant_hamster_plus_height
    try:
        if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
            print("ERROR - Unable to open SecuGen library. Exiting\n");
            exit()
        #////////////// Device intialisation ///////////////////
        result = sgfplib.Init(SGFDxDeviceName.SG_DEV_AUTO)
        if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
            print("  ERROR - Unable to initialize SecuGen library. Exiting\n");
            exit()

        print('Call sgfplib.OpenDevice()')
        result = sgfplib.OpenDevice(0)
        if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
            print("  ERROR - Unable to initialize SecuGen library. Exiting\n");
            exit()
        else:
            #input("Place the finger for the id %s on the sensor and press <<<<<<<<<< Enter >>>>>>>>",id)
            cImageBuffer = (c_char*finger_width*finger_height)()
            result = sgfplib.GetImage(cImageBuffer)
            #print('  Returned : ' + str(result))
            if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
                print("  ERROR - Unable to capture image. Exiting\n");
                #exit()
            '''else:
                 print(" Image captured ")'''
            #//////// GET IMAGE QUALITY ///////////#
            cQuality = c_int(0)
            print("+++ Call getImageQuality()")
            result = sgfplib.GetImageQuality(finger_width, finger_height, cImageBuffer, byref(cQuality))
            print('  Returned : ' + str(result))
            print("  Image quality : [" + str(cQuality.value) + "]")

            #///////////////////////////////////////////////
            #// CreateTemplate()
            print("+++ Call CreateTemplate");
            cMinutiaeBuffer = (c_char*constant_sg400_template_size)()
            result = sgfplib.CreateSG400Template(cImageBuffer, cMinutiaeBuffer);
            print('  Returned : ' + str(result))
            if (result == SGFDxErrorCode.SGFDX_ERROR_NONE):
                print("## Template created ##")
                return cMinutiaeBuffer
            else:
                print("  ERROR - Unab0le to create template. Exiting\n");
                #exit()

    finally:
        sgfplib.CloseDevice()
        result = sgfplib.Terminate()
        print('  Returned : ' + str(result))

def match_tmp(l,sgfplib,temp1,temp2):
    sts=""
    cMatched = c_bool(False)
    result=sgfplib.Create()
    #print('  Returned : ' + str(result))
    #print("Template created")
    if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
        print("ERROR - Unable to open SecuGen library. Exiting\n");
        exit()
    #////////////// Device intialisation ///////////////////
    result = sgfplib.Init(SGFDxDeviceName.SG_DEV_AUTO)
    if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
        print("  ERROR - Unable to initialize SecuGen library. Exiting\n");
        exit()
    else:
        
        #print("+++ Call MatchTemplate");
        result = sgfplib.MatchTemplate(temp1,temp2, SGFDxSecurityLevel.SL_NORMAL, byref(cMatched));
        #print('  Returned : ' + str(result))
        if (cMatched.value == True):
            sts="match"
            #print(  "<<"+sts+">>");
        else:
            sts="not match"
            #print(  "<<"+sts+">>");

        #///////////////////////////////////////////////
        #// GetMatchingScore()
        cScore = c_int(0)
        score=""
        #print("+++ Call GetMatchingScore");
        result = sgfplib.GetMatchingScore(temp1, temp2, byref(cScore));
        #print('  Returned : ' + str(result))
        score=str(cScore.value)
        print("  Score : [" + score + "]")
        return sts,score

class db_check():
    def __init__(self):
        self.dbhost="192.168.1.101"
        self.dbuser="tst_usr"
        self.dbpass="pass"
        self.dbname="zas"
        self.db=mysql.connect(self.dbhost,self.dbuser,self.dbpass,self.dbname)
        self.cu=self.db.cursor()
        print("DB connected")
    def table(self):
        try:
            qry="CREATE TABLE IF NOT EXISTS attendence (id int(100),status VARCHAR(100))"
            self.cu.execute(qry)
            print("Table created")
            qry="ALTER TABLE `attendence` CHANGE `status` `status` VARCHAR(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT 'absent'"
            self.cu.execute(qry)
            qry="ALTER TABLE `attendence` ADD PRIMARY KEY (`id`)"
            self.cu.execute(qry)
            print("Primary key added")
        except:
            self.db.rollback()
    def stud_upd(self,s_id,sts):
        stud_id=[]
        out=""
        self.table()
        try:
            qry="SELECT * FROM `attendence`"
            self.cu.execute(qry)
            res=self.cu.fetchall()
            #print(res)
            for row in res:
                stud_id.append(row[0])

            if s_id in stud_id:
                qry="UPDATE attendence SET status='%s' \
                            WHERE id='%d'" %(sts,int(s_id))
                self.cu.execute(qry)
                self.db.commit()
                out="attendence updated sucessfully for id: ",s_id
                #print(out)
                return out
            else:
                qry="INSERT INTO attendence (id,status)\
                             VALUES ('%d','%s')"%\
                             (int(s_id),sts)
                self.cu.execute(qry)
                self.db.commit()
                out="attendence inserted and updated sucessfully for id",s_id
                return out

        except:
            self.db.rollback()

        finally:

            self.db.close()

def disp(res):
    pygame.init()

    h=500
    w=150
    white=(255,255,255)
    d=pygame.display.set_mode((h,w))
    d.fill(white)
    pygame.display.set_caption("Res")
    basicfont=pygame.font.SysFont(None,20)

    txt=basicfont.render(str(res),True,(0,0,0))
    t_pos=txt.get_rect()
    t_pos.centerx=d.get_rect().centerx
    t_pos.centery=d.get_rect().centery
    d.blit(txt,t_pos)
    pygame.display.update()
    time.sleep(1)
    pygame.quit()

if __name__=="__main__":
    
    while True:
        try:
            b=""
            f_c=0
            path="images"
            sgfplib = PYSGFPLib()
            template1=capture(sgfplib)
            #print(os.getcwd())
            #c_path="/home/pi/Project/finger_print/"
            if (os.getcwd()!=c_path):
                os.chdir(c_path)
            while (template1 == None):
                template1=capture(sgfplib)
                #print("Template1:",template1)
            f_list=os.listdir(path)
            f_len=len(f_list)
            
            try:
                for f in range(f_len):

                    f_f=f_list[f]
                    #print(f_f)
                    template2=readfile(path,f_f)
                    #print(template2)
                    m_res=match_tmp(f_len,sgfplib,template1,template2)
                    #print(m_res)
                    m_res=list(m_res)
                    #print(m_res[0])
                    #print(m_res[1])
                    if ((m_res[0]=="match") and (int(m_res[1]) >=100)):
                        b=f_f.split(".")
                        s_id=int(b[0])
                        #print(s_id)
                        s_sts="present"
                        login=db_check()
                        res=login.stud_upd(s_id,s_sts)
                        #print("status: ",res)
                        disp(res)
                        if count==3:
                            count=count-f_c
                            f_c=0
                        else:
                            count=0
                    else:
                        count+=1
                        out="Sorry no match found"
                        print(out)
                        if count==f_len:
                            f_c=count
                            print(f_c)
                            disp(out)
                            count=0
                        
                        #disp(out)
                        #count=0
                    #print(count)       
            except KeyboardInterrupt:
                break
        finally:
             print("###################################################")
             print("################  THANK YOU #######################")
             print("###################################################")
             disp("Next person place the finger")
