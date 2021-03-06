import os
import sys
import re

from os.path import isfile, isdir, join, dirname
from lxml import etree

from util.constants import HTML_TAGS, GENERATOR_TAG, XML_PREFIX


add_bar = lambda d: d + '/' if d[-1] != '/' else d


def load_static(dir) -> dict:
    dir = add_bar(dir)
    if isdir(dir):
        output = dict()
        for file in os.listdir(dir):
            with open(dir + file, 'r', encoding='utf8') as f:
                output[file] = f.read()
    else:
        print('Diretório de arquivos estáticos fornecido é inválido!')
        return
    return output


def main(input_dir, output_dir, static_dir=join(dirname(__file__), 'static')):
    static_dir = add_bar(static_dir)
    static_files = load_static(static_dir)
    xslt = etree.parse(static_dir + 'teibp.xsl')
    transform = etree.XSLT(xslt)

    xmls = None
    xmls_path = ''
    if isdir(input_dir):
        xmls = [f for f in os.listdir(input_dir) if isfile(join(input_dir, f))]
        xmls_path = add_bar(input_dir)
    else:
        if '/' in input_dir:
            xmls_path = input_dir[:input_dir.rindex('/') + 1]
            xmls = [input_dir[input_dir.rindex('/') + 1:]]
        else:
            xmls_path = './'
            xmls = [input_dir]

    output_dir = add_bar(output_dir)
    try:
        os.makedirs(output_dir)
    except FileExistsError:
        pass

    for xml in xmls:
        try:
            dom = etree.parse(xmls_path + xml)
            newdom = transform(dom)

            body = newdom.find(XML_PREFIX + 'body')
            head = newdom.find(XML_PREFIX + 'head')
            
            meta = etree.fromstring(GENERATOR_TAG)
            meta.tag = XML_PREFIX + meta.tag
            head.append(meta)
            
            links = list()
            tags_blacklist = list()
            for element in newdom.xpath('//*'):
                tag_name = element.tag[element.tag.index('}') + 1:]

                if tag_name == 'head' and 'type' in element.attrib.keys():
                    element.attrib.pop('type')
                    continue
                
                if tag_name == 'body':
                    if 'class' in element.attrib.keys():
                        element.attrib.pop('class')
                
                if tag_name in ('header', 'script', 'footer'):
                    element.getparent().remove(element)
                    
                if element.text == None:
                    element.text = ' '
                
                if tag_name not in HTML_TAGS or tag_name in ('title', 'head'):
                    if tag_name not in tags_blacklist:
                        tags_blacklist.append(tag_name)
                    
                    element.attrib['class'] = tag_name
                    element.tag = 'span'

                if tag_name == 'link':
                    body.append(element)
                    href = element.attrib['href']
                    if href[href.rindex('/') + 1:] in static_files.keys():
                        links.append(element)
            
            for file in static_files:
                if file[file.rindex('.') + 1:] == 'css':
                    for t in tags_blacklist:
                        hm = static_files[file]
                        pattern = r'(?<![-.#])\b{}\b(?!-)'.format(t)
                        static_files[file] = re.sub(pattern, 
                                                    r'span.' + t, 
                                                    static_files[file])

            for l in links:
                href = l.attrib['href']
                href = href[href.rindex('/') + 1:]
                l.tag = 'style'
                l.text = f"\n {static_files[href]} \n"
                l.attrib.clear()
                l.attrib['type'] = 'text/css'
            
            etree_str = etree.tostring(newdom, method="html", 
                                       pretty_print=True)
            output = str(etree_str, 'utf-8')
            html = xml.replace('.xml', '.html')
            
            with open(f'{output_dir}/{html}', 'w', encoding='utf8') as f:
                f.write(output)

        except Exception as exc:
            print('Error: ', exc) 

if __name__ == '__main__':
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        print(('É necessário fornecer para o script ao menos o caminho de '
               'entrada e saída!'))
        print('python main.py <entrada> <saída> <argumentos-opcionais>')
