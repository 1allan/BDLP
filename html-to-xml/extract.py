import pprint
import sys
import codecs
from lxml import html

from html_renderer import HTMLRenderer
from group_finder import GroupFinder
from utils import normsp
from constants import TH_LEFT_GROUPING, TEI_WRAPPER

def get_font_size(group):
    szsum = 0.0
    szcount = 0
    for box in group:
        for txt in box['txt']:
            szsum += len(txt['txt']) * txt['fmt']['font-size']
            szcount += len(txt['txt'])
    result = szsum / szcount
    return result

def is_title(group, avg_size):
    line_count = len(group)
    space_before = group[0]['space-before']

    return (line_count == 1 and space_before > 30) or \
           (get_font_size(group) > avg_size * 1.1)

def output_line(box):
    global output_string
    for i, txt in enumerate(box['txt']):
        text = normsp(txt['txt'], left = i == 0, right = i == len(box['txt']) - 1)
        if txt['fmt']['font-style'] == 'italic':
            output_string += (f'<hi>{text}</hi>')
        else:
            output_string += (text)

def match_indent(indents, diff):
    if len(indents) == 0:
        indents[1] = [diff]
        return 1

    for key, value in indents.items():
        if abs(diff - value[0]) < 5:
            indents[key].append(diff)
            return key

    indents[len(indents) + 1] = [diff]
    return len(indents)

def output_block(group, indents, in_dirv, poetry=True):
    global output_string
    outer_tag = 'lg' if poetry else 'div' 
    line_tag = 'l' if poetry else 'p' 
    if in_div:
        sp = ' ' * 8
    else:
        sp = ' ' * 6
    output_string += (f'{sp}<{outer_tag}>\n')
    for box in group:
        if box["left"] - left_avg > 10:
            level = match_indent(indents, box["left"] - left_avg)
            output_string += (f'{sp}  <{line_tag} rend=\"indent{level}\">')
        else:
            output_string += (f'{sp}  <{line_tag}>')
        output_line(box)
        output_string += (f"</{line_tag}>")
        output_string += ("\n")
    output_string += (f'{sp}</{outer_tag}>\n')

def output_head(group):
    global output_string
    for box in group:
        output_string += (f'{" " * 8}<head>')
        output_line(box)
        output_string += ("</head>")
        output_string += ("\n")

output_string = ''
pp = pprint.PrettyPrinter(indent=4)
hr = HTMLRenderer.load_file(sys.argv[1])
gf = GroupFinder(hr.box)

left_sum = 0.0
count = 0
szsum = 0.0
szcount = 0

for group in gf.groups:
    for box in group:
        left_sum += box['left']
        count += 1
        for txt in box['txt']:
            szsum += len(txt['txt']) * txt['fmt']['font-size']
            szcount += len(txt['txt'])

left_avg = left_sum / count
sz_avg = szsum / szcount

lefts = []
classes = []

for group in gf.groups:
    for box in group:
        if box['parfmt']['text-align'] == 'left':
            left_group = None
            if len(lefts) == 0:
                lefts.append({"left": box['left']})
                left_group = 0
            else:
                for i in range(len(lefts)):
                    if abs(lefts[i]["left"] - box["left"]) < TH_LEFT_GROUPING:
                        left_group = i
                        break
                if left_group is None:
                    lefts.append({"left": box["left"]})
                    left_group = len(lefts) - 1
            classes.append(left_group)

title = ''
author = ''
with open(sys.argv[1], 'r', encoding='iso-8859-1') as f:
    string = f.read()

    tree = html.fromstring(string)
    for element in tree.xpath('//title'):
        try:
            title, author = element.text.split(', de ')
        except:
            title = element.text

header = TEI_WRAPPER.replace('[TITLE]', title)
header = header.replace('[AUTHOR]', author)

output_string += (header)
output_string += ("<text>\n")
in_div = False
indents = dict()

for group in gf.groups:
    if not is_title(group, sz_avg):
        output_block(group, indents, in_div, poetry='--poetry' in sys.argv)
    else:
        if in_div:
            output_string += (f'{" " * 6}</div>\n')
        output_string += (f'{" " * 6}<div type="chapter">\n')
        output_head(group)
        indents = dict()
        in_div = True

if in_div:
    output_string += (f'{" " * 6}</div>\n')

output_string += ("</text>\n</TEI>")
string = output_string.encode('utf-8').decode('utf-8')

with open(sys.argv[2], 'w', encoding='utf-8') as f:
    f.write(string)