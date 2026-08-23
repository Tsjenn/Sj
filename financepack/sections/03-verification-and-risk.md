Everything in this section is general information, not legal,
regulatory, tax or professional advice. Rules differ by jurisdiction,
firms differ in what they permit, and both change. Check your own
position with your regulator, your professional body and, where it
matters, your own advisers.

## Part One — The Three-Check Rule

You already have a review habit, tuned over years to the mistakes
humans make: transposed digits, a stale opening balance, a paragraph
copied from last year and not updated. AI output fails differently. It
fails smoothly. The wrong number is formatted correctly, sits in the
right column, and is surrounded by three that are right. The invented
source has a plausible title.

So the habit needs a small extension, not a replacement. Three checks,
in order, every time output leaves your hands: **the figures, the
sources, the reasoning.**

The order matters. Figures first: a wrong figure makes everything
downstream irrelevant. Sources second: that is where fabrication hides.
Reasoning last, because it takes the most thought, and you should not
spend that on a document that has already failed.

The whole thing should take a few minutes on short work and under half
an hour on something substantial. If it would take longer, the work was
the wrong shape to give to a tool.

### Check one — the figures

**What you do.** Take every number and trace it back to where it came
from. Not "does it look right" — trace it. Open the source file. Find
the figure. Match it. Then check the arithmetic between figures:
components add to the total, the variance equals the difference,
percentages are of the base you think, periods compared are the same
length.

Numbers you did not supply get harder treatment. A figure that was not
in your input came from somewhere you cannot see. Delete it or verify it
independently. There is no third option.

**What it catches.** Numbers altered in transit — rounded when they
should not have been, pulled from the wrong row, carried from one entity
to another, restated to a different currency without saying so. Totals
that do not foot. Percentages calculated the wrong way round.
Prior-period figures that quietly became current-period. Numbers
invented to fill a sentence that needed one.

**What it misses.** A number faithfully copied from a source that is
itself wrong: the check verifies transmission, not truth. It also misses
the number that should be there and is not — an omitted provision, a
missing intercompany line, a segment left out of a total you did not
think to foot. Absence is harder to see than error.

**How long.** A minute or two per page of numbers. If you cannot trace a
figure inside about thirty seconds, that is not a slow check, it is a
finding — write it down and go back to whoever produced it.

A prompt that makes this check faster, because it forces the output to
show its own working:

```
Before the answer, produce a table of every number you are about to
use. Columns: the number, the exact label or cell reference it came
from in the material I gave you, and one of these two words —
"supplied" if it came from my material, "derived" if you calculated
it. For anything derived, show the calculation. Do not include any
number you cannot place in one of those two categories. If a figure I
need is missing from my material, say so and leave it blank rather
than estimating it.

Material: [PASTE OR ATTACH]
Task: [WHAT YOU WANT PRODUCED]
```

You still trace the figures, but now against a list the tool has
committed to, which is faster than hunting through prose. The "derived"
rows tell you which calculations to re-perform.

### Check two — the sources

**What you do.** For every factual claim that is not a figure — a rule,
a treatment, a deadline, a definition, a contractual term, "the standard
requires", "market practice is" — find the source and read it yourself.
The primary document, not a summary of it. If the output names a source,
confirm it exists, confirm it says what the output says it says, and
confirm it is current.

If the output does not name a source, the claim has no source. Treat it
as a hypothesis to prove or drop.

**What it catches.** Confident references to things that do not exist,
or that exist but say something else. Rules described as they were years
ago. Guidance from one jurisdiction presented as though it applies in
yours — common, and easy to miss, because the language of finance is
shared across borders while the rules are not. Thresholds and dates that
have moved. Requirements that apply to a class of entity yours is not
in.

**What it misses.** A source that is real, current, correctly quoted
and beside the point — relevance is a judgement no check automates. Also
the source that is right for your jurisdiction and wrong for your
client's, and the well-known position with an exception your client sits
inside.

**How long.** Budget two to five minutes per claim you actually rely
on. That sounds heavy until you notice how few claims in a document
carry weight. Mark the ones that do — the ones a reader would act on, or
that would appear in a complaint — and check those properly. Skimming
twelve claims is worth less than checking three.

A useful move here is to separate the drafting from the sourcing:

```
List every factual assertion in the text below that is not a number,
one per line. For each, mark it "verifiable" if a reader could check it
against a document, or "judgement" if it is an opinion or an inference.
For each verifiable assertion, state what kind of document would settle
it. Do not tell me the answer, do not cite anything, and do not add
assertions that are not already in the text.

Text: [PASTE THE DRAFT]
```

