# Fault-Tolerant Consensus with Initially Dead Processes

Section 4 of FLP (linked below) describes an algorithm that can solve consensus in an asynchronous system with $n>2t$ (strict majority of processes are correct) as long as the failures occur before the algorithm runs.

`sim.py` attempts to implement this algorithm.

[Michael J. Fischer, Nancy A. Lynch, and Mike Paterson. 1985. Impossibility of
Distributed Consensus with One Faulty Process. J. ACM 32, 2 (1985), 374–382.
https://doi.org/10.1145/3149.214121](https://dl.acm.org/doi/10.1145/3149.214121)

## Setup
```
$ python -m venv venv
$ source venv/bin/activate
$ (venv) pip install -r requirements.txt
```

## Run
```
$ (venv) ./sim.py
```
