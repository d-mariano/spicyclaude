# Progress 001

Test command (run from `spicy-ship/scripts`): `python3 -m unittest discover -s tests -t .`

| Task | Commit | Result |
|---|---|---|
| 1.0 Print the gate flags line for a reviewer | 7b797da | RED: 12 failures (80 run). GREEN after 1.2: only the 4 AC-3 subTests erroring on KeyError, as the plan predicted |
| 2.0 Fail loud on an unknown reviewer | 7b797da | Ran 80 tests, OK |

The plan calls for one commit after task 2.2, so both parents share it:
`feat: add --gate-flags to ship_config for review_gate flags`.

Baseline before changes: 70 tests, OK. Final: 80 tests, OK.

Order note: the AC-3 test (`test_unknown_reviewer_fails_loud`) was written together with the 1.1 tests, so the RED run showed it failing on assertions. It went from FAIL to ERROR (KeyError) to green across 1.2 and 2.2.

No autonomous decisions were needed beyond D1 to D6 in the plan.
