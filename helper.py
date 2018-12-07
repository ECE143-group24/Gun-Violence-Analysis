# Helper functions to be used in data processing and visualization

import pandas as pd
import numpy as np
from plotly.offline import iplot, plot
import plotly.graph_objs as go
from collections import defaultdict
import calendar


def load_data(path):
    '''
    Loads data and returns dataframe with some added columns
    inp: path - path of csv file
    out: pandas dataframe
    '''
    df = pd.read_csv(path)
    missing_row = ['sban_1', '2017-10-01', 'Nevada', 'Las Vegas', 'Mandalay Bay 3950 Blvd S', 59, 489, 'https://en.wikipedia.org/wiki/2017_Las_Vegas_shooting', 'https://en.wikipedia.org/wiki/2017_Las_Vegas_shooting', '-', '-', '-', '-', '-', '36.095', 'Hotel', 
               '-115.171667', 47, 'Route 91 Harvest Festiva; concert, open fire from 32nd floor. 47 guns seized; TOTAL:59 kill, 489 inj, number shot TBD,girlfriend Marilou Danley POI', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    df.loc[len(df)] = missing_row
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['monthday'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.weekday
    df['loss'] = df['n_killed'] + df['n_injured']
    df['month_day_comb'] = df['date'].dt.strftime('00-%m-%d')

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
    
############  
# Time trends plot
def incidents_year_Barplot(df, title = 'Gun Violence Incidents by year'):
    '''
    Bar plot of the number of incidents by year.
    inp: 
        df: dataframe
        title: str
    '''
    year_stat = df['year'].value_counts()
    x1 = year_stat.index.tolist()[:5]
    y1 = year_stat.values.tolist()[:5]
    trace1 = go.Bar(x = x1, y = y1, name = 'year count', opacity = 0.9,
                    marker = dict(
                        color = ['rgba(222,45,38,0.8)', 'rgba(222,45,38,0.8)', 'rgba(222,45,38,0.8)',
                                 'rgba(222,45,38,0.8)', 'rgba(204,204,204,1)']))
    layout = go.Layout(title = title)
    fig = go.Figure(data = [trace1], layout = layout)
    return iplot(fig)

def incidents_month_Barplot(df, title = 'Average number of Gun Violence Incidents by month'):
    '''
    Bar plot of the average number of incidents by month.
    inp: 
        df: dataframe
        title: str
    '''
    month_count = defaultdict(int)
    for i in range(len(df)):
        if df['year'][i] in [2014, 2015, 2016, 2017]:
            month_count[df['month'][i]] += 1
    month_mean = defaultdict(int)
    for i in month_count.keys():
        month_mean[i] = month_count[i] / len([2014, 2015, 2016, 2017])
        
    x2 = list(month_mean.keys())
    y2 = list(month_mean.values())
    trace2 = go.Bar(x = [calendar.month_abbr[int(x)] for x in x2], y = y2, name = 'month', 
                    opacity = 0.9, marker = dict(color = '#f9d00f'))
    trace2_1 = go.Scatter(x = [calendar.month_abbr[int(x)] for x in x2], y = y2, name = 'month', 
                    opacity = 0.9, mode = 'lines', marker = dict(color = '#f12d2d'))
    layout = go.Layout(title = title)
    fig = go.Figure(data = [trace2, trace2_1], layout = layout)
    return iplot(fig)

def incidents_weekday_lineplot(df, title = 'Average number of Gun Violence Incidents by weekday'):
    '''
    Bar plot of the average number of incidents by weekday.
    inp: 
        df: dataframe
        title: str
    '''
    weekday_count = defaultdict(int)
    for i in range(len(df)):
        weekday_count[df['weekday'][i]] += 1
    
    weekday2018_count = defaultdict(int)
    for i in range(len(df)):
        if df['year'][i] == 2018:
            weekday2018_count[df['weekday'][i]] += 1
        
    weekmap = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'}
    weekday_mean = defaultdict(int)
    for i in weekday_count.keys():
        weekday_mean[weekmap[i]] = (weekday_count[i] - weekday2018_count[i])*1/(5 + 3/12) + weekday2018_count[i]*(0.25/(5 + 3/12))

    x3 = list(weekmap.values())
    y3 = [weekday_mean[i] for i in list(weekmap.values())]
    trace3_1 = go.Bar(x = x3, y = y3, name = 'weekday', opacity = 0.9, 
                        marker = dict(color = '#3667a6'))
    trace3_2 = go.Scatter(x = x3, y = y3, name = 'weekday', opacity = 0.9, 
                        mode = 'lines', marker = dict(color = '#f12d2d'))
    layout = go.Layout(title = title)
    fig = go.Figure(data = [trace3_1, trace3_2], layout = layout)
    return iplot(fig)

###############
# Time Series Plot
def time_series_plot(df, year, title):
    '''
    Return the time series plot of specified year with title.
    inp:
        df: dataframe
        year: int
        title: str
    '''
    temp = df[df['year'] == year].groupby('date').agg({'state': 'count', 'n_killed': 'sum', 'n_injured': 'sum'}).reset_index().rename(columns = {'state': 'incidents'})
    trace1 = go.Scatter(x = temp.date, y = temp.incidents, name = 'Total number of Incidents', 
                        mode = 'lines', marker = dict(color = '#418bf4'))
    trace2 = go.Scatter(x = temp.date, y = temp.n_killed, name = 'Total number of killed', 
                        mode = 'lines', marker = dict(color = '#ce2812'))
    trace3 = go.Scatter(x = temp.date, y = temp.n_injured, name = 'Total number of injured', 
                        mode = 'lines', marker = dict(color = '#daa1e2'))
    layout = dict(height = 350, title = title + ' - ' + '%s' % (year), 
                  legend = dict(orientation = "h", x = -.01, y = 1.2), xaxis = dict(title = 'Date Time', ticklen = 1))
    fig = go.Figure(data = [trace1, trace2, trace3], layout = layout)
    return iplot(fig)

def top10_incidents(df, year = [2014, 2015, 2016, 2017], title = 'Top 10 dates that Gun Violence Incidents happened'):
    '''
    Scatter plot of top 10 dates that Gun Violence Incidents happened.
    inp:
        df: dataframe
        year: list
        title: str
    '''
    holiday = {}
    for y in year:
        temp = df[df['year'] == y].groupby('month_day_comb').agg({'state': 'count', 'n_killed': 'sum', 'n_injured': 'sum'}).reset_index().rename(columns = {'state': 'incidents'})
        holiday[y] = temp.nlargest(10, 'incidents')
        
    color = ['#e0bb20', '#f07b3f', '#769fcd', '#283c63']
    trace = [go.Scatter(x = holiday[year[i]].month_day_comb, y = holiday[year[i]].incidents, name = '%s' % (year[i]), 
                mode = 'markers', marker = dict(size = 15, color = color[i])) for i in range(len(year))]
    layout = dict(height = 350, title = title, 
              legend = dict(orientation = "h", x = -.01, y = 1.2), xaxis = dict(title = 'Date Time', tickformat = '%b-%d'))
    fig = go.Figure(data = trace, layout = layout)
    return iplot(fig)

####################
# Numbers of guns registered by state    
def guns_per_capita_plot(statedf, xvalue, colorscale):
    '''
    Scatter plot about the number of guns registered with color bar.
    inp:
        statedf: dataframe
        xvalue: str
        colorscale: str
    '''
    data = [
    {
    'x': statedf[xvalue],
    'y': statedf['counts'],
    'mode': 'markers',
    'text': statedf['state'],
    'marker': {
        'color': statedf['Rank'],
        'size': 15,
        'showscale': True,
        'colorscale': colorscale,
        'colorbar': dict(title = 'Rank(guns_per_capita)'),
        'opacity': 0.9
        }
    }
   ]
    layout = go.Layout(title = "Gun Violence Incidents VS %s by state (2017)" % (xvalue), 
                       xaxis = dict(title = 'Total %s' % (xvalue)),
                       yaxis = dict(title = 'Gun Violence Incidents'))
    fig = go.Figure(data = data, layout = layout)
    return iplot(fig)
    
###########
# Gun Laws on Gun Violence Incidents
def rise_of_laws(data, year = [2014, 2015, 2016, 2017], title = "Rise of Gun Violence Laws"):
    '''
    Stackbar plot of rise of gun violence laws by year in different states.
    inp:
        year: list
        title: str
        data: DataFrame
    '''
    color = ['#03002c', '#bb0029', '#f5841a', '#ffdd00']
    trace = [go.Bar(x = data['state'], y = data[str(year[i])], name = '%s' % (year[i]), marker = dict(color = color[i])) for i in range(len(year))]
    layout = go.Layout(barmode = 'stack', title = title + ': %s - %s' % (year[0], year[-1]))
    fig = go.Figure(data = trace, layout = layout)
    return iplot(fig)

################
# state wise incidents plot
def state_wise_plot(statesdf,tl = 'Number of gun voilence incidents per state', colorscale = [[0.0, 'rgb(242,240,247)'],[0.2, 'rgb(218,218,235)'],[0.4, 'rgb(188,189,220)'],\
            [0.6, 'rgb(158,154,200)'],[0.8, 'rgb(117,107,177)'],[1.0, 'rgb(84,39,143)']]):
    '''
    Plot the state wise plot using iplot.
    inp:
        statesdf: Dataframe
        tl: str
        colorscale: str
        
    '''
    data = [ dict(
        type = 'choropleth',
        colorscale = colorscale,
        autocolorscale = False,
        showscale = True,
        locations = statesdf['state_code'],
        z = statesdf['counts'],
        locationmode = 'USA-states',
        marker = dict(
            line = dict (
                color = 'rgb(255, 255, 255)',
                width = 2
            ) ),
        ) ]
 
    layout = dict(
            title = tl,
            geo = dict(
                scope = 'usa',
                projection = dict( type='albers usa' ),
                showlakes = True,
                lakecolor = 'rgb(255, 255, 255)',
                countrycolor = 'rgb(255, 255, 255)')
                 )

    figure = dict(data=data, layout=layout)
    iplot(figure)

#############
# state wise incidents rate bar plot
def Barplot(x_data,y_data,title):
    '''
    Plot state/citywise wise bar plot
    inp:
        x_data: Dataframe
        y_data: Dataframe
        title: str
    '''
    trace1 = go.Bar(
        x=x_data,
        y=y_data,
        name='Location Types',
        orientation = 'v',
        marker=dict(color='purple'),
        opacity=0.7
    )

    data = [trace1]
    layout = go.Layout(
        height=400,
        margin=dict(b=150),
        barmode='group',
        legend=dict(dict(x=-.1, y=1.2)),
        title = title,
    )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='grouped-bar')

def city_data_prepare(df):
    '''
    prepare data for city population plot
    inp:
        df: Dataframe
    return:
        ip: Dataframe
    '''
    tempdf = df.groupby(by=['city_or_county']).agg({'n_killed': 'sum', 'n_injured' : 'sum', 'city_population' : 'mean', 'state' : 'count'}).reset_index().rename(columns={'state' : 'total_incidents', 'n_killed' : 'total_killed', 'n_injured' : 'total_injured'})
    tempdf['incidents_population_ratio'] = 1000*tempdf['total_incidents'] / (tempdf['city_population']+1) 
    tempdf['killed_population_ratio'] = 1000*tempdf['total_killed'] / (tempdf['city_population']+1) 
    tempdf['injured_population_ratio'] = 1000*tempdf['total_injured'] / (tempdf['city_population']+1) 
    tempdf['loss_population_ratio'] = 1000*(tempdf['total_killed'] + tempdf['total_injured']) / (tempdf['city_population']+1) 
    i_p = tempdf.sort_values(['incidents_population_ratio'], ascending=[False])
    i_p = i_p[i_p['city_population'] > 500000][:25]
    return i_p

def scatter_plot(x_data, y_data,text, title, x_title, y_title):
    '''
    Scatter plot for analysis.
    inp:
        x_data: Dataframe
        y_data: Dataframe
        title,x_title,y_title:str
    '''
    data = [
    {
        'x': x_data,
        'y': y_data,
        'mode': 'markers+text',
        'text' : text,
        'textposition' : 'bottom center',
        'marker': {
            'color': "#42f4bc",
            'size': 15,
            'opacity': 0.9
        }
    }
    ]

    layout = go.Layout(title=title, 
                   xaxis=dict(title=x_title),
                   yaxis=dict(title=y_title)
                  )
    fig = go.Figure(data = data, layout = layout)
    iplot(fig, filename='scatter-colorscale')
    
