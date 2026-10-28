#!/usr/bin/env python3
# Minesweeper (Tkinter) with stdin/stdout bridge (NDJSON).
#
# Every move command (left/right/reset/setdiff/dump) gets exactly one "state"
# reply.  Invalid moves also get an {"event": "error"} message first.
# Set MS_SEED=<int> to get the same sequence of boards on every run.

import os
import sys
import time
import json
import queue
import random
import threading
import tkinter as tk

_seed = os.environ.get("MS_SEED")
RNG = random.Random(int(_seed)) if _seed else random.Random()

DIFFICULTIES = [
    ("Beginner", 9, 9, 10),
    ("Intermediate", 16, 16, 40),
    ("Expert", 16, 30, 99),
]

NUM_COLORS = {
    1: "#1976d2", 2: "#388e3c", 3: "#d32f2f", 4: "#512da8",
    5: "#f57c00", 6: "#00796b", 7: "#7b1fa2", 8: "#455a64",
}

class Cell:
    __slots__ = ("r","c","is_mine","is_revealed","is_flagged","adjacent","btn")
    def __init__(self, r, c):
        self.r=r; self.c=c
        self.is_mine=False; self.is_revealed=False; self.is_flagged=False
        self.adjacent=0; self.btn=None

def neighbors(r, c, rows, cols):
    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if dr==0 and dc==0: continue
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc

class Board:
    def __init__(self, rows, cols, mines):
        self.rows=rows; self.cols=cols; self.mines=mines
        self.grid=[Cell(r,c) for r in range(rows) for c in range(cols)]
        self.first_click_done=False
        self.start_time=None
        self.elapsed=0.0
        self.status="ready"  # ready|playing|won|lost
    def in_bounds(self,r,c): return 0 <= r < self.rows and 0 <= c < self.cols
    def idx(self,r,c): return r*self.cols+c
    def cell(self,r,c): return self.grid[self.idx(r,c)]
    def flags_count(self): return sum(1 for cell in self.grid if cell.is_flagged)
    def revealed_safe_count(self): return sum(1 for c in self.grid if c.is_revealed and not c.is_mine)
    def safe_total(self): return self.rows*self.cols - self.mines
    def place_mines_avoiding(self, avoid_r, avoid_c):
        total=self.rows*self.cols
        forbidden={self.idx(avoid_r,avoid_c)}
        for nr,nc in neighbors(avoid_r,avoid_c,self.rows,self.cols):
            forbidden.add(self.idx(nr,nc))
        placed=0
        while placed<self.mines:
            k=RNG.randrange(total)
            if k in forbidden: continue
            cell=self.grid[k]
            if not cell.is_mine:
                cell.is_mine=True; placed+=1
        # adjacents
        for r in range(self.rows):
            for c in range(self.cols):
                cell=self.cell(r,c)
                if cell.is_mine: cell.adjacent=0; continue
                cnt=0
                for nr,nc in neighbors(r,c,self.rows,self.cols):
                    if self.cell(nr,nc).is_mine: cnt+=1
                cell.adjacent=cnt
    def flood_reveal(self, r, c):
        stack=[(r,c)]
        while stack:
            r,c=stack.pop()
            cell=self.cell(r,c)
            if cell.is_revealed or cell.is_flagged: continue
            cell.is_revealed=True
            if cell.adjacent==0 and not cell.is_mine:
                for nr,nc in neighbors(r,c,self.rows,self.cols):
                    ncell=self.cell(nr,nc)
                    if not ncell.is_revealed and not ncell.is_flagged and not ncell.is_mine:
                        stack.append((nr,nc))

class MinesweeperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minesweeper — Tk IO")
        self.resizable(False, False)
        self.configure(bg="#f5f5f5")
        self.diff_var=tk.StringVar(value=DIFFICULTIES[0][0])
        self.board=None
        self.commands=queue.Queue()  # filled by the stdin thread, drained by Tk's main loop

        top=tk.Frame(self,bg="#f5f5f5"); top.pack(padx=10,pady=10,fill="x")
        tk.Label(top,text="Difficulty:",bg="#f5f5f5").pack(side="left")
        tk.OptionMenu(top,self.diff_var,*[d[0] for d in DIFFICULTIES],command=self._on_diff_change).pack(side="left",padx=(4,10))
        tk.Button(top,text="Reset (R)",command=self.reset_board).pack(side="left")
        self.flag_label=tk.Label(top,text="Mines: 0",bg="#f5f5f5",font=("Consolas",12)); self.flag_label.pack(side="right")
        self.time_label=tk.Label(top,text="Time: 0s",bg="#f5f5f5",font=("Consolas",12)); self.time_label.pack(side="right",padx=(0,10))

        self.board_frame=tk.Frame(self,bg="#e0e0e0",bd=1,relief="solid"); self.board_frame.pack(padx=10,pady=(0,10))

        self.bind("<Key-r>", lambda e: self.reset_board())
        self.bind("<Key-1>", lambda e: self._set_diff(0))
        self.bind("<Key-2>", lambda e: self._set_diff(1))
        self.bind("<Key-3>", lambda e: self._set_diff(2))
        self.bind("<Key-d>", lambda e: self.dump_board_state())

        self.reset_board()
        self._tick_timer()

        t=threading.Thread(target=self._stdin_listener,daemon=True)
        t.start()
        self._poll_commands()

    def _stdin_listener(self):
        # Tk isn't thread-safe, so this thread only queues lines; the main loop runs them.
        for line in sys.stdin:
            self.commands.put(line)

    def _poll_commands(self):
        while True:
            try: line=self.commands.get_nowait()
            except queue.Empty: break
            self._handle_command(line)
        self.after(20, self._poll_commands)

    def _reject(self, message):
        # Invalid move: say why, then resend the state so the agent isn't left waiting.
        self.emit_event("error", message=message)
        self.dump_board_state()

    def _handle_command(self, line):
        parts=line.strip().split()
        if not parts: return
        cmd=parts[0].lower()
        if cmd in ("left","right"):
            if len(parts)!=3:
                return self._reject(f"usage: {cmd} <row> <col>, got {line.strip()!r}")
            try:
                r=int(parts[1]); c=int(parts[2])
            except ValueError:
                return self._reject(f"row and col must be integers, got {line.strip()!r}")
            if not self.board.in_bounds(r,c):
                return self._reject(f"({r}, {c}) is off the board (rows 0-{self.board.rows-1}, cols 0-{self.board.cols-1})")
            err=(self.on_left if cmd=="left" else self.on_right)(r,c)
            if err: self._reject(err)
        elif cmd=="reset":
            self.reset_board()
        elif cmd=="setdiff":
            if len(parts)==2 and parts[1].isdigit() and int(parts[1])<len(DIFFICULTIES):
                self._set_diff(int(parts[1]))
            else:
                self._reject(f"usage: setdiff <0-{len(DIFFICULTIES)-1}>, got {line.strip()!r}")
        elif cmd=="dump":
            self.dump_board_state()
        else:
            # No state reply here: unknown lines (e.g. stray prints) must not trigger extra moves.
            self.emit_event("error", message=f"unknown command {line.strip()!r}")

    def dump_board_state(self):
        state={
            "type":"state",
            "rows": self.board.rows,
            "cols": self.board.cols,
            "status": self.board.status,
            "mines": self.board.mines,
            "flags": self.board.flags_count(),
            "elapsed": int(self.board.elapsed),
            "cells":[
                {
                    "r": cell.r,
                    "c": cell.c,
                    "revealed": cell.is_revealed,
                    "flagged": cell.is_flagged,
                    "adjacent": (cell.adjacent if cell.is_revealed else None),
                    "mine": (cell.is_mine if self.board.status in ("won","lost") else None),
                } for cell in self.board.grid
            ]
        }
        print(json.dumps(state), flush=True)

    def emit_event(self, evtype, **kwargs):
        msg={"type":"event","event":evtype}
        msg.update(kwargs)
        print(json.dumps(msg), flush=True)

    def _set_diff(self, idx):
        self.diff_var.set(DIFFICULTIES[idx][0]); self.reset_board()

    def _on_diff_change(self, _=None):
        self.reset_board()

    def _current_diff(self):
        name=self.diff_var.get()
        for d in DIFFICULTIES:
            if d[0]==name: return d
        return DIFFICULTIES[0]

    def reset_board(self):
        for w in self.board_frame.winfo_children(): w.destroy()
        name, rows, cols, mines = self._current_diff()
        self.board = Board(rows, cols, mines)
        self.flag_label.config(text=f"Mines: {self.board.mines}")
        self.time_label.config(text="Time: 0s")
        for r in range(rows):
            for c in range(cols):
                btn=tk.Button(self.board_frame,width=2,height=1,text="",relief="raised",bg="#fafafa",font=("Segoe UI",11,"bold"))
                btn.grid(row=r,column=c,padx=1,pady=1,sticky="nsew")
                cell=self.board.cell(r,c); cell.btn=btn
                btn.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_left(rr,cc))
                btn.bind("<Button-3>", lambda e, rr=r, cc=c: self.on_right(rr,cc))
                btn.bind("<Button-2>", lambda e, rr=r, cc=c: self.on_right(rr,cc))
        for r in range(rows): self.board_frame.grid_rowconfigure(r,weight=1)
        for c in range(cols): self.board_frame.grid_columnconfigure(c,weight=1)
        self.emit_event("reset", difficulty=name, rows=rows, cols=cols, mines=mines)
        self.dump_board_state()

    # on_left/on_right return an error message for a move that does nothing, else None.
    def on_left(self, r, c):
        if self.board.status in ("won","lost"): return f"game is over ({self.board.status}); send reset"
        cell=self.board.cell(r,c)
        if cell.is_revealed: return f"({r}, {c}) is already revealed"
        if cell.is_flagged: return f"({r}, {c}) is flagged; unflag it before revealing"
        if not self.board.first_click_done:
            self.board.place_mines_avoiding(r,c)
            self.board.first_click_done=True
            self.board.status="playing"
            self.board.start_time=time.time()
        if cell.is_mine:
            for c0 in self.board.grid:
                if c0.is_mine: self._paint_cell(c0, revealed=True, exploded=(c0 is cell))
            self.board.status="lost"
            self._update_mine_counter()
            self.emit_event("lose", r=r, c=c)
            self.dump_board_state()
            return
        self.board.flood_reveal(r,c)
        self._refresh_all_cells()
        if self.board.revealed_safe_count()>=self.board.safe_total():
            for c0 in self.board.grid:
                if c0.is_mine: self._paint_cell(c0, revealed=True, exploded=False)
            self.board.status="won"
            self._update_mine_counter()
            self.emit_event("win")
        else:
            self.emit_event("reveal", r=r, c=c)
        self.dump_board_state()

    def on_right(self, r, c):
        if self.board.status in ("won","lost"): return f"game is over ({self.board.status}); send reset"
        cell=self.board.cell(r,c)
        if cell.is_revealed: return f"({r}, {c}) is already revealed and can't be flagged"
        cell.is_flagged=not cell.is_flagged
        self._paint_cell(cell)
        self._update_mine_counter()
        self.emit_event("flag" if cell.is_flagged else "unflag", r=r, c=c)
        self.dump_board_state()

    def _paint_cell(self, cell, revealed=None, exploded=False):
        if revealed is None: revealed=cell.is_revealed
        btn=cell.btn
        if revealed:
            btn.config(relief="sunken", bg="#e0e0e0")
            if cell.is_mine:
                btn.config(text="💣", fg="#d32f2f", bg="#ffcdd2" if exploded else "#ffe0b2")
            else:
                if cell.adjacent>0:
                    btn.config(text=str(cell.adjacent), fg=NUM_COLORS.get(cell.adjacent, "#424242"))
                else:
                    btn.config(text="", fg="#424242")
        else:
            if cell.is_flagged:
                btn.config(text="🚩", relief="raised", bg="#fff8e1", fg="#e65100")
            else:
                btn.config(text="", relief="raised", bg="#fafafa")

    def _refresh_all_cells(self):
        for cell in self.board.grid: self._paint_cell(cell, revealed=cell.is_revealed)

    def _update_mine_counter(self):
        left=max(0, self.board.mines - self.board.flags_count())
        self.flag_label.config(text=f"Mines: {left}")

    def _tick_timer(self):
        if self.board and self.board.status=="playing" and self.board.start_time is not None:
            self.board.elapsed=time.time() - self.board.start_time
            self.time_label.config(text=f"Time: {int(self.board.elapsed)}s")
        self.after(200, self._tick_timer)

def main():
    app=MinesweeperApp()
    app.update_idletasks()
    w=app.board.cols*30+40; h=app.board.rows*30+110
    w=max(w, 360); h=max(h, 250)
    try:
        app.geometry(f"{w}x{h}")
    except Exception:
        pass
    app.mainloop()

if __name__=="__main__":
    main()
