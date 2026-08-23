A prompt is a briefing, not a spell. Paste one, take whatever comes back and put your name on it, and this will go badly. Every prompt below assumes you know things the model does not: what your entity does, which numbers matter this period, what your reviewer will ask, and what happens if the answer is wrong. The prompt's job is to get that out of your head in an orderly way. Yours is everything after.

Change three things in almost every prompt here. The role line, because "assisting a finance team in a group with overseas subsidiaries and a manual consolidation" produces different work from "assisting a finance team". The constraints, so they carry your house rules and thresholds — anything a new joiner would get wrong. And the format, so the output feeds your template instead of being retyped into it.

Leave two things alone: the instruction to mark uncertainty and refuse to guess, and the ban on inventing figures. Remove either and you get confident filler, the expensive failure in this work. Before any of it, settle a separate question — whether you may put this information into this tool at all. Client data, staff data, unpublished results and anything confidential are decisions for whoever owns that policy, not for you at your desk on a Tuesday. If nobody has decided, assume not.

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
You are assisting a finance team at month-end. I will paste the
reconciling items on [ACCOUNT] for [PERIOD].

Task: group them by likely cause and say what evidence would confirm
or rule out each.

Constraints: use only what I paste; invent no amount, date or
counterparty. Where an item fits two groups, say so.

Format: a table — Item, Amount as given, Likely cause, Confirming
evidence, Who to ask. Then a list headed "Cannot classify".

Anything you are unsure about goes in that list. Do not guess.

Items:
[PASTE]
```
*Check before you use the output:* the groups are inference, not findings. Watch for items given a cause because they resembled the one above.

**P1.2 — Break explanation, written up**
*Use when:* you know why a difference arose and must write it for the file.
*Paste this:*
```
You are helping a qualified accountant write a file note. I will
describe roughly why a difference on [ACCOUNT] for [PERIOD] arose and
what I did.

Task: turn my notes into a note another accountant could follow in a
year without asking me anything.

Constraints: use only my facts. Add no causes, amounts or conclusions,
and neither soften nor strengthen mine. Plain British English.

Format: four short paragraphs — what the difference was, why it arose,
what was done, what remains open. Under 300 words.

Fill no gaps. List them under "Questions I could not answer".

Notes:
[PASTE]
```
*Check before you use the output:* the "remains open" paragraph. Models tidy loose ends into resolutions; if something is unresolved, the note must still say so.

**P1.3 — Close checklist builder**
*Use when:* your close runs on memory and one person's spreadsheet.
*Paste this:*
```
You are documenting a finance team's month-end close. I will describe
our tasks in my own words, roughly in order.

Task: turn this into a checklist someone who has never run our close
could follow.

Constraints: include only tasks I describe. Add no standard tasks you
assume we perform. Assign no deadlines I have not given.

Format: a table — Working day, Task, Owner, Depends on, Evidence
retained. Then a separate list, "Tasks you did not mention that teams
often include — confirm whether these apply".

Where sequence or ownership is ambiguous, write UNCLEAR.

Description:
[PASTE]
```
*Check before you use the output:* the dependency column. A checklist that puts a task before what it depends on is worse than none.

**P1.4 — Intercompany mismatch plan**
*Use when:* two entities disagree and you need a plan before the calls start.
*Paste this:*
```
[ENTITY A] and [ENTITY B] disagree on the intercompany balance for
[PERIOD]. I will describe what each reports and what I know.

Task: an investigation plan — causes to test in order, cheapest and
likeliest first.

Constraints: work only from what I tell you. Assume nothing about our
systems, currencies or cut-off conventions. Calculate no difference I
have not given.

Format: numbered steps, each stating what to check, what result
confirms the cause, and what to do if it does not.

End with "Assumptions I had to make". If you need information I have
not given, ask rather than proceed.

Situation:
[PASTE]
```
*Check before you use the output:* the assumptions list, then every step resting on it. Currency and cut-off conventions are what it invents most readily.

**P1.5 — Accrual and prepayment review questions**
*Use when:* you are reviewing someone else's schedule.
*Paste this:*
```
You are reviewing a schedule of accruals and prepayments for [ENTITY],
[PERIOD], pasted below as text.

Task: the questions a careful reviewer would ask — aimed at what would
be wrong if the preparer had been rushing.

Constraints: recalculate nothing and call no figure wrong; you cannot
see the evidence. Name no accounting standard. Where a point turns on
recognition, mark it "judgement — confirm against your own sources".

