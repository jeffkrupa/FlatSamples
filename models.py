import numpy as np
import torch
import torch.nn as nn
import itertools
device = torch.device('cpu')
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Defines the interaction matrices

class GraphNetv2(nn.Module):
    def __init__(self, name, n_constituents, n_targets, params, n_vertices=0, params_v=0, params_e=0, event_branch=False, pv_branch=False,  vv_branch=False, hidden=20, De=20, Do=20, dropout=0.1, softmax=False, sigmoid=False, attention_flag=False, is_oldmodel=False):
        super(GraphNetv2, self).__init__()
        self.hidden = int(hidden)
        self.P = params
        self.name = name
        self.is_oldmodel = is_oldmodel
        self.Nv = n_vertices		
        self.N = n_constituents
        self.S = params_v
        self.E = params_e
        self.Nr = self.N * (self.N - 1)
        self.Nt = self.N * self.Nv
        self.Ns = self.Nv * (self.Nv - 1)
        self.De = De
        self.Do = Do
        self.n_targets = n_targets
        self.assign_matrices()
        self.assign_matrices_SV()
        self.event_branch = event_branch
        self.pv_branch = pv_branch
        self.vv_branch = vv_branch
        self.softmax = softmax
        self.sigmoid = sigmoid
        self.relu = nn.ReLU()
        self.attention_flag = attention_flag 
    
        self.batchnorm = nn.BatchNorm1d(params)        
        self.batchnormSV = nn.BatchNorm1d(params_v)
        if self.event_branch:        
            self.batchnormE = nn.BatchNorm1d(params_e)        

        self.fr1 = nn.Conv1d(2*self.P, 4*self.De, kernel_size=1)#.cuda()
        self.fr2 = nn.Conv1d(4*self.De, 2*self.De, kernel_size=1)#.cuda()
        self.fr3 = nn.Conv1d(2*self.De, self.De, kernel_size=1)#.cuda()
        self.fr_batchnorm = nn.BatchNorm1d(self.De,  momentum=0.6)#.cuda()

        if self.event_branch:
            self.fe1    = nn.Linear(self.E,80)#.cuda()
            self.fe2    = nn.Linear(80,40)#.cuda()
            self.fe3    = nn.Linear(40,int(self.De/2))#.cuda()

        if self.pv_branch:
            self.assign_matrices_SV()
            self.fr1_pv = nn.Conv1d(self.S + self.P, self.hidden, kernel_size=1)#.cuda()
            self.fr2_pv = nn.Conv1d(self.hidden, int(self.hidden), kernel_size=1)#.cuda()
            self.fr3_pv = nn.Conv1d(int(self.hidden), self.De, kernel_size=1)#.cuda()

        if self.vv_branch:
            self.assign_matrices_SVSV()

            self.fr1_vv = nn.Conv1d(2 * self.S + self.Dr, self.hidden, kernel_size=1)#.cuda()
            self.fr2_vv = nn.Conv1d(self.hidden, int(self.hidden), kernel_size=1)#.cuda()
            self.fr3_vv = nn.Conv1d(int(self.hidden), self.De, kernel_size=1)#.cuda() 


        if self.pv_branch:
            self.fo1 = nn.Conv1d(self.P + (2 * self.De), 2*self.hidden, kernel_size=1)#.cuda()
            self.fo2 = nn.Conv1d(2*self.hidden, self.hidden, kernel_size=1)#.cuda()
            self.fo3 = nn.Conv1d(self.hidden, self.Do, kernel_size=1)#.cuda()

        else:            
            self.fo1 = nn.Conv1d(self.P + self.De, 2*self.hidden, kernel_size=1)#.cuda()
            self.fo2 = nn.Conv1d(2*self.hidden, self.hidden, kernel_size=1)#.cuda()
            self.fo3 = nn.Conv1d(self.hidden, self.Do, kernel_size=1)#.cuda()
        
        # Attention stuff
        if attention_flag: 
            self.attention = nn.MultiheadAttention(embed_dim=Do, num_heads=int(Do/2), batch_first=True)#.cuda()
            self.layer_norm_1 = nn.LayerNorm(Do)#.cuda()
            self.layer_norm_2 = nn.LayerNorm(Do)#.cuda()
            self.dropout_1 = nn.Dropout(dropout)#.cuda()
            self.dropout_2 = nn.Dropout(dropout)#.cuda()
            self.dropout_3 = nn.Dropout(dropout)#.cuda()
            self.linear_1 = nn.Linear(Do, Do*2)#.cuda()
            self.linear_2 = nn.Linear(Do*2, Do)#.cuda()
            self.linear_3 = nn.Linear(Do*self.N, Do)#.cuda()
        if self.is_oldmodel: 
            self.fc_fixed = nn.Linear(self.Do, self.n_targets)#.cuda()
        else:
            Ninputs = self.Do
            if self.event_branch: Ninputs+=int(self.De/2)
            self.fc_fixed1 = nn.Linear(Ninputs, 5*(self.n_targets))
            self.fc_fixed2 = nn.Linear(5*self.n_targets, 3*self.n_targets)
            self.fc_fixed3 = nn.Linear(3*self.n_targets, self.n_targets)


            
    def assign_matrices(self):
        self.Rr = torch.zeros(self.N, self.Nr)
        self.Rs = torch.zeros(self.N, self.Nr)
        receiver_sender_list = [i for i in itertools.product(range(self.N), range(self.N)) if i[0]!=i[1]]
        for i, (r, s) in enumerate(receiver_sender_list):
            self.Rr[r, i] = 1
            self.Rs[s, i] = 1
        self.Rr = (self.Rr).to(device)
        self.Rs = (self.Rs).to(device)

    def assign_matrices_SV(self):
        self.Rk = torch.zeros(self.N, self.Nt)
        self.Rv = torch.zeros(self.Nv, self.Nt)
        receiver_sender_list = [i for i in itertools.product(range(self.N), range(self.Nv))]
        for i, (k, v) in enumerate(receiver_sender_list):
            self.Rk[k, i] = 1
            self.Rv[v, i] = 1
        self.Rk = (self.Rk).to(device)
        self.Rv = (self.Rv).to(device)

    def assign_matrices_SVSV(self):
        self.Rl = torch.zeros(self.Nv, self.Ns)
        self.Ru = torch.zeros(self.Nv, self.Ns)
        receiver_sender_list = [i for i in itertools.product(range(self.Nv), range(self.Nv)) if i[0]!=i[1]]
        for i, (l, u) in enumerate(receiver_sender_list):
            self.Rl[l, i] = 1
            self.Ru[u, i] = 1
        self.Rl = (self.Rl)#.cuda()
        self.Ru = (self.Ru)#.cuda()

    def forward(self, x, y=None, e=None):
        ###PF Candidate - PF Candidate###
        x = self.batchnorm(x)
        Orr = self.tmul(x, self.Rr)
        Ors = self.tmul(x, self.Rs)
        B = torch.cat([Orr, Ors], 1)
        ### First MLP ###
        B = self.relu(self.fr1(B))
        B = self.relu(self.fr2(B))
        E = self.relu(self.fr3(B))
        #E = self.fr_batchnorm(E) 
        del B
        Ebar_pp = self.tmul(E, torch.transpose(self.Rr, 0, 1).contiguous())
        del E

       
        ####Secondary Vertex - PF Candidate### 
        if self.pv_branch:
            y = self.batchnormSV(y)
            Ork = self.tmul(x, self.Rk)
            Orv = self.tmul(y, self.Rv)
            B = torch.cat([Ork, Orv], 1)
            #assert torch.isfinite(B).all()
            B = self.relu(self.fr1_pv(B))
            #assert torch.isfinite(B).all()
            B = self.relu(self.fr2_pv(B))
            #assert torch.isfinite(B).all()
            E = self.relu(self.fr3_pv(B))
            #assert torch.isfinite(E).all()
            del B
            Ebar_pv = self.tmul(E, torch.transpose(self.Rk, 0, 1).contiguous())
            #assert torch.isfinite(Ebar_pv).all()
 
      

        ####Final output matrix for particles###
        if self.pv_branch:
            C = torch.cat([x, Ebar_pp, Ebar_pv], 1)
            #assert torch.isfinite(C).all()
            del Ebar_pv
        else:
            C = torch.cat([x, Ebar_pp], 1)

        del Ebar_pp; torch.cuda.empty_cache()
        #C = torch.transpose(C, 2, 1).contiguous()
        ### Second MLP ###
        C = self.relu(self.fo1(C))
        #assert torch.isfinite(C).all()
        C = self.relu(self.fo2(C))
        #assert torch.isfinite(C).all()
        O = self.relu(self.fo3(C))
        #assert torch.isfinite(O).all()
        del C
        O = torch.transpose(O, 1, 2).contiguous()
      
          
        #Taking the sum of over each particle/vertex
        if self.attention_flag: 
            O_norm = self.layer_norm_1(O)
            N = O_norm + self.dropout_1(self.attention(O, O, O, need_weights=False)[0])
            del O_norm
            N2 = self.layer_norm_2(N)
            N = N + self.dropout_3(self.linear_2(self.dropout_2(nn.ReLU()(self.linear_1(N2)))))
            del N2
            N = self.linear_3(torch.flatten(N,start_dim=1))
        else: 
            N = torch.sum(O, dim=1)


        

        if self.event_branch:
            e = self.batchnormE(e) 
            e = self.relu(self.fe1(e))
            e = self.relu(self.fe2(e))
            e = self.relu(self.fe3(e))
            N = torch.cat([N, e], 1)

        #assert torch.isfinite(N).all()
        del O
        
        ### Classification MLP ###
        if self.is_oldmodel: 
            N = self.fc_fixed(N)
        else:
            N = self.fc_fixed1(N)
            N = self.fc_fixed2(N)
            N = self.fc_fixed3(N)
        #print("output",N.shape)
        
        if self.softmax:
            N = nn.Softmax(dim=1)(N)
        elif self.sigmoid: 
            N = nn.Sigmoid()(N)
        return N
        del N; torch.cuda.empty_cache()
            
    def tmul(self, x, y):  #Takes (I * J * K)(K * L) -> I * J * L 
        x_shape = x.size()
        y_shape = y.size()
        #return torch.mm(x.view(-1, x_shape[2]), y).view(-1, x_shape[1], y_shape[1])
        return torch.mm(x.reshape(-1, x_shape[2]), y).reshape(-1, x_shape[1], y_shape[1])

