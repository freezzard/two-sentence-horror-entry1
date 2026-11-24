#!/usr/bin/env python3
"""Two-Sentence Horror entry for make.fun.

Writes one horror story of exactly two sentences to /output/entry.txt.

The story was chosen by a local pairwise tournament of ten candidates,
judged against the five criteria in the competition RULES.txt, most
important first: genuinely frightening in exactly two sentences; the
second sentence turns or reveals something that makes the first
sentence worse on a second read; the horror is implied rather than
explained; precise and concrete prose with every word earning its
place; original, not a familiar horror twist or a known story retold.

Winner: the basement-feeding story, 182 characters. Its second
sentence reverses the feeding ritual of the first: the narrator stops
feeding the basement, and something upstairs starts leaving dinner
for the narrator instead. The horror stays implied: nothing is named,
nothing is explained, and the reader is left to fill in what moved
upstairs and what it wants from the narrator next.

The program is deterministic: the same input always produces the same
bytes. It validates the story against the competition gate before it
writes anything: UTF-8 text, 1 to 400 characters, exactly two
sentences, not only white space.
"""

from __future__ import annotations

import os
import sys


HORROR_FIRST_SENTENCE = (
    "The seller left one instruction with the keys: "
    "feed the basement once a week, and never skip."
)

HORROR_SECOND_SENTENCE = (
    "I stopped a month ago, and something upstairs has started "
    "leaving dinner for me instead."
)

HORROR_ENTRY_TEXT = HORROR_FIRST_SENTENCE + " " + HORROR_SECOND_SENTENCE

HORROR_GATE_MIN_CHARS = 1
HORROR_GATE_MAX_CHARS = 400
HORROR_REQUIRED_SENTENCES = 2
HORROR_OUTPUT_PATH = "/output/entry.txt"
HORROR_SENTENCE_ENDERS = (".", "!", "?")
HORROR_ENTRY_BYTE_COUNT = 182


def horror_join_sentences(first_sentence: str, second_sentence: str) -> str:
    """Join the two story sentences with a single space between them."""
    trimmed_first = first_sentence.strip()
    trimmed_second = second_sentence.strip()
    joined_story = trimmed_first + " " + trimmed_second
    return joined_story


def horror_ender_closes_sentence(story_text: str, ender_index: int) -> bool:
    """Tell whether the ender at this index closes a sentence.

    An ender closes a sentence when the next character is white space
    or when the ender is the last character of the text. An ender
    buried inside a word, such as a decimal point, closes nothing.
    """
    text_length = len(story_text)
    next_index = ender_index + 1
    ender_is_last_char = next_index >= text_length
    if ender_is_last_char:
        return True
    next_char_is_space = story_text[next_index].isspace()
    return next_char_is_space


def horror_count_sentences(story_text: str) -> int:
    """Count sentences by scanning for sentence-ending punctuation.

    The scan walks the text once, character by character, and counts
    each period, exclamation mark, or question mark that closes a
    sentence. A run of enders, such as an ellipsis, counts once per
    ender that the closing rule accepts, and the story this program
    ships holds no such run, so the count matches a plain reading.
    """
    sentence_tally = 0
    text_length = len(story_text)
    char_index = 0
    while char_index < text_length:
        current_char = story_text[char_index]
        char_is_ender = current_char in HORROR_SENTENCE_ENDERS
        ender_closes = False
        if char_is_ender:
            ender_closes = horror_ender_closes_sentence(story_text, char_index)
        if ender_closes:
            sentence_tally = sentence_tally + 1
        char_index = char_index + 1
    return sentence_tally


def horror_text_has_content(story_text: str) -> bool:
    """Return True when the text holds at least one non-space character."""
    content_found = False
    for story_char in story_text:
        char_is_content = story_char.isspace() is False
        if char_is_content:
            content_found = True
            break
    return content_found


def horror_check_gate(story_text: str) -> list:
    """Check the story against the competition gate, collecting faults.

    The gate demands UTF-8 text of 1 to 400 characters, not only white
    space, telling exactly two sentences. Every fault is collected so
    the caller can report all of them at once instead of stopping at
    the first one.
    """
    gate_faults = []
    story_length = len(story_text)
    length_below_minimum = story_length < HORROR_GATE_MIN_CHARS
    if length_below_minimum:
        gate_faults.append(
            "story is empty: gate needs at least "
            + str(HORROR_GATE_MIN_CHARS)
            + " character"
        )
    length_above_maximum = story_length > HORROR_GATE_MAX_CHARS
    if length_above_maximum:
        gate_faults.append(
            "story is "
            + str(story_length)
            + " characters: gate allows at most "
            + str(HORROR_GATE_MAX_CHARS)
        )
    story_has_no_content = horror_text_has_content(story_text) is False
    if story_has_no_content:
        gate_faults.append("story is only white space")
    sentence_total = horror_count_sentences(story_text)
    sentence_total_wrong = sentence_total != HORROR_REQUIRED_SENTENCES
    if sentence_total_wrong:
        gate_faults.append(
            "story has "
            + str(sentence_total)
            + " sentences: gate needs exactly "
            + str(HORROR_REQUIRED_SENTENCES)
        )
    return gate_faults


def horror_encode_entry(story_text: str) -> bytes:
    """Encode the story as UTF-8 bytes, rejecting unencodable text."""
    encoded_story = story_text.encode("utf-8")
    return encoded_story


def horror_write_entry(story_text: str, output_path: str) -> int:
    """Validate the story, then write it to the output path.

    The parent directory is created when it does not exist yet. The
    file is written in binary mode so the bytes on disk are exactly
    the UTF-8 encoding of the story, with no newline added and no
    platform line-ending translation.
    """
    gate_faults = horror_check_gate(story_text)
    faults_present = len(gate_faults) > 0
    if faults_present:
        for gate_fault in gate_faults:
            print("gate fault: " + gate_fault, file=sys.stderr)
        return 1
    encoded_story = horror_encode_entry(story_text)
    output_directory = os.path.dirname(output_path)
    directory_missing = output_directory == ""
    if directory_missing:
        output_directory = "."
    os.makedirs(output_directory, exist_ok=True)
    with open(output_path, "wb") as entry_handle:
        entry_handle.write(encoded_story)
    print("wrote " + str(len(encoded_story)) + " bytes to " + output_path)
    return 0


def horror_main() -> int:
    """Build the entry text and write it to /output/entry.txt."""
    story_text = horror_join_sentences(
        HORROR_FIRST_SENTENCE, HORROR_SECOND_SENTENCE
    )
    exit_code = horror_write_entry(story_text, HORROR_OUTPUT_PATH)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(horror_main())
