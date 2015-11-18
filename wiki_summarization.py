# Import Dependencies

# General
import pickle
import pandas as pd
import re

# NLP
from nltk.tokenize import LineTokenizer, sent_tokenize
from urllib import parse
from textblob import TextBlob


# Pickling functions
def load_pickle(filename):
    """
    In:
        filename = name of the pickle file you want to open (e.g
            "my_pickle.pkl")

    Out:
        Opens and returns the content of the picklefile to a variable of your
            choice
    """
    with open(filename, "rb") as picklefile:
        return pickle.load(picklefile)


def get_sentences(article):
    """
    In:
        article = Cleaned wikipedia article text

    Out:
        sentences = List of sentences in wikipedia article
    """
    lines = LineTokenizer(blanklines='discard').tokenize(
        article.replace("<br>", "\n"))
    sentences_by_lines = [sent_tokenize(line) for line in lines]
    sentences = [sentence for line in sentences_by_lines for sentence in line]

    return sentences


def merge_subsections_with_parent(sections_needing_some_merging,
                                  section_level="=="):
    """
    In:
        sections_needing_some_merging = List of sections including subsections
            not grouped with parent section
        section_level = Level of parent section "==" --> h1, "===" --> h2, etc.

    Out:
        merged_sections = List of sections with subsections grouped with parent
    """
    sections = [section_level + section if i != 0 else section for i, section
                in enumerate(sections_needing_some_merging)]
    merged_sections = []
    for section in sections:
        if section.startswith(section_level + "="):  # If child section:
            merged_sections[-1] += "<br><br>" + section
        else:
            merged_sections.append(section)

    return merged_sections


def get_subsections(sections):
    """
    In:
        sections = List of sections with subsections grouped with parent

    Out:
        grouped_subsections = List of sections with nested list of subsections
    """
    grouped_subsections = []
    for section in sections:
        subsections = section.split("<br><br>===")
        subsections = merge_subsections_with_parent(subsections, "===")
        grouped_subsections.append(list(subsections))

    return grouped_subsections


def get_paragraphs(sections):
    """
    In:
        sections = List of sections with nested list of subsections

    Out:
        grouped_paragraphs = List of sections with nested list of subsections
            with nested list of paragraphs
    """
    grouped_paragraphs = []
    for section in sections:

        subsection_paragraphs = []
        for subsection in section:
            paragraphs = subsection.split("<br><br>")
            subsection_paragraphs.append(list(paragraphs))

        grouped_paragraphs.append(subsection_paragraphs)

    return grouped_paragraphs


def get_paragraph_sentences(sections):
    """
    In:
        sections = List of sections with nested list of with nested list of
            paragraphs

    Out:
        grouped_sentences = List of sections with nested list of subsections
            with nested list of paragraphs with nested sentences
    """
    grouped_sentences = []
    for section in sections:

        subsection_sentences = []
        for subsection in section:

            paragraph_sentences = []
            for paragraph in subsection:
                sentences = sent_tokenize(paragraph)
                paragraph_sentences.append(list(sentences))

            subsection_sentences.append(paragraph_sentences)

        grouped_sentences.append(subsection_sentences)

    return grouped_sentences


def get_sentences_with_structure(article):
    """
    In:
        article = Cleaned wikipedia article text

    Out:
        sentences_with_structure = List of sections with nested list of
            subsections with nested list of paragraphs with nested sentences
    """
    sections = article.split("<br><br>==")
    sections = merge_subsections_with_parent(sections, "==")
    sections_with_subsections = get_subsections(sections)
    sections_with_subsections_paragraphs = get_paragraphs(
        sections_with_subsections)
    sentences_with_structure = get_paragraph_sentences(
        sections_with_subsections_paragraphs)

    return sentences_with_structure


