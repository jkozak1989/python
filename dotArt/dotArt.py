import svgwrite
from PIL import Image

im = Image.open('obrazek.jpg')
pix = im.load()
#pixels
pictureWidth, pictureHeight = im.size
circleRadius = 5
drawingWidth = pictureWidth*circleRadius*2
drawingHeight = pictureHeight*circleRadius*2

dwg = svgwrite.Drawing('test.svg', size=(drawingWidth,drawingHeight))
for i in range(pictureWidth):
    for j in range(pictureHeight):
        dwg.add(dwg.circle(center=(i*circleRadius*2+circleRadius,j*circleRadius*2+circleRadius),r=circleRadius, fill=f'rgb({pix[i,j][0]},{pix[i,j][1]},{pix[i,j][2]})'))
dwg.save()