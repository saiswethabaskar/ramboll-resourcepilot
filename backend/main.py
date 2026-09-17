from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import random
from datetime import datetime


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Ramboll ResourcePilot",
    description="Intelligent Resourcing & Allocation Suggestion Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "resourcepilot.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS people (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        grade TEXT NOT NULL,
        location TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        skills TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        owner TEXT NOT NULL,
        risk TEXT NOT NULL,
        budget REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id TEXT,
        project_id TEXT,
        hours INTEGER
    );

    CREATE TABLE IF NOT EXISTS requests (
        id TEXT PRIMARY KEY,
        project_id TEXT,
        role TEXT,
        skills TEXT,
        hours INTEGER,
        duration INTEGER,
        budget REAL,
        risk TEXT
    );

    CREATE TABLE IF NOT EXISTS proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT,
        person_id TEXT,
        score REAL,
        health TEXT,
        estimated_cost REAL,
        reasoning TEXT,
        status TEXT DEFAULT 'PENDING'
    );

    CREATE TABLE IF NOT EXISTS approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proposal_id INTEGER,
        owner TEXT,
        decision TEXT,
        reason TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS reallocation_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id TEXT NOT NULL,
        from_project_id TEXT NOT NULL,
        to_project_id TEXT NOT NULL,
        hours INTEGER NOT NULL,
        reason TEXT,
        releasing_owner TEXT,
        receiving_owner TEXT,
        releasing_decision TEXT DEFAULT 'PENDING',
        receiving_decision TEXT DEFAULT 'PENDING',
        status TEXT DEFAULT 'PENDING',
        created_at TEXT
    );
    """)

    conn.commit()

    count = cur.execute(
        "SELECT COUNT(*) FROM people"
    ).fetchone()[0]

    if count == 0:
        seed_data(conn)

    conn.close()


# ============================================================
# SAMPLE DATA
# ============================================================

def seed_data(conn):

    cur = conn.cursor()

    roles = [
        "Structural Engineer",
        "Civil Engineer",
        "Environmental Engineer",
        "Data Analyst",
        "Project Planner",
        "GIS Specialist",
        "Technical Reviewer"
    ]

    locations = [
        "Chennai",
        "Bangalore",
        "Hyderabad"
    ]

    skill_pool = [
        "AutoCAD",
        "Civil 3D",
        "Structural Analysis",
        "Python",
        "Data Analysis",
        "GIS",
        "Project Planning",
        "Technical Review",
        "Environmental Assessment",
        "BIM",
        "Risk Assessment",
        "Engineering Design"
    ]

    grades = [
        "Junior",
        "Mid",
        "Senior"
    ]

    role_skills = {
        "Structural Engineer": [
            "Structural Analysis",
            "AutoCAD",
            "Engineering Design",
            "BIM"
        ],
        "Civil Engineer": [
            "Civil 3D",
            "AutoCAD",
            "Engineering Design",
            "BIM"
        ],
        "Environmental Engineer": [
            "Environmental Assessment",
            "Risk Assessment",
            "GIS"
        ],
        "Data Analyst": [
            "Python",
            "Data Analysis",
            "Risk Assessment"
        ],
        "Project Planner": [
            "Project Planning",
            "Risk Assessment",
            "Data Analysis"
        ],
        "GIS Specialist": [
            "GIS",
            "Data Analysis",
            "Environmental Assessment"
        ],
        "Technical Reviewer": [
            "Technical Review",
            "Risk Assessment",
            "Engineering Design"
        ]
    }

    random.seed(42)

    # ========================================================
    # 30 PEOPLE
    # ========================================================

    first_names = [
        "Ananya",
        "Arjun",
        "Priya",
        "Rahul",
        "Meera",
        "Karthik"
    ]

    last_names = [
        "Rao",
        "Sharma",
        "Iyer",
        "Kumar",
        "Nair"
    ]

    for i in range(1, 31):

        role = roles[(i - 1) % len(roles)]
        grade = grades[(i - 1) % len(grades)]
        location = locations[(i - 1) % len(locations)]

        skills = role_skills[role].copy()

        if i % 4 == 0:

            extra_skill = skill_pool[
                i % len(skill_pool)
            ]

            if extra_skill not in skills:
                skills.append(extra_skill)

        capacity = 40

        name = (
            f"{first_names[i % len(first_names)]} "
            f"{last_names[i % len(last_names)]}"
        )

        cur.execute("""
            INSERT INTO people
            (
                id,
                name,
                role,
                grade,
                location,
                capacity,
                skills
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"P{i:03}",
            name,
            role,
            grade,
            location,
            capacity,
            ",".join(sorted(set(skills)))
        ))

    # ========================================================
    # PROJECTS
    # ========================================================

    projects = [
        (
            "PRJ001",
            "Bridge Design Assessment",
            "Priya Shah",
            "HIGH",
            8500
        ),
        (
            "PRJ002",
            "Green Infrastructure",
            "Rahul Menon",
            "MEDIUM",
            7000
        ),
        (
            "PRJ003",
            "Urban Mobility Study",
            "Meera Iyer",
            "MEDIUM",
            6000
        ),
        (
            "PRJ004",
            "Environmental Impact Study",
            "Arjun Rao",
            "HIGH",
            9000
        ),
        (
            "PRJ005",
            "Water Systems Planning",
            "Ananya Kumar",
            "LOW",
            5000
        ),
        (
            "PRJ006",
            "Digital Engineering Pilot",
            "Karthik Nair",
            "LOW",
            6500
        )
    ]

    for project in projects:

        cur.execute("""
            INSERT INTO projects
            (
                id,
                name,
                owner,
                risk,
                budget
            )
            VALUES (?, ?, ?, ?, ?)
        """, project)

    # ========================================================
    # EXISTING ALLOCATIONS
    # ========================================================

    allocation_id = 1

    for i in range(1, 31):

        project = projects[
            (i - 1) % len(projects)
        ]

        hours = [
            16,
            20,
            24,
            28,
            32
        ][i % 5]

        cur.execute("""
            INSERT INTO allocations
            (
                id,
                person_id,
                project_id,
                hours
            )
            VALUES (?, ?, ?, ?)
        """, (
            allocation_id,
            f"P{i:03}",
            project[0],
            hours
        ))

        allocation_id += 1

        # Some employees work across two projects.
        if i % 3 == 0:

            second_project = projects[
                i % len(projects)
            ]

            cur.execute("""
                INSERT INTO allocations
                (
                    id,
                    person_id,
                    project_id,
                    hours
                )
                VALUES (?, ?, ?, ?)
            """, (
                allocation_id,
                f"P{i:03}",
                second_project[0],
                8
            ))

            allocation_id += 1

    # ========================================================
    # OPEN REQUESTS
    # ========================================================

    requests = [

        (
            "REQ001",
            "PRJ001",
            "Structural Engineer",
            "Structural Analysis,AutoCAD",
            16,
            4,
            5000,
            "HIGH"
        ),

        (
            "REQ002",
            "PRJ002",
            "Environmental Engineer",
            "Environmental Assessment,GIS",
            12,
            6,
            4500,
            "MEDIUM"
        ),

        (
            "REQ003",
            "PRJ003",
            "Data Analyst",
            "Python,Data Analysis",
            16,
            5,
            5200,
            "MEDIUM"
        ),

        (
            "REQ004",
            "PRJ004",
            "Technical Reviewer",
            "Technical Review,Risk Assessment",
            8,
            3,
            3000,
            "HIGH"
        ),

        (
            "REQ005",
            "PRJ005",
            "Project Planner",
            "Project Planning,Risk Assessment",
            8,
            4,
            2800,
            "LOW"
        ),

        (
            "REQ006",
            "PRJ006",
            "Civil Engineer",
            "Civil 3D,AutoCAD",
            20,
            6,
            6500,
            "MEDIUM"
        )
    ]

    for request in requests:

        cur.execute("""
            INSERT INTO requests
            (
                id,
                project_id,
                role,
                skills,
                hours,
                duration,
                budget,
                risk
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, request)

    conn.commit()


initialize_database()


# ============================================================
# AVAILABILITY
# ============================================================

def calculate_availability(person_id):

    conn = get_db()

    person = conn.execute("""
        SELECT capacity
        FROM people
        WHERE id=?
    """, (
        person_id,
    )).fetchone()

    if not person:

        conn.close()

        return 0

    allocated = conn.execute("""
        SELECT COALESCE(SUM(hours), 0) AS total
        FROM allocations
        WHERE person_id=?
    """, (
        person_id,
    )).fetchone()["total"]

    conn.close()

    return max(
        0,
        person["capacity"] - allocated
    )


# ============================================================
# COST
# ============================================================

def calculate_cost(
    person,
    hours,
    duration
):

    rates = {

        ("Junior", "Chennai"): 30,
        ("Mid", "Chennai"): 45,
        ("Senior", "Chennai"): 65,

        ("Junior", "Bangalore"): 32,
        ("Mid", "Bangalore"): 48,
        ("Senior", "Bangalore"): 70,

        ("Junior", "Hyderabad"): 28,
        ("Mid", "Hyderabad"): 44,
        ("Senior", "Hyderabad"): 62
    }

    hourly_rate = rates.get(
        (
            person["grade"],
            person["location"]
        ),
        45
    )

    return (
        hourly_rate *
        hours *
        duration
    )


# ============================================================
# CANDIDATE EVALUATION
# ============================================================

def evaluate_candidate(
    request,
    person
):

    required_skills = set(
        s.strip().lower()
        for s in request["skills"].split(",")
        if s.strip()
    )

    candidate_skills = set(
        s.strip().lower()
        for s in person["skills"].split(",")
        if s.strip()
    )

    matched = (
        required_skills
        .intersection(candidate_skills)
    )

    skill_score = (
        len(matched) /
        len(required_skills) *
        100
        if required_skills
        else 0
    )

    available = calculate_availability(
        person["id"]
    )

    # ========================================================
    # AVAILABILITY SCORE
    # ========================================================

    if available >= request["hours"]:

        availability_score = 100

    elif available > 0:

        availability_score = (
            available /
            request["hours"] *
            100
        )

    else:

        availability_score = 0

    # ========================================================
    # COST
    # ========================================================

    usable_hours = min(
        available,
        request["hours"]
    )

    cost = calculate_cost(
        person,
        usable_hours,
        request["duration"]
    )

    if request["budget"] > 0:

        budget_score = max(
            0,
            min(
                100,
                (
                    1 -
                    max(
                        0,
                        cost -
                        request["budget"]
                    )
                    /
                    request["budget"]
                )
                *
                100
            )
        )

    else:

        budget_score = 0

    # ========================================================
    # SPLIT / WORKABILITY
    # ========================================================

    if available >= request["hours"]:

        split_score = 100

        split_note = (
            "Full requested capacity is available."
        )

        action = "FULL_ASSIGNMENT"

    elif available >= request["hours"] * 0.5:

        split_score = 70

        split_note = (
            f"Partial capacity available "
            f"({available}h); split may be workable."
        )

        action = "PARTIAL_SPLIT"

    elif available > 0:

        split_score = 35

        split_note = (
            f"Only {available}h available; "
            "high fragmentation risk."
        )

        action = "REVIEW_SPLIT"

    else:

        split_score = 0

        split_note = (
            "No remaining capacity."
        )

        action = "NOT_WORKABLE"

    # ========================================================
    # DELIVERY RISK
    # ========================================================

    risk_score = 80

    if request["risk"] == "HIGH":

        if person["grade"] == "Senior":

            risk_score = 100

        elif person["grade"] == "Mid":

            risk_score = 75

        else:

            risk_score = 45

    elif request["risk"] == "MEDIUM":

        if person["grade"] == "Senior":

            risk_score = 95

        elif person["grade"] == "Mid":

            risk_score = 85

        else:

            risk_score = 65

    else:

        if person["grade"] == "Senior":

            risk_score = 90

        elif person["grade"] == "Mid":

            risk_score = 80

        else:

            risk_score = 70

    # ========================================================
    # OVERALL SCORE
    #
    # Skill         30%
    # Availability  25%
    # Budget        15%
    # Risk          20%
    # Split         10%
    # ========================================================

    overall = (

        skill_score * 0.30 +

        availability_score * 0.25 +

        budget_score * 0.15 +

        risk_score * 0.20 +

        split_score * 0.10
    )

    # ========================================================
    # PROPOSAL HEALTH
    # ========================================================

    if (
        skill_score >= 75
        and availability_score >= 75
        and budget_score >= 80
        and split_score >= 70
        and risk_score >= 70
    ):

        health = "GOOD"

    elif (
        skill_score >= 50
        and availability_score > 0
    ):

        health = "REVIEW"

    else:

        health = "UNSAFE"

    # ========================================================
    # REASONING
    # ========================================================

    reasons = []

    reasons.append(
        f"{len(matched)}/{len(required_skills)} "
        "required skills matched"
    )

    reasons.append(
        f"{available} hours/week actual capacity available"
    )

    if cost <= request["budget"]:

        reasons.append(
            "Estimated cost is within project budget"
        )

    else:

        reasons.append(
            "Estimated cost exceeds the project budget"
        )

    reasons.append(
        split_note
    )

    if request["risk"] == "HIGH":

        if person["grade"] == "Senior":

            reasons.append(
                "Senior grade provides stronger "
                "suitability for a high-risk project"
            )

        else:

            reasons.append(
                "High-risk project requires "
                "additional qualification review"
            )

    # ========================================================
    # TRADE-OFF
    # ========================================================

    if (
        cost > request["budget"]
        and risk_score >= 90
    ):

        trade_off = (
            "Higher delivery suitability comes "
            "with a higher estimated cost."
        )

    elif (
        cost <= request["budget"]
        and risk_score < 60
    ):

        trade_off = (
            "Lower cost is affordable, but delivery "
            "risk requires additional review."
        )

    elif (
        available < request["hours"]
        and available > 0
    ):

        trade_off = (
            "Candidate is partially available; "
            "a split reduces immediate capacity risk "
            "but may increase fragmentation."
        )

    else:

        trade_off = (
            "No major cost-versus-delivery "
            "trade-off identified."
        )

    return {

        "person_id": person["id"],

        "name": person["name"],

        "role": person["role"],

        "grade": person["grade"],

        "location": person["location"],

        "skill_score": round(
            skill_score,
            1
        ),

        "availability": available,

        "availability_score": round(
            availability_score,
            1
        ),

        "estimated_cost": round(
            cost,
            2
        ),

        "budget_score": round(
            budget_score,
            1
        ),

        "split_score": round(
            split_score,
            1
        ),

        "risk_score": round(
            risk_score,
            1
        ),

        "overall_score": round(
            overall,
            1
        ),

        "health": health,

        "recommended_action": action,

        "trade_off": trade_off,

        "reasoning": reasons
    }


# ============================================================
# BASIC API
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Ramboll ResourcePilot API is running",
        "status": "healthy"
    }


@app.get("/people")
def get_people():

    conn = get_db()

    people = conn.execute("""
        SELECT *
        FROM people
        ORDER BY name
    """).fetchall()

    conn.close()

    return [
        dict(person)
        for person in people
    ]


@app.get("/requests")
def get_requests():

    conn = get_db()

    requests = conn.execute("""
        SELECT
            r.*,
            p.name AS project_name,
            p.owner AS project_owner,
            p.risk AS project_risk
        FROM requests r
        JOIN projects p
            ON r.project_id = p.id
        ORDER BY r.id
    """).fetchall()

    conn.close()

    return [
        dict(request)
        for request in requests
    ]


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/dashboard")
def dashboard():

    conn = get_db()

    result = {

        "people": conn.execute("""
            SELECT COUNT(*)
            FROM people
        """).fetchone()[0],

        "projects": conn.execute("""
            SELECT COUNT(*)
            FROM projects
        """).fetchone()[0],

        "open_requests": conn.execute("""
            SELECT COUNT(*)
            FROM requests
        """).fetchone()[0],

        "pending_proposals": conn.execute("""
            SELECT COUNT(*)
            FROM proposals
            WHERE status='PENDING'
        """).fetchone()[0]
    }

    conn.close()

    return result


# ============================================================
# GENERATE PROPOSALS
# ============================================================

@app.get("/requests/{request_id}/proposals")
def get_proposals(
    request_id: str
):

    conn = get_db()

    request = conn.execute("""
        SELECT *
        FROM requests
        WHERE id=?
    """, (
        request_id,
    )).fetchone()

    if not request:

        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Resourcing request not found"
        )

    people = conn.execute("""
        SELECT *
        FROM people
    """).fetchall()

    conn.close()

    proposals = []

    for person in people:

        result = evaluate_candidate(
            request,
            person
        )

        if (
            result["skill_score"] > 0
            and result["availability"] > 0
        ):

            proposals.append(result)

    proposals.sort(
        key=lambda x:
        x["overall_score"],
        reverse=True
    )

    top_proposals = proposals[:5]

    conn = get_db()

    for proposal in top_proposals:

        existing = conn.execute("""
            SELECT *
            FROM proposals
            WHERE request_id=?
            AND person_id=?
            ORDER BY id DESC
            LIMIT 1
        """, (
            request_id,
            proposal["person_id"]
        )).fetchone()

        reasoning_text = " | ".join(
            proposal["reasoning"]
        )

        if existing:

            if existing["status"] == "PENDING":

                conn.execute("""
                    UPDATE proposals
                    SET
                        score=?,
                        health=?,
                        estimated_cost=?,
                        reasoning=?
                    WHERE id=?
                """, (
                    proposal["overall_score"],
                    proposal["health"],
                    proposal["estimated_cost"],
                    reasoning_text,
                    existing["id"]
                ))

            proposal["proposal_id"] = (
                existing["id"]
            )

            proposal["status"] = (
                existing["status"]
            )

        else:

            cursor = conn.execute("""
                INSERT INTO proposals
                (
                    request_id,
                    person_id,
                    score,
                    health,
                    estimated_cost,
                    reasoning,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
            """, (
                request_id,
                proposal["person_id"],
                proposal["overall_score"],
                proposal["health"],
                proposal["estimated_cost"],
                reasoning_text
            ))

            proposal["proposal_id"] = (
                cursor.lastrowid
            )

            proposal["status"] = "PENDING"

    conn.commit()

    for proposal in top_proposals:

        saved = conn.execute("""
            SELECT id, status
            FROM proposals
            WHERE request_id=?
            AND person_id=?
            ORDER BY id DESC
            LIMIT 1
        """, (
            request_id,
            proposal["person_id"]
        )).fetchone()

        if saved:

            proposal["proposal_id"] = (
                saved["id"]
            )

            proposal["status"] = (
                saved["status"]
            )

    conn.close()

    return {
        "request_id": request_id,
        "proposal_count": len(top_proposals),
        "proposals": top_proposals
    }


# ============================================================
# ALL PROPOSALS
# ============================================================

@app.get("/proposals")
def all_proposals():

    conn = get_db()

    proposals = conn.execute("""
        SELECT
            pr.id AS proposal_id,
            pr.request_id,
            pr.person_id,
            p.name,
            p.role,
            p.grade,
            p.location,
            pr.score,
            pr.health,
            pr.estimated_cost,
            pr.reasoning,
            pr.status,
            r.project_id,
            proj.name AS project_name,
            proj.owner AS project_owner
        FROM proposals pr
        JOIN people p
            ON pr.person_id = p.id
        JOIN requests r
            ON pr.request_id = r.id
        JOIN projects proj
            ON r.project_id = proj.id
        ORDER BY pr.score DESC
    """).fetchall()

    conn.close()

    return [
        dict(proposal)
        for proposal in proposals
    ]


# ============================================================
# APPROVAL WORKFLOW
# ============================================================

class ApprovalRequest(BaseModel):

    owner: str
    decision: str
    reason: str = ""


@app.post("/proposals/{proposal_id}/decision")
def decide_proposal(
    proposal_id: int,
    request: ApprovalRequest
):

    decision = (
        request.decision
        .upper()
        .strip()
    )

    if decision not in [
        "APPROVE",
        "REJECT"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                "Decision must be APPROVE or REJECT"
            )
        )

    conn = get_db()

    try:

        proposal = conn.execute("""
            SELECT
                pr.*,
                r.project_id,
                r.hours,
                r.budget AS request_budget,
                r.duration,
                r.risk AS request_risk,
                p.owner AS project_owner
            FROM proposals pr
            JOIN requests r
                ON pr.request_id = r.id
            JOIN projects p
                ON r.project_id = p.id
            WHERE pr.id=?
        """, (
            proposal_id,
        )).fetchone()

        if not proposal:

            raise HTTPException(
                status_code=404,
                detail="Proposal not found"
            )

        # Only project owner can decide.
        if (
            request.owner
            != proposal["project_owner"]
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "Only the project owner can "
                    "approve or reject this proposal"
                )
            )

        # Prevent duplicate decision.
        if proposal["status"] in [
            "APPROVED",
            "REJECTED"
        ]:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Proposal has already been "
                    f"{proposal['status'].lower()}"
                )
            )

        # ====================================================
        # REJECTION
        # ====================================================

        if decision == "REJECT":

            conn.execute("""
                INSERT INTO approvals
                (
                    proposal_id,
                    owner,
                    decision,
                    reason,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                proposal_id,
                request.owner,
                "REJECT",
                request.reason,
                datetime.now().isoformat()
            ))

            conn.execute("""
                UPDATE proposals
                SET status='REJECTED'
                WHERE id=?
            """, (
                proposal_id,
            ))

            conn.commit()

            return {
                "message": (
                    "Proposal rejected and "
                    "no allocation was created"
                ),
                "proposal_id": proposal_id,
                "decision": "REJECT",
                "allocation_created": False,
                "allocation_hours": 0
            }

        # ====================================================
        # APPROVAL RE-CHECK
        # ====================================================

        person = conn.execute("""
            SELECT *
            FROM people
            WHERE id=?
        """, (
            proposal["person_id"],
        )).fetchone()

        if not person:

            raise HTTPException(
                status_code=404,
                detail="Person no longer exists"
            )

        allocated = conn.execute("""
            SELECT COALESCE(SUM(hours), 0) AS total
            FROM allocations
            WHERE person_id=?
        """, (
            proposal["person_id"],
        )).fetchone()["total"]

        current_available = max(
            0,
            person["capacity"] - allocated
        )

        requested_hours = proposal["hours"]

        if current_available < requested_hours:

            raise HTTPException(
                status_code=409,
                detail=(
                    f"Approval blocked: only "
                    f"{current_available}h is currently "
                    f"available but {requested_hours}h "
                    f"is required"
                )
            )

        # ====================================================
        # RECORD APPROVAL
        # ====================================================

        conn.execute("""
            INSERT INTO approvals
            (
                proposal_id,
                owner,
                decision,
                reason,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            proposal_id,
            request.owner,
            "APPROVE",
            request.reason,
            datetime.now().isoformat()
        ))

        # ====================================================
        # CREATE / UPDATE ALLOCATION
        # ====================================================

        existing_allocation = conn.execute("""
            SELECT id, hours
            FROM allocations
            WHERE person_id=?
            AND project_id=?
            LIMIT 1
        """, (
            proposal["person_id"],
            proposal["project_id"]
        )).fetchone()

        if existing_allocation:

            new_hours = (
                existing_allocation["hours"]
                +
                requested_hours
            )

            conn.execute("""
                UPDATE allocations
                SET hours=?
                WHERE id=?
            """, (
                new_hours,
                existing_allocation["id"]
            ))

            allocation_id = (
                existing_allocation["id"]
            )

        else:

            cursor = conn.execute("""
                INSERT INTO allocations
                (
                    person_id,
                    project_id,
                    hours
                )
                VALUES (?, ?, ?)
            """, (
                proposal["person_id"],
                proposal["project_id"],
                requested_hours
            ))

            allocation_id = (
                cursor.lastrowid
            )

        # ====================================================
        # MARK APPROVED
        # ====================================================

        conn.execute("""
            UPDATE proposals
            SET status='APPROVED'
            WHERE id=?
        """, (
            proposal_id,
        ))

        conn.commit()

        return {
            "message": (
                "Proposal approved and "
                "allocation created"
            ),
            "proposal_id": proposal_id,
            "decision": "APPROVE",
            "allocation_created": True,
            "allocation_id": allocation_id,
            "allocation_hours": requested_hours
        }

    except HTTPException:

        conn.rollback()

        raise

    except Exception as error:

        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Approval workflow failed: "
                f"{str(error)}"
            )
        )

    finally:

        conn.close()


# ============================================================
# ALLOCATIONS
# ============================================================

@app.get("/allocations")
def all_allocations():

    conn = get_db()

    allocations = conn.execute("""
        SELECT
            a.id,
            a.person_id,
            p.name AS person_name,
            p.role,
            p.grade,
            p.capacity,
            a.project_id,
            pr.name AS project_name,
            pr.owner AS project_owner,
            a.hours
        FROM allocations a
        JOIN people p
            ON a.person_id = p.id
        JOIN projects pr
            ON a.project_id = pr.id
        ORDER BY a.id DESC
    """).fetchall()

    conn.close()

    return [
        dict(allocation)
        for allocation in allocations
    ]


# ============================================================
# PERSON AVAILABILITY
# ============================================================

@app.get("/people/{person_id}/availability")
def person_availability(
    person_id: str
):

    conn = get_db()

    person = conn.execute("""
        SELECT *
        FROM people
        WHERE id=?
    """, (
        person_id,
    )).fetchone()

    conn.close()

    if not person:

        raise HTTPException(
            status_code=404,
            detail="Person not found"
        )

    available = calculate_availability(
        person_id
    )

    return {

        "person_id": person_id,

        "name": person["name"],

        "capacity": person["capacity"],

        "available_hours": available,

        "allocated_hours": (
            person["capacity"]
            -
            available
        )
    }


# ============================================================
# REALLOCATION
# ============================================================

class ReallocationRequest(BaseModel):

    person_id: str

    from_project_id: str

    to_project_id: str

    hours: int

    reason: str = ""


class ReallocationDecision(BaseModel):

    owner: str

    decision: str

    reason: str = ""


# ============================================================
# CREATE REALLOCATION REQUEST
# ============================================================

@app.post("/reallocations")
def create_reallocation(
    request: ReallocationRequest
):

    if request.hours <= 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "Reallocation hours must be "
                "greater than zero"
            )
        )

    if (
        request.from_project_id
        ==
        request.to_project_id
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Source and destination projects "
                "must be different"
            )
        )

    conn = get_db()

    try:

        # ====================================================
        # PERSON
        # ====================================================

        person = conn.execute("""
            SELECT *
            FROM people
            WHERE id=?
        """, (
            request.person_id,
        )).fetchone()

        if not person:

            raise HTTPException(
                status_code=404,
                detail="Person not found"
            )

        # ====================================================
        # SOURCE PROJECT
        # ====================================================

        source_project = conn.execute("""
            SELECT *
            FROM projects
            WHERE id=?
        """, (
            request.from_project_id,
        )).fetchone()

        if not source_project:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Releasing project not found"
                )
            )

        # ====================================================
        # TARGET PROJECT
        # ====================================================

        target_project = conn.execute("""
            SELECT *
            FROM projects
            WHERE id=?
        """, (
            request.to_project_id,
        )).fetchone()

        if not target_project:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Receiving project not found"
                )
            )

        # ====================================================
        # SOURCE ALLOCATION
        # ====================================================

        source_allocation = conn.execute("""
            SELECT id, hours
            FROM allocations
            WHERE person_id=?
            AND project_id=?
            LIMIT 1
        """, (
            request.person_id,
            request.from_project_id
        )).fetchone()

        if not source_allocation:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Person is not allocated to "
                    "the releasing project"
                )
            )

        if (
            source_allocation["hours"]
            <
            request.hours
        ):

            raise HTTPException(
                status_code=409,
                detail=(
                    f"Only "
                    f"{source_allocation['hours']}h "
                    "can be released from this project"
                )
            )

        # ====================================================
        # CREATE PENDING REALLOCATION
        # ====================================================

        cursor = conn.execute("""
            INSERT INTO reallocation_requests
            (
                person_id,
                from_project_id,
                to_project_id,
                hours,
                reason,
                releasing_owner,
                receiving_owner,
                releasing_decision,
                receiving_decision,
                status,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?,
                'PENDING',
                'PENDING',
                'PENDING',
                ?
            )
        """, (
            request.person_id,
            request.from_project_id,
            request.to_project_id,
            request.hours,
            request.reason,
            source_project["owner"],
            target_project["owner"],
            datetime.now().isoformat()
        ))

        reallocation_id = cursor.lastrowid

        conn.commit()

        return {

            "message": (
                "Reallocation request created"
            ),

            "reallocation_id":
                reallocation_id,

            "person_id":
                request.person_id,

            "person_name":
                person["name"],

            "from_project":
                source_project["name"],

            "to_project":
                target_project["name"],

            "hours":
                request.hours,

            "releasing_owner":
                source_project["owner"],

            "receiving_owner":
                target_project["owner"],

            "status":
                "PENDING"
        }

    except HTTPException:

        conn.rollback()

        raise

    except Exception as error:

        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not create reallocation: "
                f"{str(error)}"
            )
        )

    finally:

        conn.close()


# ============================================================
# VIEW REALLOCATIONS
# ============================================================

@app.get("/reallocations")
def get_reallocations():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            rr.id AS reallocation_id,

            rr.person_id,

            p.name AS person_name,

            rr.from_project_id,

            fp.name AS from_project,

            rr.releasing_owner,

            rr.to_project_id,

            tp.name AS to_project,

            rr.receiving_owner,

            rr.hours,

            rr.reason,

            rr.releasing_decision,

            rr.receiving_decision,

            rr.status,

            rr.created_at

        FROM reallocation_requests rr

        JOIN people p
            ON rr.person_id = p.id

        JOIN projects fp
            ON rr.from_project_id = fp.id

        JOIN projects tp
            ON rr.to_project_id = tp.id

        ORDER BY rr.id DESC
    """).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# REALLOCATION OWNER DECISION
# ============================================================

@app.post(
    "/reallocations/{reallocation_id}/decision"
)
def decide_reallocation(
    reallocation_id: int,
    decision: ReallocationDecision
):

    choice = (
        decision.decision
        .upper()
        .strip()
    )

    if choice not in [
        "APPROVE",
        "REJECT"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                "Decision must be APPROVE or REJECT"
            )
        )

    conn = get_db()

    try:

        # ====================================================
        # GET REALLOCATION
        # ====================================================

        item = conn.execute("""
            SELECT *
            FROM reallocation_requests
            WHERE id=?
        """, (
            reallocation_id,
        )).fetchone()

        if not item:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Reallocation request not found"
                )
            )

        # ====================================================
        # DETERMINE OWNER
        # ====================================================

        if (
            decision.owner
            ==
            item["releasing_owner"]
        ):

            owner_type = "RELEASING"

        elif (
            decision.owner
            ==
            item["receiving_owner"]
        ):

            owner_type = "RECEIVING"

        else:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Only the releasing project owner "
                    "or receiving project owner can decide"
                )
            )

        # ====================================================
        # PREVENT DUPLICATE DECISION
        # ====================================================

        current_decision = (

            item["releasing_decision"]

            if owner_type == "RELEASING"

            else item["receiving_decision"]
        )

        if current_decision != "PENDING":

            raise HTTPException(
                status_code=400,
                detail=(
                    f"{owner_type.title()} owner has "
                    "already made a decision"
                )
            )

        # ====================================================
        # RECORD DECISION
        # ====================================================

        if owner_type == "RELEASING":

            conn.execute("""
                UPDATE reallocation_requests
                SET releasing_decision=?
                WHERE id=?
            """, (
                choice,
                reallocation_id
            ))

        else:

            conn.execute("""
                UPDATE reallocation_requests
                SET receiving_decision=?
                WHERE id=?
            """, (
                choice,
                reallocation_id
            ))

        # ====================================================
        # IF EITHER OWNER REJECTS
        # ====================================================

        if choice == "REJECT":

            conn.execute("""
                UPDATE reallocation_requests
                SET status='REJECTED'
                WHERE id=?
            """, (
                reallocation_id,
            ))

            conn.commit()

            return {

                "message": (
                    f"{owner_type.title()} owner "
                    "rejected the reallocation"
                ),

                "reallocation_id":
                    reallocation_id,

                "decision":
                    "REJECT",

                "status":
                    "REJECTED",

                "allocation_changed":
                    False
            }

        # ====================================================
        # GET UPDATED RECORD
        # ====================================================

        updated = conn.execute("""
            SELECT *
            FROM reallocation_requests
            WHERE id=?
        """, (
            reallocation_id,
        )).fetchone()

        # ====================================================
        # BOTH OWNERS APPROVED
        # ====================================================

        if (
            updated["releasing_decision"]
            == "APPROVE"

            and

            updated["receiving_decision"]
            == "APPROVE"
        ):

            # ------------------------------------------------
            # RE-CHECK SOURCE ALLOCATION
            # ------------------------------------------------

            source = conn.execute("""
                SELECT id, hours
                FROM allocations
                WHERE person_id=?
                AND project_id=?
                LIMIT 1
            """, (
                updated["person_id"],
                updated["from_project_id"]
            )).fetchone()

            if not source:

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Source allocation no longer exists"
                    )
                )

            if (
                source["hours"]
                <
                updated["hours"]
            ):

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Source project no longer has "
                        "enough hours available"
                    )
                )

            # ------------------------------------------------
            # REMOVE HOURS FROM SOURCE
            # ------------------------------------------------

            remaining_hours = (
                source["hours"]
                -
                updated["hours"]
            )

            if remaining_hours == 0:

                conn.execute("""
                    DELETE FROM allocations
                    WHERE id=?
                """, (
                    source["id"],
                ))

            else:

                conn.execute("""
                    UPDATE allocations
                    SET hours=?
                    WHERE id=?
                """, (
                    remaining_hours,
                    source["id"]
                ))

            # ------------------------------------------------
            # ADD HOURS TO TARGET
            # ------------------------------------------------

            destination = conn.execute("""
                SELECT id, hours
                FROM allocations
                WHERE person_id=?
                AND project_id=?
                LIMIT 1
            """, (
                updated["person_id"],
                updated["to_project_id"]
            )).fetchone()

            if destination:

                conn.execute("""
                    UPDATE allocations
                    SET hours=hours + ?
                    WHERE id=?
                """, (
                    updated["hours"],
                    destination["id"]
                ))

            else:

                conn.execute("""
                    INSERT INTO allocations
                    (
                        person_id,
                        project_id,
                        hours
                    )
                    VALUES (?, ?, ?)
                """, (
                    updated["person_id"],
                    updated["to_project_id"],
                    updated["hours"]
                ))

            # ------------------------------------------------
            # FINAL STATUS
            # ------------------------------------------------

            conn.execute("""
                UPDATE reallocation_requests
                SET status='APPROVED'
                WHERE id=?
            """, (
                reallocation_id,
            ))

            conn.commit()

            return {

                "message": (
                    "Both owners approved. "
                    "Reallocation completed."
                ),

                "reallocation_id":
                    reallocation_id,

                "decision":
                    "APPROVE",

                "status":
                    "APPROVED",

                "allocation_changed":
                    True,

                "hours_moved":
                    updated["hours"]
            }

        # ====================================================
        # ONE OWNER APPROVED
        # ====================================================

        conn.execute("""
            UPDATE reallocation_requests
            SET status='WAITING_FOR_OTHER_OWNER'
            WHERE id=?
        """, (
            reallocation_id,
        ))

        conn.commit()

        return {

            "message": (
                f"{owner_type.title()} owner approved. "
                "Waiting for the other project owner."
            ),

            "reallocation_id":
                reallocation_id,

            "decision":
                "APPROVE",

            "status":
                "WAITING_FOR_OTHER_OWNER",

            "allocation_changed":
                False
        }

    except HTTPException:

        conn.rollback()

        raise

    except Exception as error:

        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Reallocation workflow failed: "
                f"{str(error)}"
            )
        )

    finally:

        conn.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )