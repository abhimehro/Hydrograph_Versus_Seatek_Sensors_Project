## 2025-03-05 - Avoid Alpha for Data Markers

**Learning:** Data points in scatter plots with `alpha` (opacity) below 1.0 on a white background visually lighten the marker color. A WCAG-compliant color like `#A63600` (which has a 6.67:1 contrast ratio) may drop below the required 3.0:1 non-text contrast ratio if rendered at `alpha=0.7`.
**Action:** When plotting accessible charts, avoid using `alpha` to handle overlapping data points. Instead, use `alpha=1.0` combined with subtle marker edge outlines (e.g., `edgecolors='white', linewidth=0.5`) or distinct markers to distinguish overlapping data while maintaining the true contrast of the base color.

## 2026-03-04 - Accessible Chart Metadata

**Learning:** Data visualizations saved as PNGs are opaque to screen readers unless embedded in an HTML `<img>` tag with proper `alt` text. However, users often download or share these PNGs independently.
**Action:** Always embed descriptive `Title`, `Description` (acting as alt-text), and `Author` metadata directly into the PNG file using Matplotlib's `savefig(metadata={...})`. This ensures accessibility information travels with the file wherever it goes.

## 2025-03-05 - Chart Color Contrast

**Learning:** When using colors to distinguish data points in charts, as well as for associated text labels, it's crucial to ensure sufficient color contrast against the background to meet WCAG AA guidelines (1.4.11 for Non-text Contrast, requiring 3.0:1, and 1.4.3 for Contrast (Minimum), requiring 4.5:1 for regular text). The original orange `#FF7F0E` had a contrast ratio of 2.53:1 against white, which fails both standards.
**Action:** Always verify the contrast ratio of data visualization colors, particularly when the same color is used for text labels. Darken the color to ensure it has at least a 4.5:1 ratio if used for text, or 3.0:1 if only used for graphical objects. In this case, darkening to `#CC4C02` achieved a 4.56:1 contrast ratio while keeping the semantic "orange" meaning.

## 2024-03-24 - Accessible Matplotlib Colors

**Learning:** Default Matplotlib/Seaborn qualitative palettes (like tab10) often fail WCAG AA 4.5:1 contrast requirements for colored text on a white background. For instance, `#CC4C02` is only ~4.56:1, and `#1F77B4` is ~4.82:1.
**Action:** Always check generated hexadecimal colors using a luminance/contrast calculator when assigning them to text (like axis labels or plot titles). Darker shades like `#A63600` (Seatek, 6.67:1) and `#0E5A8A` (Hydrograph, 7.37:1) should be used as standard design tokens for accessibility in data visualization projects.

## 2025-03-07 - Opaque Legend Backgrounds

**Learning:** Semi-transparent legend backgrounds (e.g., `framealpha=0.9`) in data visualizations can cause underlying data lines or grid lines to bleed through, which reduces the contrast ratio of the legend text and can cause it to fail WCAG accessibility standards.
**Action:** Always use fully opaque backgrounds (`framealpha=1.0`) for chart legends that overlap the plot area, combined with a distinct edge color (`edgecolor='#333333'`) to ensure optimal contrast and readability for all users.

## 2024-05-24 - Persistent Legends in Dynamic Charts

**Learning:** In dynamically generated charts (where secondary datasets like a hydrograph might be absent), coupling the legend generation to the secondary dataset's plotting function causes the legend to disappear entirely for single-axis plots, reducing clarity. Additionally, large raw numbers on axes (e.g., 50000 for minutes) reduce quick readability.
**Action:** Always decouple legend creation from individual plot layers. Collect handles and labels from all active axes at the end of the chart generation process to ensure a legend is always rendered. Furthermore, apply comma formatting (`{x:,.0f}`) to large numeric axes to improve cognitive ease.

## 2026-03-10 - Legend Placement UX

**Learning:** Making chart legends fully opaque (`framealpha=1.0`) is excellent for accessibility (WCAG contrast compliance). However, placing an opaque legend inside the plot area (`loc="upper right", bbox_to_anchor=(0.99, 0.99)`) creates a new UX problem: it completely obscures underlying data points.
**Action:** When designing data visualizations with opaque legends, always place the legend _outside_ the chart bounding box (e.g., `loc="upper center", bbox_to_anchor=(0.5, -0.15)`) so that 100% of the data remains visible to users without compromising the accessibility of the text.

## 2025-03-11 - Defensive Matplotlib Secondary Axis Extraction

**Learning:** When trying to fix a bug relating to hardcoded properties (e.g., replacing `.right_ax` with index-based secondary axis selection `fig.axes[1]`), failing to verify that the extracted object is a valid plotting axes before calling methods like `get_legend_handles_labels()` can cause the application to crash.
**Action:** When collecting legend handles from secondary axes in dynamically generated Matplotlib charts (e.g., iterating through `fig.axes`), always use defensive checks like `hasattr(ax, 'get_legend_handles_labels')` prior to extraction to prevent runtime crashes.

## 2026-03-12 - CLI Visual Cues and Formatting

**Learning:** Command-line interfaces that output dense, unformatted text are difficult for users to scan quickly. Large numbers without formatting (e.g., `123456`) increase cognitive load, and lack of visual state indicators makes identifying failures slower.
**Action:** When designing CLI output, use emojis (`✅`, `❌`, `⚠️`) as quick visual cues for state. Apply comma formatting (`{:,}`) to large numbers and center-align headers to create a more delightful and readable user experience.

## 2025-03-16 - CLI Error Message Actionability

**Learning:** Command-line interfaces that return generic "VALIDATION FAILED" or "No processed files found" leave users guessing what to do next, which leads to frustration and friction.
**Action:** Always provide actionable hints (e.g., "💡 Please ensure 'Data_Summary.xlsx' is in the data/raw/ directory") in CLI error output to guide users toward resolving the issue themselves.
