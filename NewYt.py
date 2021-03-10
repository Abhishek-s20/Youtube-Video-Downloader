import tkinter as tk
from pytube import YouTube, request
from tkinter import messagebox
from tkinter import ttk
from tkinter import LabelFrame
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar, Treeview
from tkinter import messagebox as msg
# from PIL import Image, ImageTk
import time
import threading

is_paused = is_cancelled = False
adaptive_list = []
progressive_list = []
yt = object
title = ''
name = ''
naming_criteria = ['/', '\\', '<', '>', ':', '"', '|', '?']
count=0

def directory():
    path_to_save = askdirectory()
    if path_to_save is None:
        directory()
        search_button['state'] = 'disable'
    else:
        entry2.insert("0", f'{path_to_save}')
    download_button['state'] = 'normal'


def list_creation():
    global yt, title, name

    trv.delete(*trv.get_children())
    global adaptive_list
    global progressive_list

    adaptive_list = []
    progressive_list = []
    title = yt.title
    name = ''
    for c in title:
        if c not in naming_criteria:
            name += c

    progressive_videos = yt.streams.filter(progressive=True)
    for progressive_video in progressive_videos:
        progressive_list += [(title[:45], str(progressive_video.resolution) + " - " + str(progressive_video.fps)+" fps",
                              str(int(progressive_video.filesize / (1024 * 1024))) +
                              " MB", progressive_video.mime_type, "yes", progressive_video.itag)]
    for value in progressive_list:
        trv.insert('', 'end', values=value)
    status_bar['text'] = 'Loaded Successfully'
    time.sleep(1)
    status_bar['text'] = ''
    adaptive_audio = yt.streams.filter(adaptive=True, type="audio").first()
    adaptive_list += [(title[:40]+' -  Audio', adaptive_audio.abr, str(int(adaptive_audio.filesize / (1024 * 1024))),
                       adaptive_audio.mime_type, "yes", adaptive_audio.itag)]

    adaptive_videos = yt.streams.filter(adaptive=True)
    for adaptive_video in adaptive_videos:
        if adaptive_video.resolution is not None:
            adaptive_list += [(title[:45], str(adaptive_video.resolution) + " - " + str(adaptive_video.fps)
                               + " fps", str(int(adaptive_video.filesize / (1024 * 1024))) +
                               " MB", adaptive_video.mime_type, "na", adaptive_video.itag)]


def create_list():
    try:
        global yt
        v_type.set("Progressive")
        cmb['state'] = 'normal'
        path_button['state'] = 'normal'
        download_button['text'] = 'Download'
        youtube_url = entry1.get()
        yt = YouTube(youtube_url)
        threading.Thread(target=list_creation, daemon=True).start()

    except Exception as e:
        print(e)
        msg.showwarning('Error', 'Please enter a valid URL')
        cmb['state'] = 'disable'
        path_button['state'] = 'disable'
        status_bar['text'] = ''


# status for downloading - to do
def status():
    pass
    # to-do
    # threading.Thread(target=status, daemon=True).start()


def downld():
    pause_button['text'] = 'pause'
    global is_paused, is_cancelled, yt, name, count
    is_paused = False
    download_button['state'] = 'disabled'
    pause_button['state'] = 'normal'
    cancel_button['state'] = 'normal'

    try:
        tag = trv.item(trv.focus(), option='values')[-1]
        stream = yt.streams.get_by_itag(tag)
        filesi = stream.filesize
        status_bar['text'] = 'Downloading...'
        name += str(count)
        count += 1
        with open(f'{entry2.get()}/{name}.mp4', 'wb') as f:
            is_paused = is_cancelled = False
            stream = request.stream(stream.url)  # get an iterable stream
            downloaded = 0
            while True:

                if is_cancelled:
                    break
                if is_paused:
                    continue
                chunk = next(stream, None)  # get next chunk of video

                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = (downloaded / filesi) * 100
                    bar['value'] = percent
                    root.update()

                else:
                    # no more data
                    break
        if is_cancelled is False:
            status_bar['text'] = 'File Downloaded Successfully'
            time.sleep(1)
            status_bar['text'] = ''
        else:
            status_bar['text'] = 'Download Cancelled'
            time.sleep(1)
            status_bar['text'] = ''

        bar['value'] = 0
        pause_button['text'] = 'Pause'
    except Exception as e:
        if e == 'string index out of range':
            messagebox.showerror('Error', 'Please select one of the options to download')
            status_bar['text'] = ''
        else:
            messagebox.showerror('Error', 'Sorry! unable to download the file')
        print(e)

    download_button['state'] = 'normal'
    pause_button['state'] = 'disabled'
    cancel_button['state'] = 'disabled'


def start_download():

    threading.Thread(target=downld, daemon=True).start()


def pause_and_resume_download():
    global is_paused
    is_paused = not is_paused
    pause_button['text'] = 'Resume' if is_paused else 'Pause'


def cancel_download():
    global is_cancelled
    is_cancelled = True
    bar['value'] = 0


def clicked(event):
    status_bar.config(text='Loading...')


# GUI - Part
# root window
root = tk.Tk()
per = 0
root.title('Youtube-Video-Downloader')
root.geometry("700x400")
root.maxsize(700, 400)
root['background'] = 'grey75'
root['cursor']='heart'
style = ttk.Style()
style.theme_use('default')
style.configure('black.Horizontal.TProgressbar', background='light green')

# icon
# root.iconbitmap('picture.ico')

# tree
detailTree = LabelFrame(root, text="Details", bg='grey75', cursor='heart')
UrlLabel = LabelFrame(root, text="Url", bg='grey75', height=100, cursor='heart')

