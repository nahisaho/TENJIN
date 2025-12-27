#!/usr/bin/env python3
"""Extract priority 5 and 4 theories from Educational-theory-research.md."""

import json
import re
from pathlib import Path

# Read the markdown file
md_path = Path(__file__).parent.parent / "References" / "Educational-theory-research.md"
with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

# Category mapping
CATEGORY_MAP = {
    "学習理論": "learning_theory",
    "発達理論": "developmental",
    "教授法・指導法理論": "instructional_design",
    "カリキュラム理論": "curriculum",
    "動機づけ理論": "motivation",
    "評価理論": "assessment",
    "社会的学習理論": "social_learning",
    "東洋・アジア教育理論": "asian_education",
    "テクノロジー活用理論": "technology_enhanced",
    "現代教育理論": "modern_education",
    "批判的教育理論・オルタナティブ教育・特別支援教育": "critical_alternative_special",
}

# Parse theories by section
theories_p5 = []
theories_p4 = []

# Split by main sections
sections = re.split(r'\n## ', content)

current_category = None
current_priority = None

for section in sections:
    # Detect category
    for cat_ja, cat_en in CATEGORY_MAP.items():
        if section.startswith(cat_ja):
            current_category = cat_en
            break
    
    # Find priority sections
    lines = section.split('\n')
    for i, line in enumerate(lines):
        if '### 優先度5' in line:
            current_priority = 5
        elif '### 優先度4' in line:
            current_priority = 4
        elif '### 優先度3' in line:
            current_priority = 3
        elif line.startswith('| ') and '|' in line and current_priority in [5, 4]:
            # Parse table row
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 4 and parts[0] and not parts[0].startswith('---') and parts[0] != '理論名（日本語）':
                theory = {
                    "name_ja": parts[0],
                    "name": parts[1] if len(parts) > 1 else "",
                    "theorists": parts[2] if len(parts) > 2 else "",
                    "description_ja": parts[3] if len(parts) > 3 else "",
                    "category": current_category,
                    "priority": current_priority,
                }
                if current_priority == 5:
                    theories_p5.append(theory)
                else:
                    theories_p4.append(theory)

print(f"優先度5の理論数: {len(theories_p5)}")
print(f"優先度4の理論数: {len(theories_p4)}")
print(f"合計: {len(theories_p5) + len(theories_p4)}")

print("\n=== 優先度5の理論 ===")
for t in theories_p5:
    print(f"  - {t['name_ja']} ({t['name']}) [{t['category']}]")

print("\n=== 優先度4の理論 ===")
for t in theories_p4:
    print(f"  - {t['name_ja']} ({t['name']}) [{t['category']}]")

# Save to JSON for reference
output = {
    "priority_5": theories_p5,
    "priority_4": theories_p4,
}

output_path = Path(__file__).parent / "extracted_theories.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n保存先: {output_path}")
