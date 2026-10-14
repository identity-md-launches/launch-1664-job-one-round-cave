#!/usr/bin/env python3
"""Relate an allowance-review result to a rehearsed refused call, offline."""
import argparse
import json
from pathlib import Path

ROOT = Path.cwd().resolve()
ZTO = "0xd782bdea4ef02a0bd391eb9089470c8080f0a68e"


def load(name):
    path = Path(name).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("input must stay inside the workspace")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--permission", default="line-2/tools/permission-gate/example-report.json")
    parser.add_argument("--expectation", default="line-4/tools/revert-expectation/zto-expectation.json")
    args = parser.parse_args()
    permission, expectation = load(args.permission), load(args.expectation)
    token = permission.get("token_address", "").lower()
    target = expectation.get("call", {}).get("to", "").lower()
    aligned = (permission.get("schema") == "permission-gate-report-v1"
               and expectation.get("schema") == "revert-expectation-v1"
               and permission.get("chain_id") == expectation.get("chain_id") == 1
               and token == target == ZTO)
    result = {
        "schema": "permission-revert-context-v1",
        "verdict": "aligned" if aligned else "mismatch",
        "token": token,
        "call_target": target,
        "permission_decision": permission.get("decision"),
        "revert_predicate": expectation.get("expect", {}).get("kind"),
        "scope": "Connects two historical review inputs only; it never authorizes a call or token movement.",
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if aligned else 1


if __name__ == "__main__":
    raise SystemExit(main())
