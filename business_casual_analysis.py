# what does business casual mean for women (according to the internet)?

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from ols import ols_reg

figpath = 'figures/'

data = pd.read_csv('data/business_casual.csv')

# which clothing items appear most frequently in comments? 
frequency_groups = data.groupby('item').item.count()
most_frequent = frequency_groups.sort_values(ascending=False)[:20]

fig, ax = plt.subplots(figsize=(12,6))  
most_frequent.plot.bar(x='item',ax=ax,color='#008793')
plt.savefig(figpath + 'most_frequent.pdf')                       

# interpretation: 
# unsurprisingly, most of the generic "parent items" (dresses, pants, etc.) 
# appear most frequently in posts on business casual (BC) attire.
# blazers, blouses, and cardigans appear with similar frequencies in BC posts, 
# while suits appear only about half as frequently. this suggests that mix-and-
# match separates may be more typical of BC than a full suit.
# boots appear in BC posts are a surprisingly high frequency relative to other
# shoe types, e.g. heels and flats.
# it is also somewhat surprising that leggings and tees are among the 20 most-
# frequently mentioned items of clothing in BC posts.

# which specific (i.e. non-parent) clothing items appear most frequently?
specific_frequency_groups = data.loc[data['item']!= data['parent_item']].groupby('item').item.count()
most_frequent_specific = specific_frequency_groups.sort_values(ascending=False)[:20]

fig, ax = plt.subplots(figsize=(12,6))  
most_frequent_specific.plot.bar(x='item',ax=ax,color='#008793')
plt.savefig(figpath + 'most_frequent_specific.pdf') 

# interpretation:
# blazers, cardigans, and blouses are also among the most frequently mentioned 
# specific items in BC posts. this again suggests that separates such as these
# are typical of a BC outfit.
# heels and flats are also among the most frequently mentioned specific items, 
# but boots are by far the most frequently mentioned shoe. 
# sneakers also appear among the most frequently metioned specific items. this
# and the above suggest that less-formal shoe choices are acceptable for a BC
# outfit.
# leggings are the second most popular specific pant, and they are mentioned 
# only slightly less frequently than slacks in BC posts. this and the fact that
# specific tops (blazers, blouses, cardigans, etc.) are metioned much more
# frequently suggests that BC outfits are driven by top choices and a range of 
# pant types is acceptable. 
# alternatively, one could interpret the above and the fact that tees are also
# frequently mentioned in BC looks as evidence that "BC" implies a highly
# variable degree of formality to different people/in different contexts.

# what adjectives are associated with frequently-mentioned BC items?
r = 0
c = 0
fig, ax = plt.subplots(5,2,sharey='all',figsize=(6,15))
plt.subplots_adjust(hspace = 0.7)
for i in most_frequent[:10].index:
    adj_groups = data.loc[(data['item'] == i)].groupby('adjective').adjective.count()
    adj_groups.sort_values(ascending=False)[:5].plot.bar(x='adjective',ax=ax[r,c],color='#008793')
    ax[r,c].set_xlabel('')
    ax[r,c].set_title(i)
    if r == 4:
        r = 0
        c = 1
    else:
        r += 1
plt.savefig(figpath + 'most_frequent_adjective')

# interpretation:
# "casual" is a top adjective for several items (dresses, tops, blazers). this 
# could be interpreted as evidence that the distribution of BC looks skews 
# towards the "casual" end of the spectrum.
# "black" is also a top adjective for almost all items, as is "neutral" and
# other neutral colors (e.g. white). this suggests that classic/neutral
# colors may be used to temper more casual elements of BC outfits.
# "nice" is a top adjective for dresses, shoes, blouses, tops, and cardigans. 
# this is arguably in opposition to "casual" and suggests that a BC look can't 
# be (subjectively) "too" casual.

# which clothing items are associated with the most upvotes on average?
upvote_groups = data.groupby('item').comment_score.mean() 
fig = plt.subplots(figsize=(8,8))
gs = gridspec.GridSpec(2, 1, height_ratios=[1, 4]) 
ax_top = plt.subplot(gs[0])
ax_bottom = plt.subplot(gs[1])
ax_top.set_ylim(200,220)
ax_bottom.set_ylim(1,125)
ax_top.spines['bottom'].set_visible(False)
ax_bottom.spines['top'].set_visible(False)
ax_top.tick_params(labelbottom='off',length=0)
d = .015
kwargs = dict(transform=ax_top.transAxes, color='k', clip_on=False)
ax_top.plot((-d,+d), (-d,+d), **kwargs)
ax_top.plot((1-d,1+d),(-d,+d), **kwargs)
kwargs.update(transform=ax_bottom.transAxes)  
ax_bottom.plot((-d,+d), (1-d/4,1+d/4), **kwargs)
ax_bottom.plot((1-d,1+d), (1-d/4,1+d/4), **kwargs)
ax_top.scatter(frequency_groups.values,upvote_groups.values)
ax_bottom.scatter(frequency_groups.values,upvote_groups.values)
ax_bottom.axhline(np.median(upvote_groups.values), color='green', linestyle='--')
annotate_txt = (upvote_groups.sort_values(ascending=False)[:10].index)
annotate_x = frequency_groups.loc[annotate_txt].values
annotate_y = upvote_groups.sort_values(ascending=False)[:10].values
ax_top.annotate(annotate_txt[0],(annotate_x[0],annotate_y[0]))
for i in list(range(1,10)):
    ax_bottom.annotate(annotate_txt[i],(annotate_x[i],annotate_y[i]))
