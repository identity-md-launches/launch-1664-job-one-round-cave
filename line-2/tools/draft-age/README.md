# Draft Age

Withhold an unsigned ERC-20 revoke candidate when its latest measured permission is too old relative to a caller-selected Ethereum reference block. The allowance must still equal the reviewed active permission; changed or cleared permissions also withhold the old candidate. This is a standard-library Python 3.10+ offline tool that recomputes Draft Refresh and its ancestor reviews from raw evidence, rather than trusting a previous result's acceptance flag.

One command from the repository root shows it working without network access:

```sh
python3 -B line-2/tools/draft-age/draft_age.py
```

It reports `release_for_owner_review`, `accepted: true`, and an age of zero blocks for a **historical demonstration**. It exposes the exact optional unsigned candidate only when both the permission and the age checks pass. It never signs, sends, pays, posts, opens a wallet, or accesses a key.

## What happened when tried

Read the real ZTO pair at finalized Ethereum block **26,187,000**, through the assignment's contributor route, attributed to [Ethereum PublicNode](https://ethereum-rpc.publicnode.com). The original reviewed inventory was at block 26,184,897. The new capture checked that original header, used canonical hash-pinned `eth_call` for decimals, balance and allowance, and reread the measured header. A separately requested finalized reference header was still block 26,187,000. The owner's balance remained zero; the spender's allowance remained uint256 maximum. `live-after.json`, `live-reference.json` and `live-review.json` retain the actual public evidence and its review with a chosen eight-block limit. These are trusted RPC observations, not state proofs. The default demonstration uses these bundled inputs with a stricter zero-block limit. It is not a claim about today's tip.

Seven focused tests passed: inclusive age boundary, stale withholding, a reference behind the observation, conflicting same-height headers, invalid limits and reference identity, changed/cleared allowance, altered calldata, digest binding, and an offline CLI. Mutated test headers are isolated test cases, never saved as chain evidence. All ancestor test suites also passed after updating Allowance Lens's assignment route to this machine's supplied endpoint.

## Review your own inputs

All files must be inside the current workspace, at most 96 KiB each. Provide the five inputs together and choose your own inclusive age limit; none is silently assumed for external inputs:

```sh
python3 -B line-2/tools/draft-age/draft_age.py --draft line-2/tools/draft-age/reviewed-draft.json --before line-2/tools/permission-gate/live-observation.json --policy line-2/tools/permission-gate/demo-policy.json --after line-2/tools/draft-age/live-after.json --reference line-2/tools/draft-age/live-reference.json --maximum-age-blocks 8
```

The reference JSON has exactly `schema`, `chain_id`, `source`, and `block`. Schema is `permission-reference-block-v1`, chain is integer `1`, source is one of the ancestor's two public Ethereum URLs. The block has exactly `number`, `hash`, and `timestamp`, using canonical RPC quantities and a 32-byte hash. Choose a reference from evidence you trust. Same-height headers must match the observation's hash and timestamp; reference height and time must never precede the pair read.

Exit **0** releases the candidate for owner review, **3** withholds it because it is stale or its permission changed, and **1** reports malformed or inconsistent inputs. Each result includes SHA-256 digests of all five parsed inputs using sorted compact JSON, so workers can compare exactly which evidence was reviewed. These hashes do not authenticate a provider.

Age is a block count relative to the supplied reference, with no wall-clock inference. A caller can supply an old reference; this tool cannot discover that offline. A later header alone does not establish ancestry or canonicality of the earlier observation. Unknown spenders, Permit2 subpermissions, unused signatures and custom authorizations remain outside this exact measured-pair review. An accepted candidate still requires the owner's independent decision; it has no transaction authority and no assurance about future state.

Run checks:

```sh
python3 -B -m unittest discover -s line-2/tools/draft-age -p 'test_*.py' -v
```
