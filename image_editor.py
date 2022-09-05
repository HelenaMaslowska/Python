#######################################
# Author: Helena Masłowska
# 30.07.2022

from PIL import Image, ImageOps
from PIL.ImageQt import ImageQt			#read and change picture
import sys
import pathlib
import tempfile
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog		#show on the screen
from PySide2.QtGui import QPixmap, QColor, QImage, QIcon
from PySide2.QtCore import QFile , Qt

import os
import subprocess

from numpy import apply_along_axis
from mainwindow import Ui_MainWindow
FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

width = 1000
height = 800

# pyside2-uic mainwindow.ui -o mainwindow.py

# pixmap - tylko i wylacznie wyswietlanie obrazków
# qt - czyta i zapisuje obrazki
# pil - obrobka obrazu
# self.ui - wszystkie rzeczy związane z plikiem mainwindow
class MainWindow(QMainWindow):
	"""
	TODO
	Understand which path image is edited
	Fix jpg and png bug
	"""
	def __init__(self) -> None:
		'''
		pixmap: image which is shown on the screen
		curr_image: this image will be edited
		image: image which is saved in RAM but not in folder on computer
		filename: where the original photo is, it is used to open a photo
		'''
		super(MainWindow, self).__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.set_functions()
		self.pixmap = ''
		self.image = ''				#saved but not showed, bring back save pick from apply/start
		self.curr_image = ''
		self.filename = ''
		self.filename_temp = ''
		self.filetype = ''			# show the type of file, e.g. ['.jpg']
		self.last_apply = ''

	def set_functions(self):
		#buttons
		self.ui.add_img_btn.clicked.connect(self.add_photo)
		self.ui.save_as_btn.clicked.connect(self.save_as)
		self.ui.apply_btn.clicked.connect(self.apply)

		self.ui.color_chbox.clicked.connect(self.set_color_checkbox)
		self.ui.color_slider.valueChanged.connect(self.change_color_spinbox)
		self.ui.color_spinbox.valueChanged.connect(self.change_color_slider)

		self.ui.light_slider.valueChanged.connect(self.change_light_spinbox)
		self.ui.light_spinbox.valueChanged.connect(self.change_light_slider)

		self.ui.contrast_slider.valueChanged.connect(self.change_contrast_spinbox)
		self.ui.contrast_spinbox.valueChanged.connect(self.change_contrast_slider)		#w qtcreator zminić nazwe sliderów 


	def scale(self, pixmap: QPixmap):
		''' scale pixmap '''
		w, h = self.ui.image_shower.width(), self.ui.image_shower.height()
		if (pixmap.width() >= w):
			pixmap = pixmap.scaledToWidth(w)
		if (pixmap.height() >= h):
			pixmap = pixmap.scaledToHeight(h)
		return pixmap
	
	def img_to_pix(self, image: Image):			#after greyscale
		''' convert from Image type to pixmap '''
		data = image.tobytes("raw", "RGBA") 
		img = QImage(data, image.width, image.height, QImage.Format_ARGB32) 
		# img = QImage(data, image.width, image.height, QImage.Format_A2BGR30_Premultiplied) 			#this thing change whole image into blue-pink-white image xd
		pix = QPixmap.fromImage(img) 
		pix = self.scale(pix)
		return pix

	def img_to_pix_2(self):			#bring back to color
		''' convert from Image type to pixmap '''
		img = QImage(str(self.filename))
		pix = QPixmap.fromImage(img) 
		pix = self.scale(pix)
		return pix

	def update_image(self):
		self.ui.image_shower.setPixmap(self.pixmap)
		self.ui.image_shower.repaint()

	def apply(self):
		self.image = self.curr_image	
		print("applied!")
		print(self.curr_image)
		print(self.image)
		self.update_image()


	def add_photo(self):
		''' add/replace new photo to main screen and show it scaled on image_shower '''
		filename, filter = QFileDialog.getOpenFileName(
			parent=self, caption='Open file', filter="Image files (*.png *.jpg)")
		self.filename = filename	
		pixmap1 = QPixmap(filename)
		
		if pixmap1.size():
			pixmap1 = self.scale(pixmap1)
			self.image = Image.open(self.filename)
			self.curr_image = self.image
			self.pixmap = pixmap1 
			self.filetype = pathlib.Path(self.filename).suffixes			# for show type only
			print(self.filetype, self.pixmap.size())
		#print(self.filename[:self.filename.length()-self.filetype.length()])
		#self.filename_temp = self.filename 
		self.update_image()

	def save_as(self):			
		'''TODO
		IT DOESN'T WORK YET xd
		change type to self.type
		'''
		filepath = QFileDialog.getOpenFileName(self, 'Hey! Select a File')
		self.pixmap.save(self.pixmap)

	def set_color_checkbox(self):
		''' set max or min when this is checked or unchecked '''
		#self.curr_image = self.image
		if self.filename == '':
			return 
		
		pixmap = ''
		if not self.ui.color_chbox.isChecked():
			self.ui.color_slider.setValue(0)					#hardcoded, change this later	
			self.curr_image = ImageOps.grayscale(self.image).convert("RGBA")
			# print( 'szary aktualny obrazek', self.curr_image)
			# print( 'obrazek w pamięci', self.image)
			pixmap = self.img_to_pix(self.curr_image)
		else:
			#print("max:", self.ui.color_slider.maximum)
			self.ui.color_slider.setValue(100)					#hardcoded, change this later
			# print( 'kolor aktualny obrazek', self.curr_image)
			# print( 'zapisany obrazek', self.image)			
			pixmap = self.img_to_pix_2()
		self.change_color_spinbox()
		# print('before')
		# print(self.curr_image)
		# print(self.image)
		self.pixmap = pixmap
		self.update_image()

	def change_color_slider(self):
		self.ui.color_slider.setValue(self.ui.color_spinbox.value())

	def change_light_slider(self):
		self.ui.light_slider.setValue(self.ui.light_spinbox.value())

	def change_contrast_slider(self):
		self.ui.contrast_slider.setValue(self.ui.contrast_spinbox.value())

	def change_color_spinbox(self):
		self.ui.color_spinbox.setValue(self.ui.color_slider.value())

	def change_light_spinbox(self):
		self.ui.light_spinbox.setValue(self.ui.light_slider.value())

	def change_contrast_spinbox(self):
		self.ui.contrast_spinbox.setValue(self.ui.contrast_slider.value())


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())






