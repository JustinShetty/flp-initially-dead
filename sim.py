#!/usr/bin/env python3
"""Implements algorithm from section 4 of FLP."""
import dataclasses
import math
import queue
import random
import threading
import time
from typing import Dict, List, Set

DISPATCH_QUEUE = queue.Queue()
INBOUND_QUEUES: Dict[int, queue.Queue] = {}


@dataclasses.dataclass
class Stage1:
    """Message type for stage 1 of the algorithm."""

    to_pid: int
    from_pid: int

    def __repr__(self) -> str:
        return f'p{self.from_pid}->p{self.to_pid} Stage1(({self.from_pid}, ))'


@dataclasses.dataclass
class Stage2(Stage1):
    """Message type for stage 2 of the algorithm."""

    v: int
    known_pids: List[int]

    def __repr__(self) -> str:
        return f'p{self.from_pid}->p{self.to_pid} Stage2(({self.from_pid}, {self.v}, {self.known_pids}, ))'


def dispatcher(pids: Set[int]):
    """Infrastructure for passing messages."""
    global DISPATCH_QUEUE
    while True:
        if DISPATCH_QUEUE.empty():
            time.sleep(0.1)
            continue
        msg: Stage1 = DISPATCH_QUEUE.get()
        INBOUND_QUEUES[msg.to_pid].put(msg)


def protocol(all_pids: Set[int], my_pid: int, L: int):
    """Dictates behavior of each process."""

    my_val = random.randint(0, 100)

    # STAGE 1
    for to_pid in all_pids:
        msg = Stage1(to_pid, my_pid)
        print(msg)
        DISPATCH_QUEUE.put(msg)

    rxd_msgs: List[Stage1] = []
    while len(rxd_msgs) < L:
        msg: Stage1 = INBOUND_QUEUES[my_pid].get()
        if not isinstance(msg, Stage1):
            # defer Stage2 message
            INBOUND_QUEUES[my_pid].put(msg)
            continue
        rxd_msgs.append(msg)
    ancestors = {msg.from_pid for msg in rxd_msgs}

    # STAGE 2
    for to_pid in all_pids:
        msg = Stage2(to_pid, my_pid, my_val, list(ancestors))
        print(msg)
        DISPATCH_QUEUE.put(msg)

    known_pids = ancestors
    pids_rxd_from = set()
    all_proposed_values = {}
    while pids_rxd_from != known_pids:
        msg: Stage1 = INBOUND_QUEUES[my_pid].get()
        if not isinstance(msg, Stage2):
            continue
        print(f'p{my_pid} RXD {msg}')
        pids_rxd_from.add(msg.from_pid)
        known_pids.update([msg.from_pid] + msg.known_pids)
        all_proposed_values[msg.from_pid] = msg.v
    print(f'p{my_pid}: {all_proposed_values}')

    # TO-DO
    raise NotImplementedError('See TODO in README.md')
    initial_clique = pids_rxd_from

    # DECIDE
    initial_clique_vals = {
        v for pid, v in all_proposed_values.items() if pid in initial_clique
    }
    decided_value = min(list(initial_clique_vals))
    print(f'p{my_pid} DECIDED: {decided_value}')


def main():
    """Prepare and start 'processes'."""
    # Prepare constants
    N = 3
    T = math.ceil(N / 2) - 1
    L = math.ceil((N + 1) / 2)
    # num_dead = random.randint(0, T)
    num_dead = T
    dead_procs = random.sample(range(0, N), num_dead)
    all_pids = {pid for pid in range(N)}
    live_pids = {pid for pid in range(N) if pid not in dead_procs}
    print(f'N = {N}, L = {L}')
    print(live_pids)

    # Construct message queues
    for pid in range(N):
        INBOUND_QUEUES[pid] = queue.Queue()

    # Build threads
    dispatcher_th = threading.Thread(target=dispatcher, args=(live_pids,), daemon=True)
    node_ths: Dict[int, threading.Thread] = {}
    for pid in range(N):
        node_ths[pid] = threading.Thread(
            target=protocol,
            args=(
                all_pids,
                pid,
                L,
            ),
        )

    # Start threads
    dispatcher_th.start()
    for pid in live_pids:
        node_ths[pid].start()

    # Wait for nodes to finish
    for pid in live_pids:
        node_ths[pid].join()


if __name__ == '__main__':
    main()