Format: questions under Completeness, Cut-off, Basis of estimate and
Reversal. Maximum 20, ordered by money at stake.

Where the schedule gives too little for a real question, say so rather
than asking a generic one.

Schedule:
[PASTE]
```
*Check before you use the output:* whether the questions are specific to your schedule. Generic ones mean it lacked context.

## 2. Variance analysis and management commentary

**P2.1 — First-pass variance questions**
*Use when:* the variance report has landed and you have not yet spoken to the business.
*Paste this:*
```
You are assisting a financial controller investigating variances for
[ENTITY], [PERIOD]. I will paste actual, comparative and difference.

Task: for each line I flag, the questions to put to the budget holder —
those separating a timing difference, a volume difference, a price or
rate difference, a misposting, and a real change in the business.

Constraints: do not explain the variances yourself; you do not know our
business. Calculate nothing. Let no presumed cause appear in a
question's wording.

Format: for each flagged line, the account name then three to six
questions.

If a line is too small or ambiguous to be worth a conversation, say so.

Table:
[PASTE]
```
*Check before you use the output:* leading questions. "Why did costs rise due to the new hires?" gets the answer you suggested, not the true one.

**P2.2 — Commentary from your explanations**
*Use when:* you have the reasons and need them written for the pack.
*Paste this:*
```
You are drafting management commentary for [ENTITY], [PERIOD], for
[AUDIENCE]. For each variance I give the account, the figure and the
explanation obtained from the business — the only permitted source of
cause.

Task: write the commentary.

Constraints: every cause must come from my notes. Add no context,
market conditions, forward-looking statements or figures. Do not use
"significant", "material", "strong" or "challenging". Do not tell the
reader how to feel.

Format: one short paragraph per variance, largest first, opening with
the account name in bold. Maximum [WORD LIMIT] words.

Flag any explanation that does not account for its movement.

Notes:
[PASTE]
```
*Check before you use the output:* every causal phrase — "because", "driven by", "reflecting". Each must trace to something a named person told you.

**P2.3 — The walk from last period to this**
*Use when:* you need a bridge a reader can follow without the chart.
*Paste this:*
```
You are explaining a movement in [MEASURE] from [PRIOR PERIOD] to
[CURRENT PERIOD] at [ENTITY]. I give opening and closing figures and
the components, with amounts and my explanation of each.

Task: write the bridge as prose, in the order that reads clearest.

Constraints: the components must sum to the movement as given. If they
do not, stop and tell me the difference — adjust nothing, insert no
balancing item, add no components or causes of your own.

Format: a lead sentence stating the movement, one sentence per
component, a closing sentence only if I have told you what comes next.

Say plainly if you cannot reconcile my components to my movement.

Inputs:
[PASTE]
```
*Check before you use the output:* whether it reported a reconciliation failure. Smooth prose over components that do not add up hides your error.

**P2.4 — De-waffling a draft**
*Use when:* the commentary reads like a press release.
*Paste this:*
```
You are an unsentimental editor of finance writing. I will paste a
draft of management commentary.

Task: rewrite it so every sentence carries information. Cut hedging,
throat-clearing and adjectives that assert rather than describe.

Constraints: change no figure, cause or conclusion, and add no facts.
If cutting a sentence would lose a fact, keep the fact and cut the
decoration. Preserve anything marked [DO NOT CHANGE].

Format: the rewritten text, then the sentences you could not tighten
because they made a claim you could not verify from the draft itself.

Never invent a stronger version of a weak claim. Leave it and flag it.

Draft:
[PASTE]
```
*Check before you use the output:* the figures, line by line. Editors of every kind round numbers to make a sentence sit better.

**P2.5 — Attack my explanation**
*Use when:* you are about to present a reason and want it tested first.
*Paste this:*
```
You are a sceptical audit committee member with a finance background. I
give my explanation for a movement in [MEASURE] at [ENTITY], [PERIOD].

Task: attack it. Find the questions that would expose it if it were
wrong, incomplete, or an artefact of how the numbers were prepared.

Constraints: do not present alternative explanations as fact and invent
no figures to support a challenge. Frame each challenge as a question I
can go and answer.

Format: three groups — does the cause explain the size, does it explain
the timing, is there a simpler explanation. Maximum ten, hardest first.

If you cannot fault it on the information given, say so rather than
manufacturing objections.

