# created on 4/23/22 at 15:53

from tkinter import *
from tkinter import ttk, filedialog
from PIL import ImageTk, Image
from captcharfunction import *
from functools import partial

root = Tk()
root.title('CAPTCHAR')
root.geometry('600x400')
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)
root.grid_columnconfigure(2, weight=0)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=0)
entered = False


class explainedLabel():
    explanation = 0

    def __init__(self,name,enabled=True,*args, **kwargs):
        self.name = name
        self.label = Label(root,text=self.name,fg='black' if enabled else 'gray')
        self.enabled = enabled
        if args or kwargs:
            self.label.grid(*args,**kwargs)
            self.label.bind("<Enter>",self.on_enter)
            self.label.bind("<Leave>",self.on_leave)

    def on_enter(self,*args):
        if self.enabled:
            self.label.config(text=self.explanation)

    def on_leave(self,*args):
        self.label.config(text=self.name)

    def add_label(self,new_label):
        new_label.bind("<Enter>", self.on_enter)
        new_label.bind("<Leave>", self.on_leave)
        self.label = new_label

    def add_alternative(self,alt_name=None,alt_exp=None):
        if alt_name is None:
            alt_name = self.name
        if alt_exp is None:
            alt_exp = self.explanation
        self.on_alternate = False
        self.alt_name = alt_name
        self.alt_exp = alt_exp

    def alternate(self):
        self.on_alternate = not self.on_alternate
        self.name, self.alt_name = self.alt_name, self.name
        self.explanation, self.alt_exp = self.alt_exp, self.explanation
        self.on_leave()

    def disable(self):
        self.enabled = False
        self.label['fg'] = 'gray'

    def enable(self):
        self.enabled = True
        self.label['fg'] = 'black'


class explainedCheckBox():
    explanation = 0
    def __init__(self, name, variable, *args, **kwargs):
        self.name = name
        self.box = Checkbutton(root, text=self.name, variable=variable)
        if args or kwargs:
            self.box.grid(*args, **kwargs)
            self.box.bind("<Enter>", self.on_enter)
            self.box.bind("<Leave>", self.on_leave)
    def on_enter(self, *args):
        self.box.config(text=self.explanation)

    def on_leave(self, *args):
        self.box.config(text=self.name)


class defaultedEntry():
    focused = False

    def __init__(self, default, gray=False, state='normal',*args, **kwargs):
        self.default = default
        self.gray = gray  # whether the default text gets grayed out (as instruction) or not (as default value)
        self.entry = Entry(root,fg='gray' if gray else 'black')
        self.entry.grid(*args,**kwargs)
        self.entry.insert(0,default)
        self.entry['state'] = state
        self.entry.bind("<FocusIn>", self.on_Focus)
        self.entry.bind("<FocusOut>", self.on_Defocus)

    def on_Focus(self, *args):
        self.focused = True
        if self.entry.get() == self.default:
            self.entry.delete(0, "end")
            self.entry['fg'] = 'black'

    def on_Defocus(self, *args):
        self.focused = False
        if self.entry.get() == '':
            if self.gray:
                self.entry['fg'] = 'gray'
            self.entry.insert(0,self.default)

    def add_alternative(self,alt_default):
        self.on_alternate = False
        self.alt_default = alt_default

    def alternate(self):
        self.on_alternate = not self.on_alternate
        self.default, self.alt_default = self.alt_default, self.default
        self.entry.delete(0, "end")
        if not self.focused:
            self.on_Defocus()

    def disable(self):
        self.entry['state'] = 'disable'
        if not self.focused: self.on_Defocus()

    def enable(self):
        self.entry['state'] = 'normal'
        if not self.focused: self.on_Defocus()

    @property
    def value(self):
        return self.entry.get()

    @property
    def specified(self):
        return (not self.value == self.default) and (not self.value == '') and (not self.value == getattr(self, 'alt_default', ''))


def callback(*args):
    if FromEntry.specified and (url_check.get()==0 or ToEntry.specified):
        GoButton['state'] = 'normal'
        GoButton['image'] = arrowimg
    else:
        GoButton['state'] = 'disabled'
        GoButton['image'] = grayarrow


def browseFiles(entry):
    filename = filedialog.askopenfilename(initialdir = "/Users/matthewan/Desktop/",
                                          title = "Select a File",
                                          filetypes = (("Images",
                                                        "*.jpg *.jpeg *.png *.gif *.JPG *.JPEG *.PNG *.GIF"),
                                                       ("all files",
                                                        "*.*")))
    if not filename == '':
        entry.on_Focus()
        entry.entry.insert(0, filename)
    elif entry.entry.get() == entry.default:
        entry.on_Defocus()

