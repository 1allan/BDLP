import os, sys, re
from lxml import etree

from util.constants import HTML_TAGS

static = './static/'

def load_static_files():
    output = dict()
    
    for d in os.listdir(static):
        with open(static + d, 'r') as f:
            output[static + d] = f.read()
    
    return output


def main(input_dir, output_dir):
    static_files = load_static_files()
    xslt = etree.parse(static + 'teibp.xsl')
    transform = etree.XSLT(xslt)

    try:
        os.makedirs(output_dir)
    except FileExistsError:
        pass
    
    if os.path.isdir(input_dir):
        files = os.listdir(input_dir)
        if input_dir[-1] != '/':
            input_dir += '/'
    else:
        files = [input_dir]
        input_dir = ''
    
    for filename in files:
        try:
            dom = etree.parse(input_dir + filename)
            newdom = transform(dom)

            tei_tags = []
            for element in newdom.xpath('//*'):
                tag = element.tag[element.tag.index('}') + 1:]
                
                if tag == 'body':
                    element.attrib['class'] = ''
                
                if tag in ('header', 'script', 'footer'):
                    element.getparent().remove(element)

                if tag == 'head' and 'type' not in element.attrib:
                    element.tag = element.tag.replace(tag, 'div')
                    element.attrib['class'] = 'head'

                if element.text == None:
                    element.text = ' '
                
                if tag not in HTML_TAGS or tag in ('title'):
                    if tag not in tei_tags:
                        tei_tags.append(tag)
                    element.attrib['class'] = tag
                    element.tag = element.tag.replace(tag, 'div')
            
            for key, value in static_files.items():
                if key[key.rindex('.') + 1:] == 'css':
                    for tag in tei_tags:
                        pattern = re.compile(f'\b{tag}\b')
                        print(static_files[key])
                        static_files[key] = re.sub(pattern, f'.{tag}', value)
                        print(static_files[key])
            
            for element in newdom.xpath('//*'):
                tag = element.tag[element.tag.index('}') + 1:]
                if tag == 'link':
                    href = static + element.attrib['href'][element.attrib['href'].rindex('/') + 1:]
                    if href in static_files and href[href.rindex('.') + 1:] == 'css':
                        element.tag = element.tag.replace(tag, 'style')
                        element.text = f"\n {static_files[href]} \n"
                        element.attrib.clear()
                        element.attrib['type'] = 'text/css'
                
            output = str(etree.tostring(newdom, method="html", pretty_print=True), 'utf-8')
            filename = filename.replace('.xml', '.html')
            filename = filename[filename.rindex('/') + 1:] if '/' in filename else filename
            
            with open(output_dir + '/' + filename, 'w') as f:
                f.write(output.replace('\\n', ''))
        
        except Exception as exc:
            print(filename + ' failed')
            print(exc, '\n')


if __name__ == '__main__':
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        print('É necessário fornecer para o script ao menos o caminho de entrada e saída!')
        print('python main.py <input> <output> <optional-arguments>')
