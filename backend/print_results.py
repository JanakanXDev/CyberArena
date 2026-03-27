"""Print the test results file completely."""
lines = open('backend/test_final_v2.txt', encoding='ascii', errors='replace').readlines()
for i, line in enumerate(lines):
    print(f"{i+1:03d}: {line.rstrip()}")
