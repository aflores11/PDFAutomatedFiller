# Angel Flores, angelflo@usc.edu
# ITP 499, Spring 2021
# Final Project
# Description:
#   This program is made to automate boring tasks such as filling multiple PDFs
#   It is also meant to learn how to use others' modules to integrate into your own program


import PyPDF2 as pypdf
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject
import re
import io
import pdfrw
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def set_need_appearances_writer(writer: pypdf.PdfFileWriter):
    # See 12.7.2 and 7.7.2 for more information:
    # http://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
    try:
        catalog = writer._root_object
        # get the AcroForm tree
        if "/AcroForm" not in catalog:
            writer._root_object.update({
                NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})

        need_appearances = NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
        return writer

    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))
        return writer


def getpdf():
    prompt = True
    while prompt:
        try:
            name = input("\nWhat is the name of the pdf\n"
                         "** Do not include .pdf extension **\n"
                         "**** It is recommended that your PDF has fields set up already ****\n"
                         "To exit program type in \'::q\'\n"
                         "\tYour input: ")
            if name.strip() == "::q":
                exit()
            ogpdf = open(name + ".pdf", 'rb')
            prompt = False
        except OSError:
            print("File does not exist")

    try:
        pdfObj = pypdf.PdfFileReader(ogpdf, strict=False)
        if "/AcroForm" in pdfObj.trailer["/Root"]:
            pdfObj.trailer["/Root"]["/AcroForm"].update(
                {NameObject("/NeedAppearances"): BooleanObject(True)})
    except pypdf.utils.PdfReadError:
        print("PyPDF2 cannot open the PDF...")
        print("If you have edited the PDF in Preview, it might have corrupted the PDF ")
        print("More info on how to fix in README")
        ogpdf.close()
        exit()

    return [ogpdf, pdfObj]


def getPDFData(pdf):
    if pdf[1].getFields() is None:
        fields = None
    else:
        fields = pdf[1].getFormTextFields()

    global CONST_HASFIELDS

    if fields is None or not fields:
        CONST_HASFIELDS = False
        pdf.append([])
        pdf.append(dict())
    else:
        CONST_HASFIELDS = True
        pdf.append(list(fields.keys()))
        pdf.append(fields)


def showFields(pdf):
    if not CONST_HASFIELDS:
        print("Your pdf does not have form fields.")
        return

    # pdf = [file, pdfObject, list of field names, field_name dictionary]
    print("Your text fields are:")
    for i in range(0, len(pdf[2])):
        print("\t%d - %s" % (i + 1, pdf[2][i]))
    print()
    return


def twoChoice(text1, text2):
    prompt = True
    while prompt:
        try:
            print("Would you like to\n"
                  "\t1. %s\n"
                  "\t2. %s\n" % (text1, text2))
            choice = int(input("Your input: "))
            if choice < 1 or choice > 2:
                raise ValueError
            prompt = False
        except ValueError:
            print("Not a valid option.")
            choice = -1

    return choice


def get_overlay_canvas(pdfArr) -> io.BytesIO:
    data = io.BytesIO()
    pdf = canvas.Canvas(data)
    pdf.setPageSize((8.5 * inch, 11 * inch))
    for key in pdfArr[3]:
        value = pdfArr[3][key]
        pdf.drawString(x=pdfArr[4][key][0], y=pdfArr[4][key][1], text=str(value))
    pdf.save()
    data.seek(0)
    return data


def merge(overlay_canvas: io.BytesIO, template_path: str) -> io.BytesIO:
    template_pdf = pdfrw.PdfReader(template_path)
    overlay_pdf = pdfrw.PdfReader(overlay_canvas)
    for page, data in zip(template_pdf.pages, overlay_pdf.pages):
        overlay = pdfrw.PageMerge().add(data)[0]
        pdfrw.PageMerge(page).add(overlay).render()
    form = io.BytesIO()
    pdfrw.PdfWriter().write(form, template_pdf)
    form.seek(0)
    return form


def save(form: io.BytesIO, filename: str):
    with open(filename, 'wb') as f:
        f.write(form.read())


