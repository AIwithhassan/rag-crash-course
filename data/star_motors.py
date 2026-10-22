"""
Star Motors knowledge base
==========================

A fictional motorcycle maker. Every document has some text plus a few
LABELS (metadata). We'll use the labels in Level 4 for filtering.

Labels on every document:
  doc_type   -> "hr_policy", "manual", "parts_catalog", "safety"
  department -> "hr", "maintenance", "parts", "safety"
  access     -> "all_staff" (anyone) or "hr_only" (confidential)
  year       -> which year this version of the document is for

Each paragraph (separated by a blank line) becomes one CHUNK.
"""

DOCUMENTS = [
    # ------------------------------------------------------------------ HR
    {
        "title": "Remote Work Policy",
        "doc_type": "hr_policy", "department": "hr", "access": "all_staff", "year": 2026,
        "text": """Employees in office roles may do remote work up to two days per week. Remote days must be agreed with your team lead at least one week in advance.

Fridays are the preferred remote day for office staff, because most team meetings are scheduled Monday to Thursday.

Factory floor, assembly line and workshop roles are not eligible for remote work, because the work requires physical presence at the plant.""",
    },
    {
        "title": "Casual Leave Policy 2026",
        "doc_type": "hr_policy", "department": "hr", "access": "all_staff", "year": 2026,
        "text": """From 1 January 2026, every permanent employee gets 14 days of casual leave per calendar year.

Up to 3 unused casual leave days can be carried over to the next year. Casual leave must be requested in the HR portal at least 2 days in advance, except in emergencies.""",
    },
    {
        "title": "Casual Leave Policy 2025",
        "doc_type": "hr_policy", "department": "hr", "access": "all_staff", "year": 2025,
        "text": """In 2025, every permanent employee gets 10 days of casual leave per calendar year.

Unused casual leave cannot be carried over to the next year. Casual leave must be requested by email to HR at least 5 days in advance.""",
    },
    {
        "title": "Salary Bands (Confidential)",
        "doc_type": "hr_policy", "department": "hr", "access": "hr_only", "year": 2026,
        "text": """Manager salary band for 2026: 95,000 to 120,000 euros per year, plus a performance bonus of up to 15 percent.

Intern stipend for 2026: 1,400 euros per month. Team lead salary band: 70,000 to 88,000 euros per year.""",
    },
    # --------------------------------------------------------- Maintenance
    {
        "title": "Maintenance Manual: Brakes",
        "doc_type": "manual", "department": "maintenance", "access": "all_staff", "year": 2026,
        "text": """Brake squeaking or squealing when stopping is usually caused by worn brake pads, glazed pads, or dust between the pad and the disc.

To fix brake squeal: clean the disc with brake cleaner, check pad thickness, and replace the pads if they are thinner than 2 mm. Always replace pads on both sides of the wheel.

The brake system on all Star Motors city bikes uses hydraulic disc brakes. Brake fluid should be replaced every 2 years.""",
    },
    {
        "title": "Maintenance Manual: Engine Oil",
        "doc_type": "manual", "department": "maintenance", "access": "all_staff", "year": 2026,
        "text": """Engine oil leaks: if you see engine oil under the bike, check the engine oil drain plug, the engine oil filter seal and the engine gasket. Engine oil leaking onto a hot engine can smoke. Clean the area and top up the engine oil.

Service schedule: drain and replace the oil, and fit a new filter, every 5,000 km or every 6 months, whichever comes first. Use 10W-40 semi-synthetic oil.""",
    },
    {
        "title": "Assembly Machine Error Codes",
        "doc_type": "manual", "department": "maintenance", "access": "all_staff", "year": 2026,
        "text": """Assembly machine 3 is the frame welding robot in Hall B.

Error E-14 on machine 3 means the welding torch is not reaching temperature. Fix: switch the machine off, check the gas supply valve is fully open, clean the torch nozzle, then restart. If E-14 appears again, call the maintenance supervisor.

Error E-21 on machine 3 means the safety door is open. Close the door fully until it clicks, then press reset.""",
    },
    # ------------------------------------------------------------- Parts
    {
        "title": "Spare Parts Catalog: Brakes",
        "doc_type": "parts_catalog", "department": "parts", "access": "all_staff", "year": 2026,
        "text": """Part BRK-2207: rear brake pad set for the City 125. Price: 34 euros.

Part BRK-2210: front brake pad set for the City 125. Price: 39 euros.

Part BRK-2270: rear brake pad set, sintered, for the City 125 Sport. Price: 46 euros.

Part BRK-1907: rear brake pad set for the Trail 250. Price: 42 euros.

Part BRK-1910: front brake pad set for the Trail 250. Price: 44 euros.

Part BRK-2072: front brake pad set, organic, for the Cruiser 300. Price: 37 euros.

Part BRK-3001: front brake disc, 260 mm, for the City 125 and Trail 250. Price: 89 euros.

Part BRK-3007: rear brake disc, 220 mm, for the City 125. Price: 71 euros.

Part BRK-4100: brake lever, left side, for all models. Price: 18 euros.""",
    },
    {
        "title": "Spare Parts Catalog: Engine",
        "doc_type": "parts_catalog", "department": "parts", "access": "all_staff", "year": 2026,
        "text": """Part ENG-0410: oil filter for the City 125. Price: 12 euros.

Part ENG-0415: oil filter for the Trail 250. Price: 14 euros.

Part ENG-1100: engine gasket kit for the City 125. Price: 58 euros.""",
    },
    # ------------------------------------------------------------ Safety
    {
        "title": "Workshop Safety Rules",
        "doc_type": "safety", "department": "safety", "access": "all_staff", "year": 2026,
        "text": """Safety glasses and steel-toe boots are mandatory in the workshop and on the assembly line at all times.

Never work under a bike that is only held by a side stand. Always use a certified paddock stand or lift.

Brake cleaner and engine oil are flammable. Keep them away from welding areas and dispose of used oil in the red containers.""",
    },
]
