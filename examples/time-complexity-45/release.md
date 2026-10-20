# Release copy: "Time complexity" 45s (search growth: scan vs split)

Honest scope: this Reel shows how search work grows (linear scan vs halving a sorted list) and introduces
O(n) vs O(log n). The deeper "what is time complexity and why it matters" Reel is `time-complexity-loops`.

## Caption

A million names. One way to find one needs up to 1,000,000 checks. The other needs 20.

SCAN = check every name, top to bottom. The work grows with the list: O(n).
SPLIT = halve a sorted list, keep the half that can still hold the name. The work grows with the log of the list: O(log n).

Double the names and the scan's work doubles. The split adds one single check. At a billion names? 30 checks.

(The list has to be sorted first. Counting steps, not seconds.)

Which would you rather scale? Tell me: SCAN or SPLIT?

## Hashtags

#computerscience #bigO #binarysearch #algorithms #datastructures #learntocode #softwareengineering #codingreels #stem

## Alt text / cover

Cover frame: the "A billion names" comparison (scan bar full, split 30). Alt text: "Animated comparison of a linear scan and a halving search over a million names, ending with growth curves labelled O(n) and O(log n)."

## Status

Example reel shipped with reelfn. When you adapt it, script approval, final-media approval and rights review are yours; nothing here posts anywhere automatically.
