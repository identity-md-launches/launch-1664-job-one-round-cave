# Checks — Pepe 28

Ran the focused Rehearsal Expiry suite:

```sh
python3 -B -m unittest discover -s line-4/tools/rehearsal-expiry -p 'test_*.py' -v
```

All 6 tests passed. The existing line-4 tool suites were also rerun unchanged;
all **122 tests** across Call Rehearsal, Call Changes, Call Witness, Call
Expectation, Relay Rehearsal, Revert Expectation, and Rehearsal Expiry passed.
The required offline demonstration also printed `match` and exited 0:

```sh
python3 -B line-4/tools/rehearsal-expiry/rehearsal_expiry.py demo
```

The command revalidated the saved real ZTO `totalSupply()` evidence, exact call,
block, result, and declared 3,600-second age. It made no network request.

Validated the delivered PNG signature, 1254 × 1254 RGB dimensions, matching
SHA-256 at both required wall paths, and the JPEG SOI/EOI plus 512 × 512 SOF0
dimensions. A decoded RGB comparison against the verified round-27 ancestor
found zero changed pixels outside the stated addition rectangle. Final images
were visually inspected; see `VISUAL-28.md` and `delivery-checks-28.json`.
