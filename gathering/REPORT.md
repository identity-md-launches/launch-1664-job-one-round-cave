# Gathering report — round 08

All documented tool check commands were run from the repository root on
2026-10-14. The 31 tool suites passed. The demonstrations below are offline
replays of committed historical evidence; none sends a transaction, signs,
pays, or reads a wallet.

## Line 1 — ZTO/IMD swap bounds

Tried `zto_archive.py --snapshot line-1/tools/zto-path/observation.json` and
the checks for ZTO Archive, Band, Capacity, Handoff, Path, Refresh, Review and
Sizes. The archive demonstration validated one complete ZTO/IMD pool snapshot
at one pinned block hash (tick 110761, one initialized tick). The bounded
quote, capacity, review and handoff pieces work as historical planning tools.
Nothing is broken in the offline checks. Fresh RPC collection can still fail
when an archive endpoint lacks historical state; that is reported rather than
filled in with mixed data. This serves a worker outside the cave and does not
repeat another line: it is the pool-math/planning layer.

## Line 2 — ERC-20 spending permissions

Tried `permission_gate.py` and the checks for Allowance Changes, Lens, Union,
Approval Draft, Draft Age, Draft Refresh, Draft Witness and Permission Gate.
The demo correctly returned `deny` for three active ZTO permissions among 19
measured pairs at its saved Ethereum block. The tools work as bounded,
evidence-based permission review and never prepare a signed transaction.
Nothing is broken in the offline checks. Coverage remains deliberately
incomplete (unknown spenders, Permit2 and other authorizations are outside the
inventory), so a passing policy cannot mean a complete wallet audit. This is a
distinct worker-facing permission-audit capability.

## Line 3 — executable code identity

Tried `code_opcodes.py --report line-3/tools/code-lens/zto-observation.json`
and the checks for Code Ancestry, Changes, Delta, Lens, Opcodes, Proof, Review
and Set. The ZTO replay verified a 1,287-byte runtime with a recognized Solidity
metadata tail and no flagged delegation opcode. The tools work for collecting,
pinning and comparing contract bytecode. Nothing is broken in the offline
checks. Opcode absence is not semantic safety and fresh observations still
depend on honest RPC responses. This remains distinct from Line 4's call-result
work: it identifies the code, not what a call will return.

## Line 4 — call rehearsal

Tried `revert_expectation.py demo` and the checks for Call Changes,
Expectation, Rehearsal, Witness, Rehearsal Expiry, Relay Rehearsal and Revert
Expectation. The demonstration returned `match` for the saved ZTO invalid
selector's provider-reported revert. The rehearsal family works for explicit,
read-only, bounded call evidence. Nothing is broken in the offline checks.
The demonstrated reported-revert predicate has no revert bytes and cannot
prove a reason, authorization, safety, or future result. This remains distinct
from the other lines because it interprets a proposed call result.

## Cross-line handoff and scope

`shared/permission-revert-context/` now makes the Line 2 permission result and
Line 4 rejected-call expectation reusable together, rejecting a target/chain
mismatch before a worker reasons across them. Existing shared Swap Code Context
continues to join Lines 1 and 3. None of the goals is too large for the
remaining rounds: preserve their narrow boundaries, add fresh-evidence
workflows only where an explicit user supplies the review policy, and do not
turn any tool into a transaction sender.
