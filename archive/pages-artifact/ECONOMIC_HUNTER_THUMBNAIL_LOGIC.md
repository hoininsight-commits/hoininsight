# ECONOMIC_HUNTER_THUMBNAIL_LOGIC.md
# (Economic Hunter – Step 27)

## 0. Purpose
This engine is the **Art Director**.
It translates the abstract "Structural Pressure" into a single, silent image.

It does **NOT** explain.
It **Evokes**.
It forces the user to click to find the answer.

> "If the thumbnail explains the story, the click is unnecessary.
> The thumbnail must show the **Problem**, not the Solution."

---

## 1. The 4 Thumbnail Types (Visual Metaphors)

Every Thumbnail must fit one of these abstract patterns.

### Type A: The Collision
*Two massive forces meeting.*
- **Visual**: A ship crashing into a wall. A lightning bolt hitting a grid.
- **Meaning**: "Force meets Immovable Object."

### Type B: The Void
*Something missing where it should be.*
- **Visual**: An empty shelf in a warehouse. A blackout city. A missing piece of a puzzle.
- **Meaning**: "Supply Shock / Shortage."

### Type C: The Scale
*Massive imbalance.*
- **Visual**: A tiny object outweighing a huge object. A heavy weight crushing a support.
- **Meaning**: "Asymmetric Risk / Opportunity."

### Type D: The Barrier
*A blocked path.*
- **Visual**: A closed gate. A "Do Not Enter" sign. A red line on a map.
- **Meaning**: "Regulatory Ban / Market Access Denied."

---

## 2. The 3 Fixed Components

Every image is composed of ONLY these three elements.

1.  **The Spender (Object A)**: Representative of the Capital Source (e.g., Power Line, Ship, Tank).
2.  **The Bottleneck (Object B)**: Representative of the Shortage (e.g., Transformer, Metal, Chip).
3.  **The Strain (Action)**: The visual tension between them (Sparks, Cracks, Distance).

*Constraint*: Background must be Dark/High-Contrast. No busy scenes.

---

## 3. Forbidden Elements (Hard Rejection)

- **Faces**: No politicians, no CEOs. (Distraction).
- **Text/Numbers**: No "+50%", "Emergency". (That is the Title's job).
- **Stock Logos**: No Nvidia logo, no Samsung logo. (Looks like an ad).
- **Arrows**: No green "Up" arrows. (Cheap).

---

## 4. Output Schema: THUMBNAIL_SPEC

```json
{
  "thumbnail_id": "UUID",
  "topic_id": "UUID",
  "visual_type": "TYPE_B_VOID",
  "prompt_logic": "Dark warehouse with one single glowing transformer in the center. High contrast.",
  "components": {
    "object_a": "Industrial Warehouse (Dark)",
    "object_b": "Transformer (Glowing)",
    "strain": "Empty Space surrounding it"
  },
  "rejection_log": ["Rejected concept with green arrow."]
}
```

---

## 5. Mock Selection Process

**Topic**: UHV Transformer Shortage (LOCKED).

### Concept 1 (Accepted)
- **Type**: **Type B (The Void)**.
- **Visual**: A massive, dark electrical substation with one empty slot where a transformer should be. Sparks flying from loose cables.
- **Verdict**: **KEEP**. (Shows the problem: Missing hardware).

### Concept 2 (Rejected)
- **Type**: Generic.
- **Visual**: HD Hyundai Electric logo with a green arrow going up.
- **Verdict**: **REJECT**. (Reason: "Stock Logo + Arrow". Looks like a pump-and-dump video).

### Concept 3 (Rejected)
- **Type**: Face.
- **Visual**: Elon Musk looking worried next to a power line.
- **Verdict**: **REJECT**. (Reason: "Face". Relies on celebrity, not structure).

---

## 6. Absolute Prohibition
**Never** use a thumbnail that looks like a Financial Youtuber.
Use a thumbnail that looks like a **Netflix Documentary**.
Cinematic. Dark. Serious.
