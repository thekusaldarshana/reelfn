# Release copy: Time complexity through duplicate detection (64s)

## Caption

How do you check a list for duplicates? With 1,000 distinct items, comparing every unordered pair takes 499,500 comparisons. A set scan makes 1,000 membership checks and 1,000 insertions in this simplified model.

At 10,000 items, those counts become 49,995,000 pair comparisons versus 20,000 set operations. That is time complexity: O(n²) versus average O(n).

Imagine **200 million abstract operations per second**, treating a comparison, membership check, and insertion as equally costly. For one billion distinct items, that model gives about **79 years versus 10 seconds**. This is an illustrative calculation, **not a measured computer benchmark**. Real operation costs differ, and the set uses extra memory. Python set membership is average O(1), worst-case O(n); insertion relies on typical hashing and amortization.

Which method would you choose? 👇

## Hashtags

#timecomplexity #bigO #algorithms #coding #programming #computerscience #learntocode #python #datastructures

## Alt text / cover

Cover frame: "~79 years → 10 seconds (illustrative model)". Alt text: "Duplicate checking compares each unordered pair with a nested loop or scans once using a set. A table shows about 42 minutes versus 10 milliseconds for one million distinct items and about 79 years versus 10 seconds for one billion under an assumed equal operation rate."

## Status

Draft for review. Script, final media, and rights not yet approved; nothing here posts anywhere automatically.
