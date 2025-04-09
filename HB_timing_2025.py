#!/usr/bin/python

from xml.dom import minidom
from xml.etree.ElementTree import ElementTree, dump
from datetime import date
import argparse

today = date.today().strftime('%Y-%m-%d')

mapka = {}
corrs = {}

parser = argparse.ArgumentParser(description="Generate HB Phase Delay")
parser.add_argument("xml_file", help="Reference QIE xml file")
parser.add_argument("time_shift", help="QIE time shift")

args = parser.parse_args()


def read_map():
    with open("Lmap_ngHB_N_20200212.txt") as f:
        next(f) #skip the first line
        for line in f:
            l = line.split()
            geo = [int(l[0])*int(l[1]), int(l[2]), int(l[4])]         #[side*eta, phi, depth]
            ele = l[6] + l[12] + str((int(l[10])-1)*16 + int(l[11]))  #RBX + RM + qiech (in 1 QIE for a RBX/RM, there are 16 QIECH (for HB))
            mapka[ele] = geo

            
def read_corr():
    with open(args.time_shift) as f: # 2025 txt file of QIE delays adjustment, relative to 2024
        next(f)
        for line in f:
            l = line.split()
            for i in range (1,5):
                ed = l[0] + " " + str(i)
                corrs[ed] = float(l[i])

tree = ElementTree()
tree.parse(args.xml_file) # most recent QIE phase setting 2024-4-12
root = tree.getroot()

def loop():
    for sector in root.iter('CFGBrick'):
        sec = sector[3].text  #RBX
        for delay in sector.iter('Data'):
            if delay.attrib['rm'] == '5': #skipping the calibration unit
                pass
            else:
                chan = sec + delay.attrib['rm'] + delay.attrib['qie'] 
                geom = mapka[chan]
                ed = str(geom[0]) + " " + str(geom[2])
                newdel = 64 if "-999" in ed else int(delay.text)+int(round(corrs[ed])) # round(corrs[ed] / 0.5 if file given in ns        #Depth = -999 in the Lmap is calibration unit/blind channels
                if (newdel<64 and newdel>49): # account for the 14 skipped values
                    if (newdel > int(delay.text)):
                        newdel = newdel+14
                    if (newdel < int(delay.text)):
                        newdel = newdel-14

                if newdel>113 or (newdel>49 and newdel<64): print (newdel)
                delay.text = str(newdel)
    
    tree.write('HB_QIEscanSetting_timing'+today+'.xml') # new QIE phase setting with adjustments made after 2025

def main():
    read_map()
    read_corr()
    loop()


    
if __name__ == "__main__":
    main()
