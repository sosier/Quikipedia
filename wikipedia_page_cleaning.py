import re


# Main function
def clean_wiki_page(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        text = Cleaned wikipedia article text
    """
    text = remove_double_curly(text)
    text = parse_double_square(text)
    text = clean_wiki_tables(text)
    text = newline_to_br(text)
    text = remove_ref_links(text)
    text = remove_super_script(text)
    text = remove_reference_and_more_sections(text)
    text = remove_gallery(text)
    text = remove_html_comments(text)
    text = remove_divs(text)
    text = regularize_newline_spacing(text)

    return text


# Sub-functions
def remove_double_curly(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        new_text = Cleaned wikipedia article text with all instances of "{{",
            "}}", and their and contents removed
    """
    new_text = ""
    last = ""
    curlies_opened = 0

    for i, char in enumerate(text):
        if last == "{" and char == "{":
            curlies_opened += 1
        elif last == "}" and char == "}" and curlies_opened > 0:
            curlies_opened -= 1
        elif curlies_opened == 0:
            if char == "{" and text[i+1] == "{":
                pass
            else:
                new_text += char

        last = char

    return new_text


def parse_double_square(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        new_text = Cleaned wikipedia article text with all instances of "[[",
            "]]", and parsing their content to keep only desired word(s)
    """
    new_text = ""
    last = ""
    squares_opened = 0
    square_contents = ""

    for i, char in enumerate(text):
        if last == "[" and char == "[":
            squares_opened += 1
        elif last == "]" and char == "]" and squares_opened > 0:
            squares_opened -= 1
            if squares_opened == 0:
                if square_contents[:5] == "File:" or \
                   square_contents[:5] == "file:" or \
                   square_contents[:6] == "Image:" or \
                   square_contents[:6] == "image:" or \
                   square_contents[:9] == "Category:" or \
                   square_contents[:9] == "category:":
                    square_contents = ""
                else:
                    square_contents = square_contents.split("|")[-1]
                    new_text += square_contents[:-1]
                    square_contents = ""
        elif squares_opened == 0:
            if char == "[" and text[i+1] == "[":
                pass
            else:
                new_text += char
        else:
            square_contents += char

        last = char

    # Clean up "floating" / leftover square brackets (from instances of "]]]]")
    new_text = new_text.replace("\n]", "\n")

    return new_text


def clean_wiki_tables(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        new_text = Wikipedia article text with tables reformatted to have a
            consistent format;
            Note: tables NOT removed
    """
    new_text = ""
    last = ""
    tables_opened = 0
    table_contents = ""

    for i, char in enumerate(text):
        if last == "{" and char == "|":
            tables_opened += 1
        elif last == "|" and char == "}" and tables_opened > 0:
            tables_opened -= 1
            if tables_opened == 0:
                table_contents = table_contents.split("\n")[1:]
                table_contents = "\n".join(table_contents)
                table_contents = table_contents.replace("\n", "")
                table_contents = re.sub(r"style.*?\|", "|", table_contents)
                table_contents = table_contents.replace("<br/>", " ")
                table_contents = table_contents.replace("<br>", " ")
                table_contents = table_contents.replace("!!", "||")
                table_contents = table_contents.replace("! ", "")
                table_contents = table_contents.replace("|-|", "||\n||")
                table_contents = table_contents.replace("|-", "||")
                table_contents = table_contents.replace("|- |", "||\n||")
                table_contents = table_contents.replace("|+ |", "||")
                table_contents = table_contents.replace(" |", "\n|")
                table_contents = table_contents.replace("|", "||")
                table_contents = table_contents.replace("\n", "")
                table_contents = table_contents.replace("||||||||", "||\n||")
                table_contents = table_contents.replace("||||||", "||\n||")
                table_contents = table_contents.replace("||||", "||")
                table_contents = table_contents.replace("|||", "||")
                new_text += "TABLE:\n" + table_contents + "\n"
                table_contents = ""
        elif tables_opened == 0:
            if char == "{" and text[i+1] == "|":
                pass
            else:
                new_text += char
        else:
            table_contents += char

        last = char

    return new_text


def remove_reference_and_more_sections(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        text = Wikipedia article text with reference, citations, notes, etc.
            sections removed
    """
    sections_to_remove = [
        "== External links",
        "==External links",
        "== Works cited",
        "==Works cited",
        "=== Citations",
        "===Citations",
        "=== Commentary notes",
        "===Commentary notes",
        "== Notes",
        "==Notes",
        "== See also",
        "==See also",
        "== References",
        "==References",
        "== Related pages",
        "==Related pages",
        "== Other websites",
        "==Other websites",
        "== In art",
        "==In art",
        "=== Bibliography",
        "===Bibliography",
        "== Further reading",
        "==Further reading"
    ]

    section_indices = [text.rfind(section) for section in sections_to_remove]
    section_indices = [i for i in section_indices if i >= 0]

    if section_indices:
        text = text[:min(section_indices)]

    return text


def newline_to_br(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        text = Wikipedia article text with newlines ("\n") changed to break
            tags ("<br>")
    """
    text = text.replace("\n", "<br>")
    return text


def remove_ref_links(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        text = Wikipedia article text with ref tags ("<ref>...</ref>") removed
    """
    text = re.sub(r"\<ref.*?\<\/ref\>", "", text)
    text = re.sub(r"\<ref.*?\/\>", "", text)
    return text


def remove_super_script(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        text = Wikipedia article text with sup tags ("<sup>...</sup>") removed
    """
    return re.sub(r"\<sup.*?\<\/sup\>", "", text)


def remove_gallery(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        text = Wikipedia article text with gallery tags ("<gallery>...
            </gallery>") removed
    """
    return re.sub(r"\<gallery.*?\<\/gallery\>", "", text)


def remove_html_comments(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        text = Wikipedia article text with html comments ("<!--...-->") removed
    """
    return re.sub(r"\<\!\-\-.*?\-\-\>", "", text)


def remove_divs(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        text = Wikipedia article text with div tags ("<div>...</div>") removed
    """
    return re.sub(r"\<div.*?\<\/div\>", "", text)


def regularize_newline_spacing(text):
    """
    In:
        text = Raw wikipedia article text

    Out:
        text = Wikipedia article text with paragraphs spaced evenly with 2 line
            breaks ("<br><br>")
    """
    text = text.strip()
    lines = text.split("<br>")
    lines = [line for line in lines if line.strip() != ""]
    text = "<br><br>".join(lines)

    return text
