def start(output_file, outputsch_file, teacher_class_lists_file):
    import ast
    from collections import defaultdict

    # Load teacher schedules
    with open(outputsch_file, "r") as f:
        teacher_schedules = ast.literal_eval(f.read().strip())

    # Structure: {teacher_id: {period: [students...]}}
    teacher_students = defaultdict(lambda: defaultdict(list))

    # Load student assignments
    with open(outputsch_file, "r") as f:
        output = f.read()

        
    for line in output:
        parts = line.strip().split(",")
        if len(parts) != 4:
            continue
        student_id, teacher_id, class_name, period = parts
        period = int(period)
        teacher_students[teacher_id][period].append(student_id)

    # Build final result with class names
    final_data = {}
    for teacher_id, schedule in teacher_schedules.items():
        final_data[teacher_id] = []
        for period, class_name in enumerate(schedule):
            students = teacher_students[teacher_id].get(period, [])
            final_data[teacher_id].append({
                "period": period+1,
                "class": class_name,
                "students": students
            })

    # Save to file
    with open(teacher_class_lists_file, "w") as f:
        for teacher_id, periods in final_data.items():
            f.write(f"Teacher {teacher_id}:\n")
            for p in periods:
                f.write(f"  Period {p['period']}: {p['class']} - Students: {', '.join(p['students'])}\n")
            f.write("\n")

