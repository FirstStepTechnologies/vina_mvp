import hashlib

def generate_profile_hash(profession, industry, experience_level):
    profile_string = f"{profession}:{industry}:{experience_level}"
    return hashlib.md5(profile_string.encode()).hexdigest()[:7]

profiles = [
    ("Clinical Researcher", "Pharma/Biotech", "Intermediate"),
    ("HR Manager", "Tech Company", "Intermediate"),
    ("Marketing Manager", "E-Commerce", "Intermediate"),
    ("Project Manager", "Software/Tech", "Intermediate"),
    ("Clinical Researcher", "Pharma/Biotech", "Beginner"),
    ("HR Manager", "Tech Company", "Beginner"),
    ("Marketing Manager", "E-Commerce", "Beginner"),
    ("Project Manager", "Software/Tech", "Beginner"),
]

print(f"{'Profession':<25} | {'Industry':<20} | {'Exp Level':<15} | {'Hash'}")
print("-" * 80)
for p, i, e in profiles:
    h = generate_profile_hash(p, i, e)
    print(f"{p:<25} | {i:<20} | {e:<15} | {h}")
