# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This guide covers The Legend of Zelda: Tears of the Kingdom — including its story, lore, characters, abilities, and gameplay mechanics. This knowledge is valuable because the official Nintendo materials don't explain the narrative depth, character motivations, or practical gameplay strategies. Players rely on community wikis, Reddit breakdowns, and fan guides to actually understand what's happening in the game and how to play it effectively.

---

 ## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Zelda Fandom Wiki | General game information overview | https://zelda.fandom.com/wiki/The_Legend_of_Zelda:_Tears_of_the_Kingdom#Game_Information |
| 2 | Reddit r/truezelda | Community story breakdown and analysis | https://www.reddit.com/r/truezelda/comments/13l35ak/totk_botw_totk_complete_story_overhaul_and/ |
| 3 | Zelda Fandom Wiki | Full plot summary | https://zelda.fandom.com/wiki/The_Legend_of_Zelda:_Tears_of_the_Kingdom#Plot |
| 4 | Fextralife Wiki | All player abilities explained | https://zeldatearsofthekingdom.wiki.fextralife.com/Abilities |
| 5 | Inverse | Ending explained with spoilers | https://www.inverse.com/gaming/zelda-tears-kingdom-ending-explained-spoilers |
| 6 | Game8 | Weapon fusing guide | https://game8.co/games/Zelda-Tears-of-the-Kingdom/archives/409353 |
| 7 | CBR | Tips and tricks for completing shrines | https://www.cbr.com/zelda-totk-tricks-complete-shrines/ |
| 8 | Screen Rant | Why Zelda turned into a dragon | https://screenrant.com/zelda-totk-why-turned-into-dragon-secret-stone/ |
| 9 | Hyrule Archive | Sages guide — who they are and their powers | https://hyrulearchive.com/tears-of-the-kingdom/guide/sages-guide |
| 10 | Nintendo Life | Beginner tips — what to do first | https://www.nintendolife.com/guides/zelda-tears-of-the-kingdom-beginners-tips-what-to-do-first |

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Reasoning:** Documents range from short Reddit paragraphs to longer wiki and guide articles. 500 characters captures enough context for a meaningful semantic unit (a few sentences) without diluting the embedding with unrelated content. 100-character overlap ensures that facts spanning two adjacent chunks aren't lost — for example, a sentence explaining Zelda's transformation that begins at the end of one chunk and completes at the start of the next will still be retrievable.
---

## Retrieval Approach

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers (runs locally, no API key)

**Top-k:** 5 chunks per query

**Production tradeoff reflection:** For a real deployment I would consider OpenAI's text-embedding-3-large for higher accuracy on domain-specific text, or a multilingual model if the user base includes non-English speakers. The tradeoff is cost and latency vs. quality. all-MiniLM-L6-v2 is fast and free but has a 256-token context limit, which could truncate longer chunks. A production system might also use a larger context model like text-embedding-ada-002 to handle full paragraphs without truncation.
---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (local, no API key required)

**Production tradeoff reflection:** For a real deployment I would consider OpenAI's 
text-embedding-3-large or Cohere's embed-v3. The main tradeoffs are: context length — 
all-MiniLM-L6-v2 has a 256-token limit which can truncate longer chunks, while 
text-embedding-3-large supports up to 8191 tokens; accuracy on domain-specific text — 
a model fine-tuned on gaming or wiki content would likely outperform a general-purpose 
model on TotK queries; latency — local models like all-MiniLM-L6-v2 have no network 
overhead but are slower per batch than API-hosted models; and multilingual support — 
if the guide were expanded for non-English speakers, a multilingual model like 
paraphrase-multilingual-MiniLM-L12-v2 would be necessary.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt explicitly instructs the model 
to answer using ONLY the information provided in the retrieved documents and never use 
general training knowledge. The exact instruction is: "Answer the question using only 
the information in the provided documents. If the documents don't contain enough 
information to answer, say 'I don't have enough information on that.'" Retrieved chunks 
are injected into the user message as labeled context blocks in the format 
[Document N: filename] followed by the chunk text, so the model knows exactly which 
source each piece of information came from.

