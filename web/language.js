'use strict';
// Display text only: language changes never alter survey IDs, answers or scores.
(() => {
  const strings = {
    "Language":"ভাষা", "moviegame":"মুভিগেম", "MovieGame home":"মুভিগেমের প্রথম পাতা",
    "MovieGame — Find your main character":"মুভিগেম — আপনার গল্পের চরিত্র খুঁজুন",
    "Skip to content":"মূল বিষয়বস্তুতে যান", "Main navigation":"প্রধান নেভিগেশন",
    "Character Game":"চরিত্র খেলা", "The character library":"চরিত্রের সংগ্রহশালা", "Find my character":"আমার চরিত্র খুঁজুন",
    "A little self-discovery. A lot of cinema.":"নিজেকে একটু চেনা। সিনেমার বিশাল দুনিয়া।",
    "How it works & privacy":"খেলার নিয়ম ও গোপনীয়তা", "Close":"বন্ধ করুন",
    "BEHIND THE SCENES":"পর্দার আড়ালে", "A story match.":"গল্পে গল্পে মিল।", "Just for fun.":"শুধুই মজার জন্য।",
    "Each game draws 15 varied questions from its own question bank, with shuffled choices. Your answers form an eight-trait profile. We compare it with editorial character profiles using equal-weight distance. The five closest traits explain your match. Affinity is a game score, not a probability or a psychological assessment.":"প্রতিটি খেলায় নিজস্ব প্রশ্নভান্ডার থেকে ১৫টি বৈচিত্র্যময় প্রশ্ন আসে, উত্তরের ক্রমও বদলে যায়। আপনার উত্তর থেকে আটটি বৈশিষ্ট্যের একটি প্রোফাইল তৈরি হয়। প্রতিটি বৈশিষ্ট্যকে সমান গুরুত্ব দিয়ে চরিত্রগুলোর সম্পাদকীয় প্রোফাইলের সঙ্গে তা তুলনা করা হয়। সবচেয়ে কাছাকাছি পাঁচটি বৈশিষ্ট্য দিয়ে মিলের কারণ বোঝানো হয়। মিলের স্কোরটি খেলার অংশ; এটি সম্ভাবনার হিসাব বা মনস্তাত্ত্বিক মূল্যায়ন নয়।",
    "Movie identities and reference links accompany every entry. Personality profiles and themes are our interpretations. “Source checked” means a reference was checked during catalog preparation; other entries still need editorial verification. Plot details can contain spoilers.":"প্রতিটি সিনেমার সঙ্গে পরিচয় ও তথ্যসূত্রের লিংক দেওয়া আছে। ব্যক্তিত্বের প্রোফাইল ও থিম আমাদের নিজস্ব ব্যাখ্যা। ‘তথ্যসূত্র যাচাইকৃত’ মানে সংগ্রহশালা তৈরির সময় সূত্রটি দেখা হয়েছে; অন্য এন্ট্রিগুলোর সম্পাদকীয় যাচাই এখনো বাকি। বর্ণনায় গল্পের ঘটনা আগেই জানা যেতে পারে।",
    "No account, name, email, or external AI service is needed. Your quiz progress stays in this browser tab. A submitted result and a hash of your answers are retained on the server for up to 30 days when scheduled cleanup is enabled. Rate limits use a short-lived hashed network address. Clear this tab’s progress with “Start over.” Sharing is optional. The share buttons create a public, expiring result page with the display name you choose, character, and trait bars. Your full survey answers are not included. Shared images may remain in social platforms’ caches after the page expires. Instagram uses the device share sheet or an image download; it does not post automatically.":"অ্যাকাউন্ট, নাম, ইমেইল বা বাইরের কৃত্রিম বুদ্ধিমত্তার সেবা লাগে না। আপনার খেলার অগ্রগতি এই ব্রাউজার ট্যাবে থাকে। নির্ধারিত পরিষ্কার প্রক্রিয়া চালু থাকলে জমা দেওয়া ফলাফল ও উত্তরগুলোর হ্যাশ সার্ভারে সর্বোচ্চ ৩০ দিন থাকে। অনুরোধের সীমা নিয়ন্ত্রণে অল্প সময়ের জন্য নেটওয়ার্ক ঠিকানার হ্যাশ ব্যবহার করা হয়। ‘আবার শুরু করুন’ দিয়ে এই ট্যাবের অগ্রগতি মুছে ফেলতে পারেন। শেয়ার করা ঐচ্ছিক। শেয়ার বোতামে আপনার বেছে নেওয়া নাম, চরিত্র ও বৈশিষ্ট্যের বারসহ মেয়াদযুক্ত একটি প্রকাশ্য পাতা তৈরি হয়। জরিপের সম্পূর্ণ উত্তর সেখানে থাকে না। পাতার মেয়াদ শেষ হলেও সামাজিক মাধ্যমে ছবির কপি থেকে যেতে পারে। ইনস্টাগ্রামের জন্য ডিভাইসের শেয়ার মেনু বা ছবি ডাউনলোড ব্যবহার করা হয়; স্বয়ংক্রিয়ভাবে পোস্ট হয় না।",
    "Film and character names belong to their respective owners. MovieGame is an independent fan experience.":"সিনেমা ও চরিত্রের নাম সংশ্লিষ্ট মালিকদের। মুভিগেম ভক্তদের জন্য তৈরি একটি স্বাধীন অভিজ্ঞতা।",
    "YOUR NEXT PLOT TWIST IS YOU":"আপনিই গল্পের পরের চমক", "You have":"আপনার মধ্যেই আছে", "main character":"গল্পের নায়কের", "energy.":"প্রাণশক্তি।",
    "Somewhere in the movies, there’s a character who sees the world a little like you. Let’s find them.":"সিনেমার জগতে এমন এক চরিত্র আছে, যে পৃথিবীকে কিছুটা আপনার মতো করেই দেখে। চলুন তাকে খুঁজে নিই।",
    "Meet my character":"আমার চরিত্রের সঙ্গে দেখা হোক", "15 questions":"১৫টি প্রশ্ন", "About 3 minutes":"প্রায় ৩ মিনিট", "100% you":"১০০% আপনার মতো",
    "Original illustrated cards representing dreamers, explorers, and everyday heroes":"স্বপ্নবাজ, অভিযাত্রী ও প্রতিদিনের নায়কদের নিয়ে নিজস্ব আঁকা কার্ড",
    "THE INNER UNIVERSE":"মনের ভুবন", "THE":"সেই", "DREAMER":"স্বপ্নবাজ", "IMAGINE MORE":"কল্পনার ডানা মেলুন",
    "A WORLD OF POSSIBILITIES":"সম্ভাবনার পৃথিবী", "EXPLORER":"অভিযাত্রী", "GO A LITTLE FURTHER":"আরও একটু এগিয়ে যান",
    "SOME STORIES FIND YOU":"কিছু গল্প আপনাকেই খুঁজে নেয়", "EVERYDAY":"প্রতিদিনের", "HERO":"নায়ক", "IT COULD BE YOU":"সেই মানুষটি আপনিও হতে পারেন",
    "EVERY CHARACTER HAS A LITTLE OF US.":"প্রতিটি চরিত্রে আমাদেরও কিছুটা ছায়া আছে।", "Game features":"খেলার বৈশিষ্ট্য",
    "HOLLYWOOD TO DHAKA":"হলিউড থেকে ঢাকা", "A LITTLE ANIME MAGIC":"অ্যানিমের একটু জাদু", "YOUR STORY STARTS HERE":"আপনার গল্প শুরু এখানেই",
    "ONE QUIZ. DIFFERENT WORLDS.":"একটি জরিপ। নানা ভুবন।", "Where do you belong?":"আপনার ভুবন কোনটি?",
    "Big-screen legends, stories close to home, and worlds beyond imagination.":"বড় পর্দার কিংবদন্তি, চেনা জীবনের গল্প আর কল্পনাকে ছাড়িয়ে যাওয়া জগৎ।",
    "01 / THE BIG SCREEN":"০১ / বড় পর্দা", "02 / STORIES CLOSE TO HOME":"০২ / চেনা জীবনের গল্প", "03 / BEYOND THE ORDINARY":"০৩ / সাধারণের সীমানা পেরিয়ে",
    "Hollywood":"হলিউড", "Bangladeshi":"বাংলাদেশি", "Bangladeshi cinema":"বাংলাদেশি সিনেমা", "Japanese anime":"জাপানি অ্যানিমে", "All cinema":"সব সিনেমা",
    "For the bold, the brilliant, and the beautifully human.":"সাহসী, মেধাবী আর সুন্দর মানবিক মানুষদের জন্য।", "Familiar streets. Unforgettable hearts.":"চেনা পথঘাট। মনে থেকে যাওয়া মানুষ।", "A little wonder. A whole lot of possibility.":"একটু বিস্ময়। অফুরন্ত সম্ভাবনা।",
    "A DIFFERENT WAY TO FIND YOURSELF":"নিজেকে খুঁজে পাওয়ার আরেকটি পথ", "Character Game.":"চরিত্র খেলা।",
    "A separate survey about your instincts, decisions, and relationships. Discover your character across every movie in the library.":"আপনার সহজাত প্রতিক্রিয়া, সিদ্ধান্ত ও সম্পর্ক নিয়ে আলাদা একটি জরিপ। সংগ্রহশালার সব সিনেমার মধ্য থেকে খুঁজে নিন আপনার চরিত্র।",
    "Play Character Game":"চরিত্র খেলা খেলুন", "A few choices.":"কয়েকটি পছন্দ।", "A familiar kind of magic.":"চেনা এক জাদুর ছোঁয়া।",
    "Follow your instinct":"মনের কথায় চলুন", "15 varied everyday moments. Different ways to respond. No right answers.":"দৈনন্দিন জীবনের ১৫টি ভিন্ন মুহূর্ত। সাড়া দেওয়ার নানা উপায়। সঠিক বা ভুল উত্তর নেই।",
    "Meet your match":"মিলের চরিত্রটি চিনুন", "Find the character whose story energy feels closest to yours.":"যে চরিত্রের গল্পের প্রাণশক্তি আপনার সবচেয়ে কাছাকাছি, তাকে খুঁজে নিন।",
    "See the connection":"মিলের কারণ জানুন", "Five reasons, drawn from your choices. Then share your reveal.":"আপনার পছন্দ থেকে পাওয়া পাঁচটি কারণ। এরপর ফলাফল শেয়ার করুন।",
    "← Back to the lobby":"← প্রথম পাতায় ফিরুন", "Quiz progress":"খেলার অগ্রগতি", "THE OPENING CHAPTER":"গল্পের প্রথম অধ্যায়", "THE PLOT THICKENS":"গল্প জমে উঠছে", "YOUR FINAL ACT":"গল্পের শেষ অধ্যায়", "CHARACTER GAME":"চরিত্র খেলা",
    "Choose what feels most like you. Every listed answer belongs here.":"যেটি আপনার সঙ্গে বেশি মেলে, সেটি বেছে নিন। প্রতিটি উত্তরই গ্রহণযোগ্য।", "Choose your cinema":"সিনেমার ধরন বেছে নিন",
    "← Previous scene":"← আগের প্রশ্ন", "Finding your character…":"আপনার চরিত্র খোঁজা হচ্ছে…", "Reveal my character":"আমার চরিত্র দেখান", "Next scene":"পরের প্রশ্ন",
    "Progress is saved in this tab.":"অগ্রগতি এই ট্যাবে সংরক্ষিত থাকে।", "Start over":"আবার শুরু করুন",
    "THE REVEAL":"চরিত্র উন্মোচন", "Different worlds. A familiar way of being.":"ভিন্ন জগৎ। তবু চেনা এক মন।", "YOUR STORY AFFINITY":"আপনার গল্পের মিল",
    "Film reference":"সিনেমার তথ্যসূত্র", "Source checked":"তথ্যসূত্র যাচাইকৃত", "Source checked.":"তথ্যসূত্র যাচাইকৃত।", "Reference supplied; editorial verification pending.":"তথ্যসূত্র দেওয়া আছে; সম্পাদকীয় যাচাই বাকি।",
    "Affinity is a playful similarity score, not a scientific measure.":"এটি মজার ছলে মিলের স্কোর; বৈজ্ঞানিক পরিমাপ নয়।", "Your trait profile":"আপনার বৈশিষ্ট্যের প্রোফাইল",
    "THE THINGS THAT CONNECT YOU":"যে মিলগুলো আপনাদের যুক্ত করে", "Five reasons this feels like you.":"আপনার মতো মনে হওয়ার পাঁচটি কারণ।",
    "A few characters share your story energy. Explore the alternatives below as well.":"কয়েকটি চরিত্রের গল্পেই আপনার মতো প্রাণশক্তি আছে। নিচের অন্য মিলগুলোও দেখুন।",
    "courage":"সাহস", "empathy":"সহমর্মিতা", "curiosity":"কৌতূহল", "discipline":"শৃঙ্খলা", "independence":"স্বাধীনচেতা মনোভাব", "sociability":"মিশুক স্বভাব", "creativity":"সৃজনশীলতা", "resilience":"ঘুরে দাঁড়ানোর ক্ষমতা",
    "Share your character & trait bars":"আপনার চরিত্র ও বৈশিষ্ট্যের বার শেয়ার করুন", "Name on your shared result (optional)":"শেয়ার করা ফলাফলে যে নাম থাকবে (ঐচ্ছিক)", "Your name or nickname":"আপনার নাম বা ডাকনাম",
    "Sharing creates a public link with this name, your character, and the eight trait bars. Your full answers stay private.":"শেয়ার করলে এই নাম, আপনার চরিত্র ও আটটি বৈশিষ্ট্যের বারসহ একটি প্রকাশ্য লিংক তৈরি হয়। আপনার সম্পূর্ণ উত্তর গোপন থাকে।",
    "Facebook":"ফেসবুক", "Instagram":"ইনস্টাগ্রাম", "Copy Link":"লিংক কপি করুন", "Save result image":"ফলাফলের ছবি সংরক্ষণ করুন", "Your named character result with eight trait bars":"আপনার নাম ও আটটি বৈশিষ্ট্যের বারসহ চরিত্রের ফলাফল",
    "Play another story":"আরেকটি গল্প খেলুন", "Try Character Game":"চরিত্র খেলা খেলুন", "Also in your universe":"আপনার ভুবনের আরও চরিত্র", "Curious about the cast?":"চরিত্রগুলো নিয়ে কৌতূহল আছে?", "Explore the character library":"চরিত্রের সংগ্রহশালা দেখুন",
    "A WHOLE WORLD OF CHARACTERS":"চরিত্রের বিশাল এক জগৎ", "The character library.":"চরিত্রের সংগ্রহশালা।",
    "Discover the stories behind your match. Character identities are factual; themes and personality profiles are editorial interpretations.":"আপনার সঙ্গে মেলা চরিত্রের গল্প জানুন। চরিত্রের পরিচয় তথ্যভিত্তিক; থিম ও ব্যক্তিত্বের প্রোফাইল সম্পাদকীয় ব্যাখ্যা।",
    "Search films, characters, or themes":"সিনেমা, চরিত্র বা থিম খুঁজুন", "Search films, characters, or themes…":"সিনেমা, চরিত্র বা থিম খুঁজুন…", "Opening the library…":"সংগ্রহশালা খোলা হচ্ছে…",
    "No stories found. Try another title, character, or theme.":"কোনো গল্প পাওয়া যায়নি। অন্য সিনেমা, চরিত্র বা থিম দিয়ে খুঁজুন।", "← Previous":"← আগের পাতা", "Next →":"পরের পাতা →",
    "The library could not load. Change a filter to retry.":"সংগ্রহশালা খোলা যায়নি। অন্য ফিল্টার বেছে নিয়ে আবার চেষ্টা করুন।", "Getting your story ready…":"আপনার গল্প প্রস্তুত হচ্ছে…",
    "The cinema is taking a moment.":"সিনেমার দুনিয়া একটু সময় নিচ্ছে।", "Please check your connection, then try again.":"ইন্টারনেট সংযোগ দেখে আবার চেষ্টা করুন।", "Try again":"আবার চেষ্টা করুন",
    "Original MovieGame cover art":"মুভিগেমের নিজস্ব প্রচ্ছদচিত্র", "Artwork source":"ছবির তথ্যসূত্র", "reference artwork":"তথ্যসূত্রের ছবি", "original MovieGame cover":"মুভিগেমের নিজস্ব প্রচ্ছদ",
    "A new edition is here. Start a fresh story.":"নতুন সংস্করণ এসেছে। নতুন করে গল্প শুরু করুন।", "That request could not be completed. Please try again.":"অনুরোধটি সম্পন্ন করা যায়নি। আবার চেষ্টা করুন।",
    "Connection interrupted. Your answers are safe in this tab. Try the reveal again.":"সংযোগ বিচ্ছিন্ন হয়েছে। উত্তরগুলো এই ট্যাবে আছে। আবার ফলাফল দেখার চেষ্টা করুন।", "Your result could not be saved. Return to the quiz to retry.":"ফলাফল সংরক্ষণ করা যায়নি। জরিপে ফিরে আবার চেষ্টা করুন।",
    "Your game changed. Share the result of the current quiz instead.":"আপনার খেলা বদলে গেছে। বর্তমান জরিপের ফলাফল শেয়ার করুন।", "Preparing your named result and trait bars…":"আপনার নাম ও বৈশিষ্ট্যের বারসহ ফলাফল প্রস্তুত হচ্ছে…",
    "Result link copied, including your name and trait bars.":"আপনার নাম ও বৈশিষ্ট্যের বারসহ ফলাফলের লিংক কপি হয়েছে।", "Copy this result link:":"ফলাফলের এই লিংকটি কপি করুন:",
    "Facebook can preview your name and trait bars when this game is on a public HTTPS domain.":"খেলাটি প্রকাশ্য সুরক্ষিত ডোমেইনে থাকলে ফেসবুকে আপনার নাম ও বৈশিষ্ট্যের বার দেখা যাবে।",
    "The result image could not be loaded. Try again.":"ফলাফলের ছবি খোলা যায়নি। আবার চেষ্টা করুন।", "My MovieGame character":"আমার মুভিগেম চরিত্র",
    "Choose Instagram in your device share sheet. The image includes your name and all eight bars.":"ডিভাইসের শেয়ার মেনুতে ইনস্টাগ্রাম বেছে নিন। ছবিতে আপনার নাম ও আটটি বারই আছে।",
    "Your result image is ready to save. Add it to an Instagram story or post from the Instagram app.":"ফলাফলের ছবি সংরক্ষণের জন্য প্রস্তুত। ইনস্টাগ্রাম অ্যাপ থেকে স্টোরি বা পোস্টে যোগ করুন।", "Sharing cancelled. Your result image is still ready.":"শেয়ার করা বাতিল হয়েছে। ফলাফলের ছবি এখনো প্রস্তুত আছে।",
    "Sharing could not open. Use Save result image, then share it in Instagram.":"শেয়ার মেনু খোলা যায়নি। ফলাফলের ছবি সংরক্ষণ করে ইনস্টাগ্রামে শেয়ার করুন।",
    "The cinema is busy. Please retry in a moment.":"এখন অনেকেই খেলছেন। একটু পরে আবার চেষ্টা করুন।", "Submissions are temporarily unavailable. Your answers are still in this tab.":"সাময়িকভাবে উত্তর জমা নেওয়া যাচ্ছে না। উত্তরগুলো এই ট্যাবেই আছে।",
    "Too many attempts. Please try again next minute.":"অনেকবার চেষ্টা হয়েছে। পরের মিনিটে আবার চেষ্টা করুন।", "Could not save the result. Retry with the same key.":"ফলাফল সংরক্ষণ করা যায়নি। আবার একইভাবে চেষ্টা করুন।",
    "This survey has been updated. Reload to start the current edition.":"জরিপ হালনাগাদ হয়েছে। নতুন সংস্করণ শুরু করতে পাতা আবার খুলুন।", "This key already belongs to different answers. Start a new quiz.":"এই ফলাফলের সঙ্গে অন্য উত্তর রয়েছে। নতুন জরিপ শুরু করুন।",
    "This result is unavailable or has expired. Complete a new quiz before sharing.":"ফলাফলটি পাওয়া যাচ্ছে না বা মেয়াদ শেষ। শেয়ার করার আগে নতুন জরিপ শেষ করুন।",
    "15 little choices. A whole cinematic universe. Discover your movie character and the five things that connect you.":"১৫টি ছোট পছন্দ। সিনেমার বিশাল এক জগৎ। আপনার চরিত্র ও মিলের পাঁচটি কারণ আবিষ্কার করুন।"
  };
  const orderedStrings = Object.entries(strings).sort((a,b)=>b[0].length-a[0].length)
    .map(([en,bn])=>[new RegExp('(?<![A-Za-z])'+en.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'(?![A-Za-z])','g'),bn]);
  let saved;
  try { saved = localStorage.getItem('moviegame-language'); } catch {}
  const query = new URLSearchParams(location.search).get('lang');
  const isPublic = document.body?.hasAttribute('data-public-share');
  let lang = ['en','bn'].includes(query) ? query : isPublic ? document.documentElement.lang : saved === 'bn' ? 'bn' : 'en';
  const digits = value => String(value).replace(/[0-9]/g, n => '০১২৩৪৫৬৭৮৯'[n]);
  function translate(value) {
    if (lang !== 'bn') return value;
    const clean = value.trim();
    let translated = strings[clean];
    if (translated === undefined) {
      translated = clean.replace(/^(\d[\d,+]*) FILMS\. ENDLESS POSSIBILITIES\.$/, '$1টি সিনেমা। অফুরন্ত সম্ভাবনা।')
        .replace(/^SCENE (\d+) \/ (\d+)$/, 'প্রশ্ন $1 / $2')
        .replace(/^(\d+) films in this collection$/, 'এই সংগ্রহে $1টি সিনেমা')
        .replace(/^Page (\d+) of (\d+)$/, '$2 পাতার মধ্যে $1')
        .replace(/story affinity/g, 'গল্পের মিল');
      // Several elements deliberately split sentences with an icon or emphasis.
      for (const [pattern, bn] of orderedStrings) translated = translated.replace(pattern,bn);
    }
    if (!/^https?:\/\//.test(translated)) translated = digits(translated);
    return value.replace(clean, translated);
  }
  let bankPromise;
  async function localizeSurvey(survey, language=lang) {
    if (language!=='bn') return survey;
    bankPromise ||= fetch('/assets/survey-bn.json?v=19fa723cf97f', {cache:'force-cache'})
      .then(response=>{if(!response.ok) throw new Error('বাংলা উত্তরগুলো লোড করা যায়নি। আবার চেষ্টা করুন।');return response.json();})
      .catch(error=>{bankPromise=null;throw error;});
    const bank=(await bankPromise)[survey.mode];
    return {...survey, language:'bn', questions:survey.questions.map(question=>{
      const text=bank?.[question.id];
      if(!text) throw new Error('এই প্রশ্নের বাংলা অনুবাদ পাওয়া যায়নি। পাতা আবার খুলুন।');
      return {...question,text:text.text,options:question.options.map(option=>{
        const translated=text.options[String(option.id)];
        if(!translated) throw new Error('এই উত্তরের বাংলা অনুবাদ পাওয়া যায়নি। পাতা আবার খুলুন।');
        return {...option,text:translated};
      })};
    })};
  }
  function syncControl() {
    const control=document.getElementById('language-switcher');
    if(!control) return;
    if(control.tagName==='SELECT') control.value=lang;
    control.querySelectorAll('[data-language]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.language===lang)));
  }
  const original = new WeakMap(), attributes = new WeakMap();
  let observer;
  function apply() {
    observer?.disconnect();
    document.documentElement.lang = lang;
    if (isPublic) {
      syncControl();
      return; // Public pages are already translated by the server, including metadata.
    }
    const walker = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (node.parentElement?.closest('script, style, select, textarea, [data-i18n-skip]')) continue;
      const previous = original.get(node);
      const source = previous && node.nodeValue === previous.output ? previous.source : node.nodeValue;
      const output = translate(source);
      original.set(node, {source, output});
      if (node.nodeValue !== output) node.nodeValue = output;
    }
    document.querySelectorAll('[placeholder], [aria-label], [alt], meta[name="description"]').forEach(element => {
      const record = attributes.get(element) || {};
      for (const key of ['placeholder', 'aria-label', 'alt', ...(element.tagName === 'META' ? ['content'] : [])]) {
        if (!element.hasAttribute(key)) continue;
        const value = element.getAttribute(key), previous = record[key];
        const source = previous && value === previous.output ? previous.source : value;
        const output = translate(source);
        record[key] = {source, output};
        if (value !== output) element.setAttribute(key, output);
      }
      attributes.set(element, record);
    });
    syncControl();
    observer?.observe(document.documentElement, {subtree:true, childList:true, characterData:true, attributes:true, attributeFilter:['placeholder','aria-label','alt']});
  }
  window.MovieLocale = {get lang() {return lang;}, localizeSurvey, t:translate, number:value=>lang==='bn'?digits(value):String(value), apply};
  observer = new MutationObserver(apply);
  apply();
  function changeLanguage(value) {
    const next=value==='bn'?'bn':'en';
    if(next===lang) return;
    lang=next;
    try {localStorage.setItem('moviegame-language', lang);} catch {}
    const url = new URL(location.href); url.searchParams.set('lang',lang);
    if (isPublic) {location.assign(url.href);return;}
    history.replaceState(null,'',url);
    apply();
    window.dispatchEvent(new Event('moviegame:languagechange'));
  }
  document.addEventListener('click', event=>{
    const button=event.target.closest('button[data-language]');
    if(button && !button.disabled && !button.closest('fieldset')?.disabled) changeLanguage(button.dataset.language);
  });
  document.addEventListener('change', event=>{
    if(event.target.id==='language-switcher' && event.target.tagName==='SELECT') changeLanguage(event.target.value);
  });
})();
