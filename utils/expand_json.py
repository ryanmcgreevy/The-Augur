import json
import os

json_data = []
with open("stream_dump.json") as json_file: json_data = json.load(json_file)

local_dir = os.path.join( 'context_files_dump', 'md', 'uesp')
if not os.path.exists(local_dir):
    os.makedirs(local_dir)
for file in json_data:
    url_name = file['url'].split("/")[-2] + '_' + file['url'].split("/")[-1]
    if url_name != '':
        filename = os.path.join( local_dir, url_name + '.md')
    else:
        filename = os.path.join( local_dir, 'home' + '.md')
    with open(filename, 'w') as f:
        content = file['content']
        if content != None:
            f.write(content)