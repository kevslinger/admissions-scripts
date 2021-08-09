# Some Scripts for Ravenclaw Admissions Responses sheet


## Installation
We recommend you set up a python virtual environment using `virtualenv venv -p=3.8` (or your favorite
flavor or python3). Source your venv with `source venv/bin/activate`, then install the dependencies with
`pip install -r requirements.txt`. In addition, because we're interacting with Reddit and Google Sheets
(oh and also Selenium), we have two libraries which need extra care in order to use them:
- [Praw](https://github.com/praw-dev/praw)
- [Gspread](https://github.com/burnash/gspread)
- [Selenium](https://github.com/SeleniumHQ/selenium)

Once you've finished the pip installation, continue on to the next section to get set up with these libraries

## Getting Started: Local Setup
To use PRAW, you'll need to create a reddit app for your account (see details via the 
[PRAW docs](https://praw.readthedocs.io/en/stable/getting_started/authentication.html)). 
For Gspread, you'll need to create credentails on the Google Cloud console (see details via the
[Gspread docs](https://docs.gspread.org/en/latest/oauth2.html)). The google credentials are much more
annoying to get, but interacting with google sheets is very useful. 
The Gspread docs tell you to put the downloaded json file to `~/.config/gspread/service_account.json` which is
fine for a local installation, but that won't do if we're trying to host somewhere. 
I use the `dotenv` library with a `.env` file for local usage,
and save the values as environment variables for Heroku. Please see the `.env` template [here](.env.template)
to see what values you would need to fill in. For Selenium, you just need to have Chrome installed,
and a valid chromedriver, which you can get [here](https://chromedriver.chromium.org/). Although I have had issues
where my Chrome version is not the same as my Chromedriver version, which selenium doesn't like. Change the paths in 
[constants.py](constants.py) to reflect those paths (the current paths are setup to work with a Heroku instance)


Once you have your `virtualenv` setup with Praw, Gspread, and Selenium installed, you're *almost* ready to 
run stuff! I think all you would have to change in the code then is modify `DATA_TAB_NAME` and `FORM_TAB_NAME` in 
[constants.py](constants.py) to reflect the same values on your sheet, line 85 in 
[update_admissions_sheet.py](update_admissions_sheet.py) with the width of your form responses sheet (from our 
6 to whatever yours is), and then adjust `end_col` from our `X` to whatever yours is (e.g. `W` if you have width 5).

The last thing to do is to set up your sheets the same way we have them set up. So you'd need to have a form tab connected
to your application form and a data tab where you want the processed responses to go. Now, assuming everything is working,
if you run `python update_admissions_sheet.py`, the script will go all the way to the top of the form tab and start
processing from there. To avoid that, copy and past the response right above the most recent *unprocessed* applicant 
from your form tab onto your data tab, and the script should run fine (*he says, not knowing if it will run fine*). 

Okay honestly, if someone can actually reproduce this and get it working, I would be really impressed. Writing this all 
up makes it sound like a nightmare of a chore. But anyways, don't forget to share your admissions sheet with the 
`client_email` from your `.env`, or else the script will get a `403: Forbidden`.

## Moving to Heroku
Once you have the [update_admissions_sheet](update_admissions_sheet.py) script working locally, you can get setup with
a regularly run script on Heroku! Of course, to do that, you'll need a [Heroku](https://www.heroku.com) account with
enough free dyno hours to be able to run the script (10-20 hours should suffice). On the Heroku 
[apps dashboard](https://dashboard.heroku.com/apps), create a new app and name it whatever you'dlike. It'll take you to the
[Deploy](https://dashboard.heroku.com/apps/for-deletion/deploy/heroku-git) tab of your project, where I usually 
go with the `GitHub` deployment method, which can sync up with CI (e.g. [Travis](https://www.travis-ci.com/)), but 
for this project I'm using the `Heroku Git` CLI deployment because it's a little easier to setup. Right below, it 
has instructions for installing the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli), which you should 
do and then push your code to the heroku repo (with `git push heroku main` (remember to never add your `.env` file to git)). Once you've done that, go to the `Settings` tab and find the 
`Config Vars` section. Click `Reveal Config Vars` and then add in all the values from your `.env` file. The script will
be able to see these as `ENV` variables when it runs. 

Once you push your code, heroku should recognize your app as a python application, and add the `heroku/python` buildpack.
If it does not, you can add it by using `heroku buildpacks:set heroku/python`. Then, to get Google Chrome onto the heroku
instance, we need to install two other buildpacks. Currently, when I use `heroku buildpacks`, I get the following output:
```
1. heroku/python
2. https://github.com/heroku/heroku-buildpack-chromedriver.git
3. https://github.com/heroku/heroku-buildpack-google-chrome.git
```
So I think running `heroku:buildpacks add https://github.com/heroku/heroku-buildpack-chromedriver.git` and 
`heroku:buildpacks add https://github.com/heroku/heroku-buildpack-google-chrome.git` in that order will get you to the 
same spot. If you added them via the command line like so, I think you'll need to `git push heroku main` again to push 
them up to the cloud.

Great, now everything should be setup so that when the script runs on Heroku, it'll work. The last thing to do is
set up the scheduler. Go to the `Resources` tab, and in the add-ons search type in `Heroku Scheduler`. It 
has a clock icon. Click Submit Order Form with the `Standard - Free` plan selected. Then click on the scheduler
and in the new tab it opens, click on `Create job`. You can set the schedule for how often your script will run
(I have ours set to every hour) and then in the command, type in `python update_admissions_sheet.py` and click 
`Save Job`. I think that's it, good luck!

# PREFACE: Why have I done any of this
The sheet is currently at least 3 years old, and is in pretty brutal need of repair. Some of the options I'm considering:
- A light cleaning, with some additional information pasted but keeping the main structure of the sheet the same (only using the available JS scripts/etc)
- Adding additional GS/JS code to the sheet to be able to add more information.
- Writing sheets formulae (*gasps*) that can extract more information (e.g. from the reddit.user.about.json site)
- Writing a routinely run python script which uses selenium to extract information from a site e.g. 
https://www.redditmetis.com, which gives us more powerful insights (edit: this is the one I did!)
- Doing something that isn't a sheet (*gasps*)

Ideally, by doing any (or multiple) of the above, one would not need to explore the user's reddit feed, because the e.g. redditmetis overview would be sufficient information. Of course, some would slip through the cracks, but that is true also of someone looking at the most recent ~20 posts/comments

Problems I have with the current approach:
- The way it's currently setup, I need to read the form responses on "Sheet1" before even seeing whether or not they pass the karma threshold. If they have insufficient karma, consider that a desk reject in my mind.
- I need to look at both "Sheet1" and "Helper" tabs in order to get all the information I need. Ideally, all information will be contained on one tab.
- A perusal of the user's reddit page will probably only give me a glimpse into their most recent history, which is often times just a bunch of r/hp comments to prepare for the application.
- There's also something that should be fixed about that thing where it says "TRUE" if not yet checked, "FALSE" if below the karma threshold, and "ALREADY ADDED" otherwise. Because then it says, "ALREADY ADDED" if I deny, which isn't true. it's hard, though. I don't want to hardcode people's names onto the checker.