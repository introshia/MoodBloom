# 📒 Almanac Adjustment Guide

This guide helps you manually "nudge" the visual alignment of the MoodBloom Almanac (Journal) in [journal.html](file:///Users/dannamayd.desear/Documents/MoodBloom/templates/pages/journal.html).

---

## 📄 1. Page Size & Vertical Position
Controls the physical sheets of the journal.

*   **Selector**: `.al-page`
*   **CSS Location**: Around line 254
*   **Properties**:
    *   `top`: Increase this (e.g., `6%`, `7%`) to move the pages **lower**.
    *   `width`: Increase this to make the pages **wider**.
    *   `height`: Increase this to make the pages **longer**.
    *   `left`: Keep at `50%` to ensure the "fold" stays in the center.

```css
.al-page {
    position: absolute;
    left: 50%;
    top: 5.5%; /* Adjust vertical placement */
    width: 45%;  /* Adjust sheet width */
    height: 89%; /* Adjust sheet height */
    /* ... */
}
```

---

## 🕳️ 2. The Spine Gap (Reveal Rings)
Controls how much "breathing room" there is around the binder rings.

*   **Selector**: `.al-pf, .al-pb`
*   **CSS Location**: Around line 265
*   **Properties**:
    *   `left`: Increasing this (e.g., `2%`, `3%`) pushes the paper **away from the rings**.
    *   `width`: If you increase `left`, you should decrease `width` slightly so the paper doesn't stick out the other side.

```css
.al-pf, .al-pb {
    left: 1.5%; /* Increase for a wider gap */
    width: 98.5%; /* Must add up to 100% with left */
    /* ... */
}
```

> [!TIP]
> **The Rule of 100**: To keep the page perfectly aligned, make sure `left` + `width` = `100%`. 
> *   If you increase `left` to **3%**, change `width` to **97%**.
> *   If you increase `left` to **5%**, change `width` to **95%**.

---

## 💍 3. Golden Rings Overlay
Controls the "Front Arches" that sit on top of the pages. 

> [!CAUTION] 
> **Container vs Image**: 
> *   `.spine-container`: Always leave `top` and `bottom` at **5%**. If you change these, the rings will **stretch or squish**.
> *   `.rings-front`: This is what you nudge! **Increase** the `top` here to move the rings down safely.

*   **Selector**: `.rings-front`
*   **CSS Location**: Around line 436
*   **Properties**:
    *   `top`: **Increase** this (e.g., `25%`) to move the rings **lower**.
    *   `top`: **Decrease** this (e.g., `18%`) to move the rings **higher**.

> [!TIP]
> **The Rubber Band Rule (Vertical Spacing)**:
> *   **Increase Height** (e.g., `80%`) = **Stretches** rings further apart.
> *   **Decrease Height** (e.g., `55%`) = **Squeezes** rings closer together.

```css
.rings-front {
    width: 100%;
    height: 58.9%;      /* Adjust this based on the Rubber Band Rule */
    object-fit: fill;   
    position: absolute;
    top: 19.5%;           
}
```

---

## 📘 4. Outer Binder Size (Overall Scale)
Controls how large the entire notebook appears on your screen.

*   **Selector**: `.al-book-wrap`
*   **CSS Location**: Around line 205
*   **Properties**:
    *   `width`: Controls the size on smaller screens (e.g., `95vw` for "Full Screen").
    *   `max-width`: Controls the maximum size on large desktop monitors (e.g., `1400px` for a "Massive" binder).
    *   **Note**: Because of `aspect-ratio: 1.6 / 1`, the height will follow the width automatically!

```css
.al-book-wrap {
    width: 90vw;      /* Increase for mobile/tablets */
    max-width: 1200px; /* Increase for large desktop screens */
    /* ... */
}
```

> [!IMPORTANT]
> **Why does it stop growing?**
> If you set a high `max-width` (like `1700px`) but the book still looks the same, your **`width: 90vw`** is likely hitting your screen's edge. 
> *   `90vw` means "90% of your screen width."
> *   If your screen is 1800px wide, `90vw` is `1620px`. The book will **stop** there even if your `max-width` is higher. 
> *   To make it even larger, increase `width` to `95vw` or `98vw`.

---

## 💍 5. Scaling the Rings Overlay
To make the metal arches appear larger or smaller *proportionally*.

> [!TIP] 
> **The Magic Variable**: We now use **--ring-scale** in your CSS (around line 413). This means you only have to change **one number** and the math (like centering) happens automatically!

*   **Selector**: `:root`
*   **CSS Location**: Around line 413
*   **Properties**:
    *   `--ring-scale`: **Increase** (e.g., `10%`) to make rings **larger**.
    *   `--ring-scale`: **Decrease** (e.g., `8.5%`) to make rings **smaller**.

```css
:root {
    --ring-scale: 9.3%; /* Tweak this ONE number to resize the rings! */
}
```

> [!TIP]
> **Horizontal Nudge**: If the rings are the right size but just need to move a tiny bit left/right:
> *   Edit the `left: 50%` in `.spine-container`. 
> *   Try **`49.5%`** to move them **LEFT**.
> *   Try **`50.5%`** to move them **RIGHT**.

> [!TIP]
> **Horizontal Pinch**: If you want the rings to be "thinner" or "flatter" horizontally without changing their height:
> *   Add `transform: scaleX(0.8);` to `.rings-front`. 
> *   Use numbers **smaller than 1.0** to **THIN** them.
> *   Use numbers **larger than 1.0** to **WIDEN** them.

---

## 💡 Quick Tips
1.  **Use Browser Inspector (F12)**: 
    *   Right-click the page in your browser and select **Inspect**.
    *   Find the element (like `.al-page`) in the Styles tab.
    *   Tick the numbers up and down until it looks perfect.
2.  **Aspect Ratio**: The whole book is locked to a `1.6 / 1` ratio. If you change the main `.al-book-wrap` width, the height will scale automatically!
