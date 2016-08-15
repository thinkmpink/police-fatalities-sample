import argparse, getpass, subprocess
FPATH = '/home/{}/newsevents/post_extract_tests/'.format(getpass.getuser())
"""
Input: a newline-sep document containing 1 name per line.
Output: A list of only those names that contain both a "Forename" and a
"Surname" attribute. For names not meeting this requirement, an empty 
string is added to the list. 
NOTE: This script outputs names in lowercase
Ex: on input "George Michael Bluth Jr.", output "george bluth"
"""
#TODO: we don't get the name if it labels "Forename" after "Surname"
def get_names(filename):
    hnames  = []
    cmd     = ("perl {0}hapnis/hapnis.pl -names <{1}").format(FPATH, filename)
    body    = subprocess.check_output(cmd, shell=True).splitlines()
    for line in body:
	if "Forename" not in line or "Surname" not in line: hnames.append("")
	else:
	    name = line.strip().decode('utf-8').split()
	    firstlast = u""
	    for part in name:
		w = part.split("_")
                if len(w) != 2: pass
		elif w[1]=="Forename": firstlast = w[0].lower()
		elif w[1]=="Surname": firstlast = firstlast + " " + w[0].lower()
	    	else: pass
	    if " " not in firstlast.strip(): hnames.append("")
	    else: hnames.append(firstlast.lstrip())
    return hnames
 

"""
Same as get_names() but returns a dict instead of a list.
Assumes input line is e.g. "George Michael Bluth Jr. 2015-01-06"
Output (k, v) pair in dict = "george bluth": "2015-01-06" 
"""
def get_names_dict(filename):
    hnames  = {}
    cmd     = ("perl {0}hapnis/hapnis.pl -names <{1}").format(FPATH, filename)
    body    = subprocess.check_output(cmd, shell=True).splitlines()
    for line in body:
	if "Forename" in line and "Surname" in line: 
	    name = line.strip().decode('utf-8').split()
	    firstlast = u""
	    for part in name:
		w = part.split("_")
                if len(w) != 2: pass
		elif w[1]=="Forename": firstlast = w[0].lower()
		elif w[1]=="Surname": firstlast = firstlast + " " + w[0].lower()
	    	else: pass
            date = name[-1].split("_")[0]
	    if " " in firstlast.strip(): hnames[firstlast.lstrip()] = date
    return hnames


def main():
    parser = argparse.ArgumentParser(description="""Take names from 
            readfile, run hapnis.pl on them, prints with tags stripped by
            _forename _surname to stdout""") 
    parser.add_argument('-r', '--readfile', type=str, required=True,
	    help="File containing names separated by newlines")
    args  = parser.parse_args()
    names = get_names(args.readfile)
    for name in names: print name.encode('utf-8')


if __name__ == "__main__":
    main()
