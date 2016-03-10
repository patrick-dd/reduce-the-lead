
# Reduce the lead

The project's goal is to help local health departments in the United States target their testing efforts to identify the most vulnerable people to lead poisoning.

This is a terminal based program that provides a ranking of lead
poisoning risk among children in a given jurisdiction. The program
allows the user to focus on regions from the State level to the Census
block group level. A text file of the ranked regions and a map is
provided.

Reduce-the-lead relies on some libraries

* Pandas
* GeoPandas
* census
* us
* pickle
* sci-kit learn

### Why provide a ranking?

In this analysis I provide priorities for testing at the State, County, Tract and Census block level. This means that the database provides information for Federal, State and County level health practitioners [1]. Specifically, I provide a ranking of regions based on the Federal Government's analysis of what populations are at risk. This ranking is not meant to be the final word, but the start of a conversation.
    
The motivation for this analysis is the point that in the United States there is an inadequate organisation of testing. Two examples highlight this point. First, 21 States do not provide information to the Center for Disease Control and Prevention ([CDC](www.cdc.gov)). Second, of those that do send information, the information sent is inadequate. It is now acknolowedged that there is no safe BLL in children. Many states only send BLLs for children above thresholds now considered unsafe. We need to test and organise information better.

I rely on the CDC to determine which groups are at risk. I then use data from the US Census office that can pinpoint these groups at the highest spatial resolution. Often, this is at the 'block group' or census tract. A typical tract covers between 2500 and 8000 people. A tract is made of block groups, with the typical block group covering between 600 and 3000 people. For some variables, we can only obtain aggregation at the County level.

Although many regions have unsatisfactory rates of testing, many regions test well. For example, NYC has high testing rates. I still provide information on testing in these regions for three reasons. First, the analysis has the benefit of augmenting the work of these health departments. For instance, it is plausible that testing may miss groups at risk. Second and most important for future work, if we obtained data from regions with good testing, we could validate the performance of this analysis. Specifically, we could measure the performance of the maps: how accurate was this tool? How sensitive was our tool? Third, there is a low marginal cost to adding in new regions.

[1] Perhaps even [special districts](https://www.youtube.com/watch?v=3saU5racsGE) could use this information!
    
### How Reduce the lead works    

### Which groups are at risk?

The CDC defines children from the following groups as [at a higher risk](http://www.cdc.gov/nceh/lead/tips/populations.htm)
    - ~~poor~~
    - ~~members of racial-ethnic minority groups~~
    - ~~recent immigrants~~
    - ~~live in older, poorly maintained rental properties~~
    - ~~have parents who are exposed to lead at work~~
    - pregnant woman
    - refugees, or
    - ~~children adopted from other countries~~

In this analysis, I will collect data that best approximates these groups. I will provide all data so that policy makers can best define the combination of at risk groups.
 
A problem with providing information along 8 dimensions is that we're unlikely to obtain a single ranking of districts to visit. As a first attempt at resolving this, I will provide a ranking based on the linear combination of these dimensions that explains most of the variation in the data. Specifically, I'll take the first component of a principal component analysis and rank census blocks based on this. Because laws vary at the State level, I'll run the analysis for each State. This is not a 'best' ranking, the aim is to start the conversation.
 
