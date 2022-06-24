# OddsPortal-WebScraper

In the last year of my University Degree in "Statistical Sciences of Economy and Business" I had the pleasure to help one of my uni friends in the writing of his Thesis.
As he had a very deep passion for sports, he decided to merge his hobby with statistics. Fortunately for him, sport and statistics are in fact very close to each other, especially in the field of betting. </br>
What he wanted to do was trying to **evaluate the odds' precision**. The way he intended to do it was by comparing Asian Handicaps and Over/Unders used before the match for bets with the final result of the match itself.

> ### Asian Handicap
> Asian handicap betting is a form of betting in which teams are handicapped according to their form so that a stronger team must win by more points for a bet on them to win.

> ### Over/Under
> The over/under predicts the combined score of the two teams. Then, the bettors will bet if the combined score would be either more than or less than that number.

For every match, every possible score of both the AH and the O/U is given two odds, one represents the probability that the real AH or O/U will be lower, the other represents the probability that the two will be higher. In this way, the Asian Handicap or the Over/Under for which the two odds are equal (or very near to one another) is the one that the betting market predicts as more probable.<br>
<br>
## An example to understand better
I'll give you an example:<br>
<p align = "center">
<img width="500" alt="image" src="https://user-images.githubusercontent.com/98034877/175402083-d465e805-4357-4e5f-935b-c0e24e4bbe07.png">
</p>

In [Game 1 of the 2022 Finals betweet Golden State Warriors and Boston Celtics](https://www.oddsportal.com/basketball/usa/nba/golden-state-warriors-boston-celtics-MweE8wV8/#ah;1), the two odds reach the same value (1.90) at the AH -3.5. This means that, for the betting market, it is equally probable that the final score will be more than 3.5 points in favor of GSW or less than 3.5 points in favor of GSW, that is to say that the betting market best prediction is that GSW will win with 3.5 points over Boston.<br> 
<br>
In the same match, this is the Over/Under odds:
<p align = "center">
<img width="500" alt="image" src="https://user-images.githubusercontent.com/98034877/175519260-ff768b23-9558-4b00-93d4-0f15e3df3254.png">
</p>
The two odds reach the same value (1.90) at O/U +214. This means that, for the betting market, it is equally probable that the final combined score will be more than or less than 214 points, that is to say that the betting market best prediction is that the combined points will be 214.<br> 
<br>

> ### The objective
> What my friend wanted to do was to compare the AH and O/U in which the two odds reache the same value with the real difference in point (AH) and the real combined score (O/U)

## The Scraper
But why was I of any importance in this research?<br>
It didn't take long for my friend to realise that there wheren't any dataset that he could use for is research. At the time I had just finished my [Scientific Computing with Python](https://freecodecamp.org/certification/davide_giardini/scientific-computing-with-python-v7)  and [Data Analysis with Python](https://freecodecamp.org/certification/davide_giardini/data-analysis-with-python-v7) FreeCodeCamp's certifications, so I was eager to make a real use out of the Python skills I learned.<br>
<br>
The scraper uses ***Selenium*** and ***Beautiful Soup*** to:
- Access [oddsportal.com](https://www.oddsportal.com/basketball/usa/nba/results/#/)
- Change the time zone
- Loop through the seasons
  - Loop through the pages
    - For every page use the function ***scrape_links*** to scrape, for every match:
      - The teams involved
      - The final score
      - The date
      - The category (Pre-Season, Regular-Season, Play-In, Play-Off)
      - The links to the odds for the match
- For every link just scraped use the function ***scrape_odds*** to:
  - Open the Asian Handicap section, scrape the odds, find the AH for which the two odds are the most near to one another
  - Open the Over/Under section, scraoe the odds, find the O/U for which the two odds are the most near to one another
  - Scrape the score in every quarter
- Use the function ***correction*** to recheck the links that lead to missing values
<br>

## The resulting Dataset

The resulting dataset provides **15868 observation of 12 variables**:

1. Names: the teams involved in the match
2. Link: the link to the odds of the match
3. Score: the final score
4. Score.q: the score at the end of every quarter
5. OverTime: Boolean, True if the match went to Overtime
6. Score.OT: Score at the beginning of the Overtime
7. Date: the date of the match
8. Category: can be Pre-Season, Regular-Season, Play-In, Play-Off
9. AH: the Asian Handicap for which the two odds are the most near to one another
10. diff.AH: the difference between the two nearest odds in the AH section
11. O/U: the Over/Under for which the two odds are the most near to one another
12. diff.OU: the difference between the two nearest odds in the O/U section
