"""
Xzenia Live Pipeline Demo
Run this in a terminal window while OBS/ffmpeg records.
This will display the live pipeline execution for the screen recording.
"""

import sys
import time
sys.path.insert(0, 'projects/xzenia/cognitive')

import psycopg2
from sovereign_handlers import HandlerRegistry, PRETTY_BUSY_CLEANING

def run_demo():
    print("=" * 70)
    print("XZENIA COGNITIVE ARCHITECTURE - LIVE DEMO")
    print("=" * 70)
    print()
    
    # Connect to database
    conn = psycopg2.connect(dbname="nexus", host="localhost")
    cur = conn.cursor()
    
    # Show current state
    print("[1] FETCHING DEMAND REQUESTS")
    cur.execute("SELECT id, title, location, budget, status FROM demand_requests WHERE category = 'cleaning' ORDER BY created_at DESC LIMIT 5")
    rows = cur.fetchall()
    for r in rows:
        print(f"  {r[4]:10} | ${r[3]:>7.0f} | {r[2]:15} | {r[1][:30]}")
    
    print()
    print("[2] FETCHING FULFILLMENT EXECUTIONS")
    cur.execute("SELECT id, demand_id, route, price_estimate, status FROM fulfillment_executions ORDER BY created_at DESC LIMIT 5")
    execs = cur.fetchall()
    total_revenue = 0
    for e in execs:
        print(f"  {e[4]:12} | ${e[3]:>7.0f} | {e[2]:12} | {e[0][:8]}...")
        if e[4] == 'COMPLETED':
            total_revenue += e[3]
    print(f"\n  TOTAL REVENUE CAPTURED: ${total_revenue:,.0f}")
    
    print()
    print("[3] PROCESSING NEW DEMAND")
    # Get an unmatched demand
    cur.execute("SELECT id, title, location, budget FROM demand_requests WHERE status = 'routed' AND category = 'cleaning' LIMIT 1")
    demand = cur.fetchone()
    if demand:
        print(f"  Dispatching: {demand[1]} in {demand[2]} for ${demand[3]}")
        cur.execute("UPDATE demand_requests SET status = 'dispatched' WHERE id = %s", (demand[0],))
        conn.commit()
        print(f"  ✓ Status updated to DISPATCHED")
    
    print()
    print("[4] LEAD ENGINE STATUS")
    cur.execute("SELECT pipeline_stage, COUNT(*), SUM(estimated_value) FROM prospects GROUP BY pipeline_stage")
    for stage in cur.fetchall():
        print(f"  {stage[0]:15} | {stage[1]:3} leads | ${stage[2]:,.0f} pipeline")
    
    print()
    print("[5] BILLING RECOVERY STATUS")
    cur.execute("SELECT status, COUNT(*), SUM(amount) FROM billing_events GROUP BY status")
    for bill in cur.fetchall():
        print(f"  {bill[0]:15} | {bill[1]:3} events | ${bill[2]:,.0f}")
    
    print()
    print("[6] CAUSAL OBSERVATIONS")
    cur.execute("SELECT COUNT(*) FROM causal_observations")
    obs_count = cur.fetchone()[0]
    print(f"  Total observations: {obs_count}/50 (learning in progress)")
    
    cur.close()
    conn.close()
    
    print()
    print("=" * 70)
    print("DEMO COMPLETE - System running on 2019 MacBook Air")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
