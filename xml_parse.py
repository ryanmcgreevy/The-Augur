import xml.etree.ElementTree as ET 
import os
import argparse

def parse(name):
    # create element tree object 
    tree = ET.parse(name) 

    # get root element 
    root = tree.getroot() 
    local_dir = "xml_dump/"
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    for child in root.iter('{http://www.mediawiki.org/xml/export-0.10/}page'):
        title = child.find('{http://www.mediawiki.org/xml/export-0.10/}title').text
        title = title.replace("/","_")
        for child2 in child:
            content = child2.find('{http://www.mediawiki.org/xml/export-0.10/}text')
            if content != None:
                content = content.text
            else:
                content = " "
            filename = os.path.join(local_dir, title + ".txt")
            with open(filename, 'w') as f:
                if content != None: f.write(content)


parser = argparse.ArgumentParser("xml_parse")
parser.add_argument("file", help="Name of XML file to parse.", type=str)
args = parser.parse_args()

parse(args.file)