A prompt is a briefing, not a spell. Paste one, take whatever comes back and put your name on it, and this will go badly. Every prompt below assumes you know things the model does not: what your entity does, which numbers matter this period, and what happens if the answer is wrong. The prompt gets that out of your head in an orderly way. You do everything after.

Change three things in almost every prompt here. The role line, because "assisting a finance team in a group with overseas subsidiaries and a manual consolidation" produces different work from "assisting a finance team". The constraints, so they carry your house rules — anything a new joiner would get wrong. And the format, so the output feeds your template rather than being retyped into it.

Leave two things alone: the instruction to mark uncertainty and refuse to guess, and the ban on inventing figures. Remove either and you get confident filler, the expensive failure in this work. First, though, settle a separate question — whether you may put this information into this tool at all. Client data, staff data and anything confidential are decisions for whoever owns that policy, not for you at your desk. If nobody has decided, assume not.

| Change this | Keep this |
|---|---|
| The role line, to match your entity | The uncertainty rule |
| The constraints, to carry your house rules | The ban on inventing figures |
| The format, to fit your template | The instruction to list what it could not determine |

## 1. Month-end close and reconciliations

**P1.1 — Reconciliation break triage**
*Use when:* you have unexplained differences and little time.
*Paste this:*
```
You are assisting a finance team at month-end on [ACCOUNT], [PERIOD].

Task: group the reconciling items below by likely cause and say what
evidence would confirm or rule out each.

Constraints: use only what I paste. Invent no amount, date or
counterparty.

Format: a table — Item, Amount, Likely cause, Confirming evidence, Who
to ask. Then a list headed "Cannot classify".

Anything you are unsure about goes there. Never guess.

Items:
[PASTE]
```
*Check before you use the output:* the groups are inference, not findings. Confirm each against the source document.

**P1.2 — Break explanation, written up**
*Use when:* you must write up a difference you have explained.
*Paste this:*
```
You are helping an accountant write a file note on a difference on
[ACCOUNT], [PERIOD].

Task: turn my notes below into a note another accountant could follow in
a year without asking me anything.

Constraints: use only my facts. Add no causes or conclusions, and
neither soften nor strengthen mine.

Format: four short paragraphs — what the difference was, why it arose,
what was done, what remains open. Under 300 words.

Fill no gaps; list them under "Questions I could not answer".

Notes:
[PASTE]
```
*Check before you use the output:* the "remains open" paragraph. Models tidy loose ends away.

**P1.3 — Close checklist builder**
*Use when:* your close runs on memory and one person's spreadsheet.
*Paste this:*
```
You are documenting the month-end close at [ENTITY].

Task: turn the tasks below into a checklist someone who has never run
our close could follow.

Constraints: include only tasks I describe. Add no standard tasks you
assume we perform, and no deadlines I have not given.

Format: a table — Working day, Task, Owner, Depends on, Evidence. Then
any task I did not mention, as a question.

Where sequence or ownership is ambiguous, write UNCLEAR.

Our tasks, in my own words:
[PASTE]
```
*Check before you use the output:* the dependency column. A task placed before its dependency is worse than no checklist.

**P1.4 — Intercompany mismatch plan**
*Use when:* two entities disagree and you need a plan before the calls.
*Paste this:*
```
[ENTITY A] and [ENTITY B] disagree on the intercompany balance for
[PERIOD].

Task: an investigation plan — causes to test in order, cheapest and
likeliest first.

Constraints: work only from what I tell you. Assume nothing about our
systems, currencies or cut-off conventions.

Format: numbered steps, each stating what to check, what result confirms
the cause, and what to do if it does not.

End with "Assumptions I had to make". If you need more, ask.

What each entity reports:
[PASTE]
```
*Check before you use the output:* the assumptions list, then every step resting on it.

**P1.5 — Accrual and prepayment review questions**
*Use when:* you are reviewing someone else's schedule.
*Paste this:*
```
You are reviewing a schedule of accruals and prepayments for [ENTITY],
[PERIOD].

Task: the questions a careful reviewer would ask — aimed at what would
be wrong if the preparer had been rushing.

Constraints: recalculate nothing and call no figure wrong; you cannot
see the evidence. Name no accounting standard.

Format: questions under Completeness, Cut-off, Basis of estimate and
Reversal. Maximum 20, ordered by money at stake.

Where the schedule gives too little for a real question, say so.

Schedule:
[PASTE]
```
*Check before you use the output:* whether the questions are specific to your schedule. Generic ones mean thin context.

