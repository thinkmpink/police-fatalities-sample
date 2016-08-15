import argparse, getpass, psycopg2, re
DAY_OFFSET = 14


"""
Query the database "page_downloads" for raw HTML
"""
def get_page_dl_raw(conn, year, month, day):
    cur = conn.cursor()
    start_date = "{:04d}-{:02d}-{:02d}".format(year, month, day)
    end_month = (month+1) % 12 or 12
    end_year = year+1 if end_month==1 else year
    end_date = "{:04d}-{:02d}-{:02d}".format(end_year, end_month, day+DAY_OFFSET) 
    query = ("""SELECT id, date(downloadtime), page_content
                FROM page_downloads
                WHERE date(downloadtime) >= '{0}'
                      AND date(downloadtime) <= '{1}'
                ;""").format(start_date, end_date)
    fpath  = '/home/{}/newsevents/post_extract_tests/'.format(getpass.getuser())
    writef = '{}html_docs/{:d}_{:d}_html.tsv'.format(fpath, month, year)
    cur.execute(query)
    white_sp = re.compile('\s+')
    with open(writef, 'wb') as f:
        write = f.write
        for record in cur: 
            write(str(record[0]))
            write('\t')
            write(record[1].strftime('%Y-%m-%d'))
            write('\t')
            write(re.sub(white_sp, ' ', record[2]))
            write('\n')


def main():
    parser = argparse.ArgumentParser(description="""Read HTML from readonly 
            news db, write the byte data to disk, tab-separated docid, date, 
            and 1 article body per line. Unicode is assumed.""")
    parser.add_argument('-y', '--year', type=int, required=True,
            help='a starting year for the db query')
    parser.add_argument('-m', '--month', type=int, required=True,
            help='a starting month for the db query')
    parser.add_argument('-d', '--day', type=int, required=True,
            help='a starting day for the db query')
    args = parser.parse_args()
    # Password removed for security
    conn_str = "dbname='news' user='news_readonly' host='localhost' password=''"
    conn = psycopg2.connect(conn_str)
    page_dl_raw = get_page_dl_raw(conn, args.year, args.month, args.day)


if __name__ == "__main__":
    main()

