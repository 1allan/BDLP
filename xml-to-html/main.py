import os, sys
from lxml import etree

static = './static/'

def load_static_files():
    output = dict()
    
    for d in os.listdir(static):
        with open(static + d, 'r') as f:
            output[static + d] = f.read()
    
    return output


def replace(string, blacklist):
    for key, value in blacklist.items():
        if key in string:
            string = string.replace(key, value)
    return string


def main(input_dir, output_dir):
    static_files = load_static_files()
    xslt = etree.parse(static + 'teibp.xsl')
    transform = etree.XSLT(xslt)
    
    if os.path.isdir(input_dir):
        files = os.listdir(input_dir)
        input_dir = input_dir[:input_dir.rindex('/') + 1]
    else:
        files = [input_dir]
        input_dir = ''
    
    for filename in files:
        try:
            dom = etree.parse(input_dir + filename)
            newdom = transform(dom)

            for element in newdom.iter():
                tag = element.tag[element.tag.index('}') + 1:]
                
                if tag == 'header' or tag == 'footer':
                    element.getparent().remove(element)

                if tag == 'head' and 'type' not in element.attrib:
                    element.tag = element.tag.replace(tag, 'p')
                    element.attrib['class'] = 'title'

                if tag == 'script' and 'src' in element.attrib:
                    src = static + element.attrib['src'][element.attrib['src'].rindex('/') + 1:]
                    if src in static_files:
                        element.text = f"\n {static_files[src]} \n"
                        element.attrib.pop('src')
                
                if tag == 'link':
                    href = static + element.attrib['href'][element.attrib['href'].rindex('/') + 1:]
                    if href in static_files and href[href.rindex('.') + 1:] == 'css':
                        element.tag = element.tag.replace(tag, 'style')
                        element.text = f"\n {static_files[href]} \n"
                        element.attrib.clear()
                        element.attrib['type'] = 'text/css'


                if element.text == None:
                    element.text = ' '
                
            output = str(etree.tostring(newdom, method="html", pretty_print=True), 'utf-8')
            filename = filename.replace('.xml', '.html')

            if not os.path.exists(output_dir):
                try:
                    os.makedirs(os.path.dirname(output_dir))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
            
            if output_dir == '.':
                output_dir = './'

            filename = filename[filename.rindex('/') + 1:] if '/' in filename else filename
            
            with open(output_dir + filename, 'w') as f:
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