## 2. Variance analysis and management commentary

**P2.1 — First-pass variance questions**
*Use when:* the variance report has landed and nobody has spoken to the business.
*Paste this:*
```
You are assisting a controller investigating variances for [ENTITY],
[PERIOD].

Task: for each line I flag, the questions to put to the budget holder —
those separating timing, volume, price, misposting and real change.

Constraints: do not explain the variances yourself; you do not know our
business. Let no presumed cause appear in a question's wording.

Format: for each flagged line, the account name then three to six
questions.

If a line is too small to be worth a conversation, say so.

Table:
[PASTE]
```
*Check before you use the output:* leading questions. A question naming a cause returns the answer you suggested.

**P2.2 — Commentary from your explanations**
*Use when:* you have the reasons and need them written up.
*Paste this:*
```
You are drafting management commentary for [ENTITY], [PERIOD], for
[AUDIENCE]. My notes give each account, its figure and the business's
explanation — the only permitted source of cause.

Task: write the commentary.

Constraints: add no context, market conditions, forward-looking
statements or figures. Do not tell the reader how to feel.

Format: one short paragraph per variance, largest first, opening with
the account name in bold. Maximum [WORD LIMIT] words.

Flag any explanation that does not account for its movement.

Notes:
[PASTE]
```
*Check before you use the output:* every causal phrase. Each must trace to a named person.

**P2.3 — The walk from last period to this**
*Use when:* you need a bridge a reader can follow without a chart.
*Paste this:*
```
You are explaining a movement in [MEASURE] from [PRIOR PERIOD] to
[CURRENT PERIOD] at [ENTITY].

Task: write the bridge as prose, in the order that reads clearest.

Constraints: the components must sum to the movement as given. If they
do not, stop and tell me the difference. Insert no balancing item.

Format: a lead sentence stating the movement, then one sentence per
component.

Say plainly if you cannot reconcile my components to my movement.

Inputs:
[PASTE]
```
*Check before you use the output:* whether it reported a reconciliation failure rather than writing around it.

**P2.4 — De-waffling a draft**
*Use when:* the commentary reads like a press release.
*Paste this:*
```
You are an unsentimental editor of finance writing.

Task: rewrite the draft below so every sentence carries information. Cut
hedging and adjectives that assert rather than describe.

Constraints: change no figure, cause or conclusion, and add no facts. If
cutting would lose a fact, keep the fact and cut the decoration.

Format: the rewritten text, then the sentences you could not tighten
because they made a claim the draft does not support.

Never invent a stronger version of a weak claim. Flag it.

Draft:
[PASTE]
```
*Check before you use the output:* the figures, line by line. Editors round numbers to make sentences sit better.

**P2.5 — Attack my explanation**
*Use when:* you are about to present a reason and want it tested.
*Paste this:*
```
You are a sceptical audit committee member.

Task: attack the explanation below. Find the questions that would expose
it if it were wrong, incomplete, or an artefact of the numbers.

Constraints: do not present alternatives as fact, and invent no figures.
Frame each challenge as a question I can answer.

Format: three groups — size, timing, simpler explanation. Maximum ten,
hardest first.

If you cannot fault it, say so rather than manufacture objections.

My explanation:
[PASTE]
```
*Check before you use the output:* whether each challenge is answerable with evidence you can obtain. Park the rest.

## 3. Budgeting and forecasting

**P3.1 — Assumption map for a budget line**
*Use when:* a budget line has become one number nobody can defend.
*Paste this:*
```
You are making assumptions explicit for [BUDGET LINE] at [ENTITY] for
[PERIOD].

Task: break the line into the drivers needed to build it from scratch,
and say what source holds each answer.

Constraints: give no values, ranges, percentages or benchmarks — not one
number. Where a driver depends on a decision, say whose.

Format: a table — Driver, Unit, Type (fact / estimate / decision), Where
the answer lives, Question to ask.

If the line could be built two ways, show both.
```
*Check before you use the output:* that the drivers actually rebuild your line.

