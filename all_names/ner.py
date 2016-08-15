from stanford_corenlp_pywrapper import CoreNLP
import argparse, codecs, getpass, itertools, json, time
from spacy.en import English

"""
Return unique names found in the Lynx-extracted doc
:param doc: line with 4 article fields
:param proc: CoreNLP ner object
:param fatal_synset: list of fatality verbs
"""
def get_unique_names(doc, proc, fatal_synset):
    metadata  = doc.split(None, 3)
    docid, date = [""]*2
    names     = []
    sentences = []
    fatal_verbs = []
    docid     = metadata[0]
    date      = metadata[1]
    sentences = proc.parse_doc(metadata[3])[u'sentences'] 
    for sent in sentences:
        wrote_name = False
        for code, name in itertools.izip(sent[u'ner'], sent[u'lemmas']):
            if name in fatal_synset: fatal_verbs.append(name)
            if code == u'PERSON' and not wrote_name:
                wrote_name = True
                names.append(name)
            elif code == u'PERSON' and wrote_name:
                names[-1] = " ".join([names[-1], name])
            else: wrote_name = False

    return {'docid': docid, 
            'date': date, 
            'fatal_verbs': fatal_verbs, 
            'name_candidates': list(set(names))}


"""
More "functional" implementation of get_unique_names().
Uses CoreNLP
"""
def get_unique_names_f(doc, proc, fatal_synset):
    is_name = lambda name: 'name' if name[0]==u'PERSON' else ''
    snd     = lambda (x, y): y
    in_fs   = lambda x: x in fatal_synset
    
    metadata    = doc.split(None, 3)
    docid, date = [""]*2
    names       = []
    fatal_verbs = []
    docid       = metadata[0]
    date        = metadata[1]
    sentences = proc.parse_doc(doc)[u'sentences']
    for sent in sentences:
        fatal_verbs.extend(filter(in_fs, sent[u'lemmas']))
        code_and_name = zip(sent[u'ner'], sent[u'lemmas'])
        g = itertools.groupby(code_and_name, is_name)
        for tag, name_chunks in g:
            if str(tag): names.append(" ".join(map(unicode, map(snd, name_chunks))))
    return {'docid': docid, 
            'date': date, 
            'fatal_verbs': fatal_verbs,
            'name_candidates': list(set(names))}



"""
SpaCy "functional" implementation of get_unique_names().
:param doc:             document from which to extract names
:param spacy_nlp_obj:   spaCy English NLP object
:param fatal_synset:    list of common fatality verbs
:param is_name:         function to identify a 'PERSON' token
:param tok_to_uni:      function to get unicode token
:param in_fs:           function to identify whether token is in fatal_synset
"""
def sp_get_unique_names_f(doc, spacy_nlp_obj, fatal_synset, is_name, tok_to_uni,
        in_fs):
    doc         = doc.decode('utf-8')
    metadata    = doc.split(None, 3)
    docid, date = [""]*2
    docid       = metadata[0]
    date        = metadata[1]
    tokens      = spacy_nlp_obj(doc)
    ents        = list(tokens.ents)
    names       = map(tok_to_uni, filter(is_name, ents))
    fatal_verbs = map(tok_to_uni, filter(in_fs, tokens))
    return {'docid': docid, 
            'date': date, 
            'fatal_verbs': fatal_verbs,
            'name_candidates': list(set(names))}



"""
Write name objects to 'all_names/all_names_<dataset>.json' in the format:
[{docid: 12345, name_candidates: ["John Athan", "Tim Othy", ...]}, ...]
"""
def main():
    parser = argparse.ArgumentParser(description="""Read articles from 
            lynx_docs/M_YYYY_lx.tsv. Extract all names using CoreNLP (default),
            or spaCy and get fatality verbs. 
            Write to all_names/all_names_M_YYYY.json""")
    parser.add_argument('-sp', '--spacy', action='store_true', help="Use spaCy for NER")
    parser.add_argument('-y', '--year', type=int, help='incident year', required=True)
    parser.add_argument('-m', '--month', type=int, help='incident month', required=True)
    args =  parser.parse_args()

    fpath   = '/home/{}/newsevents/post_extract_tests/'.format(getpass.getuser())
    read_f  = '{}lynx_docs/{:d}_{:d}_lx.tsv'.format(fpath, args.month, args.year)
    write_f = '{}all_names/all_names_{:d}_{:d}.json'.format(fpath, args.month, args.year)
    
    fatal_synset = set(["dead","death","died","die","fatal","killed","kill","lethal","murder"])

    w = codecs.open(write_f, 'w', 'utf-8')

    if args.spacy:
        print "Opening file {} in read mode".format(read_f)
        with open(read_f, 'r') as r:
            print "Loading spaCy ..."
            load_time   = time.clock()
            nlp         = English(parser=False)
            load_time   = time.clock() - load_time
            print "Succesfully loaded spaCy English in ", str(load_time), "s"
            is_name     = lambda name: name.label_ == 'PERSON' 
            tok_to_uni  = lambda x: x.orth_
            in_fs       = lambda x: x.lower_ in fatal_synset
            doc_time    = time.clock()
            doc_count   = 0
            for doc in r:
                doc_count += 1
                json.dump(sp_get_unique_names_f(
                    doc, nlp, fatal_synset, is_name, tok_to_uni, in_fs
                ), w)
                if not doc_count % 1000:
                    print doc_count, " docs processed."
                    print "Ave time/doc:", (time.clock() - doc_time)/doc_count," s"
                w.write('\n')

    else:
        with open(read_f, 'r') as r:
            proc = CoreNLP(
                    configdict = {'annotators':'tokenize, ssplit, pos, lemma, ner'},                   
                    output_types = ["ner", "lemmas"], 
                    corenlp_jars = ["/home/sw/corenlp/stanford-corenlp-full-2015-04-20/*"]
            )
            for doc in r: 
                #json.dump(get_unique_names(doc, proc, fatal_synset), w)
                json.dump(get_unique_names_f(doc, proc, fatal_synset), w)
                w.write("\n")
    w.close()


if __name__ == "__main__":
    main()
