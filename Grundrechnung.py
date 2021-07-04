#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import random
import time
import datetime
import logging
import logging.handlers as handlers
import os
import configparser
import win32gui
import sys
from config import *



class GRUNDRECHNUNG:
    def resetTime(self):
        self.start_time = time.time()

    def updateSettings(self):
        self.current_level = self.combobox_level.get()
        self.timeout = 1000 * config[self.current_level][self.current_operation]['timeout'] #[ms]
        self.x_min = config[self.current_level][self.current_operation]['x_min']
        self.x_max = config[self.current_level][self.current_operation]['x_max']
        self.y_min = config[self.current_level][self.current_operation]['y_min']
        self.y_max = config[self.current_level][self.current_operation]['y_max']
        self.zoom = config[self.current_level][self.current_operation]['zoom']
        if self.current_operation == 'division':
            self.division_with_rest = config[self.current_level][self.current_operation]['rest']
        self.checkOperandsValues()
        self.updateQuestion()
        # self.label_question.after_cancel(self.id)
        # self.id = self.label_question.after(self.timeout, self.evaluate)
        
    def __init__(self, master):
        self.arithmetic_operations = [('Additon', 'addition'),
                                      ('Subtraktion', 'subtraction'),
                                      ('Multiplikation', 'multiplication'),
                                      ('Division', 'division'),
                                     ]
        self.arithmetic_operators = {'addition' : '+',
                                     'subtraction' : '-',
                                     'multiplication' : '*',
                                     'division' : '/',
                                    }
        self.checkRunningProgram()
        # values form config file
        self.levels = [level for level in config.keys()]
        self.current_level = self.levels[0]
        self.current_operation = 'division'
        self.timeout = 1000 * config[self.current_level][self.current_operation]['timeout'] #[ms]
        self.x_min = config[self.current_level][self.current_operation]['x_min']
        self.x_max = config[self.current_level][self.current_operation]['x_max']
        self.y_min = config[self.current_level][self.current_operation]['y_min']
        self.y_max = config[self.current_level][self.current_operation]['y_max']
        self.zoom = config[self.current_level][self.current_operation]['zoom']
        self.division_with_rest = config[self.current_level][self.current_operation]['rest']
        self.icons = icons
        
        self.fram_row = 0
        self.correct = 0
        self.wrong = 0
        self.mark = ''
        self.operand_x = random.randint(self.x_min, self.x_max)
        self.operand_x = random.randint(self.x_min, self.x_max)
        self.operand_y = random.randint(self.y_min, self.y_max)
        self.operand_y = random.randint(self.y_min, self.y_max)
        self.id = None
        self.start_time = 0
        self.stop_time = 0
        self.arithmetic_operation = StringVar()
        self.arithmetic_operation.set(self.current_operation)
        self.operator = self.arithmetic_operators[self.current_operation]
        self.openLogFile()
        self.duration = 0
        
        # start gui
        self.master = master
        self.master.title(self.current_operation)
        self.master.iconbitmap(self.icons[self.current_operation])

        # basic arithmetic operation frame
        self.frame_aritmetic_operation = LabelFrame(self.master, text = "Wahl der Grundrechnung", padx = 0, pady = 0)
        self.frame_aritmetic_operation.grid(row = self.fram_row, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.fram_row += 1
        column = 0
        for text, value in self.arithmetic_operations:
            self.radiobutton_arithnetic_operation = Radiobutton(self.frame_aritmetic_operation, text=text, variable=self.arithmetic_operation, value=value, command=self.selectArithmeticOperation)
            self.radiobutton_arithnetic_operation.grid(row = 0, column = column)
            column += 1
        
        # level bar frame
        self.frame_level = LabelFrame(self.master, text = "Level", padx = 0, pady = 0)
        self.frame_level.grid(row = self.fram_row, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.fram_row += 1
        self.combobox_level = ttk.Combobox(self.frame_level, values = self.levels, width = 20 * self.zoom)
        self.combobox_level.current(0)
        self.combobox_level.grid(row = 0, column = 0, sticky = W+E)
        self.combobox_level.bind("<<ComboboxSelected>>", self.selectLevel)

        # initial status frame
        self.frame_status = LabelFrame(self.master, text="Status", padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.frame_status.grid(row = self.fram_row, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.fram_row += 1
        self.label_richtig = Label(self.frame_status, text = "Richtige Antworten: {}".format(self.correct))
        self.label_richtig.grid(row = 0, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.label_falsch = Label(self.frame_status, text = "Falsche Antworten: {}".format(self.wrong))
        self.label_falsch.grid(row = 1, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.label_note = Label(self.frame_status, text = "Note: {}".format(self.mark))
        self.label_note.grid(row = 2, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)

        # Question frame
        self.frame_question = LabelFrame(self.master, text = "Rechne", padx = 10 * self.zoom, pady = 10 * self.zoom)
        self.frame_question.grid(row = self.fram_row, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.fram_row += 1
        self.checkOperandsValues()
        self.label_question = Label(self.frame_question, text = "{0} {2} {1}".format(self.operand_x, self.operand_y, self.operator))
        self.label_question.grid(row = 0, column = 0)
        self.id = self.label_question.after(self.timeout, self.evaluate)
        self.resetTime()
        
        # Entry frame
        self.frame_entry = LabelFrame(self.master, text = "Eingabe", padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.frame_entry.grid(row = self.fram_row, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.fram_row += 1
        self.entry = Entry(self.frame_entry, width = 20 * self.zoom)
        self.entry.bind("<Return>", self.evaluate)
        self.entry.grid(row = 0, column = 0)
        self.entry.focus()
        
        if self.current_operation == 'division':
            self.entry.configure(width = 5 * self.zoom)
            self.label_rest = Label(self.frame_entry, text = "Rest", padx = 5 * self.zoom, pady = 2 * self.zoom)
            self.label_rest.grid(row = 0, column = 1, padx = 5 * self.zoom, pady = 2 * self.zoom)

            # Rest
            self.entry_rest = Entry(self.frame_entry, name="rest", width = 5 * self.zoom)
            self.entry_rest.bind("<Return>", self.evaluate)
            self.entry_rest.grid(row = 0, column = 2)

        # Progress bar frame
        self.frame_progressbar = LabelFrame(self.master, text = "Progress", padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.frame_progressbar.grid(row = self.fram_row, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.fram_row += 1
        # Progress bar widget 
        self.progressbar_progress = ttk.Progressbar(self.frame_progressbar, orient = HORIZONTAL, length = 300, mode = 'determinate')
        self.progressbar_progress.grid(row = self.fram_row, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.bar()

        # buttons frame
        self.frame_buttons = LabelFrame(self.master, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.frame_buttons.grid(row = self.fram_row, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.fram_row += 1
        self.button_9 = Button(self.frame_buttons, text = "9", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('9'))
        self.button_8 = Button(self.frame_buttons, text = "8", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('8'))
        self.button_7 = Button(self.frame_buttons, text = "7", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('7'))
        self.button_6 = Button(self.frame_buttons, text = "6", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('6'))
        self.button_5 = Button(self.frame_buttons, text = "5", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('5'))
        self.button_4 = Button(self.frame_buttons, text = "4", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('4'))
        self.button_3 = Button(self.frame_buttons, text = "3", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('3'))
        self.button_2 = Button(self.frame_buttons, text = "2", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('2'))
        self.button_1 = Button(self.frame_buttons, text = "1", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('1'))
        self.button_0 = Button(self.frame_buttons, text = "0", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('0'))
        self.button_C = Button(self.frame_buttons, text = "C", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('C'))
        self.button_E = Button(self.frame_buttons, text = "E", padx = 5 * self.zoom, pady = 2 * self.zoom, command = lambda: self.button_click('E'))
        self.button_9.grid(row = 0, column = 2)
        self.button_8.grid(row = 0, column = 1)
        self.button_7.grid(row = 0, column = 0)
        self.button_6.grid(row = 1, column = 2)
        self.button_5.grid(row = 1, column = 1)
        self.button_4.grid(row = 1, column = 0)
        self.button_3.grid(row = 2, column = 2)
        self.button_2.grid(row = 2, column = 1)
        self.button_1.grid(row = 2, column = 0)
        self.button_0.grid(row = 3, column = 1)
        self.button_C.grid(row = 3, column = 0)
        self.button_E.grid(row = 3, column = 2)

        # status bar frame
        self.frame_StatusBar = LabelFrame(self.master, text = "Statusleiste", padx = 0, pady = 0)
        self.frame_StatusBar.grid(row = self.fram_row, column = 0, padx = 5 * self.zoom, pady = 2 * self.zoom)
        self.fram_row += 1
        self.label_StatusBar = Label(self.frame_StatusBar, text = 'Start', width = 30 * self.zoom, relief = SUNKEN, bd = 0, anchor = W)
        self.label_StatusBar.grid(row = 0, column = 0, sticky = W+E)
        
    def selectLevel(self, event = None):
        self.selectArithmeticOperation()
        # self.updateSettings()
        
        self.entry.focus()
        self.bar()
        

        
    def evaluate(self, event = None, rest = None):
        # print(event)
        self.label_question.after_cancel(self.id)
        self.stop_time = time.time()
        self.duration += self.stop_time - self.start_time
        # only integers no floating point numbers
        result = int(eval("{}{}{}".format(self.operand_x, self.operator, self.operand_y)))
        if self.current_operation == 'division': calculated_rest = self.operand_x % self.operand_y
        # entry is not empty and E-button is clicked
        if isinstance(event, str):
            entry = event
        # (entry is empty) or (entry is not empty and return is clicked)    
        elif event is not None:
            entry = self.entry.get()
            self.entry.delete(0, END)
            if self.current_operation == 'division' and self.division_with_rest:
                rest = self.entry_rest.get().strip()
                self.entry_rest.delete(0, END)
            try:
                int(entry)
                if self.current_operation == 'division': int(entry)
            except:
                self.updateStatusBar("Fehler: nur Ziffern sind erlaubt!")
                return
        if (self.current_operation == 'division' and self.division_with_rest and rest is None) or event is None or rest=='' :
            self.wrong += 1
            self.logger.info("timeout: {:>3d} {} {:<3d} =               --> [{:5.2f} sec] ==> Die richtige Antwort wäre: {:>3d} {} {:<3d} = {:<3d} Rest {:1d}." \
            .format(self.operand_x, self.operator, self.operand_y, (self.stop_time - self.start_time), self.operand_x, self.operator, self.operand_y, result, calculated_rest))
            self.updateStatusBar("Zeitüberschreitung!! Die richtige Antwort wäre: {} {} {} = {} Rest {}.".format(self.operand_x, self.operator, self.operand_y, result, calculated_rest))
            self.entry.delete(0, END)
            if self.current_operation == 'division' and self.division_with_rest: self.entry_rest.delete(0, END)
        elif ((int(entry.strip())) == int(eval("{0} {2} {1}".format(self.operand_x, self.operand_y, self.operator))) ):
            if not (self.current_operation == 'division' and self.division_with_rest) or (self.current_operation == 'division' and int(rest) == calculated_rest):
                self.correct += 1;
                self.updateStatusBar("Deine Antwort ist richtig.")
                self.logger.info("richtig: {:>3d} {} {:<3d} = {:13s} --> [{:5.2f} sec]".format(self.operand_x, self.operator, self.operand_y, entry.strip(), (self.stop_time - self.start_time)))
        else:
            self.wrong += 1
            if not (self.current_operation == 'division' and self.division_with_rest):
                self.updateStatusBar("Deine Antwort ist leider falsch. Die richtige Antwort wäre: {:>3d} {} {:<3d} = {:3d}.".format(self.operand_x, self.operator, self.operand_y, int(result)))
                self.logger.error("falsch : {:>3d} {} {:<3d} = {:13s} --> [{:5.2f} sec] ==> Die richtige Antwort wäre: {:>3d} {} {:<3d} = {:3d}." \
                .format(self.operand_x, self.operator, self.operand_y, entry.strip(), (self.stop_time - self.start_time), self.operand_x, self.operator, self.operand_y, result))
            else:
                self.updateStatusBar("Deine Antwort ist leider falsch. Die richtige Antwort wäre: {} {} {} = {} Rest {}.".format(self.operand_x, self.operator, self.operand_y, result, calculated_rest))
                self.logger.error("falsch : {:>3d} {} {:<3d} = {:6s} Rest {:1} --> [{:5.2f} sec] ==> Die richtige Antwort wäre: {:>3d} {} {:<3d} = {:<3d} Rest {:1d}." \
                .format(self.operand_x, self.operator, self.operand_y, entry.strip(), rest.strip(), (self.stop_time - self.start_time), self.operand_x, self.operator, self.operand_y, result, calculated_rest))
        prozent = 100 * self.correct/(self.correct + self.wrong)
        if 94 < prozent <= 100:
            self.mark = 1
        elif 86 < prozent <= 94:
            self.mark = 2
        elif 70 < prozent <= 86:
            self.mark = 3
        elif 60 < prozent <= 70:
            self.mark = 4
        elif 50 < prozent <= 60:
            self.mark = 5
        elif prozent <= 50:
            self.mark = 6
        self.update_status()
        self.entry.focus()
        
    def button_click(self, char):  
        # print(str(self.frame_entry.focus_get()))
        rest = None
        if char in "0123456789":
            if str(self.frame_entry.focus_get()) == ".!labelframe5.!entry":
                # print(char)
                entry = self.entry.get()
                self.entry.delete(0, END)
                self.entry.insert(0, entry + char)
            elif str(self.frame_entry.focus_get()) == ".!labelframe5.rest":
                rest = self.entry_rest.get()
                self.entry_rest.delete(0, END)
                self.entry_rest.insert(0, rest + char)
            
        elif char == 'C':
            if str(self.frame_entry.focus_get()) == ".!labelframe5.!entry":
                self.entry.delete(0, END)
            elif str(self.frame_entry.focus_get()) == ".!labelframe5.rest":
                self.entry_rest.delete(0, END)
            
        elif char == 'E':
            entry = self.entry.get()
            self.entry.delete(0, END)
            if self.current_operation == 'division' and self.division_with_rest:
                rest = self.entry_rest.get()
                self.entry_rest.delete(0, END)
            self.entry.focus()
            if entry:
                self.evaluate(entry, rest)
        
    def selectArithmeticOperation(self):
        self.current_operation = self.arithmetic_operation.get()
        self.master.title(self.current_operation)
        self.master.iconbitmap(self.icons[self.current_operation])
        self.operator = self.arithmetic_operators[self.current_operation]
        self.updateSettings()
        if self.current_operation == 'division' and self.division_with_rest:
            self.entry.configure(width = 5 * self.zoom)
            self.label_rest = Label(self.frame_entry, text = "Rest", padx = 5 * self.zoom, pady = 2 * self.zoom)
            self.label_rest.grid(row = 0, column = 1, padx = 5 * self.zoom, pady = 2 * self.zoom)
            # Rest
            self.entry_rest = Entry(self.frame_entry, name="rest", width = 5 * self.zoom)
            self.entry_rest.bind("<Return>", self.evaluate)
            self.entry_rest.grid(row = 0, column = 2)
        else:
            self.label_rest.destroy()
            self.entry_rest.destroy()
            self.entry.configure(width = 20 * self.zoom)
            
        self.updateQuestion()
        
    def bar(self):
        self.progressbar_progress.stop()
        self.progressbar_progress['value'] = 0
        self.progressbar_progress.start(int(10 * self.timeout / 1000))
  
    def checkRunningProgram(self):
        for window in self.arithmetic_operators.keys():
            hwnd = win32gui.FindWindow(None, window)
            if hwnd:
                win32gui.ShowWindow(hwnd, 5)
                win32gui.SetForegroundWindow(hwnd)
                messagebox.showerror("Error", "Applikation läuft bereits")
                sys.exit(0)
                
    def openLogFile(self):
        self.logger = logging.getLogger('my_app')
        self.logger.setLevel(logging.INFO)
        self.logHandler = handlers.RotatingFileHandler('Grundrechnung.log', maxBytes=10000, backupCount=2)
        self.logHandler.setLevel(logging.INFO)
        self.logger.addHandler(self.logHandler)
        self.logger.info('-' * 10 + ' Neue Übung: ' + str(datetime.datetime.now()).split('.')[0] + ' ' + '-' * 10)
        

        
    def checkOperandsValues(self):
        if self.current_operation in ['subtraction', 'division'] and self.operand_x < self.operand_y:
            self.operand_x , self.operand_y = self.operand_y , self.operand_x
            
            if self.current_operation == 'division':
                self.operand_x = self.operand_x % ((self.operand_y * 10) - 1)
                if not self.division_with_rest:
                    self.operand_x = self.operand_x - (self.operand_x % self.operand_y)
    
    def updateStatusBar(self, message):
        self.label_StatusBar.config(text = message)

    def update_status(self):
        self.label_richtig.config(text = "Richtige Antworten: {}".format(self.correct))
        self.label_falsch.config(text = "Falsche Antworten: {}".format(self.wrong))
        self.label_note.config(text = "Note: {}".format(self.mark))
        self.updateQuestion()
        
    def updateQuestion(self):
        self.getRandomOperands()
        self.label_question.config(text = "{0} {2} {1}".format(self.operand_x, self.operand_y, self.operator))
        self.label_question.after_cancel(self.id)
        self.id = self.label_question.after(self.timeout, self.evaluate)
        self.resetTime()
        self.bar()
 
    def getRandomOperands(self):
        self.operand_x = random.randint(self.x_min, self.x_max)
        self.operand_x = random.randint(self.x_min, self.x_max)
        self.operand_y = random.randint(self.y_min, self.y_max)
        self.operand_y = random.randint(self.y_min, self.y_max)
        self.checkOperandsValues()
        
    def displayResults(self):
        self.logger.info('\n' + 'Übung beendet : ' + str(datetime.datetime.now()).split('.')[0])
        self.logger.info("Richtige Antworten: {}".format(self.correct))
        self.logger.info("Falsche Antworten: {}".format(self.wrong))
        self.logger.info("NOTE: {}".format(self.mark))
        self.logger.info("Anzahl der Fragen: {}".format(self.correct + self.wrong))
        self.logger.info("Dauer der Übung: {}".format(time.strftime('%Hh:%Mm:%Ss', time.gmtime(self.duration))))
        if ((self.correct + self.wrong)!=0):
            self.logger.info("Leistung: %.2f Sekunden pro Frage"%((self.duration) / (self.correct + self.wrong)))
        else:
            self.logger.info("Leistung: Es wurden keine Fragen beantwortet.")

def main():
    root = Tk()
    app = GRUNDRECHNUNG(root)
    
    app.openLogFile
    root.mainloop()
    app.displayResults()
    

if __name__ == '__main__':
    main()