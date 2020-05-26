from lxml import etree
from os import listdir

trash = {
    '<script type="text/javascript" src="../js/teibp.js"/>': '<script type="text/javascript" src="../js/teibp.js"></script>',
    '<script type="text/javascript" src="../js/main.js"/>': '<script type="text/javascript" src="../js/main.js"></script>',
    '\\n': '',
    '<style type="text/css" id="tagusage-css"/>': '',
    '<style type="text/css"/>': '',
    '<title/>': '',
}

def remove_head_tags(doc):
    head_start = doc.index('<head ')
    head_end = doc[head_start:].index('>') + head_start + 1
    doc = doc.replace(
        doc[head_start:head_end], 
        '<span class="title">'
    )
    
    doc = doc.replace(doc[(doc[head_end:].index('</head>') - 1):(doc[head_end:].index('</head>') + 6)], '</span>')
    return doc

def treat_string(string, blacklist):
    for item in blacklist.items():
        string = string.replace(item[0], item[1])
    return string

for filename in listdir('../content/'):
    try:
        dom = etree.parse('../content/' + filename)
        xslt = etree.parse('../xsl/teibp.xsl')
        transform = etree.XSLT(xslt)
        newdom = transform(dom)

        filename = treat_string(filename, {' ': '_', '.xml': '.html'})
        with open('../html/' + filename, 'w') as f:
            output = str(etree.tostring(newdom, pretty_print=True), 'utf-8')
            f.write(remove_head_tags(treat_string(output, trash)))
    
    except Exception as exc:
        print(filename + ' failed')
        print(exc, '\n')