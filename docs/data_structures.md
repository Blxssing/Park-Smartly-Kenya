# Data Structures

## Stack
Linked-node LIFO stack stores recent parking operations. Push and pop are O(1).

## Queue
Linked-node FIFO queue stores vehicles waiting when the car park is full. Enqueue and dequeue are O(1).

## List / database rows
Parking slots are iterated in slot order to find the first available position.

## Hash-style lookup
SQLite indexed/unique registration access provides fast lookup and prevents duplicate active vehicles.

## Database
SQLite provides persistent dynamic storage for slots, sessions, payments and the waiting queue.
