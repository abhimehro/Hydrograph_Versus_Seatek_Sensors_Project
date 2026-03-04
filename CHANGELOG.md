# Changelog

## [Unreleased](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/tree/HEAD)

[Full Changelog](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/compare/24b72e37ae61ab7992fb361b35dbcaca2d24d340...HEAD)

**Merged pull requests:**

- 🎨 Palette: Add accessible metadata to generated charts [\#36](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/36) ([abhimehro](https://github.com/abhimehro))
- ⚡ Bolt: Optimize Excel data loading by utilizing `usecols` and header inspection [\#35](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/35) ([abhimehro](https://github.com/abhimehro))
- 🛡️ Sentinel: \[HIGH\] Fix DoS risk in DataValidator [\#34](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/34) ([abhimehro](https://github.com/abhimehro))
- 🎨 Palette: Format Y-axis tick labels with thousands separators [\#33](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/33) ([abhimehro](https://github.com/abhimehro))
- ⚡ Bolt: Optimize navd88 conversion memory usage [\#32](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/32) ([abhimehro](https://github.com/abhimehro))
- 🛡️ Sentinel: \[HIGH\] Fix DoS Risk in Pandas read\_excel [\#31](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/31) ([abhimehro](https://github.com/abhimehro))
- 🎨 Palette: Improve chart accessibility with WCAG AA compliant colors [\#30](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/30) ([abhimehro](https://github.com/abhimehro))
- 🛡️ Sentinel: \[CRITICAL\] Fix missing constant for path-length restriction [\#29](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/29) ([abhimehro](https://github.com/abhimehro))
- ⚡ Bolt: Optimize large Excel file parsing during validation [\#28](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/28) ([abhimehro](https://github.com/abhimehro))
- 🛡️ Sentinel: \[MEDIUM\] Enhance filename sanitization to prevent path-length DoS [\#27](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/27) ([abhimehro](https://github.com/abhimehro))
- 🎨 Palette: Update chart color for WCAG AA accessibility [\#26](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/26) ([abhimehro](https://github.com/abhimehro))
- 🛡️ Sentinel: \[HIGH\] Fix path traversal in chart output generation [\#25](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/25) ([abhimehro](https://github.com/abhimehro))
- ⚡ Performance Optimization: Efficient Excel Validation in DataValidator [\#24](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/24) ([abhimehro](https://github.com/abhimehro))
- 🛡️ Sentinel: \[CRITICAL\] Fix Path Traversal Vulnerability [\#23](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/23) ([abhimehro](https://github.com/abhimehro))
- ⚡ Bolt: Optimize data validation with partial reads [\#22](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/22) ([abhimehro](https://github.com/abhimehro))
- ⚡ Optimize NAVD88 conversion performance [\#20](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/20) ([abhimehro](https://github.com/abhimehro))
- 🔒 Security Fix: Remove deprecated legacy code and utils [\#19](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/19) ([abhimehro](https://github.com/abhimehro))
- 🧪 Verify ValueError for missing river mile in process\_data [\#18](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/18) ([abhimehro](https://github.com/abhimehro))
- ⚡ Parallelize chart generation for ~2.8x performance boost [\#17](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/17) ([abhimehro](https://github.com/abhimehro))
- Refactor utils/logger.py to fix duplicate import [\#16](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/16) ([abhimehro](https://github.com/abhimehro))
- 🧪 Test coverage for hydrograph data loading [\#15](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/15) ([abhimehro](https://github.com/abhimehro))
- 🔒 fix: remove vulnerable debug script `path_tester.py` [\#14](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/14) ([abhimehro](https://github.com/abhimehro))
- test: add error handling test for ChartGenerator [\#13](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/13) ([abhimehro](https://github.com/abhimehro))
- 🧹 \[code health\] Remove duplicate legacy utils directory [\#12](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/12) ([abhimehro](https://github.com/abhimehro))
- 🔒 Security Fix: Remove hardcoded absolute path in utils/config.py [\#11](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/11) ([abhimehro](https://github.com/abhimehro))
- 🧹 Refactor utils/data\_loader.py to use src implementation [\#10](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/10) ([abhimehro](https://github.com/abhimehro))
- ⚡ Optimize Dataframe Copying in Processor [\#9](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/9) ([abhimehro](https://github.com/abhimehro))
- 🧪 Testing Improvement: DataValidator.run\_validation [\#8](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/8) ([abhimehro](https://github.com/abhimehro))
- test: add test for missing river mile in SeatekDataProcessor [\#7](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/7) ([abhimehro](https://github.com/abhimehro))
- Development environment setup [\#6](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/6) ([abhimehro](https://github.com/abhimehro))
- Bump fonttools from 4.56.0 to 4.61.0 in the pip group across 1 directory [\#5](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/5) ([dependabot[bot]](https://github.com/apps/dependabot))
- Add Python analysis workflow [\#4](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/4) ([abhimehro](https://github.com/abhimehro))
- Delete .github/workflows/pylint.yml [\#3](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/3) ([abhimehro](https://github.com/abhimehro))
- Delete .github/workflows/qodana\_code\_quality.yml [\#2](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/2) ([abhimehro](https://github.com/abhimehro))
- Add qodana CI checks [\#1](https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project/pull/1) ([qodana-cloud[bot]](https://github.com/apps/qodana-cloud))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
