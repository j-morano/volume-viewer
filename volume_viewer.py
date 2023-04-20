#!/usr/bin/env python3

from pathlib import Path
import sys
import tkinter as tk

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

        self.data_index = 0
        self.data = data_list[self.data_index]
        self.data_index_tv = tk.StringVar()
        self.total_data = len(data_list) - 1

        self.num_page = 0
        self.total_pages = data.shape[0] - 1
        self.num_page_tv = tk.StringVar()

        fram = tk.Frame(self)
        tk.Button(fram, text="Prev image", command=self.prev_image).pack(side=tk.LEFT)
        tk.Button(fram, text="Next image", command=self.next_image).pack(side=tk.LEFT)
        tk.Label(fram, textvariable=self.data_index_tv).pack(side=tk.LEFT)
        tk.Button(fram, text="Prev slice", command=self.seek_prev).pack(side=tk.LEFT)
        tk.Button(fram, text="Next slice", command=self.seek_next).pack(side=tk.LEFT)
        tk.Label(fram, textvariable=self.num_page_tv).pack(side=tk.LEFT)
        tk.Label(fram, text="Shape: "+str(self.data.shape)).pack(side=tk.RIGHT)
        fram.pack(side=tk.TOP, fill=tk.BOTH)

        self.la = tk.Label(self)
        self.la.pack()

        tk.Label(self, text=stem).pack()

        self.img = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(self.data[0]))
        self.chg_image()
        self.num_page = 0
        self.num_page_tv.set(str(self.num_page)+'/'+str(self.total_pages))
        self.data_index_tv.set(str(self.data_index)+'/'+str(self.total_data))

        self.pack()


    def chg_image(self):
        self.img = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(self.data[self.num_page]))
        self.la.config(
            image=self.img,
            bg="#000000",
            width=self.img.width(),
            height=self.img.height()
        )

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

    def prev_image(self):
        if self.data_index <= 0:
            return
        self.data_index = self.data_index-1
        self.data = data_list[self.data_index]
        self.data_index_tv.set(str(self.data_index)+'/'+str(self.total_data))
        self.total_pages = self.data.shape[0] - 1
        self.num_page = 0
        self.chg_image()
        self.num_page_tv.set(str(self.num_page)+'/'+str(self.total_pages))

    def next_image(self):
        if self.data_index >= len(data_list)-1:
            return
        self.data_index = self.data_index+1
        self.data = data_list[self.data_index]
        self.data_index_tv.set(str(self.data_index)+'/'+str(self.total_data))
        self.total_pages = self.data.shape[0] - 1
        self.num_page = 0
        self.chg_image()
        self.num_page_tv.set(str(self.num_page)+'/'+str(self.total_pages))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: 3d_viewer.py <file_names>")
        exit(1)

    file_names = sys.argv[1:]

    data_list = []
    for file_name in file_names:
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

        stem = Path(file_name).stem

        if len(data.shape) == 2:
            data = np.expand_dims(data, axis=0)

        data = normalize(data)
        data_list.append(data)

    main = tk.Tk()

    app = App()

    main.bind("<Down>", lambda _e: app.seek_next())
    main.bind("<Up>", lambda _e: app.seek_prev())
    main.bind("<Left>", lambda _e: app.prev_image())
    main.bind("<Right>", lambda _e: app.next_image())
    # Vim-like keybindings
    main.bind("j", lambda _e: app.seek_next())
    main.bind("k", lambda _e: app.seek_prev())
    main.bind("h", lambda _e: app.prev_image())
    main.bind("l", lambda _e: app.next_image())

    app.mainloop()
