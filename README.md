# AIRPORT CROSSOVER TOOL

OSINT investigators wish they could get access to flight records. This tool doesn't do that, but it does show which planes landed and took off on the same days from an airport, which can be useful in offering potentially solutions to who was meeting whom.

It applies relational alegbra to the constructed databases built from the Open Sky Network and HexDB.io APIS, in order to return the details on all aircraft that fit the search criteria.

Naturally, it works best for smaller aiports, due to the more precise traffic. It's also most useful when planes are registered to a specific non-aviation private company or a person.

![image](https://user-images.githubusercontent.com/69304112/213823076-674849e2-9df0-4811-8af6-ef06ebd97e37.png)


![image](https://user-images.githubusercontent.com/69304112/213688746-c7d1a282-27f1-4a4a-9c5a-44b6f730070f.png)

For example, following the path of a Bombardier Global Express luxury jet belonging to Mineralogy, we see it landed at London's Biggin Hill airport from Nice on 3 November, 2022. 

This script show us that SaxonAir Cessna also arrived from Nice on the 3rd, which can be confirmed by looking at the sitry of both planes in ADS-B Exchange.

![image](https://user-images.githubusercontent.com/69304112/213822713-90758d1d-e836-4b02-95f7-63c44c2dafed.png)

Both departed on the 7th. 

The coincidences may be nothing, but this OSINT tool does give another possible avenue of further investigation in an area where open-source intelligence is scarce.
