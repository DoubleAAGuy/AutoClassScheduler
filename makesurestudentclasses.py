import csv
from collections import defaultdict

# Load student schedules
student_periods = defaultdict(lambda: defaultdict(str))
max_period = 0

with open("output.txt", "r") as f:
    for line in f:
        parts = line.strip().split(",")
        if len(parts) != 4:
            continue
        student_id, teacher_id, class_name, period = parts
        period = int(period)
        student_periods[student_id][period] = f"{class_name} (Teacher {teacher_id})"
        if period > max_period:
            max_period = period

# Check schedules
issues = []
for student_id, periods in student_periods.items():
    for p in range(max_period + 1):
        if p not in periods:
            issues.append(f"Student {student_id} is missing a class in Period {p}")
    # Check for duplicates (shouldn't happen if data is clean)
    if len(periods) != len(set(periods.keys())):
        issues.append(f"Student {student_id} has a period conflict!")

# Output results
if issues:
    print("Schedule Issues Found:")
    for issue in issues:
        print(" -", issue)
else:
    print("✅ All students have exactly one class each period.")