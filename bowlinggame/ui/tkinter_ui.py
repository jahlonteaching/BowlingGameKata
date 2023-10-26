from tkinter import Tk, Frame, Label, Entry, messagebox
from tkinter.constants import TOP, X, SOLID, W, LEFT, END
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Button
from customtkinter import CTk

from bowlinggame.model.bowling import Game
from bowlinggame.model.bowling_errors import FramePinsExceededError, BowlingError


class BowlingFrame(Frame):
    def __init__(self, master=None, number="", is_total=False, **kwargs):
        super().__init__(master, **kwargs)
        self.is_total = is_total
        self.config(borderwidth=1, relief=SOLID)
        self.config(padx=0, pady=0, bg="white")

        if is_total:
            bg = "darkblue"
            fg = "white"
        else:
            bg = "white"
            fg = "black"

        self.frame_label = Label(self, text=number)
        self.frame_label.pack(side=TOP, fill=X)
        self.frame_label.config(borderwidth=1, relief=SOLID, width=5, height=1, bg=bg, fg=fg)
        self.frame_rolls = Label(self, text="")
        self.frame_rolls.pack(side=TOP, fill=X)
        self.frame_rolls.config(borderwidth=1, relief=SOLID, bg=bg, fg=fg)
        self.frame_score = Label(self, text="")
        self.frame_score.pack(side=TOP, fill=X)
        self.frame_score.config(borderwidth=1, relief=SOLID, bg=bg, fg=fg)

    def update_rolls(self, rolls):
        self.frame_rolls.config(text=str(rolls))

    def update_score(self, score):
        self.frame_score.config(text=str(score))

    def activate(self):
        self.frame_label.config(bg="lightgreen")

    def clear(self):
        if not self.is_total:
            self.frame_label.config(bg="white")
        self.frame_rolls.config(text="")
        self.frame_score.config(text="")

class BowlingApp(CTk):
    def __init__(self, game: Game):
        super().__init__()
        self.add_roll_entry = None
        self.title("Bowling Score Manager")
        self.geometry("600x150")
        self.config(padx=10, pady=10)
        self.resizable(False, False)
        self.frames: list[BowlingFrame] = []
        self.game: Game = game
        self.create_frames()
        self.create_action_panel()

    def create_frames(self):

        l_frame = Label(self, text="Frame:", width=7)
        l_frame.grid(row=0, column=0, padx=1)
        l_frame.config(foreground="blue", anchor=W, justify=LEFT)

        l_roll = Label(self, text="Rolls:", width=7)
        l_roll.grid(row=1, column=0, padx=1)
        l_roll.config(foreground="blue", anchor=W, justify=LEFT)

        l_score = Label(self, text="Score:", width=7)
        l_score.grid(row=2, column=0, padx=1)
        l_score.config(foreground="blue", anchor=W, justify=LEFT)

        for i in range(1, 13):
            if i < 11:
                frame = BowlingFrame(self, number=str(i))
            elif i == 11:
                frame = BowlingFrame(self, number="Extra")
            else:
                frame = BowlingFrame(self, number="Total", is_total=True)

            frame.grid(row=0, column=i, rowspan=3, padx=1)
            self.frames.append(frame)
        self.frames[0].activate()

    def create_action_panel(self):
        l_add_roll = Label(self, text="Add roll", width=7)
        l_add_roll.grid(row=3, column=0, padx=1, pady=30)
        l_add_roll.config(fg="blue", anchor=W, justify=LEFT)

        self.add_roll_entry = Entry(self, width=13, justify=LEFT)
        self.add_roll_entry.grid(row=3, column=1, columnspan=2, pady=30)
        self.add_roll_entry.bind("<Return>", lambda event: self.add_roll())

        # add button next to entry
        add_roll_button = Button(self, text="Add", width=5, command=self.add_roll)
        add_roll_button.grid(row=3, column=3, pady=30)

        # load from file button
        load_button = Button(self, text="Load from file", width=20, command=self.load_from_file)
        load_button.grid(row=3, column=8, columnspan=3, pady=30)

        # reset button next to load button
        reset_button = Button(self, text="Reset", command=self.reset)
        reset_button.grid(row=3, column=11, columnspan=2, pady=30)

        self.bind("<Visibility>", lambda event: self.focus_roll_entry())

    def focus_roll_entry(self):
        self.add_roll_entry.focus()
        self.unbind("<Visibility>")

    def reset(self):
        self.game.restart()
        for frame in self.frames:
            frame.clear()
        self.frames[0].activate()
        self.add_roll_entry.select_range(0, END)
        self.add_roll_entry.focus()

    def add_roll(self, roll=None):
        try:
            if roll is None:
                roll = int(self.add_roll_entry.get())

            if roll < 0:
                message = "Roll must be a positive integer value"
                messagebox.showwarning(title="Validation error", message=message, parent=self)
            else:
                self.game.roll(roll)
                self.frames[self.game.current_frame_index].activate()
                self.update_frames()
        except ValueError:
            message = "Roll must be an integer value"
            messagebox.showwarning(title="Validation error", message=message, parent=self)
        except BowlingError as err:
            messagebox.showwarning(title="Warning", message=str(err), parent=self)
        finally:
            self.add_roll_entry.select_range(0, END)
            self.add_roll_entry.focus()

    def update_total_frame(self):
        self.frames[-1].update_score(self.game.score())
        self.frames[-1].update_rolls(len(self.game))

    def load_from_file(self):
        file_types = (('Text files', '*.txt'),)
        filename = askopenfilename(
            title="Select a bowling score file",
            initialdir="./assets",
            filetypes=file_types
        )
        self.process_file(filename)

    def process_file(self, file_name):
        with open(file_name, mode='r') as file:
            line = file.readline()
            rolls = line.split()
            prev_roll = 0
            for roll in rolls:
                if roll == "X":
                    self.add_roll(10)
                    prev_roll = 10
                elif roll == "/":
                    self.add_roll(10 - prev_roll)
                else:
                    self.add_roll(int(roll))
                    prev_roll = int(roll)

    def update_frames(self):
        for i, frame in enumerate(self.game.frames):
            self.frames[i].update_rolls(str(frame))
            self.frames[i].update_score(frame.score())

            # Update the extra frame
            if i == 9:
                extra_roll_str = ""
                if frame.is_strike():
                    if len(frame.rolls) == 2:
                        extra_roll_str = f"{frame.rolls[1].pins}"

                    if frame.extra_roll is not None:
                        extra_roll_str += f" | {frame.extra_roll.pins}"
                else:
                    if frame.extra_roll is not None:
                        extra_roll_str = f"{frame.extra_roll.pins}"

                self.frames[i+1].update_rolls(extra_roll_str)

        self.update_total_frame()
