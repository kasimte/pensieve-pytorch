# Pensieve-pytorch
Implementing [pensieve](http://web.mit.edu/pensieve/) using pytorch.

The [author](https://github.com/hongzimao/pensieve) of pensieve uses tensorflow to implement it.

## Dependencise:

- python-2.7.15
- pytorch-1.0.1
- numpy-1.16.2

## Notes

When I used pytorch to implement it,I found a difference between the tensorflow implementation and the paper.

In ```hongzimao/pensieve/sim/a3c.py```,author used the mean square error of **R_batch** and **criticNetwork_output**(value function,in a3c.py line 243).But **R_batch** is the cumulative rewards in particular episode.In original paper,pensieve should use mean square of **r+\gamma * V(s_{t+1})** and **V(s_{t})** (paper,equation-3).

I have no idea how different between that,so I implemented 3 models to verify it:

- model 0 : only use pytorch to rewrite pensieve,no logical changes.use R_batch to update critic network.
- model 1 : according to equation-3,think of s_batch[:-1] as states,and s_batch[1:] as new states.(is that correct?)
- model 2 : no critic network,only actorc network.

## Train

You can run an example:

        ```
        python main.py --model_type=1
        ```

## Results

<img src="img/figure-1a.png" width="400" height="400" alt="1a"/> <img src="img/figure-1b.png" width="400" height="400" alt="1b"/>