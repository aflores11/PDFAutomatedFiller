# Modules Needed to Run:
> install PyPDF2 -> pip3 install PyPDF2\
> install pdfrw -> pip3 install pdfrw\
> install reportlab -> pip3 install reportlab

# Program Instructions (IMPORTANT TO RUN):
> 1. This program has some error checks for major functionality, but it expects correctly formatted text for every input.
>2. When giving it an input .txt file. It needs to be well formatted.\
    instructions are given during the running of the program.   
    ------------------   
    The order of the data does not matter, HOWEVER, each line needs to have SAME amount
    of entries. If one entry does not have one input that others have, include the entry's number but leave
    an empty space " " next to the colon.   
    Ex: variable#:(blank_space)  
    Look at multipleWF1.txt for reference
>3. The number of the variable depends on the pdf File. Always look at the numbers to make
    sure you are putting data in the right text field

# UserWarning: Cache Overwrite

> If you get a UserWarning about overwriting Cache when giving the pdf name
> It means your pdf is corrupted and DO NOT continue. Click exit as that can 
> lead to unexpected behavior.
> It most likely because you used Preview to alter the pdf. 
> 
> To potentially fix, go on Adobe Acrobat 
> (can be free version) and click on each field. When clicking on the field, add a space and then 
> delete the space and press enter. Do it for each text field and then save pdf. Avoid altering pdfs with preview.
> 
> If that does not work, you'll have to create a new fresh pdf with text fields or get a version of it with no
> text fields and manually add coordinates.

# PDF if appearing blank on APPLE Preview but shows when click Text Field

> Do not worry, the input it there. You cn see it if you open it in Adobe or Google Chrome.  
> This problem is more on Apple's end as they work with PDFs differently. A solution that 
> I have found that fixes it is to open it through Adobe Acrobat where you will see it
> is filled. Just click save without changing anything and that sometimes fixes it for Preview


# How to get Coordinates for PDF
> The coordinates must be given in inches and the origin for the pdf should be the bottom-left corner. 
> 
> I found it hard to set the origin to bottom left corner in Adobe Acrobat but have found the application
> GIMP to be very useful. If you use it, there you can flip the pdf vertically, and although it will look weird,
> the pdf origin will be set correctly and from there get the coordinates of where you want
> text to go.
