"""Versioned, transparent editorial survey. Values are intensity, not merit."""
TRAITS = ('courage', 'empathy', 'curiosity', 'discipline', 'independence',
          'sociability', 'creativity', 'resilience')
VERSION = 'story-2'
CHARACTER_VERSION = 'character-1'
ROWS = [
 ('courage', 'The adventure starts with a leap. You…',
  ['Stay where it feels safe.', 'Watch someone else go first.', 'Take it with a trusted friend.', 'Check the landing, then jump.', 'Volunteer to take the first leap.']),
 ('empathy', 'A friend goes quiet at the party. You…',
  ['Give them space and enjoy the party.', 'Wait for them to ask for company.', 'Send a quick “you okay?”', 'Sit with them and listen.', 'Stay with them for as long as they need.']),
 ('curiosity', 'A mysterious door appears in your story. You…',
  ['Walk past; your day is already full.', 'Notice it, but stick to your route.', 'Ask someone what is behind it.', 'Look for clues before opening it.', 'Make finding out your new mission.']),
 ('discipline', 'You have a month to prepare for a big moment. You…',
  ['Trust the energy of the final day.', 'Do a little when inspiration strikes.', 'Set a few milestones.', 'Follow a steady weekly routine.', 'Create a detailed plan and keep to it.']),
 ('independence', 'Everyone has an opinion about your next chapter. You…',
  ['Let your closest people choose with you.', 'Mostly follow their advice.', 'Balance their advice with your instincts.', 'Listen, then choose your own direction.', 'Follow your vision even without support.']),
 ('sociability', 'Your ideal scene after a long week is…',
  ['A quiet evening entirely to yourself.', 'One trusted person and a good conversation.', 'A small, familiar group.', 'A lively gathering of friends.', 'A room full of new people to meet.']),
 ('creativity', 'Your team needs a way out of a problem. You…',
  ['Use the solution that already works.', 'Make one small improvement to a proven method.', 'Mix a familiar method with a fresh idea.', 'Sketch several unexpected possibilities.', 'Invent a completely new way to approach it.']),
 ('resilience', 'Your first attempt falls apart. What happens next?',
  ['You choose a different goal.', 'You take a long pause before deciding.', 'You try again with some encouragement.', 'You learn from it and return tomorrow.', 'You rebuild the plan and keep going.']),
 ('courage', 'You notice something unfair in a crowded room. You…',
  ['Avoid getting involved.', 'Speak privately to someone afterward.', 'Support the person who speaks up.', 'Raise the issue calmly yourself.', 'Speak up immediately, even if you stand alone.']),
 ('empathy', 'Someone makes a mistake that affects you. You…',
  ['Focus on what they need to fix.', 'Hear a brief explanation, then move on.', 'Consider both your needs and theirs.', 'Try to understand what led to it.', 'Help them recover as well as repair the mistake.']),
 ('curiosity', 'You arrive in a city you have never visited. You…',
  ['Stay with familiar places and routines.', 'Visit one well-known spot.', 'Explore a couple of recommended streets.', 'Follow interesting side roads and questions.', 'Spend the day discovering its hidden stories.']),
 ('discipline', 'A project loses its initial excitement. You…',
  ['Move toward something more exciting.', 'Return when the mood comes back.', 'Do enough to keep it moving.', 'Keep your regular work sessions.', 'Finish each commitment, exciting or otherwise.']),
 ('independence', 'The group wants one ending; you imagine another. You…',
  ['Happily go with the group.', 'Share your idea but accept their choice.', 'Look for a middle path.', 'Make a case for your own ending.', 'Pursue your ending on your own if needed.']),
 ('creativity', 'You are given a blank notebook. It becomes…',
  ['A practical list of things to do.', 'A record of your days.', 'A mix of notes and occasional sketches.', 'A collection of ideas, scenes, and experiments.', 'An entire imaginary world.']),
 ('resilience', 'A goal takes longer than you expected. You…',
  ['Decide a new direction would suit you better.', 'Set it aside until circumstances improve.', 'Continue with help and smaller steps.', 'Adjust the timeline and keep working.', 'Stay committed through repeated setbacks.']),
]
EXTRA_ROWS = [
 ('courage', 'An unfamiliar opportunity could change your routine. What wins you over?',
  ['A guarantee that nothing important will change.', 'Watching others try it first.', 'A small trial with an easy way back.', 'A worthwhile risk after a little research.', 'The chance to do something you have never dared before.', 'Having a trusted partner for the first attempt.']),
 ('empathy', 'Two friends tell you opposite versions of the same argument. You…',
  ['Ask what practical outcome they need.', 'Hear the short version from each.', 'Make room for both points of view.', 'Ask what each person is feeling underneath it.', 'Help both feel understood before looking for a solution.', 'Give them space, then check in individually.']),
 ('curiosity', 'You find an old photograph with no names on it. You…',
  ['Put it back; the mystery can stay a mystery.', 'Wonder briefly, then move on.', 'Ask whether someone recognizes a face.', 'Trace the place and date from the clues.', 'Follow the story until you uncover its history.', 'Save it to investigate when you have time.']),
 ('discipline', 'A personal promise competes with a more exciting invitation. You…',
  ['Follow the new invitation.', 'Move the promise to another day.', 'Weigh the two and make a compromise.', 'Finish the essential part before going.', 'Keep the promise exactly as planned.', 'Set a smaller commitment you can still keep.']),
 ('independence', 'A mentor offers a route that does not feel like yours. You…',
  ['Trust their experience and follow it.', 'Try their route before questioning it.', 'Adapt it together.', 'Keep the useful parts and choose your own route.', 'Thank them, then build a different path.', 'Ask several people before deciding for yourself.']),
 ('sociability', 'You have an unexpected free afternoon. You…',
  ['Spend it entirely on your own.', 'Message one person you know well.', 'Invite a small familiar group.', 'Make plans with several friends.', 'Find an event where you can meet new people.', 'Join company for a while, then recharge alone.']),
 ('creativity', 'You must give an ordinary object a new use. You…',
  ['Use it for its most practical existing purpose.', 'Adjust it in one small, useful way.', 'Combine two familiar uses.', 'Try an unusual use and see what happens.', 'Turn it into something nobody would expect.', 'Sketch a few ideas, then pick a workable one.']),
 ('resilience', 'Progress has been slow for several weeks. You…',
  ['Choose a goal that suits you better now.', 'Pause until circumstances feel easier.', 'Restart with smaller steps and some support.', 'Change tactics and keep a steady pace.', 'Keep testing approaches despite the setbacks.', 'Take a short break, then return with a new plan.']),
 ('sociability', 'At the end of a group trip, what do you remember most?',
  ['The quiet moments you had to yourself.', 'One meaningful conversation.', 'Time with a few people you felt close to.', 'The laughter and shared activities.', 'All the new people you connected with.', 'The balance between company and personal space.']),
]

