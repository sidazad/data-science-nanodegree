import sys

sys.path.append("../dsutils")
import pandas as pd
import pandasql
from dsutils import stat_test
from ggplot import *


def get_data(filename="improved_set.csv"):
    return pd.read_csv(filename)


def get_entries_by_date(df):
    df = df.rename(columns={'UNIT': 'unit', 'ENTRIESn_hourly': 'entries', 'DATEn': 'date'})
    # print df.head(5)
    q = """
        SELECT date, SUM(entries) from df group by date
    """
    entries = pandasql.sqldf(q, locals())
    entries = entries.rename(columns={'SUM(entries)': 'entries'})
    return entries

def get_entries_by_hour(df):
    df = df.rename(columns={'ENTRIESn_hourly': 'entries'})
    # print df.head(5)
    q = """
        SELECT hour, SUM(entries) from df group by hour
    """
    entries = pandasql.sqldf(q, locals())
    entries = entries.rename(columns={'SUM(entries)': 'entries'})
    return entries

def get_entries_by_unit(df):
    df = df.rename(columns={'UNIT': 'unit', 'ENTRIESn_hourly': 'entries'})
    q = """
        SELECT unit, SUM(entries) from df group by unit
    """
    entries = pandasql.sqldf(q, locals())
    entries = entries.rename(columns={'SUM(entries)': 'entries'})
    return entries

def get_rain_norain_entries_by_unit(df):
    df = df.rename(columns={'UNIT': 'unit', 'ENTRIESn_hourly': 'entries'})
    q = """
        SELECT unit,rain, SUM(entries) from df group by unit, rain
    """
    entries = pandasql.sqldf(q, locals())
    #print entries
    #print entries[entries["rain"]!=1]["SUM(entries)"]
    return (entries[entries["rain"] == 1]["SUM(entries)"], entries[entries["rain"] != 1]["SUM(entries)"])


def get_rain_norain_entries_by_date(df):
    df = df.rename(columns={'UNIT': 'unit', 'ENTRIESn_hourly': 'entries', 'DATEn': 'date'})
    # print df.head(5)
    q1 = """
        SELECT date,rain, SUM(entries) from df where rain=1 group by date, rain
    """
    entries1 = pandasql.sqldf(q1, locals())
    # print entries[entries["rain"]!=1]["SUM(entries)"]
    entries1 = entries1.rename(columns={'SUM(entries)': 'entries'})

    q2 = """
        SELECT date,rain, SUM(entries) from df where rain=0 group by date, rain
    """
    entries2 = pandasql.sqldf(q2, locals())
    # print entries[entries["rain"]!=1]["SUM(entries)"]
    entries2 = entries2.rename(columns={'SUM(entries)': 'entries'})

    return (entries1, entries2)


def check_normality(rain, norain):
    return (stat_test.is_normal(rain.values), stat_test.is_normal(norain.values))


def part1():
    df = get_data()
    # print df.head(100)
    rain, norain = get_rain_norain_entries_by_unit(df)
    are_normal = check_normality(rain, norain)

    print are_normal
    if not stat_test.mann_whitney_t_test(norain.values, rain.values):
        print "Null Hypothesis Failed implying Rain and No Rain data are not the same"
    print len(rain.values), len(norain.values)
    print stat_test.get_mean_median(rain.values)
    print stat_test.get_mean_median(norain.values)


def part3_histogram():
    df = get_data()
    # print df.head(100)
    rain, norain = get_rain_norain_entries_by_date(df)
    print ggplot(rain,aes(x='entries')) + geom_histogram(data=rain,binwidth=100000, fill='red', alpha=0.2) + geom_histogram(data=norain,binwidth=100000, fill='green', alpha=0.3)
    #print ggplot(aes(x='entries'), data=rain) + geom_histogram(binwidth=100000) +  ggtitle("RAIN")
    #print ggplot(aes(x='entries'), data=norain) + geom_histogram(binwidth=100000) +  ggtitle("NO RAIN")

def ridership_by_date(df):
    entries = get_entries_by_date(df)
    print entries.head(5)
    entries['date'] = entries['date'].apply(lambda x: int(x.split("-")[1]))
    print entries.head(5)
    print ggplot(aes(x='date', y='entries'), data=entries) + geom_line()

def ridership_by_hour(df):
    entries = get_entries_by_hour(df)
    print entries.head(5)
    #entries['date'] = entries['date'].apply(lambda x: int(x.split("-")[1]))
    print entries.head(5)
    print ggplot(aes(x='hour', y='entries'), data=entries) + geom_line()



def part3_freeform():
    df = get_data()
    #ridership_by_date(df)
    ridership_by_hour(df)

def find_top_five_busy_units(df):
    entries = get_entries_by_unit(df)
    entries = entries.sort(columns=['entries'], ascending=False)
    print entries
    print ggplot(entries,aes(x='entries')) + geom_histogram(data=entries,binwidth=100000, fill='blue')


def part5():
    df = get_data()
    find_top_five_busy_units(df)

if __name__ == "__main__":
    #part1()
    #part3_histogram()
    #part3_freeform()
    part5()


def check_normality(rain, norain):
    return (stat_test.is_normal(rain.values), stat_test.is_normal(norain.values))


#
# if __name__ == "__main__":
# df = get_data()
#     #print df.head(100)
#     rain, norain = get_rain_norain_entries_by_unit(df)
#     are_normal = check_normality(rain, norain)
#     print are_normal
#     if not stat_test.mann_whitney_t_test(norain.values, rain.values):
#         print "Null Hypothesis Failed implying Rain and No Rain data are not the same"
#     print stat_test.get_mean_median(rain.values)
#     print stat_test.get_mean_median(norain.values)






# References
# https://piazza.com/class/i2ddoj5wy8i6j5?cid=159
# http://docs.scipy.org/doc/scipy-0.13.0/reference/stats.html
# http://docs.scipy.org/doc/scipy-0.13.0/reference/generated/scipy.stats.ttest_ind.html
# http://forums.udacity.com/questions/100157066/cannot-import-pandasql-for-python-amd64
# http://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U_test
# http://www.graphpad.com/guides/prism/6/statistics/index.htm?how_the_mann-whitney_test_works.htm