plt.tight_layout()
plt.savefig(figpath + 'upvote_scatter')

# interpretation:
# in general, the most frequently-mentioned items appear in posts with approx.
# the median number of avg. upvotes. (note that the dist. of avg. upvotes is
# skewed by items with relatively few mentions.) 
# blouses are one exception to the above. 
# while some items with high average upvotes are classically "business" (e.g. 
# shifts, blouses, loafers), several items with high average upvotes are 
# arguably surprising as "business" attire (e.g. bandanas, beanies, berets; 
# though one should note most of these averages are drawn from relatively small 
# samples, so interpretation is tentative.) this may suggest that "fun" 
# accessories in conjunction with classic pieces comprise a good BC outfit.

# which adjectives are associated with the most upvotes on average?
r = 0
c = 0
fig, ax = plt.subplots(5,2,sharey='all',figsize=(6,15))
plt.subplots_adjust(hspace = 0.7)
for i in most_frequent[:10].index:
    adj_means = data.loc[(data['item'] == i)].groupby('adjective').comment_score.mean()
    adj_means.sort_values(ascending=False)[:5].plot.bar(x='adjective',ax=ax[r,c],color='#008793')
    ax[r,c].set_xlabel('')
    ax[r,c].set_title(i)
    if r == 4:
        r = 0
        c = 1
    else:
        r += 1
plt.savefig(figpath + 'upvote_adjective')

# interpretation:
# there is not a strong consensus as to whether or not BC looks should be sexy.
# adjectives like "appropriate," "oversized," "loose," "conservative," and
# "sensible" have high upvotes on avg. for frequently-mentioned items, but so 
# do "bodycon," "sexy," and "otk" ("over-the-knee" boots). 
# this conflict seems particularly pronounced for dresses and shoes.
# adjectives such as "sensible," "versatile," "classic," "simple,," "normal,"
# and "regular" have high avg. upvotes across a range of staple items (shoes,
# pants, blouses, blazers). this further suggests that the foundation of a BC
# wardrobe is neutral, timeless pieces.

# statistically speaking, what qualities of certain generic clothing items make
# them "more" BC?

# for a given parent item p, regress the upvotes of comment i mentioning item p
# onto dummies for specific clothing item and modifying adjectives to determine 
# what qualities make a given generic item more or less BC. 
for parent_item in ['dresses','jackets','pants','shoes','sweaters','tops']:
    
    obs = data.loc[data['parent_item']==parent_item]
    n_obs = len(obs)
    
    item_dummies = np.asmatrix(pd.get_dummies(obs['item']))
    n_item = np.size(item_dummies,1)
    item_vars = list(pd.get_dummies(obs['item']))
    
    # limit adjectives to the five most frequent and "other" to keep k small
    top_adjs = obs.groupby('adjective').adjective.count().sort_values(ascending=False)[:5].index
    obs.loc[(~obs['adjective'].isin(top_adjs)) & (~pd.isnull(obs['adjective'])),'adjective'] = 'other'
    adj_dummies = np.asmatrix(pd.get_dummies(obs['adjective']))
    n_adj = np.size(adj_dummies,1)
    adj_vars = list(pd.get_dummies(obs['adjective']).columns)
    
    # no intercept so that we don't need to use parent item as an omitted category
    X = item_dummies
    
    # create interaction terms where there's >= 1 instance of the interaction 
    # this avoids collinearity when multiple items don't appear with the same adj.
    interact_vars = []
    interactions = obs.groupby(['item','adjective']).adjective.count().index
    for i in range(len(interactions)):
        idx_item = [j==interactions[i][0] for j in item_vars]
        idx_adj = [j==interactions[i][1] for j in adj_vars]
        interacted = np.multiply(item_dummies[:,idx_item],adj_dummies[:,idx_adj])
        X = np.concatenate((X,interacted),axis=1)
        interact_vars.append(interactions[i][0] + ' x ' + interactions[i][1])
            
    var_order = item_vars + interact_vars
    
    y = np.asmatrix(obs['comment_score']).T
    
    reg = ols_reg(X,y)
    B = reg[0].tolist()[0]
    se = reg[1].tolist()[0]
    
    print('Parent item: ',parent_item)
    print('Var','Bhat','t-stat')
    for i in range(len(B)):
        print(var_order[i], B[i], B[i]/(se[i]+0.0001))
    print('\n')
    
# interpretation:
# ankle pants, skinny pants, and ponte pants have some of the highest average 
# BC scores of all specific clothing items. 
# high booties have a high average score, and are the highest-scoring item
# among specific shoe types.
# nice tanks also have a high average score, and are the highest-scoring item
# among specific tops.
    
# overall, these results suggest that a "good" BC outfit for women incorporates
# separates with tailored shapes and high-quality fabrics; and semi-casual
# footwear choices, perhaps with a heel for polish.