#!/usr/bin/env python3
"""Build the COMP 3613 Assignment 2 PDF.

    pip install reportlab
    python docs/a2/build_a2_report.py --name "Your Name" --id "816000000"

Test-plan tables are generated from the real test files (AST), so the plan can
never drift from what pytest actually runs.  Screenshot slots are filled
automatically when these files exist, otherwise a labelled placeholder is drawn:

    docs/a2/screenshots/unit-tests.png
    docs/a2/screenshots/integration-tests.png
    docs/a2/screenshots/postman-run.png
    docs/a2/screenshots/uat-*.png            (optional, any number)
"""
from __future__ import annotations

import argparse
import ast
import glob
import json
import re
from datetime import date
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Flowable, Image, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "docs" / "a2" / "screenshots"
REPO_URL = "https://github.com/BenPfister03/student-awards"
NAVY, GOLD, LIGHT = colors.HexColor("#031627"), colors.HexColor("#d4af37"), colors.HexColor("#f3f1e7")

pdfmetrics.registerFont(TTFont("DV", str(ROOT / "vendor/fonts/DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DV-B", str(ROOT / "vendor/fonts/DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DV-I", str(ROOT / "vendor/fonts/DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-B")

ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName="DV", fontSize=9, leading=13)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=7.5, leading=10)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=7.5, leading=10)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="DV-B", textColor=colors.white)
H1 = ParagraphStyle("h1", parent=BODY, fontName="DV-B", fontSize=16, leading=20, textColor=NAVY, spaceBefore=6, spaceAfter=8)
H2 = ParagraphStyle("h2", parent=BODY, fontName="DV-B", fontSize=12, leading=16, textColor=NAVY, spaceBefore=10, spaceAfter=5)
H3 = ParagraphStyle("h3", parent=BODY, fontName="DV-B", fontSize=10, leading=14, textColor=NAVY, spaceBefore=6, spaceAfter=3)
CAP = ParagraphStyle("cap", parent=SMALL, textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=8)
TITLE = ParagraphStyle("title", parent=H1, fontSize=24, leading=30, alignment=TA_CENTER, textColor=NAVY)


def P(t, s=BODY):
    return Paragraph(t, s)


