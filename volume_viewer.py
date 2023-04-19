#!/usr/bin/env python3

import sys
import tkinter as tk
from tkinter import filedialog

import numpy as np
import PIL.Image
import PIL.ImageTk
import pydicom



def normalize(data: np.ndarray) -> np.ndarray:
    data = data - np.min(data)
    data = data / np.max(data)
    data = data * 255
    data = data.astype(np.uint8)
    return data


class App(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        # self.master.title('Image Viewer')

        self.num_page = 0
        self.total_pages = data.shape[0] - 1
        self.num_page_tv = tk.StringVar()

        fram = tk.Frame(self)
        # tk.Button(fram, text="Open File", command=self.open).pack(side=tk.LEFT)
        tk.Button(fram, text="Prev", command=self.seek_prev).pack(side=tk.LEFT)
        tk.Button(fram, text="Next", command=self.seek_next).pack(side=tk.LEFT)
        tk.Label(fram, textvariable=self.num_page_tv).pack(side=tk.LEFT)
        tk.Label(fram, text="Shape: "+str(data.shape)).pack(side=tk.RIGHT)
        fram.pack(side=tk.TOP, fill=tk.BOTH)

        self.la = tk.Label(self)
        self.la.pack()

        self.img = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(data[0]))
        self.chg_image()
        self.num_page = 0
        self.num_page_tv.set(str(self.num_page)+'/'+str(self.total_pages))

        self.pack()


    def chg_image(self):
        self.img = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(data[self.num_page]))
        self.la.config(image=self.img, bg="#000000",
            width=self.img.width(), height=self.img.height())

    def open(self):
        filename = filedialog.askopenfilename()
        if filename != "":
            self.im = PIL.Image.open(filename)
        self.chg_image()
        self.num_page = 0
        self.num_page_tv.set(str(self.num_page)+'/'+str(self.total_pages))

    def seek_prev(self):
        if self.num_page <= 0:
            return
        self.num_page=self.num_page-1
        # self.im.seek(self.num_page)
        self.chg_image()
        self.num_page_tv.set(str(self.num_page)+'/'+str(self.total_pages))

    def seek_next(self):
        if self.num_page >= self.total_pages:
            return
        self.num_page = self.num_page+1
        self.chg_image()
        self.num_page_tv.set(str(self.num_page)+'/'+str(self.total_pages))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: 3d_viewer.py <file_name>")
        exit(1)

    file_name = sys.argv[1]

    if file_name.endswith(".npy"):
        data = np.load(file_name)  # type: np.ndarray
    elif file_name.endswith(".dcm"):
        data_dcm = pydicom.dcmread(file_name)
        data_dcm.SamplesPerPixel = 1
        data = data_dcm.pixel_array
    elif (
        file_name.endswith(".png")
        or file_name.endswith(".jpg")
        or file_name.endswith(".jpeg")
    ):
        data = np.array(PIL.Image.open(file_name))
    else:
        raise ValueError("File type not supported")

    if len(data.shape) == 2:
        data = np.expand_dims(data, axis=0)

    data = normalize(data)

    main = tk.Tk()

    app = App()

    main.bind("<Right>", lambda _e: app.seek_next())
    main.bind("<Left>", lambda _e: app.seek_prev())
    # Vim-like keybindings
    main.bind("l", lambda _e: app.seek_next())
    main.bind("h", lambda _e: app.seek_prev())

    app.mainloop()
