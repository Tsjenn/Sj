A prompt is a briefing, not a spell. None of the forty prompts below will do much for you if you paste one, take whatever comes back and put your name on it. They are written on the assumption that you already know something the model does not: what your entity does, which numbers matter this period, what your reviewer will ask, and what the consequences are if the answer is wrong. The prompt's job is to get that knowledge out of your head and in front of the model in an orderly way. Your job is everything after.

Three things are worth changing in almost every prompt here. First, the role line — replace the generic description with the specific one that fits your situation, because "you are assisting a finance team in a group with several overseas subsidiaries and a manual consolidation" produces different work from "you are assisting a finance team". Second, the constraints — add your house rules, your materiality thresholds, your naming conventions, anything a new joiner would get wrong. Third, the output format — make it match the document the output actually has to feed, so you are pasting into a template rather than reformatting by hand.

Two things are worth leaving alone. The instruction to mark uncertainty and refuse to guess: take it out and you get confident-sounding filler, which is the single most expensive failure mode in this work. And the instruction not to invent figures. Before any of that, though, settle a separate question: whether you are allowed to put this particular information into this particular tool. Client data, staff data, unpublished results and anything under a confidentiality obligation are decisions for whoever owns that policy in your organisation, not for you at your desk on a Tuesday. If nobody has decided, assume the answer is no until they do.

| Change this | Keep this |
|---|---|
| The role line, so it matches your entity and sector | The uncertainty rule and the refusal to guess |
| The constraints, so they carry your house rules | The ban on inventing figures |
| The output format, so it fits your template | The instruction to list what it could not determine |
| The placeholders in square brackets | The request to show its reasoning where judgement was used |

## 1. Month-end close and reconciliations

**P1.1 — Reconciliation break triage**
*Use when:* you have a list of unexplained differences and limited time before close.
*Paste this:*
```
You are assisting a finance team during month-end close. I will give you
a list of reconciling items from [ACCOUNT NAME] for [PERIOD].

Task: sort them into groups by the most likely underlying cause, and for
each group tell me what evidence would confirm or rule out that cause.

Constraints: do not estimate, extrapolate or invent any amount, date or
counterparty. Use only what is in the list I paste. Where an item could
belong to more than one group, say so rather than picking one.

Format: a table with columns Item reference, Amount as given, Likely
cause, Evidence that would confirm it, Who to ask. Below the table, a
short list headed "Cannot classify from this information" with the
reason for each.

If you are unsure about an item, put it in the cannot-classify list. Do
not guess.

Here is the list:
[PASTE LIST]
```
*Check before you use the output:* the groupings are guesses dressed as categories — confirm each cause against the source document before you act on it, and watch for items it quietly assigned to a cause because they resembled the item above.

**P1.2 — Break explanation, written up**
*Use when:* you have worked out why a difference exists and now have to write it down for the file.
*Paste this:*
```
You are helping a qualified accountant write a file note. I will describe
in rough terms why a reconciling difference on [ACCOUNT NAME] for
[PERIOD] arose, and what I did about it.

Task: turn my notes into a clear file note that another accountant could
follow in a year's time without asking me questions.

Constraints: use only the facts in my notes. Do not add causes,
amounts, dates, control references or conclusions I have not given you.
Do not soften or strengthen my conclusion. British English, plain
sentences, no adjectives of reassurance.

Format: four short paragraphs — what the difference was, why it arose,
what was done, what remains open. Under 300 words.

If my notes leave a gap that a reader would trip over, do not fill it.
List the gaps at the end under "Questions I could not answer from your
notes".

My notes:
[PASTE NOTES]
```
*Check before you use the output:* the "what remains open" paragraph — models tend to tidy loose ends into resolutions. If you left something unresolved, make sure the note still says so.

**P1.3 — Close checklist builder**
*Use when:* your close runs on memory and one person's spreadsheet.
*Paste this:*
```
You are helping a finance team document its month-end close.

Context: I will describe the tasks we perform, roughly in order, in my
own words. Our team is [NUMBER] people. The close runs from working day
[X] to working day [Y].

Task: turn this into a close checklist that could be handed to someone
who has not run our close before.

Constraints: include only tasks I have described. Do not add standard
tasks you assume we perform — instead list them separately as
suggestions I can accept or reject. Do not assign deadlines I have not
given you.

Format: a table with columns Working day, Task, Owner, Depends on,
Evidence retained. Then a separate list headed "Tasks you did not
mention that teams often include — confirm whether these apply to you".

Where my description is ambiguous about sequence or ownership, mark the
cell "UNCLEAR" rather than choosing.

My description:
[PASTE DESCRIPTION]
```
*Check before you use the output:* the dependency column. A checklist that puts a task before the thing it depends on is worse than no checklist, and this is the field most often filled in by pattern rather than logic.

**P1.4 — Intercompany mismatch investigation plan**
*Use when:* two entities disagree and you need a plan before the calls start.
*Paste this:*
```
You are assisting a group finance team. Two entities, [ENTITY A] and
[ENTITY B], disagree on the intercompany balance for [PERIOD]. I will
describe what each side reports and what I already know.

Task: produce an investigation plan — the order in which to test possible
causes, cheapest and most likely first.

Constraints: work only from what I tell you. Do not assume our systems,
our currencies, our cut-off conventions or our transfer pricing
arrangements. Do not calculate a difference I have not given you.

Format: numbered steps. Each step states what to check, what result
would confirm the cause, and what to do next if it does not.

At the end, list under "Assumptions I had to make" anything you took as
given that I did not actually state. If you cannot form a plan without
information I have not provided, say what you need instead.

Situation:
[PASTE SITUATION]
```
*Check before you use the output:* the assumptions list, and then the steps that rely on those assumptions. Currency and cut-off conventions are the two it will invent most readily.