**How source attribution is surfaced in the response:** Source filenames are collected 
programmatically from the metadata of every retrieved chunk and appended to every 
response regardless of what the LLM returns. This means attribution is guaranteed 
structurally — it does not rely on the model choosing to cite sources on its own.
---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Why did Zelda turn into a dragon? | Zelda swallowed a secret stone and sacrificed herself to revive the Master Sword, becoming the Light Dragon | Zelda turned into a dragon for two reasons: becoming the Light Dragon makes her functionally immortal | Relevant | Partially accurate |

| 2 | Who is Ganondorf and what is his backstory in TotK? | Ganondorf was a Gerudo king who stole a secret stone, became the Demon King, and was imprisoned by Rauru | Ganondorf is the Demon King who stole Sonia's Secret Stone, gained power of darkness, and filled Hyrule with monsters | Relevant | Accurate |

| 3 | What are the four main abilities Link has in TotK? | Ultrahand, Fuse, Ascend, and Recall | I don't have enough information in my documents to answer that | Partially relevant | Inaccurate |

| 4 | What is the best strategy for completing shrines efficiently? | Use Ascend to skip sections, look for hidden rooms, prioritize light of blessing shrines | I don't have enough information in my documents to answer that | Partially relevant | Inaccurate |

| 5 | Who are the five sages and what powers do they grant? | Tulin (wind), Sidon (water), Yunobo (fire), Riju (lightning), Mineru (spirit) | I don't have enough information in my documents to answer that | Off-target | Inaccurate |

---

## Failure Case Analysis

**Question that failed:**
"What are the four main abilities Link has in TotK?"

**What the system returned:**
"I don't have enough information in my documents to answer that." — even though abilities.txt was collected specifically to cover this topic and was present in the retrieved sources.

**Root cause (tied to a specific pipeline stage):**
The failure originates in the chunking stage. The abilities.txt document contains a list of all four abilities, but the 500-character chunk size split the list across multiple chunks — each chunk only mentions one or two abilities without enough surrounding context to signal that this is a complete answer to the query. The retrieval stage returned chunks that each contained partial information, and the LLM's grounding instruction caused it to 
refuse rather than synthesize across incomplete chunks.

**What you would change to fix it:**
Increase chunk size to 800–1000 characters for list-heavy documents like abilities.txt, or use a document-aware chunking strategy that keeps structured lists intact as a single chunk rather than splitting mid-list.

---

## Spec Reflection

**One way the spec helped you during implementation:**
Writing the chunking strategy in planning.md before touching any code forced a deliberate decision about chunk size and overlap. When the abilities query failed, I could trace the root cause directly back to the chunk size decision — the spec made the pipeline transparent enough to debug.

**One way your implementation diverged from the spec, and why:**
The spec anticipated that all 5 evaluation questions would be answerable. In practice, 3 out of 5 returned refusals because the chunking strategy split list-heavy content across boundaries. The implementation would need a larger chunk size for structured documents like abilities.txt and sages.txt to match the original spec's intent.
---

## AI Usage

**Instance 1**
- *What I gave the AI:* My Chunking Strategy and Documents sections from planning.md
- *What it produced:* pipeline.py with load_documents(), clean_text(), and chunk_text() using 500-char chunks with 100-char overlap
- *What I changed or overrode:* I verified the output by inspecting 5 sample chunks and confirmed the chunk count of 2684 was within acceptable range

**Instance 2**
- *What I gave the AI:* My Retrieval Approach section and grounding requirement
- *What it produced:* embeddings.py using all-MiniLM-L6-v2 and ChromaDB, and query.py with a system prompt strictly limiting answers to retrieved context
- *What I changed or overrode:* I tested out-of-scope queries to verify the refusal mechanism worked correctly, and confirmed distance scores on retrieval were below 0.5 for strong queries