import argparse, codecs, getpass, json


"""
Writes all scraped CoreNLP NER names from all_names/all_names_<dataset>.json to
all_names/<dataset>_names_only.txt
"""
def write_names(month, year):
    fpath  = '/home/{}/newsevents/post_extract_tests/'.format(getpass.getuser())
    readf  = '{}all_names/all_names_{:d}_{:d}.json'.format(fpath, month, year)
    writef = '{}all_names/{:d}_{:d}_names_only.txt'.format(fpath, month, year)
    names  = []
    with open(readf,'r') as rf:
        for line in rf: names.extend(json.loads(line)['name_candidates'])
    names = set(names)
    with codecs.open(writef, 'w', 'utf-8') as wf:
        for name in names: wf.write(u'{}\n'.format(name))

    

def main():
    parser = argparse.ArgumentParser(description="""Take json objects with 
             `name_candidates` fields, write all names in them to one big
             newline-sep set in ./<dataset>_names_only.txt""")
    parser.add_argument('-y', '--year', type=int, required=True, 
            help="Year of the dataset")
    parser.add_argument('-m', '--month', type=int, required=True, 
            help="Month of the dataset")
    args = parser.parse_args()
    write_names(args.month, args.year)


if __name__ == "__main__":
    main()
