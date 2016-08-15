import argparse, copy, functools as ft, getpass, numpy as np, pickle
from collections import defaultdict
from math import exp, log, floor
from sklearn.naive_bayes import GaussianNB
LOG_PROB_OF_ZERO = -1000

#def load_data(train_X_w_buf_file, train_Y_w_buf_file):
def load_data():
    train_X_w_buf = np.load('train_X_5_2015_name_labels.json.npy')
    train_y_w_buf = np.load('train_y_5_2015_name_labels.json.npy')
    train_y = train_y_w_buf[train_y_w_buf.nonzero()]
    train_X = train_X_w_buf[:train_y.size, :]
    return [train_X, train_y]

"""
Returns a nested dictionary of p(x_i | y):
    - assume m features, n data cases
    - for feature_i in {1..m}, get prob(feature_i | y) for y in {-1, 1}
    - dict will have the form p(val_j | feature_i, y) == dict[i][j][y]
:param X: an n*m np.ndarray
:param y: an n*1 np.ndarray
"""
#TODO: do this with a 3D tensor, not a dict
def get_log_probs(X, y):
    log_probs = {}
    num_feats = X.shape[1]
    pos_class = X[(y==1), :]
    neg_class = X[(y==-1), :]
    pos_size = pos_class.shape[0]
    neg_size = neg_class.shape[0]
    print "POS class size", pos_size
    print "NEG class size", neg_size
    default_val = [LOG_PROB_OF_ZERO, LOG_PROB_OF_ZERO]
    for feat in range(num_feats):
        log_probs[feat] = defaultdict(lambda: default_val)
        feat_data = X[:, feat]
        feat_data_pos = pos_class[:, feat]
        feat_data_neg = neg_class[:, feat]
        assert feat_data.size == y.size
        poss_vals_for_feat = np.unique(feat_data)
        for val in poss_vals_for_feat:
            log_probs[feat][val] = [0, 0]
            count_val_pos = feat_data_pos[feat_data_pos==val].shape[0]        
            count_val_neg = feat_data_neg[feat_data_neg==val].shape[0]        
            log_probs[feat][val][0] = log(float(count_val_pos+1)/(pos_size+1)) 
            log_probs[feat][val][1] = log(float(count_val_neg+1)/(neg_size+1)) 
            print "Feat: ", feat, " Val: ", val, " Log prob [+,-]: ", log_probs[feat][val]

    return log_probs


def tt_split(X, y, train_size):
    train_pct  = float(train_size)/100
    train_size = int(train_pct * y.size)
    idxs       = np.random.permutation(y.size)
    train_idxs, test_idxs = idxs[:train_size], idxs[train_size:]
    train_X, train_y      = X[train_idxs, :], y[train_idxs]
    test_X, test_y        = X[test_idxs, :], y[test_idxs]
    return [train_X, train_y, test_X, test_y]



def classify(X, log_probs, prior):
    def get_POS_probs(data, feat): 
        probs = np.asarray(map(lambda val: log_probs[feat][val][0], data))
        return probs

    def get_NEG_probs(data, feat): 
        probs = np.asarray(map(lambda val: log_probs[feat][val][1], data))
        return probs

    pos_log_prior = log(prior)
    neg_log_prior = log(float(1)-prior)
    #print "Prior for POS:", exp(pos_log_prior)
    #print "Prior for NEG:", exp(neg_log_prior)
    num_data_cases, num_feats = X.shape
    pred_y = np.zeros((num_data_cases,1))
    
    prob_arr_POS = np.zeros((num_data_cases, num_feats))
    prob_arr_NEG = np.zeros((num_data_cases, num_feats))
    
    for i in range(num_feats):
        prob_arr_POS[:, i] = get_POS_probs(X[:, i], i)
        prob_arr_NEG[:, i] = get_NEG_probs(X[:, i], i)
    assert prob_arr_POS.shape == prob_arr_NEG.shape == X.shape

    prob_arr_POS = prob_arr_POS.sum(axis=1) + pos_log_prior
    prob_arr_NEG = prob_arr_NEG.sum(axis=1) + neg_log_prior
    assert prob_arr_POS.shape == prob_arr_NEG.shape 

    # argmax step
    pred_y[prob_arr_POS >= prob_arr_NEG] = 1
    pred_y[prob_arr_POS < prob_arr_NEG] = -1
    assert 0 not in pred_y
    
    #TODO: use np.apply_along_axis w sep func
    return pred_y.flatten()


