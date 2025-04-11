#!/usr/bin/env python3

from pathlib import Path
import sys
import tkinter as tk
import pickle

import numpy as np
import PIL.Image
import PIL.ImageTk
import pydicom
import nibabel as nib



def normalize(data: np.ndarray) -> np.ndarray:
    # Convert to float
    data = data.astype(np.float32)
    # Put NaNs to 0
    data[np.isnan(data)] = 0
    data = data - np.min(data)
    data = data / (np.max(data) + 1e-6)
    data = data * 255
    data = data.astype(np.uint8)
    return data


class App(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        # self.master.title('Image Viewer')

        self.data_index = 0
        self.data_index_tv = tk.StringVar()
        self.data = data_list[self.data_index]['data']
        self.total_data = len(data_list) - 1

        self.shape_tv = tk.StringVar()
        self.shape_tv.set(self.get_shape())

        self.data_range_tv = tk.StringVar()
        self.data_range_tv.set('Range: ' + str(data_list[self.data_index]['data_range']))

        self.filename_tv = tk.StringVar()

        self.zoom_levels = [1.0, 2.0]
        self.zoom_level = 1.0
        self.zoom_level_tv = tk.StringVar()

        self.num_page = 0
        self.num_page_tv = tk.StringVar()
        self.total_pages = data.shape[0] - 1

        self.num_digits = len(str(self.total_pages))
        self.num_page_tv.set(str(self.num_page).zfill(self.num_digits)+'/'+str(self.total_pages))
        self.data_index_tv.set(str(self.data_index)+'/'+str(self.total_data))
        self.zoom_level_tv.set(str(self.zoom_level))

        self.projection_state = False

        fram = tk.Frame(self)
        tk.Button(fram, text="Prev image", command=self.prev_image).pack(side=tk.LEFT)
        tk.Button(fram, text="Next image", command=self.next_image).pack(side=tk.LEFT)
        tk.Label(fram, textvariable=self.data_index_tv).pack(side=tk.LEFT)
        tk.Button(fram, text="Prev slice", command=self.seek_prev).pack(side=tk.LEFT, padx=(16, 0))
        tk.Button(fram, text="Next slice", command=self.seek_next).pack(side=tk.LEFT)
        tk.Label(fram, textvariable=self.num_page_tv).pack(side=tk.LEFT)
        tk.Label(fram, textvariable=self.shape_tv).pack(side=tk.RIGHT, padx=(16, 0))
        fram.pack(side=tk.TOP, fill=tk.BOTH)

        fram = tk.Frame(self)
        tk.Button(fram, text="Projection", command=self.projection).pack(side=tk.LEFT)
        tk.Button(fram, text="Change zoom", command=self.zoom_in).pack(side=tk.LEFT)
        tk.Label(fram, textvariable=self.zoom_level_tv).pack(side=tk.LEFT)
        tk.Label(fram, textvariable=self.data_range_tv).pack(side=tk.RIGHT)
        fram.pack(side=tk.TOP, fill=tk.BOTH)

        # Entry with width equal to filename length
        entry = tk.Entry(self, textvariable=self.filename_tv)
        entry.pack()
        entry.config(state='readonly', width=len(self.filename_tv.get()))

        self.la = tk.Label(self)
        self.la.pack()

        self.chg_image()

        self.filename_tv.set(data_list[self.data_index]['filename'])

        self.pack()

    def projection(self):
        self.projection_state = not self.projection_state
        if self.projection_state:
            proj = np.sum(self.data, axis=1)
            proj = normalize(proj)
            self.img = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(proj))
            self.la.config(
                image=self.img,
                bg="#000000",
                width=self.img.width(),
                height=self.img.height()
            )
        else:
            self.chg_image()

    def get_shape(self) -> str:
        try:
            real_shape = " " + data_list[self.data_index]['real_shape']
        except KeyError:
            real_shape = ""
        return "Shape: "+str(self.data.shape)+f"{real_shape}"

    def zoom_in(self):
        self.zoom_level = self.zoom_levels[
            (self.zoom_levels.index(self.zoom_level) + 1) % len(self.zoom_levels)
        ]
        self.zoom_level_tv.set(str(self.zoom_level))
        self.chg_image()

    def chg_image(self):
        if self.zoom_level != 1.0:
            # Zoom x2
            w = int(self.data.shape[1] * self.zoom_level)
            h = int(self.data.shape[2] * self.zoom_level)
            self.img = PIL.ImageTk.PhotoImage(
                PIL.Image.fromarray(self.data[self.num_page])
                    .resize((h, w), PIL.Image.NEAREST)
            )
        else:
            self.img = PIL.ImageTk.PhotoImage(
                PIL.Image.fromarray(self.data[self.num_page])
            )
        self.la.config(
            image=self.img,
            bg="#000000",
            width=self.img.width(),
            height=self.img.height()
        )
        self.num_page_tv.set(str(self.num_page).zfill(self.num_digits)+'/'+str(self.total_pages))

    def seek_prev(self):
        if self.num_page <= 0:
            return
        self.num_page=self.num_page-1
        # self.im.seek(self.num_page)
        self.chg_image()

    def seek_next(self):
        if self.num_page >= self.total_pages:
            return
        self.num_page = self.num_page+1
        self.chg_image()

    def prev_image(self):
        if self.data_index <= 0:
            return
        self.data_index = self.data_index-1
        self.update_info()

    def next_image(self):
        if self.data_index >= len(data_list)-1:
            return
        self.data_index = self.data_index+1
        self.update_info()

    def update_info(self):
        self.data = data_list[self.data_index]['data']
        self.data_index_tv.set(str(self.data_index)+'/'+str(self.total_data))
        self.filename_tv.set(data_list[self.data_index]['filename'])
        self.shape_tv.set(self.get_shape())
        self.total_pages = self.data.shape[0] - 1
        self.num_page = 0
        self.chg_image()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: 3d_viewer.py <file_names>")
        exit(1)

    file_names = sys.argv[1:]

    loaded_pickle = {}
    new_file_names = []
    for file_name in file_names:
        if file_name.endswith(".pkl"):
            with open(file_name, 'rb') as f:
                pkl_data = pickle.load(f)
            for key, value in pkl_data.items():
                identifier = "{}{}.pkl".format(file_name.replace('pkl', ''), key)
                loaded_pickle[identifier] = value
                new_file_names.append(identifier)
        else:
            new_file_names.append(file_name)
    file_names = new_file_names

    data_list = []
    for file_name in file_names:
        real_shape = None
        if file_name.endswith(".npy"):
            data = np.load(file_name)  # type: np.ndarray
        elif file_name.endswith(".npz"):
            data = np.load(file_name)
            data = data.get(data.files[0])  # type: ignore
        elif file_name.endswith(".nii") or file_name.endswith(".nii.gz"):
            data = nib.load(file_name).get_fdata()  # type: ignore
        elif file_name.endswith(".dcm"):
            data_dcm = pydicom.dcmread(file_name)
            data_dcm.SamplesPerPixel = 1
            data = data_dcm.pixel_array
            try:
                num_slices = int(data_dcm[0x0028, 0x0008].value)
                spacing_between_slices = float(data_dcm[0x0018, 0x0088].value)
            except KeyError:
                num_slices = 1
                spacing_between_slices = 0
            try:
                bscan_spacing = data_dcm[0x0028, 0x0030].value
                rows = int(data_dcm[0x0028, 0x0010].value)
                cols = int(data_dcm[0x0028, 0x0011].value)
                real_shape = [
                    num_slices*spacing_between_slices,
                    cols*bscan_spacing[0],
                    rows*bscan_spacing[1],
                ]
                # Convert real_shape to string for display with 2 decimal
                #   places
                real_shape = [
                    f"{x:.2f}" for x in real_shape
                ]
                real_shape = "["+" x ".join(real_shape)+"]"
            except KeyError:
                pass
        elif (
            file_name.endswith(".png")
            or file_name.endswith(".jpg")
            or file_name.endswith(".jpeg")
        ):
            data = np.array(PIL.Image.open(file_name))
        elif file_name.endswith(".pkl"):
            data = loaded_pickle[file_name]
        else:
            raise ValueError("File type not supported")

        stem = Path(file_name).stem

        if len(data.shape) == 2:
            data = np.expand_dims(data, axis=0)
        elif len(data.shape) == 4:
            data = np.squeeze(data, axis=0)

        data_range = [float(data.min()), float(data.max())]
        data = normalize(data)
        data_item = {
            'filename': stem,
            'data': data,
            'data_range': data_range,
        }
        if real_shape is not None:
            data_item['real_shape'] = real_shape
        data_list.append(data_item)

    main = tk.Tk()
    main.title("Volume Viewer")

    app = App()

    ## Keybindings
    # Arrow keybindings
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
