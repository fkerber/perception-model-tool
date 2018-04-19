"""
This file is part of the perception model tool.

The perception model tool is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

The perception model tool is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with the perception model tool.  If not, see <http://www.gnu.org/licenses/>.
"""

from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
from scipy import misc, ndimage
from threading import Thread

import ntpath
import math
import numpy as np

from perceptual_model.perceptual_model import display_center, ObserverSpecification, \
    DEFAULT_FOVEAL_RESOLUTION, make_perpendicular_display
from scripts.util import filter_image


def main():
    MyFrame().mainloop()

class MyFrame(Frame):

    def __init__(self):
        """Initializes the GUI.
        """
        Frame.__init__(self)
        self.master.title("Filter Screenshots")
        self.master.minsize(width=400, height=425)
        self.grid(sticky=W + E + N + S)
        self.grid_rowconfigure(2, minsize=50)
        self.grid_columnconfigure(0, minsize=25)
        self.grid_columnconfigure(3, minsize=25)
        self.grid_rowconfigure(11, minsize=50)

        self.fileLabel = Label(self, text="Please select an input file")
        self.fileLabel.grid(row=0, column=1, sticky=W)

        self.fileLabel2 = Label(self)
        self.fileLabel2.grid(row=1, column=1, sticky=W)

        Button(self, text="Browse input file", command=self.load_file, width=15).grid(row=0, column=2, sticky=E)

        self.saveButton = Button(self, text="Set output file", command=self.save_file, width=15, state=DISABLED)
        self.saveButton.grid(row=1, column=2, sticky=E)

        Label(self, text="Observer distance in meters").grid(row=3, column=1, sticky=W)
        self.observer_distance = DoubleVar(value="0.4")
        self.observer_distanceEdt = Entry(self, textvariable=self.observer_distance)
        self.observer_distanceEdt.grid(row=3, column=2, sticky=W)

        Label(self, text="Display Size X in meters").grid(row=4, column=1, sticky=W)
        self.display_size_x = DoubleVar(value="0.02")
        self.display_size_xEdt = Entry(self, textvariable=self.display_size_x)
        self.display_size_xEdt.grid(row=4, column=2, sticky=W)

        Label(self, text="Display Size Y in meters").grid(row=5, column=1, sticky=W)
        self.display_size_y = DoubleVar(value="0.02")
        self.display_size_yEdt = Entry(self, textvariable=self.display_size_y)
        self.display_size_yEdt.grid(row=5, column=2, sticky=W)

        Label(self, text="Display Resolution X in pixels").grid(row=6, column=1, sticky=W)
        self.display_resolution_x = IntVar(value=200)
        self.display_resolution_xEdt = Entry(self, textvariable=self.display_resolution_x)
        self.display_resolution_xEdt.grid(row=6, column=2, sticky=W)

        Label(self, text="Display Resolution Y in pixels").grid(row=7, column=1, sticky=W)
        self.display_resolution_y = IntVar(value=200)
        self.display_resolution_yEdt = Entry(self, textvariable=self.display_resolution_y)
        self.display_resolution_yEdt.grid(row=7, column=2, sticky=W)

        Label(self, text="Horizontal Orientation of Display to Observer in Degrees").grid(row=8, column=1, sticky=W)
        self.h_angle = DoubleVar(value=10)
        self.h_angleEdt = Entry(self, textvariable=self.h_angle)
        self.h_angleEdt.grid(row=8, column=2, sticky=W)

        Label(self, text="Vertical Orientation of Display to Observer in Degrees").grid(row=9, column=1, sticky=W)
        self.v_angle = DoubleVar(value=20)
        Entry(self, textvariable=self.v_angle).grid(row=9, column=2, sticky=W)

        self.direct = IntVar(value=0)

        Radiobutton(self, text="Peripheral observation", padx=20, variable=self.direct, value=0).grid(row=10, column=1,
                                                                                                      sticky=W)
        Radiobutton(self, text="Direct observation", padx=20, variable=self.direct, value=1).grid(row=10, column=2,
                                                                                                  sticky=W)

        self.processButton = Button(self, text="Process", command=self.process, width=15, state=DISABLED)
        self.processButton.grid(row=12, column=1, columnspan=2, sticky=W + E)

    def saveBox(
            self,
            title=None,
            fileName=None,
            dirName=None,
            fileExt=".png",
            fileTypes=[("jpg files", "*.jpg"), ("png files", "*.png")]):
        """Helper function to display a save dialog.
        :param title: the title of the dialog.
        :param fileName: the suggested file name.
        :param dirName: the opened directory to save into.
        :param fileExt: the suggested file extension.
        :param fileTypes: the list of supported file types.
        :return: the path of the file to save to.
        """
        options = {}
        options['defaultextension'] = fileExt
        options['filetypes'] = fileTypes
        options['initialdir'] = dirName
        options['initialfile'] = fileName
        options['title'] = title

        return asksaveasfilename(**options)

    def load_file(self):
        """Helper function to get the path of the image to process.
        :return: None
        """
        self._fname = askopenfilename(filetypes=[("jpg files", "*.jpg"), ("png files", "*.png")])
        if self._fname:
            try:
                self.saveButton['state'] = 'normal'
                self.fileLabel['text'] = self._fname
            except:
                showerror("Open Source File", "Failed to read file\n'%s'" % self._fname)

    def save_file(self):
        """Helper function to get the path the processed image should be saved to.
        :return: None
        """
        sname = self.saveBox("Save perceived image as", ntpath.splitext(ntpath.basename(self._fname))[0] + "_perceived",
                             ntpath.dirname(self._fname), ntpath.splitext(ntpath.basename(self._fname))[1])
        if sname:
            self.fileLabel2['text'] = sname
            self.processButton['state'] = 'normal'

    def do_work(self):
        """Processes the given image based on the set parameters and saves it to the defined path.
        :return: None
        """
        image = ndimage.imread(self._fname)

        observer_pos = np.array([0, 0, 0])
        display = make_perpendicular_display(self.display_size_x.get(),
                                             self.display_size_y.get(),
                                             self.observer_distance.get(),
                                             math.radians(self.h_angle.get()), math.radians(self.v_angle.get()),
                                             self.display_resolution_x.get(),
                                             self.display_resolution_y.get())

        observer_display_dir = display_center(display) - observer_pos
        observer_direct = ObserverSpecification(observer_pos, observer_display_dir, DEFAULT_FOVEAL_RESOLUTION)

        observer_forward_dir = np.array([0, 1, 0])
        observer_forward = ObserverSpecification(observer_pos, observer_forward_dir, DEFAULT_FOVEAL_RESOLUTION)

        out_image = filter_image(image, display, observer_direct if self.direct.get() else observer_forward)
        misc.imsave(self.fileLabel2['text'], out_image[0])

        self.processButton['text'] = 'Process'
        self.processButton['state'] = 'normal'

    def process(self):
        """Helper function to update the GUI and start the processing of the image.
        :return:
        """
        self.processButton['state'] = 'disabled'
        self.processButton['text'] = 'Image is being processed ...'

        thread = Thread(target=self.do_work)
        thread.start()


if __name__ == "__main__":
    main()
