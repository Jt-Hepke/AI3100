#!/usr/bin/env python3
# controller.py — spawn the GUI game and an agent, and relay lines both ways.
# Uses text mode with line buffering (no Windows warnings).
#
# stdout of each process is relayed to the other (and mirrored here).
# stderr of each process is shown here only, so agents can debug with
#     print("...", file=sys.stderr)
# without sending anything to the game.

import subprocess as sp
import threading
import sys
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable or "python3"

def resolve(path):
    # Accept paths relative to the current directory, else look next to this script.
    if os.path.isabs(path) or os.path.exists(path):
        return path
    return os.path.join(HERE, path)

GAME = resolve(os.environ.get("MS_GAME", "minesweeper_io.py"))
AGENT = resolve(os.environ.get("MS_AGENT", "agent_template.py"))

def pump(src, dst, prefix):
    for line in iter(src.readline, ''):
        if not line:
            break
        # Mirror to our stdout for debugging
        sys.stdout.write(f"[{prefix}] {line}")
        sys.stdout.flush()
        try:
            dst.write(line)
            dst.flush()
        except Exception:
            break

def pump_err(src, prefix):
    for line in iter(src.readline, ''):
        sys.stderr.write(f"[{prefix}] {line}")
        sys.stderr.flush()

def spawn(script):
    # -u: unbuffered, so stderr lines show up as soon as they're printed
    return sp.Popen([PY, "-u", script], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE,
                    text=True, encoding='utf-8', bufsize=1)

def main():
    if not shutil.which(PY):
        print("Python interpreter not found.", file=sys.stderr); sys.exit(1)
    if not os.path.exists(GAME):
        print(f"Game script not found: {GAME}", file=sys.stderr); sys.exit(1)
    if not os.path.exists(AGENT):
        print(f"Agent script not found: {AGENT}", file=sys.stderr); sys.exit(1)

    game = spawn(GAME)
    agent = spawn(AGENT)

    for target, args in [
        (pump, (game.stdout, agent.stdin, "game")),
        (pump, (agent.stdout, game.stdin, "agent")),
        (pump_err, (game.stderr, "game stderr")),
        (pump_err, (agent.stderr, "agent stderr")),
    ]:
        threading.Thread(target=target, args=args, daemon=True).start()

    def report_agent_exit():
        rc = agent.wait()
        if game.poll() is None:
            print(f"[controller] agent exited (code {rc}); close the game window to quit.",
                  file=sys.stderr, flush=True)
    threading.Thread(target=report_agent_exit, daemon=True).start()

    try:
        game.wait()  # returns when the game window is closed
    except KeyboardInterrupt:
        pass
    finally:
        for p in (game, agent):
            try: p.terminate()
            except Exception: pass

if __name__ == "__main__":
    main()
