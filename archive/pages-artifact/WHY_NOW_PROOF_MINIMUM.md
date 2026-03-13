# WHY_NOW_PROOF_MINIMUM.md
# (Economic Hunter – Step 14)

## 0. Purpose

This engine is the **Notary Public**.
It verifies that the `WHY_NOW_CANDIDATE` (Step 13)
is supported by **Hard Evidence**, not just sentiment.

It asks:
> "Can you prove, beyond reasonable doubt,
> that this event actually happened?"

It does **NOT** judge importance.
It judges **Veracity**.

---

## 1. Proof Minimum Definition (The 4 Pillars)

A Candidate must possess ALL 4 components to be valid.

### 1. Primary Source Requirement
- Must trace back to the Originator.
- *Valid:* Government PDF, Federal Register, Company IR Filing, Official Transcript.
- *Invalid:* News summary, Analyst report, Twitter/Blog post.

### 2. Timestamped Commitment
- Must have a specific date attached to the action.
- *Valid:* "Effective Jan 1, 2026", "Meeting on Feb 14", "Q3 Earnings Call timestamp".
- *Invalid:* "Soon", "In the near future", "Recently".

### 3. Actionable Clause
- Must contain verb phrases that imply force.
- *Valid:* "Shall", "Must", "Ban", "Authorize", "Allocate".
- *Invalid:* "Consider", "Explore", "discuss", "hope".

### 4. Non-Optionality Signal
- Must show that the actor cannot easily reverse course.
- *Valid:* Signed Law, Budget Contract, Physical Breakdown.
- *Invalid:* MOU (Memorandum of Understanding), Campaign Promise.

---

## 2. Acceptance Thresholds

### LEVEL A: STRONG PROOF (Direct Pass)
- **Source**: Official Legal Document / Regulatory Filing.
- **Language**: "Mandatory", "Effective Immediately".
- **Action**: Pass to Step 15 (Context Analysis).

### LEVEL B: VALID PROOF (Standard Pass)
- **Source**: CEO/Official Direct Quote (Transcript).
- **Language**: Specific timeline + Dollar amount.
- **Action**: Pass to Step 15.

### LEVEL C: INSUFFICIENT PROOF (Reject/Return)
- **Source**: Secondary reporting ("According to sources").
- **Language**: Defensive or Vague.
- **Action**: Return to PRESSURE_BUILDING (Step 12/13).

---

## 3. Rejection Conditions

Proof is rejected PERMANENTLY if:
1.  **Circular Citation**: News A cites News B which cites News A.
2.  **Anonymous Sources**: "People familiar with the matter" (unless price action confirms).
3.  **Outdated**: Evidence is > 72 hours old without update.

---

## 4. Output Schema: WHY_NOW_PROOF_PACKET

```json
{
  "proof_id": "UUID",
  "candidate_packet_id": "UUID",
  "verification_status": "STRONG / VALID / INSUFFICIENT",
  "primary_source_url": "https://gov.us/...",
  "verbatim_quote": "Section 401(a): All entities must replace...",
  "timestamp_of_action": "ISO-8601",
  "modality_check": "PASSED (Contains 'Shall')"
}
```

---

## 5. Mock Examples

### Mock 1: SOLID (Pass)
- **Candidate**: EPA Emission Standard.
- **Trigger**: New Rule publication.
- **Proof**: Link to Federal Register final rule. Search finding "Effective Date: Model Year 2027".
- **Verdict**: `STRONG PROOF`

### Mock 2: VALID (Pass)
- **Candidate**: Hyperscaler Capex Hike.
- **Trigger**: Earnings Call Q&A.
- **Proof**: Transcript. CFO says "We are raising FY26 guidance by $4B to secure GPU supply."
- **Verdict**: `VALID PROOF`

### Mock 3: REJECT (Fail)
- **Candidate**: M&A Rumor.
- **Trigger**: News article.
- **Proof**: "Bloomberg reports Company X considering bid."
- **Verdict**: `INSUFFICIENT PROOF` (Return to Pressure).

---

## 6. Strict Rule
**"No Link, No Logic."**
If the primary source cannot be hyperlinked or referenced, it does not exist.
