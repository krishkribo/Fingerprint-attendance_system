import sys
import os

global c_path
c_path=os.getcwd()
print(c_path)
req_version=(3,0)
if sys.version_info >=req_version:
    try:
        path="python/lib/"
        sys.path.insert(0,path)
        from pysgfplib import *
        from ctypes import *
        from tkinter import *
        import MySQLdb as mysql
    except ImportError as e:
        print("Import failed ",e)
        exit()
elif (sys.version_info<=(2,8)):
    print("Need python intrepter greater than 3")
    exit()


def reg_finger(id):
    global c_path
    sgfplib = PYSGFPLib()
    result = sgfplib.Create()
    #r=Tk()
    print("##################################################################")
    print(".................Finger print Library initialised.................")
    print("##################################################################")
    #...../////// Choose the appropriate device /////////........#

    constant_hamster_pro20_width = 300
    constant_hamster_pro20_height = 400
    constant_hamster_plus_width = 260
    constant_hamster_plus_height = 300
    constant_hamster_iv_width = 258
    constant_hamster_iv_height = 336
    constant_sg400_template_size = 400

    finger_width=constant_hamster_plus_width
    finger_height=constant_hamster_plus_height
    filename=id
    path="images"
    try:
        if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
            print("  ERROR - Unable to open SecuGen library. Exiting\n");
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
            #input("Place the finger for the id %s on the sensor and press <<<<<<<<<< Enter >>>>>>>>"%id)
            
            '''r.title("ReS")
            r.geometry('150x150')
            m_o=Label(r,text="Place the finger and press ok >>>")
            m_o.grid()
            rm_msg=Button(r,text="close",command=r_panel)
            rm_msg.grid(columnspan=2,padx=50,sticky=W)
            r.mainloop()
            pass'''
            cImageBuffer = (c_char*finger_width*finger_height)()
            result = sgfplib.GetImage(cImageBuffer)
            print('  Returned : ' + str(result))
            if (result == SGFDxErrorCode.SGFDX_ERROR_NONE):
                print(" Image captured ")
                '''image1File = open (filename + ".raw", "wb")
                image1File.write(cImageBuffer1)'''
            else:
                print("  ERROR - Unable to capture image. Exiting\n");
                exit()
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
                #c_path="/home/pi/Project/finger_print/"
                if (os.getcwd()==c_path):
                    if os.path.exists(path):
                        os.chdir(path)
                        minutiae1File = open(filename + ".min", "wb")
                        minutiae1File.write(cMinutiaeBuffer)
                    else:
                        os.mkdir(path)
                        os.chdir(path)
                        minutiae1File = open(filename + ".min", "wb")
                        minutiae1File.write(cMinutiaeBuffer)
                else:
                    os.chdir(c_path)
                    if os.path.exists(path):
                        os.chdir(path)
                        minutiae1File = open(filename + ".min", "wb")
                        minutiae1File.write(cMinutiaeBuffer)
                    else:
                        os.mkdir(path)
                        os.chdir(path)
                        minutiae1File = open(filename + ".min", "wb")
                        minutiae1File.write(cMinutiaeBuffer)
                print(os.getcwd())
            else:
                print("  ERROR - Unab0le to create template. Exiting\n");
                exit()
    finally:
        sgfplib.CloseDevice()
        result = sgfplib.Terminate()
        print('  Returned : ' + str(result))

        print("###########################################################")
        print("############ Finger Print Regiserted sucessfully ##########")
        print("###########################################################")


def r_panel():
    r.destroy()

    
class db_insrt():
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
            qry="CREATE TABLE IF NOT EXISTS stud_info (id int(100),name VARCHAR(100)) "
            self.cu.execute(qry)
            print("Table created")
            qry="ALTER TABLE `stud_info` ADD PRIMARY KEY(`id`)"
            self.cu.execute(qry)
            print("Primary key added")
        except:
            self.db.rollback()
    def stud_prof(self,id,name):
        stud_id=[]
        out=""
        self.table()
        try:
            qry="SELECT * FROM stud_info"
            self.cu.execute(qry)
            res=self.cu.fetchall()
            for row in res:
                stud_id.append(row[0])
            if int(id) not in stud_id:
                qry="INSERT INTO stud_info (id,name)\
                         VALUES ('%d','%s')"%\
                         (int(id),name)
                self.cu.execute(qry)
                self.db.commit()
                out=" registered sucessfully for id :%d",int(id)
                print(out)
                return out
            else:
                out="Student id already exist try some other"
                return out
                print(out)
                while True:
                    break
        except:
            self.db.rollback()

        finally:
            self.db.close()
def GUI():
    global frame
    global r_id
    global r_name

    frame=Tk()
    frame.title("Registration Pannel")
    frame.geometry('300x300')
    label1=Label(frame,text="Enter ID:")
    label2=Label(frame,text="Enter Name:")
    label1.grid(row=0,sticky=W,padx=10,pady=10)
    label2.grid(row=1,sticky=W,padx=10,pady=10)
    r_id=Entry(frame)
    r_name=Entry(frame)
    r_id.grid(row=0,column=1,padx=10,pady=10)
    r_name.grid(row=1,column=1,padx=10,pady=10)
    loginB = Button(frame, text='Ok', command=reg)
    loginB.grid(columnspan=2,padx=100,pady=20,sticky=W)
    rmuser = Button(frame, text='Exit', fg='red', command=kill)
    rmuser.grid(columnspan=2,padx=100,pady=20, sticky=W)
    frame.mainloop()


def reg():
    global msg
    stud_id=r_id.get()
    stud_name=r_name.get()
    if ((stud_id!='') and (stud_name!='')):
        reg_finger(stud_id)
        login=db_insrt()
        res=login.stud_prof(stud_id,stud_name)
        print("status: ",res)
        msg=Tk()
        msg.title("ReS")
        msg.geometry('3000x150')
        m_o=Label(msg,text=str(res)+":)",fg="blue")
        m_o.grid()
        rm_msg=Button(msg,text="close",command=msg_panel)
        rm_msg.grid(columnspan=2,padx=50,sticky=W)
        msg.mainloop()

    else:
        frame.destroy()
        GUI()

def msg_panel():
    msg.destroy()
    frame.destroy()
    GUI()

def kill():
    frame.destroy()


if __name__=='__main__':
    GUI()