**P1.5 — Accrual and prepayment review questions**
*Use when:* you are reviewing someone else's schedule and want a second pair of eyes on what to ask.
*Paste this:*
```
You are acting as a reviewer of a schedule of accruals and prepayments
for [ENTITY], [PERIOD]. I will paste the schedule as text.

Task: produce the questions a careful reviewer would ask about this
schedule. Focus on what would be wrong if the preparer had been rushing.

Constraints: do not recalculate anything and do not tell me any figure
is wrong — you cannot see the supporting evidence. Ask questions
instead. Do not reference any accounting standard by number or name;
if a point turns on a recognition question, describe it in plain words
and mark it "judgement — confirm with your own reference sources".

Format: questions grouped under Completeness, Cut-off, Basis of
estimate, Reversal and follow-through. Maximum 20 questions, ordered by
how much money is likely to turn on them.

Where the schedule does not give you enough to form a question, say so
rather than asking a generic one.

Schedule:
[PASTE SCHEDULE]
```
*Check before you use the output:* whether the questions are actually specific to your schedule. Generic review questions are a sign it did not have enough context, and they will waste your preparer's afternoon.

## 2. Variance analysis and management commentary

**P2.1 — First-pass variance question list**
*Use when:* the variance report has landed and you have not yet spoken to the business.
*Paste this:*
```
You are assisting a financial controller preparing to investigate
variances for [ENTITY], [PERIOD]. I will paste a variance table showing
actual, budget or prior period, and the difference.

Task: for each line I flag, list the specific questions I should put to
the budget holder — the ones that would distinguish between a timing
difference, a volume difference, a price or rate difference, a
misposting, and a genuine change in the business.

Constraints: do not explain the variances yourself. You do not know our
business. Do not calculate percentages or restate my figures. Do not
speculate about causes in the wording of the questions.

Format: for each flagged line, the account name and then between three
and six questions as bullets.

If a line is too small or too ambiguous to be worth a conversation, say
so and move on.

Variance table:
[PASTE TABLE]
```
*Check before you use the output:* that it has not smuggled a presumed cause into a question ("why did headcount costs rise due to the new hires?"). Leading questions get you the answer you suggested, not the one that is true.

**P2.2 — Commentary drafted from your explanations**
*Use when:* you know the reasons and need them written up for the pack.
*Paste this:*
```
You are drafting management commentary for [ENTITY], [PERIOD], for an
audience of [AUDIENCE].

I will give you, for each variance: the account, the figure, and the
explanation I have obtained from the business. That explanation is the
only permitted source of cause.

Task: write the commentary.

Constraints: every stated cause must come from my notes. Do not add
context, market conditions, industry trends or forward-looking
statements. Do not add any figure that is not in my notes. Do not use
the words "significant", "material", "strong" or "challenging". Do not
tell the reader how to feel about the result. British English.

Format: one short paragraph per variance, ordered by size of difference,
each beginning with the account name in bold. Maximum [WORD LIMIT] words
in total.

If an explanation I gave you does not actually account for the movement
described, flag it at the end under "Explanations that do not fully
account for the movement" rather than writing around it.

My notes:
[PASTE NOTES]
```
*Check before you use the output:* the flagged list at the end, then every causal word in the body — "because", "driven by", "reflecting". Each one has to trace back to something a named person actually told you.

**P2.3 — The walk from last period to this**
*Use when:* you need a bridge narrative that a reader can follow without the chart.
*Paste this:*
```
You are helping a finance team explain a movement in [MEASURE] from
[PRIOR PERIOD] to [CURRENT PERIOD] for [ENTITY].

I will give you the opening figure, the closing figure, and the
components of the movement with their amounts and my explanation of
each.

Task: write the bridge as prose, in the order that makes the story
clearest, not necessarily the order I listed.

Constraints: the components must sum to the movement as I have given
them — if they do not, stop and tell me the difference rather than
adjusting anything or inserting a balancing item. Add no components of
your own. No causes beyond mine.

Format: a short lead sentence stating the movement, then one sentence
per component, then a closing sentence on what it means for the next
period only if I have told you what that is.

State plainly if you cannot reconcile my components to my movement.

Inputs:
[PASTE INPUTS]
```
*Check before you use the output:* whether it reported a failure to reconcile. If it produced a smooth narrative and your components do not add up, it has hidden your error inside good prose.

**P2.4 — De-waffling a draft**
*Use when:* the commentary is written but reads like a press release.
*Paste this:*
```
You are an unsentimental editor of finance writing. I will paste a draft
of management commentary.

Task: rewrite it so that every sentence carries information. Cut hedging,
cut throat-clearing, cut adjectives that assert rather than describe.

Constraints: do not change any figure, any cause or any conclusion. Do
not add facts. If cutting a sentence would remove a fact, keep the fact
and cut the decoration around it. British English. Preserve any wording
I have marked [DO NOT CHANGE].

Format: the rewritten text first. Then a short list of sentences you
could not tighten because they contained a claim you could not verify
from the draft itself — these are the ones I need to check.

Do not invent a stronger version of a weak claim. If a sentence asserts
something without support, leave it and flag it.

Draft:
[PASTE DRAFT]
```
*Check before you use the output:* the flagged list, and a line-by-line comparison of figures. Editors of all kinds have a habit of rounding numbers to make a sentence sit better.

