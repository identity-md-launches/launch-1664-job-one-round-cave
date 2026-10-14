# Permission Revert Context

This offline glue checks that Line 2's ZTO permission-gate report and Line 4's
ZTO revert expectation name the same real Ethereum token and chain. It keeps a
worker from casually joining evidence about different targets. It does not
authorize a call, assess the allowance findings, or make a historical report
current.

From the repository root:

```sh
python3 -B shared/permission-revert-context/permission_revert_context.py
```

The bundled real historical inputs print `"verdict": "aligned"`: the
permission report is a deny result and the rehearsal expectation is only the
weak `reported_revert` predicate for ZTO. The command is standard-library
Python, does no network I/O, and reads only the two explicit workspace files.
