
"""
Dining Philosophers (4 philosophers) - Monitor-based solution.
Prints events in the VS Code terminal and generates an HTML replay.
"""

import argparse
import os
import random
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))

from tracelog import Trace, write_html

N = 4
trace = Trace()
START_TIME = time.monotonic()


def log_event(actor, message):
    elapsed = time.monotonic() - START_TIME
    print(f"{elapsed:.3f} {actor} -> {message}", flush=True)


class DiningMonitor:
    def __init__(self):
        self._lock = threading.Lock()
        self._state = ["thinking"] * N
        self._can_eat = [
            threading.Condition(self._lock) for _ in range(N)
        ]

    def _left(self, i):
        return (i - 1) % N

    def _right(self, i):
        return (i + 1) % N

    def _try_to_eat(self, i):
        """Caller must hold the monitor lock."""

        if (
            self._state[i] == "hungry"
            and self._state[self._left(i)] != "eating"
            and self._state[self._right(i)] != "eating"
        ):
            self._state[i] = "eating"

            log_event(f"P{i}", "acquiring")
            trace.log(f"P{i}", "state", state="acquiring")

            log_event(f"P{i}", f"fork {i} taken")
            trace.log(f"P{i}", "fork", fork=i, owner=i)

            right_fork = (i + 1) % N
            log_event(f"P{i}", f"fork {right_fork} taken")
            trace.log(f"P{i}", "fork", fork=right_fork, owner=i)

            log_event(f"P{i}", "eating")
            trace.log(f"P{i}", "state", state="eating")

            self._can_eat[i].notify()

    def pickup(self, i):
        with self._lock:
            self._state[i] = "hungry"

            log_event(f"P{i}", "hungry")
            trace.log(f"P{i}", "state", state="hungry")

            self._try_to_eat(i)

            while self._state[i] != "eating":
                log_event(f"P{i}", "waiting for both forks")
                self._can_eat[i].wait()

    def putdown(self, i):
        with self._lock:
            log_event(f"P{i}", "releasing")
            trace.log(f"P{i}", "state", state="releasing")

            log_event(f"P{i}", f"fork {i} released")
            trace.log(f"P{i}", "fork", fork=i, owner=None)

            right_fork = (i + 1) % N
            log_event(f"P{i}", f"fork {right_fork} released")
            trace.log(f"P{i}", "fork", fork=right_fork, owner=None)

            self._state[i] = "thinking"

            log_event(f"P{i}", "thinking")
            trace.log(f"P{i}", "state", state="thinking")

            # Check whether either neighbour can now eat.
            self._try_to_eat(self._left(i))
            self._try_to_eat(self._right(i))


monitor = DiningMonitor()
meals_eaten = [0] * N


def pause(max_delay):
    time.sleep(random.uniform(0.2, 1.0) * max_delay)


def philosopher(i, meals, delay):
    for meal in range(meals):
        pause(delay)

        monitor.pickup(i)

        meals_eaten[i] += 1
        log_event(f"P{i}", f"eating meal {meals_eaten[i]}")
        pause(delay)

        monitor.putdown(i)

    log_event(f"P{i}", "done")
    trace.log(f"P{i}", "state", state="done")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--meals", type=int, default=3)
    parser.add_argument("--delay", type=float, default=0.3)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument(
        "--out",
        default=os.path.join(
            HERE,
            "..",
            "..",
            "generated_html",
            "dining_philosophers_monitor.html"
        )
    )

    args = parser.parse_args()

    if args.meals < 0 or args.delay < 0:
        parser.error("--meals and --delay must be non-negative")

    random.seed(args.seed)

    print("\nDining Philosophers - Monitor Solution")
    print("=" * 48)
    print("Starting simulation...\n")

    threads = [
        threading.Thread(
            target=philosopher,
            args=(i, args.meals, args.delay)
        )
        for i in range(N)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("\n" + "=" * 48)
    print("Meals eaten per philosopher:", meals_eaten)
    print("Total meals:", sum(meals_eaten))
    print("Simulation completed without deadlock.")

    write_html(
        args.out,
        "Dining Philosophers x4 (Monitor)",
        "dp",
        [f"P{i}" for i in range(N)],
        trace,
        forks=N
    )


if __name__ == "__main__":
    main()
