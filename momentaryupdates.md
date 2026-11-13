# CCMC: momentaryupdates

## 13.11.2026: Speechify: the latest and greatest English model, one everywhere, A/B listening test on the ADAM

> please start another agent. He needs to test the sound from all three sources of our voice engines. We developed this voice engine. Right now, we change it from international speaking to English speaking, the latest model. In manifest, you always need to write: when you use Speechify, use the latest and greatest model. Voices never go to multilingual international nonsense. We want the best sound, because Marko is a sound engineer and has very delicate ears. ... Now, to compare the sound, I want you to work with Marko. ... the sound system will be connected to my Adam speaker. Play me a test from this computer, notebook, phone, and Pixel phone, and I can listen to it. Organize this, please

**Status:** saved first (13.11.2026). Plan: ask the API which models exist (GET /v1/audio/models), set the newest English model in every voice-engine path, rule in MANTRA_MANIFEST modules/speechify-latest-model.md, test kit claude-code/tools/voice_abtest.py.


Marko refines (13.11.2026, relayed): "Any application using Speechify ... It needs to intelligently find the latest version of the model. I think the name stays the same, only the version is picked up. When it's starting, it checks if the version is correct. Make it future-proof without any special. It's built in the app. Future-proofing is built in the app, and it should be the rule for any app we're making."
**Status:** saved first. Plan: one small function per language (speechify_model.py in CCMC, used by langsay, voiced.py; Kotlin in Speechify.kt), rule MANTRA_MANIFEST modules/latest-model-at-start.md.
