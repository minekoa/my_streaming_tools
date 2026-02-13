#!/usr/bin/env python
# -*- coding: utf-8-dos -*-

import tkinter as tk
import shutil
import pathlib
from dataclasses import dataclass
from enum import Enum,  unique
import time
import pygame

#import csv

@dataclass(frozen=True)
class Config:
    ANIMEGIF_SRC_DIR           = u"画面小物"
    ANIMEGIF_READY_TO_EXERCISE = u"待ち_1-2_0.5.gif"
    ANIMEGIF_EXERCISING        = u"踏み台昇降_0.2_0.5.gif"
    ANIMEGIF_SELECTED          = u"踏み台昇降配信.gif"
    ANIMEGIF_GROGGY            = u"息切れ_0.5.gif"
    TIMER_FILE                 = u"踏み台タイマー.txt"
    TIMER_LIMIT_SECONDS        = 30 * 60 # 30分
    DST_DIR                    = u"tmp"
    SOUND_DIR                  = u"sound"
    TIMEUP_SOUND               = u"学校のチャイム.mp3"
    START_SOUND                = u"sei_ge_hoissuru_ren01.mp3"
    BGM_DIR                    = u"bgm"
    EXERCISE_MUSIC             = u"早起き体操.mp3"

@unique
class TimerState(Enum):
    STOP    = 0
    RUNNING = 1
    PAUSED  = 2


class FumidaiExerciseTool(tk.Frame):


    def __init__(self, master=None):
        super().__init__()
        self.master = master
        self.pack()
        self.init_model()
        self.create_widgets()
        self.init_sound()

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