class GraphNetnoSV(nn.Module):
    def __init__(self, name, n_constituents, n_targets, params, hidden, De=5, Do=6, softmax=False):
        super(GraphNetnoSV, self).__init__()
        self.hidden = int(hidden)
        self.P = params
        self.name = name
        self.Nv = 0 
        self.N = n_constituents
        self.Nr = self.N * (self.N - 1)
        self.Nt = self.N * self.Nv
        self.Ns = self.Nv * (self.Nv - 1)
        self.Dr = 0
        self.De = De
        self.Dx = 0
        self.Do = Do
        self.S = 0
        self.n_targets = n_targets
        self.assign_matrices()
        self.softmax = softmax
           
        self.Ra = torch.ones(self.Dr, self.Nr)
        self.fr1 = nn.Linear(2 * self.P + self.Dr, self.hidden)
        self.fr2 = nn.Linear(self.hidden, int(self.hidden/2))
        self.fr3 = nn.Linear(int(self.hidden/2), self.De)
        self.fr1_pv = nn.Linear(self.S + self.P + self.Dr, self.hidden)
        self.fr2_pv = nn.Linear(self.hidden, int(self.hidden/2))
        self.fr3_pv = nn.Linear(int(self.hidden/2), self.De)



       
        self.fo1 = nn.Linear(self.P + self.Dx + (self.De), self.hidden)
        self.fo2 = nn.Linear(self.hidden, int(self.hidden/2))
        self.fo3 = nn.Linear(int(self.hidden/2), self.Do)

        #self.fr1 = nn.DataParallel(self.fr1)        
        #self.fr2 = nn.DataParallel(self.fr2)        
        #self.fr3 = nn.DataParallel(self.fr3)
        #self.fr1_pv = nn.DataParallel(self.fr1_pv)        
        #self.fr2_pv = nn.DataParallel(self.fr2_pv)        
        #self.fr3_pv = nn.DataParallel(self.fr3_pv) 
        #self.fo1 = nn.DataParallel(self.fo1) 
        #self.fo2 = nn.DataParallel(self.fo2) 
        #self.fo3 = nn.DataParallel(self.fo3) 

        
        self.fc_fixed1 = nn.Linear(self.Do, 5*(self.n_targets))
        self.fc_fixed2 = nn.Linear(5*self.n_targets, 3*self.n_targets)
        self.fc_fixed3 = nn.Linear(3*self.n_targets, self.n_targets)
            
    def assign_matrices(self):
        self.Rr = torch.zeros(self.N, self.Nr)
        self.Rs = torch.zeros(self.N, self.Nr)
        receiver_sender_list = [i for i in itertools.product(range(self.N), range(self.N)) if i[0]!=i[1]]
        for i, (r, s) in enumerate(receiver_sender_list):
            self.Rr[r, i] = 1
            self.Rs[s, i] = 1
        self.Rr = (self.Rr).cuda()
        self.Rs = (self.Rs).cuda()
        #print("self.Rr",self.Rr)
        print("self.Rr.shape",self.Rr.shape)
        #print("self.Rs",self.Rs)
        print("self.Rs.shape",self.Rs.shape)
        
    def forward(self, x):
        ###PF Candidate - PF Candidate###
        print("x.shape",x.shape)
        print("self.Rr.shape",self.Rr.shape)
        Orr = self.tmul(x, self.Rr)
        
        print("Orr.shape",Orr.shape)
        Ors = self.tmul(x, self.Rs)
        print("Ors.shape",Ors.shape)
        B = torch.cat([Orr, Ors], 1)
        print("B0.shape",B.shape)
        #print("B0.shape",B.shape)
        del Orr, Ors
        ### First MLP ###
        #B = torch.transpose(B, 1, 2).contiguous()
        #B = B.contiguous()
        print("B1.shape",B.shape)
        #B = nn.functional.relu(self.fr1(B.view(-1, 2 * self.P + self.Dr)))
        #print("B1p5 shape",B.reshape(-1, 2 * self.P + self.Dr,self.hidden).shape)
        #B = nn.functional.relu(self.fr1(B.reshape(-1, 2 * self.P + self.Dr,self.hidden)))
        B = nn.functional.relu(self.fr1(B))#reshape(-1, 2 * self.P + self.Dr,self.hidden)))
        print("B2.shape",B.shape)
        B = nn.functional.relu(self.fr2(B))
        print("B3.shape",B.shape)
        #E = nn.functional.relu(self.fr3(B).reshape(-1, self.Nr, self.De))
        E = nn.functional.relu(self.fr3(B))#.reshape(-1, self.Nr, self.De))
        #print("E.shape",E.shape)
        del B
        E = torch.transpose(E, 1, 2).contiguous()
        print("E.shape",E.shape)
        Ebar_pp = self.tmul(E, torch.transpose(self.Rr, 0, 1).contiguous())
        print("Ebar_pp.shape",Ebar_pp.shape)
        del E
        

        ####Final output matrix for particles###
        

        C = torch.cat([x, Ebar_pp], 1)
        #print("C.shape",C.shape)
        del Ebar_pp
        C = torch.transpose(C, 1, 2).contiguous()
        #print("C.shape",C.shape)
        ### Second MLP ###
        C = nn.functional.relu(self.fo1(C.view(-1, self.P + self.Dx + (self.De))))
        #print("C.shape",C.shape)
        C = nn.functional.relu(self.fo2(C))
        #print("C.shape",C.shape)
        O = nn.functional.relu(self.fo3(C).view(-1, self.N, self.Do))
        #print("O.shape",O.shape)
        del C

        
        #Taking the sum of over each particle/vertex
        N = torch.sum(O, dim=1)
        #print("N.shape",N.shape)
        del O
        
        ### Classification MLP ###

        N = self.fc_fixed1(N)
        N = self.fc_fixed2(N)
        N = self.fc_fixed3(N)
        #print("MLP: N.shape",N.shape)
        
        if self.softmax:
            N = nn.Softmax(dim=1)(N)
        #torch.cuda.empty_cache()
    
        return N
            
    def tmul(self, x, y):  #Takes (I * J * K)(K * L) -> I * J * L 
        x_shape = x.size()
        y_shape = y.size()
        #return torch.mm(x.view(-1, x_shape[2]), y).view(-1, x_shape[1], y_shape[1])
        return torch.mm(x.reshape(-1, x_shape[2]), y).reshape(-1, x_shape[1], y_shape[1])

