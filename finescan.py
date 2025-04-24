#!/usr/bin/env python

def settings(nCycles=1, debug=False):
    out = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
#    out = [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 111, -10, -9, -8, -7, -6, -5, -4, -3]
#    out = [0, -10, 20]
#    out = [-4, -2, 0, 2, 4, 6, 8, 10]
#    out = [2]
    return out


def commands(setting, subdet, put=False):
    out = []

    # GK - would need to add HE functionality here too 
    if subdet == "HB" or subdet == "HE":
        c = 'delays_apriltest/' + str(setting) + 'ns_' + str(subdet) + '.txt'
        print(c)
        out.append(c)
    else:
        print("Subdetector %s is not supported." % subdet)
        return out
    try:
        open(c)
    except FileNotFoundError:
        print("File does not exist: ", c)

    return out

def test():
    for s in settings(debug=True):
        print(commands(s, "HB", put=True))
    
if __name__ == "__main__":
    test()
    #settings(nCycles=1, debug=True)
