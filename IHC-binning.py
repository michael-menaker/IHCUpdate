#!/usr/bin/python
import instruments as ik
import time
import sys
import glob
import serial
import os
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import numpy as np
import piplates.DAQC2plate as DAQC2
import qrcode
from datetime import date

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

global filepath
filepath = "./images/temp.png"

global languageText
languageText = [["START", "CONTINUE", "STOP", "SETUP", "Press SETUP to Begin", "Select a COM Port", "Arrays Binned: {arraysBinned}", "Measured VDC: %.2f V", "Previous Bin: {arrayBin}", "Process Halted", "Select Multimeter COM Port", "Success. Connect Printer", "Done. Press Start to Bin", "Scan Barcode", "Connect LED Array", "Query failed, press START to retry", "Read Success. Printing Label", "Complete. Press start for next", "Controls", "Status", "COM Port", "Info", "Language"],["TERMINAR"],[]]

global scaleX
global scaleY
scaleX = 2.2
scaleY = 2


#GUI DEFINITIONS
class IHCBinning(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack
        global continueState, startState, stopState, VDC, prevBin, arraysBinned, inst, serialPort, language
        VDC = 0
        arraysBinned = 0
        serialPort = ""
        continueState = tk.IntVar()
        continueState.set(0)
        startState = tk.IntVar()
        startState.set(0)
        stopState = 0
        language = 0
        self.createWidgets()
        self.mainloop()
        
    def createWidgets(self):
        global languageText, language, arraysBinned
        self.startButton = tk.Button(win, text = languageText[language][0], font = ('Helevetica', 12), command = self.binning, bg = "green", height = int(2*scaleY), width = int(24*scaleX))
        self.startButton.grid(row = 4, column = 1)
        self.startButton["state"] = "disabled"
        self.continueButton = tk.Button(win, text = languageText[language][1], font = ('Helevetica', 12), command = lambda: continueState.set(1), bg = "yellow", height = int(2*scaleY), width = int(24*scaleX))
        self.continueButton["state"] = "disabled"
        self.continueButton.grid(row = 5, column = 1)
        self.stopButton = tk.Button(win, text = languageText[language][2], font = ('Helevetica', 12), command = self.stop, bg = "red", height = int(2*scaleY), width = int(24*scaleX))
        self.stopButton.grid(row = 6, column = 1)
        self.stopButton["state"] = "disabled"
        self.setupButton = tk.Button(win, text = languageText[language][3], font = ('Helevetica', 12), command = self.setup, bg = "bisque2", height = int(2*scaleY), width = int(24*scaleX))
        self.setupButton.grid(row = 7, column = 1)
        statusfield = tk.Label(win, text = languageText[language][4], font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
        statusfield.grid(row = 2, column = 1)
        self.serialCombobox = ttk.Combobox(win, values = [languageText[language][5]], postcommand = self.serialPorts, width = int(24*scaleX), height = int(2*scaleY))
        self.serialCombobox.grid(row = 2, column = 2)
        self.serialCombobox.current(0)
        self.serialCombobox.bind("<<ComboboxSelected>>", self.updatePort)
        self.numTestedLabel = tk.Label(win, text = languageText[language][6].format(arraysBinned = arraysBinned), font = ('Helevetica', 12), height = int(2*scaleY), width = int(24*scaleX))
        self.numTestedLabel.grid(row = 4, column = 2)
        self.currentVDCLabel = tk.Label(win, text = languageText[language][7] % VDC, font = ('Helevetica', 12), height = int(2*scaleY), width = int(24*scaleX))
        self.currentVDCLabel.grid(row = 5, column = 2)
        self.previousBinLabel = tk.Label(win, text = languageText[language][8].format(arrayBin = "N/A"), font = ('Helevetica', 12), height = int(2*scaleY), width = int(24*scaleX))
        self.previousBinLabel.grid(row = 6, column = 2)
        self.languageCombobox = ttk.Combobox(win, values = ["English", "Spanish", "French"], width = int(24*scaleX), height = int(2*scaleY))
        self.languageCombobox.grid(row = 2, column = 3)
        self.languageCombobox.bind("<<ComboboxSelected>>", self.updateLanguage)
        self.languageCombobox.current(language)
        self.columnhead1 = tk.Label(win, text = languageText[language][18], font = ('Helevetica', 12, 'bold'), relief = 'flat', bg = 'lightgrey')
        self.columnhead1.grid(row = 3, column = 1)
        self.columnhead2 = tk.Label(win, text = languageText[language][19], font = ('Helevetica', 12, 'bold'), relief = 'flat', bg = 'lightgrey')
        self.columnhead2.grid(row = 1, column = 1)
        self.columnhead3 = tk.Label(win, text = languageText[language][20], font = ('Helevetica', 12, 'bold'), relief = 'flat', bg = 'lightgrey')
        self.columnhead3.grid(row = 1, column = 2)
        self.columnhead4 = tk.Label(win, text = languageText[language][21], font = ('Helevetica', 12, 'bold'), relief = 'flat', bg = 'lightgrey')
        self.columnhead4.grid(row = 3, column = 2)
        self.columnhead4 = tk.Label(win, text = languageText[language][22], font = ('Helevetica', 12, 'bold'), relief = 'flat', bg = 'lightgrey')
        self.columnhead4.grid(row = 1, column = 3)
        self.versionLabel = tk.Label(win, text = "Version 1.0", font = ('Helevetica', 12), height = int(2*scaleY), width = int(24*scaleX), relief = 'flat', bg = 'lightgrey')
        self.versionLabel.grid(row = 8, column = 3)
        self.mainloop()
               
    def close():
        win.destroy()

    def stop(self):
        global stopState
        statusfield = tk.Label(win, text = languageText[language][9], font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
        statusfield.grid(row = 2, column = 1)
        continueState.set(1)
        stopState = 1
        self.stopButton["state"] = "disabled"
        self.continueButton["state"] = "disabled"
        self.setupButton["state"] = "normal"
        self.startButton["state"] = "normal"
        
    def updatePort(self, event):
        global serialPort
        serialPort = self.serialCombobox.get()
        
    def updateLanguage(self, event):
        global language
        langString= self.languageCombobox.get()
        if(langString == "English"):
            language = 0
        elif(langString == "Spanish"):
            language = 1
        elif(langString == "French"):
            language = 2
        self.createWidgets()
            
    def serialPorts(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        self.serialCombobox["values"] = result
    
    def multimeterSetup(self):
        global inst
        try:
            inst = ik.Instrument.open_serial(port = serialPort, baud = 115200, vid = None, pid = None, serial_number = None, timeout = 3, write_timeout = 3)        
            inst.terminator = "\r"
        except:
            statusfield = tk.Label(win, text = "Serial failure. Press CONTINUE", font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
            statusfield.grid(row = 2, column = 1)
            self.continueButton.wait_variable(continueState)
            win.destroy()
        
    def printLabel(self, array_bin, VDC):
        DPI = 203
        label_width = 0.5
        label_height = label_width
        img_width = int(label_width * DPI)
        img_height = img_width

        label_img = Image.new('1', (img_width, img_height), 1)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size= 2,
            border=4,
        )
        qr.add_data(array_bin + "," + str(VDC) + "," + str(date.today()))
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")

        d = ImageDraw.Draw(label_img)
        fontsize = 37
        fontpath = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        font = ImageFont.truetype(font = fontpath, size = fontsize)
        d.text((img_width/2, 12), array_bin, 0, font = font, anchor = "mt")

        label_img.paste(qr_img, box = (int((img_width/2)-30), int(img_height/2)-17))
        label_img.save(filepath)
        os.system("lp -o media=Custom.0.5x0.5in {filepath}".format(filepath=filepath))
        
    def query(self):
        attempts = 3
        global inst
        resp = 1
        while(resp != 0):
            resp = int(inst.query("QM"))
            if(resp == 1):
                print("Syntax error in query, terminating program...\n")
                return 1
            if(resp == 2):
                print("Execution error in query, terminating program...\n")
                return 1
            if(resp == 5):
                attempts -= 1
                if(attempts == 0):
                    print("No attempts remaining, terminating program...")
                    return 1
                print("No data available, retrying query. Attempts remaining: " + str(attempts))
                time.sleep(2)
        return 0
        
    def binArray(self, VDC):
        LSL = 156.37
        USL = 162.07
        bandwidth = 1.9
        array_bin  = ""
        if VDC < 150 or VDC > 165:
            array_bin = "F"
        elif VDC <= LSL + bandwidth:
            array_bin = "L"
        elif VDC <= LSL + 2*bandwidth:
            array_bin = "N"
        else:
            array_bin = "H" 
        return array_bin   
    
    def parseSerial(self, code):
        #first 4 digits are mm/yy
        return code[4:]
    
    def parseDate(self, code):
        return code[0:4]
    
    def readVDC(self):
        global inst, VDC
        self.VDC = np.float(inst.read().split(',')[0])

    def setup(self):
        statusfield = tk.Label(win, text = languageText[language][10], font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
        statusfield.grid(row = 2, column = 1)
        self.startButton["state"] = "disabled"
        self.setupButton["state"] = "disabled"
        self.continueButton["state"] = "normal"
        self.continueButton.wait_variable(continueState)
        continueState.set(0)
        self.multimeterSetup()
        statusfield = tk.Label(win, text = languageText[language][11], font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
        statusfield.grid(row = 2, column = 1)
        self.continueButton.wait_variable(continueState)
        continueState.set(0)
        statusfield = tk.Label(win, text = languageText[language][12], font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
        statusfield.grid(row = 2, column = 1)
        self.startButton["state"] = "normal"
        self.continueButton["state"] = "disabled"
        
    def binning(self):
        global stopState, arraysBinned, VDC
        startState.set(0)
        self.startButton["state"] = "disabled"
        self.continueButton["state"] = "normal"
        self.stopButton["state"] = "normal"
        statusfield = tk.Label(win, text = languageText[language][13], font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
        statusfield.grid(row = 2, column = 1)
        #barcode = simpledialog.askstring(title="IHC Voltage Binning",prompt= languageText[language][13])
        #serial_num = self.parseSerial(barcode)
        statusfield = tk.Label(win, text = languageText[language][14], font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
        statusfield.grid(row = 2, column = 1)
        self.continueButton.wait_variable(continueState)
        continueState.set(0)
        if stopState == 1:
            stopState = 0
            return 0
        DAQC2.clrDOUTbit(0,0)#turn relay on
        self.after(5000)#wait for multimeter to adjust
        try:
            if self.query() == 1:
                statusfield = tk.Label(win, text = languageText[language][15], font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
                statusfield.grid(row = 2, column = 1)
                return 0
        except:
            statusfield = tk.Label(win, text = "Serial failure. Press CONTINUE", font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
            statusfield.grid(row = 2, column = 1)
            self.continueButton.wait_variable(continueState)
            win.destroy()
        self.readVDC()
        #print(self.VDC)
        self.currentVDCLabel = tk.Label(win, text = languageText[language][7] % self.VDC, font = ('Helevetica', 12), height = int(2*scaleY), width = int(24*scaleX))
        self.currentVDCLabel.grid(row = 5, column = 2)
        statusfield = tk.Label(win, text = languageText[language][16], font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
        statusfield.grid(row = 2, column = 1)
        arrayBin = self.binArray(self.VDC)
        self.previousBinLabel = tk.Label(win, text = languageText[language][8].format(arrayBin = arrayBin), font = ('Helevetica', 12), height = int(2*scaleY), width = int(24*scaleX))
        self.previousBinLabel.grid(row = 6, column = 2)
        self.printLabel("H", self.VDC)
        arraysBinned += 1
        DAQC2.setDOUTbit(0,0)#turn relay off
        self.numTestedLabel = tk.Label(win, text = languageText[language][6].format(arraysBinned = arraysBinned), font = ('Helevetica', 12), height = int(2*scaleY), width = int(24*scaleX))
        self.numTestedLabel.grid(row = 4, column = 2)
        statusfield = tk.Label(win, text = languageText[language][17], font = ('Helevetica', 12), relief = "solid", height = int(2*scaleY), width = int(24*scaleX))
        statusfield.grid(row = 2, column = 1)
        self.startButton["state"] = "normal"
        self.continueButton["state"] = "disabled"

DAQC2.setDOUTbit(0,0)#make sure relay is initially off
win = tk.Tk()
win.title("IHC Voltage Binning")
win.geometry("2000x1000")
win.maxsize(2000,1000)
win.config(bg = "lightgrey")

im = Image.open("./images/appleton.png")
im = im.resize((int(im.width//1.4), int(im.height//1.4)))
appletonlogo = ImageTk.PhotoImage(im)
img_label = tk.Label(image = appletonlogo)
img_label.grid(row = 7, column = 3)
win.protocol("WM_DELETE_WINDOW", IHCBinning.close)
app = IHCBinning()
win.mainloop