class Linear(nn.Module):
    def __init__(self, n_inputs, n_targets):
        super(Linear, self).__init__()
        self.f1 = nn.Linear(n_inputs, n_targets).cuda()
        self.activation = torch.nn.Sigmoid()
    def forward(self, x): 
        x = self.f1(x)
        return(self.activation(x))

class DNN(nn.Module):
    def __init__(self, name, n_inputs, n_targets):
        super(DNN, self).__init__()
        #self.flat = torch.flatten()
        self.name = name
        self.dropout = nn.Dropout(p=0.25)
        self.b0 = nn.BatchNorm1d(n_inputs).cuda()
        self.f0 = nn.Linear(n_inputs, 50).cuda()
        self.f1 = nn.Linear(50, 40).cuda()
        self.f1b = nn.Linear(40, 40).cuda()
        self.b2 = nn.BatchNorm1d(40).cuda()
        self.f2 = nn.Linear(40, 10).cuda()
        self.b3 = nn.BatchNorm1d(10).cuda()
        self.f3 = nn.Linear(10, 5).cuda()
        self.b5 = nn.BatchNorm1d(5).cuda()
        #self.f4 = nn.Linear(50, 10).cuda()
        self.f5 = nn.Linear(5, n_targets).cuda()
        self.activation = torch.nn.ReLU()
        if n_targets == 2 or n_targets == 1:
            self.lastactivation = torch.nn.Sigmoid()
        elif n_targets > 2:
            self.lastactivation = torch.nn.Softmax(dim=1)
        else:
            raise ValueError("I don't understand n_targets "+str(n_targets))
    def forward(self, x): 
        #print("before flat",x.shape)
        #print("before flat",x[0])
        x = torch.flatten(x,start_dim=1)
        #print("after flat",x.shape)
        #print("after flat",x[1])
        x = self.b0(x)
        x = self.activation(self.f0(x))
        x = self.activation(self.f1(x))
        x = self.activation(self.f1b(x))
        x = self.activation(self.f2(x))
        x = self.b3(x)
        x = self.activation(self.f3(x))
        x = self.b5(x)
        x = self.f5(x)
        #return x
        return(self.lastactivation(x))


