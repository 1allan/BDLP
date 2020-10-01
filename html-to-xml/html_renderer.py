import re
import glob
import os
import sys
import pickle
import ujson
import sys
import pprint

from bs4 import BeautifulSoup, NavigableString, Comment
from lxml import html, etree

from css import CSSCascade
from constants import DEFAULT_STYLE
from utils import normsp


class HTMLRenderer:

    def __init__(self, text, box=None, unique=None):
        if box is not None:
            self.box = box
            return
        self.unique = unique
        self.doc = BeautifulSoup(text, "lxml")
        self.css = CSSCascade()
        self.css.add_global_style(DEFAULT_STYLE)
        self.box = {"fmt": {}, "sub": [], "par": None, "typ": "root"}
        self.cur_box = self.box
        self.render()
        self.remove_par(self.box)
        self.doc = None
        self.css = None
        self.cur_box = None

    def remove_par(self, box):
        if box["typ"] != "text":
            for sub in box["sub"]:
                self.remove_par(sub)
        else:
            box["parfmt"] = box["par"]["fmt"]
        box.pop("par", None)

    def load_file(path):
        with open(path, 'rb') as f:
            s = f.read()
            s = re.sub(rb"ProductID=\"[^\"]*\"", rb"", s)
            s = s.decode('utf-8')

            tree = html.fromstring(s)
            for element in tree.xpath('//*'):
                if element.tag == 'a' or (element.text is not None and element.text.upper() == 'ÍNDICE'):
                    element.getparent().remove(element)

            s = etree.tostring(tree, method="html", pretty_print=True)

            return HTMLRenderer(s)

    def print_boxes(self, box, level=0):
        if box["typ"] != "text":
            print(f'{(" " * 4)*level}{box["typ"]} {box["top"]} {box["calc-height"]}')
            for sub in box["sub"]:
                self.print_boxes(sub, level + 1)
        else:
            print(f'{(" " * 4)*level}{box["typ"]}')

    def render(self):
        for style in self.doc.find_all("style"):
            self.css.add_global_style(style.text)
        self.render_element(self.doc.find("body"))
        self.expand_text(self.box)
        self.calculate_height(self.box)
        self.position(self.box)
        self.remove_empty_boxes(self.box)

    def remove_empty_boxes(self, box):
        if box["typ"] == "text":
            txt = ""
            for seg in box["txt"]:
                txt += seg["txt"]
            txt = txt.strip()
            return len(txt) == 0
        else:
            badidx = []
            for i, sub in enumerate(box["sub"]):
                if self.remove_empty_boxes(sub):
                    badidx.append(i)
            allofthem = len(badidx) == len(box["sub"])
            for i in reversed(badidx):
                del box["sub"][i]
            return allofthem

    def calculate_height(self, box):
        if box["typ"] == "text":
            box["calc-height"] = box["par"]["fmt"]["line-height"]
            box["calc-margin-top"] = 0.0
            box["calc-margin-bottom"] = 0.0
        else:
            height = 0.0
            bef = 0.0
            aft = 0.0
            for i, sub in enumerate(box["sub"]):
                self.calculate_height(sub)
                height += sub["calc-height"]
                if i == 0:
                    bef = sub["calc-margin-top"]
                    sub["calc-margin-top"] = 0.0
                else:
                    tot = max(box["sub"][i]["calc-margin-top"],
                              box["sub"][i - 1]["calc-margin-bottom"])
                    box["sub"][i]["calc-margin-top"] = 0
                    box["sub"][i - 1]["calc-margin-bottom"] = tot
                    height += tot
                if i == len(box["sub"]) - 1:
                    aft = sub["calc-margin-bottom"]
                    sub["calc-margin-bottom"] = 0.0

            if box["typ"] == "root":
                box["calc-height"] = height
                box["calc-margin-top"] = bef
                box["calc-margin-bottom"] = aft
            else:
                box["calc-height"] = height
                box["calc-margin-top"] = max(bef, box["fmt"]["margin-top"])
                box["calc-margin-bottom"] = max(aft,
                                                box["fmt"]["margin-bottom"])

    def nbsp_beg(self, s):
        m = re.search(r"^[\u00a0]+", re.sub(r"[ \n\r\t]", "", s))
        return len(m.group(0)) if m else 0

    def position(self, box, prev_sibl=None):
        if box["typ"] == "root":
            box["top"] = box["calc-margin-top"]
            box["left"] = 0
        else:
            if prev_sibl is not None:
                box["top"] = prev_sibl["top"] + prev_sibl["calc-height"] + \
                    prev_sibl["calc-margin-bottom"] + box["calc-margin-top"]
            else:
                box["top"] = box["par"]["top"] + box["calc-margin-top"]
            if box["typ"] != "text":
                box["left"] = box["par"]["left"] + \
                    box["fmt"]["margin-left"] + box["fmt"]["text-indent"]
            else:
                box["left"] = box["par"]["left"]
                box["left"] += self.nbsp_beg(box["expnn"]) * 5
        prev = None
        if box["typ"] != "text":
            for sub in box["sub"]:
                self.position(sub, prev_sibl=prev)
                prev = sub

    def expand_text(self, box):
        if box["typ"] == "text":
            s = ""
            for seg in box["txt"]:
                s += seg["txt"]
            box["expnn"] = s
            s = s.strip()
            box["exp"] = s
        else:
            for sub in box["sub"]:
                self.expand_text(sub)

    def append_segment(self, el, fmt):
        elnlr = normsp(el)
        if len(self.cur_box["sub"]) > 0 and self.cur_box["sub"][-1]["typ"] == "text":
            self.cur_box["sub"][-1]["txt"].append({"txt": el, "fmt": fmt})
        else:
            if len(elnlr) == 0:
                return
            new_box = {"par": self.cur_box, "typ": "text", "txt": [{"txt": el, "fmt": fmt}]}
            self.cur_box["sub"].append(new_box)

    def break_segment(self, fmt):
        if len(self.cur_box["sub"]) == 0:
            new_box = {"par": self.cur_box, "typ": "text", "txt": [{"txt": "", "fmt": fmt}]}
            self.cur_box["sub"].append(new_box)
        new_box = {"par": self.cur_box, "typ": "text", "txt": [{"txt": "", "fmt": fmt}]}
        self.cur_box["sub"].append(new_box)

    def render_element(self, el):
        self.css.push(el)
        fmt = self.css.format()
        if fmt["display"] == "block":
            new_box = {"fmt": fmt, "sub": [], "par": self.cur_box, "typ": "true"}
            self.cur_box["sub"].append(new_box)
            self.cur_box = new_box

        children = list(el.children)
        for child in children:
            if isinstance(child, NavigableString):
                self.append_segment(str(child), fmt)
            elif child.name == "br":
                self.break_segment(fmt)
            else:
                self.render_element(child)

        if fmt["display"] == "block":
            self.cur_box = self.cur_box["par"]
        self.css.pop()