CHARACTER_ROWS = [
 ('courage', 'A teammate freezes when the plan suddenly changes. Your first instinct is to…',
  ['Wait for a clearer and safer opening.', 'Let a more experienced person take over.', 'Offer to act together so neither of you is alone.', 'Take the next sensible step yourself.', 'Step into the uncertainty and get everyone moving.', 'Observe for a moment, then make a small move.']),
 ('empathy', 'A rival admits they are struggling. What matters most to you?',
  ['Keeping the competition fair and focused.', 'Being polite while keeping your distance.', 'Understanding enough to respond fairly.', 'Listening without treating them as a rival for a moment.', 'Making sure they are supported, even if you gain nothing.', 'Offering a practical kind of help they can accept.']),
 ('curiosity', 'Your character discovers that an accepted story has a missing chapter. You…',
  ['Accept that some chapters are better left closed.', 'Keep the information in mind without pursuing it.', 'Check one reliable account.', 'Compare the accounts and look for a pattern.', 'Make uncovering the missing truth your new quest.', 'Ask a trusted expert before digging deeper.']),
 ('discipline', 'Your signature skill comes from…',
  ['Instinct and whatever feels right in the moment.', 'Occasional bursts of practice.', 'A flexible mix of practice and improvisation.', 'Regular practice, even on ordinary days.', 'A demanding routine you maintain without an audience.', 'Short, achievable sessions you fit around life.']),
 ('independence', 'The person you admire most disagrees with your decision. You…',
  ['Choose their judgment over your own.', 'Usually change your decision.', 'Try to find a position you both accept.', 'Consider their concern, then make your own choice.', 'Accept the disagreement and follow your own direction.', 'Seek one more perspective before deciding.']),
 ('sociability', 'In a new ensemble cast, your natural place is…',
  ['The person comfortable doing their own thing.', 'The quiet bond with one other character.', 'A dependable member of a small circle.', 'The person who keeps the group connected.', 'The person who can strike up a bond with almost anyone.', 'Someone who joins in but also needs quiet scenes.']),
 ('creativity', 'The obvious escape route is blocked. You look for…',
  ['The safest familiar route.', 'A proven route with one small adjustment.', 'A combination of familiar tools.', 'An overlooked possibility in the surroundings.', 'An entirely new way to use what is available.', 'Several sketches of possible routes before choosing.']),
 ('resilience', 'Your character loses something they worked hard for. The next chapter is…',
  ['A new direction with a different goal.', 'A long retreat before any return.', 'Recovery with help from someone close.', 'A return with a changed plan.', 'A determined rebuild after repeated setbacks.', 'A pause that becomes a measured fresh start.']),
 ('courage', 'When the cost of speaking up becomes personal, you…',
  ['Protect your safety and avoid the confrontation.', 'Look for someone else who can raise it.', 'Support a joint statement.', 'Say what needs saying after weighing the risk.', 'Say it even if you are the only voice.', 'Find a quieter opening that still lets you act.']),
 ('empathy', 'A companion hurts you while trying to help. You…',
  ['Focus on the damage and what must be repaired.', 'Acknowledge their intent briefly.', 'Consider intent and impact together.', 'Try to understand their feelings as well as your own.', 'Help them understand themselves while you repair the relationship.', 'Ask for space, then return to the conversation.']),
 ('curiosity', 'A mysterious stranger gives you one question. You ask about…',
  ['The practical information you need right now.', 'Something useful you have already wondered about.', 'A puzzle you might realistically solve.', 'The hidden reason behind an important event.', 'A question that could overturn everything you believe.', 'A clue you can investigate at your own pace.']),
 ('discipline', 'What would your closest companion say about your promises?',
  ['They change with your mood and circumstances.', 'You mean well but often get distracted.', 'You keep them when the balance feels right.', 'You can usually be counted on to follow through.', 'You keep them even through tedious, difficult work.', 'You are learning to make fewer, more achievable promises.']),
 ('independence', 'If your group takes a path you cannot believe in, you…',
  ['Stay with the group and trust the shared direction.', 'Put your doubts aside for now.', 'Search for a compromise you can share.', 'Make your own choice while keeping the bond.', 'Take a different path even if you must go alone.', 'Step back briefly and decide after reflection.']),
 ('sociability', 'How does your character recover after an intense scene?',
  ['Solitude and no conversation.', 'Quiet time with one trusted person.', 'A small gathering with familiar faces.', 'Talking things through with the whole group.', 'Meeting people and feeling the world move again.', 'A little conversation followed by time alone.']),
 ('creativity', 'Which kind of solution feels most like your signature?',
  ['A clear, reliable method executed well.', 'A useful improvement to an established method.', 'A clever combination of existing ideas.', 'An unusual approach others overlooked.', 'A surprising invention that changes the situation.', 'An idea that is imaginative but grounded in what works.']),
 ('resilience', 'The ending you hoped for becomes impossible. You…',
  ['Let that story close and choose something else.', 'Wait before making any new commitment.', 'Find a smaller hope with someone supporting you.', 'Build a new goal from what you learned.', 'Keep moving through grief and setbacks toward a changed future.', 'Allow yourself a pause, then begin again carefully.']),
 ('courage', 'When a strange journey begins, your comfort zone is…',
  ['Staying with what is safe and known.', 'Following a proven guide.', 'Exploring with a trusted companion.', 'Trying the unfamiliar after preparing.', 'Being first into territory nobody understands.', 'Testing one unfamiliar step before committing.']),
 ('empathy', 'Someone asks you to judge a character everyone dislikes. You…',
  ['Judge the actions and leave motives aside.', 'Consider one mitigating fact.', 'Weigh motives alongside consequences.', 'Want to understand the person behind the actions.', 'Make room for their pain while still recognizing the harm.', 'Withhold judgment until you hear their account.']),
 ('curiosity', 'Which small detail is most likely to pull you into a story?',
  ['A clear task with a useful outcome.', 'A familiar mystery with a likely answer.', 'A detail that does not quite fit.', 'A pattern that hints at a deeper explanation.', 'An unanswered question that opens a whole new world.', 'A conversation that gives you a fresh perspective.']),
 ('discipline', 'Nobody will know whether you complete a difficult task. You…',
  ['Do it only if the moment inspires you.', 'Work in short bursts when you remember.', 'Set a reasonable target and adapt it.', 'Keep working to the standard you chose.', 'Maintain the same commitment without recognition.', 'Break it into smaller promises you can finish.']),
 ('independence', 'What gives your character a sense of direction?',
  ['Belonging to a group with a shared path.', 'Advice from people who know more.', 'A balance of advice and personal judgment.', 'A decision you can stand behind yourself.', 'A vision you would follow without anyone approving.', 'Reflection and a few trusted outside perspectives.']),
 ('sociability', 'Your most memorable supporting role would be…',
  ['The solitary observer.', 'The confidant of one close companion.', 'The steady presence in a tight circle.', 'The connector who keeps friends together.', 'The welcoming energy that turns strangers into a group.', 'The thoughtful presence who joins in selectively.']),
 ('creativity', 'The script gives you an empty room and one scene. You create…',
  ['A simple scene that does its job clearly.', 'A familiar scene with a useful twist.', 'A thoughtful blend of two known ideas.', 'An unexpected scene with a fresh point of view.', 'A new world that makes the empty room feel limitless.', 'A few experimental sketches before settling on a scene.']),
 ('resilience', 'What kind of second act fits your character best?',
  ['A clean break from an unsuitable goal.', 'Time away before choosing what comes next.', 'A return made possible by loyal support.', 'A patient comeback built from lessons.', 'A sustained fight through repeated disappointments.', 'A quieter restart with room for recovery.']),
]

