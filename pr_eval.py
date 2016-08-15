from fuzzywuzzy import fuzz
import argparse, codecs, getpass, itertools, json, sys
FPATH = '/home/{}/newsevents/post_extract_tests/'.format(getpass.getuser())
HAPNIS_PATH = "".join([FPATH, 'hapnis/'])
if HAPNIS_PATH not in sys.path: sys.path.append(HAPNIS_PATH)
import hapnis_normalize


def get_all_names(month, year):
    readfile = "{}all_names/all_names_{:d}_{:d}.json".format(FPATH, month, year)
    with codecs.open(readfile, "r", "utf-8") as a:
        names = []
        for line in a: names.extend(json.loads(line)['name_candidates'])
        name_set = set([name.lower() for name in names])
        return name_set


def get_gold_names(month, year):
    goldfile = "{}victim_names/{:d}_{:d}_names_strict_month.tsv".format(FPATH, 
            month, year)
    with codecs.open(goldfile, "r", "utf-8") as g:
        name_set = set([line.strip().lower() for line in g])
        return name_set


def get_names(retrieved_names_f):
    with codecs.open(retrieved_names_f, "r", "utf-8") as rf:
        name_set = set([line.strip().lower() for line in rf])
        return name_set

"""
Calculate, print precision and recall for a retrieved set of names vs. a gold set. 
Uses exact string match
:param retrieved_set:   a set of names retrieved from the data
:param gold_set:        a set of names retrived from gold data
"""
def print_pr_exact(retrieved_set, gold_set):
    tp = retrieved_set & gold_set
    print "Precision: ", float(len(tp)) / len(retrieved_set)
    print "Recall: ",    float(len(tp)) / len(gold_set)


"""
Calculate, print precision and recall for a retrieved set of names vs. a gold set. 
Uses fuzzy string match
:param retrieved_set:   a set of names retrieved from the data
:param gold_set:        a set of names retrived from gold data
:param tol:             a tolerance value for fuzz.ratio() above which to accept 
                        name match.
"""
def print_pr_fuzzy(retrieved_set, gold_set, tol):
    tp = set([g for g in gold_set for r in retrieved_set if fuzz.ratio(g,r) >= tol])
    print "Precision: ", float(len(tp)) / len(retrieved_set)
    print "Recall: ",    float(len(tp)) / len(gold_set)


"""
Gold data (the list of true positive names) is from 
(wiki_killings U fatal encounters)
"""
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--retrievednames", type=str, required=True,
            help="Filepath to get retrieved names from, e.g. 
                all_names/<dataset>_names_only.txt")
    parser.add_argument("-y", "--year", type=int, required=True,
            help="""Scrape year for retrieved data, incident year for gold data""")
    parser.add_argument("-m", "--month", type=int, required=True,
            help="Scrape month for retrieved data, incident month for gold data")
    parser.add_argument("-t", "--tolerance", type=int, help="""Percent tolerance 
            between 0 and 100 for fuzzy string matching. Tolerance is calculated 
            pairwise between name strings a and b as ratio = 2.0*M/T where 
            T = |a|+|b| and M is the number of character matches (inversely 
            related to Levenshtein edit distance). Pairs of names are counted 
            as name matches above this threshold.""", required=True)
    args  = parser.parse_args()    
    goldf = "{}victim_names/{:d}_{:d}_names_strict_month.tsv".format(FPATH, 
            args.month, args.year)
    gold_names = set(hapnis_normalize.get_names(goldf))
    gold_names.discard("")
    if args.retrievednames:
        print "\n---- P / R stats for {} ----\n".format(args.retrievednames)
        print "Retrieved set and gold set were both processed by HAPNIS."
        print "Only names containing both forename and surname were used."
        print "Both sets of names were lowercased, then compared for exact"
        print "string match."
        retrieved_names = set(hapnis_normalize.get_names(args.retrievednames))
        retrieved_names.discard("")
        print_pr_exact(retrieved_names, gold_names)


if __name__ == "__main__":
    main()
