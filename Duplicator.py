#!/usr/bin/python3

"""
RPi dc3dd Duplicator

runs using python3.2 (on RPi)
uses tkinter (may need to be installed, sudo apt-get install python-tk)

Requires :  dc3dd (sudo apt-get install dc3dd)

"""

from tkinter import *
from tkinter.scrolledtext import *
from tkinter.messagebox import * # onExit popup box
from tkinter.font import Font, nametofont
from tkinter.filedialog import askdirectory

from tkinter.ttk import * # overwrites any methods also defined by tkinter (above)

import os, re, string, subprocess
from subprocess import check_output


class Dup_GUI(Frame, object):
    def __init__(self, master):
        super(Dup_GUI, self).__init__(master)

        self.master = master # master = 'root'

        ##  WHO AM I ?
        #print("Who am I: " + self.winfo_class())  # = 'Frame' !!
        #print("Who am I: " + self.__class__.__name__) # = 'Dup_GUI'

        self.master.protocol("WM_DELETE_WINDOW", self.onExit)


        #---------------------------------------------------------
        # ttk STYLE CONFIGURATION & MAPPING
        #---------------------------------------------------------

        
        ## LEARNING POINT: ttk Styles
        # print(ttk.Style().layout("TCheckbutton"))
        #[('Checkbutton.padding', {'children': [('Checkbutton.indicator', {'side': 'left', 'sticky': ''}),
        #                       ('Checkbutton.focus', {'children': [('Checkbutton.label',{'sticky': 'nswe'})],
        #                       'side': 'left', 'sticky': 'w'})],'sticky': 'nswe'})]
        
        # print(ttk.Style().element_options("Checkbutton.indicator"))
        #('-background', '-indicatorcolor', '-indicatorrelief', '-indicatordiameter', '-indicatormargin', '-borderwidth')
        
        #print(ttk.Style().lookup("Checkbutton", "indicatordiameter"))
        # 10
        Style().configure("TCheckbutton", indicatordiameter = 20, borderwidth = 4)

        # print(ttk.Style().layout("Vertical.TScrollbar"))
        # [('Vertical.Scrollbar.trough', {'children': [('Vertical.Scrollbar.uparrow', {'side': 'top', 'sticky': ''}),
        #                       ('Vertical.Scrollbar.downarrow', {'side': 'bottom', 'sticky': ''}),
        #                       ('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'ns'})]
        # print(ttk.Style().lookup("Vertical.TScrollbar", "arrowsize"))
        # 12
        #ttk.Style().configure("Vertical.TScrollbar", arrowsize = 20) ## DOESNT WORK !!!!
        Style().configure("TCombobox", arrowsize = 20)

        # needed as 'from tkinter.ttk import *' used instead of 'import tkinter.ttk'
        Style().map("TEntry", background = [("disabled", "white")], foreground = [("disabled", "black")])

        
        #--------------------------------------------------------------------
        # APPLICATION WIDE VARIABLES
        #--------------------------------------------------------------------

        self.debugMode = 1 # 0=None, 1=Exit procedures OK/Error, 2 = Everything

        #  apps running
        self.apps = [] # list of apps for goto menu & knowing what  is running
        self.apps.append(self.__class__.__name__)
        self.currentApp = ""


        #--------------------------------------------------------------------
        # GUI SETUP
        #--------------------------------------------------------------------

        SW = self.master.winfo_screenwidth()
        SH = self.master.winfo_screenheight()

        self.screenWidth = int(SW * 0.60)
        self.screenHeight = int(SH * 0.60)
        self.widgetscale = round(SW / 800, 1)
        self.fontscale = int(SW / 80)

        # LIST OF ALL DEFAULT FONTS
        # "TkDefaultFont", "TkTextFont", "TkFixedFont", "TkMenuFont", "TkHeadingFont"
        # "TkCaptionFont", "TkSmallCaptionFont", "TkIconFont", "TkTooltipFont"
        for fontname in ["TkDefaultFont", "TkTextFont", "TkMenuFont"]:
            default_font = nametofont(fontname)
            default_font.configure(size = int(self.fontscale))

        self.bind("<Configure>", self.onResize)

        self.master.geometry(str(self.screenWidth) + "x" + str(self.screenHeight - 30))
        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.grid(column = 0, row = 0, sticky = (N, S, W, E))

        self.createMenu()
        self.mainFrame = Frame(self)
        self.mainFrame.grid(row = 0, column = 0, sticky = (N, S, W, E))
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)

        self.update_idletasks()

    #--------------------------------------------------------------------
    # CREATE GUI MAIN WINDOW, MENU & STATUS BAR
    #--------------------------------------------------------------------
    def createMenu(self):
        try:
            self.menubar = Menu(self.master)
            self.master.configure(menu = self.menubar)

            self.menubar.add_command(label = "Exit", command = lambda: self.onExit())

            if self.debugMode > 0:
                print("CreateMenu: Ok")

        except:
            if self.debugMode > 0:
                print("CreateMenu: Error")


    #--------------------------------------------------------------------
    # NAVIGATION
    #--------------------------------------------------------------------
    def todo(self):
        #default command during development
        pass

    def onResize(self, event):
        SW = self.winfo_width()
        self.fontscale = int(SW / 80)
        self.widgetscale = round(SW / 800, 1) # ????

        if self.fontscale < 8: self.fontscale = 8

        for fontname in ["TkDefaultFont", "TkTextFont", "TkMenuFont",
                         "TkCaptionFont", "TkFixedFont", "TkIconFont" ]:
            default_font = nametofont(fontname)
            default_font.configure(size = self.fontscale)

        Style().configure("TCheckbutton", indicatordiameter = int(1.5 * self.fontscale), borderwidth = 4)
        Style().configure("TCombobox", arrowsize = int(1.5 * self.fontscale))
        
        self.update_idletasks()


    def onExit(self):
        try:
            if askokcancel("Just Checking", "Do you want to close now?"):
                self.master.destroy()

            if self.debugMode > 0: print("on Exit: Ok")

        except:
            if self.debugMode > 0:
                print("on Exit: Error")


