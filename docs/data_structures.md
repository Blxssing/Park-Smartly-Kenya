# Data Structures

## Stack

The linked-node stack in `app/datastructures.py` follows last-in, first-out (LIFO) order. The parking service uses it to record recent in-memory operations. Push and pop are O(1).

## Queue

The linked-node queue follows first-in, first-out (FIFO) order. It models vehicles waiting when all parking slots are occupied. Enqueue and dequeue are O(1).

The database also persists the waiting list in the `waiting_queue` table so the queue can be reconstructed after application restarts.

## SQLite tables and indexes

- `parking_slots` stores parking spaces and their current state.
- `parking_sessions` stores vehicle entry and exit lifecycle records.
- `payments` stores simulated payment records.
- `waiting_queue` stores vehicles awaiting a slot.
- A partial unique index prevents multiple simultaneous ACTIVE or PAYMENT_PENDING sessions for the same registration.

## Complexity notes

Finding the first available slot currently scans available rows returned by SQLite and depends on the number of configured slots. Registration lookups use SQLite indexes and constraints where applicable. These choices favour clarity for a small demonstration over high-volume optimisation.
