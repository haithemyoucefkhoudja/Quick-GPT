import re
list = ['``', '`', 'def`', '```']
pattern = r"`{1,3}"
suspect = []
pattern_found = False
for item in list:
    match = re.search(pattern, item)
    _fences = match.group()
    if _fences == '```':
        pattern_found = True
        print('found')
        continue
    suspect.append(item)

print("suspect:",suspect)

all = ''.join(suspect)

print("all:", all)
# search in first one then second then the third...


parts = re.split('```', all)
print(parts)
if len(parts) > 2:
    print('not the one:')
bot_text_right = parts[1] if len(parts) > 1 else ""
bot_text_left = parts[0] if len(parts) > 1 else ""
print('left:', bot_text_left)
print("right:", bot_text_right)
# prevent the collapse between md and code blocks
print(pattern_found)
