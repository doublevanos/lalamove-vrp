How to run:
	This is deployed to heroku at: https://thawing-wave-40137.herokuapp.com.  To use it, point your browser to index.html in the lalamove-client package.


Address generation:
	So to generate the address, I wrote a script 'dumpaddresses.py' where using yelp api, I grabeed a couple hundred business addresses and saved it into a flatfile.  When the app starts, it will randomly index into the list for an address.


Known issues:
	- I'm aware of an intermittent issue where googlemaps api doesn't return properly and will cause a 500 error.  resubmitting the request will fix it.  I'm fully aware that it's not optimal, but due to the intermittent nature, it was hard to chase down.  Obviously wouldn't leave it as is in a user facing app.
