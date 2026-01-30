# Klar Natural Language Search Examples

This document demonstrates the Natural Language Processing (NLP) capabilities of the Klar Search Engine for Swedish language queries.

## Overview

Klar's NLP engine is designed to understand natural Swedish language queries, not just keywords. Users (especially elderly and youth) can type naturally as they would ask a question to a person, and the search engine processes it intelligently.

## How It Works

The NLP pipeline processes queries through several stages:

1. **Tokenization** - Splits text into words (tokens)
2. **Lemmatization** - Converts words to their root forms
   - Example: "restauranger" → "restaurang", "universitet" → "universit"
3. **Stopword Removal** - Removes common Swedish words that don't add meaning
   - Removes: "och", "det", "för", "att", "i", "på", "är", "som", etc.
4. **Synonym Expansion** - Adds related terms to improve results
   - "universitet" → also search for "högskola", "lärosäte"
5. **Search Execution** - Finds relevant documents using the processed query

## Natural Language Query Examples

### Example 1: Question Format

**User types (naturally):**
```
Var hittar jag svenska universitet?
(Where can I find Swedish universities?)
```

**What KSE does:**
- Original query: "Var hittar jag svenska universitet?"
- Processed to: ["hitta", "svensk", "universit"]
- Removes: "Var" (stopword), "jag" (stopword)
- Lemmatizes: "hittar" → "hitta", "svenska" → "svensk", "universitet" → "universit"
- Expands: "universit" → also search "högskola", "lärosäte"
- **Result:** Returns Swedish university websites

### Example 2: Informal Language

**User types (casually):**
```
jag vill lära mig om forskning
(I want to learn about research)
```

**What KSE does:**
- Original: "jag vill lära mig om forskning"
- Processed to: ["lär", "forskning"]
- Removes: "jag", "vill", "mig", "om" (all stopwords)
- Keeps meaningful words: "lära", "forskning"
- Expands: "forskning" → also "studie", "vetenskap"
- **Result:** Returns research and academic content

### Example 3: Location-Based Query

**User types:**
```
vilka restauranger finns i Stockholm
(what restaurants are in Stockholm)
```

**What KSE does:**
- Original: "vilka restauranger finns i Stockholm"
- Processed to: ["restauranga", "stockholm"]
- Removes: "vilka", "finns", "i" (stopwords)
- Lemmatizes: "restauranger" → "restauranga"
- Keeps location: "Stockholm"
- **Result:** Returns restaurants in Stockholm

### Example 4: "How" Questions

**User types:**
```
hur fungerar sökmotorer
(how do search engines work)
```

**What KSE does:**
- Original: "hur fungerar sökmotorer"
- Processed to: ["fungera", "sökmotora"]
- Removes: "hur" (stopword)
- Lemmatizes: "fungerar" → "fungera", "sökmotorer" → "sökmotora"
- **Result:** Returns educational content about search engines

## More Natural Language Examples

### For Elderly Users (Simple Language)

| Natural Query | Processed Query | Expected Results |
|---------------|-----------------|------------------|
| "Var kan jag få hjälp med pensionen" | ["hjälp", "pension"] | Pension support sites |
| "Vad kostar läkarbesök" | ["kosta", "läkarbesök"] | Healthcare cost info |
| "Hur bokar man tider hos tandläkare" | ["boka", "tid", "tandläkar"] | Dental appointment info |
| "Restauranger nära mig med hemkörning" | ["restauranga", "hemkörning"] | Delivery restaurants |

### For Youth Users (Informal Language)

| Natural Query | Processed Query | Expected Results |
|---------------|-----------------|------------------|
| "Coola ställen i Stockholm för unga" | ["cool", "stall", "stockholm", "ung"] | Youth activities in Stockholm |
| "Hur pluggar man effektivt" | ["plugga", "effektiv"] | Study tips |
| "Bästa gymmen för studenter" | ["bäst", "gymm", "student"] | Student gyms |
| "Var kan man hänga med kompisar gratis" | ["häng", "kompis", "gratis"] | Free hangout spots |

### Academic Queries