My explanation:
[PASTE]
```
*Check before you use the output:* whether each challenge is answerable with evidence you can actually obtain. Park the rest.

## 3. Budgeting and forecasting

**P3.1 — Assumption map for a budget line**
*Use when:* a budget line has become one number nobody can defend.
*Paste this:*
```
You are making assumptions explicit for [BUDGET LINE] at [ENTITY] for
[PERIOD].

Task: break the line into the drivers you would have to estimate to
build it from scratch, and say what source inside a business normally
holds each answer.

Constraints: give no values, ranges, percentages or benchmarks — not
one number. You do not know our sector or size. Where a driver depends
on a decision rather than a fact, mark it "decision required" and say
whose.

Format: a table — Driver, Unit, Type (fact / estimate / decision),
Where the answer lives, Question to ask.

If the line could sensibly be built two ways, show both.
```
*Check before you use the output:* that the drivers actually rebuild your line. A tidy list that does not reconstruct the number is decoration.

**P3.2 — Budget holder briefing**
*Use when:* the budget pack goes out to non-finance managers.
*Paste this:*
```
You are briefing non-financial managers who must submit figures for
[PERIOD]. Their cost lines are [LIST]. The deadline is [DATE]. Last
cycle's problems were [LIST].

Task: write the note that accompanies the template.

Constraints: no jargon without a plain gloss on first use. No threats
and no cheerleading. State no figure, limit or target. Promise nothing
about what finance will do with the numbers.

Format: a short opening on what we need and when; a numbered list of
what to submit; a numbered list of what not to do; who to contact.
Under 500 words.

Leave a marked [ ] wherever a figure or name is needed.
```
*Check before you use the output:* that every placeholder is still empty. A helpfully filled-in number ends up in a manager's spreadsheet.

**P3.3 — Forecast assumption challenge**
*Use when:* the forecast is built and you want the weak joints found.
*Paste this:*
```
You are reviewing the assumptions behind a forecast for [ENTITY] over
[PERIOD]. I will paste them with their values.

Task: identify which assumptions the outcome is most sensitive to,
which are inconsistent with each other, and which are too vague to be
tested later.

Constraints: do not tell me an assumption is too high or too low — you
have no basis for that. Confine yourself to sensitivity, consistency
and testability. Compute no revised outcomes.

Format: three sections — Most sensitive, Mutually inconsistent, Not
testable as written. Name the assumption and state the problem.

Where an apparent inconsistency might be reconciled by something I have
not told you, phrase it as a question.

Assumptions:
[PASTE]
```
*Check before you use the output:* the sensitivity claims. Without your model it reasons from structure alone, so treat them as a list to test.

**P3.4 — Scenario definitions, without numbers**
*Use when:* scenarios have been asked for and nobody has defined them.
*Paste this:*
```
You are defining scenarios for [ENTITY] over [PERIOD]. I will describe
the business and the uncertainties that actually worry management.

Task: define [NUMBER] scenarios. Each is a coherent story about the
world, not a percentage applied to a base case.

Constraints: no numbers, no probabilities, no likelihoods. Each must
say which of my named uncertainties resolve which way and stay
internally consistent — if demand falls, do not also assume prices hold
unless you say why.

Format: for each — a name, a paragraph of description, bullets showing
which assumptions move and in which direction, and the earliest
observable sign it is happening.

If two uncertainties cannot vary independently, say so.

Description:
[PASTE]
```
*Check before you use the output:* the early-warning signs. They are the part that gets used, and the part most often written as a platitude.

**P3.5 — Budget submission review**
*Use when:* submissions are in and you must review many quickly.
*Paste this:*
```
You are reviewing a budget submission from [DEPARTMENT] for [PERIOD]. I
will paste the submission and, separately, our submission rules.

Task: check it against the rules only. List every breach, and every
required explanation missing or too vague to be one.

Constraints: do not assess whether the figures are reasonable — that is
mine to judge. Do not compare to prior year unless I give it. Quote the
submission's exact wording whenever you flag something.

Format: a table — Rule, What the submission says, Problem, What to
request. Then one line: ready for review, or return to sender.

If a rule is ambiguous as written, flag the rule rather than choose a
reading.

Rules, then submission:
[PASTE]
```
*Check before you use the output:* the quotations. If one does not appear verbatim in the submission, discard the review and run it again.

## 4. Audit and assurance support

**P4.1 — Making sense of a request list**
*Use when:* the auditor's list has arrived and you must allocate work.
*Paste this:*
```
You are helping a finance team plan its response to an auditor's
information request list for [ENTITY], [PERIOD].

