from tkinter import *
import tkinter as tk
from tkinter import ttk
from scrap_vdab import vdab
from scrap_linkedin import scrap
import threading

import os
import sys
os.path.dirname(__file__)
sys.path.append('.\scrappy')
sys.path

# make window responsive while running with multithreding: https://www.quora.com/How-do-you-fix-a-Tkinter-Python-GUI-app-from-not-responding-using-threading
    
class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.master.title("scrappy")
        self.master.geometry('700x400')

        a = Label(self.master, text="Welcome to job search", width=30, justify="left") 
        a.grid(column=0, row=0)
    
        button_exit = Button(self.master,text='Quit app', command= self._quit).grid(column=1, row=0)
        clear_button = Button(self.master,text='Clear selection', command= self._clear).grid(column=2, row=0)

        ac = Label(self.master, text="Select a jobsite", width=30, justify="left") 
        ac.grid(column=0, row=1)

        # dropdown menu
        self.tkvar = StringVar(self.master)
        self.tkvar.set("Select an option")

        # Dictionary with options
        choices = {'vdab','linkedin'}

        popupMenu = OptionMenu(self.master, self.tkvar, *choices, command=self.show_options)
        popupMenu.grid(column=1, row=1)

    def show_options(self, event):
        if self.tkvar.get() == 'vdab':
            
            try: 
                print(self.l1) # self.url.get()
                self._clear()

            except AttributeError:
                pass

            print('choice:', self.tkvar.get())

            self.l1 = self.print_message("Copy paste the job search link: ", 0, 4)
            self.l2 = self.print_message("Specify path to save: ", 0, 5)
            self.l3 = self.print_message("OpenAI API: ", 0, 6)

            self.search_url = tk.Entry(width=30)
            self.search_url.grid(column=1, row=4)
            self.url = tk.StringVar()
            self.search_url["textvariable"] = self.url
            
            self.path = tk.Entry(width=30)
            self.path.grid(column=1, row=5)
            self.path_to_save = tk.StringVar()
            self.path["textvariable"] = self.path_to_save

            self.api_key = tk.Entry(width=30)
            self.api_key.grid(column=1, row=6)
            self.api = tk.StringVar()
            self.api_key["textvariable"] = self.api

                    # button 1 widget with red color text inside
            Button(self.master, text = "Go" , fg = "black", command=threading.Thread(target=self.start_task_vdab).start).grid(column=1, row=7)

        if self.tkvar.get() == 'linkedin':
            
            try: 
                print(self.l1) # self.url.get()
                self._clear()

            except AttributeError:
                pass

            print('choice:', self.tkvar.get())

            self.l1 = self.print_message("Copy paste the job search link: ", 0, 2)
            self.l2 = self.print_message("Specify path to save: ", 0, 3)
            self.l5 = self.print_message("OpenAI API: ", 0, 4)
            self.l3 = self.print_message("LinkedIn username: ", 0, 5)
            self.l4 = self.print_message("LinkedIn password: ", 0, 6)

            self.search_url = tk.Entry(width=30)
            self.search_url.grid(column=1, row=2)
            self.url = tk.StringVar()
            self.search_url["textvariable"] = self.url
            
            self.path = tk.Entry(width=30)
            self.path.grid(column=1, row=3)
            self.path_to_save = tk.StringVar()
            self.path["textvariable"] = self.path_to_save

            self.api_key = tk.Entry(width=30)
            self.api_key.grid(column=1, row=4)
            self.api = tk.StringVar()
            self.api_key["textvariable"] = self.api

            self.user = tk.Entry(width=30)
            self.user.grid(column=1, row=5)
            self.username = tk.StringVar()
            self.user["textvariable"] = self.username

            self.passw = tk.Entry(width=30)
            self.passw.grid(column=1, row=6)
            self.password = tk.StringVar()
            self.passw["textvariable"] = self.password

            Button(self.master, text = "Go" , fg = "black", command=self.start_task_linkedin).grid(column=1, row=7)

    def clicked_vdab(self):
        self.m1 = self.print_message("Started to search VDAB. Ignore the pop-up windows. This should take at least 20 minutes", 1, 9)
        search = vdab(self.search_url.get(), self.api.get(), path= self.path_to_save.get())
        alljobs = search.get_jobs_vdab()
        alljobs_list = search.unlist_get_href(alljobs)
        self.m2 = self.print_message(f"{len(alljobs_list)} jobs found. Starting to query the descriptions", 1, 10)
        search.get_job_description(alljobs_list)
        self.m3 = self.print_message("Ready. Take a look at the excel sheet in the location you specified.", 1, 11)

    def clicked_linkedin(self):
        
        self.m1 = self.print_message("Signing in. Ignore the windows that pop up. Do not close them.", 1, 8)
        search = scrap(self.url.get(), self.username.get(), self.password.get(), self.api.get(), path = self.path_to_save.get())
        
        self.m2 = self.print_message("Collecting all available jobs", 1, 9)
        alljobs = search.get_all_job_links()
        
        self.m3 = self.print_message(f"{len(alljobs)} jobs collected. Starting to load and process descriptions. This will last long if there are many jobs.", 1, 10)
        search.get_job_description(alljobs)

        self.m4 = self.print_message("Ready. Take a look at the excel sheet in the location you specified.", 1, 11)

    def print_message(self, m, c, r):
        '''
        m: message
        c: column
        r: row
        '''
        text_var = tk.StringVar()
        text_var.set(m)
        label = tk.Label(self.master, textvariable=text_var, width=30, justify="left", wraplength=200)
        label.grid(column=c, row=r)
        return label

    def start_task_linkedin(self): 
        # Start the long-running task in a new thread 
        thread = threading.Thread(target=self.clicked_linkedin) 
        thread.start()

    def start_task_vdab(self): 
        # Start the long-running task in a new thread 
        thread = threading.Thread(target=self.clicked_vdab) 
        thread.start()

    def _clear(self):
        try: 
            self.l1.destroy()
            self.l2.destroy()
            self.l3.destroy()
            self.search_url.destroy()
            self.path.destroy()
            self.api_key.destroy()
            self.user.destroy()
            self.passw.destroy()
            self.l4.destroy()
            self.l5.destroy()
            self.m1.destroy()
            self.m2.destroy()
            self.m3.destroy()
            self.m4.destroy()

        except AttributeError:
            pass
    
    def _quit(self):
        self.master.quit()     
        self.master.destroy()

# def main():
root = tk.Tk()
myapp = App(root)
myapp.mainloop()