**P3.2 — Budget holder briefing**
*Use when:* the budget pack goes out to non-finance managers.
*Paste this:*
```
You are briefing non-financial managers who must submit figures for
[PERIOD]. Their cost lines are [LIST]; the deadline is [DATE].

Task: write the note that accompanies the template.

Constraints: no jargon without a plain gloss. No threats and no
cheerleading. State no figure, limit or target.

Format: a short opening on what we need and when; a numbered list of
what to submit; another of what not to do.

Leave a marked [ ] wherever a figure or name is needed.
```
*Check before you use the output:* that every placeholder is still empty.

**P3.3 — Forecast assumption challenge**
*Use when:* the forecast is built and you want the weak joints found.
*Paste this:*
```
You are reviewing the assumptions behind a forecast for [ENTITY] over
[PERIOD].

Task: identify which assumptions the outcome is most sensitive to, which
are mutually inconsistent, and which cannot be tested.

Constraints: never tell me an assumption is too high or too low — you
have no basis. Compute no revised outcomes.

Format: three sections — Most sensitive, Mutually inconsistent, Not
testable as written. Name each and state the problem.

Where facts I have withheld might reconcile something, ask.

Assumptions and values:
[PASTE]
```
*Check before you use the output:* the sensitivity claims. Without your model they are a list to test, not a finding.

**P3.4 — Scenario definitions, without numbers**
*Use when:* scenarios were asked for and nobody has defined them.
*Paste this:*
```
You are defining scenarios for [ENTITY] over [PERIOD].

Task: define [NUMBER] scenarios. Each is a coherent story about the
world, not a percentage applied to a base case.

Constraints: no numbers, no probabilities, no likelihoods. Each must
stay internally consistent and use only my uncertainties.

Format: for each — a name, a paragraph, bullets showing which
assumptions move and which way, and the earliest observable sign.

If two uncertainties cannot vary independently, say so.

Business and uncertainties:
[PASTE]
```
*Check before you use the output:* the early-warning signs — the part that gets used, and the likeliest platitude.

**P3.5 — Budget submission review**
*Use when:* submissions are in and you must review many quickly.
*Paste this:*
```
You are reviewing a budget submission from [DEPARTMENT] for [PERIOD]
against our rules.

Task: list every breach, and every required explanation missing or too
vague.

Constraints: do not assess whether the figures are reasonable — that is
mine. Quote the submission's exact wording when you flag it.

Format: a table — Rule, What the submission says, Problem, What to
request. Then: ready for review, or return to sender.

If a rule is ambiguous, flag the rule rather than choose.

Rules, then submission:
[PASTE]
```
*Check before you use the output:* the quotations. If one is not verbatim, discard the review and run it again.

## 4. Audit and assurance support

**P4.1 — Making sense of a request list**
*Use when:* the auditor's list has arrived and you must allocate work.
*Paste this:*
```
You are planning a response to an auditor's request list for [ENTITY],
[PERIOD].

Task: for each item, say what is likely being established, what document
satisfies it, and which role holds it.

Constraints: this is general information about how such requests are
framed, not advice on what any standard requires — say so at the top.
Never call an item unnecessary.

Format: a table — Request, Likely purpose, Document, Owner, Effort.

Where you cannot tell what is asked, write "ask them to clarify".

List:
[PASTE]
```
*Check before you use the output:* the "likely purpose" column. It is inference, and a wrong one doubles the work.

**P4.2 — Response to an audit query**
*Use when:* you have the facts and need the reply written cleanly.
*Paste this:*
```
You are helping an accountant respond to an audit query on [TOPIC] for
[ENTITY], [PERIOD].

Task: draft the response.

Constraints: use only my facts. Never assert a treatment is correct or
compliant — state what was done and why, and let the auditor judge. Name
no standard.

Format: our position in short; the facts in order; the documents
attached; any point that remains a matter of judgement.

If my facts do not fully answer the query, say what is missing.

Query and facts:
[PASTE]
```
*Check before you use the output:* any sentence asserting compliance. Replace it with what you actually did.

