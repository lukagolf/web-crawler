# Web Crawler

## High Level Overview
The heart of the operation lies in the `run()` method. This method initializes the socket using `init_socket()`. I then log into Fakebook through the `login()` method, using credentials supplied as command line arguments. Once successfully logged in, the crawling starts with the `crawl()` method, which subsequently invokes the `crawl_page()` for each page. As I crawl, I navigate through the `frontier` list of the class, searching for any pages containing a secret flag. I also append to the `frontier` any new undiscovered pages linked from the current page.

In terms of extracting specific information from the HTTP header and page HTML, I considered a variety of (legal) libraries for parsing purposes. However, I opted for regular expressions (regex) via the `re` library. I found it straightforward, especially since I was already familiar with regex.

I made a conscious effort to modularize functionalities. Certain processes, like sending a GET, were recurrent and lengthy, prompting me to design dedicated functions for these actions. The entire logging functionality was encapsulated in the `login()` method. This made it versatile; whenever I reconsidered where to implement the login sequence, I could easily integrate the `login()` function. Breaking down each segment of this project into distinct functions allowed me to maintain a clear structure and focus throughout development.

## Challenges Faced
I encountered several challenges during the development. One primary concern was selecting the most appropriate library to interpret HTML and HTTP headers. I pondered over using the recommended libraries from the project guide, but my unfamiliarity with them pushed me towards a more known territory: regex. Naturally, using regex introduced its own set of challenges, like grasping its sometimes perplexing syntax or processing the results with string manipulation techniques.

Another hiccup was dealing with timeouts. It was initially puzzling, as I misconstrued the connection termination as a parsing issue. It wasn’t long before I discerned the need to reinitialize the socket connection.

Lastly, the crawler's speed became a concern. Given that performance wasn’t a graded aspect, I sidestepped multithreading to emphasize the crawler's accuracy. However, this rendered the crawler relatively slow, making it challenging to ascertain if it was inactive or simply processing slowly. I managed to navigate this challenge by implementing console print statements at different stages, elaborated further in "Testing".

## Testing
Testing the crawler relied primarily on print statements and live runs on Fakebook. Lacking local test cases, my only viable testing method was executing the crawler on Fakebook directly. I made it display various progress indicators during its operation, like its current page, flags found, the current frontier size, and the count of processed pages. These indicators proved invaluable, revealing previously overlooked profile edge cases. I was assured of the crawler's effectiveness once it consistently detected 5 secret flags for every member of my project team.