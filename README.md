# OS_Tasks2
# Synchronization Algorithms with AI Support and HTML Visualization

## Operating Systems Programming Assignment

This project demonstrates two fundamental synchronization problems in Operating Systems using **Python Semaphores and Monitors**. It also creates interactive HTML pages that help users observe thread execution, resource sharing, and synchronization activities.

## Implemented Problems

### 1. Readers-Writers Synchronization

The Readers-Writers problem deals with managing multiple threads that access the same shared data.

- **Semaphore-based approach:** Combines `mutex`, `room_empty`, and `turnstile` semaphores to manage reader and writer access.
- **Monitor-based approach:** Applies locks and condition variables to synchronize the operations of readers and writers.
- Permits multiple readers to access the resource concurrently.
- Ensures that a writer accesses the shared resource exclusively.
- Validates shared counter updates to identify possible synchronization problems.

### 2. Dining Philosophers Synchronization

The Dining Philosophers problem explains how multiple threads share limited resources while avoiding deadlock. This project models four philosophers and four forks.

- **Semaphore-based approach:** Assigns binary semaphores to individual forks and uses a counting semaphore to restrict fork competition to three philosophers at a time.
- **Monitor-based approach:** Tracks each philosopher's state and uses condition variables to permit eating only when both adjacent philosophers are not eating.
- Applies synchronization techniques to prevent deadlock.
- Examines starvation risks and the fairness limitations of the implemented solutions.

## Technologies and Tools

- Python 3 programming language
- Python `threading` library
- Semaphores, locks, and condition variables
- HTML, CSS, and JavaScript for interactive simulations
- JSON format for recording execution events
- Python `webbrowser` library

**Dependencies:** The project uses Python's built-in libraries and does not require external packages.

## Directory Layout

```text
.
├── readers_writers/
│   ├── semaphore/
│   │   └── rw_semaphore.py
│   └── monitor/
│       └── rw_monitor.py
├── dining_philosophers/
│   ├── semaphore/
│   │   └── dp_semaphore.py
│   └── monitor/
│       └── dp_monitor.py
├── common/
│   └── tracelog.py
├── generated_html/
└── README.md
```

## Execution Instructions

### Requirements

1. Install Python 3 on your computer.
2. Download or clone the project repository.
3. Launch a terminal or command prompt from the project's main directory.

### 1. Execute Readers-Writers with Semaphores

```bash
python rw_monitor.py --readers 4 --writers 2 --rounds 3 --delay 0.3 --out .\readers_writers_monitor.html
```

### 2. Execute Readers-Writers with Monitors

```bash
python rw_monitor.py --readers 4 --writers 2 --rounds 3 --delay 0.3 --out .\readers_writers_monitor.html
```

### 3. Execute Dining Philosophers with Semaphores

```bash
python dining_philosophers_semaphore.py
```

### 4. Execute Dining Philosophers with Monitors

```bash
python dining_philosophers_monitor.py
```

**Important:** Execute these commands from the repository's root folder. On Windows, the `python` command generally works instead of `python3`.

## Interactive HTML Simulation

During execution, each program captures synchronization events and produces a standalone HTML visualization inside the `generated_html/` folder.

The visualization provides the following features:

- Play and pause options for controlling the simulation.
- Step controls for examining individual execution events.
- Reset option to restart the playback.
- Playback speed adjustment.
- Timeline slider for navigating through execution.
- Visual representation of thread and philosopher states.
- Display of shared resource usage and fork allocation.
- Warning indicators for detected synchronization violations.

When browser access is available, the generated HTML page automatically opens in the system's default web browser after execution.

## Operating System Concepts Covered

The project illustrates several important synchronization concepts:

- Race conditions and their causes
- Mutual exclusion
- Critical sections
- Semaphore-based synchronization
- Monitor-based synchronization
- Locks and condition variables
- Deadlock prevention techniques
- Starvation and scheduling fairness
- Concurrent thread execution and event tracking

## Testing and Verification

The implementations can be evaluated by changing the number of readers, writers, execution rounds, meals, and delays.

The following conditions should be checked during testing:

- The final shared counter equals the expected total of successful write operations.
- Readers and writers never enter the protected critical section simultaneously.
- Adjacent philosophers are never eating at the same time.
- Every philosopher finishes the required number of meals in the tested runs.
- The HTML visualizations accurately represent the events recorded during program execution.

Since thread scheduling depends on runtime conditions, the order of events may differ across executions. Passing the tests does not guarantee that starvation can never occur.

## Learning Objectives

By completing this project, students gain practical knowledge of:

- Developing solutions for standard Operating Systems synchronization problems.
- Understanding the differences between semaphores and monitors.
- Identifying race conditions, deadlocks, and starvation.
- Capturing concurrent execution events for analysis and debugging.
- Building HTML-based tools to visualize synchronization behavior.

## References

1. A. B. Downey, *The Little Book of Semaphores*.
2. Abraham Silberschatz, Peter B. Galvin, and Greg Gagne, *Operating System Concepts*.
3. Andrew S. Tanenbaum and Herbert Bos, *Modern Operating Systems*.
4. [Official Python Threading Documentation](https://docs.python.org/3/library/threading.html)
5. [Official Python Webbrowser Documentation](https://docs.python.org/3/library/webbrowser.html)

## AI Assistance Disclosure

AI tools supported the development process by helping with code implementation, debugging, understanding synchronization methods, creating HTML visualizations, and preparing project documentation. All implementations and outputs should be reviewed and tested to ensure that the concepts are understood and the results are correct.

---

**Course:** Operating Systems  
**Programming Language:** Python 3
