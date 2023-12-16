import os
from multiprocessing import Pool
from shutil import copy
import re

class Converter:
    def __init__(self, vault_path, dest_folder):
        self.md_files = []
        self.images = []
        self.vault_path = vault_path
        self.dest_folder = dest_folder

    def parseFile(self, parallel = False):
        # simply collect all of the files up into the respective lists.
        self.traverse()
        self.convert(parallel)

    def convert(self, parallel):

        # copy images into dest folder in its own subfolder
        image_dest_folder = os.path.join(self.dest_folder, "Images")
        os.mkdir(image_dest_folder)

        for img_file in self.images:
            copy(img_file, image_dest_folder, True)

        # create sub Dir for html files
        os.mkdir(os.path.join(self.dest_folder,"Notes"))

        # Process the Files
        if parallel:
            with Pool() as p:
                p.map(self.format, self.md_files)
        else:
            for md_file in self.md_files:
                self.format(md_file)


    def traverse(self):
        for root, dirs, files in os.walk(self.vault_path):
            for file in files:
                if file.endswith(".md"):
                     self.md_files.append(os.path.join(root, file))
                elif file.endswith(".png"):
                    self.images.append(os.path.join(root, file))


    def format(self, md_filePath):
        title = os.path.basename(md_filePath)
        title = title.split(".")[0]
        html_dir = os.path.join(self.dest_folder,"Notes",f"{title}.html")
        html_file = open(html_dir,"w")

        # obtain a file handle
        with open(md_filePath,"r") as md_file:
            # initialize the html file with boilerplate
            html_file.write(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>{title}</title>
</head>
<body>""")
            
            # note: The triple quote """ strings don't need newline chars. 
            # It keeps the string as it looks in code.
            
            for line in md_file:
                line = self.formatLine(line,r"\[\[.+?\]\]")
                html_file.write(line)

            # add md-block script and close body and html tag
            html_file.write(f"""<script type="module" src="https://md-block.verou.me/md-block.js"></script>
                            </body>
                            </html>""")
            
        html_file.close()

    def formatLine(self, line, regexp):
        # Works well. Lets hope someone doesnt end a name of an md file with .png
        while( re.search(regexp, line) != None):
            image_match = re.search(regexp, line)
            match_pos = image_match.span()
            tag_content = line[match_pos[0] + 2 : match_pos[1] - 2]

            if tag_content.endswith(".png"):

                tag = f'<img src = "{os.path.join("Images",tag_content)}"></img>'
                line = line[:match_pos[0]-1] + tag + line[match_pos[1]:]
                # The -1 to the start index is to nab the ! from image tags
            else:
                tag = f'<a src = "{os.path.join("Notes",tag_content)}"></a>'
                line = line[:match_pos[0]]+ tag + line[match_pos[1]:]
            
            
        return line

        
        




