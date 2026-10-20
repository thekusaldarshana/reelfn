# Offline voice (experimental)

The default narrator is Gemini text-to-speech. For an offline voice, reelfn can use
[kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) 0.6.1 (MIT) with the Kokoro v1.0 model (Apache 2.0).

1. Install the extra Python packages: `npm run setup -- --local-voice`.
2. Download these two files from the project's
   [model-files-v1.1 release](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1)
   into `.tools/kokoro/` (git-ignored, about 330 MB in total):

   | File | SHA-256 |
   | --- | --- |
   | `kokoro-v1.0.onnx` | `BEB0D1848DEE9A49DA392CC3DF26958D46CFA35D321EDF434F52949153F0DF3A` |
   | `voices-v1.0.bin` | `BCA610B8308E8D99F32E6FE4197E7EC01679264EFED0CAC9140FE9C29F1FBF7D` |

3. In `brand/brand.json`, set `"voice": { "provider": "kokoro", "voice": "af_sarah" }` (any Kokoro voice name).

The model files are large and are never committed. Each render records the voice and model hashes in its manifest.
