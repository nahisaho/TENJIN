#!/usr/bin/env python3
"""Generate comprehensive relationships.json from theories.json."""

import json
from pathlib import Path
from datetime import datetime

# Read theories
theories_path = Path(__file__).parent.parent / "data" / "theories" / "theories.json"
with open(theories_path, "r", encoding="utf-8") as f:
    theories_data = json.load(f)

# Create theory lookup by name
theory_by_name = {}
theory_by_id = {}
for t in theories_data["theories"]:
    theory_by_name[t["name"]] = t
    theory_by_name[t["name_ja"]] = t
    theory_by_id[t["id"]] = t

# Define known relationships between theories
KNOWN_RELATIONSHIPS = [
    # Learning Theory relationships
    ("Operant Conditioning", "Social Learning Theory", "influences", 0.8, "Operant conditioning influenced the development of social learning theory."),
    ("Social Learning Theory", "Social Cognitive Theory", "evolved_into", 0.95, "Social learning theory evolved into social cognitive theory."),
    ("Social Cognitive Theory", "Self-Efficacy Theory", "derived_from", 0.9, "Self-efficacy theory was derived from social cognitive theory."),
    ("Constructivism", "Social Constructivism", "influences", 0.9, "Piagetian constructivism influenced social constructivism."),
    ("Social Constructivism", "Zone of Proximal Development", "derived_from", 0.95, "ZPD is derived from social constructivism."),
    ("Zone of Proximal Development", "Scaffolding Theory", "influences", 0.9, "ZPD influenced scaffolding theory."),
    ("Cognitive Development Theory", "Constructivism", "influences", 0.85, "Piaget's cognitive development influenced constructivist learning."),
    ("Experiential Learning Theory", "Constructivism", "complements", 0.85, "Experiential learning complements constructivism."),
    ("Classical Conditioning", "Operant Conditioning", "influences", 0.75, "Classical conditioning influenced operant conditioning development."),
    ("Behaviorism", "Operant Conditioning", "derived_from", 0.9, "Operant conditioning derives from behaviorism."),
    ("Behaviorism", "Classical Conditioning", "derived_from", 0.9, "Classical conditioning derives from behaviorism."),
    
    # Instructional Design relationships
    ("Bloom's Taxonomy", "ADDIE Model", "influences", 0.8, "Bloom's taxonomy influenced ADDIE model development."),
    ("Gagné's Nine Events of Instruction", "ADDIE Model", "complements", 0.85, "Gagné's events complement ADDIE model."),
    ("Scaffolding Theory", "Scaffolding", "same_as", 0.99, "Same theoretical foundation."),
    ("Constructivism", "Constructivist Learning Theory", "same_as", 0.99, "Same theoretical foundation."),
    ("Project-Based Learning", "Problem-Based Learning", "complements", 0.9, "PBL approaches complement each other."),
    ("Flipped Learning", "Blended Learning", "complements", 0.85, "Flipped learning is a form of blended learning."),
    ("Mastery Learning", "Bloom's Taxonomy", "derived_from", 0.8, "Mastery learning derives from Bloom's work."),
    ("Direct Instruction", "Mastery Learning", "complements", 0.75, "Direct instruction complements mastery learning."),
    
    # Motivation relationships
    ("Self-Determination Theory", "Growth Mindset", "complements", 0.75, "SDT complements growth mindset through intrinsic motivation."),
    ("Self-Efficacy Theory", "Expectancy-Value Theory", "complements", 0.8, "Self-efficacy complements expectancy-value theory."),
    ("Attribution Theory", "Expectancy-Value Theory", "complements", 0.8, "Attribution theory complements expectancy-value."),
    ("Growth Mindset", "Achievement Goal Theory", "complements", 0.85, "Growth mindset complements achievement goal theory."),
    ("Flow Theory", "Self-Determination Theory", "complements", 0.7, "Flow theory complements SDT."),
    ("Hierarchy of Needs", "Self-Determination Theory", "influences", 0.7, "Maslow influenced self-determination theory."),
    ("Grit", "Growth Mindset", "complements", 0.85, "Grit complements growth mindset."),
    ("Goal Setting Theory", "Achievement Goal Theory", "complements", 0.8, "Goal setting complements achievement goals."),
    
    # Developmental relationships
    ("Cognitive Development Theory", "Psychosocial Development Theory", "complements", 0.7, "Piaget and Erikson complement each other."),
    ("Attachment Theory", "Psychosocial Development Theory", "complements", 0.75, "Attachment theory complements psychosocial development."),
    ("Theory of Moral Development", "Cognitive Development Theory", "extends", 0.8, "Kohlberg extended Piaget's work on moral development."),
    ("Ecological Systems Theory", "Social Constructivism", "complements", 0.75, "Bronfenbrenner complements Vygotsky's social context focus."),
    
    # Technology-Enhanced Learning relationships
    ("Cognitive Load Theory", "Cognitive Theory of Multimedia Learning", "influences", 0.85, "CLT influenced multimedia learning theory."),
    ("Connectivism", "Learning Analytics", "influences", 0.75, "Connectivism influenced learning analytics."),
    ("TPACK", "Blended Learning", "complements", 0.8, "TPACK framework guides blended learning design."),
    ("SAMR Model", "TPACK", "complements", 0.85, "SAMR complements TPACK for technology integration."),
    ("Flipped Classroom", "Flipped Learning", "same_as", 0.99, "Same concept."),
    ("Adaptive Learning", "Personalized Learning", "complements", 0.9, "Adaptive learning enables personalized learning."),
    ("Gamification in Education", "Flow Theory", "applies", 0.75, "Gamification applies flow theory principles."),
    ("Constructionism", "Constructivism", "extends", 0.85, "Papert's constructionism extends constructivism."),
    
    # Assessment relationships
    ("Formative Assessment", "Assessment for Learning", "same_as", 0.95, "Nearly identical concepts."),
    ("Formative Assessment", "Summative Assessment", "contrasts_with", 0.6, "Different purposes in assessment."),
    ("Authentic Assessment", "Performance Assessment", "complements", 0.85, "Authentic and performance assessment complement."),
    ("Rubric Assessment", "Authentic Assessment", "supports", 0.8, "Rubrics support authentic assessment."),
    ("Dynamic Assessment", "Zone of Proximal Development", "applies", 0.85, "Dynamic assessment applies ZPD."),
    
    # Social Learning relationships
    ("Cooperative Learning", "Social Interdependence Theory", "derived_from", 0.9, "Cooperative learning derives from social interdependence."),
    ("Cooperative Learning", "Collaborative Learning", "complements", 0.9, "Cooperative and collaborative learning complement."),
    ("Communities of Practice", "Situated Learning Theory", "derived_from", 0.95, "CoP derives from situated learning."),
    ("Legitimate Peripheral Participation", "Communities of Practice", "derived_from", 0.95, "LPP is part of CoP theory."),
    ("Jigsaw Method", "Cooperative Learning", "applies", 0.85, "Jigsaw is a cooperative learning method."),
    ("Peer Instruction", "Social Learning Theory", "applies", 0.8, "Peer instruction applies social learning."),
    ("Reciprocal Teaching", "Scaffolding Theory", "applies", 0.85, "Reciprocal teaching applies scaffolding."),
    ("Dialogic Learning", "Social Constructivism", "derived_from", 0.85, "Dialogic learning derives from social constructivism."),
    ("Knowledge Building Theory", "Social Constructivism", "extends", 0.8, "Knowledge building extends social constructivism."),
    
    # Curriculum relationships
    ("Tyler's Rationale", "Backward Design", "influences", 0.8, "Tyler influenced backward design development."),
    ("Spiral Curriculum", "Cognitive Development Theory", "applies", 0.85, "Spiral curriculum applies developmental principles."),
    ("Competency-Based Education", "Outcome-Based Education", "complements", 0.9, "CBE and OBE share similar foundations."),
    
    # Critical/Alternative Education relationships
    ("Critical Pedagogy", "Pedagogy of the Oppressed", "derived_from", 0.95, "Critical pedagogy derives from Freire's work."),
    ("Culturally Relevant Pedagogy", "Multicultural Education", "complements", 0.85, "CRP complements multicultural education."),
    ("Culturally Sustaining Pedagogy", "Culturally Relevant Pedagogy", "extends", 0.9, "CSP extends CRP."),
    ("Montessori Method", "Montessori Education", "same_as", 0.99, "Same educational approach."),
    ("Waldorf Education", "Holistic Education", "complements", 0.8, "Waldorf education is a form of holistic education."),
    ("Reggio Emilia Approach", "Reggio Emilia Approach", "same_as", 0.99, "Same approach."),
    ("Universal Design for Learning", "Inclusive Education", "supports", 0.9, "UDL supports inclusive education."),
    ("Inclusion Theory", "Inclusive Education", "derived_from", 0.95, "Same theoretical foundation."),
    ("Applied Behavior Analysis", "Operant Conditioning", "applies", 0.9, "ABA applies operant conditioning."),
    ("Democratic Education", "Summerhill Education", "derived_from", 0.85, "Democratic education exemplified by Summerhill."),
    
    # Asian Education relationships
    ("Confucian Educational Philosophy", "Unity of Knowledge and Action", "influences", 0.85, "Confucianism influenced Wang Yangming."),
    ("Lesson Study", "School as Learning Community", "complements", 0.9, "Lesson study and learning community complement."),
    ("Terakoya Education", "Confucian Educational Philosophy", "influenced_by", 0.7, "Terakoya influenced by Confucianism."),
    
    # Modern Education relationships
    ("21st Century Skills", "OECD Learning Compass 2030", "complements", 0.85, "21st century skills align with OECD framework."),
    ("Social and Emotional Learning", "Emotional Intelligence Theory", "applies", 0.85, "SEL applies emotional intelligence."),
    ("STEM Education", "STEAM Education", "influences", 0.95, "STEM evolved into STEAM."),
    ("Project-Based Learning", "Maker Education", "complements", 0.85, "PBL complements maker education."),
    ("Design Thinking in Education", "Maker Education", "complements", 0.8, "Design thinking complements maker education."),
    ("Self-Regulated Learning", "Self-Determination Theory", "complements", 0.8, "SRL complements SDT."),
    ("Microlearning", "Mobile Learning", "complements", 0.75, "Microlearning suits mobile learning."),
]

