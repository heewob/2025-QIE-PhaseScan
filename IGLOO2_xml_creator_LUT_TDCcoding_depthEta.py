import xml.etree.ElementTree as xml
from datetime import date

def indent(elem, level=0):
        from xml.etree import ElementTree as xml
'''
copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
it basically walks your tree and adds spaces and newlines so the tree is
printed in a nice way
'''
def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

# https://github.com/python/cpython/commit/63673916464bace8e2147357395fdf3497967ecb
def sort_attributes(root):
    for el in root.iter():
        attrib = el.attrib
        if len(attrib) > 1:
            attribs = sorted(attrib.items())
            attrib.clear()
            attrib.update(attribs)

data = []
with open("Lmap_ngHB_N_20200212.txt","r") as f: # read in lines of txt file, split at spaces                                                                                                   
        Lmap = f.readlines()
        lines = []
        for line in Lmap:
                lines.append(line.split())
        f.close()
        # lines is a list, each entry of the list corresponds to one line of Lmap, each entry is a list of the columns of Lmap
        del lines[0][0] # delete first element of header (#) since doesn't give data
        # create a list of dicts in order to access data by name of variable it represents
        #data = []
        for line in lines[1:]:
                data.append({lines[0][i]: line[i] for i in range(len(line))}) # creates a dictionary indexed by header row

# make a dictionary {(RBX, RM, QIE, QIECH):(Eta, Depth)} for use in the channel dependent LUT. Go over lines in data and fill this new dictionary
FE_to_Det = {}
for d in data:
        FE_to_Det[(d["RBX"],d["RM"],d["QIE"],d["QIECH"])] = (d["Eta"],d["Depth"])
        if (d["Det"] == "HBX" and d["Eta"] == "16" and d["Depth"] == "-999"): 
                FE_to_Det[(d["RBX"],d["RM"],d["QIE"],d["QIECH"])] = (d["Eta"],"4") # handle ieta 16 depth 4 so that LUT is completed still

# last TDC code in prompt range listed (t_p), indexed by [ieta][depth]
HB_tp1 = [[8,  14, 15, 17], 
         [8,  14, 15, 17], 
         [8,  14, 14, 17], 
         [8,  14, 14, 17], 
         [8,  13, 14, 16], 
         [8,  13, 14, 16], 
         [8,  12, 14, 15], 
         [8,  12, 14, 15], 
         [7,  12, 13, 15], 
         [7,  12, 13, 15], 
         [7,  12, 13, 15],
         [7,  12, 13, 15], 
         [7,  11, 12, 14], 
         [7,  11, 12, 14], 
         [7,  11, 12, 14], 
         [7,  11, 12, 7]]

HB_tp2 = [[10, 16, 17, 19], 
          [10, 16, 17, 19], 
          [10, 16, 16, 19],
          [10, 16, 16, 19],
          [10, 15, 16, 18],
          [10, 15, 16, 18],
          [10, 14, 16, 17],
          [10, 14, 16, 17],
          [9,  14, 15, 17],
          [9,  14, 15, 17],
          [9,  14, 15, 17],
          [9,  14, 15, 17],
          [9,  13, 14, 16],
          [9,  13, 14, 16],
          [9,  13, 14, 16],
          [9,  13, 14, 9]]

def buildPerHBtree(CFGBrickset, RBX="HB0"):
  CFGBrick = xml.SubElement(CFGBrickset, "CFGBrick")

  Parameter = xml.SubElement(CFGBrick, "Parameter", type="string", name="INFOTYPE")
  Parameter.text = "HBTDCLUT"

  Parameter2 = xml.SubElement(CFGBrick, "Parameter", type="string", name="CREATIONSTAMP")
  Parameter2.text = date.today().strftime("%Y-%m-%d") #"2020-9-7"

  Parameter3 = xml.SubElement(CFGBrick, "Parameter", type="string", name="CREATIONTAG")
  Parameter3.text = "HBTestTag"

  Parameter4 = xml.SubElement(CFGBrick, "Parameter", type="string", name="RBX")
  Parameter4.text = RBX

  rm = []
  rm.extend(range(1,6))
  
  for irm in rm:
        qie_board = []
        n_qie_board = 4
        if irm == 5:
                n_qie_board = 1
        qie_board.extend(range(1,n_qie_board+1)) # QIE boards 1-4 for RM 1-4, and only one QIE board on calibration unit (RM = 5)
        qie_channel = []
        qie_channel.extend(range(1,17)) # channels 1-16 on each QIE board

        for board in qie_board:
                for channel in qie_channel:
                        qie = (board - 1) * 16 + channel
                        Data = xml.SubElement(CFGBrick, "Data", qie="%s"%(str(qie)), rm="%s"%(str(irm)), elements="1", encoding="hex")
                        
                        if (irm == 5):
                            t_p1 = 10
                            t_p2 = 12
                        else:
                            eta, depth = FE_to_Det[(RBX, str(irm), str(board), str(channel))]
                            t_p1 = HB_tp1[int(eta)-1][int(depth)-1]
                            t_p2 = HB_tp2[int(eta)-1][int(depth)-1]

                        error_code = "11"
                        delay1 = "01"
                        delay2 = "10"
                        prompt = "00"

                        binary_encoding = error_code*14 + delay2*(49-t_p2) + delay1*(t_p2 - t_p1) + prompt*(t_p1 + 1)
                        binary_encoding = [binary_encoding[i:i+32] for i in range(0,len(binary_encoding), 32)] # split into 4 groups
                        # convert binary string to decimal representation (specifing base 2), then call string format to return hexadecimal string, and pad up to 8 hex digits
                        Data.text = str.format('0x{:08x}', int(binary_encoding[0],2)) + " " + str.format('0x{:08x}', int(binary_encoding[1],2)) + " " + str.format('0x{:08x}', int(binary_encoding[2],2)) + " " + str.format('0x{:08x}', int(binary_encoding[3],2))

  sort_attributes(CFGBrick)



'''
function to build an example tree containing cars and ships
CFGBrickset is the root node
'''

def buildTree(site="904"):

  CFGBrickset = xml.Element("CFGBrickset")

  if site=="904":
        RBXList = ["HB0", "HB1", "HB2", "HB3", "HB4", "HB5"]
  elif site=="P5":
        i = 1
        RBXList = []
        while i < 19:
                if i < 10:
                        RBXList.append("HBP0%d" %i)
                        RBXList.append("HBM0%d" %i)
                else:
                        RBXList.append("HBP%d" %i)
                        RBXList.append("HBM%d" %i)
                print ("Appending HBP/HBM", i)
                i = i+1
  for rbx in RBXList:
        buildPerHBtree(CFGBrickset, rbx)

  indent(CFGBrickset)

  tree = xml.ElementTree(CFGBrickset)

  tree.write("HBTDCLUT_prompt_delayed_v2_%s.xml" %site, xml_declaration=True, encoding='utf-8', method="xml")

'''
main function, so this program can be called by python program.py
'''
if __name__ == "__main__":
  #buildTree()
  buildTree("P5")
