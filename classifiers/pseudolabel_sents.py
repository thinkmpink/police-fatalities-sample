import argparse, functools as ft, getpass
import itertools as it, json, numpy as np, time
from spacy.en import English
from spacy.tokens.doc import Doc
from pathos.pp import ParallelPool
from pathos.threading import ThreadPool


FATAL_SYNSET = set(["dead","death","died","die","fatal","killed",
                "kill","lethal","murder", "shoot", "shot", "shooting"
                "killing", "deaths", "shootings", "killings"])

"""
Returns 1 if the target function of a token returns true.
Recurses to the root, checking each head using the target function. If the root 
is reached without hitting the target, return 0.
"""
def matches_head(tok, target):
    if target(tok): return 1
    elif tok.dep_ == 'ROOT': return 0
    else: return matches_head(tok.head, target)

#head_in_fv = ft.partial(matches_head, target=lambda x: x in FATAL_SYNSET)


"""
Extract features from some window of text: a char span or a sentence, etc.
Return a list containing the features
:param text: the text from which to extract the features
:param name: the victim name associated with the label
:param features: the features to extract, default is unigram counts
:param fatal_vbs: a synset (set) of fatality verbs
"""
def extract_features(text, name, features, fatal_vbs=FATAL_SYNSET):
    feats = [0]*4
    if 'fatal_verbs' in features:
        num_vbs = len([word for word in text if word.orth_ in fatal_vbs])
        ## if we just pick this feature, can short circuit
        feats[0] = 1 if num_vbs else 0
        feats[1] = num_vbs
    if 'parse' in features: 
        dobjs = [tok for tok in text if tok.dep_=='dobj'] #TODO: gens not listcomps
        ct_fv_dobj = len([tok for tok in dobjs if tok.head.orth_ in fatal_vbs])
        #ct_fv_dobj = len(filter(head_in_fv, filter(is_dobj, text)))
        ##ct_fv_dobj = sum(1 for _ in it.ifilter(head_in_fv, it.ifilter(is_dobj, text)))
        feats[2] = ct_fv_dobj
        nsps = [tok for tok in text if tok.dep_=='nsubjpass']
        ct_fv_nsubjpass = len([tok for tok in nsps if tok.head.orth_ in fatal_vbs])
        #ct_fv_nsubjpass = len(filter(head_in_fv, filter(is_nsubjpass, text)))
        ##ct_fv_nsubjpass = sum(1 for _ in it.ifilter(head_in_fv, it.ifilter(is_nsubjpass, text)))
        feats[3] = ct_fv_nsubjpass
    return feats


"""
Gets first instances where parts of a "first_name last_name" are substrings 
in some context frame (e.g. sentence, token_span)
"""
def get_name_matches(name, text):
    #matches = []
    parts = name.split()
    first = parts[0].capitalize()
    last  = parts[1].capitalize()
    first_l = first.lower()
    last_l  = last.lower()
    if first in text: return True #matches.append(first)
    if last in text: return True #matches.append(last)
    if first_l in text: return True #matches.append(first_l)
    if last_l in text: return True #matches.append(last_l)
    else: return False
    #return matches

"""
Returns a sentence label with all demanded features. The label means:
the sentence contains the name of a victim.
The returned tuples contain the following:
 - label: 1 if the sentence contains a victim of a police killing, -1
   otherwise
 - name: the name of the victim associated with the label 
 - matches: a boolean of whether the name was in the sentence
 - feats: an array of integers representing the selected features
:param input_: an iterable of unicode documents
:param labels_: a list of labels (as dicts)
:nlp: a spaCy NLP object that can run a tokenizer, tagger, POS, dep parse
"""
def process_all_docs(input_, labels_, n_threads, batch_size, nlp):
    docs = (doc.decode('utf-8') for doc in input_)
    #pool = ParallelPool(nodes=n_threads)
    pool = ThreadPool(nodes=n_threads)
    doc_queue = nlp.pipe(docs, batch_size=batch_size, n_threads=n_threads)
    return pool.imap(process_doc, doc_queue, it.repeat(labeled_tuples))

