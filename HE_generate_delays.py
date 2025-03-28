#!/usr/bin/python

from xml.dom import minidom
from xml.etree.ElementTree import ElementTree, dump
from datetime import date
import argparse

today = date.today().strftime('%Y-%m-%d')

tree = ElementTree()
tree.parse('HE_QIEscanSetting_timing'+today+'.xml') #updated 2025 QIE (only HE)
root = tree.getroot()

parser = argparse.ArgumentParser(description="Generate HE Phase Delay")
parser.add_argument("start_delay", type=int, help="Start of the phase delay")
parser.add_argument("end_delay", type=int, help="End of the phase delay")
parser.add_argument("delay_steps", type=int, help="Phase delay steps")

args = parser.parse_args()


def loop():
    outOfRange = 0
    with open( str(nsShift) + 'ns_HE.txt', 'w') as f:
        for sector in root.iter('CFGBrick'):
            sec = sector[3].text
#            rm1 = 'put ' + sec + '-1' + '-QIE[1-64]_PhaseDelay ' #HB has 64 QIEs
#            rm2 = 'put ' + sec + '-2' + '-QIE[1-64]_PhaseDelay '
#            rm3 = 'put ' + sec + '-3' + '-QIE[1-64]_PhaseDelay '
#            rm4 = 'put ' + sec + '-4' + '-QIE[1-64]_PhaseDelay '
            rm1 = 'put ' + sec + '-1' + '-QIE[1-48]_PhaseDelay '  #HE has 48 QIEs
            rm2 = 'put ' + sec + '-2' + '-QIE[1-48]_PhaseDelay '
            rm3 = 'put ' + sec + '-3' + '-QIE[1-48]_PhaseDelay '
            rm4 = 'put ' + sec + '-4' + '-QIE[1-48]_PhaseDelay '
            rm1_set = ''
            rm2_set = ''
            rm3_set = ''
            rm4_set = ''
            for delay in sector.iter('Data'):
                if delay.attrib['rm'] == '5':
                    pass
                else:
                    phdelay = int(delay.text) - 2*nsShift # +4 means this is -2ns shift
                    # if (int(delay.text) == 69): print(str(int(delay.text)) + " = int(delay.text) and phdelay = " + str(phdelay))
                    #if (phdelay<64 and phdelay>49) or (phdelay-14<50): phdelay = phdelay-14
                    if (phdelay<64 and phdelay>49) or (phdelay<50 and int(delay.text)>63) or (phdelay>63 and int(delay.text)<50): # account for the 14 skipped values 
                        if (phdelay > int(delay.text)): # we are moving up in QIE values
                            phdelay = phdelay+14
                        if (phdelay < int(delay.text)): # we are moving down in QIE values
                            phdelay = phdelay-14
                        #if (int(delay.text) == 69): print(str(int(delay.text)) + " = int(delay.text) and phdelay = " + str(phdelay))
                    if (phdelay>49 and phdelay<64) or phdelay<0 or phdelay>113: 
                        #print (phdelay)
                        outOfRange += 1
                    if (phdelay>113): phdelay = phdelay - 50 # 113 # cannot be over 113, this is end of range
                    if (phdelay<0): phdelay = phdelay + 50 # 0 # end of range
                    phdelay=str(phdelay)
                    if delay.attrib['rm'] == '1': rm1_set = rm1_set + phdelay + ' '
                    if delay.attrib['rm'] == '2': rm2_set = rm2_set + phdelay + ' '
                    if delay.attrib['rm'] == '3': rm3_set = rm3_set + phdelay + ' '
                    if delay.attrib['rm'] == '4': rm4_set = rm4_set + phdelay + ' '
                        
            f.write(rm1+rm1_set+'\n' + rm2+rm2_set+'\n' + rm3+rm3_set+'\n' + rm4+rm4_set+'\n')
    if (outOfRange > 0): print(str(outOfRange) + " = out of range values")

def main():
    loop()

    
if __name__ == "__main__":
    for shift in range (args.start_delay, args.end_delay+1, args.delay_steps): 
        nsShift = shift
        print(nsShift)
        main()
