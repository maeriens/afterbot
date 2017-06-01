from os import listdir, path
import csv

THE_BAD_GUYS = {}


def add_bad_guy(file):
    """ Update bad guy! """
    responses = grab_responses(file)
    name = path.splitext(file)[0]
    THE_BAD_GUYS.update({name: responses})


def grab_responses(file):
    """ Grab files with responses and parse them """
    responses = []
    if path.splitext(file)[1] == '.txt':
        try:
            with open('./txt/' + file, encoding='utf-8') as inputfile:
                for line in inputfile:
                    responses.extend(line.strip().split(','))
        except FileNotFoundError:
            print(file + ' not found')
        finally:
            return responses
    elif path.splitext(file)[1] == '.csv':
        try:
            with open('./txt/' + file, newline='', encoding='utf-8') \
                    as inputfile:
                # Specify delimiter for reader.
                csv_rows = csv.reader(inputfile, delimiter=",")

                # Loop over rows and display them.
                for row in csv_rows:
                    responses.extend(row)
        except FileNotFoundError:
            print(file + ' not found')
        finally:
            return responses
    else:
        print(file + ' format not accepted')


# Add below the bad guys and everything; array is generated on first run
for file in listdir("./txt/"):
    add_bad_guy(file)
