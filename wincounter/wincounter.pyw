import tkinter as tk
import datetime

class WinCounter(tk.Frame):
    def __init__(self, master=None, path='win_lose.txt'):
        super().__init__()
        self.master = master
        self.pack()
        self.init_model()
        self.init_file(path)
        self.create_widgets()
        self.update_widgets()

    def init_file(self,path):
        self.f = open(path, 'w', encoding='UTF-8')
        self.write_winlose()

    def init_model(self):
        self.winCount = 0
        self.loseCount = 0
        self.history = []
        self.history.append(("reset", datetime.datetime.now()))

    def create_widgets(self):
        btnFrame = tk.Frame(self)
        btnFrame.pack(side='top',
                      padx=10, pady=10
                      )

        self.incWinBtn = tk.Button(btnFrame,
                                   text='Win %d' % self.winCount,
                                   padx=20, pady=10,
                                   command=self.incWinCount )
        self.incWinBtn.pack(side='left')

        self.incLoseBtn = tk.Button(btnFrame,
                                    text='Lose %d' % self.loseCount,
                                    padx=20, pady=10,
                                    command=self.incLoseCount )
        self.incLoseBtn.pack(side='left')


        self.wpLbl = tk.Label(self, text='--- %')
        self.wpLbl.pack(side="bottom")


        self.undoBtn = tk.Button(self, text="UNDO", fg="blue",
                                 command=self.undo)
        self.undoBtn.pack(side="bottom")


        self.quitBtn = tk.Button(self, text="QUIT", fg="red",
                                 command=self.master.destroy)
        self.quitBtn.pack(side="bottom")

        self.timestampLbl = tk.Label(self, text='---')
        self.timestampLbl.pack(side="bottom")



    def update_widgets(self):
        """
        フォーム表示の更新
        """
        self.incWinBtn['text'] = ('Win %d' % self.winCount)
        self.incLoseBtn['text'] = ('Lose %d' % self.loseCount)
        total = self.winCount + self.loseCount
        rate  = self.winCount / total if self.winCount != 0 else 0.0
        self.wpLbl['text'] = u"%.5f %% (total %d)" % (rate * 100, total)

        if len(self.history) != 0:
            lastup = self.history[-1]
            self.timestampLbl['text'] = u"last update: %s %s" % (
                lastup[0], lastup[1].strftime("%H:%M:%S") )
        else:
            self.timestampLbl['text'] = "-----"


    def write_winlose(self):
        """
        OBSで取り込むことを目的としたテキストファイルの更新
        「n勝 m敗」
        """
        self.f.seek(0)
        self.f.write( u"%d勝 %d敗\n" % (self.winCount, self.loseCount))
        self.f.flush()
        print( u"%d勝 %d敗" % (self.winCount, self.loseCount))

    def incWinCount(self):
        self.winCount += 1
        self.history.append(('win++', datetime.datetime.now()))

        self.update_widgets()
        self.write_winlose()

    def incLoseCount(self):
        self.loseCount += 1
        self.history.append(('lose++', datetime.datetime.now()))

        self.update_widgets()
        self.write_winlose()


    def undo(self):
        try:
            lastAction = self.history.pop()
        except IndexError:
            self.init_model()
            self.update_widgets()
            self.write_winlose()

            return

        if lastAction[0] == 'win++':
            self.winCount -= 1
            self.update_widgets()
            self.write_winlose()

        elif lastAction[0] == 'lose++':
            self.loseCount -= 1
            self.update_widgets()
            self.write_winlose()

if __name__ == '__main__':
    root = tk.Tk()
    app = WinCounter(master=root, path='win_lose.txt')
    app.mainloop()
