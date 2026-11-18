import docx

doc = docx.Document("data/AI_Business_Intelligence_Project.docx")
print(f"Number of paragraphs: {len(doc.paragraphs)}")
for i, p in enumerate(doc.paragraphs[:30]):
    if p.text.strip():
        print(f"P{i}: {p.text}")

print("\nTables in docx:", len(doc.tables))
for t in doc.tables:
    for row in t.rows[:5]:
        print([c.text.strip() for c in row.cells])
    print("---")
