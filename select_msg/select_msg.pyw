#!/usr/bin/env python
# -*- coding: utf-8-dos -*-

import tkinter as tk
import csv
import shutil
import pathlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    FRAME16_9_DIR       = u"枠部品"
    FRAME16_9_BASE_NAME = u"ゲーム・コメント枠(%s).png"
    FRAME4_3_DIR        = u"枠部品"
    FRAME4_3_BASE_NAME  = u"ゲームコメント枠43共用%s.png"
    BG_IMAGE_DIR        = u"背景"
    BG_IMAGE_BASE_NAME  = u"背景_%s.png"


class SelectMessage(tk.Frame):


    def __init__(self, master=None, csvpath="message.csv", outfilepath="message.txt"):
        super().__init__()
        self.master = master
        self.pack()
        self.init_model(csvpath, outfilepath)
        self.create_widgets()
        self.update_message_list()

    #-------------------------------------
    # view-controller
    #-------------------------------------

    def create_widgets(self):
        ctrlFrame = tk.Frame(self)
        ctrlFrame.pack(side='top',
                       padx=10, pady=10)


        # メッセージリスト（スクロールバー付き）
        scrolledListFrame = tk.Frame(ctrlFrame)
        scrolledListFrame.pack(side='left', fill=tk.BOTH)

        self.msgListBox = tk.Listbox(scrolledListFrame, width=100)
        self.msgListBox.bind("<<ListboxSelect>>", self.select_message)
        self.msgListBox.pack(side='left', fill=tk.BOTH)

        scrollbar = tk.Scrollbar(scrolledListFrame,
                                 orient = tk.VERTICAL,
                                 command = self.msgListBox.yview)
        scrollbar.pack(side='right', fill=tk.Y)

        self.msgListBox.config(yscrollcommand=scrollbar.set)


        # 操作ボタン（Accept, CSV Reload)
        btnFrame=tk.Frame(ctrlFrame)
        btnFrame.pack(side='left')

        self.acceptBtn = tk.Button(btnFrame, text="Accept!",
                                   command=self.accept_message)
        self.acceptBtn.pack(side='top', fill=tk.X)

        self.csvReloadBtn = tk.Button(btnFrame, text="CSV Reload",
                                      command=self.csv_reload)
        self.csvReloadBtn.pack(side='top', fill=tk.X)


        # 選択されたメッセージの表示
        self.msgLabel = tk.Message(self, text='',width=600)
        self.msgLabel.pack(side='left', fill=tk.BOTH)


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

    def init_model(self, csvpath, outfilepath):
        self.outpath = outfilepath
        self.csvpath = csvpath

        self.messages={}
        self.selected_message_key= ""

        self.load_message_csv()


    def load_message_csv(self):
        '''
        メッセージCSVの形式は (unique-game-name, console-type, bg-name, message-text)。
        これを以下のようにモデルとして保持する。
        self.messages[ unique-game-neme ] = (console-type, bg-name, message-text)
        '''
        with open(self.csvpath, newline='', encoding='UTF-8') as csvfile:
            rows = csv.reader(csvfile, delimiter=',')
            self.messages={}
            for row in rows:
                if len(row) == 4:
                    self.messages[row[0].strip()] = (row[1],row[2],row[3])

    def get_selected_console_type(self):
        values = self.messages.get(self.selected_message_key)
        return values[0] if values != None else None

    def get_selected_background_name(self):
        values = self.messages.get(self.selected_message_key)
        return values[1] if values != None else None

    def get_selected_message(self):
        values = self.messages.get(self.selected_message_key)
        return values[2] if values != None else None


    #-------------------------------------
    # event handler
    #-------------------------------------

    def select_message(self, ev):
        self.selected_message_key = self.msgListBox.get(self.msgListBox.curselection())
        self.msgLabel['text'] = self.get_selected_message()

    def accept_message(self):
        # message
        with open(self.outpath, 'w', encoding='UTF-8') as outf:
            outf.write( self.get_selected_message() )
            outf.flush()

        # console-frame
        self.accept_frame()

        # background-image
        self.accept_bg_image()

        print('accept message: "%s"' % self.get_selected_message())


    def accept_frame(self):
        self.accept_frame16_9()
        self.accept_frame4_3()

    def accept_frame16_9(self):
        src_path = pathlib.Path(Config.FRAME16_9_DIR) / (Config.FRAME16_9_BASE_NAME % self.get_selected_console_type())
        dst_path = Config.FRAME16_9_BASE_NAME % "SELECTED"

        if src_path.exists():
            print( "accept frame(16:9) <%s>: %s" % (self.get_selected_console_type(), src_path))
            shutil.copy2(src_path, dst_path)

    def accept_frame4_3(self):
        src_path = pathlib.Path(Config.FRAME4_3_DIR) / (Config.FRAME4_3_BASE_NAME % self.get_selected_console_type())
        dst_path = Config.FRAME4_3_BASE_NAME % "SELECTED"

        if src_path.exists():
            print( "accept frame(4:3) <%s>: %s" % (self.get_selected_console_type(), src_path))
            shutil.copy2(src_path, dst_path)

    def accept_bg_image(self):
        src_path = pathlib.Path(Config.BG_IMAGE_DIR) / (Config.BG_IMAGE_BASE_NAME % self.get_selected_background_name())
        dst_path = Config.BG_IMAGE_BASE_NAME % "SELECTED"

        if src_path.exists():
            print( "accept background <%s>: %s" % (self.get_selected_background_name(), src_path))
            shutil.copy2(src_path, dst_path)


    def csv_reload(self):
        self.load_message_csv()
        self.update_message_list()



if __name__ == '__main__':
    root = tk.Tk()
    root.title(u"メッセージセレクター")
    app = SelectMessage(master=root,
                        csvpath="message.csv",
                        outfilepath="message.txt")
    app.mainloop()