That gives you a checking list rather than a citation list — more
honest, because it does not invite the tool to produce references, which
is where fabrication lives.

### Check three — the reasoning

**What you do.** Close the output. In your own words, state the
argument: the conclusion, what it depends on, and what would have to be
true for it to hold. Then reopen it and compare. You are looking for
three things — a step asserted rather than argued, an assumption never
stated, and a conclusion wider than the evidence under it.

Then invert it: what is the strongest argument against the conclusion?
If you cannot construct one, you do not yet understand the position well
enough to send it.

**What it catches.** Confident conclusions built on one unrepresentative
period. Correlation dressed as cause — "margin fell because of the
pricing change", when three things changed that quarter. Recommendations
that quietly assume the reader's circumstances. Analysis that answers a
slightly different question from the one asked — the most common
failure, and the hardest to see, because the answer is good.

**What it misses.** Anything that depends on knowing the client, the
history, the personalities and the thing the last auditor flagged. It
misses reasoning that is sound in general and wrong here. And it misses
your own blind spots — you are checking with the head that approved the
approach.

**How long.** Five to ten minutes on anything carrying a
recommendation; less on descriptive work. It is the check people skip
when busy, and the one that catches the errors that embarrass people:
figure errors get found by the next reviewer, reasoning errors get found
by the client.

The prompt that helps here is the one that argues with you:

```
Argue against the conclusion in the text below. Give the three
strongest objections a well-informed sceptic would raise, the
assumption each objection attacks, and what evidence would settle it.
Do not soften them and do not offer a balanced view. Do not rewrite the
text.

Text: [PASTE THE DRAFT]
```

Read the objections as prompts for your own thinking, not as findings.
Some will be weak. The point is to make the shape of the argument
visible so you can test it.

### The verification card

Print this. Pin it where the work gets reviewed. It is deliberately
short, because a checklist nobody completes is worse than no checklist —
it produces the paperwork of assurance without the assurance.

---

**THE THREE-CHECK CARD**

*Before this leaves my hands.*

**1. FIGURES** — *trace, do not glance*

- Every number traced to a named source file, cell or document
- Totals footed; variances re-performed; percentages checked against the right base
- Periods, entities and currencies confirmed to be the ones stated
- Any number I did not supply: verified independently, or deleted

**2. SOURCES** — *read the original, not the summary*

- Every claim I am relying on has a source I have opened myself
- The source is current, and applies in this jurisdiction and to this entity
- Unsourced claims: proved or removed
- Nothing quoted that I have not read in full

**3. REASONING** — *state it without looking*

- I can state the conclusion and what it depends on, in my own words
- Every assumption is on the page, not in my head
- The conclusion is no wider than the evidence under it
- I can make the strongest case against it — and it still stands

**SIGN-OFF**

- This answers the question that was actually asked
- I can defend every line of it, unaided, to someone who challenges it
- Where I am uncertain, the document says so
- If this is wrong, I am the one who is wrong. That is correct.

Checked by: `[NAME]`  Date: `[DATE]`  Time taken: `[MINUTES]`

---

Log the time taken — for you, not for anyone else. After a fortnight
you will know which work is genuinely faster with a tool and which is
only faster until the checking starts. It is the only productivity
figure in this pack, and the only one worth having, because you measured
it yourself.

### What the three checks do not catch

They do not catch everything, and a pack that claimed otherwise would be
the sort of thing this pack exists to be an alternative to. What remains
after all three checks are done properly:

**The plausible omission.** The checks look at what is on the page. None
looks for what should be there and is not. A tool that summarises fifty
documents and silently drops the one that matters produces output that
passes every check.

**The correct-but-inapplicable.** Right rule, right numbers, wrong
client. Nothing in the checks tests fit.

**Compounding.** Verified output becomes input to the next piece of
work, and the check does not repeat. Three steps on, the assumption is
load-bearing and nobody remembers it was an assumption.

**Drift.** The tenth document of the day gets a thinner check than the
first, and reviewing fluent output is not the same mental act as writing
it. Read enough finished-looking work and the reading gets lighter
without your deciding it should.

Three things to do about the residual risk, none of which eliminates it:

1. **Write down what you assumed, and keep the input.** A short
   assumptions block at the top of anything you pass on, and the
   material you supplied stored alongside the output. If you cannot
   reconstruct what the tool was given, you cannot later work out how it
   went wrong.
