import praw
import json
import os
from sys import exit

readme_link = "https://github.com/beyond-boreas/reddit-link-scraper"
config_failure_msg = "EXIT:  Please fill out config.json per the Configuration section of the README at " + readme_link

debug = True
# Initialize our configuration file dictionary
config = None

# Specify what the default config file looks like
default_config = {
    "client_id": "",
    "client_secret": "",
    "user_agent": "",
    "subreddits": "",
    "limit": "",
    "sort": "hot",
    "time": "all",
    "output_path": "output.txt"
}

def error(msg):
    print("ERROR: " + msg)

def warn(msg):
    print("WARN:  " + msg)

def info(msg):
    print("INFO:  " + msg)

def debug(msg):
    if(debug):
        print("DEBUG: " + msg)


def configFileExists() -> bool:
    global config
    # Check if configuration file already exists
    if(os.path.exists('config.json')):
        debug("Found config.json")
        with open('config.json', 'r') as openfile:
            config = json.load(openfile)
        
        # Check that configuration file contains all the key entries we need
        for key in default_config:
            # If the config does not have a key present in default config,
            # take the key/val pair from the default config and append it
            # then write it to the file.
            if(not key in config):
                warn("config.json exists but has no " + key + " key. Appending key and default value.")
                config[key] = default_config[key]
                with open('config.json', 'w') as outfile:
                    json.dump(config, outfile, indent=4)
                    debug("Wrote " + key + " to config.json")

    # Or create a configuration file
    else:
        with open("config.json", "w") as outfile:
            json.dump(default_config, outfile, indent=4)
            warn("Created config.json")
        return False
    return True

def validAPICredentials() -> bool:
    global config
    # Check if client secret, client id are filled out
    if(config["client_id"]=="" or config["client_secret"]=="" or config["user_agent"]==""):
        error("The client_id, client_secret, or user_agent is not filled out in config.json. These values are necessary to use the Reddit API.")
        return False
    return True

def validLimit() -> bool:
    global config
    if(config["limit"]==""):
        warn("No limit is specified. Using default 100.")
        config["limit"] = "100"
        return True
    else:
        try:
            int(config["limit"])
            return True
        except ValueError:
            error("limit in config.json must be a whole number enclosed in quotations.")
            return False


def validSort() -> bool:
    global config
    validSortValues = ["hot","controversial","top","new"]
    if(config["sort"] not in validSortValues):
        error("sort value \"" + config["sort"] + "\" is invalid. Valid values are: " + ", ".join(validSortValues))
        return False
    return True


def validTime() -> bool:
    global config
    validTimeValues = ["hour","week","month","year","all"]
    if(config["time"] not in validTimeValues):
        error("time value \"" + config["time"] + "\" is invalid. Valid values are: " + ", ".join(validTimeValues))
        return False
    return True


def validConfig() -> bool:
    if(configFileExists() and validAPICredentials() and validLimit() and validSort() and validTime()):
        debug("Configuration is valid")
        return True
    return False


# Exit code if config.json is invalid
if(not validConfig()):
    error("Invalid config.json - see previous errors for reasons why.")
    exit(config_failure_msg)





def crawl():
    debug("Beginning crawl")

    # Read and clean-up subreddits
    subreddits = None
    if(config["subreddits"]==""):
        error("No subreddits have been specified.")
        exit(config_failure_msg)
    else:
        # Read subreddits into list and remove whitespace
        subreddits = ''.join(config["subreddits"].split()).split(',')
        debug("Discovered subreddits: " + ', '.join(subreddits))



    # Read sort



    reddit = praw.Reddit(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        user_agent=config["user_agent"]
    )
    reddit.read_only = True

    for subname in subreddits:
        sub = reddit.subreddit(subname)
        for submission in sub.hot(limit=2):
            print(submission.title)
            print(submission.score)
            print(submission.id)
            print(submission.url)

crawl()