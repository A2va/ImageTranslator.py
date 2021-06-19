from typing import TypedDict, List
import numpy as np


# Dict type to represent a word or words
class Word(TypedDict):
    x1: int
    y1: int
    x2: int
    y2: int
    w: int
    h: int
    text: str


# Dicty type for paragraph
class Paragraph(TypedDict):
    x: int
    y: int
    w: int
    h: int
    text: str
    image: np.ndarray
    max_width: int
    translated_text: str
    word_list: List[Word]
