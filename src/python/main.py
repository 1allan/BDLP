import os, sys
from lxml import etree

dir_list = ['../js/main.js', '../css/custom.css', '../css/teibp.css', '../css/mediaqueries.css']

def load_files(directories):
    output = dict()
    
    for d in directories:
        with open(d, 'r') as f:
            output[d] = f.read()
    
    return output


def replace(string, blacklist):
    for key, value in blacklist.items():
        if key in string:
            string = string.replace(key, value)
    return string


def main(keep_header=True):
    
    ext_files = load_files(dir_list)
    xslt = etree.parse('../xsl/teibp.xsl')
    transform = etree.XSLT(xslt)

    for filename in os.listdir('../content/'):
        try:
            dom = etree.parse('../content/' + filename)
            newdom = transform(dom)

            for element in newdom.iter():
                tag = element.tag[element.tag.index('}') + 1:]

                if tag == 'head' and 'type' not in element.attrib:
                    element.tag = element.tag.replace(tag, 'p')
                    element.attrib['class'] = 'title'

                if tag == 'script' and 'src' in element.attrib and element.attrib['src'] in ext_files:
                    element.text = f"\n {ext_files[element.attrib['src']]} \n"
                    element.attrib.pop('src')
                
                if tag == 'link' and element.attrib['href'] in ext_files:
                    element.tag = element.tag.replace(tag, 'style')
                    element.text = f"\n {ext_files[element.attrib['href']]} \n"

                if tag == 'header' and not keep_header:
                    element.getparent().remove(element)

                if element.text == None:
                    element.text = ' '
                
            output = str(etree.tostring(newdom, method="html", pretty_print=True), 'utf-8')
            filename = replace(filename, {' ': '_', '.xml': '.html'})
            
            with open('../html/' + filename, 'w') as f:
                f.write(output.replace('\\n', ''))
            
        except Exception as exc:
            print(filename + ' failed')
            print(exc, '\n')


if __name__ == '__main__':
    main(keep_header=('--keep-header' not in sys.argv))