2. **Vary who checks.** The person who framed the task is the worst
   person to check it, and the second-worst is anyone who agrees with
   them. Get fresh eyes on anything that carries real consequence.
3. **Set a ceiling.** Decide, in advance and in writing, the value or
   sensitivity of work above which the tool is not used at all. Deciding
   in the moment, under deadline, is deciding badly. Part Two is a
   starting draft of that ceiling.

## Part Two — Ten Places Not to Use It

There is a way of writing about this that treats every limitation as a
temporary inconvenience soon to be engineered away. This is not that.
Some of what follows may change; most will not, because the reason is
not capability. It is that a duty sits on a person, and cannot be
delegated to something that cannot be held to it. For each: the
situation, why the tool fails there in particular, and what to do
instead.

### 1. Signing, certifying or expressing an opinion

**The situation.** Anything where your name, signature or firm goes on a
document as the person vouching for it — accounts, certificates,
confirmations, formal opinions, representations a third party will act
on.

**Why it fails.** Your signature is not a statement that the words are
good. It says *you* did the work and *you* stand behind it. The
signature is about accountability, not text, and a tool cannot supply
accountability. Sign something you did not verify and the signature is
false, whether or not the content turns out to be right.

**Instead.** Use a tool, if at all, on drafting and checking well before
signature — never on the substance of what is certified. If a tool
touched the draft, the person signing must have re-performed the
underlying work themselves, not reviewed the prose.

### 2. Anything you cannot verify

**The situation.** The output is in a subject, language, jurisdiction or
technical area where you cannot check whether it is right.

**Why it fails.** Every safeguard in Part One assumes a checker who can
tell good from bad. Remove that and the tool is not an assistant, it is
an oracle. And fluency scales with unfamiliarity: output in an area you
do not know reads *more* convincing, because you cannot see the joins.

**Instead.** Either learn enough to check it, find someone who can, or
do not send it. A tool used to orient yourself in an unfamiliar area
gives you a list of things to look up, never the answer. The tell: if
you could not answer a follow-up question without going back to the
tool, you do not own the work.

### 3. Live disputes, investigations and privileged matters

**The situation.** Litigation, arbitration, a regulatory investigation,
a disciplinary process, a dispute with a former employee, anything where
a lawyer is involved or is about to be.

**Why it fails.** Two reasons, both serious. In a contested matter the
working papers may become visible to the other side, and a tool-produced
draft — including discarded versions and the framing of your questions —
records how you thought about the case. And protections attaching to
communications with your lawyers can be fragile; routing the same
material through a third-party system may affect them, depending on your
jurisdiction.

**Instead.** Take instructions from the lawyers on the matter, in
writing, before anything goes near a tool. Assume until told otherwise
that nothing about a live dispute goes into any external system. This is
general information, not legal advice; the rules are jurisdiction-
specific and consequential.

### 4. Decisions about a named individual

**The situation.** Pay, promotion, redundancy, hiring, performance
ratings, discipline, creditworthiness, a reference, a decision to end
someone's contract.

**Why it fails.** The decision has to be explicable to the person
affected and possibly to a tribunal or a regulator, and "the system
suggested it" is not an explanation. The tool has no access to the
context that matters — the year they had, the thing their manager did,
the reason the numbers look like that. And several jurisdictions place
obligations around automated processing of personal data and decisions
that significantly affect people; those vary, and you need to know your
own.

**Instead.** Make the decision yourself, on evidence you can point to,
and write your reasons before drafting any communication. A tool may
make an already-made decision clearer or kinder in the telling. It must
not help you reach it, and it must not receive the person's personal
data.

### 5. Anything where the client's data cannot leave your control

**The situation.** Data covered by a confidentiality undertaking, a data
processing agreement naming permitted sub-processors, a client policy
prohibiting external processing, or a requirement to keep information
in-jurisdiction. In practice also: identifiable personal data, bank
details, board material before it is public, price-sensitive
information.

**Why it fails.** Not because the tool is careless. Because pasting the
data into it is a disclosure to a third party, and you either had
permission for that or you did not. The tool's own security is not the
question; whether you were allowed to send it is, and that is settled by
contracts you signed before the tool existed.

**Instead.** Check the engagement terms and data agreements before the
work starts, not during it. Where the answer is no, either work without
the tool or use one deployed inside your own environment under terms you
have read. When in doubt, redact: much analytical work runs on structure
and anonymised figures, without names, account numbers or identifiers
leaving your systems.

### 6. Matters where a professional duty attaches to you personally

