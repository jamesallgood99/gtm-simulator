# PRD: Keelstone Safety Platform, v1.0 launch

*Sample document. Keelstone is a fictional product created to demonstrate the Synthetic Market Simulator.*

**Owner:** Product · **Status:** Approved for Q2 launch · **Last updated:** March 2026

## Problem

Employers in high-injury industries find out about unsafe work after someone is hurt. Safety
managers cover more sites than they can walk, claims data arrives months late, and the experience
mod that sets the workers' comp premium looks back three years. Brokers go into renewal with loss
runs and little else.

## Goals

1. Reduce recordable injuries and claim frequency at customer sites within the first year.
2. Give safety teams coverage across every site and shift without adding headcount.
3. Give the CFO and broker a credible, data-backed risk story at renewal.
4. Ship without new hardware and without making workers feel watched.

## Users

| User | What they need from v1 |
|---|---|
| Safety manager | See hazards and unsafe movements across sites, coach crews, close OSHA paperwork faster |
| Frontline worker | A safer job, without being disciplined by a camera |
| IT manager | Clear data handling, no new hardware, low support load |
| CFO | Total cost of risk in one place and a defensible ROI |
| Insurance broker | Better data to bring to carriers at renewal |

## Features in scope for v1.0

### F1. Hazard detection on existing cameras
Computer vision runs on the customer's existing IP cameras and flags unsafe lifts, slips and trips,
missing PPE, and forklift/pedestrian near-misses. Alerts go to the safety team, not to supervisors
by default. Setup: connect cameras through an on-site gateway (about one day per site).

### F2. Crew coaching feed
Short weekly coaching clips built from flagged events, with every face and name blurred by default.
Crew leads play them in toolbox talks. Workers can view on a shared tablet or their phone.

### F3. Broker risk report
A renewal-ready report that shows hazard trends, corrective actions and leading indicators by site.
The employer controls sharing. Brokers get their own view across all of their Keelstone clients.

### F4. Total cost of risk dashboard
Combines premium, claims, reserves, lost workdays and Keelstone leading indicators into one view,
with an ROI tracker that compares the current period against the customer's own baseline.

### F5. OSHA recordkeeping automation
Drafts OSHA 300, 300A and 301 entries from incident reports and keeps an audit trail for
inspections.

### F6. Privacy and data controls
Face and body blurring at the edge, configurable retention (default 30 days for video), SSO,
role-based access, and a worker-facing privacy notice. Video used for coaching only, never for
discipline, unless a customer explicitly changes the policy.

### F7. Anonymous near-miss reporting
Workers report a near-miss or hazard from their phone in under 30 seconds, anonymously if they
choose. Reports go to the safety team and feed the coaching feed.

### F8. Claims and HRIS integrations
Connectors for the major payroll/HRIS systems and carrier claims feeds, so headcount, hours and
claims flow in without manual exports. Requires IT to approve API access.

## Out of scope for v1.0

Wearables, carrier-side pricing integrations, and automated premium negotiation.

## Success metrics

- 25% reduction in claim frequency at 12 months (pilot customers)
- 80% of sites with at least one coaching session per week at 90 days
- Broker report shared at 60% of customer renewals

## Risks

- Workers and unions may read cameras as surveillance.
- IT security reviews may slow deployment at larger customers.
- Premium impact lags behind claim reduction by one to three years.
