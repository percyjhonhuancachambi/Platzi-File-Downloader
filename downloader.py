import click
import subprocess
from utils import *

class Downloader:
    
    def __init__(self, external_downloader: str, quality: str):
        self.external_downloader = external_downloader
        self.quality = quality
        self.data_path  = 'data.json'
        self.data = {}

    def load_data(self):
        self.data = read_json(self.data_path)

    def m3u8_downloader(self, file_path, url, ext_dwl):
        """
        external_downloader: str <- 'yt-dlp', 'aria2'
        format_selection: str <- 'bv[height<=quality]+ba/b[height<=quality]'
        """
        if (self.quality == 'best'):
            self.format_selection = 'bv+ba/b'
        else:
            self.format_selection = f'bv[height<={self.quality}]+ba/b[height<={self.quality}]'
        
        if (ext_dwl =='yt-dlp'):
            command = ['yt-dlp', '-f', self.format_selection, '-o', f'{file_path}.%(ext)s', url]
        elif (ext_dwl =='aria2'):
            command = ['yt-dlp', '-f', self.format_selection, '-o', f'{file_path}.%(ext)s', '--external-downloader', 'aria2c', '--external-downloader-args', '-s 10 -x 10 -k 1M', url]
        subprocess.run(command, check=True)

    def dl_course(self):
        course_name = self.data['name']
        videos = self.data['videos']

        j, k = 1, len(videos)
        for video in videos:
            url = video['m3u8_url']
            section = video['section']
            title = video['title']
            dir_path = f'{course_name}/{section}'
            file_path = f'{dir_path}/{j}. {title}'
            check_path(dir_path)

            if(url is None):
                print(f'[{j} / {k}][reading] {title}')
            else:
                print(f'[{j} / {k}][streaming] {title}')
                self.m3u8_downloader(file_path = file_path, url=url, ext_dwl=self.external_downloader)
            
            j = j + 1
        
        check_path('downloads')
        copy_file('data.json', course_name)
        move_folder(course_name, 'downloads')


clients = ['yt-dlp', 'aria2']
qualities = ['360', '480', '720', '1080', 'best']
help_d = 'Select the external downloader (yt-dlp or aria2). Default: aria2. ' 
help_q = 'Select the video quality (360, 480, 720, 1080 or best). Default: best'

@click.command()
@click.option('-d', type=click.Choice(clients), default='aria2', prompt=False, help=help_d)
@click.option('-q', type=click.Choice(qualities), default='best', prompt=False, help=help_q)
def main(d, q):
    check_aria2()
    dl = Downloader(external_downloader=d, quality=q)
    dl.load_data()
    dl.dl_course()

if __name__ == "__main__":
    main()