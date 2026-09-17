# Ramboll ResourcePilot

## Intelligent Resourcing & Allocation Suggestion Platform

A Python-based prototype for intelligent resource recommendation, availability analysis, cost-risk evaluation, and approval-controlled allocation/reallocation.

## Tech Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy
- HTML / CSS / JavaScript

## Why This Approach

FastAPI was selected because it provides a lightweight API framework with automatic Swagger documentation and is suitable for rapidly building a working prototype.

SQLite was selected because this is a representative pilot prototype and does not require a production database.

The recommendation engine uses transparent rule-based scoring rather than trained ML because historical labelled staffing decisions are not available in the prototype dataset.

## Core Features

### 1. Explainable Resource Recommendation

Candidates are evaluated using:

- Skill match
- Actual availability
- Delivery risk
- Budget fit
- Split feasibility

Each recommendation provides reasoning and identifies potential concerns.

### 2. Availability & Workable Split

The system calculates current allocation and remaining availability.

Partial availability is supported.

The system also considers whether splitting a resource could introduce fragmentation or delivery risk.

### 3. Cost vs Delivery Risk

Candidate recommendations consider both affordability and delivery safety.

The system highlights situations where a cheaper resource may introduce additional delivery risk and where a highly qualified resource may increase cost.

### 4. Owner Approval Gate

Recommendations do not automatically become allocations.

A project owner must explicitly approve or reject a proposal.

Rejected proposals do not create allocations.

### 5. Reallocation

Resources can be proposed for movement between projects.

A reallocation requires approval from:

- Releasing project owner
- Receiving project owner

Allocation changes occur only after both approvals.

## Recommendation Flow

Request
→ Candidate Evaluation
→ Availability Check
→ Split Assessment
→ Cost Evaluation
→ Delivery Risk Evaluation
→ Explainable Proposal
→ Owner Decision
→ Approved Allocation / Reallocation

## Prototype Scoring

The prototype uses the following configurable weights:

- Skill Match: 30%
- Availability: 25%
- Delivery Risk: 20%
- Budget: 15%
- Split Feasibility: 10%

These are prototype assumptions and are not intended to represent an official Ramboll scoring formula.

## Approval Principle

The system is recommendation-only.

Human project owners remain responsible for the final decision.

No allocation or reallocation is applied without the required approval.

## Data

The prototype uses representative synthetic data covering:

- Employees
- Skills
- Grades
- Locations
- Cost rates
- Projects
- Existing allocations
- Open resourcing requests
- Proposals
- Approval decisions

The dataset intentionally includes scenarios such as partial availability, strong skill matches, cost-risk trade-offs, split allocations and incomplete information.

## API

Main endpoints include:

- `GET /people`
- `GET /projects`
- `GET /requests`
- `GET /dashboard`
- `POST /requests/{request_id}/proposals`
- `GET /proposals`
- `POST /proposals/{proposal_id}/decision`
- `GET /allocations`
- `GET /people/{person_id}/availability`
- `POST /reallocations`
- `GET /reallocations`
- `POST /reallocations/{reallocation_id}/decision`

Swagger documentation is available at:

`/docs`

## How to Run

```bash
python -m pip install fastapi uvicorn sqlalchemy
python -m uvicorn main:app --reload
