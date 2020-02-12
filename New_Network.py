import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from datetime import datetime


class ActorNetwork(nn.Module):
    # actornetwork pass the test
    def __init__(self, state_dim, action_dim, reward_dim, n_conv=128, n_fc=128, n_fc1=128):
        super(ActorNetwork, self).__init__()
        self.s_dim = state_dim
        self.a_dim = action_dim
        self.r_dim = reward_dim
        self.vectorOutDim = n_conv
        self.scalarOutDim = n_fc
        self.numFcInput = 2 * self.vectorOutDim * (
                    self.s_dim[1] - 4 + 1) + 3 * self.scalarOutDim + self.vectorOutDim * (self.a_dim - 4 + 1)
        self.numFcOutput = n_fc1

        # -------------------define layer-------------------
        self.tConv1d = nn.Conv1d(1, self.vectorOutDim, 4)

        self.dConv1d = nn.Conv1d(1, self.vectorOutDim, 4)

        self.cConv1d = nn.Conv1d(1, self.vectorOutDim, 4)

        # how to match the preferences size???
        self.preferenceFc = nn.Linear(reward_dim, self.scalarOutDim)

        self.bufferFc = nn.Linear(1, self.scalarOutDim)

        self.leftChunkFc = nn.Linear(1, self.scalarOutDim)

        self.bitrateFc = nn.Linear(1, self.scalarOutDim)

        self.fullyConnected = nn.Linear(self.numFcInput, self.numFcOutput)

        self.outputLayer = nn.Linear(self.numFcOutput, self.a_dim)
        # ------------------init layer weight--------------------
        # tensorflow-1.12 uses glorot_uniform(also called xavier_uniform) to initialize weight
        # uses zero to initialize bias
        # Conv1d also use same initialize method
        nn.init.xavier_uniform_(self.bufferFc.weight.data)
        nn.init.constant_(self.bufferFc.bias.data, 0.0)
        nn.init.xavier_uniform_(self.leftChunkFc.weight.data)
        nn.init.constant_(self.leftChunkFc.bias.data, 0.0)
        nn.init.xavier_uniform_(self.bitrateFc.weight.data)
        nn.init.constant_(self.bitrateFc.bias.data, 0.0)
        nn.init.xavier_uniform_(self.fullyConnected.weight.data)
        nn.init.constant_(self.fullyConnected.bias.data, 0.0)
        nn.init.xavier_uniform_(self.tConv1d.weight.data)
        nn.init.constant_(self.tConv1d.bias.data, 0.0)
        nn.init.xavier_uniform_(self.dConv1d.weight.data)
        nn.init.constant_(self.dConv1d.bias.data, 0.0)
        nn.init.xavier_normal_(self.cConv1d.weight.data)
        nn.init.constant_(self.cConv1d.bias.data, 0.0)

    def forward(self, inputs, preference):
        preferenceFcOut = F.relu(self.preferenceFc(preference.view(1, -1)), inplace=True)

        bitrateFcOut = F.relu(self.bitrateFc(inputs[:, 0:1, -1]), inplace=True)

        bufferFcOut = F.relu(self.bufferFc(inputs[:, 1:2, -1]), inplace=True)

        tConv1dOut = F.relu(self.tConv1d(inputs[:, 2:3, :]), inplace=True)

        dConv1dOut = F.relu(self.dConv1d(inputs[:, 3:4, :]), inplace=True)

        cConv1dOut = F.relu(self.cConv1d(inputs[:, 4:5, :self.a_dim]), inplace=True)

        leftChunkFcOut = F.relu(self.leftChunkFc(inputs[:, 5:6, -1]), inplace=True)

        t_flatten = tConv1dOut.view(tConv1dOut.shape[0], -1)

        d_flatten = dConv1dOut.view(dConv1dOut.shape[0], -1)

        c_flatten = cConv1dOut.view(dConv1dOut.shape[0], -1)

        fullyConnectedInput = torch.cat([bitrateFcOut, bufferFcOut, t_flatten, d_flatten,
                                         c_flatten, leftChunkFcOut, preferenceFcOut], 1)

        fcOutput = F.relu(self.fullyConnected(fullyConnectedInput), inplace=True)

        out = F.softmax(self.outputLayer(fcOutput))

        return out