import hashlib
import random
from uuid import UUID

VERSIONS = {'story': VERSION, 'character': CHARACTER_VERSION}


def make_bank(rows, prefix):
    result = []
    # Contextual primary traits keep scoring interpretable. The sixth choice is
    # deliberately moderate; options are shuffled per session, never low-to-high.
    values = (0, 1, 2, 3, 4, 2)
    for i, (trait, prompt, options) in enumerate(rows):
        result.append({'id': f'{prefix}{i+1}', 'trait': trait, 'text': prompt,
            'options': [{'id': j, 'text': option, 'value': values[j]} for j, option in enumerate(options)]})
    return result


BANKS = {'story': make_bank(ROWS + EXTRA_ROWS, 's'), 'character': make_bank(CHARACTER_ROWS, 'c')}
VALUE_OPTIONS = [
 ('Protecting the people who depend on me.', 'care'),
 ('Having the freedom to choose my own path.', 'freedom'),
 ('Putting something unfair right.', 'justice'),
 ('Discovering a truth or a world nobody knows.', 'discovery'),
 ('Finding people and a place where I belong.', 'belonging'),
 ('Creating something that did not exist before.', 'creation'),
 ('Making amends and earning a new beginning.', 'redemption'),
 ('Achieving a difficult goal and proving my ability.', 'achievement'),
]
VALUE_PROMPTS = {
 'story': ['Which theme would you most want at the heart of your own story?',
           'At a turning point, which purpose would make the difficult choice worthwhile?',
           'What would make your story’s ending feel meaningful?'],
 'character': ['What would keep your character moving when the journey gets difficult?',
               'Which personal purpose would you be least willing to give up?',
               'What would you want your character to stand for?'],
}
for mode, prompts in VALUE_PROMPTS.items():
    for i, prompt in enumerate(prompts):
        BANKS[mode].append({'id':f'{mode[0]}v{i+1}', 'trait':'empathy', 'kind':'values', 'text':prompt,
            'options':[{'id':j, 'text':label, 'value':2, 'theme':theme} for j,(label,theme) in enumerate(VALUE_OPTIONS)]})
