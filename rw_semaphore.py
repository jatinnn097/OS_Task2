
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


mutex = threading.Semaphore(1)
room_empty = threading.Semaphore(1)
turnstile = threading.Semaphore(1)
read_count = 0


def pause(delay):
    if delay > 0:
        time.sleep(random.uniform(0.2, 1.0) * delay)


def reader(name, rounds, delay):
    global read_count

    for _ in range(rounds):
        log_event(name, "Thinking", state="thinking")
        pause(delay)

        log_event(name, "Waiting to read", state="waiting")

        turnstile.acquire()
        turnstile.release()

        mutex.acquire()
        read_count += 1

        if read_count == 1:
            log_event(name, "First reader: waiting for shared room", state="waiting")
            room_empty.acquire()

        log_event(
            name,
            f"Started reading (active readers: {read_count})",
            state="reading"
        )
        mutex.release()

        value = SharedCounter.value
        log_event(
            name,
            f"Read shared counter = {value}",
            kind="access",
            action="read",
            value=value
        )
        pause(delay)

        mutex.acquire()
        read_count -= 1

        log_event(
            name,
            f"Finished reading (active readers: {read_count})",
            state="thinking"
        )

        if read_count == 0:
            room_empty.release()
            log_event(name, "Last reader released the shared room")

        mutex.release()

    log_event(name, "Finished all reading rounds", state="done")


def writer(name, rounds, delay):
    for _ in range(rounds):
        log_event(name, "Thinking", state="thinking")
        pause(delay)

        log_event(name, "Waiting to write", state="waiting")

        turnstile.acquire()
        log_event(name, "Turnstile acquired; new readers must wait")

        room_empty.acquire()
        log_event(name, "Shared room acquired; exclusive writing started", state="writing")

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

        log_event(name, "Finished writing", state="thinking")

        room_empty.release()
        log_event(name, "Shared room released")

        turnstile.release()
        log_event(name, "Turnstile released; readers may proceed")

    log_event(name, "Finished all writing rounds", state="done")


def main():
    parser = argparse.ArgumentParser(
        description="Readers-Writers problem using semaphores"
    )
    parser.add_argument("--readers", type=int, default=4)
    parser.add_argument("--writers", type=int, default=2)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument(
        "--delay",
        type=float,
        default=0.3,
        help="Maximum delay scale in seconds"
    )
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument(
        "--out",
        default=os.path.join(
            HERE,
            "..",
            "..",
            "generated_html",
            "readers_writers_semaphore.html"
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

    print("Starting Readers-Writers Semaphore Simulation")
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
    print(f"Final counter = {SharedCounter.value}")
    print(f"Expected counter = {expected}")

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
        "Readers-Writers (Semaphores)",
        "rw",
        names,
        trace
    )

    print(f"HTML simulation written to: {output_path}")
    print(f"Total events: {len(trace.events)}")


if __name__ == "__main__":
    main()