**P2.5 — Attack my explanation**
*Use when:* you are about to present a reason and want it tested first.
*Paste this:*
```
You are playing the role of a sceptical audit committee member with a
finance background. I will give you my explanation for a movement in
[MEASURE] at [ENTITY] for [PERIOD].

Task: attack it. Find the questions that would expose it if it were
wrong, incomplete, or an artefact of how the numbers were prepared.

Constraints: do not propose alternative explanations as though they were
facts, and do not invent figures to support a challenge. Frame every
challenge as a question I can go and answer. Assume I am competent and
sceptical of you too.

Format: challenges in three groups — Does the cause explain the size of
the movement, Does it explain the timing, and Is there a simpler
explanation. Maximum ten challenges, hardest first.

If my explanation is internally consistent and you cannot fault it on
the information given, say so plainly instead of manufacturing
objections.

My explanation:
[PASTE EXPLANATION]
```
*Check before you use the output:* whether the challenges are answerable. A challenge you cannot resolve with evidence you can obtain is not useful before a meeting; park it and deal with the ones you can.

## 3. Budgeting and forecasting

**P3.1 — Assumption map for a budget line**
*Use when:* a budget line has become a single number nobody can defend.
*Paste this:*
```
You are helping a finance team make its budget assumptions explicit for
[BUDGET LINE] at [ENTITY] for [PERIOD].

Task: break the line down into the drivers that would have to be
estimated to build it up from scratch, and for each driver state what
source inside a business would normally hold the answer.

Constraints: give no values, ranges, percentages or benchmarks. Not one
number. You do not know our business, our sector or our size. Where a
driver depends on a decision rather than a fact, mark it "decision
required" and say whose decision it is.

Format: a table with columns Driver, Unit, Type (fact / estimate /
decision), Where the answer lives, Question to ask.

If the line could be built up in more than one sensible way, show the
two most common structures and say what would make one preferable.
```
*Check before you use the output:* that the drivers actually multiply or add up to your line. A tidy driver list that does not reconstruct the number is decoration.

**P3.2 — Budget holder briefing**
*Use when:* you are sending the budget pack to non-finance managers.
*Paste this:*
```
You are helping a finance team brief non-financial managers who must
submit budget figures for [PERIOD].

Context: their cost lines are [LIST LINES]. The submission deadline is
[DATE]. Common problems last cycle were [LIST PROBLEMS].

Task: write the briefing note that goes out with the template.

Constraints: no finance jargon without a plain-English gloss on first
use. No threats and no cheerleading. Do not state any figure, limit or
target — I will insert those. Do not promise what finance will do with
the numbers beyond what I have told you.

Format: a short opening on what we need and when, a numbered list of
what to submit, a numbered list of what not to do, and a closing line
on who to contact. Under 500 words.

Leave a clearly marked [ ] placeholder wherever a figure, limit or name
is required rather than supplying one.
```
*Check before you use the output:* every placeholder is still empty. If it has helpfully filled one in with a plausible-looking number, that number will end up in a manager's spreadsheet.

**P3.3 — Forecast assumption challenge**
*Use when:* the forecast is built and you want the weak joints found.
*Paste this:*
```
You are reviewing the assumption set behind a forecast for [ENTITY],
covering [PERIOD]. I will paste the assumptions as a list, with values.

Task: identify which assumptions the outcome is most sensitive to, which
are internally inconsistent with each other, and which are stated so
vaguely that they cannot be tested later.

Constraints: do not tell me an assumption is too high or too low — you
have no basis for that and I will not accept it. Restrict yourself to
sensitivity, internal consistency and testability. Do not compute
revised outcomes.

Format: three sections — Most sensitive, Mutually inconsistent, Not
testable as written. In each, name the assumption and say precisely
what the problem is.

Where two assumptions appear inconsistent but might be reconciled by
something I have not told you, phrase it as a question.

Assumptions:
[PASTE ASSUMPTIONS]
```
*Check before you use the output:* the sensitivity claims. Without your model it is reasoning from structure alone, so treat "most sensitive" as a list to test, not a finding.

**P3.4 — Scenario definitions, without numbers**
*Use when:* you have been asked for scenarios and want them defined before anyone models them.
*Paste this:*
```
You are helping a finance team define scenarios for [ENTITY] over
[PERIOD]. I will describe the business and the uncertainties that
actually worry management.

Task: define [NUMBER] scenarios. Each is a coherent story about the
world, not a percentage applied to a base case.

Constraints: no numbers, no probabilities, no likelihoods. Each scenario
must state which of my named uncertainties resolve which way, and the
consequences must be internally consistent — if demand falls in a
scenario, do not also assume prices hold unless you say why. Use only
the uncertainties I give you.

Format: for each scenario — a name, a one-paragraph description, a
bulleted list of which assumptions move and in which direction, and one
line on the earliest observable sign that this scenario is happening.

If two of my uncertainties cannot both be varied independently, say so.

The business and the uncertainties:
[PASTE DESCRIPTION]
```
*Check before you use the output:* the early-warning signs. They are the part of a scenario set that gets used, and the part most likely to be written as a platitude.