UrlLabel.pack(expand="Yes", fill="both", padx=3, pady=1)
detailTree.pack(fill="both", expand='yes', padx=3, pady=1)

bar = Progressbar(root, length=450, style='black.Horizontal.TProgressbar', mode='determinate')
bar.pack(expand="yes", padx=2, pady=10)


# combo-box
def change_value(*args):
    
    if v_type.get() == "Progressive":
        trv.delete(*trv.get_children())
        for value in progressive_list:
            trv.insert('', 'end', values=value)
    elif v_type.get() == "Adaptive":
        trv.delete(*trv.get_children())
        for value in adaptive_list:
            trv.insert('', 'end', values=value)
    root.update()


v_type = tk.StringVar()

# combo box -1
cmb = ttk.Combobox(detailTree, textvariable=v_type, values=["Progressive", "Adaptive"])
cmb.bind("<<ComboboxSelected>>", change_value)
v_type.set("Progressive")
cmb['state'] = 'disable'
cmb.pack(side=tk.TOP, fill='y')


# scroll bar will test later
scrollBar = tk.Scrollbar(detailTree, orient=tk.VERTICAL)

scrollBar.pack(side=tk.RIGHT, fill=tk.Y)


# tree_view

trv = Treeview(detailTree, columns=(1, 2, 3, 4, 5), show="headings", height="7", yscrollcommand=scrollBar.set,
               selectmode='browse')

trv.pack(side=tk.TOP, fill='both', pady=1)

# configure the scrollbar
scrollBar.config(command=trv.yview)

trv.heading(1, text="Name", anchor=tk.CENTER)
trv.heading(2, text="Quality", anchor=tk.CENTER)
trv.heading(3, text="Size", anchor=tk.CENTER)
trv.heading(4, text="Mime Type", anchor=tk.CENTER)
trv.heading(5, text="Audio", anchor=tk.CENTER)

trv.column(1, anchor=tk.CENTER, width=265)
trv.column(2, anchor=tk.CENTER, width=85)
trv.column(3, anchor=tk.CENTER, width=85)
trv.column(4, anchor=tk.CENTER, width=85)
trv.column(5, anchor=tk.CENTER, width=85)
trv.insert('', 'end', values=('NA', 'NA', 'NA', 'NA', 'NA'))
# LABELS

url_label = tk.Label(UrlLabel,
                     text="Youtube Url:",
                     bg='grey75',
                     justify=tk.RIGHT)
url_label.grid(row=0, column=0, padx=80, pady=5)

status_bar = tk.Label(root,
                      text="",
                      bg="grey75",
                      justify=tk.CENTER,

                      )
status_bar.pack(side=tk.BOTTOM, pady=2)

label3 = tk.Label(UrlLabel,
                  text="Directory:",
                  padx=10,
                  bg='grey75',
                  justify=tk.RIGHT)

label3.grid(row=1, column=0, padx=80, pady=5)

entry1 = tk.Entry(UrlLabel, justify=tk.CENTER, width=35, borderwidth=1, highlightthickness=2,
                  highlightbackground='grey50'
                  )
entry1.config(highlightcolor="light green")

entry2 = tk.Entry(UrlLabel, justify=tk.CENTER, width=35, borderwidth=1, highlightthickness=2,
                  highlightbackground='grey50'
                  )
entry2.config(highlightcolor="light green")
entry1.grid(row=0, column=1)
entry2.grid(row=1, column=1)


# Entry(root, textvariable=path, justify=CENTER, width=35, borderwidth=2,
#      font=('times new roman', 12, 'bold')).place(x=170, y=120)


search_button = tk.Button(UrlLabel, text="Search",
                          bg='light blue',
                          padx=11,
                          fg='black',
                          borderwidth=3,
                          relief=tk.GROOVE,
                          command=create_list,
                          )
search_button.bind("<Button-1>", clicked)

path_button = tk.Button(UrlLabel,
                        text="  Path  ",
                        bg='light blue',
                        fg='black',
                        padx=10,
                        relief=tk.GROOVE,
                        borderwidth=3,
                        command=directory,
                        )
ButtonLabel = tk.Frame(root,
                       bg='grey75',
                       )
ButtonLabel.pack()

download_button = tk.Button(ButtonLabel, text="Download",
                            bg='light blue',
                            fg='black',
                            padx=10,
                            pady=5,
                            relief=tk.GROOVE,
                            command=start_download,
                            borderwidth=3,
                            height='10',
                            )


pause_button = tk.Button(ButtonLabel, text="Pause",
                         bg='light blue',
                         fg='black',
                         padx=10,
                         pady=5,
                         height='10',
                         relief=tk.GROOVE,
                         borderwidth=3,
                         command=pause_and_resume_download
                         )

cancel_button = tk.Button(ButtonLabel, text="Cancel",
                          bg='light blue',
                          fg='black',
                          padx=10,
                          pady=5,
                          height='10',
                          relief=tk.GROOVE,
                          borderwidth=3,
                          command=cancel_download)


path_button['state'] = 'disable'
download_button['state'] = 'disable'
pause_button['state'] = 'disable'
cancel_button['state'] = 'disable'

search_button.grid(row=0, column=2, padx=80)
path_button.grid(row=1, column=2, padx=80)

pause_button.pack(side="left", padx=20, pady=10)
download_button.pack(side="left", padx=20, pady=10)
cancel_button.pack(side="left", padx=20, pady=10)

if __name__ == '__main__':
    root.mainloop()
