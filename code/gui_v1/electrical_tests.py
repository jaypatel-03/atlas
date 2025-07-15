yarr_template = "bin/scanConsole -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json -s configs/scans/rd53b/{test} -Wh"
eye_diagram_template = "bin/eyeDiagram -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json"
qc_tool_template = "measurement-{test} -c ../configs/new_hw_config_{version}.json -m ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json"

loc_id = "OX0006"
mod_sn = "20UPGM22110039"
temp = "warm"
test = "iv_measure"
    
cmd = yarr_template.format(loc_id=loc_id, mod_sn=mod_sn, temp=temp, test="TEST1")
print(cmd)




yarr_scans = ["corecolumnscan", "std_digitalscan", "std_analogscan", "std_thresholdscan_hr", "std_totscan -t 6000"]



pixel_fail = ["std_discbumpscan", "std_mergedbumpscan -t 1500", "std_thresholdscan_zerobias", "std_noisescan", "selftrigger_source -p", "selftrigger_source"]

