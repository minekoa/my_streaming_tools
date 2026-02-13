#!/usr/bin/env python
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
    SOUND_DIR                  = u"sound"
    SOUND_BUZZER               = u"開演ブザー.mp3"
    SOUND_PROJECTOR            = u"eumig-s931-super8-projector-49153.mp3"
    BGM_DIR                    = u"bgm"
    EXERCISE_MUSIC             = u"早起き体操.mp3"
    DST_DIR                    = u"tmp"
    TIMER_FILE                 = u"経過時間.txt"
    COUNTDOWN_SECOND           = 30
    BG_DIR                     = u"背景"
    BG_LIGHT                   = u"背景_映画館公開中v2_light.png"
    BG_DARK                    = u"背景_映画館公開中v2_dark.png"
    BG_DST                     = u"背景_SELECTED.png"
    SCREEN_UPPER               = u"screen_upper.png"
    SCREEN_UNDER               = u"screen_under.png"
    SCREEN_SRC_DIR             = u"画面小物"
    SCREEN_DUMMY               = u"スクリーンライト_OFF.png"
    COUNTDOWN_ANIME_SRC        = u"movie_countdown_v2.gif"
    COUNTDOWN_ANIME_DMY        = u"movie_countdown_dummy.gif"
    COUNTDOWN_ANIME_DST        = u"movie_countdown.gif"

@unique
class TimerState(Enum):
    STOP    = 0
    RUNNING = 1
    PAUSED  = 2


