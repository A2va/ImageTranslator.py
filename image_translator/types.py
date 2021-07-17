from typing import TypedDict, List, Tuple
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
    x: int  # Position of the text
    y: int
    w: int
    h: int
    dx: int  # d stands for detection
    dy: int  # Position returned by the detector
    dw: int
    dh: int
    text: str
    image: np.ndarray
    bin_image: np.ndarray
    text_color: Tuple[int, int, int]
    max_width: int
    translated_text: str
    word_list: List[Word]
