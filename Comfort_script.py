import serial
import time
import argparse
import os
import pygame
import tkinter as tk
from tkinter import font
from plyer import notification

SERIAL_PORT = '/dev/ttyUSB0' # Please change this to the port you guys are using
BAUD_RATE = 9600 #I am using 9600 in the ESP32 reading

parser = argparse.ArgumentParser(description = "Set necessary limits for comfort at you desk") # argument parsing part
parser.add_argument("-th","--tempmax",default=30.0, type=float, help='Set highest acceptable temperature')
parser.add_argument("-tl","--templow",default=19.0, type=float, help='Set lowest acceptable temperature')
parser.add_argument("-hh","--humiditymax",default=70.0, type=float, help='Set highest acceptable humidity')
parser.add_argument("-hl","--humiditylow",default=30.0, type=float, help='Set lowest acceptable humidity')
parser.add_argument("-s","--snooze",default = 60, type=int, help="The amount of time between each notification")


args = parser.parse_args() #assigning variables
TEMP_HIGH = args.tempmax
TEMP_LOW = args.templow
HUM_HIGH = args.humiditymax
HUM_LOW = args.humiditylow
SNOOZE_TIME = args.snooze

last_notification_time=0

def send_notification(title,message): # function for sending notificaitions
    global last_notification_time

    sound_file = "./Sounds/mixkit-sci-fi-click-900.wav" # this is the wav file i downloaded
    try:
        if os.path.exists(sound_file):
            pygame.mixer.music.load(sound_file) # Audio worked!!
            pygame.mixer.music.play()
        else:
            print("File not found")
    except Exception as e:
        print(f"Error occured {e}")
    

    notification.notify(title = title, message = message, app_name = 'Desk comfort application',timeout = 10)
    last_notification_time = time.time()
    print(f"Snoozing notifications for {SNOOZE_TIME/60 :.2f} minutes")

def main():
    root = tk.Tk()
    root.title("Desk Comfort Detector")
    root.geometry("400x200")
    root.resizable(False,False)
    root.configure(bg='#2E2E2E')
    #Assigning the special tkinter variables 
    temp_var = tk.StringVar(value="-- C")
    humidity_var = tk.StringVar(value="--%")
    status_var = tk.StringVar(value = "Connecting....")

    label_font = font.Font(family="Helvetica", size=16)
    value_font = font.Font(family="Helvetica", size=36, weight="bold")
    status_font = font.Font(family="Helvetica", size=10)

    #Setting up temp
    tk.Label(root, text="Temperature:", font = label_font,fg='white',bg='#2E2E2E').grid(row=0,column=0,padx=20,pady=10, sticky="w")
    temp_value_label = tk.Label(root,textvariable=temp_var, font = value_font,fg='#00BFFF',bg='#2E2E2E')
    temp_value_label.grid(row=0,column=1,padx=20,pady=10,sticky="e")
    #setting up humidity
    tk.Label(root, text='Humidity: ', font = label_font,fg='white',bg='#2E2E2E').grid(row=1,column=0,padx=20,pady=10,sticky="w")
    humidity_value_label = tk.Label(root, textvariable=humidity_var, font= value_font,fg='#00BFFF',bg='#2E2E2E')
    humidity_value_label.grid(row=1,column=1,padx=20,pady=10,sticky="e")
    #Setting up status
    status_value_label = tk.Label(root,textvariable=status_var, font=status_font,fg='grey',bg='#2E2E2E')
    status_value_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
    #Arranging in grid
    root.grid_columnconfigure(1, weight=1)

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) # for safe communication
        status_var.set(f"Successful Connection to {SERIAL_PORT}") #Set status
    except serial.SerialException as e:
        status_var.set(f"Error: Could not open serial port {SERIAL_PORT}") # set status, temp, humidity
        temp_var.set("Error")
        humidity_var.set("Error")
        root.mainloop()
        return
    
    def update_readings():
        try:
            line = ser.readline().decode('utf-8').strip() # reading the line
            if line and "T" in line and "H" in line:
                print(f"Recieved data: {line}") # Logging
                parts = line.split(',')
                temp = float(parts[0].split(':')[1])
                humidity = float(parts[1].split(':')[1])

                #Updating GUI
                temp_var.set(f"{temp:.2f} C")
                humidity_var.set(f"{humidity:.2f} %")

                issues = [] # to input the problems at the moment if any

                if temp > TEMP_HIGH:
                    issues.append(f"It's getting hot ({temp: .2f} C)")
                    temp_value_label.config(fg="#BE0707")
                elif temp < TEMP_LOW:
                    issues.append(f"It's a bit chilly ({temp:.2f}) C")
                    temp_value_label.config(fg="#BE0707")
                else:
                    temp_value_label.config(fg='#00BFFF')

                if humidity > HUM_HIGH:
                    issues.append(f"It's feeling stuffy ({humidity:.2f}) %")
                    humidity_value_label.config(fg="#BE0707")
                elif humidity < HUM_LOW:
                    issues.append(f"It's a bit dry here ({humidity:.2f}) %")
                    humidity_value_label.config(fg="#BE0707")
                else:
                    humidity_value_label.config(fg='#00BFFF')

                if issues: 
                    status_var.set("Status: Uncomfortable")
                    if(time.time() - last_notification_time > SNOOZE_TIME): # To not spam notifications all the time
                        message = " and ".join(issues).capitalize() # I got to know this is good practice compared to if else
                        final_message = f"Heads up {message}"
                        send_notification("Desk comfort Alert!", final_message)
                else:
                    status_var.set("Status: OK")
                    
        except (IndexError, ValueError):
            status_var.set(f"Warning: Received malformed Data: {line}")
            pass
        except serial.SerialException:
            status_var.set(f"Fail: Device disconnected. Exiting.")
            root.after(2000,root.destroy)
            return
        root.after(1000, update_readings)
    
    pygame.mixer.init()
    update_readings()
    root.mainloop()

    if ser.is_open:
        ser.close()
    print('Application Finished!')

if __name__ == "__main__":
    main()