**P4.3 — Control description write-up**
*Use when:* a control exists in practice but was never written down.
*Paste this:*
```
You are documenting an internal control at [ENTITY].

Task: write the control description.

Constraints: describe only what I say happens, weaknesses included.
Never write the control as it ought to be, and add no threshold or
approver I have not stated.

Format: What it is; Who performs it; How often; What evidence it leaves;
What it would catch; What it would not catch.

If you cannot complete the last section honestly, ask me questions.

What actually happens, informal parts included:
[PASTE]
```
*Check before you use the output:* the "would not catch" section. If it is short or reassuring, it is wrong.

**P4.4 — Walkthrough interview questions**
*Use when:* you are about to trace a transaction with its process owner.
*Paste this:*
```
You are preparing a walkthrough of the [PROCESS] process at [ENTITY].

Task: write the questions for the person who performs it, designed to
reveal where the documented process and the real one differ.

Constraints: open questions only, nothing answerable with yes. Do not
presume the process is followed. Assess nothing.

Format: questions in the order the transaction flows, each with a note
on what a concerning answer sounds like.

End with the questions that surface undocumented workarounds. Where my
description is too vague to build a question on, say so.

Believed process:
[PASTE]
```
*Check before you use the output:* that it does not read as an interrogation. People stop describing reality when tested.

**P4.5 — Evidence gaps in a testing plan**
*Use when:* you have drafted a testing approach and want its holes found.
*Paste this:*
```
You are reviewing a draft testing approach for [AREA] at [ENTITY].

Task: find where the evidence would not support the conclusion drawn.

Constraints: this is a logical review, not a professional or regulatory
one; say so at the top. Name no standard.

Format: for each gap — what the test does, what conclusion is drawn, why
it does not follow, what would close it.

If it is sound as far as you can tell, say so.

What we test, how, and over what population:
[PASTE]
```
*Check before you use the output:* whether it stayed inside logic. Telling you what is required is outside its competence.

## 5. Tax and compliance preparation

Everything here is preparation, not advice. No output should reach a filing without a qualified person in your jurisdiction reviewing it: tax rules differ between countries, differ within them, and change. Use these to get organised, not to reach conclusions.

**P5.1 — Information gathering checklist**
*Use when:* a filing is coming and the documents are scattered.
*Paste this:*
```
You are organising a finance team before a [FILING TYPE] for [ENTITY],
[PERIOD].

Task: a checklist of documents to gather for whoever prepares the
filing.

Constraints: this is a gathering aid and general information, not tax
advice; rules differ by jurisdiction and change. Never state what is
deductible, taxable or claimable, and reference no law or form.

Format: a table — Activity, Records to gather, Where they live, Owner,
Status.

Where treatment depends on local rules, write "for your adviser".

Activities carried out:
[PASTE]
```
*Check before you use the output:* that nothing drifted from "gather this" into "this is treated as". Strike any treatment.

**P5.2 — Categorisation queries**
*Use when:* you are cleaning a transaction listing before it goes to an adviser.
*Paste this:*
```
You are preparing a transaction listing for [ENTITY], [PERIOD], for our
tax adviser.

Task: identify transactions described too vaguely for someone else to
categorise, and write the question for whoever incurred them.

Constraints: categorise nothing and state no tax treatment; this is
preparation, not advice. Never infer purpose from a supplier name.

Format: a table — Reference, Description as given, Why it is unclear,
Question to ask, Who to ask.

Leave out anything adequately described. A short list is a good outcome.

Listing:
[PASTE]
```
*Check before you use the output:* whether purpose was inferred from vendor names. That assumption unwinds badly later.

**P5.3 — Understanding a letter you have received**
*Use when:* correspondence arrives and you need to know what it asks.
*Paste this:*
```
You are helping a finance professional understand a letter received by
[ENTITY].

Task: say plainly what it appears to ask for, what it requires by when,
and what it omits.

Constraints: this is a reading aid and general information, not legal or
tax advice; procedures differ by jurisdiction and change. Never tell me
how to respond or what my obligations are.

Format: What it asks for; Dates it states; What is unclear.

Quote ambiguous passages rather than resolving them.

Letter:
[PASTE]
```
*Check before you use the output:* the deadlines, word for word. A misread date is the one irreversible error here.

