import xml.etree.ElementTree as ET
import sys


def load_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for e in root:
        for sub_e in e:
            for sub_sub_e in sub_e:
                print(sub_sub_e)
                print(sub_sub_e.text)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        print(sys.argv[1])
        load_xml(sys.argv[1])


