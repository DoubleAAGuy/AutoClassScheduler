def start(loops):
    import itertools
    import mainfile
    # Read teachers and students
    with open('teachers.txt', 'r') as f:
        lines = f.readlines()
    number_of_teachers = len(lines)
    with open('students.txt', 'r') as f:
        liness = f.readlines()
    number_of_students = len(liness)
    def sort_by_first_number(tuples_list):
        return sorted(tuples_list, key=lambda x: int(x[1]))
    # Parse teachers: (teacher_id, [(class_name, limit), ...])
    teachers = []
    for line in lines:
        parts = line.strip().split(',')
        teacher_id = parts[0]
        class_list = []
        i = 1
        while i < len(parts):
            class_name = parts[i].replace('(', '').replace(')', '')
            limit = None
            if i+1 < len(parts):
                try:
                    limit = int(parts[i+1].replace(')', '').replace('(', ''))
                except Exception:
                    limit = None
            class_list.append((class_name, limit))
            i += 2
        teachers.append((teacher_id, class_list))

    def generate_all_possible_schedules(teachers,num_trials):
        # For each teacher, generate all possible schedules
        teacher_ids = []
        teacher_schedules = []
        for teacher_id, class_limit_list in teachers:
            teacher_ids.append(teacher_id)
            class_names = [c[0] for c in class_limit_list]
            class_combinations = itertools.product(class_names, repeat=6)
            possible_schedules = set()
            for combo in class_combinations:
                for i in range(7):
                    schedule = list(combo)
                    schedule.insert(i, 'Planning')
                    possible_schedules.add(tuple(schedule))
            teacher_schedules.append(list(possible_schedules))

        # Randomly sample combinations
        import random
        all_combinations = []
        for idx in range(num_trials):
            schedules_combo = [random.choice(schedules) for schedules in teacher_schedules]
            combo_dict = {teacher_id: list(schedule) for teacher_id, schedule in zip(teacher_ids, schedules_combo)}
            print(f"Processing random combination {idx+1}")
            all_combinations.append(combo_dict)
        return all_combinations
    # Now all_schedules is a list of dicts, each dict is a possible assignment of schedules to teachers
    all_schedules = generate_all_possible_schedules(teachers, loops)
    best_per = -1
    best_out = []
    best_sch = None
    for i, schedule in enumerate(all_schedules):
        print(f"Processing schedule {i+1}/{len(all_schedules)}")
        output = mainfile.try_once(schedule)
        # print(sort_by_first_number(output))
        if len(output)/(number_of_students*7) > best_per:
            best_out = output
            best_per = len(output) / (number_of_students * 7)
            best_sch = schedule
    print("done")
    print(f"Best schedule found with {best_per:.2%} of students' requirements met.")
    # Write best_out to output.txt, one entry per line, comma-separated
    with open('output.txt', 'w') as f:
        for entry in best_out:
            f.write(','.join(str(x) for x in entry) + '\n')
    with open('outputsch.txt', 'w') as f:
        f.write(str(best_sch))
    import processing
    return f'{best_per:.2%} Classes Covered'