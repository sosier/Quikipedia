# Import Dependencies
import flask
from urllib.request import urlopen
import re

# Most of the "magic" happens in these two files:
from wikipedia_page_cleaning import clean_wiki_page
from wiki_summarization import summarize_article

# ---------- URLS AND WEB PAGES -------------#

# Initialize the app
app = flask.Flask(__name__)


# Homepage
@app.route("/")
def homepage():
    """
    Serve homepage: summarize.html
    """
    with open("summarize.html", "r") as homepage:
        return homepage.read()


@app.route("/summarize", methods=["POST"])
def summarize():
    """
    When A POST request with json data is made to this url,
    Read the topic from the json, pull and summarize the wikipedia article,
    then return back to the web browser
    """
    data = flask.request.json
    topic = data["topic"]

    # Format topic for API / url
    topic = topic.replace(" ", "_")
    topic = topic.lower()

    try:
        # Make initial API call
        raw_english_text = urlopen("https://en.wikipedia.org/w/index.php?"
                                   "action=raw&title="+topic)
        raw_english_text = raw_english_text.read().decode('UTF-8')

        # Call the API again if redirect is required
        if raw_english_text[:9] == "#REDIRECT" or \
                raw_english_text[:9] == "#redirect":
            topic = re.search(r"\[\[.*\]\]", raw_english_text).group()[2:-2]
            topic = topic.replace(" ", "_")
            raw_english_text = urlopen("https://en.wikipedia.org/w/index.php?"
                                       "action=raw&title="+topic)
            raw_english_text = raw_english_text.read().decode('UTF-8')

        # Clean and summarize the raw text recieved from the API
        raw_english_text = clean_wiki_page(raw_english_text)
        summary_text = summarize_article(raw_english_text, topic)

    except:
        # Return error message if the user requests a article which doesn't
        # exist on Wikipedia
        raw_english_text = "Looks like there is no Wikipedia page for" + \
            " \"%s\"!<br>Try another topic." % topic.replace("_", " ")
        summary_text = raw_english_text

    # CODE TO DO THE SAME USING SIMPLE WIKIPEDIA INSTEAD, KEEPING FOR POTENTIAL
    # FUTURE USE:
    """
    try:
        raw_simple_text = urlopen("https://simple.wikipedia.org/w/index.php?"
                                  "action=raw&title="+topic)
        raw_simple_text = raw_simple_text.read().decode('UTF-8')

        if raw_simple_text[:9] == "#REDIRECT" or \
                raw_simple_text[:9] == "#redirect":
            topic = re.search(r"\[\[.*\]\]", raw_simple_text).group()[2:-2]
            topic = topic.replace(" ", "_")
            raw_simple_text = urlopen("https://simple.wikipedia.org/w/index."
                                      "php?action=raw&title="+topic)
            raw_simple_text = raw_simple_text.read().decode('UTF-8')

        raw_simple_text = clean_wiki_page(raw_simple_text)
        summary_text = summarize_article(raw_simple_text, topic)
    except:
        raw_simple_text = "Looks like there is no Simple Wikipedia page for" +\
            " \"%s\"!<br>Try another topic." % topic.replace("_", " ")
        summary_text = raw_simple_text
    """

    # Put the result in a dictionary and send back as json
    results = {
        "summary": summary_text,
        "wiki_topic": topic,
        # "english": raw_english_text,
        # "simple": raw_simple_text,
        }
    return flask.jsonify(results)

# --------- RUN WEB APP SERVER ------------#

# For local development:
app.run(debug=True)

# For public web serving:
# app.run(host='0.0.0.0', port=80)
