#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import csv
import serial
from datetime import datetime
import time



class SReader:
    def __init__(self, master=None):
        # build ui
        self.Sensor_reader = tk.Tk() if master is None else tk.Toplevel(master)
        self.Sensor_reader.configure(height=200, width=200)
        self.Sensor_reader.geometry("800x560")
        self.Sensor_reader.resizable(False, False)
        self.Sensor_reader.title("Sensor_reader")
        self.admin_label = ttk.Label(self.Sensor_reader)
        self.admin_label.configure(text='ผู้ดูแลการทดสอบ')
        self.admin_label.grid(column=0, padx=20, pady=10, row=1, sticky="w")
        self.admin_entry = ttk.Entry(self.Sensor_reader)
        self.admin_name_string = tk.StringVar()
        self.admin_entry.configure(
            textvariable=self.admin_name_string, width=60)
        self.admin_entry.grid(column=1, columnspan=2, row=1, sticky="w")
        self.patient_name = ttk.Label(self.Sensor_reader)
        self.patient_name.configure(text='ผู้ทดสอบ')
        self.patient_name.grid(column=0, padx=20, row=2, sticky="w")
        self.patient_entry = ttk.Entry(self.Sensor_reader)
        self.patient_name_string = tk.StringVar()
        self.patient_entry.configure(
            textvariable=self.patient_name_string, width=60)
        self.patient_entry.grid(column=1, columnspan=2, row=2, sticky="w")
        self.display_text = tk.Text(self.Sensor_reader)
        self.display_text.configure(height=20, width=30)
        self.display_text.grid(
            column=0,
            columnspan=5,
            padx="20 0",
            pady=20,
            row=5,
            sticky="ew")
        self.start_button = ttk.Button(self.Sensor_reader)
        self.start_button.configure(state="disabled", text='เริ่ม', width=20)
        self.start_button.grid(
            column=3,
            ipady=10,
            padx=20,
            row=2,
            rowspan=2,
            sticky="n")
        self.start_button.configure(command=self.start_button_pressed)
        self.stop_button = ttk.Button(self.Sensor_reader)
        self.stop_button.configure(
            state="disabled", text='หยุดการทอสอบ', width=20)
        self.stop_button.grid(column=4, ipady=10, row=2, rowspan=2, sticky="n")
        self.stop_button.configure(command=self.stop_button_pressed)
        self.connect_button = ttk.Button(self.Sensor_reader)
        self.connect_button.configure(
            default="normal",
            state="disabled",
            text='เชื่อมต่อบอร์ด',
            width=20)
        self.connect_button.grid(
            column=4,
            ipady=10,
            pady=20,
            row=0,
            rowspan=2,
            sticky="n")
        self.connect_button.configure(command=self.connect_uc)
        self.openfile_button = ttk.Button(self.Sensor_reader)
        self.openfile_button.configure(text='เลือกไฟล์บันทึก', width=20)
        self.openfile_button.grid(
            column=3,
            ipady=10,
            pady=20,
            row=0,
            rowspan=2,
            sticky="n")
        self.openfile_button.configure(command=self.openfile_location)
        self.counter_entry = ttk.Entry(self.Sensor_reader)
        self.pulse_counter_string = tk.StringVar()
        self.counter_entry.configure(
            font="TkDefaultFont",
            justify="right",
            state="readonly",
            textvariable=self.pulse_counter_string)
        self.counter_entry.grid(column=1, pady="10 0", row=3, sticky="nsw")
        label1 = ttk.Label(self.Sensor_reader)
        label1.configure(text='พัลส์ที่นับได้')
        label1.grid(column=0, padx=20, pady=10, row=3, sticky="nw")
        self.logfile_label = ttk.Label(self.Sensor_reader)
        self.logfile_label.configure(text='ไฟล์บันทึกผล')
        self.logfile_label.grid(
            column=0,
            padx=20,
            pady="20 0",
            row=0,
            sticky="w")
        self.logfile_entry = ttk.Entry(self.Sensor_reader)
        self.logfile_name_string = tk.StringVar()
        self.logfile_entry.configure(
            justify="left",
            state="readonly",
            textvariable=self.logfile_name_string,
            width=60)
        self.logfile_entry.grid(column=1, pady="20 0", row=0, sticky="w")
        self.Exit_Button = ttk.Button(self.Sensor_reader)
        self.Exit_Button.configure(text='ปิดโปรแกรม', width=20)
        self.Exit_Button.grid(column=4, ipady=10, pady="10 0", row=4)
        self.Exit_Button.configure(command=self.exit_button_pressed)

        # Main widget
        self.mainwindow = self.Sensor_reader

    def run(self):
        # initial serial port 
        self.serial_obj = serial.Serial()
        self.serial_obj.baudrate = 115200
        self.serial_obj.port = 'COM20'

        self.run_mainloop = False
        self.mainwindow.mainloop()

    def start_button_pressed(self):
        local_time = time.localtime()
        current_date = time.strftime("%d %b %Y", local_time)
        current_time = time.strftime("%H:%M:%S", local_time)

        self.start_exp_time = time.time()
        
        # add data to text
        addmin_name = self.admin_name_string.get() 
        if addmin_name == "":
            addmin_name = "--"

        patient_name = self.patient_name_string.get()
        if patient_name == "":
            patient_name = "--"

        textmessage = current_date + "\t" + current_time    + "\t" + addmin_name + "\t" + patient_name + "\t"
        self.display_text.insert(tk.END,textmessage)

        # disable start button
        self.start_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.NORMAL

        self.run_mainloop = True
        self.pulse_counter = 0
        self.serial_obj.flush()
        self.main_machine()


    def stop_button_pressed(self):
        self.run_mainloop = False
        self.stop_button['state'] = tk.DISABLED
        self.start_button['state'] = tk.NORMAL

    def connect_uc(self):
        if not self.serial_obj.is_open:
            self.serial_obj.open()
            if self.serial_obj.is_open:
                # enable and disable buttons
                self.connect_button['state'] = tk.DISABLED
                self.start_button['state'] = tk.NORMAL

    def openfile_location(self):
        filetypes = ( ('excel files', '*.csv'), )
        filename = filedialog.asksaveasfilename(  title='Save log file location',  initialdir='/',   filetypes=filetypes)
        if filename != None:
            filename_path = filename.split(".")
            save_file = filename_path[0] + ".csv"
            self.logfile_name_string.set(save_file)

            #======= enable and disable buttons
            self.openfile_button['state'] = tk.DISABLED
            self.connect_button['state'] = tk.NORMAL

    def exit_button_pressed(self):
        self.mainwindow.destroy()


    def main_machine(self):
        if time.time() - self.start_exp_time >= 120 or self.run_mainloop == False:
            textmessage = time.strftime("%H:%M:%S", time.localtime()) + "\t" + self.pulse_counter_string.get() 
            self.display_text.insert(tk.END,textmessage)
            log_message = self.display_text.get("end-1c linestart", "end-1c lineend").strip().split("\t")
            self.display_text.insert(tk.END,"\n")
            file_obj = open(self.logfile_name_string.get(), 'a+', newline='')
            file_writer = csv.writer(file_obj)
            file_writer.writerow([log_message[0],log_message[2],log_message[3],log_message[1],log_message[4],log_message[5]])
            file_obj.close()
            self.start_button['state'] = tk.NORMAL
            self.stop_button['state'] = tk.DISABLED
            self.run_mainloop = False

        # ============= check data from serial =======
        if self.serial_obj.in_waiting:
            data_in = self.serial_obj.readline().rstrip()
            if data_in == b'1':
                self.pulse_counter = self.pulse_counter + 1
                self.pulse_counter_string.set(str(self.pulse_counter))
        # ============== loop main machine ===========
        if self.run_mainloop:
           self.mainwindow.after(100,self.main_machine)


if __name__ == "__main__":
    app = SReader()
    app.run()
