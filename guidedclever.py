#!/usr/bin/env python


"""
GuidedClever.py

Setup:
  Install python 3.8 or newer


Requirements:
  See requirements.txt
"""


__version__ = 'v1.0.0'
__author__ = 'Ajedrecista and Ferdy'
__script_name__ = 'GuidedClever'


import queue
import sys
import subprocess
import threading
import configparser
import logging
from pathlib import Path
import random

from chess.engine import Mate
import pandas as pd


class ChessAI:
    def __init__(self, engine_file):
        self.engine_file = engine_file
        self.__engine__ = self.__engine_process__()
        self.option = self.engine_options()
        self.engine_name = self.name()
        self.K = 1.0

    def __engine_process__(self):
        return subprocess.Popen(self.engine_file, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True, bufsize=1,
                                creationflags=subprocess.CREATE_NO_WINDOW)

    def engine_options(self):
        engine_option = []
        self.send('uci')
        for eline in iter(self.__engine__.stdout.readline, ''):
            line = eline.strip()
            if line.startswith('option name '):
                sp = line.split('option name ')[1]
                name = sp.split('type')[0].strip()
                engine_option.append(name)
            if 'uciok' in line:
                break

        return engine_option

    def name(self):
        idname = None
        self.send('uci')
        for eline in iter(self.__engine__.stdout.readline, ''):
            line = eline.strip()
            if 'id name' in line:
                idname = line.split('id name ')[1]
            if 'uciok' in line:
                break

        return idname

    def author(self):
        idauthor = None
        self.send('uci')
        for eline in iter(self.__engine__.stdout.readline, ''):
            line = eline.strip()
            if 'id author' in line:
                idauthor = line.split('id author ')[1]
            if 'uciok' in line:
                break

        return idauthor

    def uci(self):
        is_show_lines = False
        self.send('uci')
        for eline in iter(self.__engine__.stdout.readline, ''):
            if is_show_lines:
                self.console_print(eline)
            if 'uciok' in eline:
                break

    def ucinewgame(self):
        self.send('ucinewgame')

    def isready(self):
        self.send('isready')
        for eline in iter(self.__engine__.stdout.readline, ''):
            self.console_print(eline)
            if 'readyok' in eline:
                logging.info(f'{self.engine_name} sent readyok')
                break

    def position(self, command):
        self.send(command)

    def stop(self):
        self.send('stop')

        for eline in iter(self.__engine__.stdout.readline, ''):
            self.console_print(eline)
            if 'bestmove ' in eline:
                break

    def ponderhit(self, thr_event):
        self.send('ponderhit')

        for eline in iter(self.__engine__.stdout.readline, ''):
            self.console_print(eline)
            if 'bestmove ' in eline:
                break

    def go(self, command):
        self.send(command)

        d = {}

        for eline in iter(self.__engine__.stdout.readline, ''):
            line = eline.rstrip()

            if 'depth' in line and 'score' in line and 'multipv' in line:
                if 'score cp' in line:
                    score = int(line.split('score cp')[1].split()[0])
                elif 'score mate' in line:
                    mate_num = int(line.split('score mate')[1].split()[0])

                    # Todo: Create a formula to convert mate score to cp score.
                    score = Mate(mate_num).score(mate_score=32000)
                else:
                    print('info string missing score, use 0.')
                    sys.stdout.flush()
                    score = 0

                mpv = int(line.split('multipv')[1].split()[0])
                pv = line.split(' pv ')[1].split()[0]
                d.update({mpv: [pv, score]})

            if 'bestmove ' in eline:
                # Returns a move based on prng.
                K = self.K
                logging.info(f'K = {self.K}')

                top_score = d[1][1]/100

                cnt, num, moves, scores = 0, [], [], []
                for k, v in d.items():
                    cnt += 1
                    num.append(cnt)
                    moves.append(v[0])
                    scores.append(round(v[1]/100, 2))

                d = []
                for i, s in enumerate(scores):
                    d.append(round(s - top_score, 2))

                p = proba(d, K)
                f = F(p)

                data = {'num': num, 'move': moves, 'scores': scores, 'd(i)': d, 'P(i)': p, 'F(i)': f}
                df = pd.DataFrame(data)

                print(df.to_string(index=False))
                sys.stdout.flush()

                move_num, rn = search_move_num(d, f)
                bestmove = moves[move_num-1]
                bestscore = scores[move_num-1]

                print(f'info string movenumber {move_num} randomnumber {rn} minf {min(f)} maxf {max(f)}')
                print(f'info score cp {int(bestscore*100)}')
                sys.stdout.flush()

                print(f'bestmove {bestmove}')
                sys.stdout.flush()

                break

    def go_infinite(self, command, thr_event):
        self.send(command)

        while not thr_event.isSet():
            for eline in iter(self.__engine__.stdout.readline, ''):
                if thr_event.wait(0.01):
                    break
                self.console_print(eline)

    def go_ponder(self, command, thr_event):
        self.send(command)

        while not thr_event.is_set():
            for eline in iter(self.__engine__.stdout.readline, ''):
                if thr_event.wait(0.01):
                    break
                self.console_print(eline)

    def console_print(self, msg):
        print(f'{msg.rstrip()}')
        sys.stdout.flush()

    def setoption(self, command):
        self.send(command)

    def quit(self):
        self.send('quit')
        logging.info(f'{self.engine_name} received quit.')

    def send(self, command):
        self.__engine__.stdin.write(f'{command}\n')


def proba(d, K=1.0):
    """
    d is a list of float.

    Prob(i) = 10^[d(i)/K] / SUM{10^[d(i)/K]}
    """
    prob = []

    sumv = 0
    for i in d:
        sumv += 10 ** (i / K)

    for i in d:
        value = (10 ** (i / K)) / sumv
        prob.append(round(value, 4))

    return prob