class RoadShowTool(tk.Frame):

    def __init__(self, master=None):
        super().__init__()
        self.master = master
        self.pack()
        self.init_model()
        self.create_widgets()
        self.init_sound()

        self.update_bg_image()
        self.update_screen_light()

    #-------------------------------------
    # view-controller
    #-------------------------------------

    def create_widgets(self):
        ctrlFrame = tk.Frame(self)
        ctrlFrame.pack(side='top',
                       padx=10, pady=10)


        # 操作ボタン（Ready, Start, Pause)
        btnFrame=tk.Frame(ctrlFrame)
        btnFrame.pack(side='left')

        self.stopBtn = tk.Button(btnFrame, text="Select File",
                                  command=self.selectFile)
        self.stopBtn.pack(side='top', fill=tk.X)


        self.stopBtn = tk.Button(btnFrame, text="Stop",
                                  command=self.stopRoadShow)
        self.stopBtn.pack(side='top', fill=tk.X)


        self.startBtn = tk.Button(btnFrame, text="Start",
                                  command=self.startRoadShow)
        self.startBtn.pack(side='top', fill=tk.X)


        # 選択されたメッセージの表示
        self.msgLabel = tk.Message(self, text='',width=600)
        self.msgLabel.pack(side='top', fill=tk.BOTH)



    #-------------------------------------
    # model
    #-------------------------------------

    def init_model(self):
        self.timer_init()
        self.screen_file_path = ''

        self.init_countdown_anime()

    #-------------------------------------
    # button event
    #-------------------------------------
    def stopRoadShow(self):
        print( "STOP ROAD SHOW")
        self.timer_stop()

        line = f"\n"
        self.timer_f.seek(0)
        self.timer_f.write(line)
        self.timer_f.flush()


        self.updateWidgets()
        self.update_bg_image()
        self.update_screen_light()


    def startRoadShow(self):
        if self.timer_state == TimerState.STOP:
            self.start_buzzer.play()
            time.sleep(self.start_buzzer.get_length())

            self.projector_working.play(loops=-1)
            self.timer_start()

        elif self.timer_state == TimerState.RUNNING:
            self.timer_pause()

        elif self.timer_state == TimerState.PAUSED:
            self.timer_resume()

        self.updateWidgets()
        self.update_bg_image()
        self.update_screen_light()


    def selectFile(self):
        self.screen_file_path = filedialog.askopenfilename(
            title="ファイルを選択",
            filetypes=[
                ("PNG", "*.png"),
                ("All files", "*.*"),
            ]
        )
        print (self.screen_file_path)

        # update screen image
        dst_path_under = pathlib.Path(Config.DST_DIR) / Config.SCREEN_UNDER
        shutil.copy2(self.screen_file_path, dst_path_under)

        if not self.timer_state == TimerState.RUNNING:
            dst_path_upper = pathlib.Path(Config.DST_DIR) / Config.SCREEN_UPPER
            shutil.copy2(self.screen_file_path, dst_path_upper)

        self.updateWidgets()


    def updateWidgets(self):
        self.updateStartButtonText()
        self.msgLabel['text']= self.screen_file_path

    def updateStartButtonText(self):
        if   self.timer_state == TimerState.STOP:    self.startBtn['text'] = "Start"
        elif self.timer_state == TimerState.RUNNING: self.startBtn['text'] = "Pause"
        elif self.timer_state == TimerState.PAUSED:  self.startBtn['text'] = "Resume"


    #------------------------------------------------------------
    ## BG
    #------------------------------------------------------------

    def update_bg_image(self):
        src_path = pathlib.Path(Config.DST_DIR) / Config.SCREEN_UNDER

        if self.timer_state == TimerState.STOP:
            src_path = pathlib.Path(Config.BG_DIR) / Config.BG_LIGHT
        elif self.timer_state == TimerState.RUNNING:
            src_path = pathlib.Path(Config.BG_DIR) / Config.BG_DARK
        elif self.timer_state == TimerState.PAUSED:
            src_path = pathlib.Path(Config.BG_DIR) / Config.BG_LIGHT

        dst_path = pathlib.Path(Config.DST_DIR) / Config.BG_DST
        shutil.copy2(src_path, dst_path)



    def update_screen_light(self):
        '''
        スクリーンライトの画像（アニメーションpng）の差し替えで対応できなかったので、
        点滅光源png を 二枚の投影画像（配信のサムネイル）で挟み込み、
        上側を透明pngに差し替えることで実現する
        '''
        src_path       = pathlib.Path(Config.DST_DIR) / Config.SCREEN_UNDER
        if not src_path.exists():
            return

        dst_path_upper = pathlib.Path(Config.DST_DIR) / Config.SCREEN_UPPER
        blank_image    = pathlib.Path(Config.DST_DIR) / Config.SCREEN_UPPER

        if self.timer_state == TimerState.STOP:
            shutil.copy2(src_path, dst_path_upper)
        elif self.timer_state == TimerState.RUNNING:
            src_path = pathlib.Path(Config.SCREEN_SRC_DIR) / Config.SCREEN_DUMMY
            shutil.copy2(src_path, dst_path_upper)
        elif self.timer_state == TimerState.PAUSED:
            pass
