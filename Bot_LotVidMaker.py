#####################
#  Bot LotVidMaker  #
#####################

import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import os
import threading

class DragDropListbox(tk.Listbox):
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.SINGLE
        super().__init__(master, kw)
        self.drag_data = {'x': 0, 'y': 0, 'item': None}
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<ButtonRelease-1>', self.on_drop)

    def on_click(self, event):
        self.drag_data['item'] = self.nearest(event.y)
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def on_drag(self, event):
        if self.drag_data['item'] is not None:
            x = event.x_root - self.drag_data['x']
            y = event.y_root - self.drag_data['y']
            self.place(x=x, y=y, anchor=tk.NW)

    def on_drop(self, event):
        if self.drag_data['item'] is not None:
            self.drag_data['item'] = None

def combine_media(video_files, image_files, audio_files, output_folder_path, num_videos, progress_bar, prompt_text):
    if not video_files or not image_files or not audio_files or not output_folder_path or num_videos <= 0:
        prompt_text.insert(tk.END, "Erro: Preencha todos os campos corretamente.\n")
        return

    total_videos = len(video_files)
    total_images = len(image_files)
    total_audios = len(audio_files)

    if total_videos == 0 or total_images == 0 or total_audios == 0:
        prompt_text.insert(tk.END, "Erro: Deve conter pelo menos um arquivo em cada pasta.\n")
        return

    for i in range(num_videos):
        video_index = i % total_videos
        image_index = i % total_images
        audio_index = i % total_audios

        input_video = os.path.join(video_files[video_index][0], video_files[video_index][1])
        input_image = os.path.join(image_files[image_index][0], image_files[image_index][1])
        input_audio = os.path.join(audio_files[audio_index][0], audio_files[audio_index][1])

        output_file_path = os.path.join(output_folder_path, f"output_{i + 1}.mp4")
        command = f"ffmpeg -i \"{input_video}\" -loop 1 -i \"{input_image}\" -i \"{input_audio}\" -filter_complex \"[1][0]scale2ref=w='iw':h='-1'[wm][vid];[vid][wm]overlay=format=auto[out]\" -map \"[out]\" -map 2:a? -c:v libx264 -pix_fmt yuv420p -t 00:00:10.000 \"{output_file_path}\""

        progress_bar.start()
        prompt_text.insert(tk.END, f"Iniciando criação de videos {i + 1}/{num_videos}...\n")

        def run_command():
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True)
            for line in process.stdout:
                prompt_text.insert(tk.END, line)
                prompt_text.see(tk.END)
            process.wait()
            progress_bar.stop()
            prompt_text.insert(tk.END, f"Vídeo {i + 1}/{num_videos} criados com sucesso!\n")

        threading.Thread(target=run_command).start()

def open_root_folder():
    root_folder = os.getcwd()
    subprocess.Popen(f'explorer "{root_folder}"')

def select_folder(listbox, folder_type):
    folder_path = filedialog.askdirectory()
    listbox.delete(0, tk.END)
    files = sorted(os.listdir(folder_path))
    for file in files:
        listbox.insert(tk.END, (folder_path, file))

root = tk.Tk()
root.title("Bot LotVidMaker Criação de videos em lote")

video_label = tk.Label(root, text="Vídeo base:")
video_label.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)

video_listbox = DragDropListbox(root, width=50, height=5)
video_listbox.grid(row=0, column=1, padx=5, pady=5)

video_button = tk.Button(root, text="Selecionar", command=lambda: select_folder(video_listbox, "video"))
video_button.grid(row=0, column=2, padx=5, pady=5)

image_label = tk.Label(root, text="Imagem:")
image_label.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)

image_listbox = DragDropListbox(root, width=50, height=5)
image_listbox.grid(row=1, column=1, padx=5, pady=5)

image_button = tk.Button(root, text="Selecionar", command=lambda: select_folder(image_listbox, "image"))
image_button.grid(row=1, column=2, padx=5, pady=5)

audio_label = tk.Label(root, text="Áudio:")
audio_label.grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)

audio_listbox = DragDropListbox(root, width=50, height=5)
audio_listbox.grid(row=2, column=1, padx=5, pady=5)

audio_button = tk.Button(root, text="Selecionar", command=lambda: select_folder(audio_listbox, "audio"))
audio_button.grid(row=2, column=2, padx=5, pady=5)

## Ini cod - Pasta de saída
output_label = tk.Label(root, text="Pasta de Saída:")
output_label.grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)

output_folder_var = tk.StringVar()
output_folder_entry = tk.Entry(root, textvariable=output_folder_var, width=50)
output_folder_entry.grid(row=3, column=1, padx=5, pady=5)

def select_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder_var.set(folder_path)

output_folder_button = tk.Button(root, text="Selecionar", command=select_output_folder)
output_folder_button.grid(row=3, column=2, padx=5, pady=5)
## Fim cod - Pasta de saída

num_videos_label = tk.Label(root, text="Quant. de Vídeos:")
num_videos_label.grid(row=4, column=0, sticky=tk.E, padx=5, pady=5)

num_videos_var = tk.IntVar()
num_videos_entry = tk.Entry(root, textvariable=num_videos_var, width=10)
num_videos_entry.grid(row=4, column=1, padx=5, pady=5)

prompt_text = tk.Text(root, height=10, width=80)
prompt_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

combine_button = tk.Button(root, text="Criar Videos", command=lambda: combine_media(video_listbox.get(0, tk.END), image_listbox.get(0, tk.END), audio_listbox.get(0, tk.END), output_folder_var.get(), num_videos_var.get(), progress_bar, prompt_text))
combine_button.grid(row=7, column=0, sticky=tk.W, padx=10, pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
progress_bar.grid(row=7, column=1, columnspan=2, sticky=tk.W, padx=5, pady=10)

def clear_fields():
    video_listbox.delete(0, tk.END)
    image_listbox.delete(0, tk.END)
    audio_listbox.delete(0, tk.END)
    output_folder_var.set("")
    num_videos_var.set("")
clear_button = tk.Button(root, text="Limpar Campos", command=clear_fields)
clear_button.grid(row=4, column=2, sticky=tk.W, padx=10, pady=10)

root.mainloop()
