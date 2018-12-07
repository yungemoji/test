from flask import Flask, jsonify,request
import os
import spacy
from symspellpy.symspellpy import SymSpell, Verbosity
import stringdist
nlp = spacy.load("en")

app = Flask(__name__)

def symchecka(input_term):
    # create object
    initial_capacity = 83000
    # maximum edit distance per dictionary precalculation
    max_edit_distance_dictionary = 2
    prefix_length = 7
    sym_spell = SymSpell(initial_capacity, max_edit_distance_dictionary,
                         prefix_length)
    # load dictionary
    dictionary_path = os.path.join(os.path.dirname(__file__),
                                   "frequency_dictionary_en_82_765.txt")
    term_index = 0  # column of the term in the dictionary text file
    count_index = 1  # column of the term frequency in the dictionary text file
    if not sym_spell.load_dictionary(dictionary_path, term_index, count_index):
        print("Dictionary file not found")
        return

    # max edit distance per lookup (per single word, not per whole input string)
    max_edit_distance_lookup = 2
    suggestions = sym_spell.lookup_compound(input_term,
                                            max_edit_distance_lookup)
    # display suggestion term, edit distance, and term frequency
    for suggestion in suggestions:
        return(suggestion.term)
def matcher(instring):

    corrected = nlp(symchecka(instring))
    raw = nlp(instring.lower())

    cor_list = []
    raw_list = []

    for token in raw:
        raw_list.append(token.text)
    for token in corrected:
        cor_list.append(token.text)

    nc = [x for x in raw_list if x not in cor_list]

    pairlist = []
    for x in cor_list:
        if (x in cor_list and x in raw_list):
            cor_tuple = (x, x)
            pairlist.append(cor_tuple)
        else:
            minlevlist = []
            for item in nc:
                minlevlist.append(stringdist.levenshtein_norm(x, item))
            minloc = minlevlist.index(min(minlevlist))
            errtuple = (x, nc[minloc])
            pairlist.append(errtuple)

    pos_list = []
    for token in corrected:
        pos_list.append(token.pos_)

    final_list = []
    n = 0
    for i in pairlist:
        finaltuple = {"token": i[0], "pos": pos_list[n], "raw": i[1]}
        final_list.append(finaltuple)
        n = n + 1
    return final_list
def inputchecker(data):
    if "input" in data:
        instring = data["input"]
        if isinstance(instring,str):
            if instring.isdigit():
                return "input must be an alphabet string"
            else:
                return True
        else:
            return "input must be a string"
    else:
        return "data must contain a key named input"

@app.route("/",methods=['POST'])
def test_json():
    data = request.get_json()
    if inputchecker(data)==True:
        instring = data["input"]
        return jsonify({'tokens':matcher(instring)})
    else:
        return inputchecker(data),400

if __name__ == '__main__':
    app.run(debug=True)