**P3.5 — Budget submission review**
*Use when:* submissions are in and you must review many quickly.
*Paste this:*
```
You are performing a first-pass review of a budget submission from
[DEPARTMENT] for [PERIOD]. I will paste the submission and, separately,
our submission rules.

Task: check the submission against the rules only. List every point of
non-compliance, and every place where a required explanation is missing
or is too vague to be an explanation.

Constraints: do not assess whether the figures are reasonable. That is
my job and you lack the context. Do not compare to prior year unless I
have given you prior year. Quote the exact wording from the submission
when you flag it.

Format: a table with columns Rule, What the submission says, Problem,
What to request. Then a one-line overall statement — ready for review,
or return to sender.

If a rule is ambiguous as written, flag the rule itself rather than
guessing which reading applies.

Rules:
[PASTE RULES]

Submission:
[PASTE SUBMISSION]
```
*Check before you use the output:* the quoted wording. If a quotation does not appear verbatim in the submission, treat the whole review as unreliable and run it again.

## 4. Audit and assurance support

**P4.1 — Making sense of a request list**
*Use when:* the audit request list has arrived and you need to allocate work.
*Paste this:*
```
You are helping a finance team plan its response to an auditor's
information request list for [ENTITY], [PERIOD]. I will paste the list.

Task: for each item, state in plain words what the auditor is likely to
be trying to establish, what document or extract would satisfy it, and
which of my team roles would normally hold it.

Constraints: this is general information about how such requests are
usually framed, not advice on what any standard or regulator requires.
Say that plainly at the top of your output. Do not cite any standard,
regulation or professional pronouncement. Do not tell me an item is
unnecessary or can be refused.

Format: a table with columns Request, Likely purpose, Document to
provide, Owner, Effort (low / medium / high).

Where you cannot tell what is being asked for, write "ask the audit team
to clarify" rather than guessing.

Request list:
[PASTE LIST]
```
*Check before you use the output:* the "likely purpose" column. It is inference, and if you send documents based on a wrong inference you will do the work twice.

**P4.2 — Drafting a response to an audit query**
*Use when:* you have the facts and need the reply written cleanly.
*Paste this:*
```
You are helping a qualified accountant respond to an audit query on
[TOPIC] for [ENTITY], [PERIOD]. I will give you the query and the facts
and documents we hold.

Task: draft the response.

Constraints: use only the facts I supply. Do not assert that a treatment
is correct, compliant or in accordance with anything — state what was
done and why we did it, and let the auditor form their view. Do not
name any standard, regulation or authority. Do not commit us to anything
I have not said we will do. Neutral tone, no defensiveness.

Format: a short statement of our position, then the facts in order, then
a list of the documents attached, then any point we accept remains a
matter of judgement.

If the facts I have given you do not fully answer the query, say what is
missing at the end instead of writing around the gap.

Query and facts:
[PASTE]
```
*Check before you use the output:* any sentence that asserts compliance. Delete it and replace it with what you actually did. Your position is what happened, not a claim about the rules.

**P4.3 — Control description write-up**
*Use when:* a control exists in practice but has never been written down.
*Paste this:*
```
You are documenting an internal control for [ENTITY]. I will describe
what actually happens, in my own words, including the parts that are
informal.

Task: write the control description.

Constraints: describe only what I have told you happens, including the
weaknesses. Do not write the control as it ought to be. Do not add
frequency, thresholds, approvers or evidence that I have not stated. Do
not reference any control framework by name. Do not use the word
"ensures" — say what the control does and what it would catch.

Format: What the control is, Who performs it, When and how often, What
evidence it leaves, What it would catch, What it would not catch.

The last section is the important one. If my description does not let
you complete it honestly, say so and ask me the questions that would.

What happens:
[PASTE DESCRIPTION]
```
*Check before you use the output:* the "what it would not catch" section. If it is short or reassuring, it is wrong — that section is the reason for writing the description at all.

**P4.4 — Walkthrough interview questions**
*Use when:* you are about to sit with a process owner and trace a transaction.
*Paste this:*
```
You are preparing an interview plan for a walkthrough of the [PROCESS]
process at [ENTITY]. I will describe what we believe the process is.

Task: write the questions to ask the person who actually performs it,
designed to reveal where the documented process and the real one differ.

Constraints: open questions only — nothing answerable with yes. Do not
ask questions that presume the process is being followed. Do not assess
anything; you are writing questions, not conclusions. No framework or
standard references.

Format: questions in the order the transaction flows, each with a
one-line note on what a concerning answer would sound like.

Add a final group headed "Questions to ask if they seem to be describing
the manual rather than their day", with the questions that usually
surface workarounds.

Believed process:
[PASTE DESCRIPTION]
```
*Check before you use the output:* that the questions do not read as an interrogation. You want a description of reality, and people stop giving you one the moment they feel tested.

