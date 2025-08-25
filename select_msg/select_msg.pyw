import tkinter as tk
import csv

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
        with open(self.csvpath, newline='', encoding='UTF-8') as csvfile:
            rows = csv.reader(csvfile, delimiter=',')
            self.messages={}
            for row in rows:
                if len(row) == 2:
                    self.messages[row[0].strip()] = row[1]

    def get_selected_message(self):
        return self.messages.get(self.selected_message_key)


    #-------------------------------------
    # event handler
    #-------------------------------------

    def select_message(self, ev):
        self.selected_message_key = self.msgListBox.get(self.msgListBox.curselection())
        self.msgLabel['text'] = self.get_selected_message()

    def accept_message(self):
        with open(self.outpath, 'w', encoding='UTF-8') as outf:
            outf.write( self.get_selected_message() )
            outf.flush()

        print('accept! "%s"' % self.get_selected_message() )

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