def browseFolders(entry):
    filename = filedialog.askdirectory(initialdir = "/Users/matthewan/Desktop/",
                                          title = "Select a File",)
    if not filename == '':
        entry.on_Focus()
        entry.entry.insert(0, filename)
    elif entry.entry.get() == entry.default:
        entry.on_Defocus()


# 1,2: an arrow and the GO button
arrowimg = Image.open('Arrow.png').resize((50,25))
grayarrow = Image.open('GrayArrow.png').resize((50,25))

arrowimg = ImageTk.PhotoImage(arrowimg)
grayarrow = ImageTk.PhotoImage(grayarrow)


def GO():
    if url_check.get() == 1:
        screenshot_path = url_screenshot(url = FromEntry.value,
                                         folder = ToEntry.value,
                                         name = SSNameEntry.value,
                                         pause = float(SSPaceEntry.value))
        images, open_paths = imgFromDir(directory=screenshot_path, filter=False).values()
        notice = f'Saved screenshot from ' + FromEntry.value
        inst1.config(text=notice)
    else:
        images, open_paths = imgFromDir(directory=FromEntry.value,
                                    filter=TagEntry.value).values()
    if len(images) == 0:
        notice = 'No images found! Please check your directory.'
        inst1.config(text=notice)
        return None
    plural = 's' if len(images)>1 else ''
    notice = f'Loaded {len(images)} image{plural} from ' + FromEntry.value
    inst1.config(text=notice)
    captcha_paths = []
    for index, image in enumerate(images):
        notice = f'Captcharing {getFileName(open_paths[index])} ({index}/{len(images)})...'
        inst2.config(text=notice)
        captchan_image = captcha(image,
                                 density=float(DensityEntry.value),
                                 color=ColorEntry.value,
                                 size=float(SizeEntry.value))
        new_name = getFileName(open_paths[index],extension=False) + '_' + TagEntry.value
        saving_folder = ToEntry.value if ToEntry.specified else getFolderPath(open_paths[index])
        saved_path = saveImg(image=image,
                             folder=saving_folder,
                             name=new_name)
        captcha_paths.append(saved_path)
        notice = f'Saving {getFileName(open_paths[index])} ({index}/{len(images)})...'
        inst2.config(text=notice)

    notice = f'Saved {len(images)} image{plural} to ' + (ToEntry.value if ToEntry.specified else getFolderPath(open_paths[index])) + (getFileName(saved_path) if len(images)==1 else '')
    inst2.config(text=notice)

    slogan = 'MORS OBSTACVLIS VERBI'
    sloganLabel = Label(root, text=slogan, font=("Times", 24, "bold"))
    sloganLabel.grid(row=4, column=2, columnspan=3)
    sloganExLabel = explainedLabel(name=sloganLabel['text'])
    sloganExLabel.add_label(sloganLabel)
    sloganExLabel.explanation = '''DEATH TO OBSTACLES OF THE WORD'''


GoButton = Button(root, image=grayarrow, padx=10, pady=10, command=GO, state='disabled')
GoButton.grid(row=1,column=2)


# 0,0: text asking for reading directory
FromLabel = explainedLabel(name='Import Directory',row=0,column=0)
FromLabel.explanation = '''enter the directory of a single image,\nor a folder to read all the images in it'''

# 1,0: entry box for input directory
temp_text_in = 'Read the image(s) from here...'
FromEntry = defaultedEntry(default=temp_text_in,gray=True,row=1,column=0,sticky='ew')
sv_in = StringVar(value=FromEntry.value)
sv_in.trace_add("write", callback)
FromEntry.entry['textvariable'] = sv_in


# 1,1: file browser for input
fileimg = Image.open('FileBrowser.png').resize((24,18))
fileimg = ImageTk.PhotoImage(fileimg)
grayfile = Image.open('GrayFile.png').resize((24,18))
grayfile = ImageTk.PhotoImage(grayfile)
InExploreButton = Button(root, image=fileimg, command=partial(browseFiles,entry=FromEntry))
InExploreButton.grid(row=1,column=1)


# 0,3: text asking for saving directory
ToLabel = explainedLabel(name='Export Directory',row=0,column=3)
ToLabel.explanation = '''the directory of the folder for saving the\nimage(s), or leave blank to have\ntheir images be saved to the same folder'''

# 1,3: entry box for output directory
temp_text_out = '...And save the image(s) to here'
ToEntry = defaultedEntry(default=temp_text_out,gray=True,row=1,column=3,sticky='ew')
sv_out = StringVar(value=ToEntry.value)
sv_out.trace_add("write", callback)
ToEntry.entry['textvariable'] = sv_out

