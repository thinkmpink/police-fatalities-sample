import argparse, codecs, getpass, re, sys
sys.path.insert(0, '../../text_extraction')
import wrappers


"""
Convert raw html to text
"""
def html_to_text(year, month, lx):
    extract_f  = lx.extract
    fpath      = '/home/{}/newsevents/post_extract_tests/'.format(getpass.getuser())
    read_file  = '{}html_docs/{:d}_{:d}_html.tsv'.format(fpath, month, year)
    write_file = '{}lynx_docs/{:d}_{:d}_lx.tsv'.format(fpath, month, year)
    with open(read_file, 'rb') as rf:
    #with codecs.open(read_file, 'r', 'utf-8') as rf:
        with codecs.open(write_file, 'w', 'utf-8') as wf:
            for record in rf: _extract_and_write(record, wf, extract_f)


"""
Write list of tab-separated article and metadata in format:
ID, Date(downloadtime), Title, Body
Calls extraction function `extract_f` on a tuple (ID, date, HTML markup)
"""
#TODO: Do this and extraction via a generator that writes to the file? 
def _extract_and_write(record, f, extract_fn):
    record  = record.decode('utf-8', errors='replace').split("\t")
    ID, date, title, body = [u"None"]*4
    if record[0]:     ID = record[0] 
    if record[1]:     date = record[1]
    if record[2].lstrip(): 
        article = extract_fn(record[2]) 
        if article.title and article.title.lstrip(): title = re.sub(r'\s+', ' ', article.title)
        if article.body and article.body.lstrip():   
            body = re.sub(r'\s+', ' ', article.body)
            # body = emoji.clean_emoji_and_symbols(body)
    for field in (ID, date, title): 
        f.write(field)
        f.write(u'\t')
    #f.write(u'nhvyTOMz7ySY5tXkDsWn')
    f.write(body)
    f.write(u'\n')
    

def main():
    parser = argparse.ArgumentParser(description="""Read HTML from 
            html_docs/M_YYYY_html.tsv, use Lynx extractor to convert article 
            body field to text. Write unicode to lynx_docs/M_YYYY_lx.tsv. """)
    parser.add_argument('-y', '--year', type=int, required=True,
                        help='a starting year for the db query')
    parser.add_argument('-m', '--month', type=int, required=True,
                        help='a starting month for the db query')
    args = parser.parse_args()
    lx = wrappers.LynxExtractor()
    html_to_text(args.year, args.month, lx)


if __name__ == "__main__":
    main()
