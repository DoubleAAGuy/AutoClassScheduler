import random
import processing
# Class to manage student limits per class per period
class StudentLimit:
    def __init__(self, class_limits):
        # class_limits: dict of (teacher_id, period) -> max_students
        self.class_limits = class_limits
        self.class_counts = {}  # (teacher_id, period): count

    def can_assign(self, teacher_id, period):
        key = (teacher_id, period)
        limit = self.class_limits.get(key, None)
        if limit is None:
            return True  # No limit set
        return self.class_counts.get(key, 0) < limit

    def assign(self, teacher_id, period):
        key = (teacher_id, period)
        self.class_counts[key] = self.class_counts.get(key, 0) + 1

    def get_count(self, teacher_id, period):
        return self.class_counts.get((teacher_id, period), 0)
def try_once(num1, teachers_file, students_file, output_file, outputsch_file, teacher_class_lists_file):
    teachers = []
    unique_classes = set()
    class_limits = {}
    with open(teachers_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        parts = line.strip().split(',')
        teacher_id = parts[0]
        classes = parts[1:]
        # Assume format: teacher_id, class1, limit1, class2, limit2, ...
        class_list = []
        for i in range(0, len(classes), 2):
            class_name = classes[i].replace('(', '').replace(')', '')
            class_list.append(class_name)
            if i+1 < len(classes):
                try:
                    limit = int(classes[i+1].replace(')', '').replace('(', ''))
                except Exception:
                    limit = None
                # For each period, set the limit for this teacher/class
                for period in range(7):
                    class_limits[(teacher_id, period)] = limit
        teachers.append((teacher_id, class_list))
        unique_classes.update(class_list)

    student_limit = StudentLimit(class_limits)

    #print("Teachers and their classes:")
    # Read students
    with open(students_file, 'r') as f:
        student_lines = f.readlines()
    students = []
    for line in student_lines:
        parts = line.strip().split(',')
        student_id = parts[0]
        classesreq = parts[1:]
        students.append((student_id, classesreq))

    def sort_by_first_number(data):
        return sorted(data, key=lambda x: int(x[0]))
    def sort_by_first_then_last(data):
        import re
        def extract_int(s):
            s = str(s)
            match = re.search(r'\d+', s)
            return int(match.group()) if match else 0
        return sorted(data, key=lambda x: (extract_int(x[0]), extract_int(x[-1])))

    # Now go through the students and assign them to classes
    # Check what classes they can take for each period
    classes_a_Stu_can_take = []
    teacher_ids = list(num1.keys())
    number_of_teachers = len(teacher_ids)
    for student_id, classesreq in students:
        for class_per in range(7):
            for teacher_id in teacher_ids:
                class_for_period = num1[teacher_id][class_per]
                if class_for_period in classesreq:
                    # Only add if not over the limit
                    if student_limit.can_assign(teacher_id, class_per):
                        classes_a_Stu_can_take.append((student_id, teacher_id, class_for_period, class_per))

    # Split by period
    periods = [[] for _ in range(7)]
    for entry in classes_a_Stu_can_take:
        periods[entry[3]].append(entry)
    # Sort each period by student id
    for i in range(7):
        periods[i] = sorted(periods[i], key=lambda x: x[0])

    output = []

    # Assign students who have only one option for a period
    # def assign_students_to_classes(period):
    #     # Build a map student_id -> list of options
    #     from collections import defaultdict
    #     student_map = defaultdict(list)
    #     for entry in period:
    #         student_map[entry[0]].append(entry)
    #     for student_id, options in student_map.items():
    #         if len(options) == 1:
    #             if options[0] not in output:
    #                 # Check limit before assigning
    #                 _, teacher_id, _, class_per = options[0]
    #                 if student_limit.can_assign(teacher_id, class_per):
    #                     output.append(options[0])
    #                     student_limit.assign(teacher_id, class_per)
    # for period in periods:
    #     assign_students_to_classes(period)

    # # Assign a class to a student if they can only get that class in one period across all periods
    # def give_only_one_thats_avialbie_all_periods(periods):
    #     from collections import defaultdict
    #     # For each student, class, count in how many periods it appears
    #     student_class_periods = defaultdict(list)
    #     for pidx, period in enumerate(periods):
    #         for entry in period:
    #             student_class_periods[(entry[0], entry[2])].append(pidx)
    #     for (student_id, class_name), period_idxs in student_class_periods.items():
    #         if len(period_idxs) == 1:
    #             # Only available in one period
    #             period = periods[period_idxs[0]]
    #             for entry in period:
    #                 if entry[0] == student_id and entry[2] == class_name and entry not in output:
    #                     _, teacher_id, _, class_per = entry
    #                     if student_limit.can_assign(teacher_id, class_per):
    #                         output.append(entry)
    #                         student_limit.assign(teacher_id, class_per)
    # give_only_one_thats_avialbie_all_periods(periods)

    # Randomly assign remaining classes (greedy)
    def randomly_assign_remaining_classes(periods):
        # Track (student_id, period) already assigned
        assigned = set((o[0], o[3]) for o in output)
        # Track subjects each student already has
        student_subjects = {}
        for o in output:
            student_id = o[0]
            subject = o[2]
            student_subjects.setdefault(student_id, set()).add(subject)
        for pidx, period in enumerate(periods):
            period_shuffled = period[:]
            random.shuffle(period_shuffled)
            for entry in period_shuffled:
                student_id, teacher_id, subject, class_per = entry

                # Skip if same period already assigned or already assigned this subject
                if (student_id, pidx) in assigned:
                    continue
                if student_id in student_subjects and subject in student_subjects[student_id]:
                    continue
                if entry in output:
                    continue

                # Check teacher capacity
                if student_limit.can_assign(teacher_id, class_per):
                    output.append(entry)
                    assigned.add((student_id, pidx))
                    student_subjects.setdefault(student_id, set()).add(subject)
                    student_limit.assign(teacher_id, class_per)


    randomly_assign_remaining_classes(periods)
    processing.start(output_file, outputsch_file, teacher_class_lists_file)
    return sort_by_first_then_last(output)