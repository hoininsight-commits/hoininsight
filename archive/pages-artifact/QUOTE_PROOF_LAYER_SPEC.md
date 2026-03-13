# Quote Proof Layer Specification (IS-31)

## 1. Overview
The Quote Proof Layer ensures that every signal emitted as a `TRIGGER` or `TRUST_LOCKED` decision is backed by a verbatim, official quote or text artifact from an authoritative source. This layer acts as the "final sanity check" for the linguistic integrity of the signal.

## 2. Source Categories & Enums

### Fact Type (Quote Context)
- `OFFICIAL_STATEMENT`: Direct transcript or statement from a gov/official body.
- `REGULATORY_FILING`: Excerpt from an SEC, KRX, or similar filing.
- `LEGAL_DOCKET`: Court or hearing schedule/item.
- `POLICY_EXCERPT`: Specific line from a bill or executive order.
- `TRANSCRIPT_EXCERPT`: Confirmed transcript from an earnings call or FOMC presser.
- `CALENDAR_ITEM`: Official schedule entry with date/time markers.

### Source Kind
- `GOV`: Government ministry or White House.
- `FILING`: SEC, DART, KRX.
- `EARNINGS_CALL`: Company IR official transcripts.
- `OFFICIAL_PRESS`: Official press releases from the entity itself.
- `REGULATOR`: Fed, BOK, SEC, FTC.
- `COURT`: Supreme Court or lower courts.

## 3. Reason Codes
- `PASS`: Requirement met (>=1 strong official or 2 independent medium).
- `HOLD:MISSING_QUOTE`: No valid quote artifact found.
- `HOLD:VAGUE_QUOTE`: Quote exists but lacks specific action/intent.
- `HOLD:LENGTH_EXCEEDED`: Quote is too long (>240 chars or >2 lines).
- `REJECT:NON_INDEPENDENT`: Sources for the quote are redundant or same-source.
- `HOLD:CONTEXT_NEEDED`: Quote lacks leading/trailing context for verification.

## 4. Verification Rules
- **Rule 1: Length**: Must be $\le 240$ chars and $\le 2$ lines.
- **Rule 2: Strength**: 
  - `OFFICIAL_TRANSCRIPT` with context $\implies$ **PASS**.
  - 1 Strong (`GOV`, `REGULATOR`) $\implies$ **PASS**.
  - 2 Independent Medium sources $\implies$ **PASS**.
- **Rule 3: Independence**: Different `source_kind` and different `source_ref`.

## 5. Mock Examples

### Example 1: SPEECH (Powell FOMC Statement Excerpt)
- **Source Kind**: `REGULATOR`
- **Source Ref**: `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`
- **Fact Type**: `TRANSCRIPT_EXCERPT`
- **Excerpt**: "The Committee does not expect it will be appropriate to reduce the target range until it has gained greater confidence that inflation is moving sustainably toward 2 percent."

### Example 2: POLICY (Bill Implementation)
- **Source Kind**: `GOV`
- **Source Ref**: `https://www.whitehouse.gov/briefing-room/`
- **Fact Type**: `POLICY_EXCERPT`
- **Excerpt**: "Effective immediately, all exports of specialized semiconductor chips to listed entities are suspended pending further technical review."

### Example 3: CALENDAR (Supreme Court Schedule)
- **Source Kind**: `COURT`
- **Source Ref**: `data/ops/scotus_docket_2026.json`
- **Fact Type**: `CALENDAR_ITEM`
- **Excerpt**: "No. 23-1234: Epic Systems Corp. v. Murphy. Oral Argument Scheduled for March 10, 2026, 10:00 AM."
