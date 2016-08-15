import argparse, datetime as dt, getpass
from calendar import monthrange

"""
FE input: "M/D/YYYY H:M:S Victim Name"
WK input: "YYYY-MM-DD victim name"
combined_names output: (YYYY, M, D, "victim name")
"""
def combine_names(fpath):
    names = set()
    fe_file = "{}victim_names/fe_names.tsv".format(fpath)
    wk_file = "{}victim_names/wk_names.tsv".format(fpath)
    with open(fe_file, "r") as fe:
        for line in fe:
            line = line.split()
            date = line[0].split("/")
            name = " ".join(line[2:]).lower()
            name_tuple = (int(date[2]), int(date[0]), int(date[1]), name)
            names.add(name_tuple)
    with open(wk_file, "r") as wk:
        for line in wk:
            line = line.split()
            date = line[0].split("-")
            name = " ".join(line[1:]).lower()
            if date[0] == 'None': 
                name_tuple = (1900, 1, 1, name)
            else:
                name_tuple = (int(date[0]), int(date[1]), int(date[2]), name)
            names.add(name_tuple)
    return names

"""
Write names from combine_names() to 3 files:
    - victim_names/<dataset>_names.tsv (used in `grep_names.sh`)
    - victim_names/<dataset>_name_date.tsv (used for ...)
    - victim_names/<dataset>_names_strict_month.tsv (used in `pr_eval.py`)
:param fpath:       /path/to/post_extract_tests/
:param names:       a set of gold standard names
"""
def write_names_by_month(fpath, names, year, month):
    writefn = "{0}victim_names/{1}_{2}_names.tsv".format(fpath, month, year)
    writefnd = "{0}victim_names/{1}_{2}_name_date.tsv".format(fpath, month, 
            year)
    writefnds = "{0}victim_names/{1}_{2}_names_strict_month.tsv".format(fpath, 
            month, year)
    f_name   = open(writefn, "w")
    f_name_d = open(writefnd, "w")
    f_name_s = open(writefnds, "w")
    arg_date = dt.datetime(year, month, 1) 
    arg_date += dt.timedelta(monthrange(year, month)[1])
    for date_name in names:
        this_date = dt.datetime(date_name[0], date_name[1], date_name[2])
        name_lower = date_name[3]
        if this_date.month == arg_date.month and this_date.year == arg_date.year:
            f_name_s.write(name_lower + "\n")
        if this_date < arg_date:
            name_upper = " ".join([name.capitalize() for name in name_lower.split()])
            f_name.write(name_lower + "\n")
            f_name.write(name_upper + "\n")
            f_name_d.write("{}\t{:04d}-{:02d}-{:02d}\n".format(name_lower, 
                                  date_name[0], date_name[1], date_name[2]))
    f_name.close()
    f_name_d.close()
    f_name_s.close()


def main():
    fpath = '/home/{}/newsevents/post_extract_tests/'.format(getpass.getuser())
    parser = argparse.ArgumentParser(description="""Take formatted gold victim
            names from Wiki and Fatal Encounters data where incident month < MONTH+1, 
            write names to victim_names/<dataset>_names.tsv and name-date pairs to
            victim_names/<dataset>_name_date.tsv""")
    parser.add_argument('-y', '--year', type=int, help="Year of the dataset", 
            required=True)
    parser.add_argument('-m', '--month', type=int, help="Month of the dataset", 
            required=True)
    args = parser.parse_args()
    names = combine_names(fpath)
    write_names_by_month(fpath, names, args.year, args.month) 


if __name__ == "__main__":
    main() 