Task: for each item, say plainly what is likely being established, what
document would satisfy it, and which team role holds it.

Constraints: this is general information about how such requests are
usually framed, not advice on what any standard or regulator requires —
say so at the top. Cite no standard or regulation. Never tell me an
item is unnecessary or can be refused.

Format: a table — Request, Likely purpose, Document to provide, Owner,
Effort (low / medium / high).

Where you cannot tell what is being asked, write "ask the audit team to
clarify".

List:
[PASTE]
```
*Check before you use the output:* the "likely purpose" column. It is inference, and a wrong inference means doing the work twice.

**P4.2 — Response to an audit query**
*Use when:* you have the facts and need the reply written cleanly.
*Paste this:*
```
You are helping a qualified accountant respond to an audit query on
[TOPIC] for [ENTITY], [PERIOD]. I give the query and the facts and
documents we hold.

Task: draft the response.

Constraints: use only my facts. Do not assert that a treatment is
correct, compliant or in accordance with anything — state what was done
and why, and let the auditor form their view. Name no standard,
regulation or authority. Commit us to nothing I have not said.

Format: our position in short; the facts in order; the documents
attached; any point that remains a matter of judgement.

If my facts do not fully answer the query, say what is missing.

Query and facts:
[PASTE]
```
*Check before you use the output:* any sentence asserting compliance. Delete it and say what you did instead. Your position is what happened, not a claim about the rules.

**P4.3 — Control description write-up**
*Use when:* a control exists in practice but has never been written down.
*Paste this:*
```
You are documenting an internal control at [ENTITY]. I will describe
what actually happens, including the informal parts.

Task: write the control description.

Constraints: describe only what I say happens, weaknesses included.
Never write the control as it ought to be. Add no frequency, threshold,
approver or evidence I have not stated. Name no control framework.
Never use the word "ensures".

Format: What it is; Who performs it; When and how often; What evidence
it leaves; What it would catch; What it would not catch.

The last section is the point. If my description does not let you
complete it honestly, ask me the questions that would.

What happens:
[PASTE]
```
*Check before you use the output:* the "would not catch" section. If it is short or reassuring it is wrong — that section is the reason for writing the description.

**P4.4 — Walkthrough interview questions**
*Use when:* you are about to sit with a process owner and trace a transaction.
*Paste this:*
```
You are preparing a walkthrough of the [PROCESS] process at [ENTITY]. I
will describe what we believe the process is.

Task: write the questions for the person who actually performs it,
designed to reveal where the documented process and the real one
differ.

Constraints: open questions only, nothing answerable with yes. Do not
presume the process is followed. Assess nothing — you are writing
questions, not conclusions. No framework references.

Format: questions in the order the transaction flows, each with a
one-line note on what a concerning answer sounds like.

End with a group headed "Questions to ask if they seem to be describing
the manual rather than their day".

Believed process:
[PASTE]
```
*Check before you use the output:* that it does not read as an interrogation. People stop describing reality the moment they feel tested.

**P4.5 — Evidence gaps in a testing plan**
*Use when:* you have drafted a testing approach and want the holes found.
*Paste this:*
```
You are reviewing a draft testing approach for [AREA] at [ENTITY],
[PERIOD] — what we intend to test, how, and over what population.

Task: find where the evidence obtained would not support the conclusion
drawn.

Constraints: this is a logical review, not a professional or regulatory
one; say so at the top. Do not say whether the approach meets any
standard, and name none. Propose no sample sizes. Assume nothing about
our population.

Format: for each gap — what the test does, what conclusion is drawn,
why the first does not support the second, what would close it.

If it is sound as far as you can tell, say so, and say what further
information would raise your confidence.

Approach:
[PASTE]
```
*Check before you use the output:* whether it stayed inside logic. Once it starts telling you what is required, it has left the ground it can be trusted on.

## 5. Tax and compliance preparation

Everything here is preparation, not advice, and no output should reach a filing without a qualified person in your jurisdiction reviewing it. Tax rules differ between countries, differ within them, and change — often with effect from a date already past. Use these to get organised, not to reach conclusions.

**P5.1 — Information gathering checklist**
*Use when:* a filing is coming and the documents are scattered.
*Paste this:*
```
You are helping a finance team organise itself before a [FILING TYPE]
for [ENTITY] covering [PERIOD]. I will list the activities carried out.

Task: a checklist of documents and records to gather for whoever
prepares the filing.

