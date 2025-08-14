def replace_first_3_digits_with_line_number(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for i, line in enumerate(f_in, start=1):
            if i < 100:
                new_line = line
                f_out.write(new_line)
            else:
                # Replace first 3 digits with line number (as string)
                # Assuming first 3 characters are digits to replace
                new_line = f"{i}{line[3:]}" if len(line) >= 3 else f"{i}\n"
                f_out.write(new_line)

replace_first_3_digits_with_line_number('students.txt', 'students1.txt')
