
"""
Dining Philosophers (4 philosophers) - Semaphore-based solution.
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

forks = [threading.Semaphore(1) for _ in range(N)]
room = threading.Semaphore(N - 1)
meals_eaten = [0] * N


def log_event(actor, message):
    elapsed = time.monotonic() - START_TIME
    print(f"{elapsed:.3f} {actor} -> {message}", flush=True)


def pause(max_delay):
    time.sleep(random.uniform(0.2, 1.0) * max_delay)


def philosopher(i, meals, delay):
    name = f"P{i}"
    left = i
    right = (i + 1) % N

    for _ in range(meals):
        log_event(name, "thinking")
        trace.log(name, "state", state="thinking")
        pause(delay)

        log_event(name, "hungry")
        trace.log(name, "state", state="hungry")

        log_event(name, "waiting for room")
        room.acquire()

        log_event(name, "acquiring forks")
        trace.log(name, "state", state="acquiring")

        log_event(name, f"waiting for fork {left}")
        forks[left].acquire()
        log_event(name, f"fork {left} acquired")
        trace.log(name, "fork", fork=left, owner=i)

        pause(delay / 3)

        log_event(name, f"waiting for fork {right}")
        forks[right].acquire()
        log_event(name, f"fork {right} acquired")
        trace.log(name, "fork", fork=right, owner=i)

        log_event(name, "eating")
        trace.log(name, "state", state="eating")

        meals_eaten[i] += 1
        log_event(name, f"meal {meals_eaten[i]}")
        pause(delay)

        log_event(name, "releasing forks")
        trace.log(name, "state", state="releasing")

        trace.log(name, "fork", fork=left, owner=None)
        forks[left].release()
        log_event(name, f"fork {left} released")

        trace.log(name, "fork", fork=right, owner=None)
        forks[right].release()
        log_event(name, f"fork {right} released")

        room.release()
        log_event(name, "room permit released")

    log_event(name, "done")
    trace.log(name, "state", state="done")


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
            "dining_philosophers_semaphore.html"
        )
    )

    args = parser.parse_args()

    if args.meals < 0 or args.delay < 0:
        parser.error("--meals and --delay must be non-negative")

    random.seed(args.seed)

    print("\nDining Philosophers - Semaphore Solution")
    print("=" * 48)

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
        "Dining Philosophers x4 (Semaphores)",
        "dp",
        [f"P{i}" for i in range(N)],
        trace,
        forks=N
    )


if __name__ == "__main__":
    main()