class CriticNetwork(nn.Module):
    # return a value V(s,a)
    # the dim of state is not considered
    def __init__(self, state_dim, a_dim, reward_dim, n_conv=128, n_fc=128, n_fc1=128):
        super(CriticNetwork, self).__init__()
        self.s_dim = state_dim
        self.a_dim = a_dim
        self.r_dim = reward_dim
        self.vectorOutDim = n_conv
        self.scalarOutDim = n_fc
        self.numFcInput = 2 * self.vectorOutDim * (
                    self.s_dim[1] - 4 + 1) + 3 * self.scalarOutDim + self.vectorOutDim * (self.a_dim - 4 + 1)
        self.numFcOutput = n_fc1

        # ----------define layer----------------------
        self.tConv1d = nn.Conv1d(1, self.vectorOutDim, 4)

        self.dConv1d = nn.Conv1d(1, self.vectorOutDim, 4)

        self.cConv1d = nn.Conv1d(1, self.vectorOutDim, 4)

        self.preferenceFc = nn.Linear(reward_dim, self.scalarOutDim)

        self.bufferFc = nn.Linear(1, self.scalarOutDim)

        self.leftChunkFc = nn.Linear(1, self.scalarOutDim)

        self.bitrateFc = nn.Linear(1, self.scalarOutDim)

        self.fullyConnected = nn.Linear(self.numFcInput, self.numFcOutput)

        self.outputLayer = nn.Linear(self.numFcOutput, 1)

        # ------------------init layer weight--------------------
        # tensorflow-1.12 uses glorot_uniform(also called xavier_uniform) to initialize weight
        # uses zero to initialize bias
        # Conv1d also use same initialize method
        nn.init.xavier_uniform_(self.bufferFc.weight.data)
        nn.init.constant_(self.bufferFc.bias.data, 0.0)
        nn.init.xavier_uniform_(self.leftChunkFc.weight.data)
        nn.init.constant_(self.leftChunkFc.bias.data, 0.0)
        nn.init.xavier_uniform_(self.bitrateFc.weight.data)
        nn.init.constant_(self.bitrateFc.bias.data, 0.0)
        nn.init.xavier_uniform_(self.fullyConnected.weight.data)
        nn.init.constant_(self.fullyConnected.bias.data, 0.0)
        nn.init.xavier_uniform_(self.tConv1d.weight.data)
        nn.init.constant_(self.tConv1d.bias.data, 0.0)
        nn.init.xavier_uniform_(self.dConv1d.weight.data)
        nn.init.constant_(self.dConv1d.bias.data, 0.0)
        nn.init.xavier_normal_(self.cConv1d.weight.data)
        nn.init.constant_(self.cConv1d.bias.data, 0.0)

    def forward(self, inputs, preference):
        preferenceFcOut = F.relu(self.preferenceFc(preference.view(1, -1)), inplace=True)

        bitrateFcOut = F.relu(self.bitrateFc(inputs[:, 0:1, -1]), inplace=True)

        bufferFcOut = F.relu(self.bufferFc(inputs[:, 1:2, -1]), inplace=True)

        tConv1dOut = F.relu(self.tConv1d(inputs[:, 2:3, :]), inplace=True)

        dConv1dOut = F.relu(self.dConv1d(inputs[:, 3:4, :]), inplace=True)

        cConv1dOut = F.relu(self.cConv1d(inputs[:, 4:5, :self.a_dim]), inplace=True)

        leftChunkFcOut = F.relu(self.leftChunkFc(inputs[:, 5:6, -1]), inplace=True)

        t_flatten = tConv1dOut.view(tConv1dOut.shape[0], -1)

        d_flatten = dConv1dOut.view(dConv1dOut.shape[0], -1)

        c_flatten = cConv1dOut.view(dConv1dOut.shape[0], -1)
        print(c_flatten.shape, "----shape-----")

        fullyConnectedInput = torch.cat([bitrateFcOut, bufferFcOut, t_flatten,
                                         d_flatten, c_flatten, leftChunkFcOut, preferenceFcOut], 1)

        fcOutput = F.relu(self.fullyConnected(fullyConnectedInput), inplace=True)

        out = self.outputLayer(fcOutput)

        return out


if __name__ == '__main__':
    S_INFO = 6
    S_LEN = 8
    AGENT_NUM = 3
    ACTION_DIM = 6
    REWARD_DIM = 3

    discount = 0.9
    # what should be the preference shape?????
    weight = torch.FloatTensor([[0.2, 0.3, 0.5], [0.2, 0.3, 0.5], [0.2, 0.3, 0.5]])

    timenow = datetime.now()
    c_net = CriticNetwork([S_INFO, S_LEN], ACTION_DIM, REWARD_DIM)  # agent_num=2

    t_c_net = CriticNetwork([S_INFO, S_LEN], ACTION_DIM, REWARD_DIM)

    a_net = ActorNetwork([S_INFO, S_LEN], ACTION_DIM, REWARD_DIM)  # action_dime=4

    a_optim = torch.optim.Adam(a_net.parameters(), lr=0.001)

    c_optim = torch.optim.Adam(c_net.parameters(), lr=0.005)

    loss_func = nn.MSELoss()

    esp = 100
    for i in range(esp):
        npState = torch.randn(AGENT_NUM, S_INFO, S_LEN)
        net_npState = torch.randn(AGENT_NUM, S_INFO, S_LEN)
        # reward=torch.randn(1)
        reward = torch.randn(AGENT_NUM)

        action = a_net.forward(npState, weight)
        t_action = a_net.forward(net_npState, weight)

        q = c_net.forward(npState, weight)
        print(q)
        t_q_out = t_c_net.forward(net_npState, weight)

        updateCriticLoss = loss_func(reward, q)

        c_net.zero_grad()
        updateCriticLoss.backward()
        c_optim.step()

    print('train 4800 times use:' + str(datetime.now() - timenow))



