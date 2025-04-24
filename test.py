from xml.dom import minidom
from xml.etree.ElementTree import ElementTree, dump
from datetime import date

tree = ElementTree()
tree.parse('phaseTuning_HB_2024_v2.xml') # most recent QIE phase setting 2024-4-12
root = tree.getroot()

for sector in root.iter('CFGBrick'):
    print("sector   ",sector[0].text, sector[1].text,sector[2].text)
    sec = sector[3].text
    print("sec   ",sec)
    for delay in sector.iter('Data'):
        print("delay    ", delay.text)

