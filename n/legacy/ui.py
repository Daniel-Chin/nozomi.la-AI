# deprecated

from ai import ALL_RESPONSES, RES_NEGATIVE, RES_FINE, RES_BETTER, RES_MORE, RES_WOW, RES_SAVE, DEBUG
import tkinter as tk
from PIL import Image, ImageTk
from nozo import ImageWorker
from io import BytesIO
import database

TITLE = 'Nozomi.la AI'
LOOP_INTERVAL = 100
PADDING = 5
RIGHT_FRAME_WIDTH = 150

DISPLAY = {
  RES_NEGATIVE: ('(N)egative', 'I wish to see no more of this'), 
  RES_FINE: ('(O)k', 'I feel neutral'), 
  RES_BETTER: ('(H)as Value', 'I can enjoy it'),
  RES_MORE: ('(M)ore', 'Show more like this'), 
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
  print('UI doc', doc.id)

  tk.Label(root, text=f'{mode} Mode').pack()

  resize_h = h / (doc.height * len(doc.img_urls))
  resize_w = (w - RIGHT_FRAME_WIDTH) / doc.width
  if resize_h > resize_w:
    resize = resize_w
  else:
    resize = resize_h
  resize_wh = (
    round(doc.width * resize), round(doc.height * resize)
  )

  lowerFrame = tk.Frame(root)
  lowerFrame.pack()
  leftFrame = tk.Frame(lowerFrame)
  leftFrame.pack(side=tk.LEFT)
  rightFrame = tk.Frame(lowerFrame)
  rightFrame.pack(side=tk.LEFT)
  root.rightFrame = rightFrame

  imgWorkers = []
  imgLabels = []
  root.imgLabels = imgLabels
  for url in doc.img_urls:
    imgWorkers.append(ImageWorker(url))
    imgLabel = tk.Label(leftFrame, text='Loading...')
    imgLabel.pack()
    imgLabels.append(imgLabel)
  
  root.bind('<Key>', onKey)
  root.buttons = {}

  root.after(
    LOOP_INTERVAL, loop, root, imgWorkers, 
    imgLabels.copy(), result, resize_wh, 
  )
  root.mainloop()
  return result[0]

def loop(root, imgWorkers, imgLabelsLeft, result, resize_wh):
  for i, worker in [*enumerate(imgWorkers)]:
    img_bytes = worker.check()
    if img_bytes is not None:
      label = imgLabelsLeft.pop(i)
      imgWorkers.pop(i)
      bio = BytesIO()
      bio.write(img_bytes)
      bio.seek(0)
      image = Image.open(bio).resize(resize_wh, Image.ANTIALIAS)
      photo = ImageTk.PhotoImage(image)
      label.configure(text=None, image=photo)
      label.bio = bio # keep ref
      label.photo = photo
  if imgWorkers:
    root.after(
      LOOP_INTERVAL, loop, root, imgWorkers, 
      imgLabelsLeft, result, resize_wh, 
    )
  else:
    for response in ALL_RESPONSES:
      button = tk.Button(root.rightFrame, text=DISPLAY[response][0])
      button.response = response
      button.result = result
      button.root = root
      button.bind('<Button-1>', onClick)
      button.bind('<Return>', onClick)
      button.bind('<Key>', onKey)
      button.pack(fill=tk.X, padx=PADDING, pady=PADDING)
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
  char = (event.char or event.keysym).upper()
  buttons = event.widget.root.buttons
  try:
    response = {
      'N': RES_NEGATIVE, 
      'O': RES_FINE, 
      'H': RES_BETTER, 
      'G': RES_WOW, 
      'S': RES_SAVE, 
    }[char]
  except KeyError:
    return
  buttons[response].focus_set()