def cascade_train(train_X, train_y, prior, num_classifiers):
    log_prob_arr = []
    X = copy.deepcopy(train_X)
    y = copy.deepcopy(train_y)
    for i in range(num_classifiers):
        print "Classifier #", i, " dim (X, test_y)", X.shape, y.shape
        cur_clf = get_log_probs(X, y)
        log_prob_arr.append(cur_clf)
        pred_y = classify(X, cur_clf, prior)
        print "Pred #", i, " dim", pred_y.shape
        #Update prior? Is that cheating?
        pred_NEG = pred_y==-1
        test_NEG = y==-1
        true_NEG = pred_NEG & test_NEG
        remain_idxs = np.logical_not(true_NEG)
        X = X[remain_idxs, :]
        y = y[remain_idxs]
    return log_prob_arr


def cascade_rule(x):
    return 1 if -1 not in x else -1


def cascade_classify(X, log_prob_arr, prior):
    classifications = np.zeros((X.shape[0], len(log_prob_arr)))
    for i, clsfr in enumerate(log_prob_arr):
        classifications[:, i] = classify(X, clsfr, prior)
        print "Cascade classifier ", i, " done"
    #for i in range(X.shape[0]):
    print "Applying cascade rule..."
    y = np.apply_along_axis(cascade_rule, 1, classifications)
    return y.flatten()

def get_accuracy(pred_y, test_y):
    print "Num -1 in pred:", pred_y[pred_y==-1].size
    #print "Num 0 in pred:", pred_y[pred_y==0].size
    print "Num 1 in pred:", pred_y[pred_y==1].size
    print "Num -1 in test:", test_y[test_y==-1].size
    #print "Num 0 in test:", test_y[test_y==0].size
    print "Num 1 in test:", test_y[test_y==1].size
    
    test_POS = test_y==1
    pred_POS = pred_y==1
    corr_POS = pred_POS[test_POS & pred_POS].size
    print "Num corr POS predictions:", corr_POS
    num_corr = pred_y[pred_y==test_y].size
    print "Total accuracy:", float(num_corr)/pred_y.size    
    return float(num_corr)/pred_y.size    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-clf', '--classifier', type=str, required=True,
            help='The type of classifier you want. Currently supported:
                    Naive Bayes: "nb", Gaussian Naive Bayes: "gnb"')
    parser.add_argument('-m', '--month', type=int, help='The month to classify.')
    parser.add_argument('-y', '--year', type=int, help='The year to classify.')
    parser.add_argument('-X', '--Xlabelpath', type=str, help='Binary .npy filepath
            containing X data. Must be in N by m. Use only as alternative to 
            providing month and year data')
    parser.add_argument('-y', '--ylabelpath', type=str, help='Binary .npy filepath
            containing Y labels. Must be in N by 1. Use only as alternative to 
            providing month and year data')
    parser.add_argument('--prior', type=int, help='Point estimate for prior of 
            POS class')
    args = parser.parse_args()

    if args.classifier == 'nb': 
        clf = get_log_probs(train_X, train_y)
        
    elif args.classifier == 'gnb':
        gnb = GaussianNB()
        clf = gnb.fit(train_X, train_y)
    
    data_X, data_y = load_data()
    print data_X.shape
    print data_y.shape
    print "feat 3 data vals", np.unique(data_X[:, 2])
    print "feat 4 data vals", np.unique(data_X[:, 3])
    #data_X = data_X[:, 1:]
    train_X, train_y, test_X, test_y = tt_split(data_X, data_y, 70)
    #log_probs = get_log_probs(train_X, train_y)
    #pred_y = classify(test_X, log_probs, 0.0075)
    #log_prob_arr = cascade_train(train_X, train_y, 0.01, 2)
    #pred_cascaded_y = cascade_classify(test_X, log_prob_arr, 0.01)
    #gnb = GaussianNB()
    #pred_y = gnb.fit(train_X, train_y).predict(test_X)
    #print "pred dims:", pred_cascaded_y.shape
    #print "test dims:", test_y.shape
    print get_accuracy(pred_y, test_y)
    #print get_accuracy(pred_cascaded_y, test_y)


if __name__ == '__main__':
    main()