**P4.5 — Evidence gaps in a testing plan**
*Use when:* you have drafted a testing approach and want the holes found.
*Paste this:*
```
You are reviewing a draft testing approach for [AREA] at [ENTITY],
[PERIOD]. I will paste the approach, including what we intend to test,
how, and over what population.

Task: identify where the evidence obtained would not actually support
the conclusion drawn — gaps between what the test proves and what the
approach claims it proves.

Constraints: this is a logical review, not a professional or regulatory
one. State that at the top. Do not tell me whether the approach meets
any standard, and do not name one. Do not propose sample sizes or
statistical parameters. Do not assume facts about our population that I
have not given you.

Format: for each gap — What the test does, What conclusion is drawn,
Why the first does not support the second, What additional evidence
would close it.

If the approach is sound as far as you can tell from the information
given, say so and say what information you would need to be more
confident.

Approach:
[PASTE APPROACH]
```
*Check before you use the output:* whether it stayed inside logic. The moment it starts telling you what is required, it has left the territory it can be trusted in.

## 5. Tax and compliance preparation

Everything in this group is preparation. None of it is advice, and none of the outputs should reach a filing without a qualified person in your jurisdiction reviewing it. Tax rules differ by country, differ within countries, and change — often with effect from a date that has already passed by the time you read about it. Use these prompts to get organised, not to reach conclusions.

**P5.1 — Information gathering checklist**
*Use when:* a filing or return is coming and the documents are scattered.
*Paste this:*
```
You are helping a finance team organise itself before a [FILING TYPE]
for [ENTITY] covering [PERIOD]. I will list the activities the entity
carried out during the period.

Task: produce a checklist of the documents and records the team should
gather and have ready for whoever prepares the filing.

Constraints: this is a document-gathering aid and general information
only, not tax advice. Rules differ by jurisdiction and change; I will
have this reviewed by a qualified adviser in my jurisdiction. Do not
state what is deductible, taxable, claimable or reportable. Do not
reference any tax law, section, regulator or filing form. Do not assume
my jurisdiction.

Format: a table with columns Activity, Records to gather, Where they
usually live, Owner, Status.

Where an activity's treatment plainly depends on local rules, write
"jurisdiction-dependent — for your adviser" in place of any conclusion.

Activities:
[PASTE LIST]
```
*Check before you use the output:* that nothing in it has drifted from "gather this" to "this is treated as". Strike any line that states a treatment.

**P5.2 — Categorisation queries**
*Use when:* you are cleaning a transaction listing before it goes to an adviser.
*Paste this:*
```
You are helping prepare a transaction listing for [ENTITY], [PERIOD],
before it is sent to our tax adviser. I will paste the listing with
descriptions and amounts.

Task: identify the transactions whose description is too vague, too
generic or too inconsistent for someone else to categorise, and write
the question we need to put to the person who incurred them.

Constraints: do not categorise anything yourself and do not state any
tax treatment. This is preparation, not advice. Do not change or
recalculate any amount. Do not infer a purpose from a supplier name.

Format: a table with columns Reference, Description as given, Why it is
unclear, Question to ask, Who to ask.

Where a description is adequate, leave it out. A short list is a good
outcome.

Listing:
[PASTE LISTING]
```
*Check before you use the output:* whether it has inferred purpose from vendor names. "Software supplier, therefore software cost" is exactly the kind of assumption that later needs unwinding.

**P5.3 — Understanding a letter you have received**
*Use when:* correspondence has arrived and you need to know what is being asked before you panic.
*Paste this:*
```
You are helping a finance professional understand a piece of
correspondence. I will paste the text of a letter received by [ENTITY].

Task: tell me, in plain words, what the letter appears to ask for, what
it appears to require by when, and what it does not say.

Constraints: this is a reading aid and general information only. It is
not legal or tax advice, rules and procedures differ by jurisdiction and
change, and I must confirm my position with a qualified adviser. Do not
tell me how to respond, whether the position stated is correct, or what
my rights or obligations are. Do not name any law, regulator or
authority. Work only from the words in the letter.

Format: three sections — What it asks for, Dates and deadlines it
states, What is unclear or unstated.

If a passage is ambiguous, quote it and say so rather than resolving it.

Letter:
[PASTE TEXT]
```
*Check before you use the output:* the deadlines, against the letter itself, word for word. A misread date is the one error here with an irreversible consequence.

**P5.4 — Questions for your adviser**
*Use when:* you have adviser time booked and want to use it well.
*Paste this:*
```
You are helping a finance team prepare for a meeting with its tax
adviser about [TOPIC] at [ENTITY]. I will describe our situation and
what we already know.

Task: write the questions we should ask, ordered so that the answers
build on each other, and note for each what documents we should have to
hand when we ask it.

Constraints: do not answer any of the questions. Do not indicate what
the likely answer is, and do not state any rule or treatment. This is
meeting preparation only, not advice; rules differ by jurisdiction and
change.

Format: numbered questions, each with a sub-line "Bring:" listing the
documents.

Add a final section, "Things we should tell them without being asked",
for facts in my description that an adviser would want to know early.

Our situation:
[PASTE DESCRIPTION]
```
*Check before you use the output:* the final section. It is the most valuable part and the easiest to get wrong, because it depends on facts you may not have mentioned.

**P5.5 — Obligations calendar**
*Use when:* deadlines live in several people's heads.
*Paste this:*
```
You are helping a finance team build an internal compliance calendar for
[ENTITY]. I will list the obligations we know we have, with the
deadlines as we understand them.

Task: turn my list into a working calendar, with the internal
preparation milestones that have to happen before each external
deadline.

Constraints: use only the obligations and dates I give you. Do not add
obligations you assume apply to us, and do not correct my dates — you do
not know my jurisdiction and requirements change. Where you think I may
have omitted something common, put it in a separate list of questions,
phrased as questions.

Format: a table with columns External deadline, Obligation, Internal
milestone, Days before, Owner. Sorted by date.

Add a line at the top stating that the dates come from me and must be
confirmed against our own sources each year.

Obligations:
[PASTE LIST]
```
*Check before you use the output:* that no deadline has been silently adjusted, and that no obligation has appeared that you did not list.

