'''
Tools to do graphics in the terminal.  
`clearLine`: fill the current line with ' ' (whitespace)  
`eastAsianStrLen`: length of str as displayed on terminal (so chinese characters and other fullwidth chars count as 2 or more spaces)  
`displayAllColors`: display all colors that your terminal supports.  
`printTable`: print a table in the terminal.  
'''
from unicodedata import east_asian_width

def eastAsianStrSparse(s, marks = []):
    chars = []
    marks_movement = {}
    for i, char in enumerate(s):
        if i in marks:
            marks_movement[i] = len(chars)
        chars.append(char)
        if east_asian_width(char) in 'AFNW':
            chars.append('')
    if marks:
        return chars, [marks_movement[x] for x in marks]
    else:
        return chars

def eastAsianStrToWidths(s, fullwidth_scale = 2):
    widths = []
    for char in s:
        if east_asian_width(char) in 'AFNW':
            widths.append(fullwidth_scale)
        else:
            widths.append(1)
    return widths

def eastAsianStrLen(s, fullwidth_scale = 2):
    return sum(eastAsianStrToWidths(s, fullwidth_scale))

def eastAsianStrLeft(s, n):
    widths = eastAsianStrToWidths(s)
    width = 0
    for i, w in enumerate(widths):
        width += w
        if width > n:
            return s[:i]
    return s

def eastAsianStrRight(s, n):
    widths = eastAsianStrToWidths(s)
    width = 0
    for i, w in reversed(tuple(enumerate(widths))):
        width += w
        if width >= n:
            return s[i:]
    return s

def eastAsianStrPad(s, padding, pad_char = ' '):
    return s + pad_char * (padding - eastAsianStrLen(s))

def printTable(table):
    col_width = [0 for _ in table[0]]
    for line in table:
        for i, text in enumerate(line):
            col_width[i] = max(col_width[i], eastAsianStrLen(text))
    for line in table:
        print(' | ', end = '')
        for i, text in enumerate(line):
            print(eastAsianStrPad(text, col_width[i]), end=' | ')
        print()

if __name__ == '__main__':
    from console import console
    displayAllColors()
    printTable([
        ['ID', 'Name', 'Thing'], 
        ['32678941829045312', 'Daniel', 'This is a demo'], 
        ['340286501983078', 'Person B', 'Thing 2'], 
    ])
    console(globals())
