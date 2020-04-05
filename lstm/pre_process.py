#!/bin/usr/python3
# ----------------------------------------------------------
# Process data, spits out a cleaned out .csv file.
#
# ToDO:
# ---- 
# Optimize,i.e., use Pandas.DataFrame.isin() to create
# booleans which we can then use Vectorization to apply 
# mthods;
#
# argparse; 
#
# Use str.isalnum() to check if there only exists alpha or
# numeric characters;
# ----------------------------------------------------------

import os
import pandas as pd
import re
import string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


def load_files(filenames):
    yield pd.read_csv(filenames)

def remove_punctuation(word: str):
    # This handles cases like: Breeders and Breeders'
    table = str.maketrans('', '', string.punctuation)
    return word.translate(table)

def normalize(word: str) -> str:
    return word.lower()

def remove_stopwords(word: str) -> str:
    """
    Remove stop words - words that do not contribute to the deeper meaning of the phrase.
    e.g. 'some', 'not', 'do', 'the'
    """
    stop_words = stopwords.words('english')
    if not word in stop_words:
        return word
    else:
        return '0'
    
def reduce_base(word: str) -> str:
    """
    Reducing each word to its root or base
    """
    porter = PorterStemmer()
    return porter.stem(word)
    
def check_token_length(word: str, max_word_length: int) -> str:
    if len(word) < max_word_length:
        return True
    else:
        return False

def remove_single_punctuation(ThisWord) -> str:
    punctuations = '!"#%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    if ThisWord != '0':
        if (len(ThisWord)==1) and (ThisWord in punctuations):
            return '0'  
    return ThisWord

def remove_unwanted_tokens(ThisWord) -> str:
    unwanted = [
        'am','AM','PM', 'pm','p','a',"®","©","„",
        '€','▪', "/","—","-",'!',"•", '#','"','’',
        "‘",'&',"'",'(',')','}','{','*',':','<',
        '=','>','?','@','^','|'
    ]
    
    index = 0
    valid = True
    while valid and index < len(unwanted):
        if (unwanted[index] in ThisWord) and ('$' not in ThisWord):
            ThisWord = '0'
            valid = False
        index += 1
    return ThisWord

# Check if the first string starts with a letter, if yes use certain functions:
def process_words(token: str) -> str:
    """
    Helper function
    """
    
    max_word_length = 20
    
    # Create alphabet string
    alphabet = [chr(x) for x in range(65, 65+26)] + [chr(x) for x in range(97, 97+26)]
    
    # TO DO: replace this condition with str.isalnum()
    if token[0] in alphabet:
        
        # Lower case
        token = normalize(token)
        
        # Remove punctuation
        token = remove_punctuation(token)
        
        # Remove stem words
        token = reduce_base(token)
        
        # Remove stop words
        token = remove_stopwords(token)
        
        # After processing, is is less than character length we want?
        if check_token_length(token, max_word_length):
            return token
        else:
            return '0'

    else:
        # Remove single punctuation
        token = remove_single_punctuation(token)

        # Remove remove_unwanted_tokens
        token = remove_unwanted_tokens(token)
        
        # After processing, is is less than character length we want?
        if check_token_length(token, max_word_length):
            return token
        else:
            return '0'

def main():
    # Read filenames from the given path
    directory = './data_source'
    filename = 'training.csv'
    data_files = os.path.join(directory, filename)

    # Read in data in chunks
    data = pd.concat(load_files(data_files))

    # Let's drop NaN if there are any
    data['token'].dropna(inplace = True)

    # Keep only slug and token column
    data = data[['slug','token']]

    # Make sure the column are all str types
    data['token'] = data['token'].astype(str) 

    # Create a new column with processed (this is tmp)
    data['processed'] = data['token'].map(process_words)

    # Remove rows that have a 0s and/or empty string
    data = data[data.processed != '0']

    # Check we have file directory
    if not os.path.isdir('./processed_data'):
        os.mkdir('./processed_data')

    # Let's save this for now
    #data.to_csv('./data_source/mini_training.csv')
    data.to_csv('./processed_data/processed_data_instances.csv')


if __name__ == '__main__':
    main()