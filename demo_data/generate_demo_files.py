import os
from pathlib import Path

demo_dir = Path(r"c:\Users\likhi\Downloads\Sovereign AI Workbench\demo_data")
demo_dir.mkdir(parents=True, exist_ok=True)

# 1. Inspection Report
report_txt = """SOVEREIGN INDUSTRIAL INSPECTION REPORT
Date of Inspection: 12 September 2026
Facility: MRPL Refinery Complex, Substation 04
Equipment Tag: V-04-PRV (Unit 04 Overpressure Relief Valve)
Inspected By: Senior Engineer Abhinaya

EXECUTIVE SUMMARY:
Routine annual inspection performed on Unit 04 Pressure Relief Valve assembly.

INSPECTION FINDINGS:
1. Pressure relief valve set point verified at 42.5 bar.
2. Minor surface oxidation observed on flange bolts B-04 and B-05.
3. The previous annual inspection expired on 30 August 2026. Current inspection status is OVERDUE.
4. The maintenance log section 04-B lacks the mandatory supervising engineer signature.

RECOMMENDATIONS:
- Replace flange gaskets and apply anti-corrosion coating to bolts.
- Obtain certified lead engineer sign-off before bringing Unit 04 back online.
- Perform hydrostatic pressure test at 45.0 bar test pressure.
"""
with open(demo_dir / "Inspection_Report_Unit04.txt", "w", encoding="utf-8") as f:
    f.write(report_txt)

# 2. Safety Regulation
reg_txt = """MINISTRY OF HEAVY INDUSTRIES & PSU SAFETY MANDATES
REGULATION REF: SAFETY-REG-2025-V2
Effective Date: 01 January 2025

SECTION 04.2: PRESSURE RELIEF SYSTEM MANDATES
1. Mandatory Inspection Frequency: All primary overpressure relief valves (PRV) installed on high-pressure steam and hydro-carbon lines must undergo comprehensive physical inspection and bench testing at intervals not exceeding twelve (12) calendar months.
2. Sign-Off Authorization: No pressure relief equipment shall be certified for active service without explicit double sign-off from both the primary inspector and the certified plant supervisor.
3. Non-Compliance Protocols: Any relief valve with an expired inspection window or unverified maintenance sign-off shall be immediately flagged as HIGH RISK and placed on operational hold.
"""
with open(demo_dir / "Safety_Regulation_2025.txt", "w", encoding="utf-8") as f:
    f.write(reg_txt)

# 3. Maintenance SOP
sop_txt = """STANDARD OPERATING PROCEDURE: EQUIPMENT MAINTENANCE & SIGN-OFF
SOP NUMBER: SOP-MAINT-04-REV3
Department: Maintenance & Asset Integrity

SECTION 02.1: MAINTENANCE SIGN-OFF AND APPROVAL WORKFLOW
1. Pre-Commissioning Verification: Prior to releasing any unit (including Unit 04) for active operational duty, the responsible technician must submit the completed physical inspection log.
2. Documentation Requirements:
   a) Hydrostatic pressure test logs attached.
   b) Component replacement certificates verified.
   c) Responsible engineer's physical or digital signature stamped in log section 04-B.
3. Approval Notes: An official Approval Note summarizing findings, regulatory compliance, and risk mitigations must be prepared and reviewed prior to supervisor authorization.
"""
with open(demo_dir / "Maintenance_SOP.txt", "w", encoding="utf-8") as f:
    f.write(sop_txt)

# 4. Equipment Manual
manual_txt = """EQUIPMENT TECHNICAL MANUAL - UNIT 04 OVERPRESSURE ASSEMBLY
MODEL: PRV-9000-HEAVY
Manufacturer: Sovereign Engineering Ltd.

TECHNICAL SPECIFICATIONS:
- Nominal Diameter: 250 mm (10 inches)
- Maximum Allowable Working Pressure (MAWP): 50.0 bar
- Factory Set Trip Pressure: 42.5 bar
- Temperature Range: -20°C to +350°C
- Body Material: Forged Stainless Steel 316L

OPERATIONAL SAFETY LIMITS:
- Operating pressures must remain below 42.5 bar during standard continuous operation.
- Hydrostatic test pressure limit: 1.5 x MAWP (75.0 bar max).
"""
with open(demo_dir / "Equipment_Manual.txt", "w", encoding="utf-8") as f:
    f.write(manual_txt)

print("Demo data files created successfully!")
