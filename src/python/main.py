from lxml import etree
from os import listdir

trash = {
    '\\n': '',
}

def treat_string(string, blacklist):
    for key in blacklist:
        if key in string:
            string = string.replace(key, blacklist[key])
    return string

for filename in listdir('../content/'):
    try:
        dom = etree.parse('../content/' + filename)
        xslt = etree.parse('../xsl/teibp.xsl')
        transform = etree.XSLT(xslt)
        newdom = transform(dom)

        for elem in newdom.iter():
            tag = elem.tag[elem.tag.index('}') + 1:]

            if tag == 'head':
                elem.tag = elem.tag.replace(tag, 'p')
                elem.attrib['class'] = 'title'

            if elem.text == None:
                elem.text = ' '
            
        output = str(etree.tostring(newdom, pretty_print=True), 'utf-8')
        filename = treat_string(filename, {' ': '_', '.xml': '.html'})
        with open('../html/' + filename, 'w') as f:
            f.write(treat_string(output, trash))
    
    except Exception as exc:
        print(filename + ' failed')
        print(exc, '\n')