import re


def split_sentences(data: str):
    """Split string into sentences"""
    # Split by ". "
    sentences = re.split(r"(?<=\.) ", data)
    sentences_with_space = [
        sentence + (" " if i < len(sentences) - 1 else "")
        for i, sentence in enumerate(sentences)
    ]
    # Split by \n
    final_result: list[str] = []
    for sentence in sentences_with_space:
        split_by_newline = sentence.split("\n")
        for i, part in enumerate(split_by_newline):
            needs_newline = "\n" in sentence and i < len(split_by_newline) - 1
            part = part + "\n" if needs_newline else part
            final_result.append(part)

    return final_result