Constraints: this is a gathering aid and general information only, not
tax advice; rules differ by jurisdiction and change, and a qualified
adviser will review it. Never state what is deductible, taxable,
claimable or reportable. Reference no tax law, regulator or form.

Format: a table — Activity, Records to gather, Where they usually live,
Owner, Status.

Where treatment depends on local rules, write "jurisdiction-dependent —
for your adviser" instead of a conclusion.

Activities:
[PASTE]
```
*Check before you use the output:* that nothing drifted from "gather this" into "this is treated as". Strike any line stating a treatment.

**P5.2 — Categorisation queries**
*Use when:* you are cleaning a transaction listing before it goes to an adviser.
*Paste this:*
```
You are preparing a transaction listing for [ENTITY], [PERIOD], before
it goes to our tax adviser.

Task: identify the transactions described too vaguely for someone else
to categorise, and write the question to put to whoever incurred them.

Constraints: categorise nothing yourself and state no tax treatment —
this is preparation, not advice. Change and recalculate no amount.
Never infer a purpose from a supplier name.

Format: a table — Reference, Description as given, Why it is unclear,
Question to ask, Who to ask.

Leave out anything adequately described. A short list is a good
outcome.

Listing:
[PASTE]
```
*Check before you use the output:* whether purpose has been inferred from vendor names. "Software supplier, therefore software cost" needs unwinding later.

**P5.3 — Understanding a letter you have received**
*Use when:* correspondence arrives and you need to know what is being asked.
*Paste this:*
```
You are helping a finance professional understand correspondence
received by [ENTITY].

Task: tell me plainly what it appears to ask for, what it appears to
require by when, and what it does not say.

Constraints: this is a reading aid and general information only, not
legal or tax advice; procedures differ by jurisdiction and change, and
I must confirm my position with a qualified adviser. Do not tell me how
to respond, whether the position stated is correct, or what my rights
or obligations are. Name no law or authority. Work only from the words
in the letter.

Format: What it asks for; Dates and deadlines it states; What is
unclear or unstated.

Quote ambiguous passages rather than resolving them.

Letter:
[PASTE]
```
*Check before you use the output:* the deadlines, word for word against the letter. A misread date is the one error here with an irreversible consequence.

**P5.4 — Questions for your adviser**
*Use when:* you have adviser time booked and want to use it well.
*Paste this:*
```
You are preparing a finance team for a meeting with its tax adviser
about [TOPIC] at [ENTITY]. I will describe our situation.

Task: the questions to ask, ordered so the answers build on each other,
with the documents to have to hand for each.

Constraints: answer none of them. Do not hint at the likely answer, and
state no rule or treatment. This is meeting preparation only; rules
differ by jurisdiction and change.

Format: numbered questions, each with a sub-line "Bring:".

End with "Things we should tell them without being asked" — facts in my
description an adviser would want early.

Our situation:
[PASTE]
```
*Check before you use the output:* the final section. It is the most valuable part and depends on facts you may not have mentioned.

**P5.5 — Obligations calendar**
*Use when:* deadlines live in several people's heads.
*Paste this:*
```
You are building an internal compliance calendar for [ENTITY]. I will
list the obligations we know we have, with deadlines as we understand
them.

Task: turn the list into a working calendar, with the internal
preparation milestones that must happen before each external deadline.

Constraints: use only my obligations and dates. Add no obligations you
assume apply to us, and correct none of my dates — you do not know my
jurisdiction and requirements change. Anything you think I may have
omitted goes in a separate list, phrased as questions.

Format: a table — External deadline, Obligation, Internal milestone,
Days before, Owner. Sorted by date.

Open with a line stating the dates come from me and must be confirmed
each year.

Obligations:
[PASTE]
```
*Check before you use the output:* that no deadline has been silently adjusted and no obligation has appeared that you did not list.

## 6. Contracts, agreements and policy documents

Reading a contract for its finance consequences is not the same as advising on it. These prompts extract and organise. They do not interpret, and none replaces your legal adviser.

**P6.1 — Finance summary of an agreement**
*Use when:* a signed agreement lands and you need to know what it does to your numbers.
*Paste this:*
```
You are helping a finance team understand the financial mechanics of an
agreement involving [ENTITY].

Task: summarise only the provisions affecting money moving, timing, or
what must be recorded and tracked.

Constraints: this is a reading aid, not legal advice; law differs by
jurisdiction and an adviser will review the legal questions. Quote the
clause reference and operative wording for every point. Do not
interpret ambiguous drafting — flag it. State no accounting treatment.