def F(p):
    """
    p is a list of float.

    F(i) = Prob(i) + SUM[Prob(j)], with j < i
    """
    res = []

    cumsum = 0

    for i, v in enumerate(p):
        cumsum += v if i > 0 else 0
        value = v + cumsum
        res.append(round(value, 4))

    return res


def get_config_info(cfg_file):
    """
    Read cfg file and return engine file path and logging.
    """
    eng, islog = None, False

    parser = configparser.ConfigParser()
    parser.read(cfg_file)
    for section_name in parser.sections():
        sname = section_name.lower()
        for name, value in parser.items(section_name):
            if sname == 'engine':
                if name == 'enginefile':
                    eng = value
                    print(f'info string set {name} to {value}')
                elif name.lower() == 'log':
                    islog = value
                    if islog.lower() == 'true' or islog == 1:
                        islog = True

    return eng, islog


def engine_loop(engine, name, thr_event, que):
    while True:
        command = que.get()

        if command.startswith('position '):
            engine.position(command)
            logging.info(f'{name} received {command}')

        elif command == 'go infinite':
            engine.go_infinite(command, thr_event)
            logging.info(f'{name} received {command}')

        elif command.startswith('go ponder'):
            engine.go_ponder(command, thr_event)
            logging.info(f'{name} received {command}')

        elif command.startswith('go '):
            engine.go(command)
            logging.info(f'{name} received {command}')

        elif command == 'stop':
            engine.stop()
            logging.info(f'{name} received {command}')

        elif command == 'ponderhit':
            engine.ponderhit(thr_event)
            logging.info(f'{name} received {command}')

        elif command == 'isready':
            engine.isready()
            logging.info(f'{name} received {command}')

        elif 'setoption ' in command:
            optname = command.split()[2]
            optvalue = command.split()[4]
            if optname.lower() == 'k':
                engine.K = float(optvalue)
            else:
                engine.setoption(command)
            logging.info(f'{name} received {command}')

        elif command == 'uci':
            engine.uci()
            logging.info(f'{name} received {command}')

        elif command == 'ucinewgame':
            engine.ucinewgame()
            logging.info(f'{name} received {command}')

        elif command == 'quit':
            break


def search_move_num(d, f):
    """
    Search the move number based on generated random number.
    """
    move_num = 0
    max_tries = 10
    tries = 0

    # Don't return unless we get the move number.
    while True:
        tries += 1

        # Generate random number between the min and max of f.
        prng = random.uniform(min(f), max(f))
        prng = round(prng, 4)

        found = False
        for i in range(len(d)):
            if i == len(d) - 1:
                break

            low = f[i]
            high = f[i+1]

            if low >= prng >= high or low <= prng <= high:
                move_num = i
                found = True
                break

        if found:
            break

        print('info string failed to get move num, generate random number again...')

        if tries >= max_tries:
            break

    return move_num + 1, prng


def main():
    sys.stdin.flush()
    cfg_file = 'guidedclever.cfg'

    # Check cfg file.
    config_file = Path(cfg_file)
    if not config_file.is_file():
        print(f'{cfg_file} file is required to run {__script_name__}! Exiting ...')
        sys.stdin.flush()
        sys.exit(1)

    # Get engine files and switch conditions from config file.
    engine_file, is_logging = get_config_info(cfg_file)

    if is_logging:
        logging.basicConfig(
            filename='guidedclever.log', filemode='w', level=logging.DEBUG,
            format='%(asctime)s :: %(levelname)s :: %(message)s')

    # Check engine files based on cfg file
    if engine_file is None:
        logging.info('engine is missing.')
        sys.exit(1)

    engine = ChessAI(engine_file)
    engname = engine.name()

    print(f'info string {__script_name__} {__version__} powered by {engname}')
    sys.stdin.flush()

    # Set engine options.
    parser = configparser.ConfigParser()
    parser.read(cfg_file)
    for section_name in parser.sections():
        sname = section_name.lower()
        for name, value in parser.items(section_name):
            if sname == 'engine':
                if name in [opt.lower() for opt in engine.option]:
                    engine.setoption(f'setoption name {name} value {value}')
                    print(f'info string setoption name {name} value {value}')
                    sys.stdin.flush()

    que = queue.Queue()
    thr_event = threading.Event()
    thr = threading.Thread(target=engine_loop, args=(
        engine, engname, thr_event, que), daemon=True)
    thr.start()

    while True:
        command = input('').strip()

        if command == 'uci':
            print(f'id name {__script_name__} {__version__}')
            print(f'id author {__author__}')
            print('option name K type string default 1.0 min 0.0 max 1000.0')
            print('uciok')
            sys.stdin.flush()

        elif command == 'ucinewgame':
            thr_event.clear()
            que.put(command)

        elif command == 'isready':
            thr_event.clear()
            que.put(command)

        elif command == 'quit':
            que.put(command)
            break

        elif command == 'ponderhit':
            thr_event.set()
            que.put(command)

        elif command.startswith('position '):
            que.put(command)

        elif command == 'go infinite':
            thr_event.clear()
            que.put(command)

        elif command.startswith('go ponder'):
            thr_event.clear()
            que.put(command)

        elif command.startswith('go '):
            thr_event.clear()
            que.put(command)

        elif 'stop' in command:
            thr_event.set()
            que.put(command)

        elif 'setoption ' in command:
            que.put(command)

        else:
            print(f'info string unknown command {command}')
            sys.stdout.flush()

    engine.quit()


if __name__ == "__main__":
    main()
