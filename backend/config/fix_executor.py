import re

with open('apps/chatbot/executor.py', 'r') as f:
    content = f.read()

# Fix lines with extra closing parentheses
lines = content.split('\n')
fixed_lines = []
for line in lines:
    # Remove extra ) at end of line if it has payload.get pattern
    if 'payload.get(' in line and line.rstrip().endswith('))'):
        line = line.rstrip()[:-1]  # Remove the extra )
    fixed_lines.append(line)

with open('apps/chatbot/executor.py', 'w') as f:
    f.write('\n'.join(fixed_lines))

print('Fixed executor.py')
