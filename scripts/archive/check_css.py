import sys

with open('styles/globals.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Remove comments to count braces accurately
in_comment = False
comment_start = -1
stripped_css = []
i = 0
while i < len(css):
    if not in_comment and css[i:i+2] == '/*':
        in_comment = True
        comment_start = i
        i += 2
        continue
    if in_comment and css[i:i+2] == '*/':
        in_comment = False
        i += 2
        continue
    if not in_comment:
        stripped_css.append(css[i])
    i += 1

if in_comment:
    print(f"ERROR: Unclosed comment started at index {comment_start}")
    lines = css[:comment_start].split('\n')
    print(f"Line: {len(lines)}")
else:
    print("Comments are fully closed.")

clean_css = "".join(stripped_css)

open_braces = 0
last_open_line = 0
for i, char in enumerate(clean_css):
    if char == '{':
        open_braces += 1
    elif char == '}':
        open_braces -= 1
        if open_braces < 0:
            print("ERROR: Too many closing braces!")
            break

if open_braces > 0:
    print(f"ERROR: Unclosed opening braces! Count: {open_braces}")
elif open_braces == 0:
    print("Braces are balanced.")