# 1,4: file browser for output
OutExploreButton = Button(root, image=fileimg, command=partial(browseFolders,entry=ToEntry))
OutExploreButton.grid(row=1,column=4)

# 2~3,0~1: switch button to url download
FromLabel.add_alternative(alt_name='URL to be Opened',
                          alt_exp='load the url and work with a\nscreenshot of the entire page')
FromEntry.add_alternative(alt_default='Load a screenshot from here...')
ToLabel.add_alternative(alt_exp='enter the directory of the folder to save\nthe screenshots and captcha image(s) to;\n(this must be filled under URL mode)')

def urlON(*args):
    FromLabel.alternate()
    FromEntry.alternate()
    ToLabel.alternate()
    if url_check.get() == 1:
        InExploreButton['state'] = 'disabled'
        InExploreButton['image'] = grayfile
        SSNameLabel.enable()
        SSNameEntry.enable()
        SSPaceLabel.enable()
        SSPaceEntry.enable()
    elif url_check.get() == 0:
        InExploreButton['state'] = 'normal'
        InExploreButton['image'] = fileimg
        SSNameLabel.disable()
        SSNameEntry.disable()
        SSPaceLabel.disable()
        SSPaceEntry.disable()
    callback()

mode = 'file'
url_check = IntVar()
url_check.trace_add("write",urlON)
UrlButton = explainedCheckBox(name='save from url',variable=url_check,row=2,column=0,rowspan=2)
UrlButton.explanation = 'tick if the import source is a URL'

# 2,/ and 3,/: instructions
inst1 = Label(root, text='Press the arrow to captcha the images when all set.')
inst1.grid(row=2,column=2,columnspan=3)
inst2 = Label(root, text='For explanations, hover the cursor over the labels.')
inst2.grid(row=3,column=2,columnspan=3)


# 5,/: separator line
ttk.Separator(root, orient=HORIZONTAL).grid(row=5,column=0,columnspan=5,sticky='ew')

# 6,0: 'Options' text
Label(root, text='Options',font=('Helvetica',25)).grid(row=6,column=2)

# 7, 0~1: tag option
TagLabel = explainedLabel(name='File Tag',row=7,column=0,columnspan=2)
TagLabel.explanation = '''extension to the original file name, indicating \n that the image has been captcha-ed,\ne.g."image.png" → "image_captchad.png"\nAlso, CAPTCHAR would skip images carrying\nthis tag, so they are not captcha-ed twice'''
TagEntry = defaultedEntry(default='captcha',row=7,column=3,columnspan=2)

# 8, 0~1: density option
DensityLabel = explainedLabel(name='Captcha Density',row=8,column=0,columnspan=2)
DensityLabel.explanation = '''how likely each pixel generates a distracting\nletter for captcha, in decimal probability\ni.e. 0.01 gives a chance of 1%'''
DensityEntry = defaultedEntry(default='0.005',row=8,column=3,columnspan=2)

# 9, 0~1: captcha color option
ColorLabel = explainedLabel(name='Captcha Color',row=9,column=0,columnspan=2)
ColorLabel.explanation = '''the color of the captcha characters;\nonly accepts English words of colors'''
ColorEntry = defaultedEntry(default='black',row=9,column=3,columnspan=2)

# 10, 0~1: font size option
SizeLabel = explainedLabel(name='Captcha Size',row=10,column=0,columnspan=2)
SizeLabel.explanation = '''size of captcha letters,\nin Python cv2 font units'''
SizeEntry = defaultedEntry(default='2',row=10,column=3,columnspan=2)

# 11,/: separator line
ttk.Separator(root, orient=HORIZONTAL).grid(row=11,column=0,columnspan=5,sticky='ew')

# 12, 0~1: screenshot name option
SSNameLabel = explainedLabel(name='Screenshot Name',enabled=False,row=12,column=0,columnspan=2)
SSNameLabel.explanation = '''name of the screenshot photo\n(without extensions like .png)'''
SSNameEntry = defaultedEntry(default='screenshot',state='disabled',row=12,column=3,columnspan=2)

# 13, 0~1: pace option
SSPaceLabel = explainedLabel(name='Screenshot Speed',enabled=False,row=13,column=0,columnspan=2)
SSPaceLabel.explanation = '''how many seconds are given for a chunk\nof the page to load; pages with many\nimages might take longer to load'''
SSPaceEntry = defaultedEntry(default='0.1', state='disabled', row=13, column=3, columnspan=2)

root.mainloop()