QUESTIONS = BANKS['story']  # Versioned question bank, not a fixed repeated sequence.


def select_questions(mode, seed):
    UUID(str(seed))
    bank = BANKS[mode]
    rng = random.Random(hashlib.sha256(f'{VERSIONS[mode]}:{seed}'.encode()).digest())
    ordinary = [q for q in bank if q.get('kind') != 'values']
    selected = [rng.choice([q for q in ordinary if q['trait'] == trait]) for trait in TRAITS]
    selected += rng.sample([q for q in bank if q.get('kind') == 'values'], 2)
    ids = {q['id'] for q in selected}
    selected += rng.sample([q for q in ordinary if q['id'] not in ids], 15-len(selected))
    rng.shuffle(selected)
    questions = []
    for original in selected:
        question = dict(original, options=[dict(o) for o in original['options']])
        rng.shuffle(question['options'])
        questions.append(question)
    return questions


def public_questions(questions):
    return [dict(q, options=[{'id': o['id'], 'text': o['text']} for o in q['options']]) for q in questions]


def answer_option(question, answer):
    return next(o for o in question['options'] if o['id'] == answer)


def validate_answers(answers, questions):
    return set(answers) == {q['id'] for q in questions} and all(
        any(o['id'] == answers[q['id']] for o in q['options']) for q in questions)


def profile(answers, questions):
    buckets = {trait: [] for trait in TRAITS}
    for question in questions:
        if question.get('kind') == 'values':
            continue
        buckets[question['trait']].append(answer_option(question, answers[question['id']])['value'] / 4)
    return {trait: sum(values) / len(values) for trait, values in buckets.items()}