## 6. Contracts, agreements and policy documents

Reading a contract for its finance consequences is not the same as advising on it. These prompts extract and organise. They do not interpret, and nothing here replaces your legal adviser.

**P6.1 — Finance summary of an agreement**
*Use when:* a signed agreement lands on your desk and you need to know what it does to your numbers.
*Paste this:*
```
You are helping a finance team understand the financial mechanics of an
agreement. I will paste the text of an agreement involving [ENTITY].

Task: summarise only the provisions that affect money moving, timing, or
what has to be recorded and tracked.

Constraints: this is a reading aid, not legal advice; I will have legal
questions reviewed by a qualified adviser, and law differs by
jurisdiction. Quote the clause reference and the operative wording for
every point you make. Do not interpret ambiguous drafting — flag it. Do
not state the accounting treatment. Do not summarise clauses you were
not given.

Format: sections for Amounts payable or receivable, Timing and triggers,
Variation and escalation mechanisms, Termination and its financial
consequences, Anything creating an ongoing obligation to track.

End with "Clauses I could not interpret with confidence", quoting each.

Agreement:
[PASTE TEXT]
```
*Check before you use the output:* every quoted clause reference against the document. Quotation is the one thing you can verify quickly, and if the references drift, nothing else in the summary is safe.

**P6.2 — Payment terms extraction**
*Use when:* you are loading terms into a system or comparing across a portfolio.
*Paste this:*
```
You are extracting data from a contract for [ENTITY]. I will paste the
text.

Task: extract the payment terms into a structured table for entry into
our systems.

Constraints: extract only. Do not interpret, do not normalise into
categories of your own, and do not fill an empty field with what is
usual. Every value must appear in the text; give the clause reference
for each. If a field is not addressed in the contract, write "not
stated" — never a default.

Format: a table with columns Field, Value, Clause reference. Fields:
currency, amount basis, invoicing frequency, payment period, late
payment consequence, price adjustment mechanism, discount or rebate
terms, expenses treatment, disputed amounts.

Below the table, list any provision that affects payment but did not fit
these fields.

Contract:
[PASTE TEXT]
```
*Check before you use the output:* every "not stated" and every populated field with an odd clause reference. Extraction failures cluster in documents with unusual numbering.

**P6.3 — Obligations and dates register**
*Use when:* the contract creates things somebody must remember to do.
*Paste this:*
```
You are building an obligations register from an agreement involving
[ENTITY]. I will paste the text.

Task: list every obligation that falls on us, every deadline, notice
period and renewal or expiry date, and every condition that triggers
one.

Constraints: quote the clause reference and the wording for each entry.
Do not calculate a date unless the contract states the reference point
and the period, and where you do calculate one, show the working.
Do not list obligations that fall on the other party unless they trigger
one of ours. Do not interpret conditional wording — quote it.

Format: a table with columns Obligation, Owner function, Trigger or
date, Notice period, Clause, Wording quoted.

Flag separately any obligation whose trigger you could not determine
from the text.

Agreement:
[PASTE TEXT]
```
*Check before you use the output:* any calculated date. Notice periods interact with definitions of business days and month-ends, and that is where the arithmetic quietly goes wrong.

**P6.4 — Questions for legal review**
*Use when:* you have limited legal budget and want it spent on the right clauses.
*Paste this:*
```
You are helping a finance team prepare for legal review of a draft
agreement involving [ENTITY]. I will paste the draft and describe the
commercial deal we believe we have agreed.

Task: identify where the drafting and my description of the deal do not
obviously match, and write the questions to put to our legal adviser.

Constraints: do not give legal advice, do not state what any clause
means as a matter of law, and do not say whether a term is standard or
reasonable. Law differs by jurisdiction and changes. Confine yourself
to: this is what you said the deal is, this is what the words say, here
is the question.

Format: a table with columns Commercial expectation, Clause and wording,
The mismatch, Question for counsel. Ordered by financial exposure as I
have described it.

If the drafting matches my description, say so for that point rather
than inventing a concern.

The deal, then the draft:
[PASTE]
```
*Check before you use the output:* that the "commercial expectation" column reflects what you actually said, not a tidier version of it.

**P6.5 — Internal policy drafting**
*Use when:* you need a policy document that people will actually follow.
*Paste this:*
```
You are drafting an internal [POLICY TYPE] policy for [ENTITY]. I will
tell you the rules we have decided, the limits we have set, and the
behaviour we are trying to change.

Task: write the policy.

Constraints: include only rules I have given you. Do not add limits,
thresholds, approval levels or exceptions of your own — if you think one
is missing, list it as a question at the end. Do not reference any law
or regulation; where a rule exists because of an external requirement, I
will add that myself. Write for someone who will read it once, in a
hurry. British English. No sentence longer than 25 words.

Format: Purpose, Who it applies to, The rules as numbered clauses, What
to do if the rules do not cover your situation, Who owns this policy.

End with "Decisions you have not made yet" listing the gaps.

Our decisions:
[PASTE]
```
*Check before you use the output:* the gaps list, before circulating anything. A policy with an unmade decision inside it will be tested by the first person who finds the gap.

