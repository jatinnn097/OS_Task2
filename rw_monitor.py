
import argparse
import os
import random
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))

from tracelog import Trace, write_html

trace = Trace()
START_TIME = time.monotonic()


def log_event(actor, message, kind="state", **data):
    elapsed = time.monotonic() - START_TIME
    print(f"{elapsed:.3f} {actor} -> {message}", flush=True)
    trace.log(actor, kind, **data)


class SharedCounter:
    value = 0


class ReadersWritersMonitor:
    def __init__(self):
        self._lock = threading.Lock()
        self._can_read = threading.Condition(self._lock)
        self._can_write = threading.Condition(self._lock)
        self._active_readers = 0
        self._writing = False
        self._waiting_writers = 0

    def start_read(self, who):
        with self._lock:
            log_event(who, "Waiting to read", state="waiting")

            while self._writing or self._waiting_writers > 0:
                self._can_read.wait()

            self._active_readers += 1
            log_event(
                who,
                f"Started reading (active readers: {self._active_readers})",
                state="reading"
            )

    def end_read(self, who):
        with self._lock:
            self._active_readers -= 1
            log_event(
                who,
                f"Finished reading (active readers: {self._active_readers})",
                state="thinking"
            )

            if self._active_readers == 0:
                self._can_write.notify()

    def start_write(self, who):
        with self._lock:
            self._waiting_writers += 1
            log_event(who, "Waiting to write", state="waiting")

            while self._writing or self._active_readers > 0:
                self._can_write.wait()

            self._waiting_writers -= 1
            self._writing = True
            log_event(who, "Started writing", state="writing")

    def end_write(self, who):
        with self._lock:
            self._writing = False
            log_event(who, "Finished writing", state="thinking")

            if self._waiting_writers > 0:
                self._can_write.notify()
            else:
                self._can_read.notify_all()


monitor = ReadersWritersMonitor()


def pause(delay):
    if delay > 0:
        time.sleep(random.uniform(0.2, 1.0) * delay)


def reader(name, rounds, delay):
    for _ in range(rounds):
        log_event(name, "Thinking", state="thinking")
        pause(delay)

        monitor.start_read(name)

        value = SharedCounter.value
        log_event(
            name,
            f"Read shared counter = {value}",
            kind="access",
            action="read",
            value=value
        )

        pause(delay)
        monitor.end_read(name)

    log_event(name, "Finished all reading rounds", state="done")


def writer(name, rounds, delay):
    for _ in range(rounds):
        log_event(name, "Thinking", state="thinking")
        pause(delay)

        monitor.start_write(name)

        temp = SharedCounter.value
        pause(delay)
        SharedCounter.value = temp + 1

        log_event(
            name,
            f"Updated shared counter = {SharedCounter.value}",
            kind="access",
            action="write",
            value=SharedCounter.value
        )

        monitor.end_write(name)

    log_event(name, "Finished all writing rounds", state="done")


def main():
    parser = argparse.ArgumentParser(
        description="Readers-Writers problem using a monitor"
    )
    parser.add_argument("--readers", type=int, default=4)
    parser.add_argument("--writers", type=int, default=2)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--delay", type=float, default=0.3)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument(
        "--out",
        default=os.path.join(
            HERE,
            "..",
            "..",
            "generated_html",
            "readers_writers_monitor.html"
        )
    )

    args = parser.parse_args()

    if args.readers < 0 or args.writers < 0:
        parser.error("--readers and --writers cannot be negative")
    if args.rounds < 0:
        parser.error("--rounds cannot be negative")
    if args.delay < 0:
        parser.error("--delay cannot be negative")

    random.seed(args.seed)
    SharedCounter.value = 0

    print("Starting Readers-Writers Monitor Simulation")
    print(
        f"Readers: {args.readers}, Writers: {args.writers}, "
        f"Rounds: {args.rounds}, Delay: {args.delay}s"
    )
    print("-" * 60)

    threads = []

    for i in range(args.readers):
        threads.append(
            threading.Thread(
                target=reader,
                args=(f"R{i + 1}", args.rounds, args.delay)
            )
        )

    for i in range(args.writers):
        threads.append(
            threading.Thread(
                target=writer,
                args=(f"W{i + 1}", args.rounds, args.delay)
            )
        )

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    expected = args.writers * args.rounds

    print("-" * 60)
    print(f"Final counter: {SharedCounter.value}")
    print(f"Expected counter: {expected}")

    if SharedCounter.value == expected:
        print("Result: OK - no lost updates")
    else:
        print("Result: ERROR - unexpected counter value")

    names = (
        [f"R{i + 1}" for i in range(args.readers)]
        + [f"W{i + 1}" for i in range(args.writers)]
    )

    output_path = os.path.abspath(args.out)

    write_html(
        output_path,
        "Readers-Writers (Monitor)",
        "rw",
        names,
        trace
    )

    print(f"HTML simulation written to: {output_path}")
    print(f"Total events: {len(trace.events)}")


if __name__ == "__main__":
    main()
