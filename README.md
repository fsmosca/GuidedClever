# GuidedClever
A chess engine adaptor that will select a move randomly from a multipv search info of the engine.

### Setup
* Install python 3.8 or later  
* Download the [repo](https://github.com/fsmosca/GuidedClever/archive/main.zip)  
* Install dependent modules  
  * pip install -r requirements.txt
  
### Prepare the engine
* Modify guidedclever.cfg to point where your engine is located.  
* There is guidedclever.bat, modify it and change the path of your python. It can then be installed as a uci engine under Arena GUI.

### Random Move from multipv
![board](https://i.imgur.com/YuRiK1X.png)
```
2021-01-03 03:13:02.352-->1:position startpos moves e2e4 c7c5 b1c3
2021-01-03 03:13:02.356-->1:go wtime 58032 btime 61000 winc 1000 binc 1000
2021-01-03 03:13:07.908<--1: num move  scores  d(i)   P(i)   F(i)
2021-01-03 03:13:07.914<--1:   1 e7e6   -0.19  0.00 0.1361 0.1361
2021-01-03 03:13:07.918<--1:   2 a7a6   -0.24 -0.05 0.1213 0.2426
2021-01-03 03:13:07.922<--1:   3 b8c6   -0.32 -0.13 0.1009 0.3231
2021-01-03 03:13:07.926<--1:   4 d7d6   -0.37 -0.18 0.0899 0.4020
2021-01-03 03:13:07.931<--1:   5 h7h6   -0.41 -0.22 0.0820 0.4761
2021-01-03 03:13:07.936<--1:   6 b7b6   -0.46 -0.27 0.0731 0.5403
2021-01-03 03:13:07.942<--1:   7 g7g6   -0.48 -0.29 0.0698 0.6068
2021-01-03 03:13:07.948<--1:   8 d8c7   -0.57 -0.38 0.0567 0.6504
2021-01-03 03:13:07.955<--1:   9 d8b6   -0.59 -0.40 0.0542 0.7021
2021-01-03 03:13:07.961<--1:  10 d8a5   -0.67 -0.48 0.0451 0.7381
2021-01-03 03:13:07.967<--1:  11 g8f6   -0.73 -0.54 0.0393 0.7716
2021-01-03 03:13:07.971<--1:  12 h7h5   -0.77 -0.58 0.0358 0.8039
2021-01-03 03:13:07.978<--1:  13 e7e5   -0.78 -0.59 0.0350 0.8381
2021-01-03 03:13:07.987<--1:  14 g8h6   -1.04 -0.85 0.0192 0.8415
2021-01-03 03:13:07.992<--1:  15 b8a6   -1.06 -0.87 0.0184 0.8591
2021-01-03 03:13:07.998<--1:  16 d7d5   -1.36 -1.17 0.0092 0.8591
2021-01-03 03:13:08.004<--1:  17 a7a5   -1.73 -1.54 0.0039 0.8577
2021-01-03 03:13:08.010<--1:  18 b7b5   -1.76 -1.57 0.0037 0.8612
2021-01-03 03:13:08.016<--1:  19 g7g5   -1.95 -1.76 0.0024 0.8623
2021-01-03 03:13:08.022<--1:  20 f7f6   -2.08 -1.89 0.0018 0.8635
2021-01-03 03:13:08.028<--1:  21 f7f5   -2.09 -1.90 0.0017 0.8651
2021-01-03 03:13:08.034<--1:  22 c5c4   -2.56 -2.37 0.0006 0.8646
2021-01-03 03:13:08.038<--1:info string movenumber 6 randomnumber 0.552 minf 0.1361 maxf 0.8651
2021-01-03 03:13:08.045<--1:info score cp -46
2021-01-03 03:13:08.052<--1:bestmove b7b6

```
