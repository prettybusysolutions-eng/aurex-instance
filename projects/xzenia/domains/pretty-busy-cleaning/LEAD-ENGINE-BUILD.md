# Lead Engine Build

## Purpose
Dominate the first real economic loop:
**lead arrives -> classify -> respond -> follow up -> book or close out**

## Components to build next
1. `lead-queue.json`
2. `lead-memory.json`
3. `lead_classifier.py`
4. `followup_scheduler.py`
5. `pipeline_summary.py`
6. LaunchAgent for recurring lead follow-up check

## Required inputs
- incoming contact/message surface
- lead source if known
- service interest
- location
- timing urgency
- quote readiness

## Output states
- new
- qualified
- waiting_on_info
- quoted
- followup_due
- booked
- lost

## First practical rule
No lead should sit without a known state.

## Mutation target later
Once the Lead Engine is live, route performance data into CSMR for conversion optimization.
