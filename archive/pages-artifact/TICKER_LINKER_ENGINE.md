# TICKER LINKER ENGINE (Step 4)

**Role:** The Bridge. Connects the abstract "Bottleneck" (Step 3) to specific "Tickers" (Real-world Companies).
**Input:** 1~3 Verified Bottleneck Entities (from Step 3).
**Output:** locked_ticker_card (1~3 Tickers) OR REJECT.

---

## 1. Module 1: BOTTLENECK_SLOT_TO_COMPANY_MAP

### Objective
Identify companies that *currently* occupy the bottleneck slot defined in Step 3.

### Rule: "Theoretical is Forbidden"
*   **Allowed:** Companies that *are* selling the bottleneck item today.
*   **Forbidden:** Companies that *plan* to sell it, *might* sell it, or *announced a roadmap* to sell it. "Coming Soon" = REJECT.

---

## 2. Module 2: REALITY_FILTER

### Objective
Purge any company that fails the "Real Business" test. Eliminate "Concept Stocks."

### The 5-Point Reality Check (Must Pass at least 4/5)
1.  **Revenue Existence:** Does this specific product generate >10% of revenue (or is growing >50% YoY)? If it's a 1% side-project, REJECT.
2.  **Delivery Record:** Have they actually shipped this product to a client? (Press release of "partnership" is NOT delivery).
3.  **Regulatory/Cert Clearance:** Do they hold the necessary license (FDA, Mil-spec, ISO, Grid Code)?
4.  **Production Scale:** Can they make it *at scale*? (Lab prototypes don't count for structural flows).
5.  **Lead-Time Feasibility:** Can they deliver within the "Why Now" timeframe? (If they are sold out for 5 years, can they actually capture *new* money? If yes via pricing power -> Pass. If no via capacity lock -> Warning).

**Rejection Rule:** Fail 2 or more = **IMMEDIATE REJECT**.

---

## 3. Module 3: MONOPOLY_PRESSURE_SCORE

### Objective
Force-rank the survivors to ensure the list collapses to **1~3** winners.

### Scoring Criteria
1.  **Market Share:** Who owns >50%? (The King).
2.  **Switching Cost:** Who is hardest to fire? (The Lock).
3.  **Installed Base:** Who dominates the existing infrastructure? (The Legacy).
4.  **Expansion Speed:** Who is building capacity fastest? (The Hunter).

### The Collapse Rule (Hard Constraint)
*   **1 Winner:** The Monopoly. -> **LOCK**.
*   **2 Winners:** The Duopoly. -> **LOCK**.
*   **3 Winners:** The Oligopoly. -> **LOCK**.
*   **4+ Winners:** The Commodity. -> **REJECT** (LOCK FORBIDDEN).

*If 4 companies pass the Reality Filter, use the Score to cut the weakest link. If you cannot statistically prove he is weak, then the whole thesis is too fragmented -> REJECT.*

---

## 4. Module 4: ANTI-HALLUCINATION_GUARDRAIL

### Objective
Ensure every selected ticker is backed by hard facts, not narrative.

### Validation Rule
Each ticker must cite **at least 2** independent "Hard Facts":
*   **Fact A (Contract/Money):** "Signed $1B deal with [Client]" or "Backlog increased 30%".
*   **Fact B (Tech/Cert):** "Passed NVIDIA qualification test" or "Only vendor with [Spec]".

*Forbidden Sources:* "Rumored," "Analysts expect," "Company roadmap," "Forum speculation."

---

## 5. Output Logic
*   **Success:** 1~3 Tickers passed all filters. -> Output `LOCKED_TICKER_CARD`.
*   **Failure:**
    *   0 Tickers passed Reality Filter. -> `REJECT: NO_REAL_PLAYER`.
    *   4+ Tickers remained after Scoring. -> `REJECT: FRAGMENTED_MARKET`.
    *   Evidence missing. -> `REJECT: INSUFFICIENT_PROOF`.
