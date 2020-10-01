import re
import glob
import io
import sys
import math

from utils import normsp
from constants import TH1, TH2


class GroupFinder:
    
    def __init__(self, box):
        self.box = box
        self.text_boxes = []
        self.find_text_boxes(self.box)
        self.calculate_spacing()
        self.groups = []
        self.find_groups()
    
    def compatible_align(self, a, b):
        alignments = {'left', 'justify'}
        return a == b or a in alignments and b in alignments
    
    def find_groups(self):
        for i in range(0, len(self.text_boxes)):
            if i == 0:
                self.groups.append([self.text_boxes[i]])
                continue
            if i == len(self.text_boxes) - 1:
                good = True
                if good and not self.compatible_align(self.text_boxes[i]["parfmt"]["text-align"], self.text_boxes[i - 1]["parfmt"]["text-align"]):
                    good = False
                if good and len(self.groups[-1]) > 1 and (self.text_boxes[i]["space-before"] - self.text_boxes[i - 1]["space-before"]) >= TH1:
                    good = False
                if good:
                    self.groups[-1].append(self.text_boxes[i])
                else:
                    self.groups.append([self.text_boxes[i]])
                continue
            good = True
            if len(self.groups[-1]) == 1:
                good = True
                if good and not self.compatible_align(self.text_boxes[i]["parfmt"]["text-align"], self.text_boxes[i - 1]["parfmt"]["text-align"]):
                    good = False
                if good and (self.text_boxes[i]["space-before"] - self.text_boxes[i - 1]["space-before"]) >= TH1:
                    good = False
                if good and (self.text_boxes[i]["space-before"]) >= TH2:
                    good = False
            else:
                good = True
                if good and not self.compatible_align(self.text_boxes[i]["parfmt"]["text-align"], self.text_boxes[i - 1]["parfmt"]["text-align"]):
                    good = False
                if good and abs(self.text_boxes[i]["space-before"] - self.text_boxes[i - 1]["space-before"]) >= TH1:
                    good = False
            if good:
                self.groups[-1].append(self.text_boxes[i])
            else:
                self.groups.append([self.text_boxes[i]])
        for i in range(0, len(self.groups) - 1):
            if len(self.groups[i]) > 1 and len(self.groups[i + 1]) > 1:
                good = True
                if not self.compatible_align(self.groups[i][-1]["parfmt"]["text-align"], self.groups[i + 1][0]["parfmt"]["text-align"]):
                    good = False
                if abs(self.groups[i][-1]["space-after"] - self.groups[i + 1][0]["space-after"]) >= TH1:
                    good = False
                if (self.groups[i][-1]["space-before"] - self.groups[i + 1][0]["space-before"]) <= TH1:
                    good = False
                if good:
                    self.groups[i + 1].insert(0, self.groups[i][-1])
                    del self.groups[i][-1]
            if len(self.groups[i]) > 1 and len(self.groups[i + 1]) == 1:
                good = True
                if not self.compatible_align(self.groups[i][-1]["parfmt"]["text-align"], self.groups[i + 1][0]["parfmt"]["text-align"]):
                    good = False
                if (self.groups[i][-1]["space-before"] - self.groups[i + 1][0]["space-before"]) <= TH1:
                    good = False
                if (self.groups[i + 1][0]["space-after"] - self.groups[i][-1]["space-after"]) <= TH1:
                    good = False
                if good:
                    self.groups[i + 1].insert(0, self.groups[i][-1])
                    del self.groups[i][-1]
                    
    def calculate_spacing(self):
        for i, box in enumerate(self.text_boxes):
            if i > 0:
                box["space-before"] = box["top"] - (self.text_boxes[i - 1]["top"] + self.text_boxes[i - 1]["parfmt"]["line-height"])
                self.text_boxes[i - 1]["space-after"] = box["space-before"]
            elif i == len(self.text_boxes) - 1:
                box["space-after"] = box["calc-margin-bottom"]
            else:
                box["space-before"] = box["calc-margin-top"]
            

    def find_text_boxes(self, box):
        if box["typ"] == "text":
            self.text_boxes.append(box)
        else:
            for sub in box["sub"]:
                self.find_text_boxes(sub)