import numpy as np
import torch
import torch.nn as nn

'''Based on https://github.com/WangYueFt/dgcnn/blob/master/pytorch/model.py.'''


def knn(x, k):
    inner = -2 * torch.matmul(x.transpose(2, 1), x)
    xx = torch.sum(x ** 2, dim=1, keepdim=True)
    pairwise_distance = -xx - inner - xx.transpose(2, 1)
    idx = pairwise_distance.topk(k=k + 1, dim=-1)[1][:, :, 1:]  # (batch_size, num_points, k)
    return idx


# v1 is faster on GPU
def get_graph_feature_v1(x, k, idx):
    batch_size, num_dims, num_points = x.size()

    idx_base = torch.arange(0, batch_size, device=x.device).view(-1, 1, 1) * num_points
    idx = idx + idx_base
    idx = idx.view(-1)

    fts = x.transpose(2, 1).reshape(-1, num_dims)  # -> (batch_size, num_points, num_dims) -> (batch_size*num_points, num_dims)
    fts = fts[idx, :].view(batch_size, num_points, k, num_dims)  # neighbors: -> (batch_size*num_points*k, num_dims) -> ...
    fts = fts.permute(0, 3, 1, 2).contiguous()  # (batch_size, num_dims, num_points, k)
    x = x.view(batch_size, num_dims, num_points, 1).repeat(1, 1, 1, k)
    fts = torch.cat((x, fts - x), dim=1)  # ->(batch_size, 2*num_dims, num_points, k)
    return fts


