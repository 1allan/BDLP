import re
import sys

from bs4 import BeautifulSoup, NavigableString, Comment

from constants import SIZES_PCT, SIZES_PX

class CSSParser:

    def __init__(self, text, context=None):
        self.text = text
        self.rules = []
        if context is None:
            self.parse()
        else:
            self.found_selector(context.name)
            self.parse_rule_body(text)
        self.expand()
        self.index()

    def expand(self):
        for rule in self.rules:
            attrs = rule["attributes"]
            for name, value in attrs.items():
                if value.endswith("!important"):
                    value = value.replace('!important', '')
                    attrs[name] = value
                if name == "margin":
                    values = value.slit()
                    if len(values) == 1:
                        attrs["margin-top"] = value
                        attrs["margin-bottom"] = value
                        attrs["margin-left"] = value
                        attrs["margin-right"] = value
                    elif len(values) <= 4:
                        attrs["margin-top"] = values[0]
                        if len(values) >= 2:
                            attrs["margin-right"] = values[1]
                        if len(values) >= 3:
                            attrs["margin-bottom"] = values[2]
                        if len(values) == 4:
                            attrs["margin-left"] = values[3]
                    else:
                        raise Exception("unknown margin: " + value)

    def index(self):
        self.index_element_class = dict()
        self.index_element = dict()
        self.index_all = dict()

        for rule in self.rules:
            if rule["selector"][0] == "@":
                continue
            for selector in rule['selector'].split(','):
                selector = selector.strip()
                m = re.match(r"^([a-zA-Z]+)\.([a-zA-Z-]+)$", selector)
                if m:
                    element_name = m.group(1).strip().lower()
                    class_name = m.group(2).strip()
                    key = element_name + "." + class_name

                    if key not in self.index_element_class.keys():
                        self.index_element_class[key] = dict()
                    for attr_name in rule["attributes"]:
                        self.index_element_class[key][attr_name] = rule["attributes"][attr_name]

                m = re.match(r"^([a-zA-Z][a-zA-Z0-9]*)$", selector)
                if m:
                    element_name = m.group(1).strip().lower()
                    key = element_name
                    if key not in self.index_element.keys():
                        self.index_element[key] = dict()
                    for attr_name in rule["attributes"]:
                        self.index_element[key][attr_name] = rule["attributes"][attr_name]

                if selector == "*":
                    for attr_name in rule["attributes"]:
                        self.index_all[attr_name] = rule["attributes"][attr_name]

    def found_selector(self, s):
        self.rules.append({"selector": s.strip(), "attributes": dict()})

    def found_property(self, s):
        self._property_name = s.strip().lower()
        self.rules[-1]["attributes"][self._property_name] = None

    def found_value(self, s):
        self.rules[-1]["attributes"][self._property_name] = s.strip().lower()

    def parse_rule_body(self, body):
        i = 0
        s = 200
        pro = ""
        val = ""
        while i < len(body):
            if s == 200:
                if body[i] == ":":
                    s = 300
                    self.found_property(pro)
                    pro = ""
                else:
                    pro += body[i]
            elif s == 300:
                if body[i] == ";":
                    s = 200
                    self.found_value(val)
                    val = ""
                else:
                    val += body[i]
            i += 1
        if len(val) > 0:
            self.found_value(val)

    def parse(self):
        i = 0
        s = 0
        sel = ""
        bod = ""
        while i < len(self.text):
            if s == 0:
                if self.text[i:i + 4] == "<!--":
                    i += 3
                elif self.text[i:i + 2] == "/*":
                    s = 100
                    i += 1
                elif self.text[i] == "{":
                    s = 200
                    self.found_selector(sel)
                    sel = ""
                else:
                    sel += self.text[i]
            elif s == 100:
                if self.text[i:i + 2] == "*/":
                    s = 0
                    i += 1
            elif s == 200:
                if self.text[i] == "}":
                    s = 0
                    self.parse_rule_body(bod)
                    bod = ""
                else:
                    bod += self.text[i]
            i += 1


class CSSCascade:
    def __init__(self):
        self.global_parsers = []
        self.chain = []

    def add_global_style(self, text):
        self.global_parsers.append(CSSParser(text))

    def push(self, el):
        desc = dict()
        desc["el"] = {"name": el.name, "class": el.attrs.get("class", [])}
        style = el.attrs.get("style", "")
        if el.name == "font":
            if "size" in el.attrs.keys():
                if re.match(r"^[0-9]$", el.attrs["size"]):
                    sz = int(el.attrs["size"])
                    if sz < 1:
                        sz = 1
                    if sz > 7:
                        sz = 7
                    sz = SIZES_PX[sz]
                elif re.match(r"^[+-][0-9]$", el.attrs["size"]):
                    sz = int(el.attrs["size"])
                    if sz < -7:
                        sz = -7
                    if sz > 7:
                        sz = 7
                    sz = SIZES_PCT[sz]
                style = f'font-size: {sz}; {style}'
        desc["parser"] = CSSParser(style, el)
        self.chain.append(desc)

    def pop(self):
        self.chain.pop()

    def get_length(self, text):
        try:
            if text.endswith("px"):
                return float(text[0:-2])
            elif text.endswith("pt"):
                return float(text[0:-2]) * 1.333333333333333
            elif text.endswith("cm"):
                return float(text[0:-2]) * 37.7953323885
            elif text == "0":
                return 0.00
            else:
                return float(text)
        except ValueError:
            return 1.0

    def set_attr(self, attrs, name, value):
        if name.startswith("margin-") or name.endswith("-height") or \
           name.endswith("-size") or name in ["width", "height", "text-indent"]:
            if value.endswith("%"):
                if name not in attrs:
                    if name == "width":
                        value = 100.00
                    else:
                        raise Exception("Attribute with no value set: " + name)
                else:
                    value = attrs[name] * float(value[:-1]) * 0.01
                self.set_attr(attrs, name, str(value) + "px")
                return
            elif value.endswith("em"):
                value = attrs["font-size"] * float(value[:-2])
                self.set_attr(attrs, name, str(value) + "px")
                return
            if name == "font-size":
                attrs[name] = self.get_length(value)
                attrs["line-height"] = attrs[name] * 1.2
            elif name == "line-height" and value == "normal":
                attrs["line-height"] = attrs["font-size"] * 1.2
            else:
                attrs[name] = self.get_length(value)
        else:
            attrs[name] = value

    def __attrs_setter(self, parser, el_name, class_names, attrs=None):
        attrs = attrs if attrs is not None else dict()
        for key, value in parser.index_all.items():
            self.set_attr(attrs, key, value)
        for key, value in parser.index_element.get(el_name, {}).items():
            self.set_attr(attrs, key, value)
        for name in class_names:
            for key, value in parser.index_element_class.get(el_name + "." + name, {}).items():
                self.set_attr(attrs, key, value)

    def format(self):
        attrs = {}
        for desc in self.chain:
            el_name = desc["el"]["name"]
            el_class = desc["el"]["class"]
            for parser in self.global_parsers:
                self.__attrs_setter(parser, el_name, el_class, attrs)
            self.__attrs_setter(desc['parser'], el_name, el_class, attrs)
        return attrs

    def attributes_for(self, element, attrs=None):
        attrs = attrs if attrs is not None else dict()
        for parser in self.parsers:
            self.__attrs_setter(parser, element.name.lower(),
                       element.attrs.get('class', []), attrs)
        return attrs