Format: Amounts payable or receivable; Timing and triggers; Variation
and escalation; Termination and its financial consequences; Ongoing
obligations to track.

End with "Clauses I could not interpret with confidence", quoting each.

Agreement:
[PASTE]
```
*Check before you use the output:* every clause reference against the document. If the references drift, nothing else in the summary is safe.

**P6.2 — Payment terms extraction**
*Use when:* you are loading terms into a system or comparing across a portfolio.
*Paste this:*
```
You are extracting data from a contract for [ENTITY].

Task: extract the payment terms into a table for system entry.

Constraints: extract only. Do not interpret, do not normalise into
categories of your own, and never fill an empty field with what is
usual. Every value must appear in the text, with its clause reference.
If a field is not addressed, write "not stated" — never a default.

Format: a table — Field, Value, Clause reference. Fields: currency,
amount basis, invoicing frequency, payment period, late payment
consequence, price adjustment, discounts or rebates, expenses, disputed
amounts.

Below it, list any payment provision that did not fit these fields.

Contract:
[PASTE]
```
*Check before you use the output:* every "not stated", and any field with an odd clause reference. Extraction fails most in documents with unusual numbering.

**P6.3 — Obligations and dates register**
*Use when:* the contract creates things somebody must remember to do.
*Paste this:*
```
You are building an obligations register from an agreement involving
[ENTITY].

Task: list every obligation falling on us, every deadline, notice
period, renewal and expiry date, and every condition that triggers one.

Constraints: quote the clause reference and wording for each entry.
Calculate a date only where the contract states both the reference
point and the period, and show the working. Omit the other party's
obligations unless they trigger ours. Do not interpret conditional
wording — quote it.

Format: a table — Obligation, Owner function, Trigger or date, Notice
period, Clause, Wording quoted.

Flag separately any obligation whose trigger you could not determine.

Agreement:
[PASTE]
```
*Check before you use the output:* every calculated date. Notice periods interact with business-day and month-end definitions, and that is where the arithmetic goes quietly wrong.

**P6.4 — Questions for legal review**
*Use when:* legal budget is limited and you want it spent on the right clauses.
*Paste this:*
```
You are preparing a finance team for legal review of a draft agreement
involving [ENTITY]. I will paste the draft and describe the commercial
deal we believe we agreed.

Task: find where the drafting and my description do not obviously
match, and write the questions for our legal adviser.

Constraints: give no legal advice, state what no clause means as a
matter of law, and never say whether a term is standard or reasonable.
Confine yourself to: this is what you said the deal is, this is what
the words say, here is the question.

Format: a table — Commercial expectation, Clause and wording, The
mismatch, Question for counsel. Ordered by exposure as I described it.

Where drafting matches my description, say so rather than invent a
concern.

The deal, then the draft:
[PASTE]
```
*Check before you use the output:* that the expectation column reflects what you actually said, not a tidier version of it.

**P6.5 — Internal policy drafting**
*Use when:* you need a policy people will actually follow.
*Paste this:*
```
You are drafting an internal [POLICY TYPE] policy for [ENTITY]. I give
the rules we have decided, the limits we have set, and the behaviour we
are trying to change.

Task: write the policy.

Constraints: include only my rules. Add no limits, thresholds, approval
levels or exceptions of your own — if one seems missing, list it as a
question. Reference no law or regulation. Write for someone reading it
once, in a hurry. No sentence over 25 words.

Format: Purpose; Who it applies to; The rules as numbered clauses; What
to do if the rules do not cover your situation; Who owns this policy.

End with "Decisions you have not made yet".

Our decisions:
[PASTE]
```
*Check before you use the output:* the gaps list, before circulating anything. A policy with an unmade decision inside it gets tested by whoever finds the gap.

## 7. Board papers, reports and written communication

**P7.1 — Board paper structure**
*Use when:* you know what to say and not yet how to arrange it.
*Paste this:*
```
You are structuring a board paper on [TOPIC] for [ENTITY]. I will give
the decision required, what the board already knows, and the facts I
hold.

Task: propose the structure — sections, what belongs in each, roughly
how long each should be.

Constraints: structure only. Draft no content, supply no facts, suggest
no recommendation. Assume the board reads the first page properly and
the rest selectively.

Format: a numbered outline. For each section: purpose in one line, what
goes in it, target length, and whether it belongs in the paper or an
appendix.

End with "Facts you will need that you have not mentioned" — as
questions, not assumptions.

