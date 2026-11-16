# Algorithms and Workflows

This document describes the current demonstration behaviour. It is not a production parking-system specification.

## Slot display
1. Read parking slots from SQLite.
2. Display each slot number and its AVAILABLE or OCCUPIED state.

## Vehicle entry
1. Normalize the registration by trimming whitespace and converting it to uppercase.
2. Reject an empty registration.
3. Reject a vehicle with an ACTIVE or PAYMENT_PENDING session.
4. Reject a vehicle already in the waiting queue.
5. Find the first available slot.
6. If a slot exists, mark it OCCUPIED and create an ACTIVE session.
7. Otherwise, persist the vehicle in the waiting queue in arrival order.

## Vehicle exit request
1. Find the vehicle's active session.
2. Parse entry and supplied exit timestamps.
3. Calculate elapsed whole minutes.
4. Reject an exit timestamp earlier than entry.
5. Calculate the sample tariff.
6. Mark the session PAYMENT_PENDING.
7. Keep the slot occupied until simulated payment succeeds.

## Simulated payment and queue promotion
1. Verify the session is awaiting payment.
2. Record a payment row with status PAID.
3. Mark the parking session PAID.
4. Release its slot.
5. Return a software-only barrier state of OPEN.
6. Promote the oldest queued vehicle if one is waiting.

The payment operation is a simulation. It does not verify a bank, mobile-money, or card transaction and must not be treated as proof of real payment.
