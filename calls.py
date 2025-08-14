import mainfile
with open('students.txt', 'r') as f:
        lines = f.readlines()
best = 0
bestoutput = []
for i in range(1000):
    current = mainfile.try_once()
    if len(current) > best:
        best = len(current)
        bestoutput = current
print("Best score:", best/(len(lines) * 7) * 100)
with open("output.txt", "w") as file:
    file.write(str(bestoutput))