Background:
[PASTE]
```
*Check before you use the output:* the gaps list against your own knowledge. It is the closest thing here to a rehearsal.

**P7.2 — One page from twenty**
*Use when:* the paper is written and the summary is due.
*Paste this:*
```
You are writing the executive summary of the paper below. The audience
is [AUDIENCE]; the decision required is [DECISION].

Task: a summary of no more than one page.

Constraints: every statement must appear in the paper. Add nothing.
Where the paper qualifies a key point, the qualification must survive —
never simplify a hedged conclusion into a firm one. Change no figure.
Add no recommendation the paper does not make.

Format: the decision in one sentence; three to five bullets of what the
reader must know to make it; the main uncertainty; what happens next.

List separately any point where the paper is unclear about its own
conclusion.

Paper:
[PASTE]
```
*Check before you use the output:* the hedges. Summarising flattens qualified statements into confident ones, and the summary is what gets quoted back at you.

**P7.3 — The difficult email**
*Use when:* you must tell someone something they will not like.
*Paste this:*
```
You are helping a finance professional write a difficult message. I
will describe the situation, the recipient, the relationship and the
outcome I want.

Task: draft the message.

Constraints: state the substance in the first three sentences — no
warm-up. Do not apologise for facts. Do not soften a deadline or
consequence I have given, and add none I have not. No flattery, no
false warmth, no exclamation marks. Do not characterise the recipient's
likely feelings.

Format: subject line, then the message, under 200 words.

Then one alternative opening paragraph with a different balance of
directness, and a line on when each is better.

The situation:
[PASTE]
```
*Check before you use the output:* whether a commitment has crept in. Awkward drafts acquire offers of help you did not intend to make.

**P7.4 — Anticipating the questions**
*Use when:* you present tomorrow.
*Paste this:*
```
You are preparing a finance presenter for questions on [TOPIC] at
[ENTITY]. I will paste my paper and describe the audience.

Task: predict the questions, hardest first — including those from
someone who read only the summary, and those from someone who read the
appendix closely.

Constraints: do not answer them and do not draft my answers; I need to
know what I do not know. Invent no facts about our business in the
framing of a question. Where a question is prompted by something absent
from my paper, say what is absent.

Format: three groups — questions the paper answers, questions it raises
but does not answer, questions it does not anticipate at all.

Say plainly where a likely question has no available answer.

Paper and audience:
[PASTE]
```
*Check before you use the output:* the middle group. Those are the questions you will be asked and are least prepared for.

**P7.5 — Plain-English pass**
*Use when:* a document must be read by people outside finance.
*Paste this:*
```
You are rewriting a finance document for readers who are competent
professionals but not accountants.

Task: rewrite it so it can be read once and understood.

Constraints: keep every figure exactly as written and every
qualification intact. Where a technical term is unavoidable, keep it
and gloss it in brackets on first use — do not swap in a loose synonym.
Never simplify a conditional statement into an unconditional one. Add
no examples or analogies of your own.

Format: the rewritten document, then a list of the terms you glossed
and the gloss used, so I can check each.

Where a passage cannot be made plainer without changing its meaning,
leave it under "Kept as written".

Document:
[PASTE]
```
*Check before you use the output:* every gloss. A slightly wrong definition, in a document going to non-specialists, is harder to correct later than the jargon was.

## 8. Process documentation and team training

**P8.1 — Procedure from your own narration**
*Use when:* the process exists only in the hands of the person who does it.
*Paste this:*
```
You are turning a spoken description into a written procedure. Below
are notes of someone describing how they perform [PROCESS] at [ENTITY].

Task: write the procedure as numbered steps a competent newcomer could
follow.

Constraints: include only steps described in the source. Add no steps
that seem obvious. Do not reorder into a more logical sequence without
flagging it. Add no system names, field names or approvals not
mentioned. Where the speaker says "usually" or "it depends", preserve
the conditionality — do not turn it into a rule.

Format: numbered steps starting with a verb; sub-steps where the source
gives detail; a "Before you start" list.

End with "Points the description left open".

Source:
[PASTE]
```
*Check before you use the output:* the conditionals. Turning "usually we check with the manager" into "check with the manager" changes the process; deleting it changes it more.

**P8.2 — Desk instructions for a new joiner**
*Use when:* somebody starts on Monday.
*Paste this:*
```
You are writing desk instructions for a new joiner in a finance team at
[ENTITY], covering [TASK]. I will paste our procedure and say what the
joiner already knows.

