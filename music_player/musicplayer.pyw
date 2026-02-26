# -*- coding: utf-8-dos -*-

import tkinter as tk
from tkinter import filedialog
import shutil
import pathlib
from dataclasses import dataclass
from enum import Enum,  unique
import time
import pygame

#import csv

@dataclass(frozen=True)
class Config:
    BGM_DIR                    = u"bgm"
    BGM_DEFAULT_VOL            = 0.1
    SOUND_OUTPUT_DEVICE_NAME   = u"VoiceMeeter Input (VB-Audio VoiceMeeter VAIO)"
    DST_DIR                    = u"tmp"


@unique
class MusicPlayState(Enum):
    STOP    = 0
    RUNNING = 1
    PAUSED  = 2


class MusicPlayer(tk.Frame):
    def __init__(self, master=None):
        super().__init__()
        self.master = master
        self.pack()
        self.init_model()
        self.init_music_player()
        self.create_widgets()
        self.updateWidgets()


    def init_model(self):
        self.playlist=[]
        self.volume = Config.BGM_DEFAULT_VOL
        self.index=0
        self.state= MusicPlayState.STOP
        self.loopOne = False


    #-------------------------------------
    # view-controller
    #-------------------------------------

    def create_widgets(self):
        self.create_control_buttons()   # 操作ボタン（Play, Stop, Pause..etc)
        self.create_volume_control_widgets()
        self.creage_playlist_control_widgets()


    def create_control_buttons(self):
        '''操作ボタン（Play, Stop, Pause..etc)'''
        btnFrame=tk.Frame(self)
        btnFrame.pack(side='top', fill=tk.BOTH,
                      padx=10, pady=10)


        self.prevBtn = tk.Button(btnFrame, text="⏪", width=3, font=('',20),
                                 command=self.prevMusic)
        self.prevBtn.pack(side='left', fill=tk.X)


        self.stopBtn = tk.Button(btnFrame, text="⏹", width=3, font=('',20),
                                  command=self.stopMusic)
        self.stopBtn.pack(side='left', fill=tk.X)


        self.startBtn = tk.Button(btnFrame, text="▶", width=5, font=('',20),
                                  command=self.startMusic)
        self.startBtn.pack(side='left', fill=tk.X)

        self.nextBtn = tk.Button(btnFrame, text="⏩", width=3, font=('',20),
                                 command=self.nextMusic)
        self.nextBtn.pack(side='left', fill=tk.X)



    def create_volume_control_widgets(self):
        volFrame=tk.Frame(self)
        volFrame.pack(side='top', fill=tk.BOTH,
                      padx=10, pady=10)
        self.volDownBtn = tk.Button(volFrame, text="-", width=2,
                                    command=self.volumeDown)
        self.volDownBtn.pack(side='left')

        self.volUpBtn = tk.Button(volFrame, text="+", width=2,
                                  command=self.volumeUp)
        self.volUpBtn.pack(side='left')

        self.volLabel = tk.Message(volFrame, text='',width=1000)
        self.volLabel.pack(side='left', fill=tk.X)



    def creage_playlist_control_widgets(self):
        # プレイリスト
        musicBtnFrame =tk.Frame(self)
        musicBtnFrame.pack(side='top', fill=tk.BOTH)

        self.selectBgmBtn = tk.Button(musicBtnFrame, text="Select BGM", width=14, padx=2,
                                      command=self.selectBgmFile)
        self.selectBgmBtn.pack(side='left', fill=tk.X)

        self.clearBgmBtn = tk.Button(musicBtnFrame, text="Clear", width=8, padx=2,
                                     command=self.clearBgmList)
        self.clearBgmBtn.pack(side='left', fill=tk.X)

        self.loopOneBtn = tk.Button(musicBtnFrame, text="loop(1)", width=8, padx=2,
                                    command=self.toggleLoopOne)
        self.loopOneBtn.pack(side='left', fill=tk.X)


        # 選択されたプレイリストの表示
        self.msgLabel = tk.Message(self, text='',width=1000)
        self.msgLabel.pack(side='top', fill=tk.BOTH)



    def updateWidgets(self):
        self.updateStartButtonText()
        self.msgLabel['text']= '\n'.join(
            '%s %s' % ('*' if i == self.index else ' ', p.name)
            for (i, p)
            in zip(range(0,len(self.playlist)), self.playlist))


        volview= int(self.volume * 40.0)

        self.volLabel['text']= '%2d %s' % ( volview , '|' *  volview)

        self.loopOneBtn['bg'] = '#FF0000' if self.loopOne else self.selectBgmBtn.cget("bg") # defalt bg color を別のボタンからゲット


    def updateStartButtonText(self):
        if   self.state == MusicPlayState.STOP:    self.startBtn['text'] = "▶" # Play Mark
        elif self.state == MusicPlayState.RUNNING: self.startBtn['text'] = "⏸" # Pause Mark
        elif self.state == MusicPlayState.PAUSED:  self.startBtn['text'] = "⏯" # Resume Mark


    #-------------------------------------
    # button event
    #-------------------------------------

    def stopMusic(self):
        self.state = MusicPlayState.STOP
        self.index = 0

        self.fade_out_and_stop_bgm()
        self._tickCancel()
        self.updateWidgets()


    def startMusic(self):
        if self.state == MusicPlayState.STOP:
            if not self.playlist : return
            self.play_music()
            self._tick()

        elif self.state == MusicPlayState.RUNNING:
            # 再生中にリストをクリアされたケースがあるので、プレイリスト空判定はしない
            self.pause_music()

        elif self.state == MusicPlayState.PAUSED:
            # 再生中にリストをクリアされたケースがあるので、プレイリスト空判定はしない
            self.resume_music()

        self.updateWidgets()


    def prevMusic(self):
        if not self.playlist : return

        self.index -= 1
        if self.index < 0:
            self.index = len(self.playlist) -1

        if self.state == MusicPlayState.RUNNING:
            self.fade_out_and_stop_bgm()
            self.play_music()
        elif self.state == MusicPlayState.PAUSED:
            self.fade_out_and_stop_bgm()
            self.play_music()
            self.pause_music()

        self.updateWidgets()


    def nextMusic(self):
        if not self.playlist : return

        self.index += 1
        if self.index > len(self.playlist):
            self.index = 0

        if self.state == MusicPlayState.RUNNING:
            self.fade_out_and_stop_bgm()
            self.play_music()
        elif self.state == MusicPlayState.PAUSED:
            self.fade_out_and_stop_bgm()
            self.play_music()
            self.pause_music()

        self.updateWidgets()



    def toggleLoopOne(self):
        self.loopOne = not self.loopOne

        if self.state == MusicPlayState.RUNNING:
            self.fade_out_and_stop_bgm()
            self.play_music()
        elif self.state == MusicPlayState.PAUSED:
            self.fade_out_and_stop_bgm()
            self.play_music()
            self.pause_music()

        self.updateWidgets()


    def selectBgmFile(self):
        bgm_file_path = filedialog.askopenfilename(
            title="ファイルを選択",
            initialdir= pathlib.Path.cwd() / Config.BGM_DIR,
            filetypes=[
                ("mp3", "*.mp3"),
                ("All files", "*.*"),
            ]
        )
        self.playlist.append(pathlib.Path(bgm_file_path))
        self.updateWidgets()

    def clearBgmList(self):
        self.playlist = []
        self.updateWidgets()


    def volumeUp(self):
        self.volume = self.volume + 0.025
        if self.volume > 1.0:
            self.volume = 1.0

        pygame.mixer.music.set_volume(self.volume)
        self.updateWidgets()


    def volumeDown(self):
        self.volume = self.volume - 0.025
        if self.volume < 0.0:
            self.volume = 0.0

        pygame.mixer.music.set_volume(self.volume)
        self.updateWidgets()


    #-------------------------------------
    # sound
    #-------------------------------------
    def init_music_player(self):
        pygame.mixer.init(devicename=Config.SOUND_OUTPUT_DEVICE_NAME)
        pygame.mixer.music.set_volume(self.volume)


    def play_music(self):
        pygame.mixer.music.load(self.playlist[self.index])
        pygame.mixer.music.play(loops= -1 if self.loopOne else 0)
        self.state = MusicPlayState.RUNNING


    def pause_music(self):
        self.fade_out_and_pause_bgm()
        self.state = MusicPlayState.PAUSED


    def resume_music(self):
        self.fade_in_and_unpause_bgm()
        self.state = MusicPlayState.RUNNING

    def fade_in_and_start_bgm(self):
        ms=1000
        steps=10

        endv = pygame.mixer.music.get_volume()
        diff = endv - 0.0
        step = diff / steps

        pygame.mixer.music.set_volume(0)
        pygame.mixer.music.play(-1)

        for i in range(steps):
            pygame.mixer.music.set_volume(step*(i+1))
            pygame.time.delay(ms // steps)

    def fade_out_and_stop_bgm(self):
        ms=1000
        steps=10

        start = pygame.mixer.music.get_volume()
        diff = 0.0 - start
        step = diff / steps

        for i in range(steps):
            pygame.mixer.music.set_volume(start + step*(i+1))
            pygame.time.delay(ms // steps)


        pygame.mixer.music.stop()
        pygame.mixer.music.set_volume(start) # 次回再生用に戻しておく


    def fade_in_and_unpause_bgm(self):
        ms=1000
        steps=10

        endv = pygame.mixer.music.get_volume()
        diff = endv - 0.0
        step = diff / steps

        pygame.mixer.music.set_volume(0)
        pygame.mixer.music.unpause()

        for i in range(steps):
            pygame.mixer.music.set_volume(step*(i+1))
            pygame.time.delay(ms // steps)

    def fade_out_and_pause_bgm(self):
        ms=1000
        steps=10

        start = pygame.mixer.music.get_volume()
        diff = 0.0 - start
        step = diff / steps

        for i in range(steps):
            pygame.mixer.music.set_volume(start + step*(i+1))
            pygame.time.delay(ms // steps)


        pygame.mixer.music.pause()
        pygame.mixer.music.set_volume(start) # 次回再生用に戻しておく




    #------------------------------------------------------------
    ## tick-tack
    #------------------------------------------------------------
    def _tick(self):
        if self.state == MusicPlayState.RUNNING and not pygame.mixer.music.get_busy():
            self.index += 1
            if not (self.index < len(self.playlist)):
                self.index =0

                # プレイリストが消されている？
                if not self.playlist :
                    return

            print("Auto Change Music #%d %s" % (self.index, self.playlist[self.index].name))
            self.updateWidgets()
            time.sleep(0.5)
            pygame.mixer.music.load(self.playlist[self.index])
            pygame.mixer.music.play()


        # 次の0.05秒
        self.after_id = self.after(50, self._tick)

    def _tickCancel(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None



if __name__ == '__main__':
    root = tk.Tk()
    root.title(u"配信用音楽プレイヤー")
    app = MusicPlayer(master=root)
    app.mainloop()