#            shutil.copy2(src_path, dst_path_upper)




    def init_countdown_anime(self):
        self.is_enable_countdown_anime = False

        src_path = pathlib.Path(Config.SCREEN_SRC_DIR) / Config.COUNTDOWN_ANIME_DMY
        dst_path = pathlib.Path(Config.DST_DIR) / Config.COUNTDOWN_ANIME_DST
        shutil.copy2(src_path, dst_path)


    def enable_countdown_anime(self):
        if not self.is_enable_countdown_anime:
            self.is_enable_countdown_anime = True

            src_path = pathlib.Path(Config.SCREEN_SRC_DIR) / Config.COUNTDOWN_ANIME_SRC
            dst_path = pathlib.Path(Config.DST_DIR) / Config.COUNTDOWN_ANIME_DST
            shutil.copy2(src_path, dst_path)



    def disable_countdown_anime(self):
        if self.is_enable_countdown_anime:
            self.is_enable_countdown_anime = False

            src_path = pathlib.Path(Config.SCREEN_SRC_DIR) / Config.COUNTDOWN_ANIME_DMY
            dst_path = pathlib.Path(Config.DST_DIR) / Config.COUNTDOWN_ANIME_DST
            shutil.copy2(src_path, dst_path)

    #------------------------------------------------------------
    ## TIMER
    #------------------------------------------------------------
    def timer_init(self):
        self.is_in_count_down = False
        self.start_time  = None
        self.paused_time = None
        self.timer_state = TimerState.STOP
        self.after_id = None

        self.timer_f = open( pathlib.Path(Config.DST_DIR) / (Config.TIMER_FILE),
                             'w', encoding='UTF-8')

    def timer_reset(self):
        self.is_in_count_down = False
        self.timer_state = TimerState.STOP
        self.start_time  = None
        self.paused_time = None

        self._tickCancel()


    def timer_start(self):
        if self.timer_state != TimerState.STOP:
            return

        self.is_in_count_down = True
        self.timer_state = TimerState.RUNNING
        self.start_time  = time.perf_counter()
        self.paused_time = None

        self._tick()


    def timer_stop(self):
        if self.timer_state == TimerState.STOP:
            return

        self.timer_state = TimerState.STOP
        self.start_time  = None
        self.paused_time = None

        self._tickCancel()


    def timer_pause(self):
        if self.timer_state != TimerState.RUNNING:
            return

        self.timer_state = TimerState.PAUSED
        self.paused_time = time.perf_counter()

        self._tickCancel()


    def timer_resume(self):
        if self.timer_state != TimerState.PAUSED:
            return

        self.timer_state = TimerState.RUNNING
        self.start_time  = self.start_time + (time.perf_counter() - self.paused_time)
        self.paused_time = None

        self._tick()

    #-------------------------------------
    # sound
    #-------------------------------------
    def init_sound(self):
        pygame.mixer.init(devicename="VoiceMeeter Input (VB-Audio VoiceMeeter VAIO)")

        self.start_buzzer = pygame.mixer.Sound( str(pathlib.Path(Config.SOUND_DIR) / Config.SOUND_BUZZER))
        self.start_buzzer.set_volume(0.3)

        self.projector_working = pygame.mixer.Sound(str(pathlib.Path(Config.SOUND_DIR) / Config.SOUND_PROJECTOR) )
        self.projector_working.set_volume(0.3)

#        pygame.mixer.music.load(pathlib.Path(Config.BGM_DIR) / Config.EXERCISE_MUSIC)
#        pygame.mixer.music.set_volume(0.1)
#        pygame.mixer.music.play(-1)
#
#    def play_buzzer(self):
#        original_vol = pygame.mixer.music.get_volume()
#
#        pygame.mixer.music.set_volume(0.03)
#        self.end_bell.play()
#
#        time.sleep(self.end_bell.get_length())
#        pygame.mixer.music.set_volume(original_vol)


    #------------------------------------------------------------
    ## tick-tack
    #------------------------------------------------------------

    @staticmethod
    def to_hms(seconds: float):
        total = int(seconds)
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        return (h, m, s)

    def _tick(self):
        if not self.timer_state == TimerState.RUNNING:
            return

        elapsed = time.perf_counter() - self.start_time

        if self.is_in_count_down and elapsed >= (Config.COUNTDOWN_SECOND):
            self.is_in_count_down = False
            self.projector_working.stop()
            self.disable_countdown_anime()

        line = ""
        if self.is_in_count_down:
            h, m, s = self.to_hms(Config.COUNTDOWN_SECOND +1.0 - elapsed)
            line = f"あと {m:02d}:{s:02d}\n"

            if s == 10:
                self.enable_countdown_anime()
        else:
            h, m, s = self.to_hms(elapsed - (Config.COUNTDOWN_SECOND))
            line = f"{h:02d}:{m:02d}:{s:02d}\n"


        self.timer_f.seek(0)
        self.timer_f.write(line)
        self.timer_f.flush()


        # 次の0.05秒
        self.after_id = self.after(50, self._tick)


    def _tickCancel(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None





if __name__ == '__main__':
    root = tk.Tk()
    root.title(u"ロードショー配信ツール")
    app = RoadShowTool(master=root)
    app.mainloop()