| Natural Query | Processed Query | Expected Results |
|---------------|-----------------|------------------|
| "Vilka är Sveriges bästa universitet för medicin" | ["svensk", "bäst", "universit", "medicin"] | Medical schools |
| "Hur ansöker man till högskola" | ["ansök", "högskol"] | University application info |
| "Forskning om klimatförändringar i Sverige" | ["forskning", "klimatförändring", "sverig"] | Climate research |

### Local Business Queries

| Natural Query | Processed Query | Expected Results |
|---------------|-----------------|------------------|
| "Vem fixar trasiga datorer i Uppsala" | ["fix", "trasig", "dator", "uppsala"] | Computer repair Uppsala |
| "Billig mataffär i närheten" | ["billig", "mataffär", "närhet"] | Budget grocery stores |
| "Öppettider för biblioteket" | ["öppettid", "bibliotek"] | Library hours |

## Key Features

### 1. Handles Misspellings (Basic)

While Klar's current implementation focuses on lemmatization rather than spell correction, it handles word variations:

- "universitetet" and "universitet" → both become "universit"
- "restaurangerna" and "restauranger" → both become "restauranga"

### 2. Understanding Swedish Grammar

Swedish has compound words and complex grammar. Klar handles:

- **Compound words:** "biblioteksbok" → processed correctly
- **Definite/indefinite forms:** "boken" / "bok" → "bok"
- **Plural forms:** "böcker" → "bok"

### 3. Synonym Understanding

Klar expands queries with Swedish synonyms:

| Original | Synonyms Also Searched |
|----------|------------------------|
| universitet | högskola, lärosäte |
| forskning | studie, vetenskap |
| utbildning | kurs, program |
| student | studerande, elev |

## Testing NLP Yourself

You can test the NLP processing from Python:

```python
from kse.nlp.kse_nlp_core import NLPCore

# Initialize NLP
nlp = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)

# Test a natural language query
query = "Var hittar jag svenska universitet?"
processed = nlp.process_text(query)

print(f"Original: {query}")
print(f"Processed: {processed}")
# Output: ['hitta', 'svensk', 'universit']
```

## Comparison: Keyword vs. Natural Language

### Traditional Keyword Search (Google-style)

User must think in keywords:
- "svenska universitet" ✓ Works
- "Var hittar jag svenska universitet?" ✗ Too many irrelevant words

### Klar Natural Language Search

User types naturally:
- "svenska universitet" ✓ Works
- "Var hittar jag svenska universitet?" ✓ Also works!
- "jag vill veta om svenska universitet" ✓ Works too!

## Supported Swedish Language Features

### Stopwords (Removed)

Klar removes 133 common Swedish stopwords including:
- Pronouns: jag, du, han, hon, vi, ni, de
- Prepositions: i, på, av, till, från, för
- Articles: en, ett, den, det
- Conjunctions: och, eller, men
- Common verbs: är, var, har, hade, blir, blev
- Question words: vad, var, vem, hur, när, varför

### Lemmatization

Converts Swedish words to root forms:
- Verbs: "springer", "sprang", "sprungit" → "spring"
- Nouns: "boken", "böcker", "böckerna" → "bok"
- Adjectives: "svenska", "svenskt", "svenskar" → "svensk"

## Limitations & Future Improvements

### Current Limitations

1. **Basic synonym expansion** - Currently only 4 hardcoded synonym sets
2. **No spell correction** - Misspellings may not match correctly
3. **Limited entity recognition** - Doesn't identify all names/places/organizations
4. **Swedish-only** - No support for other languages

### Planned Improvements

1. **Machine-learned synonyms** - Use word embeddings for semantic similarity
2. **Spell correction** - Handle typos automatically
3. **Entity recognition** - Better understanding of names, places, dates
4. **Query intent detection** - Distinguish informational vs. navigational queries
5. **Multi-language support** - Add English support for international users

## Conclusion

Klar's NLP engine makes search accessible to everyone, regardless of technical knowledge. Users can type naturally in Swedish, and the search engine understands their intent.

**Key Advantages:**
- ✅ Natural language queries work
- ✅ No need to think in keywords
- ✅ Handles Swedish grammar and word forms
- ✅ Removes irrelevant words automatically
- ✅ Expands queries with synonyms
- ✅ Accessible for elderly and youth users

For more information:
- See `README.md` for general documentation
- See `KSE-DEPLOYMENT.md` for deployment
- See `REMOTE_CLIENT_GUIDE.md` for client setup
