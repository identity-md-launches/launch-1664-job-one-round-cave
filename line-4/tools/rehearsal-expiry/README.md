# Rehearsal Expiry

Make a saved Ethereum call rehearsal expire at a deliberately chosen review time. It first revalidates an exact call expectation and its exact block, then reports whether the evidence is inside a bounded age window. This prevents a worker from silently treating an old favorable rehearsal as current. It is Python 3.9+ standard library only and runs offline: no installation, key, wallet, sender, transaction, payment, or network request is needed.

From the repository root, run:

```sh
python3 -B line-4/tools/rehearsal-expiry/rehearsal_expiry.py demo
```

When tried on 2026-10-14, the command printed `match` and exited 0. It revalidated a saved real **ZTO** `totalSupply()` rehearsal at block `0x18f88a5` against the supplied exact value `1000000000000000000000000000`. The declared review time is exactly 3,600 seconds after that block and its window is 7,200 seconds, so the evidence is current *at that declared review time*. It is not a claim about ZTO now. ZTO is used first at its real Ethereum address `0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`; no requester-owned value is needed.

For a reviewed evidence file and policy of your own:

```sh
python3 -B line-4/tools/rehearsal-expiry/rehearsal_expiry.py check path/to/observation.json path/to/expiry-policy.json
```

An expiry policy contains exactly `schema`, hexadecimal Unix `as_of`, integer `max_age_seconds` (0 through 2,678,400), and an embedded `call-expectation-v1` policy. The embedded policy binds chain ID, sender presence, target, calldata, native value, exact block header, evidence mode, and expected returned bytes/bool/uint256. `as_of` is intentionally an explicit review input rather than the machine clock, so the result is reproducible and does not pretend to know when an operator will submit anything.

| Verdict | Exit | Meaning |
| --- | ---: | --- |
| `match` | 0 | Exact expected call evidence matched and is no older than the declared limit. |
| `mismatch` | 1 | The call result differed, or matched but had already expired. |
| `inconclusive` | 2 | Context, evidence mode, timestamp, or input was invalid or insufficient. |

The focused offline suite covers the real ZTO case, exact expiry boundary, pre-block review times, changed context/result, policy limits, and CLI errors:

```sh
python3 -B -m unittest discover -s line-4/tools/rehearsal-expiry -p 'test_*.py' -v
```

This is a freshness label on unauthenticated historical RPC evidence, not a safety decision. It neither reads an independent clock nor verifies current state, code, balances, gas, fees, permissions, canonicality, inclusion, or eventual execution. It imports the adjacent `call-expectation/` validators rather than duplicating their parsing; retain that folder and its `call-witness/` and `call-changes/` dependencies when moving this tool. Nothing is signed, sent, paid, posted, or deployed.
