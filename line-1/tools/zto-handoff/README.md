# ZTO Handoff

Turn one exact, already reviewed ZTO/IMD planning bound into a compact handoff a
human or another worker can inspect. It first reruns `ZTO Review` against the
snapshot, report, and policy, then accepts only one amount that exactly matches
a complete reviewed candidate. The output binds the source digests, pinned
block, requested input, and minimum output with its own canonical digest.

It never prepares settlement: the output has no recipient, router, calldata,
gas choice, signature, key, or transaction. It is deliberately a handoff for
human review rather than something that can spend or send.

## One command to see it working

From the repository root, with Python 3.10+ and no installation or network:

```sh
python3 -B line-1/tools/zto-handoff/zto_handoff.py --demo --amount 100000000
```

The bundled offline demonstration uses real historical ZTO/IMD pool evidence at
Ethereum block 26,184,260. It returns `ready_for_human_review` for exactly
100,000,000 ZTO and a 1%-tolerance minimum of
1,184.169088029408336486 IMD. `--policy POLICY --snapshot SNAPSHOT --report
REPORT --amount AMOUNT` accepts caller-supplied workspace JSON and repeats the
same review before making a handoff.

## What happened when tried

The demonstration succeeded offline and tests covered the accepted historical
candidate, rejection of an unreviewed or partial amount, report tampering, and
the no-network CLI path:

```sh
python3 -B -m unittest discover -s line-1/tools/zto-handoff -p 'test_*.py' -v
```

The output is a planning bound from a historical snapshot, not a current quote,
execution promise, state proof, router simulation, or MEV/gas/transfer model.
The caller supplies policy and tolerance; a changed pool can make a future
execution differ. It uses only standard-library Python plus committed sibling
Line 1 sources and never reads secrets or environment variables.
