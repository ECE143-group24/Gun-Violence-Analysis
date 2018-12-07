# Helper functions to be used in data processing and visualization

import pandas as pd
import numpy as np
from plotly.offline import iplot
import plotly.graph_objs as go
from collections import defaultdict

def load_data(path):
    '''
    Loads data and returns dataframe with some added columns
    inp: path - path of csv file
    out: pandas dataframe
    '''
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['monthday'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.weekday
    df['loss'] = df['n_killed'] + df['n_injured']

    return df

def get_bucketed_data(data,column,max_num):
    '''
    Returns labels and values of data after bucketing upto max_num
    inp: data, column, max_num
    out: labels, values (list)
    '''
    data['temp'] = data[column].apply(lambda x : str(max_num)+'+' if x>=max_num else str(x))
    tempdf = data['temp'].value_counts().reset_index()

    labels = list(tempdf['index'])
    values= list(tempdf['temp'])

    return labels, values

def get_age_distribution(person_type_data,age_data,target_person_type):
    '''
    Returns histogram of age given person type(victim/suspect)
    inp: person and age data,target_person_type
    out: histogram - dict
    '''
    person_type_df=person_type_data.str.replace("[::|,]"," ").str.lower()
    age_df=age_data.str.replace("[::|,]"," ").str.lower()

    age_groups = defaultdict(int)
    for i in range(len(person_type_df)):
        person_type=str(person_type_df[i]).split()
        person_type=dict(zip(person_type[::2], person_type[1::2]))
        age=str(age_df[i]).split()
        age=dict(zip(age[::2],age[1::2]))

        for key in person_type:
            value=person_type[key]
            if target_person_type in value and key in age:
                target_age = age[key]
                age_groups[target_age] += 1

    return age_groups

def get_person_type_counts(data,column,types):
    '''
    Returns counts of person types given data, column and needed types
    inp: data,column,types
    out: counts (list)
    '''
    p_status = data[column].str.replace("[::0-9|,]","").str.upper()
    p_status = p_status[p_status.notnull()]
    p_status = pd.DataFrame(p_status)

    for p_type in types:
        p_status[p_type]  = p_status[column].str.count(p_type)

    counts = [sum(p_status[p_type]) for p_type in types]

    return counts

def get_mean_vs_data(data1,data2,max_num):
    '''
    Returns mean of data1 vs data2 over a range (1,max_num)
    inp: data1,data2,max_num
    out: x,y - lists
    '''
    x=[]
    y=[]
    for n in range(1,max_num):
        inds=data1==n
        val=np.mean(data2[inds])
        x.append(n)
        y.append(val)

    return x,y

def plot_pie(labels,values,title):
    '''
    Plot pie chart given labels, values, title
    inp: labels, values, title
    '''
    trace1 = go.Pie(labels=labels, values=values)
    layout = dict(height=600, title=title, legend=dict(orientation="h"));
    fig = go.Figure(data=[trace1], layout=layout)
    iplot(fig)

def plot_histogram(data,xaxis,title):
    '''
    Plot histogram given data,xaxis,title
    inp: data,title
    '''
    trace1 = go.Bar(x=list(data.keys()), y=list(data.values()))
    layout = dict(height=400, title=(title).upper(),
                  xaxis=xaxis, legend=dict(orientation="h"))
    fig = go.Figure(data=[trace1], layout=layout)
    iplot(fig)