**The situation.** Independence and conflict assessments. Ethical
judgements. Whether to accept or resign from an engagement. Whether
something must be reported, and to whom. Anything your professional body
treats as a matter for your own judgement.

**Why it fails.** These duties sit on you as a person precisely because
they exist to be exercised when it is uncomfortable — when the client is
large, the fee is significant and the easy answer is available. A tool
produces the conventional answer, usually the comfortable one, and has
nothing at stake. That is the problem: the duty exists because you do.

**Instead.** Decide it yourself, document the reasoning at the time in
your own words, and consult a human — a partner, an ethics helpline,
your professional body — where you are unsure. The written record of
your reasoning is the point, and it has to be yours.

### 7. Suspicions of fraud, error or dishonesty

**The situation.** Something looks wrong and a person may have done it
deliberately.

**Why it fails.** These situations carry reporting obligations that vary
by jurisdiction and can be time-critical, and some carry prohibitions on
telling anyone what you suspect. A drafting tool cannot know your
obligations or who you are permitted to speak to. There is also a
practical trap: writing up a suspicion in a system you do not control
creates a record you may not be able to retrieve, delete or explain.

**Instead.** Follow your firm's escalation procedure immediately — and
if you do not know it, find out today rather than the day you need it.
Take advice on your reporting obligations from someone qualified to give
it. Keep your own note, written at the time and held locally. Nothing
external, nothing informal.

### 8. Advice that turns on the specific rules of a place

**The situation.** Tax positions, filing obligations, statutory
deadlines, entity-specific reporting requirements, licensing — anything
where the answer changes when you cross a border or a threshold.

**Why it fails.** These rules are numerous, local and revised often.
Material describing them ages badly and is uneven across jurisdictions,
so the answer reflects the places most written about rather than the
place you are in. That is dangerous, because the *structure* of the
answer is usually right — the right considerations, in the right order —
while the threshold, rate or date inside it is wrong or foreign.

**Instead.** Use the primary source published by the relevant authority,
or a subscription service that states its currency date. A tool may help
you frame the question or draft the covering letter. The rule itself
comes from the source every time, and you note the date you checked.

### 9. The record of what happened

**The situation.** Minutes, file notes, attendance notes, records of
what was said and decided.

**Why it fails.** A record is not a summary. Its value is that it is a
first-hand account by someone present — exactly what a generated version
is not. A tool asked to tidy up rough notes smooths them, fills gaps
with what usually happens, and turns the awkward half-sentence someone
said into a clean sentence they did not. In a dispute that difference is
everything, and the smoothing is invisible once done.

**Instead.** Write records yourself, close to the event, in plain
language, including the parts that are unresolved or unflattering. If
you use a transcription tool, keep the transcript as the record and mark
it as such — and check what your policy and local law say about
recording people, which is a real question, not a formality.

### 10. Anything you would not be able to defend line by line

**The situation.** The general case. You are about to send work you
could not walk through, unaided, if the recipient rang and asked why.

**Why it fails.** Not a limitation of the tool. A limitation of the
arrangement. Work you cannot defend is work you have not done, and
whether a tool, a junior or a template produced it changes nothing about
your position.

**Instead.** Either do the work until you can defend it, or say plainly
that you have not. "I have not verified this — it is a starting point"
is a perfectly professional sentence, and the honest one. Most of the
trouble people get into with these tools starts with an unwillingness to
say it.

## Part Three — Assessing a Tool Before It Touches Client Data

Marketing pages are written to be reassuring. Contracts are written to
be enforceable. They are different documents and routinely say different
things. This section is about getting answers in the second kind.

Work through the table below with the vendor, or with your own IT team
if the tool is deployed internally. Two rules make it worth doing. Get
the answers in writing, with the clause reference: "yes, of course" is
not an answer, "clause 8.3 of the data processing addendum" is. And if a
question comes back vague after you have asked twice, record the
vagueness as the answer. It is information.

Fill in the third column with what they said and the fourth with your
own decision — a judgement your firm makes, not one a checklist makes
for you.

### What happens to our input

| # | Question to ask | Their answer | Acceptable? |
|---|---|---|---|
| 1 | Is anything we submit used to train or improve your models, or anyone else's? | | |
| 2 | If so, how do we switch it off, is the switch on our plan, and does it cover every feature? | | |
| 3 | Which third parties process our input — model provider, host, subcontractors? Name them all. | | |
| 4 | Do you keep our input for safety, abuse or quality review? Who sees it, and for how long? | | |
| 5 | Does any of this differ for uploaded files or connected data sources, versus typed text? | | |

