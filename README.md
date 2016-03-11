
# Reduce-the-lead

The project's goal is to help local health departments in the United States target their testing efforts to identify the most vulnerable people to lead poisoning.

This is a terminal based program that provides a ranking of lead
poisoning risk among children in a user chosen jurisdiction. The program
allows the user to focus on regions from the State level to the Census
block group level. A text file of the ranked regions and a map is
provided.

Reduce-the-lead relies on some libraries

* [Pandas](pandas.pydata.org)
* [GeoPandas](geopandas.org)
* [census](github.com/sunlightlabs/census)
* [US](pypi.python.org/pypi/us)
* [scikit-learn](scikit-learn.org)

If you want to download data yourself, you will need a [US Census
API](www.census.gov/developers/) key.

You will also need to create a file called ``census_api.ini`` file. In
this file, do this

```
[census_api]
key: <<YOUR-CENSUS-KEY>>
```

After creating the ``census_api.ini`` file, you can run
``data_download.py`` to do its magic. Or you can unzip ``data.zip``.

To run Reduce-the-lead, simply type ``python reducethelead.py`` at the
command line.

To see how ``reducethelead.py`` operates, look at the
``example_reducingthelead.ipynb`` IPython notebook.

### Why provide a ranking?

The motivation for this analysis is the point that in the United States
there is an inadequate organisation of testing. Two examples highlight 
this point. First, 21 States do not provide
information to the Center for Disease Control and Prevention
([CDC](www.cdc.gov)). Second, of those that do send information, the
information sent is inadequate. It is now acknolowedged that there is no
safe threshold BLL in children. Many states only send BLLs for children above
thresholds. We need to test and organise
information better.

### How Reduce-the-lead works

I rely on the CDC to determine which groups are at risk.

The CDC defines children from the following groups as 
[at a higher risk](http://www.cdc.gov/nceh/lead/tips/populations.htm)

    - poor
    - members of racial-ethnic minority groups
    - recent immigrants
    - live in older, poorly maintained rental properties
    - refugees
    - children adopted from other countries
    - have parents who are exposed to lead at work, or
    - pregnant woman

In this analysis, I will collect data that best approximates these groups. 

The data comes from the five year US Census American Community Survey
ending in 2013. This data source provides the highest possible spatial
resolution, allowing for ranking of Census block groups. A typical block
group contains between 600 and 3000 people. The cost is that the
information is not immediate. The data can be interpreted as five year
averages. Reduce-the-lead results should be used with caution in rapidly
changing communities.

In this version, I have data that approximates the first six of these
groups. Data on parents' jobs or pregnancy was not available at a low
enough spatial resolution.

### How does Reduce-the-lead generate a single ranking from 8 dimensions?

A problem with providing information along 8 dimensions is that we're 
[unlikely to obtain a single ranking of districts to visit.](http://en.wikipedia.org/wiki/arrow%27s_impossibility_theorem) 
As a first attempt at resolving this, I will provide a ranking based on the 
linear combination of these dimensions that explains most of the variation 
in the data. Specifically, I'll take the first component of a principal 
component analysis and rank census blocks based on this. Because laws vary 
at the State level, I'll run the analysis for each State. This is not a 
'best' ranking, the aim is to start the conversation.

TL;DR: with [Principal Components
Analysis](http://en.wikipedia.org/wiki/principal_components_analysis).


Reduce-the-lead can augment the work of 
health departments that have good testing procedures. For instance, it is 
plausible that testing may miss some groups at risk. In addition, if we 
obtained data from regions with good testing, we could validate the 
performance of this analysis. Specifically, we could measure the 
performance of the maps: how accurate was Reduce-the-lead? How sensitive 
was Reduce-the-lead? This information  will help improve Reduce-the-lead 
and in turn, improve targeting of lead poisoning tests at the local level.