## 7. Board papers, reports and written communication

**P7.1 — Board paper structure**
*Use when:* you know what you need to say and not yet how to arrange it.
*Paste this:*
```
You are helping a finance director structure a board paper on [TOPIC]
for [ENTITY]. I will tell you the decision or noting item required, what
the board already knows, and the facts I hold.

Task: propose the structure — sections, what belongs in each, and
roughly how long each should be.

Constraints: structure only. Do not draft the content, do not supply
facts, and do not suggest a recommendation. Assume the board has limited
time and will read the first page properly and the rest selectively.

Format: a numbered outline. For each section: purpose in one line, what
goes in it, target length, and whether it belongs in the paper or an
appendix.

At the end, list under "Facts you will need that you have not mentioned"
the gaps a board would notice — as questions, not assumptions.

Background:
[PASTE]
```
*Check before you use the output:* the gaps list against your own knowledge. It is the closest thing here to a rehearsal for the meeting.

**P7.2 — One page from twenty**
*Use when:* the paper is written and the summary is due.
*Paste this:*
```
You are writing the executive summary of a paper I will paste. The
audience is [AUDIENCE] and the decision required is [DECISION].

Task: write a summary of no more than one page.

Constraints: every statement must appear in the paper. Add nothing. If
the paper contains a qualification on a key point, the qualification
must survive into the summary — do not simplify a hedged conclusion into
a firm one. Do not change any figure. Do not add a recommendation the
paper does not make.

Format: the decision required in one sentence, three to five bullets of
what the reader must know to make it, the main risk or uncertainty, and
what happens next.

List separately any point where the paper is unclear about its own
conclusion.

Paper:
[PASTE]
```
*Check before you use the output:* the hedges. Summarisation flattens qualified statements into confident ones, and the summary is the part that gets quoted back at you.

**P7.3 — The difficult email**
*Use when:* you have to tell someone something they will not like.
*Paste this:*
```
You are helping a finance professional write a difficult message. I will
describe the situation, the recipient, the relationship, and the outcome
I want.

Task: draft the message.

Constraints: state the substance in the first three sentences — no
warm-up. Do not apologise for facts. Do not soften a deadline or a
consequence I have given you, and do not add one I have not. No
flattery, no false warmth, no exclamation marks. Do not characterise the
recipient's likely feelings. British English.

Format: subject line, then the message. Under 200 words.

Then give me one alternative opening paragraph with a different balance
of directness, and one line on when each is the better choice.

The situation:
[PASTE]
```
*Check before you use the output:* whether any commitment has crept in. Drafts of awkward messages tend to acquire an offer to help that you did not intend to make.

**P7.4 — Anticipating the questions**
*Use when:* you present tomorrow.
*Paste this:*
```
You are preparing a finance presenter for questions on [TOPIC] at
[ENTITY]. I will paste my paper or notes and describe the audience.

Task: predict the questions, hardest first, including the ones that come
from someone who has read only the summary and the ones that come from
someone who has read the appendix closely.

Constraints: do not answer them and do not draft my answers — I need to
know what I do not know. Do not invent facts about our business in the
framing of a question. Where a question would be prompted by something
absent from my paper, say what is absent.

Format: three groups — Questions the paper answers, Questions the paper
raises but does not answer, Questions the paper does not anticipate at
all. Within each, hardest first.

Say plainly if a likely question has no answer available from what I
have given you.

My paper and audience:
[PASTE]
```
*Check before you use the output:* the middle group. Those are the questions you will be asked and are least prepared for.

**P7.5 — Plain-English pass**
*Use when:* a document has to be read by people outside finance.
*Paste this:*
```
You are rewriting a finance document for readers who are competent
professionals but not accountants. I will paste the text.

Task: rewrite it so it can be read once and understood.

Constraints: keep every figure exactly as written. Keep every
qualification. Where a technical term is unavoidable, keep it and add a
short gloss in brackets on first use — do not replace it with a loose
synonym. Do not simplify a conditional statement into an unconditional
one. British English. Do not add examples, analogies or context of your
own.

Format: the rewritten document, then a list of the terms you glossed
and the gloss you used, so I can check each one.

If a passage cannot be made plainer without changing its meaning, leave
it and list it under "Kept as written".

Document:
[PASTE]
```
*Check before you use the output:* every gloss. A slightly wrong definition of a technical term, in a document going to non-specialists, is harder to correct later than the jargon was.

## 8. Process documentation and team training

**P8.1 — Procedure from your own narration**
*Use when:* the process exists only in the hands of the person who does it.
*Paste this:*
```
You are turning a spoken description into a written procedure. I will
paste a transcript or notes of someone describing how they perform
[PROCESS] at [ENTITY].

Task: write the procedure as numbered steps that a competent newcomer
could follow.

Constraints: include only steps described in the source. Do not add
steps that seem obvious, do not reorder into a more logical sequence
without flagging it, and do not add system names, field names or
approvals not mentioned. Where the speaker says "usually" or "it
depends", preserve the conditionality — do not turn it into a rule.

Format: numbered steps, each starting with a verb. Sub-steps where the
source gives detail. A "Before you start" list of what you need to hand.

End with "Points the description left open", listing every place the
speaker was vague, and a note where you changed the order.

Source:
[PASTE]
```
*Check before you use the output:* the conditionals. Turning "usually we check with the manager" into "check with the manager" changes the process, and turning it into nothing changes it more.