def process_doc(doc, labeled_tuples):
    docid   = doc[0].orth_
    doc_labels = [label for label in labeled_tuples if label['docid']==docid]
    for labeled_tuple in doc_labels:
        name        = labeled_tuple['name']
        label       = labeled_tuple['victim']
        contexts    = doc.sents 
        for context in contexts:
            feats   = extract_features(context, name, ['fatal_verbs', 'parse'])
            matches = get_name_matches(name, context.text)
            yield (label, name, matches, feats)
    

def main(n_threads=2, batch_size=4000):
    parser = argparse.ArgumentParser(description="""Extract features from a 
            document containing docids in the beginning of each line. Use
            (docid, name) pairs to locate the document, then extract relevant
            features. Requires spaCy for NLP pipeline""")
    parser.add_argument('-f', '--readfile', type=str, required=True,
            help="Data filepath, e.g. lynx_docs/<dataset>_lx.tsv")
    parser.add_argument('-l', '--labelfile', type=str, required=True,
            help="Label filepath, e.g. classifiers/<dataset>_labels.json")
    parser.add_argument('-t', '--nthreads', type=int,
            help="Number of threads for processing docs. Recommend 30.")
    parser.add_argument('-b', '--batchsize', type=int,
            help="Number of documents to queue. Recommend 10000.")
    parser.add_argument('-d', '--ndocs', type=int, required=True,
            help="Number of docs to process. Try wc -l <READFILE>")
    args = parser.parse_args()

    if args.nthreads: n_threads = args.nthreads
    if args.batchsize: batch_size = args.batchsize

    with open(args.labelfile, 'r') as l
        labels = [json.loads(line) for line in l]

    f = open(args.readfile, 'r')
    docs = (doc for doc in f)
    print "Loading spaCy ..."
    load_time   = time.clock()
    nlp         = English()
    load_time   = time.clock() - load_time
    print "Successfully loaded spaCy English in ", str(load_time), "s"

    max_sent_per_doc = 10000
    features_X = np.zeros((args.ndocs * max_sent_per_doc, 4), dtype=np.int8)
    features_y = np.zeros((args.ndocs * max_sent_per_doc,), dtype=np.int8)

    #for i, info in enumerate(sentence_feats):
    i = 0
    sentence_feats = process_all_docs(docs, labels, n_threads, batch_size, nlp)
    for gen in sentence_feats:
        for info in gen:
            if not i%1000: print i, " docs processed"
            feats = info[3]
            name_label = info[0]
            name_in_sent = info[2]
            label = 1 if name_label==1 and name_in_sent else -1 
            features_X[i] = feats
            features_y[i] = label
            i += 1
    print "Num sentences:", i
    np.save("train_X_" + args.labelfile, features_X)
    np.save("train_y_" + args.labelfile, features_y)

    f.close()


if __name__ == "__main__":
    main()














################## IN PROGRESS / DEPRECATED ###################



"""
Deserialize a serialized parse and try the same extraction logic as process_all_labels 
"""
def process_all_labels_from_bytes(label_handle, logs, nlp):
    labeled_tuples = [json.loads(line) for line in label_handle]
    nlp_doc = Doc(nlp.vocab)
    handles = (open(f, 'rb') for f in logs)
    b_gens = (Doc.read_bytes(h) for h in handles)
    docs = decode_docs(nlp_doc, b_gens)
    for line in docs:
        docid = line[0].orth_
        doc_labels = filter(lambda x: x['docid']==docid, labeled_tuples)
        for labeled_tuple in doc_labels:
            name = labeled_tuple['name']
            label = labeled_tuple['victim']
            contexts = line.sents
            for context in contexts:
                feats = extract_features(context,name, ['fatal_verbs', 'parse'])
                matches = get_name_matches(name, map(lambda x: x.orth_, context))
                yield (label, name, matches, feats, context)


def decode_docs(nlp_doc, b_gens):
    for b_gen in b_gens:
        for b_doc in b_gen:
            yield nlp_doc.from_bytes(b_doc)

"""
Returns all token spans of length `context param` in `doc`
Ex: doc = "Hi there dog", context_param=2
    assert span_contexts(doc, context_param) == [u'Hi there', u'there dog']
:param spacy_doc: a spacy document object from which to pull the windows
:param context_param: number of words window
"""
#TODO: BUGGY! Returns empty list if context param > len(tokens(doc))
def spacy_span(spacy_doc, context_param=10):
    return map(lambda x: " ".join(x),
        zip(*(doc[i:] for i in xrange(context_param)))
    )
