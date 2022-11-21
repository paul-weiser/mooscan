# mooscan - an open source moodle scraper
mooscan is a small CLI script that lists all of your active Moodle tests, assignments and workshops including their status.
It simplifies keeping track of everything that you still need to do.

## Aquiring a wstoken
To use this script, you need to create a wstoken. This is necessary to access the Moodle API. One option is to intercept the traffic that the Moodle mobile app sends and receives with a tool such as [mitmproxy](https://github.com/mitmproxy/mitmproxy). Another alternative is to follow [these instructions in the Moodle Docs](https://docs.moodle.org/dev/Creating_a_web_service_client) in the section "How to get a user token".

## Aquiring your userid
To aquire your userid simply log in to Moodle using a webbrowser and navigate to your profile page (at the top right of the screen). Then your id will show up as an URL argument for you to copy.