**P5.4 — Questions for your adviser**
*Use when:* you have adviser time booked and want to use it well.
*Paste this:*
```
You are preparing a finance team to meet its tax adviser about [TOPIC]
at [ENTITY].

Task: the questions to ask, ordered so the answers build on each other,
with the documents to have to hand for each.

Constraints: answer none of them. Never hint at the likely answer or
state a rule. This is meeting preparation only.

Format: numbered questions, each with a sub-line "Bring:".

End with "Things we should tell them without being asked". Where my
description leaves a gap, ask rather than assume.

Our situation:
[PASTE]
```
*Check before you use the output:* the final section — the most valuable part, resting on facts you may have omitted.

**P5.5 — Obligations calendar**
*Use when:* deadlines live in several people's heads.
*Paste this:*
```
You are building an internal compliance calendar for [ENTITY].

Task: turn the obligations below into a calendar, with the internal
milestones before each external deadline.

Constraints: use only my obligations and dates, and correct none of them
— you do not know my jurisdiction. List anything you think I omitted as
questions.

Format: a table — External deadline, Obligation, Internal milestone,
Days before, Owner. Sorted by date.

Open by saying the dates come from me and need confirming.

Obligations, with deadlines as we understand them:
[PASTE]
```
*Check before you use the output:* that no deadline was silently adjusted and no obligation added.

## 6. Contracts, agreements and policy documents

Reading a contract for its finance consequences is not the same as advising on it. These prompts extract and organise; they do not interpret, and none replaces your legal adviser.

**P6.1 — Finance summary of an agreement**
*Use when:* a signed agreement lands and you need its effect on the numbers.
*Paste this:*
```
You are explaining the financial mechanics of an agreement involving
[ENTITY].

Task: summarise only the provisions affecting money, timing, or what
must be tracked.

Constraints: this is a reading aid, not legal advice; law differs by
jurisdiction. Quote the clause reference and wording for every point,
never interpret ambiguous drafting, and state no accounting treatment.

Format: Amounts payable or receivable; Timing and triggers; Variation;
Termination and its financial consequences; Obligations to track.

End with "Clauses I could not interpret with confidence", quoting each.

Agreement:
[PASTE]
```
*Check before you use the output:* every clause reference. If the references drift, nothing else is safe.

**P6.2 — Payment terms extraction**
*Use when:* you are loading terms into a system or comparing a portfolio.
*Paste this:*
```
You are extracting data from a contract for [ENTITY].

Task: extract the payment terms into a table for system entry.

Constraints: extract only; never normalise into your own categories.
Every value must appear with its clause reference. If a field is not
addressed, write "not stated" — never a default.

Format: a table — Field, Value, Clause. Fields: currency, amount basis,
invoicing frequency, payment period, late payment, price adjustment,
discounts, expenses, disputes.

Then list any payment provision that did not fit.

Contract:
[PASTE]
```
*Check before you use the output:* every "not stated", and any odd clause reference.

**P6.3 — Obligations and dates register**
*Use when:* the contract creates things somebody must remember to do.
*Paste this:*
```
You are building an obligations register from an agreement involving
[ENTITY].

Task: list every obligation falling on us, with every deadline, notice
period, renewal date and triggering condition.

Constraints: quote the clause reference and wording for each entry.
Calculate a date only where the contract gives both the reference point
and the period. Never interpret conditional wording — quote it.

Format: a table — Obligation, Owner function, Trigger or date, Notice
period, Clause, Wording quoted.

Flag any obligation whose trigger you could not determine.

Agreement:
[PASTE]
```
*Check before you use the output:* every calculated date. Business-day and month-end definitions break the arithmetic.

**P6.4 — Questions for legal review**
*Use when:* legal budget is limited and you want it spent well.
*Paste this:*
```
You are preparing for legal review of a draft agreement involving
[ENTITY].

Task: find where the draft and the deal I describe diverge, and write
the questions for counsel.

Constraints: give no legal advice and never say whether a term is
standard or reasonable. Confine yourself to: what I said the deal is,
what the words say, the question.

Format: a table — Commercial expectation, Clause and wording, The
mismatch, Question for counsel.

Where drafting matches my description, say so rather than invent
concern.

The deal, then the draft:
[PASTE]
```
*Check before you use the output:* that the expectation column reflects what you said, not a tidier version of it.