def matchToPage(pdf, filename):
    pdfWriter = pypdf.PdfFileWriter()
    set_need_appearances_writer(pdfWriter)
    if "/AcroForm" in pdfWriter._root_object:
        pdfWriter._root_object["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})

    for pageNum in range(pdf[1].numPages):
        page = pdf[1].getPage(pageNum)
        pdfWriter.addPage(page)
        pdfWriter.updatePageFormFieldValues(page, pdf[3])

    try:
        output = open(filename, "wb")
    except FileNotFoundError:
        print("Error Saving File. If you are using a / in save name, make sure it leads to a directory and not used "
              "for dates")
        exit()

    pdfWriter.write(output)
    output.close()
    return


def dynamicNamePrint(pdf):
    print("The available data inputs are:")
    iterator = 1
    for key in pdf[3].keys():
        print("%d. %s" % (iterator, key))
        iterator += 1

    print("Please provide the order of how you want to name your files. Numbers will be\n"
          "used as the dynamic name, everything else will be added as part of the name\n"
          "use pipes ( | ) to separate numbers and groups of characters you want together\n"
          "if you want a space between two variables add it between two pipes e.g. | | \n"
          "Keep variable names on their own -> \"test -| #1 |- file\" not \"test - #1 | - file\"\n"
          "EX: to save as \"John Doe - file\" you'd write: #1 | | #2 | - file")
    to_return = input("Your input: ")
    return to_return


def dynamicName(pdf, line):
    saveName = ""
    lineArr = line.split("|")
    pattern = '^#[0-9]{1,2}'
    for item in lineArr:
        if re.fullmatch(pattern, item.strip()):
            temp = item.strip().replace("#", "")
            num = int(temp) - 1
            newKeys = list(pdf[3].keys())
            try:
                saveName += pdf[3][newKeys[num]]
            except IndexError:
                print("Invalid Choice of Dynamic Variable")
                continue
        else:
            saveName += item
    return saveName


def saveToPDF_single(pdf):
    choice = twoChoice("Manually name the file", "Dynamically Name File")
    if choice == 1:
        save_name = input("Please provide the name of the file without .pdf extension: ")
    else:
        save_name = dynamicName(pdf, dynamicNamePrint(pdf))

    if CONST_HASFIELDS:
        matchToPage(pdf, save_name.strip() + ".pdf")
    else:
        canvas_data = get_overlay_canvas(pdf)
        form = merge(canvas_data, template_path='./' + pdf[0].name)
        save(form, filename=save_name.strip() + ".pdf")
    return


def parseLine(line, pdf, changed):
    # pdf = [file, pdfObject, list of field names, field_name dictionary]
    inputArr = line.strip().split("|")
    for index in inputArr:
        key_value = index.split(":")
        try:
            index = int(key_value[0])
            if index < 1 or index > len(pdf[2]):
                raise ValueError
        except ValueError:
            continue

        # index is from 1 -> len not 0 -> len -1
        key = pdf[2][index - 1]
        pdf[3][key] = key_value[1].strip()
        changed.add(key)


def manualAdd(pdf):
    changed = set()

    # pdf = [file, pdfObject, list of field names, field_name dictionary]
    print("These are your inputs")
    for i in range(0, len(pdf[2])):
        print("\t%d - %s" % (i + 1, pdf[2][i]))
    print("IMPORTANT, Please enter you data in a single line with the following format:\n"
          "\t#:value | #:value | #:value   etc.\n"
          "\t: is for key -> value , | is used to denote different key->value pairs\n"
          "\tAny number that is not a valid choice will be disregarded")
    parseLine(input("Your input: "), pdf, changed)

    for key in pdf[2]:
        if key not in changed:
            pdf[3].pop(key)

    return


def getLineData(pdf):
    prompt = True
    while prompt:
        try:
            inFile = input("Name of the file input (include .txt extension):  ")
            doc = open(inFile.strip(), 'r')
            prompt = False
        except OSError:
            print("File Does not exist")
            inFile = ""
    changed = set()
    parseLine(doc.readline(), pdf, changed)
    doc.close()
    for key in pdf[2]:
        if key not in changed:
            pdf[3].pop(key)
    return


def getFileData(pdf):
    prompt = True
    while prompt:
        try:
            inFile = input("Name of the DATA file input (include .txt extension):  ")
            doc = open(inFile.strip(), 'r')
            prompt = False
        except OSError:
            print("File Does not exist")

    choice = 0
    iterator = 1
    dynamic_track = 1
    for line in doc:
        changed = set()
        parseLine(line, pdf, changed)

        for key in pdf[2]:
            try:
                if key not in changed:
                    pdf[3].pop(key)
            except KeyError:
                continue

        if dynamic_track == 1:
            choice = twoChoice("Manually name the files(same name but numbered in asc order automatically)",
                               "Dynamically "
                               "name the files")

            if choice == 1:
                save_name = input("What will you name the files without .pdf extension (will show as <name>_#): ")
                save_name += "_"
            elif choice == 2:
                save_name = dynamicNamePrint(pdf)

        if choice == 1:
            if CONST_HASFIELDS:
                matchToPage(pdf, "%s%d.pdf" % (save_name.strip(), iterator))
            else:
                canvas_data = get_overlay_canvas(pdf)
                form = merge(canvas_data, template_path='./' + pdf[0].name)
                save(form, filename="%s%d.pdf" % (save_name.strip(), iterator))
            iterator += 1
        elif choice == 2:
            if CONST_HASFIELDS:
                matchToPage(pdf, filename=dynamicName(pdf, save_name).strip() + ".pdf")
            else:
                canvas_data = get_overlay_canvas(pdf)
                form = merge(canvas_data, template_path='./' + pdf[0].name)
                save(form, filename=dynamicName(pdf, save_name).strip() + ".pdf")
        dynamic_track += 1

    doc.close()
    return


def manualCoord(pdf):
    pdf.append(dict())
    # pdf is now a list of [file, pdfObject, list of field names, field_name dictionary, field->coordinate dict]
    while True:
        response = input("Enter (x-coordinate|y-coordinate|input_field_name or \'::d\' if done):")
        if response.strip() == "::d":
            break
        inputArr = response.split("|")
        try:
            x_c = float(inputArr[0])
            y_c = float(inputArr[1])
            key = inputArr[2].strip()
        except ValueError:
            print("Invalid Input")
            continue
        except IndexError:
            print("Invalid Input")
            continue

        pdf[2].append(key)
        pdf[3][key] = ""
        pdf[4][key] = (x_c * inch, y_c * inch)

    if not pdf[4]:
        print("Need to insert coordinates")
        exit()



def coordFromFile(pdf):
    print("File should be formatted as such:\n"
          "\tline1: x_coord|y_coord|name_1\n"
          "\tline2: x_coord|y_coord|name_2\n"
          "\tline3: x_coord|y_coord|name_3\n"
          "etc ---- Do not include the \'line#:\' part")
    prompt = True
    while prompt:
        try:
            inFile = input("Name of the COORDINATE file input (include .txt extension):  ")
            doc = open(inFile.strip(), 'r')
            prompt = False
        except OSError:
            print("File Does not exist")
    pdf.append(dict())
    for line in doc:
        inputArr = line.split("|")
        try:
            x_c = float(inputArr[0])
            y_c = float(inputArr[1])
            key = inputArr[2].strip()
        except ValueError:
            print("Invalid Input")
            continue
        except IndexError:
            print("Invalid Input")
            continue

        pdf[2].append(key)
        pdf[3][key] = ""
        pdf[4][key] = (x_c * inch, y_c * inch)
    doc.close()


def getCoordinates(pdf):
    print("IMPORTANT:\n"
          "\t format as following:   x_coordinate (inches) | y_coordinate (inches) | text_field_name\n"
          "\t For pdfs, x=0 inch, y=0inch starts at bottom left corner.")
    choice = twoChoice("Manually enter coordinates", "Provide file with coordinates")
    if choice == 1:
        manualCoord(pdf)
    elif choice == 2:
        coordFromFile(pdf)
    else:
        pass


def multipleFiller(pdf):
    if not CONST_HASFIELDS:
        getCoordinates(pdf)

    getFileData(pdf)


def singleFiller(pdf):
    if not CONST_HASFIELDS:
        getCoordinates(pdf)

    choice = twoChoice("Manually Enter Text Data", "Provide Formatted .txt File")
    if choice == 1:
        manualAdd(pdf)
    else:
        getLineData(pdf)

    saveToPDF_single(pdf)


def menu(pdf):
    prompt = True
    while prompt:
        try:
            choice = int(input("Would you like to:\n"
                               "\t1. View Form Fields\n"
                               "\t2. Fill Single PDF\n"
                               "\t3. Fill Multiple PDFs\n"
                               "\t4. Exit\n"
                               "Your input: "))
            prompt = False
        except ValueError:
            print("Not a valid option.")
            choice = ""

    if choice == 1:
        showFields(pdf)
        return True
    elif choice == 2:
        singleFiller(pdf)
    elif choice == 3:
        multipleFiller(pdf)
    elif choice == 4:
        pass
    else:
        print("Invalid Menu Choice")
        return True

    try:
        pdf[0].close()
    except IOError:
        pass
    print("Goodbye!")
    return False


def main():
    pdf = getpdf()
    # pdf returned as a list of [file, pdfObject]
    getPDFData(pdf)
    # pdf returned as a list of [file, pdfObject, list of field names, field_name dictionary]
    while menu(pdf):
        pass


CONST_HASFIELDS = False  # Global constant that will be set when file is read. Default False
main()
