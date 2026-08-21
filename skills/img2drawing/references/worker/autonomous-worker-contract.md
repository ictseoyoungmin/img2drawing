# Autonomous worker contract

The skill must carry the workflow knowledge that was previously supplied through user corrections.

The worker is expected to:
- discover stage intent from the skill;
- generate its own review artifacts;
- identify concrete mismatches;
- select corrections;
- repeat hardening;
- decide routine stage advancement;
- reopen earlier stages when required.

The user is not a required visual critic in the normal loop.

## Escalate only for target ambiguity
Ask the user only when:
- the source cannot be inspected;
- the requested drawing target is ambiguous;
- two requirements conflict and no safe interpretation exists.

Poor drawing quality is solved through re-observation and hardening, not by outsourcing critique to the user.
