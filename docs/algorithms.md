# Algorithms

## Slot display
1. Read all slots from the database.
2. Display each slot number and its AVAILABLE/OCCUPIED state.

## Entry
1. Normalize registration number.
2. Reject if the vehicle is already active or waiting.
3. Find the first available slot.
4. If one exists, mark it occupied and create an ACTIVE session.
5. Otherwise enqueue the vehicle in FIFO waiting order.

## Exit
1. Find the active session by registration.
2. Parse entry and exit timestamps.
3. Calculate elapsed minutes.
4. Apply the tariff rules.
5. Set the session to PAYMENT_PENDING.
6. Keep the slot occupied until payment succeeds.

## Payment/barrier
1. Verify the session is awaiting payment.
2. Record a PAID payment.
3. Mark the session PAID.
4. Release the slot.
5. Open the barrier in the software model.
6. Promote the next waiting vehicle in FIFO order.