**P6.5 — Internal policy drafting**
*Use when:* you need a policy people will actually follow.
*Paste this:*
```
You are drafting an internal [POLICY TYPE] policy for [ENTITY].

Task: write the policy.

Constraints: include only my rules. Add no thresholds, approval levels
or exceptions — if one seems missing, list it as a question. Reference
no law. No sentence over 25 words.

Format: Purpose; Who it applies to; The rules as numbered clauses; What
to do if they do not cover your situation; Who owns it.

End with "Decisions you have not made yet".

Rules and limits we have decided:
[PASTE]
```
*Check before you use the output:* the gaps list, before circulating anything.

## 7. Board papers, reports and written communication

**P7.1 — Board paper structure**
*Use when:* you know what to say and not yet how to arrange it.
*Paste this:*
```
You are structuring a board paper on [TOPIC] for [ENTITY].

Task: propose the structure — sections, what belongs in each, roughly
how long each should be.

Constraints: structure only. Draft no content, supply no facts, suggest
no recommendation.

Format: a numbered outline. For each section: purpose in one line, what
goes in it, target length, and whether it belongs in an appendix.

End with "Facts you will need that you have not mentioned".

Background:
[PASTE]
```
*Check before you use the output:* the gaps list against your own knowledge — the closest thing here to a rehearsal.

**P7.2 — One page from twenty**
*Use when:* the paper is written and the summary is due.
*Paste this:*
```
You are summarising the paper below for [AUDIENCE]. The decision
required is [DECISION].

Task: a summary of no more than one page.

Constraints: every statement must appear in the paper. Where it
qualifies a key point, the qualification must survive — never harden a
hedged conclusion. Change no figure.

Format: the decision in one sentence; three to five bullets of what the
reader must know; the main uncertainty; next steps.

List any point where the paper is unclear about its conclusion.

Paper:
[PASTE]
```
*Check before you use the output:* the hedges. Summarising turns qualified statements into confident ones.

**P7.3 — The difficult email**
*Use when:* you must tell someone something they will not like.
*Paste this:*
```
You are helping a finance professional write a difficult message.

Task: draft the message.

Constraints: state the substance in the first three sentences — no
warm-up. Never apologise for facts, soften a deadline I have given, or
add one I have not. No flattery and no exclamation marks.

Format: subject line, then the message, under 200 words.

Then one alternative opening with a different balance of directness. If
my description leaves the outcome unclear, ask.

Situation, recipient, outcome I want:
[PASTE]
```
*Check before you use the output:* whether a commitment crept in that you did not intend to make.

**P7.4 — Anticipating the questions**
*Use when:* you present tomorrow.
*Paste this:*
```
You are preparing a presenter for questions on [TOPIC] at [ENTITY].

Task: predict the questions, hardest first — from a summary-only reader
and from one who read the appendix.

Constraints: never answer them or draft my answers; I need to know what
I do not know. Invent no facts about our business.

Format: three groups — what the paper answers, what it raises but leaves
unanswered, what it does not anticipate.

Say plainly where a likely question has no answer available.

Paper and audience:
[PASTE]
```
*Check before you use the output:* the middle group — the questions you will be asked and are least ready for.

**P7.5 — Plain-English pass**
*Use when:* a document must be read by people outside finance.
*Paste this:*
```
You are rewriting a finance document for readers who are competent
professionals but not accountants.

Task: rewrite it to be read once and understood.

Constraints: keep every figure and qualification intact. Keep
unavoidable technical terms and gloss them in brackets on first use —
never a loose synonym, and never make a conditional statement
unconditional.

Format: the rewritten document, then the terms you glossed and the gloss
used.

Where a passage cannot be plainer without changing meaning, leave it
under "Kept as written".

Document:
[PASTE]
```
*Check before you use the output:* every gloss. A wrong definition is harder to correct later than the jargon was.

## 8. Process documentation and team training

**P8.1 — Procedure from your own narration**
*Use when:* the process lives only in the head of the person who does it.
*Paste this:*
```
You are turning a spoken description of [PROCESS] at [ENTITY] into a
written procedure.

Task: write the procedure as numbered steps a competent newcomer could
follow.

Constraints: include only steps in the source; add no system names or
approvals not mentioned. Where the speaker says "usually" or "it
depends", preserve the conditionality. Flag any reordering.

Format: numbered steps starting with a verb; sub-steps where the source
gives detail; a "Before you start" list.

End with "Points the description left open".

Notes of the description:
[PASTE]
```
*Check before you use the output:* the conditionals. Turning "usually we check" into "check" changes the process.

