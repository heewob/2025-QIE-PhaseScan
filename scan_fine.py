#!/usr/bin/env python

import argparse, time
import fec_jm_fine, umnio
#import qie11_phases, tdc_thresholds
import finescan, tdc_thresholds
import datetime

start = time.time()

def applySetting(module, setting, subdet, client, host, port, test_mode, logfile=None):
    #cmds  = module.commands(setting, subdet, put=True)
    #cmds += module.commands(setting, subdet, put=False)
    cmds = module.commands(setting, subdet, put=True)

    f = 'delays_apriltest/' + str(setting) + 'ns_' + str(subdet) + '.txt' # GK would need to label files by HE or HB

    if test_mode:
        fec_jm_fine.onlyLog(client, host, port, cmds, logfile, file_script = f)
    else:
        fec_jm_fine.sendAndLog(client, host, port, cmds, logfile, file_script = f)

def parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", help="code written to uMNio during change of setting", metavar="N", type=int, default=999)
    parser.add_argument("--cycles", help="number of cycles (negative will permanently loop)", type=int, default=1)
    parser.add_argument("--hb", help="scan HB settings", action="store_true", default=False)
    parser.add_argument("--he", help="scan HE settings", action="store_true", default=False)
    parser.add_argument("--hf", help="scan HF settings", action="store_true", default=False)
    parser.add_argument("--zdc", help="scan ZDC settings", action="store_true", default=False)
    parser.add_argument("--logfile", help="log file to append to", default="scan_log.txt")
    parser.add_argument("--ngfec-exe", help="use this program to communicate with the server", default="/nfshome0/hcalpro/ngFEC/ngFEC.exe")
    parser.add_argument("--seconds", help="number of seconds to sleep per setting", type=int, default=300)
    parser.add_argument("--tdc-threshold", help="Scan TDC threshold rather than phase", action='store_true', default=False)
    parser.add_argument("--test-mode", help="Don't interact with hardware", action='store_true', default=False)
    return parser.parse_args()


def main(args):
    module = tdc_thresholds if args.tdc_threshold else finescan

    while args.cycles:
        i=0
        for setting in module.settings():
            logfile = open(args.logfile, "a")
            print("Looping over settings, with time = " + str(time.time() - start))
            print("Writing value %d to uMNIO." % args.code)

            if not args.test_mode:
                umnio.write_setting(args.code)

            print("Applying setting: %d" % setting)
            
            if args.hb:
                applySetting(module, setting, "HB", args.ngfec_exe, "hcalngccm03", 64400, args.test_mode, logfile=logfile)
            if args.he:
                applySetting(module, setting, "HE", args.ngfec_exe, "hcalngccm02", 64000, args.test_mode, logfile=logfile)
            if args.hf:
                applySetting(module, setting, "HF", args.ngfec_exe, "hcalngccm01", 63000, args.test_mode, logfile=logfile)
            if args.zdc:
                applySetting(module, setting, "ZDC", args.ngfec_exe, "hcalngccm01", 63000, args.test_mode, logfile=logfile)

            print("Writing value %d to uMNIO." % setting)
            if not args.test_mode:
                umnio.write_setting(setting)

            print("...sleeping")
            
            time.sleep(args.seconds)

            logfile.write("Writing value %d to uMNIO." % setting)
            logfile.write("at  "+str(datetime.datetime.now()))
            logfile.write("############################################\n")
            logfile.close()

        args.cycles -= 1
        logfile = open(args.logfile, "a") # added logfile line
        print("Reverting to default QIE phases") # added logfile line 
        #        applySetting(module, "0", "HB", args.ngfec_exe, "hcalngccm03", 64400, args.test_mode, logfile=logfile)
        applySetting(module, "0", "HB", args.ngfec_exe, "hcalngccm03", 64400, args.test_mode, logfile=logfile)
        applySetting(module, "0", "HE", args.ngfec_exe, "hcalngccm02", 64000, args.test_mode, logfile=logfile)
        # GK: would need to add applySetting for HE line as well here
        logfile.close() # added logfile line 

        if not args.test_mode:
            umnio.write_setting(0)

if __name__ == "__main__":
    args = parsed_args()
    try:
        main(args)
    except KeyboardInterrupt:
        pass

    if not args.test_mode:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Settings are still at the final scan value.")
        print("Configure a run to restore to default values.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