Task: rewrite it for someone doing this for the first time, without our
internal shorthand.

Constraints: change no step and no sequence. Expand an abbreviation
only where I have told you what it means — otherwise mark it [EXPAND
THIS]. Invent no screen names, menu paths or system behaviour. Add no
reassurance and no encouragement.

Format: the instructions, with a "what this step is for" line under
each; then "When to stop and ask".

List anything in our procedure you could not make sense of.

Procedure and context:
[PASTE]
```
*Check before you use the output:* the "when to stop and ask" section, with the person who currently does the job. Only they can write it.

**P8.3 — Training exercises**
*Use when:* you are teaching a technique rather than a task.
*Paste this:*
```
You are designing practice exercises for a finance team learning
[TECHNIQUE OR TASK] at [ENTITY]. I will describe the team's level and
the mistakes they currently make.

Task: design [NUMBER] exercises that surface exactly those mistakes, in
increasing difficulty.

Constraints: use fictional data, clearly labelled as fictional. No
exercise may present invented figures as real market, industry or
benchmark data. Reference no real organisation. Each needs a definite
right answer, or — for a judgement exercise — a definite list of what a
good answer must address.

Format: for each, the scenario, what the learner produces, the mistake
it surfaces, and the marking notes.

If a mistake cannot be surfaced by an exercise, say so.

Team and mistakes:
[PASTE]
```
*Check before you use the output:* the marking notes. Vague ones produce an argument rather than learning.

**P8.4 — Handover note**
*Use when:* somebody is leaving, or going on long leave.
*Paste this:*
```
You are building a handover note for [ROLE] at [ENTITY]. I will
describe what the role does, in whatever order it comes to me.

Task: organise it into a handover document and identify what is
missing.

Constraints: use only what I give you. Do not assume responsibilities
from the job title. Assign no deadlines or contacts I have not named.
Where I have been vague, keep my words and mark it "needs detail".

Format: Recurring tasks by frequency; One-off items in progress with
status; Who to contact for what; Access required; Known problems and
workarounds; Things only this person knows.

The last section matters most. Prompt me with questions to fill it.

What the role does:
[PASTE]
```
*Check before you use the output:* the questions it puts to you, and answer them before the person leaves. Afterwards, the note is whatever it is.

**P8.5 — Explaining a spreadsheet to its future maintainer**
*Use when:* a model has grown and one person understands it.
*Paste this:*
```
You are documenting a spreadsheet formula for a future maintainer.
Below are the formula, the sheet layout, and what the calculation is
meant to achieve.

Task: explain what the formula actually does, step by step, and whether
that matches my description of the intent.

Constraints: work only from the formula text and the layout described.
Assume no ranges, named ranges or sheet contents I have not given. Do
not rewrite the formula unless asked. Where an edge case cannot be
determined from what I provided, say so.

Format: what it does in one sentence; a numbered breakdown from the
innermost operation outwards; then Edge cases — blanks, errors, text
where a number is expected, ranges that grow.

End with "Where this may not match your stated intent".

Formula, layout and intent:
[PASTE]
```
*Check before you use the output:* the edge cases, by testing them in a copy of the file. An explanation of a formula is a hypothesis until the spreadsheet agrees.

## Building your own

Every prompt above is the same six parts in the same order. Once you see the frame you can write your own in about two minutes.

| Part | What it does | Typical failure if you omit it |
|---|---|---|
| Role | Sets who is speaking, and to whom | Generic writing pitched at nobody |
| Task | States the single job | Several half-done jobs |
| Context | Supplies the facts only you have | Plausible invention filling the gap |
| Constraints | Rules out what you do not want | Added figures, added causes, added cheer |
| Format | Names the shape of the output | Retyping it by hand afterwards |
| Uncertainty rule | Says what to do when it does not know | Confident, fluent, wrong |

The last is the part people leave out, and the part that separates a tool from a liability. "If you are unsure, say so" is the weak version. The strong ones name the behaviour: put unclassifiable items in a separate list; quote the clause you could not interpret; state what information you would need; say plainly that you cannot reconcile the components to the total. Give it somewhere to put its ignorance and it will use it. Give it nowhere and it will smooth the gap over with something that reads well.

Two habits are worth forming. Write the check before you write the prompt — decide what would be wrong in the output and how you would spot it. If you cannot answer that, you are not ready to use the output for anything that matters. And keep your prompts in a file the team can see and improve, with a line under each recording what went wrong the last time someone used it. A prompt library nobody edits is a library of first attempts.
