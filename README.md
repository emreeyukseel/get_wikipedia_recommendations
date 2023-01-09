# Get Wikipedia Recommendations

Welcome to the Get Wikipedia Recommendations project! This is a system that uses Wikidata ontologies to provide new topic recommendations for two Wikipedia pages that you are interested in through Knowledge Graphs.

# Installation

To install the required libraries, follow these steps:

1) Make sure you have Python and pip installed on your system. If you don't have them already, you can download Python from the official website (https://www.python.org/) and install it. pip is usually installed along with Python.
2) Open a terminal window and navigate to the root directory of the project (where the requirement.txt file is located).
3) Run the following command:

   ``` pip install -r requirements.txt" ```
   
# Getting Recommendation
To get recommendations and knowledge graph for both input, run the following command:
  ``` python main.py URL1 URL2 LIMIT ```
  
  Replace URL1 and URL2 with the Wikipedia URLs of the pages you want recommendations for, and replace LIMIT with the number of iterations you want the code to run for. The greater the value, the more recommendations will be generated, but the runtime will also be longer. Here is the example for input.
  
  The example related to racism and Black Lives Matter is as follows:
  
    ``` python main.py 'https://en.wikipedia.org/wiki/Racism' 'https://en.wikipedia.org/wiki/Black_Lives_Matter' 30 ```
  
  
  You can find the knowledge graph output as png file in *output_folder* 
