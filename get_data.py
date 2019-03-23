import pandas as pd
import numpy as np
import praw
import string
import re
import nltk

# function to return subreddit posts associated with a given keyword
def get_keyword_data(reddit,sub,kw,word_set):
    
    keyword_df = pd.DataFrame()
    
    # get posts associated with the keyword 
    key_posts = sub.search(kw)
    
    # get post-level data for each post
    for p in key_posts:
        post_df = get_post_data(reddit,p,word_set)
        keyword_df = keyword_df.append(post_df)
    
    keyword_df = keyword_df.reset_index(drop=True)
    
    # return df with each row being a single post
    return keyword_df
    
    
# function to get post-level data 
def get_post_data(reddit,p,word_set):
    
    # get post id, then send it off to get comment data
    post_vars = vars(p)
    post_id = post_vars['id']
        
    print('now parsing post ', post_vars['id'])
                
    # send the post off for comment-level processing
    comment_df = get_comment_data(reddit,post_id,word_set)
        
    # return a dataframe with clothing item data for the given post
    return comment_df
 
# function to get comment-level data       
def get_comment_data(reddit,post_id,word_set):
    
    comment_df = pd.DataFrame()
    
    punctuation_table = str.maketrans(dict.fromkeys(string.punctuation))
    digit_table = str.maketrans(dict.fromkeys(string.digits))
    
    # get the post submission based on the post id
    submission = reddit.submission(id=post_id)
    
    # parse through top-level comments; get score, look for words of interest
    for tlc in submission.comments:
        v = vars(tlc)
        body = v['body']
        score = v['score']
        comment_id = v['id']
        
        # isolate unique sentences in the comment body for pos tagging
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',body)
        for url in urls:
            body = body.replace(url,'')
        sentences = re.split('.\n',body)
        sentences = [s.translate(punctuation_table).translate(digit_table).lower() for s in sentences]
            
        for sentence in sentences:
            pos_df = pd.DataFrame(nltk.pos_tag(nltk.word_tokenize(sentence)),columns=['word','pos'])
            try:
                pos_df['next_word'] = list(pos_df.loc[1:,'word'].values) + ['']
            except:
                pos_df['next_word'] = ''
            pos_df['adjective'] = ''
            intersection = set(re.findall(r'(?: ' + ' | '.join(word_set) + ' )',sentence))
            
            for match in intersection:
                idx_match = pos_df['next_word'].str.contains(match.strip())
                idx_adj = idx_match & (pos_df['pos'] == 'JJ')
                pos_df.loc[idx_adj,'adjective'] = pos_df.loc[idx_adj,'word']
                match_df = pd.DataFrame({'post_id':[post_id]*sum(idx_match),
                                         'comment_id':[comment_id]*sum(idx_match),
                                         'comment_score':[score]*sum(idx_match),
                                         'item':[match.strip()]*sum(idx_match),
                                         'adjective':pos_df.loc[idx_match,'adjective'].values})
                comment_df = comment_df.append(match_df)
    
    return comment_df

# load the womens clothing vocabulary we'll be using for this project
# note: clothing categories and clothing sub-types are based loosely on 
# classification schemes for womens' clothing on department store websites.
clothing_vocab = pd.read_csv('data/womens_clothing_vocab.csv') 
clothing_vocab = clothing_vocab.fillna(value='')

# user data for  reddit auth
client_id = 'your_client_id'
client_secret = 'your_client_secret'
username = 'your_username'
password = 'your_password'
user_agent = 'your_user_agent'

# search keyword
keyword = 'business-casual'

# words of interest to parse from comments
word_set = np.delete(np.unique(clothing_vocab[['item','item_singular']].values.flatten()),0)

# initialize praw utility to help get data
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent,
                     username=username,
                     password=password)

# specify subreddit of interest
subreddit = reddit.subreddit('femalefashionadvice')

keyword_df = get_keyword_data(reddit,subreddit,keyword,word_set)

# merge reddit data with clothing vocab to add clothing category column
data_plural = keyword_df.merge(clothing_vocab[['parent_item','item']],how='inner',on='item')
singular_vocab = clothing_vocab.loc[clothing_vocab['item_singular']!= '',['parent_item','item','item_singular']]
data_singular = keyword_df.merge(singular_vocab,how='inner',left_on='item',right_on='item_singular').drop(columns=['item_x','item_singular']).rename(columns={'item_y':'item'})
data = data_plural.append(data_singular).reset_index(drop=True)

# fix cases where item is used as modifier on parent item (e.g. "sheath dress")
for parent_item in np.unique(data['parent_item']):
    unique_items = list(np.unique(clothing_vocab.loc[clothing_vocab['parent_item'] == parent_item,['item','item_singular']].values.flatten()))
    try:
        unique_items.remove('')
    except:
        unique_items = unique_items
    try:
        unique_items.remove(parent_item)
    except:
        unique_items = unique_items
    idx = (data['parent_item'] == parent_item) & (data['adjective'].isin(unique_items))
    data.loc[idx,'item'] = data.loc[idx,'adjective']
    idx_singular = (idx & data['item'].isin(clothing_vocab['item_singular']))
    data.loc[idx_singular,'item'] = data.loc[idx_singular,'item'] + 's'
    data.loc[idx,'adjective'] = np.nan

data.to_csv('data/business_casual.csv',index=False)

