import os
dir = "test_table"
for filename in os.listdir(dir):
   path = os.path.join(dir, filename)
   with open(path, 'r') as f:
      lines = f.readlines()

   with open(path, "w") as f:
    for line in lines:
        if "(javascript:collapseTable\(0\)" not in line:
            f.write(line)
        else:
           f.close()
           break 