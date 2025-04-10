1. What does the files do?
 
 - `HBTDCLUT-HB_TDC_2024_v1.xml` is the original TDCLUT. This wasn't changed for 2025 May phase scan. This can be found on http://hcalmon.cms/xmldbweb/viewxml/4/
 -  `Lmap_ngHX_N_20200212.txt` is the Lmap for each subdetectors.
 - `phaseTuning_HB_2024_v2.xml` and `phaseTuning_HE_2024_Jul.xml` were the phase scan setting for 2024 (http://hcalmon.cms/xmldbweb/viewxml/1/). This will be used as the 'reference setting' for the new 2025 phase scan setting.
 - `HB_QIEphase_adjustment_relativeTo2024_2025v1.txt` and `HE_QIEphase_adjustment_relativeTo2024_2025v1.txt` are the new phase adjustments.
 - `HB_timing_2025.py` and `HE_timing_2025.py` takes in the reference scan setting and the new adjustments and make the new phase scan settings.
 - `HB_generate_delays.py` and `HE_generate_delays.py` takes in the new phase scan setting and generates txt files of delays.
 - `IGLOO2_xml_creator_LUT_TDCcoding_depth.py` makes LUT xml file.
 - `run_QIE_timing_delay.py` is a wrapper code that runs `HX_timing_2025.py` and `HX_generate_delays.py`.
 - `scan_fine.py` is used for the phase scan.

2. How to make the phase scan setting xml and delay files

run `run_QIE_timing_delay.py` with the substructure, reference xml, phase shift, start delay, end delay, delay steps as the input.
- example: `python3 run_QIE_timing_delay.py HB reference.xml time_shift.txt start_delay end_delay delay_steps`

3. How to upload the new configuration files on CFGgit

- First, log into cmsusr(P5) and check if you are subscribed to hcalcgf by typing “id”. Copy the new scan settings, delay files, and `scan_fine.py` in your personal P5 account.
  Before uploading the changes in CFGgit, check the current QIE and LUT. Log into HCAL PC and connect to the ngCCM, for HB: `ssh hcalngccm03` then `hgFEC.exe -p 64400`, for HE: `ssh hcalngccm02` then `ngFEC.exe -p 64000`.
  From there, you can enter `get` commands like below to check the current QIE and LUT. (Note that you should be VERY CAREFUL when setting new values with the `put` or `tput` command.)

```
get HBM10-1-QIE[1-64]_PhaseDelay
get HBM06-1-Qie[1-64]_TDCLUT
get HEP02-1-QIE[1-48]_PhaseDelay
```

- Second, make changes in CFGgit. If this is your first time, follow this.
```
git clone /hcalrun/hcalrun/HcalCfg
cd HCalCfg
git checkout pro
```
If you have this repository already, make sure to git pull first.
```
cd HcalCfg
git fetch
git pull origin pro
```
Now we can make changes in the CFGgit files. Edit lines in Master/global.xml and RBX/ngSettings.cfg to have the new scan setting files and uMNio word. 
Reference commit log (http://hcalmon.cms/cgit/HcalCfg/commit/?id=ac11ad5097c823f5937fb31b6f7c79ee6859523b). After making the change, push the change.

- Third, check if the change is applied.
Reconfigure pick up the new setting - just reset and configure when we are in local.
Do `get` phase delay and TDCLUT to see if the change is applied.

4. Run the phase scan

Connect to HCAL PC and open a tmux session. Use scan_fine.py to scan with each point for 600 seconds.
```
ssh hcalngccm03
tmux new -s 2025Scan
python2 scan_fine.py --seconds 600 --cycles -1 --hb --he --logfile 2025Scan.txt | tee output_2025_scan.txt
```
After detatching from tmux (Ctrl+B and D), reattach with tmux attach-session -t 2025Scan.

During the phase scan, be connected to P5 shifter zoom at all times.
You can find a detailed guide to phase scan [here](https://github.com/gk199/QIE_PhaseScan/blob/main/QIE_Scan.md)

5. Lastly, revert the config to original
