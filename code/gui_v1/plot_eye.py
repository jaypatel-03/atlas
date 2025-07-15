import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
file = r"/home/jayp/atlas/OX0006/20UPGM22110561/Measurements/DATA_TRANSMISSION/2025-07-11_155140/output.log"
data = []
with open(file) as f:
    lines = f.readline()
    while not lines.__contains__("0 | "):
        lines = f.readline()
    for i in range(32):
        line = lines.replace('\n', '')
        # data = [s.replace('\n', '') for s in lines]
        parts = [x.strip() for x in line.split('|')]
        row = [float(val) for val in parts[1:-1]]
        data.append(row)
        lines = f.readline()
    # print(data)
    
plt.imshow(data, cmap='viridis')
plt.savefig('img/test.png')