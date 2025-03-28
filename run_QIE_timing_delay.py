#run this script to make the new HB/HE timing xml and phase delay txt files
#example: python3 run_QIE_timing_delay.py HB reference.xml time_shift.txt start_delay end_delay delay_steps

import subprocess
import argparse

def run_command(command):
    result = subprocess.run(command, shell=True, check=True)
    return result

def main():
    parser = argparse.ArgumentParser(description="Wrapper for HB/HE Timing and Phase Delay")
    parser.add_argument("detector", choices=["HB", "HE"], help="Specify the detector (HB or HE)")
    parser.add_argument("xml_file", help="Reference QIE timing xml file")
    parser.add_argument("time_shift", help="QIE time shift")
    parser.add_argument("start_delay", type=int, help="Start of the phase delay")
    parser.add_argument("end_delay", type=int, help="End of the phase delay")
    parser.add_argument("delay_steps", type=int, help="Spacing of the phase delay")

    args = parser.parse_args()

    if args.detector == "HB":
        print ("Generating HB QIE timing...")
        run_command(f"python3 HB_timing_2025.py {args.xml_file} {args.time_shift}")

        print("Generating HB Phase Delay...")
        run_command(f"python3 HB_generate_delays.py {args.start_delay} {args.end_delay} {args.delay_steps}")

    elif args.detector == "HE":
        print ("Generating HE QIE timing...")
        run_command(f"python3 HE_timing_2025.py {args.xml_file} {args.time_shift}")

        print("Generating HE Phase Delay...")
        run_command(f"python3 HE_generate_delays.py {args.start_delay} {args.end_delay} {args.delay_steps}")


    print("Files created")

if __name__ == "__main__":
    main()

