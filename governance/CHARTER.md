# NXS-Bench Advisory Board Charter

## Status

This charter is drafted in advance so the governance model is ready when
NXS-Bench reaches **10 external contributions**. Until that threshold is met,
the board is not yet seated and these rules operate as pre-approved formation
documents rather than a live governing body.

If six months pass after the NXS-Bench v1.0 launch without reaching the
10-contribution threshold, NXS evaluates one of two actions:

1. lower the threshold with public justification, or
2. actively recruit contributions through academic partnerships and conference
   presentations.

## Purpose

The Advisory Board exists to ensure that NXS-Bench remains a fair, unbiased,
and scientifically rigorous benchmark for AI agent evaluation.

## Scope of Authority and Veto Power

The board approves:

- new benchmark domains
- methodology changes
- scoring rubric updates
- scenario retirement and rotation policies

The board may veto any change that would advantage NXS unfairly, including:

- inflating NXS results through methodology changes
- weakening scenarios that NXS currently fails
- removing or reshaping score reporting to make NXS look better without a
  defensible methodological reason

The board does **not** control:

- day-to-day maintenance
- bug fixes
- documentation updates
- routine scenario contributions that go through normal pull request review

## Composition

- 3-5 external voting members
- at least 1 academic researcher
- at least 1 representative from a competing or otherwise different agent
  platform
- at least 1 enterprise practitioner who evaluates AI systems in production
- 1 NXS liaison seat to provide technical context

The NXS liaison may participate in discussion but is non-voting whenever a
decision presents a conflict of interest for NXS.

## Terms

- External members serve 2-year terms.
- Terms are staggered so the full board does not rotate at once.
- Initial appointments may use shorter 1-year terms for a subset of seats to
  establish the stagger.

## Selection and Renewal

- Candidates may be nominated by existing board members or the community.
- Appointments are confirmed by majority vote of current non-recused voting
  members.
- Vacancies are filled using the same nomination and confirmation process.
- Membership changes are published in `governance/MEMBERS.md`.

## Voting Rules

- Quorum: 3 non-recused voting members
- Standard approval rule: simple majority of votes cast
- Async votes run through GitHub Issues using the Advisory Board vote template
  in `.github/ISSUE_TEMPLATE/advisory-board-vote.md`
- Votes remain open long enough to allow participation across time zones unless
  an emergency decision is required

## Conflict of Interest Policy

- Board members must disclose current employers, investments, advisory roles,
  and direct benchmark-related commercial interests.
- A board member from Platform X must recuse themselves from votes that
  directly affect Platform X's results.
- The NXS liaison is automatically recused from any vote where NXS has a direct
  competitive interest.
- Recusals are documented in the vote issue and in the published minutes.

## Operations

- Quarterly meetings are held virtually.
- The standing agenda covers benchmark health, new domain proposals,
  methodology change proposals, and community growth metrics.
- Meeting minutes are published under `governance/minutes/`.
- All board decisions are public and documented with rationale.

## Transparency

- Charter updates are public.
- Membership is public.
- Async vote records are public.
- Quarterly minutes are public.

## Amendments

This charter may be amended only through a board-approved vote that meets
quorum and documents the rationale publicly.