**P8.2 — Desk instructions for a new joiner**
*Use when:* somebody starts on Monday.
*Paste this:*
```
You are writing desk instructions for a new joiner in a finance team at
[ENTITY], covering [TASK]. I will paste our existing procedure and
describe what the new joiner does and does not already know.

Task: rewrite the procedure for someone doing it for the first time,
without our internal shorthand.

Constraints: change no step and no sequence. Expand abbreviations only
where I have told you what they mean — otherwise mark them [EXPAND
THIS]. Do not invent screen names, menu paths or system behaviour. Add
no reassurance and no encouragement.

Format: the instructions, with a "what this step is for" line under each
step, and a final section "When to stop and ask" listing the situations
where a newcomer should escalate rather than proceed.

List anything in our procedure that you could not make sense of.

Procedure and context:
[PASTE]
```
*Check before you use the output:* the "when to stop and ask" section, with the person who currently does the job. It is the part that prevents expensive mistakes and the part only they can write.

**P8.3 — Training exercises**
*Use when:* you are teaching a technique rather than a task.
*Paste this:*
```
You are designing practice exercises for a finance team learning
[TECHNIQUE OR TASK] at [ENTITY]. I will describe the level of the team
and the mistakes they currently make.

Task: design [NUMBER] exercises that would surface exactly those
mistakes, in increasing difficulty.

Constraints: exercises must use fictional data that is clearly labelled
as fictional, and no exercise may present invented figures as real
market, industry or benchmark data. Do not reference any real
organisation. Each exercise must have a definite right answer, or, if it
is a judgement exercise, a definite list of what a good answer must
address.

Format: for each — the scenario, what the learner must produce, the
mistake it is designed to surface, and the marking notes.

If a mistake I described cannot be surfaced by an exercise, say so and
suggest what would address it instead.

Team and mistakes:
[PASTE]
```
*Check before you use the output:* the marking notes. If they are vague, the exercise will produce an argument rather than learning.

**P8.4 — Handover note**
*Use when:* somebody is leaving, or going on leave, or moving on.
*Paste this:*
```
You are building a handover note for [ROLE] at [ENTITY]. I will describe
what the role does, in whatever order it comes to me.

Task: organise it into a handover document, and identify what is
missing.

Constraints: use only what I give you. Do not assume responsibilities
based on the job title. Do not assign deadlines or contacts I have not
named. Where I have described something vaguely, keep my words and mark
it "needs detail".

Format: Recurring tasks by frequency, One-off items in progress with
status, Relationships and who to contact for what, Access and
permissions required, Known problems and workarounds, Things only this
person knows.

The last section matters most. Prompt me with questions to fill it — the
undocumented knowledge that walks out of the door.

What the role does:
[PASTE]
```
*Check before you use the output:* the questions it asks you at the end, and answer them before the person leaves. After they leave, the note is whatever it is.

**P8.5 — Explaining a spreadsheet to its future maintainer**
*Use when:* a model has grown and only one person understands it.
*Paste this:*
```
You are documenting a spreadsheet formula so that a future maintainer
can understand it. I will paste the formula and describe the sheet
layout and what the calculation is meant to achieve.

Task: explain what the formula actually does, step by step, and whether
that matches my description of the intent.

Constraints: work only from the formula text and the layout I describe.
Do not assume ranges, named ranges or sheet contents I have not given
you. Do not rewrite the formula unless I ask. If the formula's behaviour
in an edge case cannot be determined from what I have provided, say so.

Format: what it does in one sentence; then a numbered breakdown from the
innermost operation outwards; then Edge cases, covering blanks, errors,
text where a number is expected, and ranges that grow.

End with "Where this may not match your stated intent", or state plainly
that it appears to match.

Formula, layout and intent:
[PASTE]
```
*Check before you use the output:* the edge cases, by testing them in a copy of the file. An explanation of a formula is a hypothesis until the spreadsheet agrees with it.

## Building your own

Every prompt above is the same six parts in the same order, and once you see the frame you can write your own in about two minutes.

| Part | What it does | Typical failure if you omit it |
|---|---|---|
| Role | Sets who is speaking and to whom | Generic writing pitched at nobody |
| Task | States the single job | Several half-done jobs |
| Context | Supplies the facts only you have | Plausible invention filling the gap |
| Constraints | Rules out what you do not want | Added figures, added causes, added cheer |
| Format | Names the shape of the output | Reformatting by hand afterwards |
| Uncertainty rule | Says what to do when it does not know | Confident, fluent, wrong |

The last one is the part people leave out, and it is the part that makes the difference between a tool and a liability. "If you are unsure, say so" is a weak version. Better ones name the behaviour precisely: put unclassifiable items in a separate list; quote the clause you could not interpret; state what information you would need; say plainly that you cannot reconcile the components to the total. Give it somewhere to put its ignorance and it will use it. Give it nowhere, and it will smooth the gap over with something that reads well.

Two habits are worth forming. Write the check before you write the prompt — decide what would be wrong in the output and how you would spot it, and if you cannot answer that, you are not ready to use the output for anything that matters. And keep your prompts in a file where your team can see and improve them, with a line under each recording what went wrong the last time someone used it. A prompt library that nobody edits is a library of your first attempts.
