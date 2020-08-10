from ai import ALL_RESPONSES, RES_NEGATIVE, RES_FINE, RES_WOW, RES_SAVE
import tkinter as tk
from PIL import Image, ImageTk
from nozo import ImageWorker
from io import BytesIO
import database

TITLE = 'Nozomi.la AI'
LOOP_INTERVAL = 100
PADDING = 10

DISPLAY = {
  RES_NEGATIVE: ('(N)egative', 'I wish to see no more of this'), 
  RES_FINE: ('(O)k', 'I feel neutral'), 
  RES_WOW: ('(G)ood', 'One of the rare good ones'), 
  RES_SAVE: ('(S)tar', 'Super good. Save to disk'), 
}

def getResponse(doc, mode):
  # modifies doc.local_filenames if RES_SAVE. 
  result = []
  root = tk.Tk()
  root.title(TITLE)
  root.root = root
  root.doc = doc
  w, h = root.winfo_screenwidth(), root.winfo_screenheight()
  root.geometry("%dx%d+0+0" % (w, h))

  resize = h / (doc.height * len(doc.img_urls))
  resize = min(resize, w / doc.width)

  imgWorkers = []
  imgLabels = []
  root.imgLabels = imgLabels
  for url in doc.img_urls:
    imgWorkers.append(ImageWorker(url))
    imgLabel = tk.Label(root, text='Loading...')
    imgLabel.pack()
    imgLabels.append(imgLabel)
  
  root.after(
    LOOP_INTERVAL, loop, root, imgWorkers, 
    imgLabels.copy(), result, resize,
  )
  root.bind('<Key>', onKey)
  root.buttons = {}

  root.mainloop()
  return result[0]

def loop(root, imgWorkers, imgLabelsLeft, result, resize):
  root.after(
    LOOP_INTERVAL, loop, root, imgWorkers, 
    imgLabelsLeft, result, resize,
  )
  for i, worker in [*enumerate(imgWorkers)]:
    img_bytes = worker.check()
    if img_bytes is not None:
      label = imgLabelsLeft.pop(i)
      imgWorkers.pop(i)
      bio = BytesIO()
      bio.write(img_bytes)
      bio.seek(0)
      image = Image.open(bio).resize((
        root.doc.width * resize, root.doc.height * resize
      ), Image.ANTIALIAS)
      photo = ImageTk.PhotoImage(image)
      label.configure(text=None, image=photo)
      label.bio = bio # keep ref
      label.photo = photo
  if not imgWorkers:
    frame = tk.Frame(root)
    frame.pack(fill=tk.X)
    for response in ALL_RESPONSES:
      button = tk.Button(frame, text=DISPLAY[response][0])
      button.response = response
      button.result = result
      button.root = root
      button.bind('<Button-1>', onClick)
      button.bind('<Return>', onClick)
      button.bind('<Key>', onKey)
      button.pack(frame, side=tk.LEFT, expand=tk.YES, padx=PADDING/2, pady=PADDING)
      root.buttons[response] = button

def onClick(event):
  button = event.widget
  button.result.append(button.response)
  if button.response == RES_SAVE:
    root = button.root
    imgs = []
    for label in root.imgLabels:
      label.bio.seek(0)
      imgs.append(label.bio.getbuffer())
    database.saveImg(root.doc, imgs)
  button.root.destroy()

def onKey(event):
  char = event.char or event.keysym
  buttons = event.widget.root.buttons
  try:
    response = {
      'N': RES_NEGATIVE, 
      'O': RES_FINE, 
      'G': RES_WOW, 
      'S': RES_SAVE, 
    }[char]
  except KeyError:
    return
  buttons[response].focus_set()
