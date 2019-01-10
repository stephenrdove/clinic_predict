import numpy as np 
from sklearn.ensemble import RandomForestClassifier
import torch
from torch import nn
from torch import optim
from collections import OrderedDict


class DynamicNetwork(nn.Module):

    def __init__(self, hidden_sz, vocab_sz, rnn_layers=1,embed_sz=10):
        """
        :param hidden_sz (int): The size of our RNN's hidden state
        :param embedding_lookup (str): The type of word embedding used.
                                       Either 'glove', 'elmo', 'both', or 'random'.
        :param num_layers (int): The number of RNN cells we want in our net (c.f num_layers param in torch.nn.LSTMCell)
        """
        super(DynamicNetwork, self).__init__()
        self.hidden_sz = hidden_sz
        self.rnn_layers = rnn_layers
        self.embed_sz = embed_sz
        self.vocab_sz = vocab_sz
        self.embedding_lookup = nn.Embedding(self.vocab_sz,self.embed_sz)
        hidden_linear = 25

        self.dropout = nn.Dropout(p=0.5)
        self.gru = nn.GRU(self.embed_sz, self.hidden_sz, self.rnn_layers,batch_first=True,bidirectional=False)

        layers = OrderedDict([
                    ('lin0',nn.Linear(self.hidden_sz, hidden_linear)),
                    ('relu', nn.ReLU()),
                    ('lin1',nn.Linear(hidden_linear,2))
                    #,('softmax', nn.LogSoftmax())
                ])
        self.net = nn.Sequential(layers) 


    def forward(self, tokens, seq_lens):
        """ The forward pass for our model
                 :param tokens: vectorized sequence inputs as token ids.
                 :param seq_lens: original sequence lengths of each input (prior to padding)
        """
        curr_batch_size = seq_lens.shape[0]

        # the embeddings for the token sequence
        embeds = self.embedding_lookup(tokens) 
        dropped_embeds = self.dropout(embeds)
        
        # Sort seq_lens and embeds in descending order of seq_lens
        sorted_lens , indices = torch.sort(seq_lens,descending=True)
        sorted_embeds = dropped_embeds[indices]

        pack_padded = nn.utils.rnn.pack_padded_sequence(sorted_embeds,sorted_lens,batch_first=True)

        # Apply the RNN over the sequence of packed embeddings
        _ , hidden_state = self.gru(pack_padded)
        hidden_state = torch.squeeze(hidden_state)
        
        # Pass the encoding through the classifier 
        label_dist = self.net(hidden_state)
        label_dist = label_dist.reshape(curr_batch_size,-1)

        _, unsorted_indices = indices.sort(0)
        output = label_dist[unsorted_indices]
      
        return output

def initialize_model(vocab):
    hidden_sz = 100
    rnn_layers = 1
    vocab_sz = len(vocab)
    embed_sz = 10
    model = DynamicNetwork(hidden_sz,vocab_sz,rnn_layers,embed_sz)
    print('\t\tModel Initialized')
    return model

def train_dynamic(model,X,seq_lens,y,num_epoches=5,learning_rate=0.01,batch_sz=20,mode='ed'):
    train_len = len(y)
    if mode == 'ed':
        weight = np.asarray([0.2,0.8])
    elif mode == 'op':
        weight = np.asarray([0.003,0.997])
    else:
        weight = np.asarray([1.0,1.0])
    weight = torch.from_numpy(weight)
    weight = weight.type(torch.FloatTensor)
    loss_func = nn.CrossEntropyLoss(weight=weight) 
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(num_epoches):
        running_loss = 0.0
        for j in range(int(train_len / batch_sz)):
            i = j * batch_sz
            tokens = X[i:i+batch_sz]
            lens = seq_lens[i:i+batch_sz]
            labels = y[i:i+batch_sz]

            model.train() 

            model.zero_grad() # clear gradients (torch will accumulate them)
            probs = model(tokens,lens) # Run the forward pass
            loss = loss_func(probs, labels) # Calculate the loss
            loss.backward() # Back propogate
            optimizer.step() # Update Steps

            running_loss += loss.item()
    
    print('\t\tTraining Finished')


def test_dynamic(model,X,seq_lens):
    y_pred = []
    softmax = nn.Softmax(1)
    for i in range(len(X)):
        model.eval()
        with torch.no_grad():
            output = model(X[i:i+1],seq_lens[i:i+1])
            probs = softmax(output)
            list_probs = []
            for item in probs[0]:
                list_probs.append(item.item())
            y_pred.append(list_probs)
    print('\t\tTesting Finished')
    return np.asarray(y_pred)


def static_clf(X,y):
    clf = RandomForestClassifier(n_estimators=10)
    clf.fit(X,y)
    return clf


def dynamic_clf(X,seq_lens,y,test_X,test_seq_lens,vocab,mode):
    tokened_X = np.asarray([[vocab[event] if event in vocab else vocab['*UNK*'] for event in x] for x in X])
    tokened_test_X = np.asarray([[vocab[e] if e in vocab else vocab['*UNK*'] for e in x] for x in test_X])
    tokened_X = torch.from_numpy(tokened_X)
    tokened_test_X = torch.from_numpy(tokened_test_X)
    seq_lens = torch.from_numpy(seq_lens)
    test_seq_lens = torch.from_numpy(test_seq_lens)
    y = torch.from_numpy(np.asarray(y))
    
    model = initialize_model(vocab)
    train_dynamic(model,tokened_X,seq_lens,y,1,0.01,20,mode=mode)
    y_pred = test_dynamic(model,tokened_test_X,test_seq_lens)
    return y_pred