# v2 is faster on CPU
def get_graph_feature_v2(x, k, idx):
    batch_size, num_dims, num_points = x.size()

    idx_base = torch.arange(0, batch_size, device=x.device).view(-1, 1, 1) * num_points
    idx = idx + idx_base
    idx = idx.view(-1)

    fts = x.transpose(0, 1).reshape(num_dims, -1)  # -> (num_dims, batch_size, num_points) -> (num_dims, batch_size*num_points)
    fts = fts[:, idx].view(num_dims, batch_size, num_points, k)  # neighbors: -> (num_dims, batch_size*num_points*k) -> ...
    fts = fts.transpose(1, 0).contiguous()  # (batch_size, num_dims, num_points, k)

    x = x.view(batch_size, num_dims, num_points, 1).repeat(1, 1, 1, k)
    fts = torch.cat((x, fts - x), dim=1)  # ->(batch_size, 2*num_dims, num_points, k)

    return fts


class EdgeConvBlock(nn.Module):
    r"""EdgeConv layer.
    Introduced in "`Dynamic Graph CNN for Learning on Point Clouds
    <https://arxiv.org/pdf/1801.07829>`__".  Can be described as follows:
    .. math::
       x_i^{(l+1)} = \max_{j \in \mathcal{N}(i)} \mathrm{ReLU}(
       \Theta \cdot (x_j^{(l)} - x_i^{(l)}) + \Phi \cdot x_i^{(l)})
    where :math:`\mathcal{N}(i)` is the neighbor of :math:`i`.
    Parameters
    ----------
    in_feat : int
        Input feature size.
    out_feat : int
        Output feature size.
    batch_norm : bool
        Whether to include batch normalization on messages.
    """

    def __init__(self, k, in_feat, out_feats, batch_norm=True, activation=True, cpu_mode=False):
        super(EdgeConvBlock, self).__init__()
        self.k = k
        self.batch_norm = batch_norm
        self.activation = activation
        self.num_layers = len(out_feats)
        self.get_graph_feature = get_graph_feature_v2 if cpu_mode else get_graph_feature_v1

        self.convs = nn.ModuleList()
        for i in range(self.num_layers):
            self.convs.append(nn.Conv2d(2 * in_feat if i == 0 else out_feats[i - 1], out_feats[i], kernel_size=1, bias=False if self.batch_norm else True))

        if batch_norm:
            self.bns = nn.ModuleList()
            for i in range(self.num_layers):
                self.bns.append(nn.BatchNorm2d(out_feats[i]))

        if activation:
            self.acts = nn.ModuleList()
            for i in range(self.num_layers):
                self.acts.append(nn.ReLU())

        if in_feat == out_feats[-1]:
            self.sc = None
        else:
            self.sc = nn.Conv1d(in_feat, out_feats[-1], kernel_size=1, bias=False)
            self.sc_bn = nn.BatchNorm1d(out_feats[-1])

        if activation:
            self.sc_act = nn.ReLU()

    def forward(self, points, features):

        topk_indices = knn(points, self.k)
        x = self.get_graph_feature(features, self.k, topk_indices)

        for conv, bn, act in zip(self.convs, self.bns, self.acts):
            x = conv(x)  # (N, C', P, K)
            if bn:
                x = bn(x)
            if act:
                x = act(x)

        fts = x.mean(dim=-1)  # (N, C, P)

        # shortcut
        if self.sc:
            sc = self.sc(features)  # (N, C_out, P)
            sc = self.sc_bn(sc)
        else:
            sc = features

        return self.sc_act(sc + fts)  # (N, C_out, P)


