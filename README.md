# airport_compare
OSINT investigators wish they could get access to flight records. This doesn't do that, but it does show which planes landed and took off on the same day from an airport.

It utilise API feeds from Open Sky Network and HexDB.io, and builds and merges databases to return the details on any aircraft that may have been at a location for a meeting.

Works best for smaller aiports.

![image](https://user-images.githubusercontent.com/69304112/213688746-c7d1a282-27f1-4a4a-9c5a-44b6f730070f.png)

For example, following the path of a Bombardier Global Express luxury jet belonging to Mineralogy, we see it landed at London's Biggin Hill airport from Nice on 3 November, 2022. 

![image](https://user-images.githubusercontent.com/69304112/213689931-8326bfa9-fd85-4500-8454-2864cc14c2ce.png)

This script show us that SaxonAir Cessna also arrived from Nice on the 3rd.

![image](https://user-images.githubusercontent.com/69304112/213689804-64cc197a-5bc8-43ff-a489-7dd34b177403.png)

Both departed on the 7th, giving a possible avenue of investigation.
