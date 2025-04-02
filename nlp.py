import spacy
import pandas as pd


def preprocess(text):
    words = []
    lemmas = []
    separable = []
    nlp = spacy.load("de_core_news_md")
    doc = nlp(text)

    for token in doc:
        words.append(token.text)
        lemmas.append(token.lemma_)
        if token.dep_ == "svp": 
            # Found a separable verb prefix (like "auf" in "stand auf")
            full_verb = token.text + token.head.lemma_
            separable.append({"head": token.head.i, "part":token.i, "full": full_verb})
        if token.pos_ == "PUNCT":
            pass
        
    df = pd.DataFrame({
        "word": words,
        "lemma": lemmas,
    })  
    
    df["variation"] = None
    
    for e in separable:
        df.loc[e["head"], "variation"] = e["full"]
        df.loc[e["part"], "variation"] = e["full"]
        
    return df