#!/usr/bin/env python3
# agent_template.py — minimal agent (replace with your solver).
"""
How the agent talks to the game (run everything with: python controller.py)

The game sends JSON lines on stdin. After every move you get one "state":

  {"type": "state", "rows": 9, "cols": 9, "status": "playing",
   "mines": 10, "flags": 0, "elapsed": 12,
   "cells": [{"r": 0, "c": 0, "revealed": true, "flagged": false,
              "adjacent": 1, "mine": null}, ...]}

  status    "ready" (no clicks yet) | "playing" | "won" | "lost"
  adjacent  number of neighboring mines if revealed, else null
  mine      null until the game ends
  rows and columns are numbered from 0

You may also get events, which you can usually ignore, e.g.
  {"type": "event", "event": "error", "message": "(3, 4) is already revealed"}
An invalid move gets an error event followed by the unchanged state.

Reply by printing ONE command per state (always flush=True):
  left r c     reveal cell (r, c)        first click is always safe
  right r c    flag / unflag cell (r, c)
  reset        start a new game
  setdiff i    0 = Beginner, 1 = Intermediate, 2 = Expert (starts a new game)
  dump         ask for the current state again

Anything printed to stdout goes to the game. Use debug(...) for your own output;
it shows up in the controller's console as "[agent stderr] ...".
"""

import sys, json, random, time

MOVE_DELAY = 3        # seconds between moves (lower it while testing)
WIN_PAUSE = 10        # seconds to leave a won board on screen before resetting
LOSS_PAUSE = 2        # seconds to leave a lost board on screen before resetting
STOP_AFTER_WIN = False  # True: stay on the winning board instead of starting a new game

def debug(*args):
    print(*args, file=sys.stderr, flush=True)

def neighbors(r, c, rows, cols):
    """Yield the (row, col) of each of the up-to-8 cells around (r, c)."""
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0: continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc

def make_grid(state):
    """grid[r][c] -> that cell's dict from the state message."""
    grid = [[None] * state["cols"] for _ in range(state["rows"])]
    for cell in state["cells"]:
        grid[cell["r"]][cell["c"]] = cell
    return grid

def choose_move(state):
    # Replace this with your solver: use make_grid() and neighbors() to reason
    # about which hidden cells are safe ("left") or must be mines ("right").
    cells = state["cells"]
    hidden = [(c["r"], c["c"]) for c in cells if not c["revealed"] and not c["flagged"]]
    if not hidden:
        return None
    r, c = random.choice(hidden)
    return f"left {r} {c}"

def main():
    stopped = False
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") == "event" and msg.get("event") == "error":
            debug("game rejected a command:", msg.get("message"))
            continue
        if msg.get("type") != "state":
            continue
        status = msg.get("status")
        if stopped:
            if status != "ready":
                continue  # sitting on the winning board until someone presses Reset
            stopped = False
        if status == "won":
            debug("WON!")
            if STOP_AFTER_WIN:
                stopped = True
                continue
            time.sleep(WIN_PAUSE)
            print("reset", flush=True)
            continue
        if status == "lost":
            time.sleep(LOSS_PAUSE)
            print("reset", flush=True)
            continue
        move = choose_move(msg)
        time.sleep(MOVE_DELAY)
        print(move if move else "dump", flush=True)

if __name__ == "__main__":
    main()