def generate_sentence_location_data(sentences_with_structure):
    """
    In:
        sentences_with_structure = List of sections with nested list of
            subsections with nested list of paragraphs with nested sentences

    Out:
        location_data = List of lists of sentences and their location data.
            Data inludes:
                - Sentence
                - Cumulative section #
                - Cumulative subsection #
                - Cumulative paragraph #
                - Cumulative sentence #
                - Cumulative section percentile
                - Cumulative section percentile
                - Cumulative paragraph percentile
                - Cumulative sentence percentile
                - Subsection # in section
                - Paragraph # in subsection
                - Sentence # in paragraph
                - Subsection in section percentile
                - Paragraph in subsection percentile
                - Sentence in paragraph percentile
                - Paragraph # in section
                - Paragraph in section percentile
                - Sentence # in subsection
                - Sentence in subsection percentile
                - Sentence # in section
                - Sentence in section percentile
                - Total # of sentences
                - Sentence length
    """
    location_data = []

    cum_s = 0  # Cumulative section
    cum_ss = 0  # Cumulative section
    cum_p = 0  # Cumulative paragraph
    cum_sent = 0  # Cumulative sentence

    cum_s_sent = 0  # Cumulative sentence in section
    cum_ss_sent = 0  # Cumulative sentence in subsection
    cum_p_sent = 0  # Cumulative sentence in paragraph

    cum_s_p = 0  # Cumulative paragraph in section
    cum_ss_p = 0  # Cumulative paragraph in subsection

    cum_s_ss = 0  # Cumulative subsection in section

    # Total sections
    total_s = len(sentences_with_structure)
    # Total subsections
    total_ss = sum([len(section) for section in sentences_with_structure])
    # Total paragraphs
    total_p = sum([len(subsection) for section in sentences_with_structure
                   for subsection in section])
    # Total sentences
    total_sent = sum([len(paragraph) for section in sentences_with_structure
                      for subsection in section for paragraph in subsection])

    for s, section in enumerate(sentences_with_structure):
        # Total subsections in section
        s_total_ss = len(section)
        # Total paragraphs in section
        s_total_p = sum([len(subsection) for subsection in section])
        # Total sentences in section
        s_total_sent = sum([len(paragraph) for subsection in section
                            for paragraph in subsection])

        for ss, subsection in enumerate(section):
            # Total paragraphs in subsection
            ss_total_p = len(subsection)
            # Total sentences in subsection
            ss_total_sent = sum([len(paragraph) for paragraph in subsection])

            for p, paragraph in enumerate(subsection):
                # Total sentences in paragraph
                p_total_sent = len(paragraph)

                for sent, sentence in enumerate(paragraph):
                    sent_len = len(sentence)  # Sentence length
                    """See docstring above for a list of data definitions
                    in order"""
                    location_data.append(
                        [sentence,
                            cum_s, cum_ss, cum_p, cum_sent,
                            cum_s/total_s, cum_ss/total_ss, cum_p/total_p,
                            cum_sent/total_sent,

                            ss, p, sent,
                            ss/s_total_ss, p/ss_total_p, sent/p_total_sent,

                            (cum_p - cum_s_p), (cum_p - cum_s_p)/s_total_p,
                            (cum_sent - cum_ss_sent),
                            (cum_sent - cum_ss_sent)/ss_total_sent,

                            (cum_sent - cum_s_sent),
                            (cum_sent - cum_s_sent)/s_total_sent,

                            total_sent,
                            sent_len])

                    cum_sent += 1

                cum_p_sent = cum_sent
                cum_p += 1

            cum_ss_p = cum_p
            cum_ss_sent = cum_sent
            cum_ss += 1

        cum_s_ss = cum_ss
        cum_s_p = cum_p
        cum_s_sent = cum_sent
        cum_s += 1

    return location_data


def get_topic_mentions(sentence, topic):
    """
    In:
        sentence = Cleaned sentence from wikipedia article
        topic = Cleaned topic of wikipedia article

    Out:
        topic_mentions = # of times topic was mentioned in the sentence
            (normalized for number of words in the topic)
    """
    topic_words = TextBlob(topic).words.lower()
    sent_text = TextBlob(sentence)

    topic_mentions = 0
    for word in topic_words:
        topic_mentions += sent_text.word_counts[word]

    try:
        topic_mentions = topic_mentions/len(topic_words)
    except:
        topic_mentions = 0

    return topic_mentions