#-------------------------------------------------
# Duplicator
#-------------------------------------------------
class Duplicator(Frame):
    def __init__(self, master, app, no_of_dest_drives):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print("Who am I:  " + self.winfo_class())  # = 'Frame' !!
        #print("Who is my master: " + master.__class__.__name__) # = Frame
        #print("Who is my app: " + app.__class__.__name__) # = Dup_GUI
        #print("Who am I:  " + self.__class__.__name__) # = 'Duplicator'

        self.app = app
        self.app.apps.append(self.__class__.__name__)

        self.monitorMode = "Insert" # options: Insert, Overtype

        self.bind("<Configure>", self.onResize)

        #----------------START DELARATIONS------------------------------
        self.no_of_dest_drives = no_of_dest_drives
        self.err = 0
        
        ##
        # Directory Copier items
        self.src_dir_path = StringVar()
        self.src_dir_path.set("")
        self.src_fldr = StringVar()
        self.src_fldr.set("")

        self.dest_fldr = []
        for count in range (self.no_of_dest_drives):
            self.dest_fldr.append(StringVar())
            self.dest_fldr[count].set("")

        ##
        # Drive Cloner items
        self.device_list = [] # all devices discovered by 'lsblk' (name, mountpoint)
        self.drive_locks = [] # boolean value True if 'locked'
        self.drive_list = [] # only those drives which are NOT 'locked' (used by Comboboxes)
        self.dest = [] # a list of StringVar
        
        self.default_tab_spacing =  [4.0, 7.0, 9.0, 11.0, 13.0, 14.0]
        self.driveList_tabsL = []
        for i in range(len(self.default_tab_spacing)):
            self.driveList_tabsL.append(round(self.default_tab_spacing[i] * self.app.widgetscale, 1))
        d = self.driveList_tabsL
        self.driveList_tabs = str(d[0])+"c "+str(d[1])+"c r "+str(d[2])+"c r "+str(d[3])+"c r "+str(d[4])+"c r "+str(d[5])+"c"

        
        #------------------END DELARATIONS------------------------------

        self.createWidgets()

        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.grid(column = 0, row = 0, sticky = (N, S, W, E))

    def createWidgets(self):
        self.nBook = Notebook(self)
        self.nBook.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = (N, S, W, E))

        ## DIRECTORY COPIER
        self.directoryCopy = Frame(self.nBook, padding = (5, 5, 5, 5))
        self.nBook.add(self.directoryCopy, text = "Directory Copier")
        
        r = 0
        c = 0
        # Source Directory Selection
        Label(self.directoryCopy, text = "Source").grid(row = r, column = c, columnspan = 3, pady = (5, 0))
        Label(self.directoryCopy, text = "Root Path").grid(row = r + 1, column = c)
        self.src_dir_path_entry = Entry(self.directoryCopy, textvariable = self.src_dir_path, width = 30)
        self.src_dir_path_entry.configure(state = "disabled")
        self.src_dir_path_entry.grid(row = r + 1, column = c + 1, padx = 5, pady = 5)
        self.src_dir_butt = Button(self.directoryCopy, text = "Browse", command = lambda: self.buttonHandler('src_fldr'))
        self.src_dir_butt.grid(row = r + 1, column = c + 2, padx = 5, pady = 5)

        Label(self.directoryCopy, text = "Copy folder").grid(row = r + 2, column = c)
        self.src_fldr_entry = Entry(self.directoryCopy, textvariable = self.src_fldr, width = 30)
        self.src_fldr_entry.configure(state = "disabled")
        self.src_fldr_entry.grid(row = r + 2, column = c + 1, padx = 5, pady = 5)

        Button(self.directoryCopy, text = "Reset", command = lambda: self.reset()).grid(row = r + 4, column = c)
        self.go_butt = Button(self.directoryCopy, text = "GO !", command = lambda: self.goDirCopy(), state = "disabled")
        self.go_butt.grid(row = r + 4, column = c + 1)

        c = 4
        # Destination Directory Selections
        Label(self.directoryCopy, text = "Destination").grid(row = r, column = c, columnspan = 3, pady = (5, 0))

        self.dest_fldr_butt = []
        for count in range(self.no_of_dest_drives):
            r += 1
            Browse_Label(self.directoryCopy, "Dest " + str(count + 1), [r, c])
            Browse_Entry(self.directoryCopy, self.dest_fldr[count], [r, c + 1])
            self.dest_fldr_butt.append(Browse_Button(self.directoryCopy, self, "dest_fldr" + str(count + 1), [r, c + 2]))

        r += 1
        c = 0
        # Monitor
        self.monitor = ScrolledText(self.directoryCopy, width = 10, height = 10, font = "TkTextFont", state = "disabled")
        self.monitor.vbar.configure(width = 2 * self.app.fontscale)
        self.monitor.grid(row = r, column = c, columnspan = 7, padx = 10, pady = 10, sticky = (N, S, W, E))
        self.columnconfigure(3, weight = 1)
        self.rowconfigure(r, weight = 1)

        ## DRIVE CLONER ##
        self.driveCloner = Frame(self.nBook, padding = (5, 5, 5, 5))
        self.nBook.add(self.driveCloner, text = "Drive Cloner")

        r = 0
        c = 0
        # Source Drive Selection
        Label(self.driveCloner, text = "Source").grid(row = r, column = c, columnspan = 3, pady = (5, 0))
        Label(self.driveCloner, text = "Drive").grid(row = r + 1, column = c)
        self.src_combo = Browse_Combo(self.driveCloner, self, "src", [r + 1, c + 1])

        Button(self.driveCloner, text = "Reset", command = lambda: self.reset()).grid(row = r + 4, column = c)
        self.start_butt = Button(self.driveCloner, text = "START !", command = lambda: self.startDriveClone(), state = "disabled")
        self.start_butt.grid(row = r + 4, column = c + 1)

        c = 4
        # Destination Drive Selections
        Label(self.driveCloner, text = "Destination").grid(row = r, column = c, columnspan = 3, pady = (5, 0))

        self.dest_combo = []
        for count in range(self.no_of_dest_drives):
            r += 1
            Browse_Label(self.driveCloner, "Dest " + str(count + 1), [r, c])
            self.dest_combo.append(Browse_Combo(self.driveCloner, self, "dest " + str(count + 1), [r, c + 1]))

        r += 1
        c = 0
        # Monitor
        self.monitor2 = ScrolledText(self.driveCloner, width = 10, height = 10, font = "TkTextFont", state = "disabled")
        self.monitor2.vbar.configure(width = 2 * self.app.fontscale)
        self.monitor2.grid(row = r, column = c, columnspan = 6, padx = 10, pady = 10, sticky = (N, S, W, E))
        self.columnconfigure(3, weight = 1)
        self.rowconfigure(r, weight = 1)


        # IDENTIFY DRIVES
        self.driveIdentify = Frame(self.nBook, padding = (5, 5, 5, 5))
        self.nBook.add(self.driveIdentify, text = "Identify Drives", sticky = 'nswe')
        
        r = 0
        c = 0
        self.identify_butt = Button(self.driveIdentify, text = "Get Drives", command = lambda: self.buttonHandler('identify'))
        self.identify_butt.grid(row = r, column = c, padx = 5, pady = 5)

        # Monitor
        self.monitorID = ScrolledText(self.driveIdentify, width = 10, height = 5, font = "TkTextFont",
                                      state = "disabled", tabs = self.driveList_tabs)
        self.monitorID.vbar.configure(width = 2 * self.app.fontscale)
        self.monitorID.grid(row = r + 1, column = c, columnspan = 2, padx = 10, pady = 10, sticky = (N, S, W, E))

        self.driveIdentify.columnconfigure(1, weight = 1)
        self.driveIdentify.rowconfigure(r + 1, weight = 1)


    def buttonHandler(self, button):
        if button == 'src_fldr':
            directory = askdirectory()
            if directory:
                (filepath, dirname) = os.path.split(directory)
                self.src_dir_path.set(filepath + '/')
                self.src_fldr.set(dirname)
                self.dest_fldr_butt[0].configure(state = "normal")

        elif button[:9] == "dest_fldr":
            directory = askdirectory()
            if directory:
                x = int(button[9:]) # drives numbered 1 to X, array elements are 0 to X-1
                self.dest_fldr[x - 1].set(directory)
                if x == 1:
                    self.go_butt.configure(state = "normal")
                if x < self.no_of_dest_drives:
                    self.dest_fldr_butt[x].configure(state = "normal")

        elif button == "identify":
            self.identifyDrives()

        elif button == "src":
            pass

        elif button[:4] == "dest":
            pass

    def onResize(self, event):
        self.after(100, self.delayedResize)
        self.update_idletasks()

    def delayedResize(self):
        self.monitor.vbar.configure(width = int(1.5 * self.app.fontscale))
        self.monitor2.vbar.configure(width = int(1.5 * self.app.fontscale))
        self.monitorID.vbar.configure(width = int(1.5 * self.app.fontscale))

        for i in range(len(self.default_tab_spacing)):
            self.driveList_tabsL[i] = round(self.default_tab_spacing[i] * self.app.widgetscale, 1)
            
        d = self.driveList_tabsL
        self.driveList_tabs = str(d[0])+"c "+str(d[1])+"c r "+str(d[2])+"c r "+str(d[3])+"c r "+str(d[4])+"c r "+str(d[5])+"c"
        self.monitorID.configure(tabs = self.driveList_tabs)

    def reset(self):
        #  reset Directory Copier
        self.src_dir_path.set("")
        self.src_fldr.set("")

        for count in range(self.no_of_dest_drives):
            self.dest_fldr[count].set("")
            self.dest_fldr_butt[count].configure(state = "disabled")

        self.go_butt.configure(state = "disabled")

        self.monitor.configure(state = "normal")
        self.monitor.delete(0.0, END)
        self.monitor.configure(state = "disabled")

        #  reset Drive Cloner
        self.devs = 0
        self.drive_list = []
        self.dest = []
        
        self.src_combo.set("")
        self.src_combo.configure(values = self.drive_list)

        for i in range(self.no_of_dest_drives):
            self.dest_combo[i].set("")
            self.dest_combo[i].configure(values = self.drive_list, state = "disabled")

        self.monitor2.configure(state = "normal")
        self.monitor2.delete(0.0, END)
        self.monitor2.configure(state = "disabled")

        self.monitorID.configure(state = "normal")
        self.monitorID.delete(0.0, END)
        self.monitorID.configure(state = "disabled")
        
        try:
            if self.lockdrives.winfo_exists(): self.lockdrives.destroy()
        except: pass

        
    def talk_to_dc3dd(self, src_file, cmd, monitor):
        self.dup_process = subprocess.Popen(cmd, stderr=subprocess.PIPE, preexec_fn=os.setpgrp) # note STDERR!!
        output = ""

        while True:
            self.update()
            char = self.dup_process.stderr.read(1).decode(encoding = "ascii", errors = "ignore")
            if char == "" and self.dup_process.poll() != None: # 'None' indicates subprocess is still running
                if self.err == 0:
                    info = "##    " + src_file + "  --Ok--    ##\n\n"
                else:
                    info = "##    " + src_file + "  --Error--    ##\n\n"
                self.post_info(monitor, info)
                return

            output += char
            if output.find('\r') >= 0:
                info = output.strip('\r')
                output = ""
                if not info.isspace():
                    self.post_info(monitor, info + '\n')
                    self.monitorMode = "Overtype"
            elif output.find('\n')>= 0:
                self.monitorMode = "Insert"
                info = output.replace('  ', '')
                self.post_info(monitor, info)
                if output.find("[!!]") >= 0:
                    self.err += 1
                output = ""
            else:
                pass
                #print(char, end = "")

    def post_info(self, monitor, info):
        monitor.configure(state = "normal")
        
        if self.monitorMode == "Overtype":
            end = monitor.index("insert")
            start = monitor.index("insert -1 lines")
            monitor.delete(start, end)
            
        monitor.insert(END, info)
        monitor.configure(state = "disabled")
        monitor.see(END)
        self.update()


    #----------------DIRECTORY COPIER------------------------------
    def goDirCopy(self):
        if self.go_butt["text"] == "GO !":
            self.go_butt.configure(text = "CANCEL !!!")

            self.src_root = self.src_dir_path.get()
            self.cpy_fldr = self.src_fldr.get()
            self.src_longpath = os.path.join(self.src_root, self.cpy_fldr)

            self.dest_fldr_list = []
            for count in range(self.no_of_dest_drives):
                if self.dest_fldr[count].get():
                    self.dest_fldr_list.append(self.dest_fldr[count].get())

            self.err = 0

            # create destination directories
            for root, dirs, files in os.walk(self.src_root):
                for src_d in dirs:
                    src_d_full = os.path.join(root, src_d)
                    if len(src_d_full) >= len(self.src_longpath) and src_d_full.find(self.src_longpath) >= 0: # ie found a cpy_fldr & its subfolders
                        for dest_fldr in self.dest_fldr_list:
                            dest_path = os.path.join(dest_fldr +'/', src_d_full.replace(self.src_root, ""))
                            if not os.path.exists(dest_path):
                                os.mkdir(dest_path)

            self.walk_results = os.walk(self.src_root)
            self.get_src_filelist()

        else:
            self.go_butt.configure(text = "GO !")
            self.after_cancel(self.next_dup) # cancel the next iteration of next_dup
            print("Attempting to CANCEL")
            os.system("sudo kill %s" % (self.dup_process.pid, ))

            info = "\n\n  FILE COPY CANCELLED with " + str(self.err) + " errors"
            self.monitor.configure(state = "normal")
            self.monitor.insert(END, info)
            self.monitor.configure(state = "disabled")
            self.monitor.see(END)
            
    def get_src_filelist(self):
        try:
            root, dirs, files = next(self.walk_results)
            self.walk_root = root
            self.walk_filelist = []
            self.walk_filelist.extend(files)
            self.walk_filecount = len(self.walk_filelist)
            self.walk_counter = 0

            self.duplicate_file()

        except:
            info = "\n####    FILE COPY COMPLETE with " + str(self.err) + " errors    ####\n\n"
            self.monitor.configure(state = "normal")
            self.monitor.insert(END, info)
            self.monitor.configure(state = "disabled")
            self.monitor.see(END)

            self.go_butt.configure(text = "GO !")


    def duplicate_file(self):
        if self.walk_root.find(self.src_longpath) >= 0 and self.walk_filecount > 0:
            item = self.walk_filelist[self.walk_counter]

            # replace spaces with underscore in source directory filenames
            if item.find(" ") >= 0:
                item_cln = item.replace(" ", "_")
                os.rename(os.path.join(self.walk_root, item), os.path.join(self.walk_root, item_cln))
            else:
                item_cln = item

            # start duplicating file
            src_file = os.path.join(self.walk_root, item_cln)
            cmd = []
            cmd.append("dc3dd")
            cmd.append("if=" + src_file)
            for dest_fldr in self.dest_fldr_list:
                dest_file = os.path.join(dest_fldr, src_file.replace(self.src_root, ""))
                cmd.append("of=" + dest_file)

            self.talk_to_dc3dd(src_file, cmd, self.monitor)
            self.walk_counter += 1
            if self.walk_counter < self.walk_filecount:
                self.next_dup = self.after(500, self.duplicate_file) # schedule next file, named to enable 'cancel'

            else:
                self.next_dup = self.get_src_filelist()

        else:
            self.next_dup = self.get_src_filelist() # next step in os.walk

    #----------------END DIRECTORY COPIER------------------------



    #----------------DRIVE CLONER-------------------------------------

    def identifyDrives(self):
        lsblk_results = []
        self.device_list = []
        self.drive_locks = []
        self.devs = 0
        lsblk = subprocess.Popen(['lsblk'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in lsblk.stdout:
            self.devs += 1
            line = line.decode('ascii', 'ignore') # 'ascii' or 'utf-8', 'ignore' errors in the decoding
            parts = re.split(r'\s+', line.strip())
            name, majmin, rm, size, ro, devtype = parts[:6]
            if len(parts) > 6:
                mountpoint = parts[6]
            else:
                mountpoint = None

            lsblk_results.append([name, majmin, rm, size, ro, devtype, mountpoint])
            self.device_list.append([name, mountpoint])

        self.monitorID.configure(state = "normal")
        self.monitorID.insert(END, "\t***   System Devices Report (command line: lsblk)   ***\n")
        
        for i in range(7): self.monitorID.insert(END, lsblk_results[0][i] + "\t")
        for d in range(1, self.devs):
            self.monitorID.insert(END, "\n")
            for i in range(7):
                if lsblk_results[d][i] != None:
                    self.monitorID.insert(END, lsblk_results[d][i] + "\t")
        self.monitorID.configure(state = "disabled")

        ##  LOCK DRIVES
        try:
            if self.lockdrives.winfo_exists(): self.lockdrives.destroy()
        except: pass
        
        self.lockdrives = Frame(self.nBook, padding = (5, 5, 5, 5))
        self.nBook.add(self.lockdrives, text = "Lock Drives", sticky = 'nswe')

        info = "Check those drives you want to EXCLUDE from the selection lists"
        Label(self.lockdrives, text = info).grid(columnspan = 3, sticky = W)
        info = "(Note, drives 'mmcblk*' are initially locked by default)\n"
        Label(self.lockdrives, text = info).grid(columnspan = 3, sticky = W)

        for d in range(1, self.devs):
            self.drive_locks.append(BooleanVar())
            if self.device_list[d][1]:
                Label(self.lockdrives, text = self.device_list[d][1]).grid(row = d + 1, column = 0, sticky = E)
            name = self.device_list[d][0]
            if name[:6] == "mmcblk":
                self.drive_locks[d-1].set(True)
            Checkbutton(self.lockdrives, text = name, variable = self.drive_locks[d - 1],
                        width = 12, command = lambda: self.createDriveList()).grid(row = d + 1, column = 1)

        self.createDriveList()
        self.src_combo.configure(state = "readonly")

    def createDriveList(self):
        self.drive_list = []
        for d in range(1, self.devs):
            if self.drive_locks[d -1].get() == False:
                self.drive_list.append(self.device_list[d][0])
        
        self.src_combo.set("")
        self.src_combo.configure(values = self.drive_list)
        for i in range(self.no_of_dest_drives):
            self.dest_combo[i].set("")
            self.dest_combo[i].configure(values = self.drive_list, state = "disabled")

            self.dest = []

    def comboSelected(self, comboName):
        if comboName == 'src':
            self.dest_combo[0].configure(state = "readonly")
        elif comboName[:4] == "dest":
            x = int(comboName[4:]) # drives numbered 1 to X, array elements are 0 to X-1
            if x == 1:
                self.start_butt.configure(state = "normal")

            self.dest.append(self.dest_combo[x -1].get())
            if x < self.no_of_dest_drives:
                self.dest_combo[x].configure(state = "readonly")

    def startDriveClone(self):
        if self.start_butt["text"] == "START !":
            self.start_butt.configure(text = "CANCEL !!!")
            src = self.src_combo.get()
            self.err = 0
            
            cmd = ["sudo", "dc3dd", "if=/dev/" + src]
            for i in range(len(self.dest)):
                cmd.append("of=/dev/" + self.dest[i])
            self.talk_to_dc3dd(src, cmd,self.monitor2)

        else:
            self.start_butt.configure(text = "START !")
            os.system("sudo kill %s" % (self.dup_process.pid, ))
            # alternative might be subprocess.Popen("sudo kill %s" % (self.dup_process.pid, ))

        
    #----------------END DRIVE CLONER------------------------------



#-------------------------------------------------
# Widget Classes
#-------------------------------------------------

class Browse_Label(Label):
    def __init__(self, master, labeltxt, pos):
        Label.__init__(self, master = master)

        r = pos[0]
        c = pos[1]
        self.configure(text = labeltxt)
        self.grid(row = r, column = c)

class Browse_Entry(Entry):
    def __init__(self, master, varName, pos):
        Entry.__init__(self, master = master)

        r = pos[0]
        c = pos[1]
        self.configure(textvariable = varName, width = 25)
        self.configure(state = "disabled")
        self.grid(row = r, column = c, padx = 5, pady = 5)

class Browse_Combo(Combobox):
    def __init__(self, master, owner, comboName, pos):
        Combobox.__init__(self, master = master)

        r = pos[0]
        c = pos[1]
        self.configure(width = 25, state = "disabled")
        self.grid(row = r, column = c, padx = 5, pady = 5)
        self.bind('<<ComboboxSelected>>', lambda event: owner.comboSelected(comboName))

class Browse_Button(Button):
    def __init__(self, master, owner, buttonName, pos):
        Button.__init__(self, master = master)

        r = pos[0]
        c = pos[1]
        self.configure(text = "Browse", command = lambda:owner.buttonHandler(buttonName))
        self.configure(state = "disabled")
        self.grid(row = r, column = c, padx = 5, pady = 5)


#-------------------------------------------------
# MAIN
#-------------------------------------------------

if __name__ == "__main__":

    root = Tk()
    app = Dup_GUI(root)
    app.master.title("RPi dc3dd Duplicator")

    no_of_dest_drives = 4
    app.duplicator = Duplicator(app.mainFrame, app, no_of_dest_drives)

    root.mainloop()
