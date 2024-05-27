#!/usr/bin/env python
import matplotlib.pyplot as plt 
import csv 
import numpy as np
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import subprocess

def findFiles(dir_path):
    # list to store files
    fileList = []
    # Iterate directory
    for file_path in os.listdir(dir_path):
        # check if current file_path is a file
        f=os.path.join(dir_path, file_path)
        if os.path.isfile(f):
            if file_path=="ps_log.csv" or file_path=="tec_log.csv" or file_path=="history.html":
                # add filename to list
                fileList.append(f)
        else:
            fileList.extend(findFiles(f))
    fileList.sort(key=lambda fileList: os.path.splitext(fileList)[1])
    fileList.reverse()
    return fileList
#seconds to minutes
def secToMin(t):
    return round(t/60, 2)
#date time to seconds
def datetimeToSec(tm):
    tm=datetime.strptime(tm, '%Y-%m-%d %H:%M:%S').timestamp()
    return int(float(tm))

def tofloat(s):
    if(s.replace(".","").isnumeric()):
        return float(s)
    else:
        return float(0)

def main(args):
    fileList=findFiles(os.getcwd())
    x_ps = [] 
    y_ps1 = [] 
    y_ps2 = [] 
    y_ps3 = [] 
    x_tec = [] 
    y_tec1 = [] 
    y_tec2 = []
    y_tec3 = []
    firstRow=""
    comment={}
    x_comment=[]
    time0sec=0
    dt_comment=dict()  #dictionary date/time---command/comment
    for fl in fileList:
        if "history" in fl:
            with open(fl, 'r') as file:
                html_content = file.read()
                # Create a BeautifulSoup object
                soup = BeautifulSoup(html_content, 'html.parser')
                tables=soup.find_all('tbody')
                tr=tables[3].find_all('tr')
                for each_tr in tr:
                    td=each_tr.find_all("td")
                    temp=[]
                    if(len(td)!=0):
                        if (td[0].get_text()+" "+td[1].get_text()) in dt_comment:
                            temp.append(dt_comment[td[0].get_text()+" "+td[1].get_text()])
                            temp.append(" /"+td[2].get_text()+"/ "+td[3].get_text())
                            dt_comment[td[0].get_text()+" "+td[1].get_text()]=temp
                        else:
                            dt_comment[td[0].get_text()+" "+td[1].get_text()]=" /"+td[2].get_text()+"/ "+td[3].get_text().replace(",", "_").replace("=","-")
               
        elif "ps_log" in fl: 
            colNo=1          
            with open(fl,'r') as csvfile: 
                lines = csv.reader(csvfile, delimiter=',') 
                firstRow=next(lines) #skip the first row
                if ("Date" in firstRow[0].split(";")[1]):
                    colNo=2
                counter=0
                for row in lines: 
                    counter=counter+1
                    arr_row=row[0].split(";")  #separate into columns
                    #column lists of millisecond[0], date/time[1], ps1[2],ps2,speed,ps3...
                    x_base=datetimeToSec(arr_row[1])
                    if counter==1:
                        base=x_base
                        time0sec=x_base-int(arr_row[0])/1000        
                    x_ps.append(secToMin(x_base-base))
                    y_ps1.append(tofloat(arr_row[colNo]))   #column number, ps1
                    y_ps2.append(tofloat(arr_row[colNo+1])) #column number, ps2
                    y_ps3.append(tofloat(arr_row[colNo+3])) #column number, ps3
                   
        elif "tec_log" in fl:
            with open(fl,'r') as csvfile: 
                lines = csv.reader(csvfile, delimiter=',') 
                next(lines) #skip the first row
                counter=0
                for row in lines: 
                    counter=counter+1
                    arr_row=row[0].split(";")
                    x_base=datetimeToSec(arr_row[1])              #second of first point
                    if counter==1:
                        base=x_base  
                        time0sec=x_base-int(arr_row[0])/1000                                        
                    x_tec.append(secToMin(x_base-base))#x-axe minutes
                    y_tec1.append(tofloat(arr_row[2])) #column number 2 chamber sensor 
                    y_tec2.append(tofloat(arr_row[3])) #column number 3 HEC sensor
                    y_tec3.append(tofloat(arr_row[4])) #column number 4 IR sensor     
        else:
            print("No file is found!") 
    y_comment=[]
    for key in list(dt_comment.keys()):  #new dt_comment:  second--command/comment
        elapse=secToMin(datetimeToSec(key)-time0sec)  #1699392873 -2023-11-07 13:34:33 starting time
        x_comment.append(elapse)
        comment[str(elapse)]=dt_comment[key]
        y_comment.append(2)  
    #plot
    fig,(ax_p, ax_p2, ax_t)=plt.subplots(3, 1, sharex=True)
    fig.suptitle('Pressure(Up)/Temperature(Down) vs Time')
    #ax_p=plt.axes([0.12,0.6,0.8,0.35])
    ax_p.plot(x_ps,y_ps1, ",-.b", label="PS1")
    ax_p.plot(x_ps,y_ps2, ",--r", label="PS2")
    #ax_p.plot(ps_comment.keys(), y_comment, "o:b")
    ax_p.tick_params(axis="both", which="major", labelsize="8")
    ax_p.tick_params(axis="both", which="minor", labelsize="8")
    ax_p.legend(fontsize="5",loc="upper left")
    #ax_p.set_xlabel("Time (minutes)", fontsize="8")
    ax_p.set_ylabel("Pressure (mbar)", fontsize="8")
    ax_p.plot(x_comment, y_comment, " yx")
    #ax_p.set_title("Pressure (mbar) vs Time (min)", fontsize="8")
    
    ax_p2.plot(x_ps,y_ps3, ",:g", label="PS3")
    ax_p2.tick_params(axis="both", which="major", labelsize="8")
    ax_p2.tick_params(axis="both", which="minor", labelsize="8")
    ax_p2.legend(fontsize="5",loc="upper left")
    ax_p2.set_ylabel("Pressure (mbar)", fontsize="8")
    ax_p2.plot(x_comment, y_comment, " yx")
  
    #ax_t=plt.axes([0.12,0.1,0.8,0.35])
    ax_t.plot(x_tec, y_tec1, ",-.r", label="Chamber")
    ax_t.plot(x_tec, y_tec2, ",--c", label="HEC")
    ax_t.plot(x_tec, y_tec3, ",:b", label="IR")
    ax_t.tick_params(axis="both", which="major", labelsize="8")
    ax_t.tick_params(axis="both", which="minor", labelsize="8")
    ax_t.legend(fontsize="5", loc="upper left")   
    ax_t.set_ylabel("Temperatures (c)", fontsize="8")
    ax_t.plot(x_comment, y_comment, " yx")
    #ax_t.set_title("Temperature (c) vs Time (min)", fontsize="8")
    ax_t.set_xlabel("Time (minute)", fontsize="8")
    
    def onclick(event):
        f_path="popup.bat"
        d_path=os.getcwd()
        file_p=os.path.join(d_path, f_path)
        #print ('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %(event.button, event.x, event.y, event.xdata, event.ydata))
        if event.xdata:
            list_comm=[e for j, e in enumerate(list(comment.keys())) if abs(float(e)-float(event.xdata))<0.01]
            if len(list_comm)>0:
                banner=""
                for i in list_comm:
                    banner= banner+str(comment[i])
                    banner=banner.replace(" ", "_").replace(",","_").replace("'","").replace('"',"").replace("[","").replace("]", "")
                    batch=file_p+" "+banner  
                    print(batch)               
                    subprocess.call(batch, shell=True)  
        
    cid = fig.canvas.mpl_connect('button_release_event', onclick)

    plt.show()
    
if __name__ == '__main__':
    main(sys.argv)