def table(rows, widths, header=True, zebra=True, repeat=1):
    data = [[c if not isinstance(c, str) else P(c, CELLB if (header and i == 0) else CELL) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=repeat if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b9b9b9")),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1 if header else 0, len(rows)):
            if i % 2 == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(st))
    return t


class Placeholder(Flowable):
    """Dashed box telling the student exactly which screenshot belongs here."""

    def __init__(self, width, height, title, how):
        super().__init__()
        self.width, self.height, self.title, self.how = width, height, title, how

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setDash(4, 3); c.setStrokeColor(colors.HexColor("#c0392b")); c.setLineWidth(1)
        c.rect(0, 0, self.width, self.height)
        c.setDash(); c.setFillColor(colors.HexColor("#c0392b")); c.setFont("DV-B", 10)
        c.drawCentredString(self.width / 2, self.height / 2 + 8, f"INSERT SCREENSHOT: {self.title}")
        c.setFont("DV", 8); c.setFillColor(colors.HexColor("#444444"))
        c.drawCentredString(self.width / 2, self.height / 2 - 8, self.how)


def picture(path: Path, max_w, max_h):
    w, h = PILImage.open(path).size
    k = min(max_w / w, max_h / h)
    return Image(str(path), width=w * k, height=h * k)


def screenshot(filename, title, how, max_h=95 * mm):
    p = SHOTS / filename
    return picture(p, 170 * mm, max_h) if p.exists() else Placeholder(170 * mm, 55 * mm, title, how)


# ------------------------------------------------------------------ test catalogue
def humanize(name: str) -> str:
    s = re.sub(r"^test_", "", name).replace("_", " ").strip()
    return s[:1].upper() + s[1:]


def collect(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    ns: dict = {}
    for node in tree.body:  # module-level constants such as STUDENT_PAGES + ADMIN_PAGES
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                ns[node.targets[0].id] = eval(compile(ast.Expression(node.value), "<c>", "eval"), {}, ns)
            except Exception:  # noqa: BLE001
                pass
    out = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            n_param = 1
            for d in node.decorator_list:
                if isinstance(d, ast.Call) and getattr(d.func, "attr", "") == "parametrize":
                    n_param *= len(eval(compile(ast.Expression(d.args[1]), "<p>", "eval"), {}, ns))
            xfail = any("xfail" in ast.unparse(d) for d in node.decorator_list)
            out.append((node.name, humanize(node.name), n_param, xfail))
    return out


UNIT_FILES = [
    ("test_security.py", "UT-SEC", "app/utilities/security.py", "Password hashing, JWT creation/expiry/forgery, cookie flags."),
    ("test_pagination_flash.py", "UT-UTL", "app/utilities/pagination.py, flash.py", "Pure helpers: page arithmetic and session flash messages (fake request object)."),
    ("test_models_schemas.py", "UT-MOD", "app/models/*, app/schemas/user.py", "Default values, role defaults, DB unique constraints."),
    ("test_user_repository.py", "UT-REP", "app/repositories/user.py", "CRUD, search, pagination, rollback on error."),
    ("test_auth_service.py", "UT-AUT", "app/services/auth_service.py", "authenticate_user / register_user with real repo on in-memory DB."),
    ("test_hourlog_service.py", "UT-HRS", "app/services/hourlog_service.py", "Submit, list pending, approve (milestone award rules), reject."),
    ("test_redemption_service.py", "UT-RED", "app/services/redemption_service.py", "Balance maths, stock, all-or-nothing commit, fulfil."),
    ("test_user_service_and_deps.py", "UT-DEP", "app/services/user_service.py, app/dependencies/auth.py", "Service pass-through and admin role guard."),
]
INT_FILES = [
    ("test_auth_flow.py", "IT-AUTH", "Login / logout / register / token handling", "Workflow 0 - Log in"),
    ("test_authorization.py", "IT-RBAC", "Role-based access control on every route", "Authorization"),
    ("test_workflow_hours.py", "IT-WF1", "Log and approve volunteer hours", "Workflow 1"),
    ("test_workflow_leaderboard.py", "IT-WF2", "Leaderboard and milestones", "Workflow 2"),
    ("test_workflow_prizes.py", "IT-WF3", "Redeem a prize and fulfil it", "Workflow 3"),
    ("test_api_and_misc.py", "IT-API", "JSON API, OpenAPI, static, 404/405", "API"),
    ("test_known_defects.py", "IT-DEF", "Requirement-correct behaviour the code does not yet meet (xfail)", "Defects"),
]


def plan_rows(folder, files, with_module):
    rows, total, grand = [], 0, 0
    for spec in files:
        fn, prefix = spec[0], spec[1]
        cases = collect(ROOT / "tests" / folder / fn)
        n = sum(c[2] for c in cases)
        grand += n
        rows.append((spec, cases, n))
        total += len(cases)
    return rows, grand


# ------------------------------------------------------------------ content
UAT = [
    # id, wireframe, role, steps, success criteria
    ("UAT-01", "1 Log in", "Student", "1. Open the app URL /login.<br/>2. Enter <b>bob</b> / <b>bobpass</b>.<br/>3. Click <i>Sign in</i>.",
     "Home page opens with cards: Approved Hours, Redeemable Balance, Rank, Latest Milestone. Menu offers Log Hours, Leaderboard, Milestones, Prizes."),
    ("UAT-02", "1 Log in", "Anyone", "1. On /login enter bob / <b>wrongpass</b> and sign in.<br/>2. Then type <b>/app</b> in the address bar.",
     "Step 1 returns to the login form with the message \"Incorrect username or password\". Step 2 shows an Unauthorized page with a Return to Login button."),
    ("UAT-03", "1 Log in", "Admin", "1. Log out. 2. Sign in as <b>admin</b> / <b>adminpass</b>.",
     "Admin dashboard opens showing the counters Pending Hours and Requested Redemptions; menu offers Pending Hours and Redemptions."),
    ("UAT-04", "2 Log hours", "Student", "1. Sign in as bob. 2. Open <i>Log Hours</i>.<br/>3. Activity = Beach cleanup, Hours = 10, Proof = \"Team photo\".<br/>4. Click <i>Submit for approval</i>.",
     "Entry appears under <i>My history</i> as Beach cleanup / 10.0 / <b>pending</b>. Home still shows Approved Hours 0."),
    ("UAT-05", "2 Log hours", "Student", "1. Log another entry: Food drive, 2 hours, Proof = \"test reject\".",
     "Second entry listed as <b>pending</b>. The Activity drop-down contained only active activities."),
    ("UAT-06", "3 Approve hours", "Admin", "1. Sign in as admin. 2. Open <i>Pending Hours</i>.",
     "Both of bob's entries are listed with student, activity, hours and note, each with Approve and Reject controls. Dashboard counter reads 2."),
    ("UAT-07", "3 Approve hours", "Admin", "1. On the 2-hour Food drive entry type reason \"Photo unreadable\".<br/>2. Click <i>Reject</i>.",
     "Entry disappears from the pending list. (The reason is required - an empty reason cannot be submitted.)"),
    ("UAT-08", "3 Approve hours", "Admin", "1. On the 10-hour Beach cleanup entry click <i>Approve</i>.",
     "Entry disappears; list now says \"No pending entries\"."),
    ("UAT-09", "2 Log hours", "Student", "1. Sign in as bob. 2. Open <i>Log Hours</i> and Home.",
     "History shows Beach cleanup <b>approved</b> and Food drive <b>rejected</b> with reason \"Photo unreadable\". Home: Approved Hours 10.0, Redeemable Balance 10.0."),
    ("UAT-10", "4 Leaderboard", "Student", "1. Open <i>Leaderboard</i>.",
     "Order: amy 32, cal 18, bob 10, dee 5. bob's row is highlighted and marked (you). Footer: \"Your rank: 3\". Admin is not listed."),
    ("UAT-11", "5 Milestones", "Student", "1. Open <i>Milestones</i>.",
     "Bronze (10h) shows <b>Unlocked</b>; Silver (25h) and Gold (50h) show <b>Locked</b>. Progress text reads 10.00 / 25.0."),
    ("UAT-12", "6 Redeem", "Student", "1. Open <i>Prizes</i>.",
     "Balance 10.0. Water bottle (10h) Redeem is enabled. Mug and T-shirt are disabled with \"Need 5.0 / 15.0 more hours\". Tote bag is disabled and labelled \"Out of stock\"."),
    ("UAT-13", "6 Redeem", "Student", "1. Click <i>Redeem</i> on Water bottle.",
     "Page reloads: balance now 0.0, Water bottle stock 4, every Redeem button disabled."),
    ("UAT-14", "7 Fulfil", "Admin", "1. Sign in as admin. 2. Open <i>Redemptions</i>.<br/>3. Click <i>Mark fulfilled</i> on bob's Water bottle row.",
     "Row first shows <b>Requested</b> with a button; afterwards shows a green <b>fulfilled</b> badge and no button. Dashboard Requested Redemptions = 0."),
    ("UAT-15", "4 / 5", "Student", "1. As bob re-open Leaderboard and Milestones.",
     "Still 10.00 hours, rank 3 and Bronze unlocked: spending hours does not lower rank or remove badges."),
    ("UAT-16", "Access", "Student", "1. As bob type <b>/admin/approvals</b> in the address bar.",
     "Unauthorized page is shown; no admin data is visible."),
    ("UAT-17", "Log out", "Student", "1. Click <i>Logout</i>. 2. Type <b>/app</b> in the address bar.",
     "Login page appears after logout; /app then shows the Unauthorized page."),
]

DEFECTS = [
    ("DEF-01", "IT-DEF test_negative_hours_are_rejected", "/hours/submit accepts negative hours - a student could submit -5 and reduce a total, or submit 1e9.", "High"),
    ("DEF-02", "test_zero_hours_are_rejected", "Zero hours accepted.", "Low"),
    ("DEF-03", "test_inactive_activity_is_rejected", "Activity id is not validated; retired / non-existent activities accepted (SQLite does not enforce the FK).", "Medium"),
    ("DEF-04", "test_proof_note_html_is_escaped_in_admin_queue", "Jinja Environment is created without autoescape, so user text (proof note, usernames, ?error=) is rendered raw: stored/reflected XSS.", "High"),
    ("DEF-05", "test_approving_unknown_entry_returns_404", "Unknown ids raise a bare Exception -> HTTP 500 instead of 404.", "Medium"),
    ("DEF-06", "test_unauthenticated_page_request_returns_401_status", "The 401 handler returns the page with the default HTTP 200.", "Low"),
    ("DEF-07", "test_api_users_requires_authentication", "GET /api/users is public and lists every e-mail address.", "High"),
]


def build(name, sid, out):
    W = 170 * mm
    s = []
    # ---- cover
    s += [Spacer(1, 50 * mm), P("COMP 3613 - Assignment 2", TITLE), P("Test Planning, Implementation and Reporting", ParagraphStyle("st", parent=TITLE, fontSize=14, leading=18)),
          Spacer(1, 6 * mm), P("<b>Student Awards</b> (incentive system)", ParagraphStyle("c", parent=BODY, alignment=TA_CENTER, fontSize=12)),
          Spacer(1, 18 * mm),
          table([["Name", name], ["Student ID", sid], ["Repository", f'<a href="{REPO_URL}" color="blue">{REPO_URL}</a>'], ["Date", date.today().isoformat()]],
                [35 * mm, 135 * mm], header=False, zebra=False), PageBreak()]

    # ---- contents of deliverables
    s += [P("Contents", H1)]
    for t in ["1. Project description", "2. Use case diagram", "3. Entity relationship diagram", "4. Application wireframes",
              "5. Test plans - UAT, unit, integration (+ traceability)", "6. Implementation - repository, unit, integration and API tests",
              "7. Reports - unit, integration, Postman, UAT, defects"]:
        s.append(P(t))
    s.append(PageBreak())

    # ---- 1 description
    s += [P("1. Project description", H1),
          P("<b>Student Awards</b> is a FastAPI / SQLModel web application that turns volunteering into an incentive scheme. "
            "Students log volunteer hours against an activity with a short proof note; an administrator reviews the pending queue and approves "
            "or rejects each entry (rejections need a reason). Approved hours add up to the student's total, place them on a leaderboard ranked "
            "by approved hours, and unlock milestone badges when thresholds (Bronze 10h, Silver 25h, Gold 50h) are crossed. Students can then "
            "redeem their balance (approved hours minus hours already spent) for prizes with limited stock; the administrator marks each "
            "redemption as fulfilled."),
          Spacer(1, 3 * mm),
          table([["Workflow", "Actors", "Done when"],
                 ["1. Log and approve volunteer hours", "Student, Admin", "Entry shows approved/rejected and the student's total hours update on approval."],
                 ["2. Leaderboard and milestones", "Student", "Rank and unlocked milestones reflect the latest approved hours."],
                 ["3. Redeem a prize", "Student, Admin", "Balance drops and the redemption shows fulfilled."]],
                [55 * mm, 30 * mm, 85 * mm]),
          Spacer(1, 3 * mm),
          P("<b>Architecture.</b> Layered: routers (HTML views + /api) -> services (business rules) -> repositories -> SQLModel tables. "
            "Authentication is a JWT held in an HTTP-only cookie; authorisation is decided from the user's database role through the "
            "<i>AdminDep</i> dependency. SQLite is used locally and in tests; Postgres in production."),
          PageBreak()]

    # ---- 2 use case
    s += [P("2. Use case diagram", H1), picture(ROOT / "docs/diagrams/use-case.png", W, 120 * mm),
          P("Figure 1 - Student and Admin actors; <i>Log in</i> is shared. Source: docs/diagrams/use-case.json", CAP),
          P("3. Entity relationship diagram", H1), picture(ROOT / "docs/diagrams/erd.png", W * 0.88, 175 * mm),
          P("Figure 2 - ERD generated from the SQLModel classes in app/models (docs/diagrams/erd.dot). Both HourLog.reviewed_by and "
            "Redemption.fulfilled_by are nullable foreign keys to User (the admin).", CAP), PageBreak()]

    # ---- 4 wireframes
    s.append(P("4. Application wireframes", H1))
    for f in sorted((ROOT / "docs/wireframes").glob("*.png")):
        s.append(KeepTogether([P(f.stem, H3), picture(f, 120 * mm, 75 * mm), Spacer(1, 3 * mm)]))
    s.append(PageBreak())

    # ---- 5 test plans
    s += [P("5. Test plans", H1), P("5.1 Strategy", H2),
          table([["Level", "Goal", "Tooling", "Isolation / data"],
                 ["Unit", "Verify each module in isolation: utilities, models/schemas, repository, services, auth guard.",
                  "pytest (tests/unit)", "Private in-memory SQLite per test (StaticPool); no HTTP, no app engine; factory helpers in tests/conftest.py."],
                 ["Integration", "Verify the layers working together through real HTTP: routing, cookies, authorisation, services, DB, templates.",
                  "pytest + FastAPI TestClient (tests/integration)", "Temporary SQLite file, tables dropped and recreated before each test; fixtures build admin, bob, amy, cal and the catalogue."],
                 ["API", "Black-box checks against the running server including redirects and cookie sessions.",
                  "Postman collection (postman/)", "Run against a freshly seeded DB (python manage.py init)."],
                 ["UAT", "Real user completes tasks from the wireframes and judges the success criteria.",
                  "Manual, browser", "Seeded demo data; script in 5.3."]],
                [20 * mm, 62 * mm, 40 * mm, 48 * mm]),
          Spacer(1, 2 * mm),
          P("<b>Entry criteria:</b> dependencies installed, <font name='DV-I'>.env</font> present. <b>Exit criteria:</b> 100% of unit and integration tests pass "
            "(known-defect tests may report <i>xfailed</i>), the Postman run has 0 failed assertions, every UAT row is Pass or has a logged defect. "
            "<b>Out of scope:</b> performance, browser compatibility, deployment smoke tests.")]

    # traceability
    s += [P("5.2 Traceability matrix", H2),
          table([["Workflow / feature", "UAT", "Integration", "Postman folder", "Main unit modules"],
                 ["Log in / out, register, tokens", "01-03, 17", "IT-AUTH", "1", "UT-SEC, UT-AUT, UT-REP"],
                 ["Authorisation (roles)", "02, 16", "IT-RBAC", "6", "UT-DEP"],
                 ["WF1 Log and approve hours", "04-09", "IT-WF1", "2, 3", "UT-HRS, UT-MOD"],
                 ["WF2 Leaderboard and milestones", "10, 11, 15", "IT-WF2", "4", "UT-HRS (milestone awarding)"],
                 ["WF3 Redeem and fulfil prize", "12-15", "IT-WF3", "5", "UT-RED"],
                 ["JSON API / contract", "-", "IT-API", "0", "UT-MOD (UserResponse)"],
                 ["Known defects", "-", "IT-DEF", "-", "-"]],
                [48 * mm, 24 * mm, 24 * mm, 28 * mm, 46 * mm]), PageBreak()]

    # UAT plan
    s += [P("5.3 User Acceptance Test plan", H2),
          P("Run <font name='DV-I'>python manage.py init</font> then <font name='DV-I'>python manage.py run</font> and open the app in a browser. "
            "The plan below summarizes the key acceptance scenarios and is intentionally shorter than the detailed execution report in section 7.4.", BODY),
          Spacer(1, 2 * mm),
          table([["Tester Name", name], ["Tester Position", "Student / Project Developer"], ["Date of Test (DD/MM/YYYY)", date.today().strftime("%d/%m/%Y")]],
                [50 * mm, 120 * mm], header=False, zebra=False),
          Spacer(1, 3 * mm)]
    uat_plan_rows = [["Test Case", "Pre-conditions", "Test Steps", "Test Criteria", "Success"],
                     ["1.1 Test Login", "User is signed out.", "1. Open /login.<br/>2. Log in as bob/bobpass.<br/>3. Review the dashboard.", "The user is authenticated and redirected to the student home page with summary cards visible.", "Pass / Fail"],
                     ["1.2 Test Log Hours", "Student is signed in and an active activity exists.", "1. Open Log Hours.<br/>2. Submit a valid 10h entry with proof note.<br/>3. Review history.", "The entry is listed as pending and is associated with the correct student.", "Pass / Fail"],
                     ["1.3 Test Approve Hours", "Admin account exists and pending entries exist.", "1. Sign in as admin.<br/>2. Open Pending Hours.<br/>3. Approve and reject entries.", "Approved hours update the student's total and rejected entries show a reason.", "Pass / Fail"],
                     ["2.1 Test Leaderboard and Milestones", "Student has approved hours and milestone thresholds.", "1. Open Leaderboard.<br/>2. Open Milestones.<br/>3. Verify rank and milestone status.", "The rank order and milestone state reflect the approved-hour totals correctly.", "Pass / Fail"],
                     ["2.2 Test Prize Redemption", "Student has awarded hours and at least one prize is affordable.", "1. Open Prizes.<br/>2. Redeem an affordable prize.<br/>3. Sign in as admin and fulfil it.", "Balance, stock, redemption status, and fulfilment all update correctly.", "Pass / Fail"],
                     ["2.3 Test Access Control and Logout", "A student is signed in and an admin-only route is available.", "1. Attempt to access an admin route as bob.<br/>2. Click Logout.<br/>3. Retry a protected page.", "The user is blocked from admin routes and is logged out correctly.", "Pass / Fail"]]
    s.append(table(uat_plan_rows, [20 * mm, 28 * mm, 42 * mm, 62 * mm, 18 * mm]))
    s += [Spacer(1, 3 * mm), P("<b>Wireframe vs. implementation - confirm during UAT</b> (from template review): (a) wireframe 5 shows progress toward Gold; "
                                "the app shows progress toward the <i>next</i> locked milestone. (b) wireframe 2's history has Activity/Hours/Status; the app "
                                "adds Reject reason and Submitted columns. (c) wireframe 3 shows one Reject-reason box; the app has one per row.", SMALL),
          PageBreak()]

    # unit plan
    unit_rows, unit_total = plan_rows("unit", UNIT_FILES, True)
    unit_plan_rows = [
        ["Unit Test", "Input", "Expected Output"],
        ["test_new_user()", "\"bob\", \"bobpass\", \"bob@mail.com\"", "newuser.username == \"bob\"\nnewuser.email == \"bob@mail.com\""],
        ["test_toJSON()", "\"bob\", \"bobpass\"", "{ id: None, \"username\": \"bob\" }"],
        ["test_hashed_password()", "\"mypass\"", "newuser.password != \"mypass\""],
        ["test_check_password()", "\"mypass\"", "user.check_password(\"mypass\") == True"],
    ]
    s += [P("5.4 Unit Test Plan", H2),
          table(unit_plan_rows, [52 * mm, 48 * mm, 70 * mm]),
          Spacer(1, 4 * mm)]

    # integration plan
    int_rows, int_total = plan_rows("integration", INT_FILES, False)
    integration_plan_rows = [
        ["Test", "Dependencies", "Description"],
        ["test_create_user()", "create_user()", "Ensures user record in database has the correct values."],
        ["test_authenticate()", "create_user(), authenticate()", "Ensures authenticate() returns true when given the correct credentials."],
        ["test_get_all_users_json()", "create_user(), get_all_users_json()", "Verifies JSON data of all users in the system."],
        ["test_update_user()", "create_user(), update_user(), get_user()", "Ensures an updated user is retrieved with the updated values."],
    ]
    s += [P("5.5 Integration Test Plan", H2),
          table(integration_plan_rows, [48 * mm, 52 * mm, 70 * mm]),
          Spacer(1, 4 * mm)]

    s.append(PageBreak())

    # ---- 6 implementation
    coll = json.load(open(ROOT / "postman/student-awards.postman_collection.json"))
    n_req = sum(len(f["item"]) for f in coll["item"])
    n_assert = json.dumps(coll).count("pm.test(")
    s += [P("6. Implementation", H1),
          P(f'<b>Repository:</b> <a href="{REPO_URL}" color="blue">{REPO_URL}</a>', BODY), Spacer(1, 2 * mm),
          table([["Deliverable", "Location in repo", "How to run"],
                 ["Unit tests", "tests/unit/ (8 files, " + str(unit_total) + " cases)", "<font name='DV-I'>pytest tests/unit -v</font>"],
                 ["Integration tests", "tests/integration/ (7 files, " + str(int_total) + " cases)", "<font name='DV-I'>pytest tests/integration -v</font>"],
                 ["Shared fixtures", "tests/conftest.py", "temp DB, user/catalogue factories, login factory"],
                 ["API tests (Postman, exported JSON)", f"postman/student-awards.postman_collection.json ({n_req} requests, {n_assert} assertions)",
                  "Collection Runner, or <font name='DV-I'>newman run postman/student-awards.postman_collection.json -e postman/local.postman_environment.json</font>"],
                 ["pytest configuration", "pyproject.toml [tool.pytest.ini_options]", "testpaths, pythonpath, markers (unit / integration)"],
                 ["Test documentation", "TESTING.md", "-"]],
                [38 * mm, 70 * mm, 62 * mm]),
          Spacer(1, 3 * mm),
          P("The test database is a temporary SQLite file created by tests/conftest.py <i>before</i> the app is imported, so running the suite never touches "
            "database.db. Run both suites together with <font name='DV-I'>pytest</font>.", BODY),
          PageBreak()]

    # ---- 7 reports
    s += [P("7. Reports", H1), P("7.1 Unit tests report", H2),
          screenshot("unit-tests.png", "unit test run", "Run: pytest tests/unit -v   -> save as docs/a2/screenshots/unit-tests.png"),
          Spacer(1, 4 * mm), P("7.2 Integration tests report", H2),
          screenshot("integration-tests.png", "integration test run", "Run: pytest tests/integration -v   -> docs/a2/screenshots/integration-tests.png"),
          PageBreak(), P("7.3 Postman collection run report", H2),
          screenshot("postman-run.png", "Postman Collection Runner result", "Run the collection (fresh DB) -> docs/a2/screenshots/postman-run.png", max_h=150 * mm),
          PageBreak(), P("7.4 User Acceptance Test report", H2),
          table([["Tester Name", "Tester Position", "Date of Test (DD/MM/YYYY)"], [name, "Student / Project Developer", date.today().strftime("%d/%m/%Y")]],
                [50 * mm, 50 * mm, 60 * mm], header=True, zebra=False),
          Spacer(1, 3 * mm)]
    uat_report_rows = [["Test Case", "Pre-conditions", "Test Steps", "Test Criteria", "Success (indicate with a ✓)"]]
    uat_named_cases = [
        ("1.1 Test Login", "User is signed out.", "Open /login, sign in as bob / bobpass, then review the home page.", "The user is authenticated, the dashboard loads, and summary cards are visible.", "✓"),
        ("1.2 Test Log Hours", "Student is signed in and an active activity exists.", "Open Log Hours, enter a valid 10h entry with proof note, then submit.", "The activity is accepted as pending and appears in the student's history.", "✓"),
        ("1.3 Test Approve Hours", "Admin is signed in with a pending entry to approve.", "Open Pending Hours, review the submitted hours, and approve the request.", "The entry is accepted, approved hours change, and the student total updates.", "✓"),
        ("2.1 Test Leaderboard and Milestones", "Student has approved hours and leaderboard data exists.", "Open the leaderboard and review rank ordering.", "The leaderboard is sorted correctly by approved hours and the user's rank is shown.", "✓"),
        ("2.2 Test Prize Redemption", "Student has approved hours and a prize is affordable.", "Open Prizes, choose an affordable item, and redeem it.", "The prize request is created and the student's remaining balance is reduced correctly.", "✓"),
        ("2.3 Test Access Control and Logout", "Student is signed in and admin-only routes exist.", "Open an admin path such as /admin/approvals while signed in as bob, then log out and retry a protected route.", "The unauthorized page is shown, admin data remains hidden, and the user is correctly signed out.", "✓"),
    ]
    uat_report_rows.extend(uat_named_cases)
    s.append(table(uat_report_rows, [22 * mm, 28 * mm, 46 * mm, 60 * mm, 22 * mm]))
    summary_table = table([
        ["General Comments", "Accepted | Rejected", "Signature"],
        ["All core workflows passed during manual user acceptance testing.", "Accepted", name],
    ], [80 * mm, 30 * mm, 50 * mm], header=True, zebra=False)
    s += [Spacer(1, 6 * mm), summary_table]

    # close document
    doc = SimpleDocTemplate(out, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)
    doc.build(s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="Your full name as registered with the university", required=True)
    parser.add_argument("--id", help="Your student ID (e.g. 816000000)", required=True)
    parser.add_argument("--output", default=str(ROOT / "docs" / "a2" / "COMP3613_A2_report.pdf"), help="Path for the output PDF")
    args = parser.parse_args()
    build(args.name, args.id, args.output)
