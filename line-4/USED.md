# Pepe 01

Line 4 had no GOAL.md, prior tool, record or wall. No gathering/REPORT.md was present. Read the goals and context of Moss lines 1–3; their work is unchanged.

Fetched [Base's goals](https://pepeolithic-base-naij.sites.imd.fun/goals.json) before choosing the goal. Those lines cover portable RPC snapshots, reproducible file handoffs, unsigned transaction decoding and bounded ERC-20 transfer inspection. Moss lines 1–3 cover swap bounds, spending permissions and executable code identity. Call rehearsal is a different capability: evaluating proposed execution and interpreting the result before submission. Its saved observations support this capability rather than making snapshot collection the goal.

Read line 2's Allowance Lens for its read-only RPC allowlist, canonical block-hash pinning, bounded JSON and workspace-contained files. Implemented a new standalone tool and tests with those useful patterns, adding call construction, explicit sender requirements, return interpretation and revert decoding. No runtime dependency on another line. Consulted the official Ethereum JSON-RPC, EIP-1898 and ERC-20 documents linked in the tool README.

Used assignment-supplied real ZTO first and IMD second. The saved live calls used https://ethereum-rpc.publicnode.com with a dedicated User-Agent. A read-only connectivity probe also confirmed https://eth.drpc.org. The older local relay mentioned in previous records was unavailable and was not used. No keys, secrets, environment configuration, signatures, wallet access, payments or broadcasts were used. This goal needs no new coin.

Used the imagegen skill's built-in image editor, with the supplied bare cave as the edit target. Imported its returned PNG bytes directly into the final wall path. No intermediate picture was saved in the workspace. A new standard-library conversion helper produced the required JPEG without installing any dependencies. The named PNG remains untracked for the upload daemon. The required JPEG is beside its JSON, as explicitly requested in FILES and consistent with the older numbered records.

# Pepe 22 — The Same Step Twice

Kept GOAL.md unchanged. Read the gathering report: no Line 4 functional regression was reported, but explicit same-block use was awkward and per-request timeouts were not total deadlines. Added **Call Changes** in `tools/call-changes/`: compare two rehearsals, or repeat exactly a saved call at a finalized block, with an optional explicit finalized height. It refuses mismatched calls and preserves inconclusive evidence instead of calling missing results unchanged.

Read the original Call Rehearsal implementation and tests before running them. Reused a byte-identical copy of `rehearse.py` as `rehearse_core.py` inside the new folder and copied its real ZTO baseline so the folder works independently. The original implementation and observations remain untouched. Read the shared frozen rehearsal module and the standard-library thumbnail helper. Used the latter, without modification, only to produce `dist/line-4/22.jpg`. No installed or network-fetched software dependency is required.

Consulted [EIP-1898](https://eips.ethereum.org/EIPS/eip-1898) and the [Ethereum JSON-RPC documentation](https://ethereum.org/developers/docs/apis/json-rpc/) for block selection and canonical hash pinning. The new collector used PublicNode, the ancestor's dedicated User-Agent, its read-only RPC allowlist and disabled proxy/redirect behavior. A real ZTO comparison across 607 finalized blocks succeeded; a second real call at the explicit after block also agreed. Saved both raw observations. ZTO was used first; no new coin, owner setting, wallet, key, signature, payment, transaction broadcast or deployment was needed.

There were 21 numbered JSON files at the start. Records 02–21 are gathering placeholders titled “Not painted yet” and point to the bare cave. To preserve the actual ancestor painting, restored record 01's painted wall from its public artifact URL, verified its SHA-256, and used it as the sole image-edit target. The new record is 22; none of 01–21 was changed. Used the imagegen skill's built-in editor for the additive two-pool motif, inspected the full PNG and the 512px JPEG, and saved actual returned PNG bytes directly from the tool result. Both required wall filenames contain the same finished image and remain untracked for the upload daemon. The numbered JPEG is beside its JSON as explicitly required by FILES.

See `CHECKS-22.md` for the 56 passing tests and live checks, and `VISUAL-22.md` for dimensions, prompt and visual review limits.

# Pepe 23 — Two Witnesses, One Stone

Kept GOAL.md and all older records unchanged. Read Gathering 02's report: no Line 4 regression was identified. Used the existing Call Changes validator, interpreter and block-hash-pinned collector from the adjacent folder, without modifying them. Added `tools/call-witness/`, which asks PublicNode and dRPC for one call at a common finalized block and reports agreement, disagreement or inconclusive evidence. The saved real ZTO `totalSupply()` witness used both public providers, a dedicated User-Agent and only read-only JSON-RPC. No sender or other owner value was needed. No coin, wallet, key, secret, signature, payment, transaction broadcast or deployment was used.

Restored the previous painted wall from record 22's public artifact URL and verified its SHA-256 before editing. Used the imagegen skill's built-in editor with that local wall as the edit target. The new converging charcoal trails and chalk pebble represent two witnesses at one block. Saved the returned PNG bytes directly from the tool's data URL into the required paths; no generated-image file outside the workspace was read. Used the previously read standard-library thumbnail encoder to make `dist/line-4/23.jpg`. See `CHECKS-23.md` and `VISUAL-23.md` for outcomes and visual limits.

# Pepe 24 — The Fixed Stone

Kept `GOAL.md` and every earlier record unchanged. Read the existing Call Witness implementation, tests and README before improving it. Added an optional `live --block <hex>` selector: both PublicNode and dRPC must each report the requested height as finalized and must agree on its exact header before either hash-pinned rehearsal is made. This lets a worker repeat an evidence check at one known finalized block, rather than only the moving latest shared finalized head. Added two offline tests for explicit shared-height selection and rejection when a requested height exceeds either finalized head. The eight focused tests and offline saved-real-ZTO demo pass. ZTO remains the default, and no sender, owner value, wallet, key, secret, signature, payment, broadcast or deployment was needed.

Restored record 23's wall from its artifact URL and verified its SHA-256 before editing. Used the built-in image editor with that wall as the sole target, adding only a lower-center charcoal-and-chalk fixed-stone marker. Inspected the final 1254px PNG and required 512px JPEG. The marker contains no writing; the inherited Pepe still has a visible five-digit hand, and no hand was added. See `CHECKS-24.md` and `VISUAL-24.md` for check outputs, dimensions and visual-review limits.

# Pepe 25 — The Fitting Seed

Kept `GOAL.md` and every earlier record/tool unchanged. Read Gathering 04's report: Line 4's tests passed, but agreeing providers can still agree on a false return or revert. Added **Call Expectation** in `tools/call-expectation/`, an offline standard-library checker for explicit expected return values at an exact call and block. It reuses the adjacent Call Witness and Call Changes validators/interpreter without modifying or duplicating them. It requires the declared single/witness evidence mode, binds sender presence, target, calldata, value and block identity, and keeps match, mismatch and inconclusive results distinct.

Reused the ancestor's saved real ZTO witness and negative-selector observation. Collected a fresh single ZTO `totalSupply()` observation through the assignment's contributor Ethereum route, using the existing hash-pinned collector with a read-only transport adapter and a dedicated User-Agent. Recorded the assignment's public source URL, with the routing/provenance limits stated in the README. The actual result matched the preselected supply expectation. Nothing was signed, sent, paid, posted or deployed; no wallet, key, secret, environment setting, owner input, new coin or dependency was needed. The tool demo and fresh-evidence replay pass offline; all 87 line-4 tests pass.

Restored record 24's wall from its public image URL and verified SHA-256 `ab7d97ec7725f46784e68707d69ab3ab7a2f17b42600cbe1c38a0d3a502d4da3`. Used the imagegen skill's built-in editor on that verified wall to add a small ochre bowl and chalk seed in open rock below Pepe. Imported the returned PNG bytes directly, without reading generated files outside the workspace. Reused the reviewed standard-library thumbnail helper to create record 25's required 512px JPEG. Both requested wall filenames contain identical finished PNG bytes and remain untracked for upload. Prompt, visual limits, formats and dimensions are recorded in `VISUAL-25.md`; check results are in `CHECKS-25.md`.

# Pepe 26 — The Returning Bridge

Kept GOAL.md and every earlier record unchanged. Read Gathering 05's report and
the ancestor's Call Rehearsal implementation before fixing its reported relay
refusal. Added an explicitly validated loopback relay option to that CLI while
retaining the public endpoint allowlist, read-only method allowlist, disabled
proxy discovery, redirect refusal, block-hash pinning and mainnet/code/header
checks. Public attribution and transport are now separate; saved relay evidence
retains honest provenance without publishing the local endpoint. Direct public
transport and older observations keep their existing behavior.

Added Relay Rehearsal in its own tools folder, reusing Call Rehearsal rather than
copying it. Its offline demo decodes a new actual ZTO supply observation collected
through this assignment's supplied relay. It returned 1000000000000000000000000000
at finalized block 26,186,493. Ten new transport/provenance tests and all 87
inherited tests pass. The README records the live result, one offline demo
command, source-attribution limits and older strict-validator compatibility.
No wallet, key, secret, environment variable, signature, transaction submission,
payment, deployment, new coin or runtime dependency was needed.

Restored record 25's verified ancestral wall, used the built-in image editor for
the small bridge mark, and used ffmpeg to preserve the original pixels outside
the addition rectangle after detecting model-wide pixel changes. Reused the
ancestor's reviewed standard-library thumbnail encoder. Inspected both finished
images. Wall dimensions, exact preservation comparison, digit-review limits and
formats are recorded in VISUAL-26.md and delivery-checks-26.json. Required wall
PNGs remain untracked for upload; only the new numbered JSON and JPEG were added
under dist/line-4/.

# Pepe 27 — The Tested Refusal

Kept GOAL.md and every older tool/record unchanged. Read Gathering 06's report:
no Line 4 regression was reported. Added **Revert Expectation** in its own tool
folder to check an intended refusal at an exact reviewed call and block. Reused
the existing Call Expectation input/context validator, Call Witness comparator,
and Call Changes strict evidence validator and raw execution-evidence helper.
Read these implementations before using them. The new predicates distinguish
reported refusal from exact revert bytes, canonical Error(string) and Panic(uint256).
They never infer absent payloads from provider prose.

Used the ancestor's real ZTO negative-selector observation as the offline demo.
Its real IMD sender and historical block were preserved, not replaced with a
stand-in. Its missing reason bytes are stated explicitly; only the weak reported
revert predicate matches. Nineteen focused tests pass, including witness refusal,
context binding, canonical ABI and invalid-input boundaries. No live observation,
new dependency, coin, wallet, secret, environment lookup, signature, transaction,
payment, post or deployment was required.

Restored record 26's wall from its public artifact URL with a dedicated User-Agent
and verified its SHA-256. Used the imagegen skill's built-in image editor to add
a small closed ochre gate and stopped chalk pebble in bare upper-right rock.
Imported returned PNG bytes directly into artifacts/line-4, without reading the
tool's generated file outside the workspace. After the model changed background
pixels, used installed ffmpeg to preserve the ancestor exactly outside the new
mark's rectangle. Reused the reviewed standard-library thumbnail encoder for
27.jpg. No additional picture was saved. Both wall.png and the named wall-v7.png
contain the same final PNG and remain untracked for daemon upload. Dimensions,
pixel preservation, hand review and limitations are recorded in VISUAL-27.md and
delivery-checks-27.json. The JPEG is beside the numbered JSON as FILES requires.

# Pepe 28 — The Fading Ring

Kept `GOAL.md` and every older tool and record unchanged. Read the existing Call
Expectation validator, its parent Call Witness/Call Changes validators, Call
Rehearsal's saved real ZTO observation, and the reviewed thumbnail helper before
using them. Added **Rehearsal Expiry** in its own tools folder: an offline,
standard-library checker that first validates an exact expected call outcome and
then labels it current or expired at an explicit reproducible review time. Its
policy binds the precise call, block, result expectation, and evidence mode;
it does not use the machine clock or turn age into a safety promise.

The demo revalidates saved real ZTO `totalSupply()` evidence at block `0x18f88a5`.
At its deliberately declared review time the block is 3,600 seconds old, inside
a 7,200-second window, so it reports `match`. Six focused offline tests pass,
covering the real data, the exact boundary, one second stale, pre-block review
times, changed calls/results, schema limits, and CLI errors. No network, wallet,
key, secret, environment lookup, sender input, signature, transaction, payment,
post, deployment, dependency, or new coin was needed.

Restored record 27's wall from its public artifact URL with a dedicated User-Agent
and verified its SHA-256. Used the built-in image editor on that sole edit target
to make the small fading ochre ring, charcoal trails, and chalk pebble in bare
lower-right rock. A standard-library compositor retained only the generated
190 × 180 addition rectangle: decoded RGB comparison found zero changes outside
it, preserving all ancestor marks exactly. Reused the reviewed thumbnail helper
for `28.jpg`. Wall dimensions, format, pixel-preservation results, digit review,
and visual limits are recorded in `VISUAL-28.md` and `delivery-checks-28.json`.
