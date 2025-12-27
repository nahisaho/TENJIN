#!/usr/bin/env python3
"""Generate complete theorists.json from theories.json."""

import json
import re
from pathlib import Path
from datetime import datetime

# Read theories
theories_path = Path(__file__).parent.parent / "data" / "theories" / "theories.json"
with open(theories_path, "r", encoding="utf-8") as f:
    theories_data = json.load(f)

# Read existing theorists for reference
existing_path = Path(__file__).parent.parent / "data" / "theories" / "theorists.json"
with open(existing_path, "r", encoding="utf-8") as f:
    existing = json.load(f)

# Create mapping of existing theorists
existing_map = {t["name"]: t for t in existing["theorists"]}

# Extract all unique theorists from theories
theorist_theories = {}  # name -> list of theory_ids

for theory in theories_data["theories"]:
    for theorist_name in theory.get("theorists", []):
        if theorist_name and theorist_name.strip():
            clean_name = theorist_name.strip()
            if clean_name not in theorist_theories:
                theorist_theories[clean_name] = []
            theorist_theories[clean_name].append(theory["id"])

# Known theorist data (from Educational-theory-research.md)
KNOWN_THEORISTS = {
    "B.F. Skinner": {"name_ja": "B.F.スキナー", "birth": 1904, "death": 1990, "nationality": "American", "field": "Behavioral Psychology"},
    "Albert Bandura": {"name_ja": "アルバート・バンデューラ", "birth": 1925, "death": 2021, "nationality": "Canadian-American", "field": "Social Psychology"},
    "John Sweller": {"name_ja": "ジョン・スウェラー", "birth": 1946, "nationality": "Australian", "field": "Educational Psychology"},
    "David A. Kolb": {"name_ja": "デイヴィッド・コルブ", "birth": 1939, "nationality": "American", "field": "Organizational Behavior"},
    "Jean Piaget": {"name_ja": "ジャン・ピアジェ", "birth": 1896, "death": 1980, "nationality": "Swiss", "field": "Developmental Psychology"},
    "John Dewey": {"name_ja": "ジョン・デューイ", "birth": 1859, "death": 1952, "nationality": "American", "field": "Philosophy of Education"},
    "Lev Vygotsky": {"name_ja": "レフ・ヴィゴツキー", "birth": 1896, "death": 1934, "nationality": "Russian", "field": "Developmental Psychology"},
    "Edward L. Deci": {"name_ja": "エドワード・デシ", "birth": 1942, "nationality": "American", "field": "Psychology"},
    "Richard M. Ryan": {"name_ja": "リチャード・ライアン", "birth": 1953, "nationality": "American", "field": "Psychology"},
    "Jerome Bruner": {"name_ja": "ジェローム・ブルーナー", "birth": 1915, "death": 2016, "nationality": "American", "field": "Cognitive Psychology"},
    "Erik Erikson": {"name_ja": "エリク・エリクソン", "birth": 1902, "death": 1994, "nationality": "German-American", "field": "Developmental Psychology"},
    "John Bowlby": {"name_ja": "ジョン・ボウルビィ", "birth": 1907, "death": 1990, "nationality": "British", "field": "Psychiatry"},
    "Socrates": {"name_ja": "ソクラテス", "birth": -470, "death": -399, "nationality": "Greek", "field": "Philosophy"},
    "Maria Montessori": {"name_ja": "マリア・モンテッソーリ", "birth": 1870, "death": 1952, "nationality": "Italian", "field": "Education"},
    "William Kilpatrick": {"name_ja": "ウィリアム・キルパトリック", "birth": 1871, "death": 1965, "nationality": "American", "field": "Education"},
    "Howard Barrows": {"name_ja": "ハワード・バロウズ", "birth": 1928, "death": 2011, "nationality": "American", "field": "Medical Education"},
    "Jonathan Bergmann": {"name_ja": "ジョナサン・バーグマン", "nationality": "American", "field": "Education"},
    "Aaron Sams": {"name_ja": "アーロン・サムズ", "nationality": "American", "field": "Education"},
    "Robert M. Gagné": {"name_ja": "ロバート・ガニェ", "birth": 1916, "death": 2002, "nationality": "American", "field": "Educational Psychology"},
    "Benjamin Bloom": {"name_ja": "ベンジャミン・ブルーム", "birth": 1913, "death": 1999, "nationality": "American", "field": "Educational Psychology"},
    "George Siemens": {"name_ja": "ジョージ・シーメンス", "nationality": "Canadian", "field": "Learning Technology"},
    "Stephen Downes": {"name_ja": "スティーブン・ダウンズ", "nationality": "Canadian", "field": "Learning Technology"},
    "Punya Mishra": {"name_ja": "プニャ・ミシュラ", "nationality": "Indian-American", "field": "Educational Technology"},
    "Matthew Koehler": {"name_ja": "マシュー・ケーラー", "nationality": "American", "field": "Educational Technology"},
    "Richard E. Mayer": {"name_ja": "リチャード・メイヤー", "birth": 1947, "nationality": "American", "field": "Educational Psychology"},
    "Carol S. Dweck": {"name_ja": "キャロル・ドゥエック", "birth": 1946, "nationality": "American", "field": "Psychology"},
    "Carol Dweck": {"name_ja": "キャロル・ドゥエック", "birth": 1946, "nationality": "American", "field": "Psychology"},
    "佐藤学": {"name_ja": "佐藤学", "birth": 1951, "nationality": "Japanese", "field": "Education"},
    "孔子": {"name_ja": "孔子", "birth": -551, "death": -479, "nationality": "Chinese", "field": "Philosophy"},
    "Paulo Freire": {"name_ja": "パウロ・フレイレ", "birth": 1921, "death": 1997, "nationality": "Brazilian", "field": "Critical Pedagogy"},
    "Ralph Tyler": {"name_ja": "ラルフ・タイラー", "birth": 1902, "death": 1994, "nationality": "American", "field": "Curriculum"},
    "Grant Wiggins": {"name_ja": "グラント・ウィギンズ", "birth": 1950, "death": 2015, "nationality": "American", "field": "Education"},
    "Jay McTighe": {"name_ja": "ジェイ・マクタイ", "nationality": "American", "field": "Education"},
    "Paul Black": {"name_ja": "ポール・ブラック", "nationality": "British", "field": "Education"},
    "Dylan Wiliam": {"name_ja": "ディラン・ウィリアム", "birth": 1954, "nationality": "British", "field": "Educational Assessment"},
    "David Johnson": {"name_ja": "デイヴィッド・ジョンソン", "birth": 1940, "nationality": "American", "field": "Cooperative Learning"},
    "Roger Johnson": {"name_ja": "ロジャー・ジョンソン", "nationality": "American", "field": "Cooperative Learning"},
    "Jean Lave": {"name_ja": "ジーン・レイヴ", "birth": 1939, "nationality": "American", "field": "Social Anthropology"},
    "Etienne Wenger": {"name_ja": "エティエンヌ・ウェンガー", "birth": 1952, "nationality": "Swiss", "field": "Learning Theory"},
    "Ivan Pavlov": {"name_ja": "イワン・パブロフ", "birth": 1849, "death": 1936, "nationality": "Russian", "field": "Physiology"},
    "David Ausubel": {"name_ja": "デイヴィッド・オーズベル", "birth": 1918, "death": 2008, "nationality": "American", "field": "Educational Psychology"},
    "Howard Gardner": {"name_ja": "ハワード・ガードナー", "birth": 1943, "nationality": "American", "field": "Developmental Psychology"},
    "George A. Miller": {"name_ja": "ジョージ・ミラー", "birth": 1920, "death": 2012, "nationality": "American", "field": "Cognitive Psychology"},
    "Carl Rogers": {"name_ja": "カール・ロジャーズ", "birth": 1902, "death": 1987, "nationality": "American", "field": "Psychology"},
    "Abraham Maslow": {"name_ja": "アブラハム・マズロー", "birth": 1908, "death": 1970, "nationality": "American", "field": "Psychology"},
    "Malcolm Knowles": {"name_ja": "マルコム・ノールズ", "birth": 1913, "death": 1997, "nationality": "American", "field": "Adult Education"},
    "Allan Collins": {"name_ja": "アラン・コリンズ", "nationality": "American", "field": "Learning Sciences"},
    "Lawrence Kohlberg": {"name_ja": "ローレンス・コールバーグ", "birth": 1927, "death": 1987, "nationality": "American", "field": "Moral Psychology"},
    "Urie Bronfenbrenner": {"name_ja": "ユーリ・ブロンフェンブレンナー", "birth": 1917, "death": 2005, "nationality": "American", "field": "Developmental Psychology"},
    "David Premack": {"name_ja": "デイヴィッド・プリマック", "birth": 1925, "death": 2015, "nationality": "American", "field": "Cognitive Psychology"},
    "Daniel Goleman": {"name_ja": "ダニエル・ゴールマン", "birth": 1946, "nationality": "American", "field": "Psychology"},
    "Rudolf Steiner": {"name_ja": "ルドルフ・シュタイナー", "birth": 1861, "death": 1925, "nationality": "Austrian", "field": "Education"},
    "Loris Malaguzzi": {"name_ja": "ロリス・マラグッツィ", "birth": 1920, "death": 1994, "nationality": "Italian", "field": "Early Childhood Education"},
    "Siegfried Engelmann": {"name_ja": "ジークフリード・エンゲルマン", "birth": 1931, "death": 2019, "nationality": "American", "field": "Instructional Design"},
    "M. David Merrill": {"name_ja": "M.デイヴィッド・メリル", "birth": 1937, "nationality": "American", "field": "Instructional Design"},
    "John M. Keller": {"name_ja": "ジョン・ケラー", "nationality": "American", "field": "Instructional Design"},
    "Walter Dick": {"name_ja": "ウォルター・ディック", "nationality": "American", "field": "Instructional Design"},
    "Lou Carey": {"name_ja": "ルー・キャリー", "nationality": "American", "field": "Instructional Design"},
    "Joseph Schwab": {"name_ja": "ジョセフ・シュワブ", "birth": 1909, "death": 1988, "nationality": "American", "field": "Curriculum"},
    "Philip Jackson": {"name_ja": "フィリップ・ジャクソン", "birth": 1928, "death": 2015, "nationality": "American", "field": "Education"},
    "James Beane": {"name_ja": "ジェームズ・ビーン", "nationality": "American", "field": "Curriculum"},
    "Susan Drake": {"name_ja": "スーザン・ドレイク", "nationality": "Canadian", "field": "Curriculum"},
    "William Spady": {"name_ja": "ウィリアム・スペイディ", "nationality": "American", "field": "Curriculum"},
    "Jacquelynne S. Eccles": {"name_ja": "ジャクリーン・エクルズ", "birth": 1944, "nationality": "American", "field": "Psychology"},
    "Bernard Weiner": {"name_ja": "バーナード・ウェイナー", "birth": 1935, "nationality": "American", "field": "Psychology"},
    "Mihaly Csikszentmihalyi": {"name_ja": "ミハイ・チクセントミハイ", "birth": 1934, "death": 2021, "nationality": "Hungarian-American", "field": "Psychology"},
    "Suzanne Hidi": {"name_ja": "スザンヌ・ヒディ", "nationality": "Canadian", "field": "Educational Psychology"},
    "K. Ann Renninger": {"name_ja": "K.アン・レニンガー", "nationality": "American", "field": "Educational Psychology"},
    "Reinhard Pekrun": {"name_ja": "ラインハルト・ペクルン", "nationality": "German", "field": "Educational Psychology"},
    "Martin Seligman": {"name_ja": "マーティン・セリグマン", "birth": 1942, "nationality": "American", "field": "Psychology"},
    "Edwin A. Locke": {"name_ja": "エドウィン・ロック", "birth": 1938, "nationality": "American", "field": "Industrial Psychology"},
    "Gary P. Latham": {"name_ja": "ゲイリー・レイサム", "birth": 1945, "nationality": "Canadian", "field": "Organizational Psychology"},
    "Angela Duckworth": {"name_ja": "アンジェラ・ダックワース", "birth": 1970, "nationality": "American", "field": "Psychology"},
    "Helen C. Barrett": {"name_ja": "ヘレン・バレット", "nationality": "American", "field": "Educational Technology"},
    "Reuven Feuerstein": {"name_ja": "ルーベン・フォイエルシュタイン", "birth": 1921, "death": 2014, "nationality": "Israeli", "field": "Cognitive Psychology"},
    "Morton Deutsch": {"name_ja": "モートン・ドイッチ", "birth": 1920, "death": 2017, "nationality": "American", "field": "Social Psychology"},
    "Elliot Aronson": {"name_ja": "エリオット・アロンソン", "birth": 1932, "nationality": "American", "field": "Social Psychology"},
    "Eric Mazur": {"name_ja": "エリック・マザー", "birth": 1954, "nationality": "Dutch-American", "field": "Physics Education"},
    "Annemarie Palincsar": {"name_ja": "アニー・パリンサー", "nationality": "American", "field": "Educational Psychology"},
    "Ann Brown": {"name_ja": "アン・ブラウン", "birth": 1943, "death": 1999, "nationality": "British-American", "field": "Educational Psychology"},
    "Mikhail Bakhtin": {"name_ja": "ミハイル・バフチン", "birth": 1895, "death": 1975, "nationality": "Russian", "field": "Philosophy"},
    "Marlene Scardamalia": {"name_ja": "マーリーン・スカーダマリア", "nationality": "Canadian", "field": "Learning Sciences"},
    "Carl Bereiter": {"name_ja": "カール・ベライター", "birth": 1930, "nationality": "American-Canadian", "field": "Educational Psychology"},
    "王陽明": {"name_ja": "王陽明", "birth": 1472, "death": 1529, "nationality": "Chinese", "field": "Philosophy"},
    "福沢諭吉": {"name_ja": "福沢諭吉", "birth": 1835, "death": 1901, "nationality": "Japanese", "field": "Education"},
    "陶行知": {"name_ja": "陶行知", "birth": 1891, "death": 1946, "nationality": "Chinese", "field": "Education"},
    "ラビンドラナート・タゴール": {"name_ja": "ラビンドラナート・タゴール", "birth": 1861, "death": 1941, "nationality": "Indian", "field": "Literature/Education"},
    "マハトマ・ガンディー": {"name_ja": "マハトマ・ガンディー", "birth": 1869, "death": 1948, "nationality": "Indian", "field": "Philosophy"},
    "J. クリシュナムルティ": {"name_ja": "J.クリシュナムルティ", "birth": 1895, "death": 1986, "nationality": "Indian", "field": "Philosophy"},
    "シュリ・オーロビンド": {"name_ja": "シュリ・オーロビンド", "birth": 1872, "death": 1950, "nationality": "Indian", "field": "Philosophy"},
    "Ruben R. Puentedura": {"name_ja": "ルーベン・プエンテドゥラ", "nationality": "American", "field": "Educational Technology"},
    "Michael B. Horn": {"name_ja": "マイケル・ホーン", "nationality": "American", "field": "Educational Innovation"},
    "John Traxler": {"name_ja": "ジョン・トラクスラー", "nationality": "British", "field": "Mobile Learning"},
    "Rose Luckin": {"name_ja": "ローズ・ラッキン", "nationality": "British", "field": "AI in Education"},
    "Karl Kapp": {"name_ja": "カール・カップ", "nationality": "American", "field": "Gamification"},
    "Chris Dede": {"name_ja": "クリス・デーデ", "nationality": "American", "field": "Educational Technology"},
    "Seymour Papert": {"name_ja": "シーモア・パパート", "birth": 1928, "death": 2016, "nationality": "South African-American", "field": "Learning Theory"},
    "Randy Garrison": {"name_ja": "ランディ・ギャリソン", "nationality": "Canadian", "field": "Online Learning"},
    "Michael Fullan": {"name_ja": "マイケル・フラン", "birth": 1940, "nationality": "Canadian", "field": "Educational Change"},
    "Robert Marzano": {"name_ja": "ロバート・マルザーノ", "birth": 1946, "nationality": "American", "field": "Educational Research"},
    "Sylvia Martinez": {"name_ja": "シルビア・マルティネス", "nationality": "American", "field": "Maker Education"},
    "Theo Hug": {"name_ja": "テオ・フグ", "nationality": "Austrian", "field": "Educational Sciences"},
    "Barry Zimmerman": {"name_ja": "バリー・ジマーマン", "birth": 1942, "death": 2019, "nationality": "American", "field": "Educational Psychology"},
    "Gloria Ladson-Billings": {"name_ja": "グロリア・ラドソン・ビリングス", "birth": 1947, "nationality": "American", "field": "Critical Pedagogy"},
    "James A. Banks": {"name_ja": "ジェームズ・バンクス", "birth": 1941, "nationality": "American", "field": "Multicultural Education"},
    "Johann Heinrich Pestalozzi": {"name_ja": "ヨハン・ペスタロッチ", "birth": 1746, "death": 1827, "nationality": "Swiss", "field": "Education"},
    "Friedrich Froebel": {"name_ja": "フリードリヒ・フレーベル", "birth": 1782, "death": 1852, "nationality": "German", "field": "Early Childhood Education"},
    "Mel Ainscow": {"name_ja": "メル・エインスコウ", "nationality": "British", "field": "Inclusive Education"},
    "O. Ivar Lovaas": {"name_ja": "O.イヴァー・ロヴァース", "birth": 1927, "death": 2010, "nationality": "Norwegian-American", "field": "Psychology"},
    "Eric Schopler": {"name_ja": "エリック・ショプラー", "birth": 1927, "death": 2006, "nationality": "American", "field": "Psychology"},
    "David Rose": {"name_ja": "デイヴィッド・ローズ", "nationality": "American", "field": "Special Education"},
    "Anne Meyer": {"name_ja": "アン・メイヤー", "nationality": "American", "field": "Special Education"},
    "bell hooks": {"name_ja": "ベル・フックス", "birth": 1952, "death": 2021, "nationality": "American", "field": "Critical Pedagogy"},
    "George Dei": {"name_ja": "ジョージ・デイ", "nationality": "Ghanaian-Canadian", "field": "Anti-Racist Education"},
    "Django Paris": {"name_ja": "ジャンゴ・パリス", "nationality": "American", "field": "Culturally Sustaining Pedagogy"},
    "Linda Tuhiwai Smith": {"name_ja": "リンダ・スミス", "nationality": "New Zealand Māori", "field": "Indigenous Research"},
    "Mogobe Ramose": {"name_ja": "モゴベ・ラモセ", "nationality": "South African", "field": "Ubuntu Philosophy"},
    "Gregory Cajete": {"name_ja": "グレゴリー・カヘテ", "nationality": "Native American", "field": "Indigenous Education"},
    "Jim Cummins": {"name_ja": "ジム・カミンズ", "birth": 1949, "nationality": "Irish-Canadian", "field": "Bilingual Education"},
    "Johann Friedrich Herbart": {"name_ja": "ヨハン・フリードリヒ・ヘルバルト", "birth": 1776, "death": 1841, "nationality": "German", "field": "Philosophy/Psychology"},
    "A.S. Neill": {"name_ja": "A.S.ニール", "birth": 1883, "death": 1973, "nationality": "Scottish", "field": "Education"},
    "Peter Petersen": {"name_ja": "ペーター・ペーターゼン", "birth": 1884, "death": 1952, "nationality": "German", "field": "Education"},
    "Ron Miller": {"name_ja": "ロン・ミラー", "nationality": "American", "field": "Holistic Education"},
    "Daniel Greenberg": {"name_ja": "ダニエル・グリーンバーグ", "birth": 1934, "nationality": "American", "field": "Democratic Education"},
    "Ella Flatau": {"name_ja": "エラ・フラタウ", "nationality": "Danish", "field": "Outdoor Education"},
    "A. Jean Ayres": {"name_ja": "A.ジーン・エアーズ", "birth": 1920, "death": 1988, "nationality": "American", "field": "Occupational Therapy"},
    "孟子": {"name_ja": "孟子", "birth": -372, "death": -289, "nationality": "Chinese", "field": "Philosophy"},
    "荀子": {"name_ja": "荀子", "birth": -313, "death": -238, "nationality": "Chinese", "field": "Philosophy"},
    "朱熹": {"name_ja": "朱熹", "birth": 1130, "death": 1200, "nationality": "Chinese", "field": "Philosophy"},
    "蔡元培": {"name_ja": "蔡元培", "birth": 1868, "death": 1940, "nationality": "Chinese", "field": "Education"},
    "森有礼": {"name_ja": "森有礼", "birth": 1847, "death": 1889, "nationality": "Japanese", "field": "Education"},
    "牧口常三郎": {"name_ja": "牧口常三郎", "birth": 1871, "death": 1944, "nationality": "Japanese", "field": "Education"},
    "斎藤喜博": {"name_ja": "斎藤喜博", "birth": 1911, "death": 1981, "nationality": "Japanese", "field": "Education"},
    "大村はま": {"name_ja": "大村はま", "birth": 1906, "death": 2005, "nationality": "Japanese", "field": "Education"},
    "スワミ・ヴィヴェーカーナンダ": {"name_ja": "スワミ・ヴィヴェーカーナンダ", "birth": 1863, "death": 1902, "nationality": "Indian", "field": "Philosophy"},
}

