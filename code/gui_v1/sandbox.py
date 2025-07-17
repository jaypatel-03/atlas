import json 
'''
file = "/home/jayp/atlas/module-qc-database-tools/OX0006/20UPGM22110561/20UPGM22110561_L2_warm.json"
with open(file, "r") as jsonfile:
    data = json.load(jsonfile)
for a in range(4):
    print(f"Chip {a}: {data['chips'][a]['enable']} ")
    
data['chips'][0]['enable'] = 0


with open(file, "w") as jsonfile:
    myJSON = json.dump(data, jsonfile)
    jsonfile.close()
    
 '''   
file = "/home/jayp/atlas/code/gui_v1/config.json"
 
config_data = {
     'default_home_path' : "",
     
} 