**P8.2 — Desk instructions for a new joiner**
*Use when:* somebody starts on Monday.
*Paste this:*
```
You are writing desk instructions for a new joiner at [ENTITY], covering
[TASK].

Task: rewrite the procedure below for a first-timer, without our
internal shorthand.

Constraints: change no step and no sequence. Expand an abbreviation only
where I have said what it means — otherwise mark it [EXPAND THIS].

Format: the instructions, each step with a "what this is for" line, then
"When to stop and ask".

List anything in our procedure you could not make sense of.

Procedure, and what the joiner knows:
[PASTE]
```
*Check before you use the output:* the "when to stop and ask" section, with whoever does the job now.

**P8.3 — Training exercises**
*Use when:* you are teaching a technique rather than a task.
*Paste this:*
```
You are designing exercises for a team learning [TECHNIQUE] at [ENTITY].

Task: design [NUMBER] exercises surfacing exactly the mistakes below, in
increasing difficulty.

Constraints: use fictional data, clearly labelled. Never present
invented figures as real market or benchmark data, and name no real
organisation. Each needs a definite right answer or marking list.

Format: for each, the scenario, what the learner produces, the mistake
it surfaces, marking notes.

If a mistake cannot be surfaced by an exercise, say so.

Their level and current mistakes:
[PASTE]
```
*Check before you use the output:* the marking notes. Vague ones produce arguments, not learning.

**P8.4 — Handover note**
*Use when:* somebody is leaving, or going on long leave.
*Paste this:*
```
You are building a handover note for [ROLE] at [ENTITY].

Task: organise the notes below into a handover document and identify
what is missing.

Constraints: use only what I give you. Never assume responsibilities
from the job title or name contacts I have not given. Where I was vague,
mark "needs detail".

Format: Recurring tasks by frequency; One-off items in progress;
Contacts; Access required; Known workarounds; Things only this person
knows.

Prompt me with questions to fill the last section.

What the role does:
[PASTE]
```
*Check before you use the output:* the questions it puts to you, and answer them before the person leaves.

**P8.5 — Explaining a spreadsheet to its future maintainer**
*Use when:* a model has grown and one person understands it.
*Paste this:*
```
You are documenting a spreadsheet formula for its future maintainer.

Task: explain what the formula does, step by step, and whether that
matches my intent.

Constraints: work only from the formula text and the layout described.
Assume no ranges or sheet contents I have not given.

Format: one sentence on what it does; a numbered breakdown from the
inside out; then Edge cases — blanks, errors, wrong types, growth.

Say so where an edge case cannot be determined from what I gave.

Formula, layout and intended result:
[PASTE]
```
*Check before you use the output:* the edge cases, by testing them in a copy of the file.

## Building your own

Every prompt above is the same six parts in the same order. Once you see the frame, your own take about two minutes.

| Part | What it does | Typical failure if you omit it |
|---|---|---|
| Role | Sets who is speaking, and to whom | Generic writing pitched at nobody |
| Task | States the single job | Several half-done jobs |
| Context | Supplies the facts only you have | Plausible invention filling the gap |
| Constraints | Rules out what you do not want | Added figures, added causes, added cheer |
| Format | Names the shape of the output | Retyping it by hand afterwards |
| Uncertainty rule | Says what to do when it does not know | Confident, fluent, wrong |

The last is the part people leave out, and the part that separates a tool from a liability. "If you are unsure, say so" is the weak version. The strong ones name the behaviour: put unclassifiable items in a separate list; quote the clause you could not interpret; say plainly that you cannot reconcile the components to the total. Give it somewhere to put its ignorance and it will use it. Give it nowhere and it will smooth the gap over with something that reads well.

Two habits are worth forming. Write the check before you write the prompt — decide what would be wrong in the output and how you would spot it. If you cannot answer that, you are not ready to use the output for anything that matters. And keep your prompts where the team can improve them, with a line under each recording what went wrong last time. A prompt library nobody edits is a library of first attempts.