###########################################
### smieci - może coś się kiedyś przyda ###


#color = QGraphicsColorizeEffect(self)		#library QWidgets QGraphicsColorizeEffect
# 	c = self.pixmap.pixel(x,y)
# 	avg = (c.getRed()*0.3 + c.getGreen()*0.6 + c.getBlue()*0.1)/3
# 	colors = QColor(c).getRgbF()
# 	print ("(%s,%s) = %s avg: %s" % (x, y, colors, avg))

'''class Window(QMainWindow):

	def __init__(self):
		super().__init__()
		name_list = ["name", "s_width", "s_height", "b_width", "b_height", "function"]
		set = {zip(name_list, set(enumerate(name_list)))}
		
		set_buttons = [
			[	"Add image", 	20, 	int(height / 2) - 20, 	100, 	40,		self.clickme],
			[	"Save",			20, 	int(height / 2) + 30,	100,	40 	]
		]

		self.setWindowTitle("Paintroom")
		self.setGeometry(400, 200, width, height)
		self.label = QLabel(self)
		
		self.UiComponents()
		self.show()

	def UiComponents(self):
		# for button in self.set_buttons:
		# 	button = QPushButton(button[0], self)
		# 	button.setGeometry(button[1], button[2], button[3], button[4])
		# 	button.clicked.connect(self.clickme)
		for i in self.set_buttons:
			button = QPushButton(i[self.set["name"]], self)
			button.setGeometry(i[self.set["s_width"]], i[self.set["s_height"]], i[self.set["b_width"]], i[self.set["b_height"]]  )
			button.clicked.connect(self.clickme)
		# button = QPushButton("Add image", self)
		# button.setGeometry(20, int(height / 2) + 40, 100, 40  )
		# button.clicked.connect(self.clickme)

	def explore(path):
		# explorer would choke on forward slashes
		path = os.path.normpath(path)

		if os.path.isdir(path):
			subprocess.run([FILEBROWSER_PATH, path])
		elif os.path.isfile(path):
			subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])

	def clickme(self):
		filename, filter = QFileDialog.getOpenFileName(
            parent=self, caption='Open file', filter='*.png')
		self.pixmap = QPixmap(filename)
		self.label.setPixmap(self.pixmap)
		self.label.resize(self.pixmap.width(), self.pixmap.height())
		print("pressed")'''


# def text_setup(window):
# 	helloMsg = QLabel('<h1>Hello World!</h1>', parent=window)
# 	helloMsg.move(20, 1)	

# def buttons_setup(window):

# 	layout = QVBoxLayout()
# 	layout.addWidget(QPushButton('Add image'))
# 	window.setLayout(layout)

# def window_setup():
# 	window = QWidget()
# 	window.setWindowTitle('Paintroom')
# 	window.setGeometry(100, 100, 1000, 700)
# 	window.move(60, 15)
# 	text_setup(window)
# 	buttons_setup(window)	
# 	window.show()
# 	return window


# def main():
# 	try:
		
# 		#Relative Path
# 		img = Image.open("bird.jpg") 

# 		#Saved in the same relative location
# 		img.save("rotated_picture.jpg")


# 		#img = img.show()
# 	except IOError:
# 		pass


# app = QApplication(sys.argv)
# window = window_setup()
# sys.exit(app.exec_())


