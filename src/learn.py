
###############################################################################
# Learn the neural network parameters
###############################################################################

import sys
import os
import re
import codecs

from vec4net import make_list, WINDOW, SHAPE
SIZE = WINDOW*SHAPE

import network

def get_files(ft='train'):
    "Get train/test file list for further process"
    path_data = '../dat/'
    tmp_lst = os.listdir(path_data)
    file_lst = []
    for item in tmp_lst:
        if re.search('\A'+ft+'.*\.iob2', item):
            file_lst.append(path_data + item)
    return file_lst

def get_sentences(file_lst, RUN):
    "Get sentences and coresponding tags from file list in CV no. RUN and RUN+1"
    sentences = [] 
    item = file_lst[RUN]
    f = codecs.open(item, encoding='utf-8', mode = 'r', errors = 'ignore')
    sent = []
    tags = []
    word = ''
    tag  = ''
    for line in f:
        line = line.lower().split() # TODO: Think about lower!
        if not line: # End of sentence. 
            if word:
                word = '' # Flush word buffer.
                tag  = ''
            if sent:
                sentences.append((sent, tags))
                sent = [] # Flush sentence buffer.
                tags = []
            continue
        word, tag = line
        sent.append(word)
        tags.append(tag[0]) # First letter
    f.close()
    if sent: sentences.append((sent, tags))
    return sentences

def make_train_test(RUN):
    train = []
    test  = []
    train_list = get_files('train')
    train_sent = get_sentences(train_list, RUN)
    for s in train_sent:
        train += list(make_list(s))
    test_list  = get_files('test')
    test_sent  = get_sentences(test_list, RUN)
    for s in test_sent:
        test += list(make_list(s))
    return train, test


# Network learning, this is the awesome part
if __name__ == '__main__':
    HIDDEN = 30
    EPOCHS = 30
    MINI_BATCH_SIZE = 10
    ETA = 0.5
    LAMBDA = 5.0
    accuracy = {}
    n_args = len(sys.argv)
    if n_args == 1:
        a = 0
        b = 5
    elif n_args ==  2:
        a = int(sys.argv[1])
        b = a+1
    else:
        a = int(sys.argv[1])
        b = int(sys.argv[2]) + 1
    try:
        assert 0 <= a < b <= 5
    except:
        print('''
              Usage: python3 learn.py [from] [to]
              ===================================
              * [from] and [to] is optional, default to 0 and 4, i.e. run full
              5 cross-validation from 0 to 4
              * If specified, [from] and [to] must meet the inequility
              0 <= [from] < [to] <= 4
              ''')
        sys.exit(1)
    # We run a to b cross-validation and take the average accuracy
    ranges = range(a, b)
    for RUN in ranges:
        print('Run cross-validation #{}'.format(RUN))
        net = network.Network([SIZE, HIDDEN, 3])
        training_data, test_data = make_train_test(RUN)
        # training_data = training_data[:1000]; test_data = test_data[:100]
        acc = net.SGD(training_data, EPOCHS, MINI_BATCH_SIZE, ETA, 
                      lmbda=LAMBDA,
                      evaluation_data=test_data,
                      monitor_evaluation_accuracy=True)
        # Take the last (not best) accuracy and length of the test set
        accuracy[RUN] = (acc[-1], len(test_data))
        # Save the model for later use
        net.save('../var/{}hidden-{}epochs-{}batch-{}eta-{}lambda-{}window-{}shape-{}run.net'.\
            format(HIDDEN, EPOCHS, MINI_BATCH_SIZE, ETA, LAMBDA, WINDOW, SHAPE, RUN))
    # Display the result
    print("===================")
    print("FINAL RESULTS:")
    print("===================")
    for i in ranges:
        print("Accuracy on CV #{0} is {1:.2f} %"\
              .format(i, accuracy[i][0]/accuracy[i][1]*100))
    print("===================")
    a = sum([accuracy[i][0] for i in ranges])
    b = sum([accuracy[i][1] for i in ranges])
    print("Average accuracy: {:.2f} %".format(a/b*100))




