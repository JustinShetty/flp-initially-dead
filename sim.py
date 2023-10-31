#!/usr/bin/env python3
"""Implements algorithm from section 4 of FLP."""
import dataclasses
import math
import queue
import random
import threading
import time
from typing import Dict, List, Set

import networkx as nx

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


def dispatcher():
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
        DISPATCH_QUEUE.put(msg)

    G = nx.DiGraph()
    G.add_node(my_pid)
    while len(G) < L:
        msg: Stage1 = INBOUND_QUEUES[my_pid].get()
        if not isinstance(msg, Stage1):
            # defer Stage2 message
            INBOUND_QUEUES[my_pid].put(msg)
            continue
        G.add_edge(msg.from_pid, msg.to_pid)

    # STAGE 2
    for to_pid in all_pids:
        msg = Stage2(to_pid, my_pid, my_val, list(G.nodes()))
        DISPATCH_QUEUE.put(msg)

    pids_rxd_from = set()
    all_proposed_values = {}
    while pids_rxd_from != set(G.nodes()):
        msg: Stage1 = INBOUND_QUEUES[my_pid].get()
        if not isinstance(msg, Stage2):
            continue
        pids_rxd_from.add(msg.from_pid)
        all_proposed_values[msg.from_pid] = msg.v
        # direct ancestor
        G.add_edge(msg.from_pid, my_pid)
        # ancestor's ancestors
        for known_pid in msg.known_pids:
            G.add_edge(known_pid, msg.from_pid)

    all_proposed_values = dict(sorted(all_proposed_values.items()))
    print(f'p{my_pid}: all_proposed_values = {all_proposed_values}')

    # In this case, the largest strongly-connected component is also the initial clique
    initial_clique = max(nx.strongly_connected_components(G), key=len)
    print(f'p{my_pid}: initial_clique: {initial_clique}')

    # DECIDE
    initial_clique_vals = {
        v for pid, v in all_proposed_values.items() if pid in initial_clique
    }
    decided_value = min(list(initial_clique_vals))
    print(f'p{my_pid} DECIDED: {decided_value}')


def main():
    """Prepare and start 'processes'."""
    # Prepare constants
    N = 10
    T = math.ceil(N / 2) - 1
    L = math.ceil((N + 1) / 2)
    num_dead = random.randint(0, T)
    dead_procs = random.sample(range(0, N), num_dead)
    all_pids = {pid for pid in range(N)}
    live_pids = {pid for pid in range(N) if pid not in dead_procs}
    print(f'N = {N}, L = {L}, T (max initially dead) = {T}, num_dead = {num_dead}')
    print(f'live_pids: {live_pids}')

    # Construct message queues
    for pid in range(N):
        INBOUND_QUEUES[pid] = queue.Queue()

    # Build threads
    dispatcher_th = threading.Thread(target=dispatcher, daemon=True)
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