class ParticleNet(nn.Module):

    def __init__(self,
                 input_dims,
                 num_classes,
                 conv_params=[(7, (32, 32, 32)), (7, (64, 64, 64))],
                 fc_params=[(128, 0.1)],
                 use_fusion=True,
                 use_fts_bn=True,
                 use_counts=True,
                 for_inference=False,
                 sigmoid=False,
                 for_segmentation=False,
                 event_branch=False,
                 **kwargs):
        super(ParticleNet, self).__init__(**kwargs)
        self.event_branch = event_branch
        self.use_fts_bn = use_fts_bn
        if self.use_fts_bn:
            self.bn_fts = nn.BatchNorm1d(input_dims)

        self.use_counts = use_counts

        self.edge_convs = nn.ModuleList()
        for idx, layer_param in enumerate(conv_params):
            k, channels = layer_param
            in_feat = input_dims if idx == 0 else conv_params[idx - 1][1][-1]
            self.edge_convs.append(EdgeConvBlock(k=k, in_feat=in_feat, out_feats=channels, cpu_mode=for_inference))

        self.use_fusion = use_fusion
        if self.use_fusion:
            in_chn = sum(x[-1] for _, x in conv_params)
            out_chn = np.clip((in_chn // 128) * 128, 128, 1024)
            self.fusion_block = nn.Sequential(nn.Conv1d(in_chn, out_chn, kernel_size=1, bias=False), nn.BatchNorm1d(out_chn), nn.ReLU())

        self.for_segmentation = for_segmentation

        fcs = []
        if self.event_branch:
            self.ec = nn.Sequential(
                nn.BatchNorm1d(27),
                nn.Linear(27,50),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(50,50),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(50,25),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(25,int(fc_params[0][0]/4)),
                nn.ReLU(),
                nn.Dropout(0.1),
            )                                     
        
        for idx, layer_param in enumerate(fc_params):
            channels, drop_rate = layer_param
            if idx == 0:
                in_chn = out_chn if self.use_fusion else conv_params[-1][1][-1]
                if self.event_branch:
                    in_chn = in_chn + int(in_chn/4)
            else:
                in_chn = fc_params[idx - 1][0]
            if self.for_segmentation:
                fcs.append(nn.Sequential(nn.Conv1d(in_chn, channels, kernel_size=1, bias=False),
                                         nn.BatchNorm1d(channels), nn.ReLU(), nn.Dropout(drop_rate)))
            else:
                fcs.append(nn.Sequential(nn.Linear(in_chn, channels), nn.ReLU(), nn.Dropout(drop_rate)))

        if self.for_segmentation:
            fcs.append(nn.Conv1d(fc_params[-1][0], num_classes, kernel_size=1))
        else:
            fcs.append(nn.Linear(fc_params[-1][0], num_classes))

            
        self.fc = nn.Sequential(*fcs)

        self.for_inference = for_inference
        self.sigmoid = sigmoid 
    def forward(self, points, features, mask=None, event_features=None):
#         print('points:\n', points)
#         print('features:\n', features)
        if mask is None:
            mask = (features.abs().sum(dim=1, keepdim=True) != 0)  # (N, 1, P)
        points *= mask
        features *= mask
        coord_shift = (mask == 0) * 1e9
        if self.use_counts:
            counts = mask.float().sum(dim=-1)
            counts = torch.max(counts, torch.ones_like(counts))  # >=1

        if self.use_fts_bn:
            fts = self.bn_fts(features) * mask
        else:
            fts = features
        outputs = []
        for idx, conv in enumerate(self.edge_convs):
            pts = (points if idx == 0 else fts) + coord_shift
            fts = conv(pts, fts) * mask
            if self.use_fusion:
                outputs.append(fts)
        if self.use_fusion:
            fts = self.fusion_block(torch.cat(outputs, dim=1)) * mask

#         assert(((fts.abs().sum(dim=1, keepdim=True) != 0).float() - mask.float()).abs().sum().item() == 0)
        
        if self.for_segmentation:
            x = fts
        else:
            if self.use_counts:
                x = fts.sum(dim=-1) / counts  # divide by the real counts
            else:
                x = fts.mean(dim=-1)
        #print("self.event_branch",self.event_branch)
        #print("event_features",event_features)
        if self.event_branch:
            e = self.ec(event_features)
            x = torch.cat((x,e),dim=1)
        output = self.fc(x)
        if self.sigmoid:
            output = torch.sigmoid(output)
        elif self.for_inference:
            output = torch.softmax(output, dim=1)
        # print('output:\n', output)
        return output


class FeatureConv(nn.Module):

    def __init__(self, in_chn, out_chn, **kwargs):
        super(FeatureConv, self).__init__(**kwargs)
        self.conv = nn.Sequential(
            nn.BatchNorm1d(in_chn),
            nn.Conv1d(in_chn, out_chn, kernel_size=1, bias=False),
            nn.BatchNorm1d(out_chn),
            nn.ReLU()
            )

    def forward(self, x):
        #print(torch.where(~torch.isfinite(x),1,0).nonzero())
        return self.conv(x)


class ParticleNetTagger(nn.Module):

    def __init__(self,
                 name,
                 pf_features_dims,
                 sv_features_dims,
                 num_classes,
                 conv_params=[(7, (32, 32, 32)), (7, (64, 64, 64))],
                 fc_params=[(128, 0.1)],
                 use_fusion=True,
                 use_fts_bn=True,
                 use_counts=True,
                 pf_input_dropout=None,
                 sv_input_dropout=None,
                 for_inference=False,
                 sigmoid=False,
                 event_branch=False,
                 **kwargs):
        super(ParticleNetTagger, self).__init__(**kwargs)
        self.name = name
        self.event_branch = event_branch
        self.pf_input_dropout = nn.Dropout(pf_input_dropout) if pf_input_dropout else None
        self.sv_input_dropout = nn.Dropout(sv_input_dropout) if sv_input_dropout else None
        self.pf_conv = FeatureConv(pf_features_dims, 32)
        self.sv_conv = FeatureConv(sv_features_dims, 32)
        self.pn = ParticleNet(input_dims=32,
                              num_classes=num_classes,
                              conv_params=conv_params,
                              fc_params=fc_params,
                              use_fusion=use_fusion,
                              use_fts_bn=use_fts_bn,
                              use_counts=use_counts,
                              for_inference=for_inference,
                              sigmoid=sigmoid,
                              event_branch=event_branch,
        )

    def forward(self, pf_points, pf_features, pf_mask, sv_points, sv_features, sv_mask, event_features=None):
        if self.pf_input_dropout:
            pf_mask = (self.pf_input_dropout(pf_mask) != 0).float()
            pf_points *= pf_mask
            pf_features *= pf_mask
        if self.sv_input_dropout:
            sv_mask = (self.sv_input_dropout(sv_mask) != 0).float()
            sv_points *= sv_mask
            sv_features *= sv_mask
        #print("pf_points/sv_points",pf_points.shape,sv_points.shape) 
        #print("pf_features/sv_features",pf_features.shape, sv_features.shape)
        #print("pf_mask/sv_mask",pf_mask.shape, sv_mask.shape)
        points = torch.cat((pf_points, sv_points), dim=2)
        #print("self.pf_conv(pf_features * pf_mask)",self.pf_conv(pf_features * pf_mask).shape)
        #print("self.sv_conv(sv_features * sv_mask)",self.sv_conv(sv_features * sv_mask).shape)
        #print("self.pf_conv(pf_features * pf_mask) * pf_mask ",(self.pf_conv(pf_features * pf_mask) * pf_mask).shape)
        #print("self.sv_conv(sv_features * sv_mask) * sv_mask ",(self.sv_conv(sv_features * sv_mask) * sv_mask).shape)
        
        #print("pf_features",pf_features.shape,"\npf_mask",pf_mask.shape,"\nsv_features",sv_features.shape,"\nsv_mask",sv_mask.shape,)
        features = torch.cat((self.pf_conv(pf_features * pf_mask) * pf_mask, self.sv_conv(sv_features * sv_mask) * sv_mask), dim=2)
        #print("features",features.shape)
        #features = torch.cat((self.pf_conv(pf_features * pf_mask), self.sv_conv(sv_features * sv_mask)), dim=2)
        mask = torch.cat((pf_mask, sv_mask), dim=2)
        #print("mask",mask.shape)
        #print("points",points.shape)
        #print("features",features.shape)
        #print("mask",mask.shape)
        return self.pn(points, features, mask, event_features)
