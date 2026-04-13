# EMAIL DELIVERY SKILL (LEARNED)

## FAILURES ENCOUNTERED & FIXES

### FAILURE 1: Tab Navigation
**What failed:** Tab through form fields to reach send button
**Why:** Tabs don't land on Gmail send button
**Fix:** Never use Tab - use click at known position or keyboard shortcut

### FAILURE 2: Coordinate Guessing  
**What failed:** Clicked at {100, 600}, {80, 580}, etc - random positions
**Why:** Screen/window sizes vary, position was always wrong
**Fix:** Get actual window bounds, calculate relative position, or ask user

### FAILURE 3: Output Before Verification
**What failed:** Reported "sent" without verifying
**Why:** No checkpoint after action
**Fix:** MUST verify in Sent folder before reporting success

### FAILURE 4: Multiple Tabs
**What failed:** Opened multiple tabs, lost track, clicks went to wrong place
**Why:** No single-step execution
**Fix:** One compose, send, verify - THEN next

### FAILURE 5: JS Disabled
**What failed:** Chrome JavaScript blocked for verification
**Why:** Security setting not enabled
**Fix:** Accept that programmatic verification may fail, plan for manual check

### FAILURE 6: Silent Failures
**What failed:** AppleScript returned code 0 but send didn't happen
**Why:** Permission blocked but no error shown
**Fix:** Verify via Sent folder regardless of return code

---

## COMPLETE EXECUTION PROTOCOL

```
STEP 1: PRE-FLIGHT
- Check if Chrome is running
- Ask user to enable JS if needed (optional)

STEP 2: OPEN COMPOSE
- Open ONE compose with recipient, subject, body in URL
- Wait 3 seconds for load

STEP 3: USER-clicks-SEND (REQUIRED)
- Since automation fails, ASK user to click send
- This is the only reliable method

STEP 4: WAIT
- Wait 5 seconds for user action

STEP 5: VERIFY
- Open Sent folder
- Check if email is there (if JS enabled)
- If JS disabled: ask user to verify manually

STEP 6: CONFIRM
- Only report success after verification
- If not verified: report failure honestly

STEP 7: LOG
- Log to operation_log.py: recipient, result, verification status
```

---

## KEY LEARNINGS

1. **Never assume automation works** - verify everything
2. **Single-step execution** - one action, verify, next
3. **User-click is reliable** - accept this limitation
4. **Verification mandatory** - no exceptions
5. **Log everything** - learn from failures

---

## SKILL: send_email(recipient, subject, body)

```python
def send_email(recipient, subject, body):
    # 1. Open compose
    open_compose(recipient, subject, body)
    wait(3)
    
    # 2. Ask user to click send
    print(f"Please click SEND for {recipient}")
    wait_for_confirmation()
    
    # 3. Verify
    if verify_in_sent(recipient):
        log_success(recipient)
        return "SENT"
    else:
        log_failure(recipient)
        return "FAILED"
```

---

**This skill now contains the fixes from all failures.**