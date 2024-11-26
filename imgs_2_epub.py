# Import required modules.
import os
import time
import shutil
import sys
import itertools
from PIL import Image
from datetime import datetime
import uuid
import zipfile
import threading

debug = True # Set to True for debug prints.

settings={} # Create settings dict.

def roman(int): ## Turn any int into roman numeral (for pre-pages).
    
    # Create Lists for roman numerals.
    m = ["", "m", "mm", "mmm"]
    c = ["", "c", "cc", "ccc", "cd", "d", "dc", "dcc", "dccc", "cm"]
    x = ["", "x", "xx", "xxx", "xl", "l", "lx", "lxx", "lxxx", "xc"]
    i = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix"]
    
    # Do some math and get roman numerals (I don't remember how it works).
    thous = m[int // 1000]
    hunds = c[(int%1000)//100]
    tens = x[(int%100)//10]
    ones = i[int%10]

    return (thous+hunds+tens+ones) # Return roman numeral

# Create varaibles for threaded loading messages.
processDone = False
loadmsg=""
donemsg=""

def loadPrint():## Animated 'loading...' messages.

    for frame in itertools.cycle(["...", "   ", ".  ", ".. "]): # For each animation frame:

        if processDone: # Check if loading is done:

            # If so, write last print and break.
            sys.stdout.write(("\r"+loadmsg+"..."))
            sys.stdout.flush()
            break

        # Otherwise, print current animation frame and wait.
        sys.stdout.write(("\r"+loadmsg+frame))
        sys.stdout.flush()
        time.sleep(0.1)

    sys.stdout.write("\n"+donemsg+"\n") # One done (break-ed), print done message.

def startLoadPrint(msg): ##Set all load-print variables, then start.
    
    # Get vars.
    global processDone
    global loadmsg
    
    # Set to not done, load msg as the msg.
    processDone = False
    loadmsg = msg
    
    # Start thread, start animation.
    anim = threading.Thread(target=loadPrint)
    anim.start()
    
def endLoadPrint(msg): ## Get load-print variables and end animation.
    
    # Get vars.
    global processDone
    global donemsg
    
    # Set to done, donemsg to msg, then sleep.
    donemsg = msg
    processDone = True
    time.sleep(0.2)

while True: ## Get filepaths from user.
    
    # Tell user the current path.
    print(f"\nCurrent Path - {os.path.dirname(os.path.realpath(__file__))}")
    
    while True: # Get the ePUB path.
        
        # Prompt user for desired path, set to "ePUB_path" in dict.
        settings.update({"ePUB_path": input("\nWhere do you want the file to be"
                                            +" created? (Leave blank for "+
                                            "current path): ")})
        
         # Debug Print - ePUB Path Input
        if debug == True: print("ePUB PATH IN: "+settings["ePUB_path"]) 
        
        # If the path is blank, set it to the current path and break.
        if(settings["ePUB_path"] == ""):
            settings.update({"ePUB_path": os.path.dirname(
                os.path.realpath(__file__))})
            break
        
        # If the path doesnt exist, is invalid, or otherwise inaccessable, reprompt.
        elif (os.path.exists(settings["ePUB_path"]) == False):
            print("\nPath is invalid!")
            
        else: break # If path is good and not blank, break.
    
    if debug == True: print("ePUB PATH: "+settings["ePUB_path"]) # Debug Print - Set ePUB Path
    
    while True: # Get the image path and make sure it has images.
        
        while True: # While true, prompt for image path.
            
            settings.update({"img_path": input("\nWhere are your images stored?"
                                               +" (Leave blank for current"
                                               +" path): ")}) # Prompt user.
            
            # Debug Print - Image Path Input
            if debug == True: print("IMAGE PATH IN: "+settings["img_path"])
            
            # If the image path is blank, set to current directory and break.
            if(settings["img_path"] == ""):
                settings.update({"img_path": os.path.dirname(os.path.realpath(__file__))})
                break
            
            # If path invalid, reprompt.
            elif (os.path.exists(settings["img_path"]) == False):
                print("\nPath is invalid!")
                
            else:break # If path good, break.

        # Debug Print - Current Image Path
        if debug == True: print("IMAGE PATH SAVE: "+settings["img_path"])
        
        print("\nStarting search\n") # Update user.
        
        startLoadPrint("Searching for images") # Start loading print.
        
        if debug == True: print("FILES IN PATH: "+str(os.listdir(
            settings["img_path"]))) # Debug Print - All Files In Img Path
        
        imgs = [f for f in os.listdir(settings["img_path"]) if (
            f[:-4].replace(".", "").replace("img_", "")).isdigit()]
        # Filter files in image path:
        # - Remove last 4 characters from file, along with removing periods 
        #   (remove file extension)
        # - Remove 'img_' (Set file to just number)
        # - If file is a digit, keep it (Only proper filenames will stay in, 
        #                                others will not be considered)

        if len(imgs) == 0: # If no proper images are found, reprompt.
            
            endLoadPrint("\nCould not find any images! Make sure your images "
                         +"are in the image path.")
            
        else: # If images are found, end load print, give images to sorted list.
            
            endLoadPrint(f"\n{str(len(imgs))} images found!") # End load, udpate user.
            
            if debug == True: print("UNSORTED IMAGES: "+str(imgs)) # Debug Print - Unsorted Images
            
            # Sort images by number.
            imgs.sort(key=lambda f: int(f[:-4].replace(".", "").replace("img_"
                                                                        , "")))
            
            if debug == True: print("SORTED IMAGES: "+str(imgs)) # Debug Print - Sorted Images
            
            print(f"\nPaths set to:\nFile Path - {settings['ePUB_path']}!"
                  +"\nImage Path - {settings['img_path']}!") # Update user.
            
            break # Break.
    
    break # Leave path setting.

def promptMeta(tochange, question, good, bad, invalidMsg): ## Prompt user for metadata.
    
    while True:
        
        response = input(question) # Prompt user, save to response.
        
        # Debug Print - Meta And Response
        if debug == True: print(f"META {tochange} RESPONSE {response}") 
        
        # If message is bad, beat user with sticks.
        if (bad != False) and (response in bad or response == bad):print(invalidMsg)
        
        # If message is not good, beat user with sticks.
        elif (good != False) and (response not in good):print(invalidMsg)
        
        else: # Otherwise, set metadata to response.
            
            settings.update({tochange:response}) # Update metadata.
            
            # Debug Print - Meta Changed
            if debug == True: print(f"META {tochange} SET VALID {response}")
            
            break # Break.

# Prompt user for desired filename.
promptMeta("filename", 
           "\nePUB File Name (Ex: 'My_Book', 'scott_pilgrim_1.ePUB'): ", False, 
           ("", "/", "<", ">", ":", "\\", "|", "?", "*"), "\nFile name is blank"
           +" or contains invalid characters. Please provide a file name.")

# Propmpt user for title of ePUB.
promptMeta("title", "\nWhat's the title of your book (Ex: Scott Pilgrim, Vol 1:" 
           +" Precious Little Life): ", False, "",
           "\nTitle cannot be blank. Please provide a title.")

# Prompt user for language.
# [TO-DO: Verify supplied tag is well-formed.]
promptMeta("lang",
           "\nWhat language is your book in? MUST be well-formed language tag."
           +" (Look here for tags: https://r12a.github.io/app-subtags/)\n"       
           +"(Leave blank for default, 'en-US'): ", False, False,
           "\nInvalid language tag!")

if settings["lang"] == "": settings.update({"lang":"en-US"}) # If blank, set to en-US.

# Prompt user for last modified date.
promptMeta("dateMod", "\nWhen is the 'last modified' date?"
           +" (Time must be in UTC format!) (Leave blank for current time): ",
           False, False, "\nInvalid date modified!")

if settings["dateMod"] == "": settings.update({"dateMod": datetime.now(). # If blank, set to now.
                                               strftime("%Y-%m-%dT%H:%M:%SZ")})
# Prompt for identifier.
promptMeta("identifier", "\nPlease provide a unique identifier for your ePUB "
           +"(Ex: UUID, DOI, ISBN)\nFor custom identifiers, "
           +"include the type at the beginning of the identifier "
           +"(EX: isbn:#####)\n(Leave blank for random UUID): ", False, False, 
           "\nInvalid Identifier!")

# If blank, create random UUID.
if settings["identifier"] == "": settings.update({"identifier": "uuid:"+
                                                  str(uuid.uuid4())})

while True:
    # Prompt user for page start.
    # [TO-DO: Make it more clear what the hell it means.]
    promptMeta("pageStart", "\nWhat does your book consider 'Page 1'? "
               +"(0 = Cover, 1 = 'Page 1', etc.): ", False, False,
               "\nInvalid page!")
                                                                        
    if settings["pageStart"].isdigit() == True: break # If the answer is a number, go ahead.
    
    else: print("\nInvalid Page!") # Otherwise, definetely invalid, so reprompt.
    
settings.update({"pageStart": int(settings["pageStart"])-1}) # Set answer to dict.

# Prompt user for legacy compatability.
promptMeta("legacy", "\nWould you like to enable legacy compatability? "
           +"(May be needed for old ePUB readers) (y/n): ", ("y", "n"), False,
           "\nInvalid choice! Please type 'y' or 'n'.")

# Prompt user for table of contents.
promptMeta("toc", "\nWould you like a table of contents? (y/n): ", ("y", "n"),
           False, "\nInvalid choice! Please type 'y' or 'n'.")

settings.update({"chapters": []}) # Prepare chapter list and chapter name list (to prevent crashes).
settings.update({"chapName": []})

if settings["toc"] == "y": # If the user wants the TOC, do following.
    
    while True:
    
        while True:
            
            # Ask what page the current chapter starts on.
            chapter = input("\nWhat page does Chapter "
                            +str(len(settings["chapters"])+1)
                            +" start? (Leave blank to end): ")
            
            if debug == True: print("CHAPTER: "+chapter) # Debug Print - Chapter Number
            
            if chapter != "": # If chapter is not blank:
                
                if chapter.isdigit(): # If the input is a digit:
                
                    if chapter == "0":                        # If the page is 0, append cover page.
                        settings["chapters"].append("cover")
                    
                    else: settings["chapters"].append("pg_"+chapter) # Otherwise, append page.
                    
                else: print("\nNot a page!") # If not digit, invalid.
            
            else: break # If blank, leave loop.
        
        break 
    
    if debug == True: print("CHAPTERS: "+str(settings["chapters"])) # Debug Print - Chapters List.

    # Prompt user for custom chapter names.
    if len(settings["chapters"]) > 0: promptMeta(
        "chapName", "\nWould you like to give your chapter custom names? "
        +"(y/n): ", ("y", "n"), False, 
        "\nInvalid choice! Please type 'y' or 'n'.")

    settings.update({"chapterNames": []}) # Prepare chapter names list (to prevent crashes). 
    
    if settings["chapName"] == "y": # If user wants custom chapter names:
        
        for i in range(len(settings["chapters"])): # Index through chapters,
            
            name = input("\nPlease give a custom name to Chapter "+str(i+1) # Prompt for name.
                         +" (Leave blank to skip): ")
            
            if name != "": settings["chapterNames"].append(name) # If not blank, apply name.
            
            # Otherwise, keep 'Chapter #'.
            else: settings["chapterNames"].append("Chapter "+str(i+1))
            
    else:
        # If not chapter names, keep default.
        for i in range(len(settings["chapters"])):
            settings["chapterNames"].append("Chapter "+str(i+1))

# Prompt for# reading dir.
promptMeta("dir", "\nWhich way should your ePUB be read? (Left-to-right for "
           +"english and similar languages) (ltr/rtl): ", ("ltr", "rtl"), False,
           "Not a direction! Please type 'ltr' or 'rtl'")

# Prompt for optional meta.
promptMeta("optionalMeta", "\nWould you like to include additional metadata, "
           +"such as authors?\n(It is heavily reccommended to add this metadata"
           +" in in a seperate app like Calibre or Sigil instead)\n(y/n): ",
           ("y", "n"), False, "Please put 'y' or 'n'.")

# Create directory indexes for all optional meta to prevent crashes
settings.update({"titleSort": ""})
settings.update({"authors":[]})
settings.update({"authorSort":[]})
settings.update({"authorAltScript":[]})
settings.update({"contributors":[]})
settings.update({"contributorSort":[]})
settings.update({"contributorAltScript":[]})
settings.update({"pubdate":""})
settings.update({"publisher":""})
settings.update({"desc":""})

if settings["optionalMeta"] == "y": # If user wants optional metadata, do the following.
    
    settings.update({"titleSort": input(
        "\nHow should your title be sorted? (Ex: The Lord of the Rings -> " # Prompt for title sort.
        +"Lord of the Rings, The)\n(Leave blank to skip): ")})
    
    if debug == True: print("TITLE SORT: "+settings["titleSort"]) # Debug Print - Title Sort
    
    while True:
        
        auth = input("\nWho is an author of the book? (Person/Company that " # Prompt for authors.
                     +"played a primary role in the creation of the book)\n"
                     +"(Leave blank to skip/end): ")
        
        if debug == True: print("AUTH: "+auth) # Debug Print - Added Author
        
        if auth == "": break # If left blank, skip.
        
        else: settings["authors"].append(auth) # If not blank, add to authors.
    
    if debug == True: print("AUTHOR LIST: "+settings["authors"]) # Debug Print - Author Lists
    
    if len(settings["authors"]) > 0: # If the author list is longer than 0:
        
        for i in range(len(settings["authors"])): # Index through authors
            
            while True:
                
                # Prompt for author name sort.
                settings["authorSort"].append(
                    input("\nFor each author, provide a sort name\n"
                          +"(Ex: Brian Lee O'Malley -> O'Malley, Bryan Lee)"
                          +"\nCurrent Author is "
                          +f"{str(settings['authors'][i])}: "))
                
                # Debug Print - Author Sort Input
                if debug == True: print("AUTHOR SORT: "+settings["authorSort"])
                
                # If blank, reprompt.
                if settings["authorSort"] == "": print("\nPlease provide an "
                                                       +"author sort.")
                
                else: break # Otherwise break.
                
    if len(settings["authors"]) > 0: # If there are any authors present:
        
        for i in range(len(settings["authors"])): # Index through authors,
            
            while True:
                
                altScript = input( # and prompt for alt scripts.
                    "\nFor each author, you may provide an alt script "
                    +"(Ex: 'Hirohiko Araki, en' -> '荒木 飛呂彦, jp')\n"
                    +"(Leave blank to skip author): ").replace(" ", "")
                
                if debug == True: print("ALT SCRIPT: "+altScript) # Debug Print - Alt Script Add
                
                # If a comma is not present, reprompt (attempt to guarantee Name, Tag format).
                # [TODO: Make a better system.]
                if "," not in altScript: print("\nInvalid Alt-Script!")
                
                # If alt script is valid, append to list and break.
                else:
                    settings["authorAltScript"].append(altScript)
                    break
                
            if debug == True: print("ALT SCRIPTS: " # Debug Print - All Alt Scripts
                                    +settings["authorAltScripts"])
            
    while True:
        
        contributor = input( # Prompt for contributors.
            "\nIs there a contributor of the book? (Person/Company that played"
            +" a secondary role in book creation)\n(Leave blank to skip/end): ")
        
        # Debug Print - Contributor Add
        if debug == True: print("CONTRIBUTOR: "+settings["contributor"]) 
        
        # If blank, leave.
        if contributor == "": break
        
        # Otherwise, append contributor to list.
        else: settings["contributors"].append(contributor)
        
    if debug == True: print("CONTRIBUTORS: "+settings["contributors"]) # Debug Print - Contributors
    
    if len(settings["contributors"]) > 0: # If any contributors added:
        
        for i in range(len(settings["contributors"])): # Index through contributors, 
            
            while True:
                
                settings["contributorSort"].append(input( # Prompt for contributor sorts.
                    "\nFor each contributor, provide a sort name\n"
                    +"(Ex: Brian Lee O'Malley -> O'Malley, Bryan Lee)\n"
                    +f"Current Contributor is {settings['contributors'][i]}: "))
                
                if debug == True: print("CONTRIBUTOR SORT: " # Debug Print - Contributor Sort Add
                                        +settings["contributorSort"])
                
                if settings["contributorSort"] == "": # If no sort is given, reprompt.
                    print("\nPlease provide an contributor sort.")
                    
                else: break # Otherwise break.
                
    if len(settings["contributors"]) > 0: # If any contributors added:
        
        for i in range(len(settings["contributors"])): # Index through contributors.
        
            while True:
        
                altScript = input( # Prompt for alt-script.
                    "\nFor each contributor, you may provide an alt script "
                    +"(Ex: Hirohiko Araki, en -> 荒木 飛呂彦, jp)\n"
                    +"(Leave blank to skip contributor): ").replace(" ", "")
                
                if debug == True: print("CONTRIBUTOR ALT: "+altScript) # Debug Print - Alt Script
                
                # If no comma, invalid (attempt to enforce format)
                # [TODO: Fix this also.]
                if "," in altScript != True: print("\nInvalid Alt-Script!")
                
                else: # Otherwise, append to list.
                    settings["contributorAltScript"].append(altScript)
                    break
                
            if debug == True: print("CONTR. ALT SCTIPTS: " # Debug Print - Contributor Alt Scripts
                                    +settings["contributorAltScripts"])
            
    # Prompt for publisher.
    settings.update({"publisher": input("\nDoes your book have a publisher? "
                                        +"(Leave blank to skip): ")})
    
    if debug == True: print("PUBLISHER: "+settings["publisher"]) # Debug Print - Publisher Add
            
    settings.update({"pubdate": input( # Prompt for publication date.
        "\nWhen was the publication date of your book? "
        +"(Please write in UTC format)\n(Leave blank to skip): ")})
    
    if debug == True: print("PUBLICATION DATE: "+settings["pubdate"]) # Debug Print - Publication
    
    # Prompt for description.
    settings.update({"desc": input("\nIf you would like to add a description, "
                                   +"write it here (Leave blank to skip): ")})
    
    if debug == True: print("DESCRIPTION: "+settings["desc"]) # Debug Print - Description Add
    
### CREATE DIRECTORIES

print("\nMetadata gathered, starting filemaking proccess\n") # Update user.

startLoadPrint("Creating directories") # Start loading animation.

## MAIN DIRECTORY

def create_directory(path): # Create directory function.
    
    global donemsg # Bring in global variables.
    global processDone
    
    if not os.path.exists(path): # If the requested path doesn't already exist:
    
        try: # Try to make directory, and Debug Print - Directory Created
    
            os.makedirs(path)
            if debug == True: print(f"DIR {path}")
    
        except Exception as error: # If any error occurs:
            
            # Print error to user and quit.
            endLoadPrint(f"\nDirectory {path} can't be created."
                         +f" Reason: {error}")
    
            quit()
    
    else: # If the path already exists, Debug Print - Directory Exists
    
        if debug == True: print(f"{path} PRESENT")

def create_file(path, write): # Create file function.
    
    global donemsg # Bring in global variables.
    global processDone
    
    try:
        with open((path), "a") as file: # Try to open/create file and write to it.
    
            file.write(write)
    
        if debug == True: print (f"FILE {path}") # Debug Print - File Created
    
    except Exception as error: # If error occurs, print to user and quit.
    
        endLoadPrint(f"\File {path} can't be created. Reason: {error}")
    
        quit()

# Create ePUB file directory.
create_directory(os.path.join(settings["ePUB_path"], settings["filename"]))

create_file(os.path.join( # Create mimetype file.
    settings["ePUB_path"], settings["filename"],"mimetype"), 
            "application/ePUB+zip")

create_directory(os.path.join( # Create META-INF directory.
    settings["ePUB_path"], 
    settings["filename"], "META-INF"))

create_directory(os.path.join(settings["ePUB_path"], # Create OEBPS directory.
                              settings["filename"], "OEBPS"))

create_directory(os.path.join(settings["ePUB_path"], # Create OEBPS/images directory.
                              settings["filename"], "OEBPS", "images"))

endLoadPrint("\nDirectories Created!\n") # End loading animation.

### COPY IMAGES

startLoadPrint("Copying images") # Start loading animation.

for i in range(len(imgs)): # Index through images.
    
    shutil.copy(os.path.join(settings["img_path"],imgs[i]), # Copy images from image path to images
                os.path.join(settings["ePUB_path"], settings["filename"],
                             "OEBPS","images"))
    
    if debug == True:print(f"COPY {imgs[i]} ") # Debug Print - Image Copied

endLoadPrint("\nImages Copied!\n") # End loading animation

### FILES

## XHTML FILES + DYNAMIC CODE FOR OTHERS

# Create base code for stylesheet (dynamic code will be added later, this code is consistent).
stylesheet = """html, body {
    height:100%;
    overflow:hidden;
    background-color: #fff;
}

img {
    max-width:100%;
    max-height:100%;
}"""

# Base navigation code (dynamic parts added later, this code is consitent).
navigation = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:ePUB=\"http://www.idpf.org/2007/ops\">
<head>
    <title>{settings['title']}</title>
    <link rel=\"stylesheet\" href=\"stylesheet.css\" type=\"text/css\"/>
    <meta charset=\"utf-8\"/>
</head>
<body>
    <nav xmlns:ePUB=\"http://www.idpf.org/2007/ops\" role=\"doc-toc\" ePUB:type=\"toc\" id=\"toc\">
        <ol>"""

pagelist = [] # Create pagelist.

manifestXHTML = "" # Create blank strings for the manifest and spine.
spine = ""

startLoadPrint("Creating files") # Start loading.

for i in range(len(imgs)): # Index through image list.

    pageImg = Image.open(os.path.join(settings["ePUB_path"], # Open each image w/ PIL.
                                      settings["filename"],"OEBPS","images",
                                      imgs[i]))

    if pageImg.format == "JPEG": mediatype = "jpeg" # Check for filetype and set mediatype
    elif pageImg.format == "PNG": mediatype = "png" # accordingly.
    elif pageImg.format == "GIF": mediatype = "gif"
    elif pageImg.format == "WebP": mediatype = "webp"
    
    page_num = i # Set page number to current index.
    
    width, height = pageImg.size # Set with and height to the image's width and height.
    
    page_num -= int(settings["pageStart"]) # Offset the page number by the 'pageStart' setting.
    
    if i == 0: # If this is the first indexed image, it is the cover.
        
        title = "Cover" # Set title accordingly.
        
        file_name = "cover.xhtml" # Set filename accordingly.
        
        # Create XHTML for the cover page.
        xhtml_code = f"""
<body class=\"body_cover\">
    <div class=\"image_cover\">
        <img src=\"images/{imgs[i]}\" alt=\"Cover\"/>
    </div>
</body>"""

        # Create stylesheet code for the cover.
        stylesheet += f"""
body.body_cover {{
	width: {str(width)}px;
	height: {str(height)}px;
	margin: 0;
}}

div.image_cover > img {{
    position: absolute;
    top: 0px;
	left: 0px;
	margin: 0;
	z-index: 0;
}}"""

        # If there are no chapters/TOC, set cover as the only chapter (a TOC is required).
        if len(settings["chapters"]) == 0: navigation += """
            <li>
                <a href=\"cover.xhtml\">Cover</a>
            </li>"""
        
        # Create manifest XHTML for the cover.
        manifestXHTML += f"""
        <item id=\"cover\" href=\"cover.xhtml\" media-type=\"application/xhtml+xml\"/>
        <item id=\"cover-image\" properties=\"cover-image\" href=\"images/{imgs[i]}\" media-type=\"image/{mediatype}\"/>"""
        
        # Create spine data for the cover.
        spine += """
        <itemref idref=\"cover\" linear=\"yes\"/>"""
        
        # If page_num is less than 1 (Cover is before 'page 1'), add pre-page num (roman numeral).
        if page_num < 1:
            pagelist.append(roman(page_num+settings["pageStart"]+1))

        else: # Otherwise, append the page number as-is.
            pagelist.append(str(page_num))
    
    elif page_num < 1: # If the page numnber is less than one (is pre-page):
        
        title = f"Page {roman(page_num+settings['pageStart']+1)}" # Create title for pre-page.
        
        # Create file name for pre-page.
        file_name = f"pg_{roman(page_num+settings['pageStart']+1)}.xhtml"
        
        # Create XHTML code for pre-page.
        xhtml_code = f"""
<body class=\"body_{roman(page_num+settings['pageStart']+1)}\">
    <div class=\"image_{roman(page_num+settings['pageStart']+1)}\">
        <img src=\"images/{imgs[i]}\" width=\"{str(width)}\" height=\"{str(height)}\" alt=\"Page {roman(page_num+settings['pageStart']+1)}\" />
    </div>
</body>"""

        # Create stylesheet code for pre-page.
        stylesheet += f"""

body.body_{str(page_num)} {{	width: {str(width)}px; height: {str(height)}px;	margin: 0; }}

img.image_{str(page_num)} {{	position: absolute; top: 0px; left: 0px; margin: 0;	z-index: 0; }}"""

        # Create manifest data for pre-page.
        manifestXHTML += f"""
        <item id=\"xhtml_{str(i)}\" href=\"{file_name}\" media-type=\"application/xhtml+xml\"/>
        <item id=\"{imgs[i]}\" href=\"images/{imgs[i]}\" media-type=\"image/{mediatype}\"/>"""
        
        # Create spine data for pre-page.
        spine += f"""
        <itemref idref=\"xhtml_{str(i)}\" linear=\"yes\"/>"""
        
        pagelist.append(roman(page_num+settings["pageStart"]+1)) # Append to pagelist.

    else: # If regular page, do this:
        
        title = "Page "+str(page_num) # Set proper title.
        
        file_name = f"pg_{str(page_num)}.xhtml" # Set proper filename.
        
        # Create XHTML code.
        xhtml_code = f"""
<body class=\"body_{str(page_num)}\">
    <div class=\"image_{str(page_num)}\">
        <img src=\"images/{imgs[i]}\" width=\"{str(width)}\" height=\"{str(height)}\" alt=\"{str(page_num)}\" />
    </div>
</body>"""

        # Create stylesheet code.
        stylesheet += f"""
body.body_{str(page_num)} {{	width: {str(width)}px; height: {str(height)}px;	margin: 0; }}

img.image_{str(page_num)} {{	position: absolute; top: 0px; left: 0px; margin: 0;	z-index: 0; }}"""

        # Generate manifest data for page.
        manifestXHTML += f"""
        <item id=\"xhtml_{str(i)}\" href=\"{file_name}\" media-type=\"application/xhtml+xml\"/>
        <item id=\"{imgs[i]}\" href=\"images/{imgs[i]}\" media-type=\"image/{mediatype}\"/>"""
        
        # Create spine data for page.
        spine += f"""
        <itemref idref=\"xhtml_{str(i)}\" linear=\"yes\"/>"""
        
        # Append page to pagelist.
        pagelist.append(str(page_num))
    
    # Create XHTML base XHTML code.
    xhtml_code = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:ePUB=\"http://www.idpf.org/2007/ops\">
<head>
    <meta charset=\"UTF-8\"/>
    <meta name=\"viewport\" content=\"width={str(width)}, height={str(height)}\" />
    <title>{title}</title>
    <link href=\"stylesheet.css\" type=\"text/css\" rel=\"stylesheet\" />
</head>{xhtml_code}
</html>"""

    # Set filepath for XHTML file.
    file_path = os.path.join(settings["ePUB_path"], settings["filename"], 
                             "OEBPS", file_name)
    
    pageImg.close() # Close image.
    
    create_file(file_path, xhtml_code) # Create XHTML file

# Create stylesheet with all generated CSS code.
create_file(os.path.join(settings["ePUB_path"], settings["filename"],"OEBPS",
                         "stylesheet.css"), stylesheet)

# Index through chapters and generate NAV code for them.
for i in range(len(settings["chapters"])): navigation += f"""
            <li>
                <a href=\"{settings['chapters'][i]}.xhtml\">{settings['chapterNames'][i]}</a>
            </li>"""

# End NAV's TOC, start page-list.
navigation += """
        </ol>
    </nav>
    <nav xmlns:ePUB=\"http://www.idpf.org/2007/ops\" role=\"doc-pagelist\" ePUB:type=\"page-list\" id=\"page-list\">
        <ol>"""

# Index through pagelist.
for i in range(len(pagelist)):
    
    # If the page is cover, link to cover XHTML. 
    if i == 0: navigation += f"""
            <li><a href=\"cover.xhtml\">{pagelist[i]} of {(len(pagelist)-settings['pageStart'])-1}</a></li>"""
    
    # Otherwise, generate typical code.
    else: navigation += f"""
            <li><a href=\"pg_{pagelist[i]}.xhtml\">{pagelist[i]} of {(len(pagelist)-settings['pageStart'])-1}</a></li>"""

# Add NAV end code.
navigation += """
        </ol>
    </nav>
</body>
</html>"""

# Create NAV file.
create_file(os.path.join(settings["ePUB_path"], settings["filename"],"OEBPS",
                         "nav.xhtml"), navigation)

# Create container.xml file.
create_file(os.path.join(settings["ePUB_path"], settings["filename"],"META-INF",
                         "container.xml"), 
"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<container version=\"1.0\" xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\">
    <rootfiles>
        <rootfile 
            full-path=\"OEBPS/content.opf\" 
            media-type=\"application/oebps-package+xml\"/>
   </rootfiles>
</container>""")

# Create Apple Books metadata (for compatability).
create_file(os.path.join(settings["ePUB_path"], settings["filename"],"META-INF",
                         "com.apple.ibooks.display-options.xml"), 
"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<display_options>
	<platform name=\"*\">
		<option name=\"fixed-layout\">true</option>
		<option name=\"open-to-spread\">true</option>
	</platform>
</display_options>""")

#[TO-DO: Make sure it is compatable with many other programs, add files when nessesary.]

# Only generate if legacy is enabled.
if settings["legacy"] == "y":
    
    # Generate NCX top code.
    ncxLegacy = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<ncx version=\"2005-1\" xml:lang=\"en-US\" xmlns=\"http://www.daisy.org/z3986/2005/ncx/\">
<head>
    <meta name=\"dtb:uid\" content=\"{settings['identifier']}\"/>
    <meta name=\"dtb:depth\" content=\"{len(pagelist)-settings['pageStart']}\"/>
    <meta name=\"dtb:totalPageCount\" content=\"{len(pagelist)-settings['pageStart']}\"/>
    <meta name=\"dtb:maxPageNumber\" content=\"{len(pagelist)-settings['pageStart']}\"/>
</head>
<docTitle>
    <text>{settings['title']}</text>
</docTitle>
<navMap>"""

    if len(settings["chapters"]) == 0: # If there are no chapters, add cover for TOC.
        ncxLegacy += """
    <navPoint id=\"cover\" playOrder=\"1\">
        <navLabel>
            <text>Cover</text>
        </navLabel>
        <content src=\"cover.xhtml\"/>
    </navPoint>"""
    
    else: # If there are chapters:
        
        for i in range(len(pagelist)): # Index through pagelist.
            
            for j in range(len(settings["chapters"])): # Also index through chapters.
                
                # If the currently indexed page is the start of the currently indexed chapter:
                if pagelist[i] == settings["chapters"][j]:
                    
                    #Generate NCX entry for chapter.
                    ncxLegacy += f"""
    <navPoint id=\"chapter_{j+1}\" playOrder=\"{i-int(settings['pageStart'])}\">
        <navLabel>
            <text>{settings['chapterNames'][j]}</text>
        </navLabel>
        <content src=\"pg_{pagelist[i]}.xhtml\"/>
    </navPoint>"""
    
    # End TOC, start page-list.
    ncxLegacy += """
</navMap>
<pageList>
    <navLabel>
        <text>Pages</text>
    </navLabel>"""

    if len(settings["chapters"]) != 0: # If there are chapters:
        
        # Generate special cover code.
        ncxLegacy += """
    <pageTarget type=\"normal\" id=\"cover_page\" value=\"0\" playOrder=\"1\">
        <navLabel>
            <text>Cover</text>
        </navLabel>
        <content src=\"cover.xhtml\"/>
    </pageTarget>"""
    
    for i in range(len(pagelist)): # Index through pagelist.
        
        # If the page is not the start of a chapter and is not the cover:
        if pagelist[i] not in settings["chapters"] and i != 0: 
            
            # Add to the pageList.
            ncxLegacy += f"""
    <pageTarget type=\"normal\" id=\"pg_{pagelist[i]}\" value=\"{i+1}\" playOrder=\"{i+1}\">
        <navLabel>
            <text>{pagelist[i]} of {(len(pagelist)-settings['pageStart'])-1}</text>
        </navLabel>
        <content src=\"pg_{pagelist[i]}.xhtml\"/>
    </pageTarget>"""
    
    # End NCX document.
    ncxLegacy += """
</pageList>
</ncx>"""

# Create NCX document.
create_file(os.path.join(settings["ePUB_path"], settings["filename"],"OEBPS",
                         "toc.ncx"), ncxLegacy)

# Generate some package document code.
package = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<package xmlns=\"http://www.idpf.org/2007/opf\" version=\"3.0\" unique-identifier=\"pub-id\" xml:lang=\"{settings['lang']}\" dir=\"{settings['dir']}\">
    <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\">
        <meta name=\"cover\" content=\"cover-image\" />
        <dc:identifier id=\"pub-id\">{settings['identifier']}</dc:identifier>
        <dc:language>{settings['lang']}</dc:language>
        <meta property=\"dcterms:modified\">{settings['dateMod']}</meta>
        <dc:title id=\"title\">{settings['title']}</dc:title>
        <meta property=\"rendition:layout\">pre-paginated</meta>
        <meta property=\"rendition:spread\">both</meta>"""

if settings["optionalMeta"] == "y": # If optional metadata was added:
    
    # If title sort was added, add to package.
    if settings["titleSort"] != "": package += f"""
        <meta property=\"file-as\" refines=\"#title\">{settings['titleSort']}</meta>"""
    
    # If authors were added, add to package.
    if len(settings["authors"]) > 0:
        
        # Index through authors.
        for i in range(len(settings["authors"])):
            
            # Create author metadata.
            authorPkg = f"""        
        <dc:creator id=\"creator_{str(i)}\">{settings['authors'][i]}</dc:creator>
        <meta refines=\"#creator_{str(i)}\" property=\"file-as\">{settings['authorSort'][i]}</meta>"""
            
            # If altscript added, add a meta refines.
            if settings['authorAltScript'][i] != "": authorPkg += f"""
        <meta refines=\"#creator_{str(i)}\" property=\"alternate-script\" xml:lang=\"{(settings['authorAltScript'][i]).split(',')[1]}\">{(settings['authorAltScript'][i]).split(',')[0]}</meta>"""
            
            package += authorPkg # Add to package doc.

    # If any contributors added:
    if len(settings["contributors"]) > 0:
        
        # Index through contributors:
        for i in range(len(settings["contributors"])):
            
            # Create package data.
            contributorPkg = f"""
        <dc:contributor id=\"contributor_{str(i)}\">{settings['contributors'][i]}</dc:contributor>
        <meta refines=\"#contributor_{str(i)}\" property=\"file-as\">{settings['contributorSort'][i]}</meta>"""
            
            # If altscript added, add meta refines.
            if settings['contributorAltScript'][i] != "": contributorPkg += f"""
        <meta refines=\"#contributor_{str(i)}\" property=\"alternate-script\" xml:lang=\"{(settings['contributorAltScript'][i]).split(',')[1]}\">{(settings['contributorAltScript'][i]).split(',')[0]}</meta>"""
            
            package += contributorPkg # Add to package doc.

    # If publication date was given, add to doc.
    if settings["pubdate"] != "": package += f"""
        <dc:date>{settings['pubdate']}</dc:date>"""
        
    # If publisher was added, add to doc.
    if settings["publisher"] != "": package += f"""
        <dc:publisher>{settings['publisher']}</dc:publisher>"""

    # If description was added, add to doc.
    if settings["desc"] != "": package += f"""
    <dc:description>
{settings['desc']}
    </dc:description>"""
    
# End metadata section, start manifest.
package += """
    </metadata>
    <manifest>"""

# Add NAV and stylesheet documents to package (not added dynamically since they are always there),
# and add previosuly generated manifest code.
package += f"""
        <item id=\"toc\" properties=\"nav\" href=\"nav.xhtml\" media-type=\"application/xhtml+xml\"/>
        <item id=\"style\" href=\"stylesheet.css\" media-type=\"text/css\"/>{manifestXHTML}"""

# If legacy is enabled, add NCX to the manifest and spine data.
if(settings["legacy"]) == "y": package += f"""
        <item id=\"ncx\" href=\"toc.ncx\" media-type=\"application/x-dtbncx+xml\"/>
    </manifest>
    <spine toc=\"ncx\" page-progression-direction=\"{settings['dir']}\">"""

# Otherwise, end manifest normally and have normal spine.
else: package += f"""
    </manifest>
    <spine page-progression-direction=\"{settings['dir']}\">"""

# Add spine to package document, end package document.
package += spine + """
    </spine>
</package>"""

# Create the package document file.
create_file(os.path.join(settings["ePUB_path"], settings["filename"],"OEBPS",
                         "content.opf"), package)


endLoadPrint("\nFiles Created!\n") # End file creation load.

startLoadPrint("Creating ePUB") # Start compilation load.

try: # Do the following while catching any errors:
    
    # Open/create ePUB file.
    with zipfile.ZipFile(settings["ePUB_path"]+"\\"+settings["filename"]+
                         ".ePUB", 'w') as ePUB:
        
        # Write mimetype file first (needs to be at the top of file).
        ePUB.write(os.path.join(settings["ePUB_path"], settings["filename"], 
                                "mimetype"), "mimetype")
        
        # Index every file in /META-INF.
        for file in os.listdir(os.path.join(settings["ePUB_path"], 
                                            settings["filename"], "META-INF")):
        
        # Add to /META-INF folder inside ePUB.
            ePUB.write(os.path.join(settings["ePUB_path"], settings["filename"],
                                    "META-INF", file), "META-INF\\"+file)
        
        # Index every file from /OEBPS.
        for file in os.listdir(os.path.join(settings["ePUB_path"], 
                                            settings["filename"], "OEBPS")):
            
            # Add to /OEBPS in ePUB.
            ePUB.write(os.path.join(settings["ePUB_path"], settings["filename"],
                                    "OEBPS", file), "OEBPS\\"+file)

        # Index every file from /OEBPS/images.
        for file in os.listdir(os.path.join(settings["ePUB_path"], 
                                            settings["filename"], "OEBPS", 
                                            "images")):

            # Add to /OEBPS/images in ePUB.
            ePUB.write(os.path.join(settings["ePUB_path"], settings["filename"],
                                    "OEBPS", "images", file), "OEBPS\\images\\"
                                                            +file)

        # If not in debug, remove directory we initially made files is.
        if debug != True: shutil.rmtree(os.path.join(settings["ePUB_path"],
                                                     settings["filename"]))

# If any error caught, inform user and quit.
except Exception as error:
    print (f"File {os.path.join(settings['ePUB_path'], settings['filename'])}."
           +f"ePUB can't be created. Reason: {error}")
    quit()

# If all succeeds, print path and end load, then quit.
endLoadPrint(f"\nePUB created at {settings['ePUB_path']}!")
quit()