### Where it is stored, and for how long

| # | Question to ask | Their answer | Acceptable? |
|---|---|---|---|
| 6 | Which countries is our data stored, processed and backed up in? List them all. | | |
| 7 | Can we require a named region, and is that contractual or a setting you can change? | | |
| 8 | How long is our input retained by default, and can we shorten it? | | |
| 9 | How long does it persist in backups, logs and caches after deletion? | | |
| 10 | Is it encrypted at rest and in transit, and who holds the keys? | | |

### Who at your end can see it

| # | Question to ask | Their answer | Acceptable? |
|---|---|---|---|
| 11 | Which of your staff can access our content, in what circumstances, on whose approval? | | |
| 12 | Is that access logged, and can we see the log? | | |
| 13 | Do your staff sign confidentiality undertakings covering our clients' information? | | |
| 14 | If a government or law-enforcement request reaches our data, will you tell us where permitted? | | |
| 15 | Have you had an incident affecting customer content, and what is your notification period? | | |

### What happens when we leave

| # | Question to ask | Their answer | Acceptable? |
|---|---|---|---|
| 16 | On termination, what is deleted, when, and how is deletion evidenced? | | |
| 17 | Can we export content, history and configuration in a usable format, as a contractual right? | | |
| 18 | What survives termination in your favour: licences to our content, aggregated data, derived material? | | |
| 19 | If you suspend or terminate our account, do we still get our data out, and for how long? | | |
| 20 | If the service is discontinued, what notice do we get? | | |

### The contract versus the marketing page

| # | Question to ask | Their answer | Acceptable? |
|---|---|---|---|
| 21 | Which document governs — terms, data processing addendum, security page, sales deck? Show the order of precedence. | | |
| 22 | Which of the claims on your website appear as obligations in the contract? Name the clauses. | | |
| 23 | Can you change the terms unilaterally, with what notice, and can we exit without penalty if you do? | | |
| 24 | What is your liability cap, and what is excluded from it? | | |
| 25 | Do you accept the role of processor, on our instructions, in writing? | | |
| 26 | Do you hold current independent security certification, and may we see the report, not the badge? | | |

### What changes if you are acquired

| # | Question to ask | Their answer | Acceptable? |
|---|---|---|---|
| 27 | On a change of control, do our terms transfer unchanged, and for how long? | | |
| 28 | Is our data an asset that could be sold or transferred in insolvency or acquisition? | | |
| 29 | Do we get notice and a right to terminate on a change of control? | | |
| 30 | On a funding or ownership change, what happens to the commitments in questions 6 to 9? | | |

Two notes on using this. Question 22 produces the most silence, and the
silence is the finding. And a sensible way to handle the paperwork is to
have a tool extract, not interpret:

```
Read the attached terms and produce a table with three columns: the
question below, the exact quoted wording from the document that
addresses it, and the clause number. If the document does not address a
question, write "not addressed" — do not infer, summarise or fill the
gap. Quote verbatim. Do not tell me whether the terms are good.

Questions:
[PASTE THE QUESTIONS FROM THE TABLE ABOVE]
Document: [ATTACH THE TERMS]
```

That gives you a map of where to read. You still read the clauses
yourself, and anything that matters commercially or legally goes to
someone qualified to advise on it. Extraction is a task a tool does
well. Judging whether a liability cap is acceptable is not.

### The assessment has a shelf life

An assessment describes a supplier on the day you did it, and nothing
more. Terms are revised. Sub-processors are added. Features arrive that
handle data differently from the feature you assessed, and they arrive
switched on. Free and paid tiers can differ on exactly the points you
cared about, so an upgrade changes your position without anyone deciding
to change it. Companies are bought. Retention settings get reset by a
migration.

None of this is bad faith; it is what happens to software companies. The
consequence is that a one-off assessment filed away is a record of a
decision, not evidence of a current position.

So repeat it. Once a year for anything touching client data, and
immediately on any of these triggers: the terms change, the ownership
changes, you start using a materially new feature, your plan changes, a
client asks where their data goes, or you take on work under a stricter
confidentiality regime than usual. Keep the completed tables with the
date and the name of the person who filled them in, so the next review
is a comparison rather than a fresh start.

And keep one thing in your own hands whatever the assessment says: know
which of your clients' information must never be submitted to an
external system at all, write that list down, and make sure everyone who
could paste something has read it. Vendor assurances describe what
someone else promises to do. That list describes what you control.
