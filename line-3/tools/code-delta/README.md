# Code Delta

Compare the proof-backed executable-code identities of one Ethereum contract at two historical blocks. It reconstructs both state/header proofs, compares every supported candidate proxy-path position and measured slot, and shows a bounded instruction window for changed runtime bytes. Added/removed path entries and beacon runtimes are explicit. This helps a worker locate code changes before deciding what needs review.

One command from the repository root works **offline on real ZTO first, then IMD evidence**:

```sh
python3 -B line-3/tools/code-delta/demo.py
```

Expected: `demonstration_passed: true`, with matching endpoint identities for both tokens, a distance of **1,752 blocks**, and `unanchored-rpc-header`. Exit 0 means the documented comparison succeeded; it grants no code approval. Python **3.9+** and only the standard library are needed. Keep the committed sibling `code-ancestry`, `code-proof`, `code-lens` (including Keccak), and `code-opcodes` folders. No installation or network is needed for replay.

## What happened when tried

Fresh real proofs were collected through the assignment-provided Ethereum relay at RPC-reported finalized block **26,187,032**, hash `0xb6e55dcdf6ded6229f188d80f0b986222b198d104e09e9194bb8d97539355a06`. Public attribution is [Ethereum PublicNode](https://ethereum-rpc.publicnode.com); the relay's upstream identity is explicitly unverified. The earlier committed bundles are at block **26,185,280**. Both endpoints reverified their runtime hashes and two measured proxy slots.

| Token | Runtime bytes | Endpoint comparison |
| --- | ---: | --- |
| ZTO | 1,287 | Same runtime hash and measured code path/slots |
| IMD | 22,990 | Same runtime hash and measured code path/slots |

`zto-later-proof.json` and `imd-later-proof.json` contain the complete later raw proofs. `zto-delta.json`, `imd-delta.json`, and `demo-result.json` record the replay results. No independent anchor was available or invented. These are historical observations, not current-code certificates. No coin, wallet, key, secret, signature, transaction, payment, publication or deployment is needed.

## Compare your own bundles

For the saved ZTO pair, run:

```sh
python3 -B line-3/tools/code-delta/code_delta.py --before line-3/tools/code-proof/zto-proof.json --after line-3/tools/code-delta/zto-later-proof.json
```

Use raw Code Proof bundles, not summaries or Code Lens observations. Both must identify the same nonzero target on chain 1; the second must have a strictly greater block number. The CLI reads only files inside the current workspace, caps each input at 100,000 bytes and refuses duplicate JSON keys. It performs no network request and writes no files. Invalid proofs, different targets, reversed/equal heights, malformed inputs or mismatched anchors exit 1 with no partial result on stdout. CLI syntax errors exit 2. Valid comparisons exit 0 whether identities match or differ.

Optional `--before-anchor-hash` and `--after-anchor-hash` separately check each endpoint against an execution block hash selected by the caller. Supply authentic hashes from an independently trusted source. Each side retains its own anchor label; pinning only one never anchors the other. Copying hashes from the bundles only tests equality. No flag, embedded verdict or saved success summary can certify anchor authenticity.

## Read the changed window correctly

All runtime bytes participate, including recognized Solidity metadata. PUSH operands are decoded with their opcode, so bytes such as `f4` inside PUSH data are not treated as DELEGATECALL instructions. Truncated PUSH operands keep their actual byte extent and missing-byte count. Unknown opcodes have numeric labels; this is a linear inventory, not an EVM interpreter.

Matching instruction prefix and suffix are trimmed in linear time. A changed window gives half-open byte ranges, full-window Keccak hashes, instruction counts and at most the first/last eight instructions per side. Omitted counts are explicit. The window can contain unchanged instructions between changes and **is not a minimal edit script**. An insertion/deletion can have an empty range on one side. Common instruction bytes at shifted PCs do not establish semantic equivalence. `prefix_before_metadata_equal` is a diagnostic only; metadata can contain executable bytes, and the complete runtime still differs.

Candidate path entries are compared by their ordered position; a replacement implementation address is always reported even if its bytecode matches. Beacon runtimes are compared separately by address. Beacon `implementation()` results remain unproven and are surfaced in each proof result. A supported proxy-slot candidate does not prove the runtime routes through that slot. Custom routing, selector reachability, source equivalence and contract safety are outside coverage.

Two matching endpoints do **not** prove continuous stability between them. Two different heights do **not** prove common-chain ancestry or finality. The tool reports `common_chain_ancestry_verified: false` and `anchor_authenticity_verified: false`. Use the existing Code Review/Code Set tools when you need an exact reviewed-identity acceptance gate; this piece is a comparison, never an acceptance gate.

Run the focused checks:

```sh
python3 -B -m unittest discover -s line-3/tools/code-delta -p 'test_*.py' -v
```

The checks cover both real endpoint replays, fully reconstructed synthetic changed-code and beacon/path fixtures, corruption on either side, forged consistent runtime reports, separate anchors, target/height refusals, hex normalization, PUSH data/truncation, metadata inclusion, insertion/deletion, bounded previews, repetitive maximum-size runtimes and CLI failure without partial JSON. Synthetic fixtures exist only in tests and are never saved as chain observations.

The mark's meaning: **Pepe compares two code trails and notices the stone that differs.**
