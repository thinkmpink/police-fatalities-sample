# Event-labeling pipeline

Events are parameterized by a victim name, a article document ID, an incident date, and a scrape date. 
### Dependencies / Notes
  - Assumes Hobbes directory structure with a `newsevents` [clone] at `/home/USER/newsevents/`.
  - Recommended: use a [virtual environment] and install all requirements.
If you will be actively developing this code, install `pip-tools`, then run: `your/virtualenv/bin/pip-sync`. More info at the [pip-tools] dev blog. (This generally seems like good Python package management.) Otherwise, `your/virtualenv/bin/pip install -r post_extract_tests/requirements.txt` will do.
  - For any given month of fatality events, the scripts must be run in the following order: text extraction, then name extraction, then classification, then evaluation. *(The classification step can be skipped.)*
  - More detailed usage information can be found by entering `python <script_name>.py -h` or manually looking in the docstrings.

### Text extraction

###### `post_extract_tests/html_docs/*`
  - HTML documents collected from `news_readonly`, saved on disk.
  - Scraped within some month: docs between YYYY/M/D and YYY(Y+1/Y)/M+1/D+14.
  - Result file: `M_YYYY_html.tsv`. Each line is tab-separated (docid, scrape_date, raw HTML)
  - Usage: `python get_html.py -m5 -y2015`
  - Running time per 100,000 documents: 14 minutes

###### `post_extract_tests/lynx_docs/*`
  - Clean raw HTML by removing JS and other markup. Uses Lynx, a UNIX-based text extractor.
  - Write to `lynx_docs/M_YYYY_lx.tsv` on disk. 
  - Usage: `python get_lx_docs.py -m5 -y2015`
  - Running time per 100,000 documents: 29 minutes

### Name extraction

###### `post_extract_tests/all_names/*`
  - Extract all names from `lynx_docs/M_YYYY_lx.tsv`. 
  - A name is any token or token span for which an NER tool outputs the tag 'PERSON'.
  - Use [spaCy] or [CoreNLP] to identify names. Put them in `all_names_M_YYYY.json` under `'name_candidates': ['Bob', ...]`. Also extracts fatality verbs.
  - Get the names and metadata: `python ner.py -m5 -y2015 -sp` (to use spaCy). 
  - Get only the names ouputted by `ner.py`: `python json_to_txt_names.py -m5 -y2015`
  - Expected running time per 100,000 documents: 37 minutes
  - Note: CoreNLP and SpeedRead, two semi-supported NER tools, are deprecated due to speed and/or brittleness on string encodings. Use spaCy.


### Classification

###### Labeling
  - Label (docid, name) pairs with {1, -1}
    - 1: [name] was the victim of a police killing
    - -1: [name] was not the victim of a police killing
    - 1 is chosen if [HAPNIS]-normalized [name] (see below) matches a HAPNIS normalized name in the gold standard. -1 is chosen otherwise.
  - Usage: `python classifiers/pseudolabel_names.py -m5 -y2015 -j all_names/all_names_5_2015.json`
  - Label (sentence,) with {1, -1}. 
    - 1: [sentence] contains the name of someone killed by police. 
    - -1: [sentence] does not contains the name of someone killed by police
    - 1 is chosen if, for the document with ID and name (docid, name) containing [sentence], the pseudolabel for (docid, name) is 1 and the sentence contains either the first name or last name of [name]. -1 is chosen otherwise.
  - Usage: `python classifiers/pseudolabel_sents.py -f lynx_docs/5_2015_lx.tsv -l classifiers/5_2015_name_labels.json`
  - Expected running time per 100,000 documents: 4 hours and 45 minutes

###### Training
  - Train a Naive Bayes classifier on some numpy ndarray in (N x m) of feature vectors, where N is the number of sentences and m is the number of features. Currently, this is four features: (1) presence of fatal verbs, (2) count of fatal verbs, (3) count of dobj of fatal verbs, (4) count of nsubjpass of fatal verbs.
  - Serialize trained model to disk.
  - Usage: `python classifiers/train.py -m5 -y2015 -clf 'nb'`. Use `-h` after the program name for other options. 
  - Expected running time per 100,000 documents: 

###### Testing
  - Test the trained model on a test set. 

### Evaluation

###### `pr_eval.py`
  - Calculate precision and recall on name extraction or classification.
  - Gold standard names are found in `victim_names/M_YYYY_names_strict_month.tsv`
  - Retrieved names can be found in `all_names/M_YYYY_names_only.txt`. (Run `json_to_text_names.py` to get the `names_only` file.)
  - Filter using [HAPNIS]-disambiguated "fore_name sur_name" pairs.



[//]: #
   [clone]: <https://github.com/SoCLlab/newsevents.git>
   [CoreNLP]: <http://stanfordnlp.github.io/CoreNLP/>
   [HAPNIS]: <http://www.umiacs.umd.edu/~hal/HAPNIS/>
   [spaCy]: <https://spacy.io/>
   [virtual environment]: <https://virtualenv.pypa.io/en/stable/>
   [pip-tools]: <http://nvie.com/posts/better-package-management/>


