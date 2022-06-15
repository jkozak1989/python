import pandas as pd
from PIL import Image, ImageTk
import tkinter
from sklearn.tree import DecisionTreeClassifier

data = pd.read_csv("colors.csv")

X = data[["red","green","blue"]]
y = data["Name"]

model = DecisionTreeClassifier(criterion='entropy', random_state = 0)

model.fit(X.values, y.values)

sample = pd.DataFrame([[100,131,200]])

def predictColor(model,colorTuple):
    color = model.predict([[colorTuple[0],colorTuple[1],colorTuple[2]]])
    print(f"You clicked on {color[0]}.")

root = tkinter.Tk()

def check_rgb(x,y, img):
    pix = img.load()
    predictColor(model,pix[x,y])

def callback(event):
    global img
    check_rgb(event.x, event.y, img)


w = tkinter.Canvas(root, width=500, height=500, bd=0, highlightthickness=0, relief='ridge')
w.pack()

img = Image.open("picture.png")
img = img.resize((500,500))
tkImg = ImageTk.PhotoImage(img)
w.create_image(0, 0, image=tkImg, anchor="nw")

root.bind("<Button-1>", callback)

print("Welcome to Colorblind Helper app. You can left-click in any given place in the picture and the app will predict the color for you.")
root.mainloop()
