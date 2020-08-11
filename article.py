import wx
import os
import sys
import fitz

from PIL import Image
import PIL.ImageOps	

start_char = 'A'

local_path = os.path.dirname(os.path.realpath(__file__))
images_path = os.path.join(local_path, 'images')

if not os.path.exists(images_path):
    os.makedirs(images_path)

def get_path(wildcard):
	app = wx.App(None)
	style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
	dialog = wx.FileDialog(None, 'Open', wildcard=wildcard, style=style)
	dialog.SetDirectory(os.path.join(local_path, ''))
	if dialog.ShowModal() == wx.ID_OK:
		path = dialog.GetPath()
	else:
		path = None
	dialog.Destroy()
	return path

def change_contrast(img, level):
	factor = (259 * (level + 255)) / (255 * (259 - level))
	def contrast(c):
		return 128 + factor * (c - 128)
	return img.point(contrast)


def write_images_from_pdf(pdf_path):
	page_count = 0
	doc = fitz.open(pdf_path)
	for page in doc:
		pix = page.getPixmap(matrix=fitz.Matrix(150/72,150/72))
		img_name = 'img_' + chr(ord(start_char)+page_count) + '.png'
		pix.writePNG(os.path.join(images_path, img_name))
		page_count += 1

def createOneVerticalImage(pdf_path):
	image_file_paths = [os.path.join(images_path, f) for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
	image_file_paths.sort()
	
	images = [Image.open(img_path) for img_path in image_file_paths]
	
	widths, heights = zip(*(i.size for i in images))

	total_height = sum(heights)
	max_width = max(widths)

	new_im = Image.new('RGB', (max_width, total_height))

	x_offset = 0
	
	for one_image in images:
		centered_offset = int((max_width - one_image.size[0])/2)
		colored_image = PIL.ImageOps.invert(one_image)
		colored_image = change_contrast(colored_image, -35)
		new_im.paste(colored_image, (centered_offset,x_offset))
		x_offset += colored_image.size[1]
	
	new_path = os.path.join(local_path , os.path.splitext(os.path.basename(pdf_path))[0] + '.jpg')
	new_im.save(new_path)

def deleteUsedImages():
	list( map( os.unlink, (os.path.join( images_path,f) for f in os.listdir(images_path)) ) )
	os.rmdir(images_path)

def main():
	try:
		pdf_path = get_path('*.pdf')
		write_images_from_pdf(pdf_path)
		createOneVerticalImage(pdf_path)
		deleteUsedImages()
		
	except Exception as e:
		print(str(e))
		sys.exit()
	
if __name__== "__main__":
	main()
