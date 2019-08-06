# Trackerian
## Use the Command-Line to Keep Track of Your Time
Easily keep track of your daily activities and see summarised data of how your day/week/overall time is broken down. Summaries display the percentage of tracked time each activity accounts by both the name of the activity and the tags you associated with it.

### INSTALLATION
Installation is as simple as cloning the repository, or at the very least downloading the trackerian file, to your computer.

    git clone https://github.com/IFinners/trackerian.git

### USAGE INSTRUCTIONS
To use the program navigate to the folder you downloaded the repository/file to and run it using Python 3


**Tracking, Tagging and Finishing Activities**

To start tracking an activity simply use the `-b` `--begin` argument:

    python3 trackerian.py --begin Write Readme

One word tags can be added to the current activity either alongside the `--begin` argument with the `-t` `--tag` argument:

    python3 trackerian.py --begin Write Readme --tag Documentation Productive

Or, if passed alone, to the most recent activity, whether it is still being tracked or not:

    python3 trackerian.py -t Documentation Productive

To finish tracking an activity either begin tracking a new activity or use the `-f` `--finish` argument:

    python3 trackerian.py --finish

This activity is now safely completed with its **_name_**, **_tags_**, **_start time_**, **_end time_** and **_duration_** calculated and ready to be used for summaries.

**Activity Summaries and Lists**

Summaries are invoked with the `-s` `--summary` arguments. Three values can be passed to `--summary`:
**_day_** will summarise activities tracked during the current day (since 04:00) and is the default value so will be invoked by passing `--summary` with no additional argument.
**_week_** will summaries activities tracked within the last seven days.
**_all_** will summaries all activities that you have tracked while using Trackerian.

For example, to get a summary of your activities for the last seven days:

    python3 trackerian.py --summary week

Your tracked activities can be displayed in an enumerated list that displays their start and end times, name, duration and associated tags with the `-l` `--list` argument. This argument takes the same **_day_**/**_week_**/**_all_** optional arguments as `--summary` and once again defaults to the equivalent of passing **_day_**:
    
    python3 trackerian.py --list week

From this list you can tell what, if anything, is currently being tracked but this information can also be found more specifically by using the `-c` `--current` argument:

    python3 trackerian.py --current

**Editing and Removing Activities**

Activities with typos in their names, missing tags or inaccurate times can invalidate the summaries and that is why you can edit all of the pertinent information about any activity. This is done through the `-e` `--edit` arguments and works as follows.

    python3 trackerian.py --edit [activity number] [information category] [new value(s)]
    
**_activity number_** is the number displayed on the left hand side of the activity you wish to edit when using the `--list` argument. 

**_information category_** is the type of information you want to edit. There are four categories:
* name - The name of the activity.
* start - The time the activity was started. 
* end - The time the activity was ended.
* tag - The single-word tag(s) associated with the activity. 

**_new value(s)_** are the new value(s) you want to REPLACE the current value(s) that activity has under that information category. A couple of things to note:
* start and end values are to be formatted HH:MM:SS. The date is taken from the current value and currently cannot be changed.
* tag DOES NOT ADD to the current list of tags for that activity but REPLACES it. To add a tag you will have to rewrite the entire space-separated list with your new tag included.

For example to change the 'Write Readme' activity name you would:

    python3 trackerian.py --edit 0 name Writing Readme

If for any reason you need to remove an activity from your history, including the one you are currently tracking, you can use the `-r` `--remove` argument:

    python3 trackerian.py --remove [activity number]

**Further Help**

With the information above, you should have no trouble using Trackerian and making the most out of your time but feel free to raise any issues on the repository page. A condensed help message for all of these arguments can be invoked by passing the `-h` `--help` argument or running the program with no arguments given.
