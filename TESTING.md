# Testing - COMP 3613 Assignment 2

| Level | Where | Command |
|---|---|---|
| Unit | `tests/unit/` | `pytest tests/unit -v` |
| Integration | `tests/integration/` | `pytest tests/integration -v` |
| Everything | `tests/` | `pytest` |
| API (Postman) | `postman/student-awards.postman_collection.json` | Postman Collection Runner, or `newman run postman/student-awards.postman_collection.json -e postman/local.postman_environment.json` |
| UAT | `docs/a2/A2_Report.pdf` section 5.3 | manual, in a browser |

Run everything from the **project root** (templates are loaded from `app/templates`).

```bash
pip install -r requirements.txt
pytest                      # unit + integration
pytest -m unit              # same as tests/unit
pytest -m integration       # same as tests/integration
pytest -rx                  # also list the xfailed known-defect tests
```

## How the tests are isolated
`tests/conftest.py` sets `DATABASE_URI` to a throw-away SQLite file **before** the app is imported, so your
`database.db` is never touched. Unit tests use their own in-memory SQLite engine. Integration tests drop and recreate
the tables before every test and drive the real app through FastAPI's `TestClient`.

## Postman
1. `python manage.py init` (drops and reseeds the database) then `python manage.py run`.
2. Import `postman/student-awards.postman_collection.json` (and optionally `postman/local.postman_environment.json`).
3. Open the Collection Runner, keep **Save cookies** on, run all folders in order. Re-run `python manage.py init` before every run.

The requests are ordered: login cookies, pending-entry ids and redemption ids are carried from one request to the next.

## Known defects
`tests/integration/test_known_defects.py` holds `xfail` tests that describe correct behaviour the app does not have yet
(negative hours accepted, autoescape off, `/api/users` public, ...). Fix a defect, and its test turns into `XPASS` -
delete the `xfail` marker then.

## Building the PDF report
```bash
pip install reportlab
# save screenshots to docs/a2/screenshots/: unit-tests.png, integration-tests.png, postman-run.png (+ optional uat-*.png)
python docs/a2/build_a2_report.py --name "Your Name" --id "816000000"
```
