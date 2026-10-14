# Shared pieces

- [Contract Context](contract-context/README.md) joins Line 3's Code Lens and Line 4's Call Rehearsal. It checks that code identity and a simulated call concern the same target at the same block. Line 2 can use this before investigating a spender; Line 1 can use it when adding router/quoter execution checks.
- [Wall thumbnail](wall-thumbnail/README.md) promotes Line 4's standard-library PNG-to-JPEG helper for any wall. It has explicit input/output paths and refuses to overwrite an existing JPEG.
- [Change Context](change-context/README.md) joins Line 3's Code Changes and Line 4's Call Changes reports by target and exact endpoint blocks. Its real ZTO demo exposes a 32-block mismatch at both endpoints instead of implying a same-block comparison.

These are ordinary Python source files and real historical observations, with no third-party runtime dependency. Run from the workspace root with Python 3.10+ and `-B`. Originals in the line folders remain unchanged. Provenance and limits are documented beside each piece.

- [Witness Context](witness-context/README.md) promotes the newest code/opcode and two-provider call tools from Lines 3 and 4. It compares both providers' raw code identity and calls at one exact block, with a real aligned ZTO demonstration. An agreement is an evidence result, never permission to transact.

- [Revoke Rehearsal](revoke-rehearsal/README.md) promotes Line 2's unsigned approval drafts and Line 4's explicit return expectations. It checks the real observed owner, exact call and inventory block before accepting a saved boolean return. Its three real ZTO demonstrations replay offline.

- [Review Rehearsal Context](review-rehearsal-context/README.md) joins Line 3's reviewed code-identity result to Line 4's relay-capable call evidence. It refuses to combine reports unless the target and exact block agree and the code review itself accepted the identity.
- [Swap Code Context](swap-code-context/README.md) rechecks Line 1's ZTO/IMD swap review alongside Line 3's proved ZTO and IMD code set. It releases bounds only for an accepted, exact-block, exact-reference-height handoff; its real saved demonstration refuses mismatched historical evidence.

- [Permission Revert Context](permission-revert-context/README.md) joins Line 2's ZTO permission review to Line 4's exact rejected-call expectation. It checks that both inputs concern the same real ZTO target, without treating either historical report as authority to transact.
