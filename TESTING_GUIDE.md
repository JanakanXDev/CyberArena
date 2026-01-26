    # CyberArena Testing Guide

## Quick Start Testing

### 1. **Guided Simulation Mode** (Start Here)

**What to Test:**
- Continuous simulation with hidden phases
- Hypothesis formation and validation
- Actions that appear successful but fail later
- Delayed consequences

**Steps:**
1. Select "Guided Simulation" mode
2. Choose "Operation: Broken Trust" scenario
3. Start the simulation

**Expected Behavior:**
- ✅ You should see initial system logs in the System View
- ✅ You should see hypotheses to test (e.g., "Input flows directly into database queries")
- ✅ At least one action should be available immediately: "Probe input validation boundaries"
- ✅ Other actions should be locked until you validate a hypothesis

**Test Flow:**
1. **Form a Hypothesis**: Click on a hypothesis (e.g., "Boolean conditions can be manipulated")
   - If correct: Action unlocks
   - If incorrect: Risk increases, action stays locked
   
2. **Execute an Action**: Click "Probe input validation boundaries"
   - Should see logs appear in System View
   - Detection level should increase slightly
   - Turn count should increment

3. **Test Delayed Consequences**: 
   - After 2-3 turns, you should see a delayed consequence log
   - Previous actions may show unexpected results

4. **Test Contradictions**:
   - If you test the wrong hypothesis ("Errors reveal system structure"), it should fail
   - System should show a contradiction message

---

### 2. **Attacker Campaign Mode**

**What to Test:**
- User plays as attacker
- AI defender actively responds
- Stealth and evasion mechanics

**Steps:**
1. Select "Attacker Campaign" mode
2. Choose any scenario
3. Start simulation

**Expected Behavior:**
- ✅ AI defender should be active
- ✅ Actions focused on attacking (probe, escalate, pivot, persist)
- ✅ AI should react to your actions (enable logging, block IPs, patch vulnerabilities)

**Test Flow:**
1. **Stealthy Probing**: Click "Probe system boundaries stealthily"
   - Detection should increase slowly
   - AI should start monitoring after a few actions

2. **Watch AI Response**:
   - After several actions, check System View for AI activity
   - Should see logs like "Monitoring active on web_server"
   - AI aggressiveness should increase

3. **Test Escalation**: Try "Attempt privilege escalation"
   - Risk and detection should spike
   - AI should respond more aggressively

---

### 3. **Defender Campaign Mode**

**What to Test:**
- User plays as defender
- AI attacker probes and escalates
- Detection and incident response

**Steps:**
1. Select "Defender Campaign" mode
2. Choose any scenario
3. Start simulation

**Expected Behavior:**
- ✅ Initial risk should be higher (attacks already in progress)
- ✅ Actions focused on defense (monitor, isolate, restrict, patch)
- ✅ AI attacker should continue attacking

**Test Flow:**
1. **Enable Monitoring**: Click "Monitor system for anomalies"
   - Detection level should increase
   - Should see monitoring logs

2. **Isolate Components**: Click "Isolate potentially compromised component"
   - Risk should decrease
   - Integrity should increase

3. **Watch AI Attacker**:
   - AI should continue probing
   - Should see attack logs in System View
   - Risk may continue to increase if not properly defended

---

### 4. **Playground Mode**

**What to Test:**
- No fixed objectives
- Full freedom to experiment
- Optional AI opponent
- Can break the system

**Steps:**
1. Select "Playground Mode"
2. Choose any scenario
3. Start simulation

**Expected Behavior:**
- ✅ Multiple actions available immediately
- ✅ No forced phase progression
- ✅ Can execute destructive actions

**Test Flow:**
1. **Try Different Strategies**:
   - Probe flows
   - Alter boundaries
   - Escalate context
   - Isolate components

2. **Test System Destruction**: Click "Test system destruction"
   - Integrity should drop significantly
   - System should still be recoverable
   - No "game over" screen

3. **Experiment Freely**:
   - Try any combination of actions
   - See how they interact
   - Learn from consequences

---

## Core Features Testing

### **Hypothesis System**

**Test:**
1. Form a hypothesis
2. Validate it (correct or incorrect)
3. Check if actions unlock based on validation

**Expected:**
- ✅ Correct hypothesis → Actions unlock
- ✅ Incorrect hypothesis → Risk increases, actions stay locked
- ✅ Hypotheses show as "Validated" or "Invalidated" after testing

---

### **Delayed Consequences**

**Test:**
1. Execute an action (e.g., "Probe input validation boundaries")
2. Wait 2-3 turns
3. Check Event Log for delayed consequences

**Expected:**
- ✅ Should see log: "Delayed consequence: Previous probe triggered logging"
- ✅ Detection should increase later, not immediately
- ✅ Actions that appeared successful may show failures later

---

### **Contradiction Engine**