#        self.readyBtn = tk.Button(btnFrame, text="Ready",
#                                  command=self.readyToExercise)
#        self.readyBtn.pack(side='top', fill=tk.X)


        self.startBtn = tk.Button(btnFrame, text="Start",
                                  font=("", 24),
                                  height=10, width=30,
#                                  height=20, width=60,
                                  command=self.startExercise)
        self.startBtn.pack(side='top', fill=tk.X)


        # 選択されたメッセージの表示
        self.msgLabel = tk.Message(self, text='',
                                   font=("", 40),
                                   width=600)
        self.msgLabel.pack(side='top', fill=tk.BOTH)


    def update_message_list(self):
        keys = sorted(self.messages.keys())
        self.msgListBox.delete(0,tk.END)
        for key in keys:
            self.msgListBox.insert(tk.END, key)
        self.msgLabel['text']  = self.get_selected_message()

        if self.selected_message_key != '':
            for i in range( len(keys) ):
                if keys[i] == self.selected_message_key:
                    self.msgListBox.select_set(i) # 選択位置
                    self.msgListBox.activate(i)   # カーソル位置
                    break


    #-------------------------------------
    # model
    #-------------------------------------

    def init_model(self):
        self.anime_init()
        self.timer_init()


    #-------------------------------------
    # button event
    #-------------------------------------


    def readyToExercise(self):
        '''
        踏み台昇降の準備をする
        - アニメGIFを準備モーションに差し替え
        - カウンター類をゼロにする
        '''

        self.anime_readyExercise()
        self.timer_stop()


    def startExercise(self):
        '''
        踏み台昇降の準備をする
        - アニメGIFを準備モーションに差し替え
        - カウンター類を開始する
        '''
        if self.timer_state == TimerState.STOP:
            self.play_start_whistle() # 同期的
            self.anime_startExercise()
            self.timer_start()

        elif self.timer_state == TimerState.RUNNING:
            self.anime_breakExercise()
            self.timer_pause()

        elif self.timer_state == TimerState.PAUSED:
            self.anime_startExercise()
            self.timer_resume()

        self.updateStartButtonText()

    def updateStartButtonText(self):
        if   self.timer_state == TimerState.STOP:    self.startBtn['text'] = "Start"
        elif self.timer_state == TimerState.RUNNING: self.startBtn['text'] = "Pause"
        elif self.timer_state == TimerState.PAUSED:  self.startBtn['text'] = "Resume"



    #------------------------------------------------------------
    ## ANIMATION
    #------------------------------------------------------------
    def anime_init(self):
        src_path = pathlib.Path(Config.ANIMEGIF_SRC_DIR) / Config.ANIMEGIF_READY_TO_EXERCISE
        dst_path = pathlib.Path(Config.DST_DIR) / Config.ANIMEGIF_SELECTED

        if src_path.exists():
            shutil.copy2(src_path, dst_path)

    def anime_readyExercise(self):
        src_path = pathlib.Path(Config.ANIMEGIF_SRC_DIR) / Config.ANIMEGIF_READY_TO_EXERCISE
        dst_path = pathlib.Path(Config.DST_DIR) / Config.ANIMEGIF_SELECTED

        if src_path.exists():
            shutil.copy2(src_path, dst_path)

    def anime_startExercise(self):
        src_path = pathlib.Path(Config.ANIMEGIF_SRC_DIR) / Config.ANIMEGIF_EXERCISING
        dst_path = pathlib.Path(Config.DST_DIR) / Config.ANIMEGIF_SELECTED

        if src_path.exists():
            shutil.copy2(src_path, dst_path)

    def anime_breakExercise(self):
        src_path = pathlib.Path(Config.ANIMEGIF_SRC_DIR) / Config.ANIMEGIF_GROGGY
        dst_path = pathlib.Path(Config.DST_DIR) / Config.ANIMEGIF_SELECTED

        if src_path.exists():
            shutil.copy2(src_path, dst_path)



    #------------------------------------------------------------
    ## TIMER
    #------------------------------------------------------------
    def timer_init(self):
        self.set_count = 0      # エクササイズのセットカウント

        self.start_time  = None
        self.paused_time = None
        self.timer_state = TimerState.STOP
        self.after_id = None

        self.timer_f = open( pathlib.Path(Config.DST_DIR) / (Config.TIMER_FILE),
                             'w', encoding='UTF-8')

    def timer_reset(self):
        self.timer_state = TimerState.STOP
        self.start_time  = None
        self.paused_time = None
        self.set_count   = 0

        self._tickCancel()


    def timer_start(self):
        if self.timer_state != TimerState.STOP:
            return

        self.timer_state = TimerState.RUNNING
        self.start_time  = time.perf_counter()
        self.paused_time = None
        self.set_count   += 1

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
        pygame.mixer.init()

        self.start_whistle = pygame.mixer.Sound(pathlib.Path(Config.SOUND_DIR) / Config.START_SOUND)
        self.start_whistle.set_volume(0.3)

        self.end_bell = pygame.mixer.Sound(pathlib.Path(Config.SOUND_DIR) / Config.TIMEUP_SOUND )
        self.end_bell.set_volume(0.3)

        pygame.mixer.music.load(pathlib.Path(Config.BGM_DIR) / Config.EXERCISE_MUSIC)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)


    def play_start_whistle(self):
        pygame.mixer.music.stop()


        time.sleep(0.5)
        self.start_whistle.play()

        time.sleep(self.start_whistle.get_length()+ 0.5)
        pygame.mixer.music.play(-1)





    def play_end_bell(self):
        original_vol = pygame.mixer.music.get_volume()

        pygame.mixer.music.set_volume(0.03)
        self.end_bell.play()

        time.sleep(self.end_bell.get_length())
        pygame.mixer.music.set_volume(original_vol)




    #------------------------------------------------------------
    ## tick-tack
    #------------------------------------------------------------

    def _tick(self):
        if not self.timer_state == TimerState.RUNNING:
            return

        elapsed = time.perf_counter() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        line = f"SET:{self.set_count:d} / {minutes:02d}:{seconds:02d}\n"


        self.timer_f.seek(0)
        self.timer_f.write(line)
        self.timer_f.flush()

        self.msgLabel["text"] = line


        if elapsed >= Config.TIMER_LIMIT_SECONDS:
            # 30分たったら自動停止
            self.timer_stop()
            self.anime_breakExercise()
            self.updateStartButtonText()

            self.play_end_bell() # 同期的なので注意
            self.anime_readyExercise()

        else:
            # 次の1秒
            self.after_id = self.after(1000, self._tick)


    def _tickCancel(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None



if __name__ == '__main__':
    root = tk.Tk()
    root.title(u"踏み台昇降配信ツール")
    app = FumidaiExerciseTool(master=root)
    app.mainloop()
