## 2026-03-04 - Accessible Chart Metadata

**Learning:** Data visualizations saved as PNGs are opaque to screen readers unless embedded in an HTML `<img>` tag with proper `alt` text. However, users often download or share these PNGs independently.
**Action:** Always embed descriptive `Title`, `Description` (acting as alt-text), and `Author` metadata directly into the PNG file using Matplotlib's `savefig(metadata={...})`. This ensures accessibility information travels with the file wherever it goes.

## 2025-03-05 - Chart Color Contrast

**Learning:** When using colors to distinguish data points in charts, as well as for associated text labels, it's crucial to ensure sufficient color contrast against the background to meet WCAG AA guidelines (1.4.11 for Non-text Contrast, requiring 3.0:1, and 1.4.3 for Contrast (Minimum), requiring 4.5:1 for regular text). The original orange `#FF7F0E` had a contrast ratio of 2.53:1 against white, which fails both standards.
**Action:** Always verify the contrast ratio of data visualization colors, particularly when the same color is used for text labels. Darken the color to ensure it has at least a 4.5:1 ratio if used for text, or 3.0:1 if only used for graphical objects. In this case, darkening to `#CC4C02` achieved a 4.56:1 contrast ratio while keeping the semantic "orange" meaning.

## 2024-03-24 - Accessible Matplotlib Colors
**Learning:** Default Matplotlib/Seaborn qualitative palettes (like tab10) often fail WCAG AA 4.5:1 contrast requirements for colored text on a white background. For instance, `#CC4C02` is only ~4.56:1, and `#1F77B4` is ~4.82:1.
**Action:** Always check generated hexadecimal colors using a luminance/contrast calculator when assigning them to text (like axis labels or plot titles). Darker shades like `#A63600` (Seatek, 6.67:1) and `#0E5A8A` (Hydrograph, 7.37:1) should be used as standard design tokens for accessibility in data visualization projects.
