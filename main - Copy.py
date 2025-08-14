

with open('teachers.txt', 'r') as f:
    lines = f.readlines()

teachers = []
unique_classes = set()

for line in lines:
    parts = line.strip().split(',')
    teacher_id = parts[0]
    classes = parts[1:]
    teachers.append((teacher_id, classes))
    unique_classes.update(classes)

print("Teachers and their classes:")
for tid, classes in teachers:
    print(f"Teacher {tid}: {classes}")

print("\nUnique classes:")
print(sorted(unique_classes))

#decode students.txt
with open('students.txt', 'r') as f:
    lines = f.readlines()
student_num = 0
students = []
for line in lines:
    parts = line.strip().split(',')
    student_id = parts[0]
    classesreq = parts[1:]
    students.append((student_id, classesreq))
    student_num += 1
def sort_by_first_number(data):
    return sorted(data, key=lambda x: int(x[0]))
def sort_by_first_then_last(data):
    return sorted(data, key=lambda x: (int(x[0]), int(x[-1])))
print("\nStudents and their required classes:")
# for sid, classes in students:
#     # print(f"Student {sid}: {classes}")

#randomly set teachers teaching scheduals make sure they have 1 planning period
import random


def generate_schedule(teachers, unique_classes):
    schedule = {}
    for teacher_id, classes in teachers:
        # Pick 6 classes randomly **with repetition** from teacher's classes
        assigned_classes = [random.choice(classes) for _ in range(6)]
        
        # Insert 'Planning' randomly in the schedule (anywhere in 8 slots)
        planning_index = random.randint(0, 6)
        assigned_classes.insert(planning_index, 'Planning')
        
        schedule[teacher_id] = assigned_classes
    return schedule

num1 = generate_schedule(teachers, unique_classes)
# print(len(num1))  # Print first 5 teacher schedules for brevity

number_of_teachers = len(num1)
#now go through the students and assign them to classes
#check what classes they can take for each period
classes_a_Stu_can_take = []
def check_avi(students, schedule):
    for student_id, classesreq in students:
        #one student
        for class_per in range(7):
            for i in range(number_of_teachers):
                teacher_id = list(schedule.keys())[i]
                class_for_period = schedule[teacher_id][class_per]
                if class_for_period in classesreq:
                    classes_a_Stu_can_take.append((student_id, teacher_id, class_for_period, class_per))
                    # print(f"Student {student_id} can take {class_for_period} with Teacher {teacher_id} in period {class_per + 1}.")

avi= check_avi(students, num1)
# print(avi)
# print(classes_a_Stu_can_take)
per1 = []
per2 = []
per3 = []
per4 = []
per5 = []
per6 = []
per7 = []
output = []
# print(classes_a_Stu_can_take)
#start assigning students to classes

#if a student has only one class for a period, assign them to that class
def sort_into_per(classes_a_Stu_can_take):
    for i in classes_a_Stu_can_take:
        if i[3] == 0:
            per1.append(i)
        elif i[3] == 1:
            per2.append(i)
        elif i[3] == 2:
            per3.append(i)
        elif i[3] == 3:
            per4.append(i)
        elif i[3] == 4:
            per5.append(i)
        elif i[3] == 5:
            per6.append(i)
        elif i[3] == 6:
            per7.append(i)
#sort the periods by student id
sort_into_per(classes_a_Stu_can_take)
def sort_periods_by_student_id(period_list):
    return sorted(period_list, key=lambda x: x[0])
per1 = sort_periods_by_student_id(per1)
per2 = sort_periods_by_student_id(per2)
per3 = sort_periods_by_student_id(per3)
per4 = sort_periods_by_student_id(per4)
per5 = sort_periods_by_student_id(per5)
per6 = sort_periods_by_student_id(per6)
per7 = sort_periods_by_student_id(per7)







# print(per1)
#find if A STUDENT ONLY HAS ONE OTION FOR THAT PERIOD
def assign_students_to_classes(period):
    for i in range(len(period)):
        try:
            if period[i-1][0] == period[i][0] or period[i+1][0] == period[i][0]:
                pass
            else:
                output.append(period[i])
                period.remove(period[i])
        except IndexError:
            pass

assign_students_to_classes(per1)
assign_students_to_classes(per2)
assign_students_to_classes(per3)
assign_students_to_classes(per4)
assign_students_to_classes(per5)
assign_students_to_classes(per6)
assign_students_to_classes(per7)

print(output)
print()
print()
print()
print()
print()

# Assign a class to a student if they can only get that class in one period across all periods
def give_only_one_thats_avialbie_all_periods(per1, per2, per3, per4, per5, per6, per7):
    #if the student only cna get pe1 in 3rd period for example and no other periods give them that class
    for period in [per1, per2, per3, per4, per5, per6, per7]:
        class_want = period[0][2]
        student_id = period[0][0]
        # Check if this class is available in other periods
        if all(class_want not in p or student_id not in [s[0] for s in p] for p in [per1, per2, per3, per4, per5, per6, per7] if p != period):
            if period[0] not in output and not (period[0][0],period[0][2]) in [(s[0],s[2]) for s in output] and not (period[0][3],period[0][2]) in [(s[0],s[3]) for s in output]:
                output.append(period[0])
                period.remove(period[0])
    


give_only_one_thats_avialbie_all_periods(per1, per2, per3, per4, per5, per6, per7)

print("updated:")
print(sort_by_first_number(output))

def randomly_assign_remaining_classes(per1, per2, per3, per4, per5, per6, per7):
    all_periods = [per1, per2, per3, per4, per5, per6, per7]
    for period in all_periods:
        if period[0] not in output and not (period[0][0],period[0][2]) in [(s[0],s[2]) for s in output] and not (period[0][0],period[0][3]) in [(s[0],s[3]) for s in output]:
            output.append(period[0])
            period.remove(period[0])

randomly_assign_remaining_classes(per1, per2, per3, per4, per5, per6, per7)

print("updated 2.0:")
print(sort_by_first_then_last(output))
print(f"Total percentage of students assigned: {len(output) / (len(students)*7) * 100:.2f}%")
