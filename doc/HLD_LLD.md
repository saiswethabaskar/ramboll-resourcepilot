# HLD & LLD

## 1. High-Level Design

```text
                    +----------------------+
                    |   Project Owner      |
                    +----------+-----------+
                               |
                               v
+-------------+       +---------------------+
| Resourcing  | ----> | FastAPI Application |
| Request     |       +----------+----------+
+-------------+                  |
                                 v
                    +---------------------+
                    | Recommendation      |
                    | Engine               |
                    +----------+----------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
        Availability        Cost          Delivery Risk
              |                |                |
              +----------------+----------------+
                               |
                               v
                    +---------------------+
                    | Ranked Proposals    |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    | Owner Approval Gate |
                    +----------+----------+
                               |
                    +----------+----------+
                    |                     |
                    v                     v
                Approved              Rejected
                    |
                    v
              Allocation /
              Reallocation
              2. Main Components
API Layer

FastAPI exposes REST endpoints for requests, proposals, approvals, allocations and reallocations.

Recommendation Engine

Evaluates candidates based on skills, availability, cost, delivery risk and split feasibility.

Database Layer

SQLite stores employees, projects, allocations, requests, proposals and approval records.

Approval Layer

Ensures that recommendations are only applied after the required owner approval.

Frontend

A lightweight HTML/CSS/JavaScript dashboard consumes the REST API.

3. Database Schema
People
id
name
grade
location
skills
hourly_rate
Projects
id
name
owner
work_type
risk_level
budget
Allocations
id
person_id
project_id
hours
Requests
id
project_id
required_skills
required_hours
budget
work_type
risk_level
Proposals
id
request_id
person_id
score
health
reasoning
status
Approvals
id
proposal_id
owner
decision
reason
Reallocation Requests
id
person_id
from_project_id
to_project_id
hours
reason
status
Reallocation Decisions
id
reallocation_id
owner
decision
reason
4. API Design
Generate proposals

POST /requests/{request_id}/proposals

Generates candidate proposals for an open request.

Decide proposal

POST /proposals/{proposal_id}/decision

Requires project owner approval.

Create reallocation

POST /reallocations

Creates a reallocation proposal.

Decide reallocation

POST /reallocations/{reallocation_id}/decision

Requires both releasing and receiving project owner approval.

5. Approval Logic
Proposal
   |
   v
Owner Decision
   |
   +---- REJECT --> No allocation
   |
   +---- APPROVE --> Allocation created/updated

For reallocation:

Reallocation
     |
     v
Releasing Owner
     |
     v
Receiving Owner
     |
     +---- Either Reject --> No change
     |
     +---- Both Approve --> Apply reallocation
6. Design Principles
Explainability over opaque recommendations
Human approval before action
Actual availability rather than nominal availability
Cost and delivery risk considered together
Support partial allocation
Explicit audit trail
Recommendation-only AI behaviour