def get_sentence_type_data(sentence):
    """
    In:
        sentence = Cleaned sentence from wikipedia article

    Out:
        subheading = Sentence is a subheading (Yes = 1, No = 0)
        heading = Sentence is a heading (Yes = 1, No = 0)
        table = Sentence is part of a table (Yes = 1, No = 0)
        bullet = Sentence is a bullet (Yes = 1, No = 0)
        numbered_bullet = Sentence is a numbered bullet (Yes = 1, No = 0)
    """
    subheading = 0
    heading = 0
    table = 0
    bullet = 0
    numbered_bullet = 0

    if sentence.startswith("==="):
        subheading = 1
    elif sentence.startswith("=="):
        heading = 1
    elif sentence.startswith("TABLE:") or sentence.startswith("||"):
        table = 1
    elif sentence.startswith(":*") or sentence.startswith("*"):
        bullet = 1
    elif sentence.startswith("#"):
        numbered_bullet = 1

    return subheading, heading, table, bullet, numbered_bullet


def get_sentiment_data(sentence):
    """
    In:
        sentence = Cleaned sentence from wikipedia article

    Out:
        polarity = Postive / negative sentiment of the sentence
        subjectivity = Objectivity / subjectivity sentiment of the sentence
    """
    sentiment = TextBlob(sentence).sentiment
    polarity, subjectivity = tuple(sentiment)
    return polarity, subjectivity


def convert_article_to_data(article, topic, return_dataframe=True):
    """
    In:
        article = Cleaned wikipedia article
        topic = Topic of wikipedia article
        return_dataframe = Whether or not to return a Pandas DataFrame;
            if False, returns a list of lists instead

    Out:
        Pandas DataFrame of sentence data for the wikipedia article
            OR
        List of lists of sentence data for the wikipedia article
    """
    sentences = get_sentences(article)
    topic = parse.unquote(topic.replace("_", " "))

    sentences_with_structure = get_sentences_with_structure(article)
    sentence_location_data = generate_sentence_location_data(
        sentences_with_structure)

    article_data_list = []
    for sentence, location_data \
            in zip(sentences, sentence_location_data):

        sentence_type_data = get_sentence_type_data(sentence)
        topic_mentions = get_topic_mentions(sentence, topic)
        sentiment_data = get_sentiment_data(sentence)

        data_row = [sentence] + location_data[1:] + list(sentence_type_data) +\
            [topic_mentions] + list(sentiment_data)
        article_data_list.append(data_row)

    if return_dataframe:
        column_names = ["sentence", "cum_sect", "cum_subsect", "cum_para",
                        "cum_sent", "cum_sect_%", "cum_subsect_%",
                        "cum_para_%", "cum_sent_%", "subsect_in_sect",
                        "para_in_subsect", "sent_in_para", "subsect_in_sect_%",
                        "para_in_subsect_%", "sent_in_para_%",
                        "para_in_section", "para_in_section_%",
                        "sent_in_subsect", "sent_in_subsect_%", "sent_in_sect",
                        "sent_in_sect_%", "total_sents", "sent_len",
                        "subheading", "heading", "table", "bullet",
                        "numbered_bullet", "topic_mentions", "polarity",
                        "subjectivity"]
        return pd.DataFrame(article_data_list, columns=column_names)
    else:
        return article_data_list


"""Load Summarization Model"""
model_pack = load_pickle("prediction_model.pkl")
model = model_pack["model"]


def build_summary(sentences, paragraph_numbers, included_predictions):
    """
    In:
        sentences = List of sentences in article to summarize
        paragraph_numbers = List of paragraph numbers of the sentences in
            article to summarize
        included_predictions = List of 1 (Yes), 0 (No) predictions for whether
            or not each sentence is included in the summary

    Out:
        summary = Summary string for article
    """
    summary_list = [(sentence, paragraph_number)
                    for sentence, paragraph_number, included
                    in zip(sentences, paragraph_numbers, included_predictions)
                    if included == 1]

    summary = ""
    last_paragraph_number = 0
    i = 0
    for sentence, paragraph_number in summary_list:
        if i == 0:
            summary += sentence
            i += 1
        elif paragraph_number > last_paragraph_number:
            summary += "<br><br>" + sentence
        else:
            summary += " " + sentence
        last_paragraph_number = paragraph_number

    return summary


def add_html_tages_to_summary(summary):
    """
    In:
        summary = Summary string for article with Wiki markdown

    Out:
        summary = Summary string for article with Wiki markdown replaced by
            HTML tags
    """
    # Bold tags
    while re.search(r"\'\'\'.*?\'\'\'", summary):
        instance = re.search(r"\'\'\'.*?\'\'\'", summary).group()
        summary = summary.replace(instance, "<b>" + instance[3:-3] + "</b>")

    # Italic tags
    while re.search(r"\'\'.*?\'\'", summary):
        instance = re.search(r"\'\'.*?\'\'", summary).group()
        summary = summary.replace(instance, "<i>" + instance[2:-2] + "</i>")

    # Italic heading tags
    while re.search(r"\=\=\=\=.*?\=\=\=\=", summary):
        instance = re.search(r"\=\=\=\=.*?\=\=\=\=", summary).group()
        summary = summary.replace(instance, "<i>" + instance[4:-4] + "</i>")

    # Bold and italic heading tags
    while re.search(r"\=\=\=.*?\=\=\=", summary):
        instance = re.search(r"\=\=\=.*?\=\=\=", summary).group()
        summary = summary.replace(instance, "<b><i>" + instance[3:-3] +
                                  "</i></b>")

    # Bold heading tags
    while re.search(r"\=\=.*?\=\=", summary):
        instance = re.search(r"\=\=.*?\=\=", summary).group()
        summary = summary.replace(instance, "<b>" + instance[2:-2] +
                                  "</b>")

    # Clean up any extra spaces
    summary = summary.replace("<b> ", "<b>")
    summary = summary.replace("<i> ", "<i>")
    summary = summary.replace(" </b>", "</b>")
    summary = summary.replace(" </i>", "</i>")

    # Unordered list tags
    while re.search(r"\*.*?(?:\<br\>\<br\>|$)", summary):
        instance = re.search(r"\*.*?(?:\<br\>\<br\>|$)", summary).group()
        summary = summary.replace(instance, "<ul><li>" + instance[1:] +
                                  "</li></ul>")

    # Ordered list tags
    while re.search(r"\#.*?(?:\<br\>\<br\>|$)", summary):
        instance = re.search(r"\#.*?(?:\<br\>\<br\>|$)", summary).group()
        summary = summary.replace(instance, "<ol><li>" + instance[1:] +
                                  "</li></ol>")

    # Clean up extra unordered list tags
    if re.search(r"\<ul\>.*\<\/ul\>", summary):
        instance = re.search(r"\<ul\>.*\<\/ul\>", summary).group()
        new_instance = instance[4:-5].replace("<ul>", "")
        new_instance = new_instance.replace("</ul>", "")
        new_instance = new_instance.replace("<br>", "")
        summary = summary.replace(instance, "<ul>" + new_instance + "</ul>")

    # Clean up extra ordered list tags
    if re.search(r"\<ol\>.*\<\/ol\>", summary):
        instance = re.search(r"\<ol\>.*\<\/ol\>", summary).group()
        new_instance = instance[4:-5].replace("<ol>", "")
        new_instance = new_instance.replace("</ol>", "")
        new_instance = new_instance.replace("<br>", "")
        summary = summary.replace(instance, "<ol>" + new_instance + "</ol>")

    return summary


def summarize_article(article, topic):
    """
    In:
        article = Cleaned wikipedia article to summarize
        topic = Topic of wikipedia article to summarize

    Out:
        summary = Summary string for article
    """
    df = convert_article_to_data(article, topic)

    sentences = df["sentence"]
    paragraph_numbers = df["cum_para"]

    X = df.drop(["sentence"], axis=1)

    predictions = model.predict(X)

    summary = build_summary(sentences, paragraph_numbers, predictions)
    summary = add_html_tages_to_summary(summary)

    return summary
