# Quikipedia

###Data:  
 - [Wikipedia](https://en.wikipedia.org)  
 - [Simple Wikipedia](https://simple.wikipedia.org)  

###Technologies:  
 - Python  
   - BeautifulSoup  
   - Pandas  
   - NLTK  
   - TextBlob
   - FuzzyWuzzy
   - Flask
   - RegEx
   - scikit-learn
 - HTML
 - CSS
 - Javascript
   - JQuery  
   - AJAX  
 - UNIX  
 - Github  

###Methodolgy:  
 1. Scrape Simple Wikipedia article index (list) pages to get the links to all individual Simple Wikipedia pages  
 2. Scrape all individual Simple Wiki pages to get the links to their respective Full English Wiki pages  
 3. Using the scraped links, pull the raw text of all Simple Wiki articles and their respective Full English Wiki articles using the Wikipedia API
 4. Clean the text of all the Wiki articles pulled and split into sentences  
 5. For each sentence in each Simple Wiki article, find closet sentence(s) from its respective Full English article and flag these sentences as "kept"; do not flag all others. (We are saying these sentences are important to keep in a summary of the Full English article.)  
 6. Convert each Full English article sentence into a data vector with the following features:  
  - Location in article (e.g. sentence #, paragraph #, section #, sentence # in paragraph, etc.)  
  - Number of sentences in article  
  - Length of sentence  
  - Flags if sentence is a heading, subheading, bullet point, part of a table, etc.  
  - Number of times article topic is mentioned in the sentence  
  - Sentence sentiment  
  - AND MOST IMPORTANTLY: the "Kept" / NOT flag
 7. Fit a random forrest model to the sentence data vectors  
 8. Save the model for future use in the Quikipedia app  
 9. Collect user topic input in the Quikipedia app (any topic that has a Wikipedia article, regardless of if it has a Simple English article or not)  
 10. Pull and clean Full English Wikipedia article for user requested topic  
 11. Convert sentences from user requested article into data vectors  
 12. Feed these sentence data vectors into the pre-created random forrest model to flag sentences to keep in the summary  
 13. Finally, recombine these "kept" sentences and display article summary for the user  
