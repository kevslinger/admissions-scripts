# Some Scripts for Ravenclaw Admissions Responses sheet

The sheet is currently at least 3 years old, and is in pretty brutal need of repair. Some of the options I'm considering:
- A light cleaning, with some additional information pasted but keeping the main structure of the sheet the same (only using the available JS scripts/etc)
- Adding additional GS/JS code to the sheet to be able to add more information.
- Writing sheets formulae (*gasps*) that can extract more information (e.g. from the reddit.user.about.json site)
- Writing a routinely run python script which uses selenium to extract information from a site e.g. https://www.redditmetis.com, which gives us more powerful insights
- Doing something that isn't a sheet (*gasps*)

Ideally, by doing any (or multiple) of the above, one would not need to explore the user's reddit feed, because the e.g. redditmetis overview would be sufficient information. Of course, some would slip through the cracks, but that is true also of someone looking at the most recent ~20 posts/comments

Current problems I have with the current approach:
- The way it's currently setup, I need to read the form responses on "Sheet1" before even seeing whether or not they pass the karma threshold. If they have insufficient karma, consider that a desk reject in my mind.
- I need to look at both "Sheet1" and "Helper" tabs in order to get all the information I need. Ideally, all information will be contained on one tab.
- A perusal of the user's reddit page will probably only give me a glimpse into their most recent history, which is often times just a bunch of r/hp comments to prepare for the application.
- There's also something that should be fixed about that thing where it says "TRUE" if not yet checked, "FALSE" if below the karma threshold, and "ALREADY ADDED" otherwise. Because then it says, "ALREADY ADDED" if I deny, which isn't true. it's hard, though. I don't want to hardcode people's names onto the checker.