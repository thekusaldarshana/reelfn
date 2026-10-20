# Release: post copy and delivery

## `reels/<name>/release.md`
Fill the template with: **Caption**, **Hashtags**, **Alt text / cover**, **Decisions** (what the creator chose and
what you chose), **Status** (approvals still pending). Nothing posts automatically.

Caption structure (short, no links; works for Instagram, TikTok and YouTube Shorts):
1. Hook line that mirrors the first frame (a number or a situation).
2. Two to four lines of the insight, with the same numbers as the video.
3. One line of honesty: assumptions and limits ("assumes 200 million steps a second; counts steps, not seconds").
4. A closing question the viewer can answer in a comment.

Hashtags: 8-12; two or three broad, a few topic-specific, one learning tag, and the creator's `hashtag` from
`brand/brand.json` if set. Alt text: one sentence describing what the animation shows, with its numbers.

## Deliver
- The video is `output/<name>/<name>.mp4` (or `-<version>.mp4`). Tell the creator where it is; if your harness can
  send files, send it. In a cloud or temporary workspace, `output/` disappears with the session, so always send it.
- Report the file hash (`outputSha256` in the manifest); final approval is bound to it.
- A video made with `--voice placeholder` is silent: say so, and never present it as final.

## Saving work
`reels/` and `brand/` are the creator's and git-ignored by default. Do not commit, push or open pull requests unless
the creator asks. If they keep reels in their own fork, they can remove those lines from `.gitignore`.

## Final message checklist
Done/stuck first · what the reel actually teaches vs its title · decisions made (and how to change them) · assumptions
on screen · evidence quality (e.g. "a table cell was garbled in the fetch") · files · open approvals · next question.