**Test:**
1. Form an incorrect hypothesis (e.g., "Errors reveal system structure")
2. Validate it
3. System should contradict your assumption

**Expected:**
- ✅ Should see contradiction message in Event Log
- ✅ Should appear in State Panel under "Contradictions"
- ✅ Previous successful actions may be marked as failed

---

### **Mentor AI**

**Test:**
1. Click "Mentor" button in header to enable
2. Execute some actions
3. Check for mentor guidance

**Expected:**
- ✅ Mentor should only ask questions, never give answers
- ✅ Should highlight anomalies and inconsistencies
- ✅ Should suggest concepts to study (not solutions)

---

### **AI Opponent**

**Test (Attacker Campaign):**
1. Execute several probing actions
2. Watch System View for AI defender activity

**Expected:**
- ✅ AI should enable logging after detection threshold
- ✅ AI should block suspicious activity
- ✅ AI should deploy patches or honeypots
- ✅ AI aggressiveness should increase

**Test (Defender Campaign):**
1. Start simulation
2. Watch for AI attacker activity

**Expected:**
- ✅ AI should probe vulnerabilities
- ✅ AI should escalate privileges
- ✅ AI should adapt to your defenses
- ✅ Risk should increase if not properly defended

---

## UI Testing

### **Four-Zone Layout**

**System View (Top Left):**
- ✅ Should show system components
- ✅ Should show vulnerability status
- ✅ Should show system logs (partial, noisy signals)

**Action Panel (Top Right):**
- ✅ Should show available actions
- ✅ Should show hypotheses to test
- ✅ Locked actions should be clearly marked

**State Panel (Bottom Left):**
- ✅ Should show Risk Score (0-100)
- ✅ Should show Detection Level (0-100)
- ✅ Should show System Integrity (0-100)
- ✅ Should show AI Aggressiveness (if active)
- ✅ Should show user assumptions
- ✅ Should show contradictions

**Event Log (Bottom Right):**
- ✅ Should show action history
- ✅ Should show cause-effect traces
- ✅ Should show delayed consequences
- ✅ Should show contradictions

---

## What to Verify

### ✅ **Success Criteria:**

1. **No Phase Buttons**: Phases should never be visible to user
2. **No Completion Screens**: Simulation should feel continuous
3. **Hidden Outcomes**: Consequences should be revealed after actions, not before
4. **Meaningful Failures**: At least one action should appear successful but fail later
5. **AI Adaptation**: AI should change behavior based on your actions
6. **Strategy Matters**: Fast clicking should fail, careful thinking should succeed
7. **Hypothesis-Based**: Actions should be phrased as intent, not exploit names
8. **Delayed Effects**: Some consequences should trigger later
9. **Contradictions**: System should break wrong assumptions
10. **Mentor Guidance**: Mentor should only ask questions, never give answers

---

## Common Issues to Check

### **If Actions Don't Work:**
- Check browser console for errors
- Check backend terminal for errors
- Verify backend is running on port 5000
- Check Network tab for failed API calls

### **If No Actions Appear:**
- Check if hypotheses need to be validated first
- Look at debug indicator in Action Panel
- Check console logs for action count

### **If AI Doesn't Respond:**
- Wait a few turns (AI may take time to react)
- Check System View for AI activity logs
- Verify AI opponent is initialized for the mode

### **If State Doesn't Update:**
- Check browser console for API errors
- Check backend terminal for processing logs
- Verify state is being set correctly

---

## Performance Testing

1. **Multiple Actions**: Execute 10+ actions in sequence
2. **Rapid Clicks**: Try clicking actions very quickly
3. **Long Sessions**: Run simulation for 20+ turns
4. **Mode Switching**: Switch between different modes

**Expected:**
- ✅ No crashes or errors
- ✅ State updates correctly
- ✅ Logs don't overflow
- ✅ UI remains responsive

---

## Learning Analytics Testing

1. Complete a simulation session
2. Check if learning data is being tracked
3. Verify recommendations are generated

**Expected:**
- ✅ Assumptions are recorded
- ✅ Strategies are tracked
- ✅ Failures are logged
- ✅ Concepts are identified

---

## Final Checklist

Before considering the platform complete, verify:

- [ ] All four learning modes work
- [ ] Hypotheses can be formed and validated
- [ ] Actions execute and update state
- [ ] Delayed consequences trigger
- [ ] Contradictions appear when assumptions are wrong
- [ ] AI opponent adapts to user behavior
- [ ] Mentor AI only asks questions
- [ ] UI shows all four zones correctly
- [ ] No phase buttons or completion screens
- [ ] Actions are hypothesis-based (no exploit names)
- [ ] At least one action appears successful but fails later
- [ ] System feels continuous and alive

---

## Reporting Issues

If you find issues, note:
1. Which mode you were in
2. What action you took
3. What you expected to happen
4. What actually happened
5. Any console errors
6. Any backend terminal errors

Happy Testing! 🎯