# Generate relationships
relationships = []
rel_counter = 1

for source_name, target_name, rel_type, strength, description in KNOWN_RELATIONSHIPS:
    source = theory_by_name.get(source_name)
    target = theory_by_name.get(target_name)
    
    if source and target and source["id"] != target["id"]:
        rel = {
            "id": f"rel-{rel_counter:03d}",
            "source_id": source["id"],
            "target_id": target["id"],
            "relationship_type": rel_type,
            "strength": strength,
            "description": description
        }
        relationships.append(rel)
        rel_counter += 1

# Add category-based relationships for theories without explicit relationships
categories = {}
for t in theories_data["theories"]:
    cat = t["category"]
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(t)

# Add some intra-category relationships for completeness
for cat, theories in categories.items():
    # Add relationships between theories by same theorist
    theorist_theories = {}
    for t in theories:
        for theorist in t.get("theorists", []):
            if theorist not in theorist_theories:
                theorist_theories[theorist] = []
            theorist_theories[theorist].append(t)
    
    for theorist, ts in theorist_theories.items():
        if len(ts) > 1:
            for i, t1 in enumerate(ts):
                for t2 in ts[i+1:]:
                    # Check if relationship already exists
                    existing = False
                    for r in relationships:
                        if (r["source_id"] == t1["id"] and r["target_id"] == t2["id"]) or \
                           (r["source_id"] == t2["id"] and r["target_id"] == t1["id"]):
                            existing = True
                            break
                    
                    if not existing:
                        rel = {
                            "id": f"rel-{rel_counter:03d}",
                            "source_id": t1["id"],
                            "target_id": t2["id"],
                            "relationship_type": "complements",
                            "strength": 0.7,
                            "description": f"Both theories developed by {theorist}."
                        }
                        relationships.append(rel)
                        rel_counter += 1

# Create output
output = {
    "metadata": {
        "version": "2.0.0",
        "total_relationships": len(relationships),
        "relationship_types": list(set(r["relationship_type"] for r in relationships)),
        "generated_at": datetime.now().strftime("%Y-%m-%d")
    },
    "relationships": relationships
}

# Save
output_path = Path(__file__).parent.parent / "data" / "theories" / "relationships.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Generated {len(relationships)} relationships")
print(f"Relationship types: {output['metadata']['relationship_types']}")
print(f"Saved to: {output_path}")
