# created on 4/23/22 at 23:48

import numpy as np
import glob
import cv2
import os
import webcolors
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.webdriver.common.by import By


def removeExtension(directory):
    # removes the extension of the directory (e.g. '.jpg')
    directory = str(directory)
    if '.' not in directory: return directory
    dirlist = directory.split('.')  # splits the directory string into two parts: abs.dir+filename, and the extension
    if len(dirlist) > 2:
        print('Warning: the directory contains more than one "."')
    return dirlist[0]


def getFileName(directory,extension=True):
    if not extension:
        directory = removeExtension(directory)
    return directory.split('/')[-1]


def getFolderPath(directory):
    return '/'.join(directory.split('/')[:-1])+'/'

def getExtension(directory):
    return '.' + directory.split('.')[-1]

def validir(directory):
    # receives a directory (abs.directory + file name + extension), and appends (i) indices to the file name
    # if necessary, to avoid overwriting existing files

    if not os.path.isfile(directory):
        return directory

    folder = getFolderPath(directory)
    name = getFileName(directory,extension=False)
    extension = getExtension(directory)
    print(folder,name,extension)

    index = 2  # the index to be appended to the file name if already exists

    while os.path.isfile(folder + name + f'({index})' + extension):
        index += 1

    return folder + name + f'({index})' + extension


# captcha a single image
def captcha(image,density=0.001, color='black', size=2):
    # the default is probably enough for WeChat
    # density:  how likely each pixel will generate a captcha line
    # filter:  decides if the program will load images that have 'captcha' in its name--so that the
    # captcha'ed images will not be captcha'ed again if left in the same folder

    if isinstance(color,str):
        color = webcolors.name_to_rgb(color)
    text = '''vitae hominum omnibus graviores sunt, populi cibandi atque sanandi sunt, morsque obstaculis verbi'''
    count = 0
    dims = np.shape(image)[:-1]
    locs = np.random.rand(*dims) > (1-density)  # generate the random locations of the captcha-lines

    for start_point,yes in np.ndenumerate(locs):
        if yes:
            start_point = tuple(reversed(start_point))  # cv2 takes (x,y), while the array enumeration gives (y,x)
            size_rand = int(size + size ** (1/2) * np.random.uniform(0.5,1))
            cv2.putText(img=image, text=text[count % len(text)], org=start_point, fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.2*size_rand, color=color, thickness=1)
            count += 1
    return image


def imgFromDir(directory, filter='captcha'):
    # filter: if specified, the program will not load images carrying the filter word--so that the
    # captcha-ed images will not be captcha-ed again if left in the same folder

    accepted = ['jpeg', 'jpg', 'png', 'gif', 'JPG', 'PNG', 'GIF']

    # open images
    images = []
    paths = []
    if any([ext in directory for ext in accepted]):
        # if the directory is an image (rather than a folder), just read it
        images.append(cv2.imread(directory))
        paths.append(directory)
        print('[captcha] loaded 1 image at ' + str(directory))
    else:
        # reading all the images in the entire folder
        if not '/' == directory[len(directory) - 1]: directory += '/'
        typedirecs = [glob.glob(directory + '*.' + ext) for ext in accepted]
        [images.append(cv2.imread(path)) for i in typedirecs for path in i if ((filter is False) or (filter not in str(path)))]
        [paths.append(str(path)) for i in typedirecs for path in i if ((filter is False) or (filter not in str(path)))]
        print('[captcha] loaded {} image(s)'.format(len(images)) + ' from ' + str(directory))
        print(paths)
    return {'images': images, 'paths': paths}


def saveImg(image, folder, name):
    if not '/' == folder[len(folder) - 1]:
        folder += '/'
    if '.' in name:
        name = removeExtension(name)
    full_path = folder + name + '.png'
    valid_path = validir(full_path)  # look for a valid (i.e. not taken) directory
    cv2.imwrite(valid_path, image)
    return valid_path

def url_screenshot(url, folder, name='screenshot', scroll_height=500, pause=1.0):
    # receive a string of url (or list of urls) and saves a screenshot of it (them each)

    # open Chrome
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # go through the url list...
    print(f'loading {url}...')
    driver.get(url)

    # scroll down the page while waiting the page to load
    page_length = int(driver.execute_script("return document.body.scrollHeight"))
    n_scrolls = int(np.ceil(page_length / scroll_height))

    for i in range(n_scrolls):
        print('\r' + str(n_scrolls-i), end=' sections left (~ {} seconds)...'
              .format(int(np.ceil(pause*(n_scrolls-i)))))
        # Scroll down by scroll_height
        driver.execute_script("window.scrollTo(0,{});".format(scroll_height * i))

        # Wait to load page
        sleep(pause)

    # take screenshot of the full page and save it
    # stretch the window to accommodate the full page
    if not '/' == folder[len(folder) - 1]:
        folder += '/'
    valid_directory = validir(folder+name+'.png')
    S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
    driver.set_window_size(S('Width'), S('Height'))
    driver.find_element(By.TAG_NAME, 'body').screenshot(valid_directory)
    print(f'\r screenshot saved to {valid_directory}')
    driver.quit()
    return valid_directory