# Generate theorist entries
theorists = []
theorist_counter = 1

for name, theory_ids in sorted(theorist_theories.items()):
    # Check if we have known data
    known = KNOWN_THEORISTS.get(name, {})
    
    if name in existing_map:
        entry = existing_map[name].copy()
        entry["id"] = f"theorist-{theorist_counter:03d}"
        entry["related_theories"] = theory_ids
    else:
        entry = {
            "id": f"theorist-{theorist_counter:03d}",
            "name": name,
            "name_ja": known.get("name_ja", name),
            "birth_year": known.get("birth"),
            "death_year": known.get("death"),
            "nationality": known.get("nationality", "Unknown"),
            "primary_field": known.get("field", "Education"),
            "contributions": [],
            "key_works": [],
            "related_theories": theory_ids
        }
    
    theorists.append(entry)
    theorist_counter += 1

# Create output
output = {
    "metadata": {
        "version": "2.0.0",
        "total_theorists": len(theorists),
        "source": "Educational-theory-research.md",
        "generated_at": datetime.now().strftime("%Y-%m-%d")
    },
    "theorists": theorists
}

# Save
output_path = Path(__file__).parent.parent / "data" / "theories" / "theorists.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Generated {len(theorists)} theorists")
print(f"Saved to: {output_path}")
