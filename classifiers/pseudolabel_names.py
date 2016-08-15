import argparse, codecs, datetime as dt, getpass, json, subprocess, sys
FPATH = '/home/{}/newsevents/post_extract_tests/'.format(getpass.getuser())
HAPNIS_PATH = "".join([FPATH, 'hapnis/'])
if HAPNIS_PATH not in sys.path: sys.path.append(HAPNIS_PATH)
import hapnis_normalize


def get_labels(jsonr, month, year, goldnames):
    name_date_tuples = {}
    docids           = []
    scrapedates      = []
    with codecs.open(jsonr, 'r', 'utf-8') as j:
        with codecs.open('.names.txt', 'w', 'utf8') as w:
            for line in j:
                doc         = json.loads(line)
                names       = doc['name_candidates']
                docid       = doc['docid']
                scrapedate  = doc['date']
                for name in names:
                    w.write(name + '\n')
                    docids.append(docid)
                    scrapedates.append(scrapedate)

    names = hapnis_normalize.get_names('.names.txt')
    for docid, name, scrapedate in zip(docids, names, scrapedates):
        if name:
            if name in goldnames:
                event_date = dt.datetime.strptime(goldnames[name], "%Y-%m-%d")
                scr_date   = dt.datetime.strptime(scrapedate, "%Y-%m-%d")
                if event_date <= scr_date:
                    name_date_tuples[docid, name, scrapedate] = 1
                else: 
                    name_date_tuples[docid, name, scrapedate] = -1
            else:
                name_date_tuples[docid, name, scrapedate] = -1

    cmd = 'rm .names.txt'
    subprocess.check_output(cmd, shell=True)
    return  name_date_tuples


def get_gold_names(month, year):
    goldf = '{}victim_names/{:d}_{:d}_name_date.tsv'.format(FPATH, month, year)
    gold_names = hapnis_normalize.get_names_dict(goldf)
    gold_names.pop("", None)
    return gold_names


def main():
    parser = argparse.ArgumentParser(description="""Choose labels for (name, 
            docid) pairs in {-1, 1}, meaning {not a victim of a police killing, 
            victim of a police killing}. The 1 label is chosen if the "firstname
            lastname" lowercased matches the FE or WK database and the incident 
            date precedes the scrape date.""")
    parser.add_argument('-j', '--jsonf', type=str, required=True,
            help='<dataset>.json containing names. Try all_names/*.json.')
    parser.add_argument('-y', '--year', type=int, required=True,
            help='Scrape year for extracted data, incident year for gold data')
    parser.add_argument('-m', '--month', type=int, required=True,
            help='Scrape month for extracted data, incident month for gold data')
    args = parser.parse_args()
    
    gold_names = get_gold_names(args.month, args.year)
    labels = get_labels(args.jsonf, args.month, args.year, gold_names)
    
    name_path = '{}classifiers/{:d}_{:d}_name_labels.json'.format(FPATH, 
            args.month, args.year)
    name_date_path = '{}classifiers/{:d}_{:d}_name_date_labels.json'.format(FPATH, 
            args.month, args.year)
    
    with codecs.open(name_path, 'w', 'utf-8') as names_:
        with codecs.open(name_date_path, 'w', 'utf-8') as name_dates_:
            for docid, name, scrapedate in labels:
                json.dump(
                    {u'docid': docid, 
                     u'name': name,
                     u'victim': labels[docid, name, scrapedate]}, names_)
                json.dump(
                    {u'docid': docid, 
                     u'name': name,
                     u'incidentdate': gold_names.get(name, None), 
                     u'scrapedate': scrapedate,
                     u'victim': labels[docid, name, scrapedate]}, name_dates_)
                names_.write('\n')
                name_dates_.write('\n')


if __name__ == '__main__':
    main()
