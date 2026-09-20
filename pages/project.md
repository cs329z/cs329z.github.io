---
title: Course Project
---

The final project is the main assignment of the course. Working in teams, you will design, build, and
evaluate an agentic system of your own choosing over the quarter. Projects must relate in a reasonable way
to at least one of the central topics of the course: building agents (retrieval, tool use, memory,
multi-agent systems, optimization), the data agents need, or evaluating and making agents safe. Beyond
that, the choice of domain is yours. Example project ideas:

- A syllabus reader that extracts deadlines and adds them to your calendar
- A course-schedule optimizer for next quarter
- A research-paper discovery and summarization agent
- A campus-event aggregator and recommender
- A coding agent specialized for a particular codebase, framework, or language
- A rigorous evaluation of an existing agent that surfaces its failure modes

Whatever you build, we expect rigor in how you evaluate it. Simply building a tool and showing that it
works in one instance will not score highly. Strong projects define their evaluation early: what tasks
the agent is expected to handle, where the data for those tasks comes from and how it was collected, what
counts as success, and how success is measured (code-based graders, LLM-as-judge, human ratings, or a
combination). Evaluate over a meaningful set of tasks, report results with appropriate baselines and
comparisons, and analyze where and why the agent fails.

### Teams & Mentors

Projects can be done in teams of 1–3 people. In our experience, teams of 3 lead to the best outcomes, so we
encourage you to form a team of that size. Each team will be assigned a mentor from the teaching team, who
will give feedback on all project-related work and generally be available throughout the quarter.

### Submission Format

The proposal, midway report, and final report must use the
[ICLR submission format](https://www.overleaf.com/latex/templates/template-for-iclr-2025-conference-submission/gqzkdyycxtvt)
and follow the ICLR requirements, except where we specify otherwise below. Page limits exclude references.

### Code Submission

With the midpoint demo and the final report, you must also submit a link to a GitHub repository containing
your project's code. The repository must include a README that walks a reader through running the project:
how to install dependencies, configure any API keys or credentials, run the agent, and reproduce the
evaluation reported in your paper. Write it so that a classmate who has never seen your code can get the
system running. Your mentor will use the README when grading, and it will also facilitate peer review of
your project.

### Milestones

Exact dates and times are listed in the [Deadlines](#deadlines) table above, and the weight of each
milestone is listed under [Grading](#coursework).

#### 1. Project Proposal (Week 3)

A short paper (1–2 pages) that explains the problem your agent will address, why it matters, and how it fits
within the scope of CS329Z. Briefly summarize existing work and compare it to your idea to justify how your
project builds on it. The goal is to clearly define a direction; this is not a full literature review, but a
focused justification of what you want to work on and why. The ideal is to keep the same topic for the
proposal and the final project, but it is fine if your direction changes over time. The proposal is graded
on its own merits regardless of what you end up building. Suggested structure:

1. **Problem Definition and Motivation:** What is the core problem your agent will address? Why is it
   meaningful, and to whom? Why is it a good fit for an agentic system rather than a simpler solution?
2. **Comparison with Existing Work:** What have past systems or papers tried in this area, and where do they
   fall short? This might be due to limitations in model capability, missing tools or data, poor
   reliability, or a lack of evaluation.
3. **Next Steps and Direction:** A possible approach or system design for how you plan to tackle this
   problem, and how you would know if it works.
4. **References:** Entries should appear alphabetically and give at least full author name(s), year of
   publication, title, and outlet if applicable (e.g., journal or proceedings name).

#### 2. Midpoint Demo & Midway Report (Week 7)

The midpoint demo is a recorded video of your system, submitted rather than presented in class; a working
prototype is expected. Alongside the video, submit a link to your GitHub repository with a README for running
the prototype (see [Code Submission](#project) above). The midway report is a short,
structured paper (3–4 pages) designed to help you establish your core system and evaluation framework. No
prior-work discussion is needed. Grading is based mainly on the Environment & Data, Methods, and Summary of
Progress sections. Required sections:

1. **Research Questions or Problem Specification:** A statement of the project's core research questions,
   or, for application-oriented projects, a specification of the problem the agent solves and for whom (one
   paragraph).
2. **Environment & Data:** A description of the environment, tools, and dataset(s) the agent will operate
   on, and the data you will use to evaluate it, including how that evaluation data is collected or
   constructed and what success criteria and metrics you will use.
3. **Methods:** A description of the agent architecture and approaches you are using, and a preliminary
   description of the approach that will be the focus of your investigation. At this stage, some aspects
   may not yet be worked out; preliminary descriptions are fine.
4. **Summary of Progress:** What you have done, what you still need to do, and any obstacles or concerns
   that might prevent your project from coming to fruition.
5. **References:** In the same format as for the proposal.

#### 3. Final Report & Final System Demo (Finals Week)

The final system demo is presented live on Demo Day during finals week. The final report is an 8-page paper in
ICLR submission format, adhering to ICLR guidelines concerning references, layout, supplementary
materials, and so forth. Submit it together with a link to your final GitHub repository, whose README must
let a reader run the system and reproduce your results. The report is graded out of 20 points. Required
components:

1. **Introduction** (2 points)
2. **Related Work** (1 point)
3. **Environment & Data** (1 point)
4. **Methods** (5 points): The agent's architecture, components, and design decisions.
5. **Results** (10 points): Your evaluation of the system over a meaningful set of tasks, with baselines or
   comparisons, and an error analysis of its failure modes. A single working example is not an evaluation.
6. **Discussion / Conclusion** (1 point)
7. **Safety & Ethical Considerations:** An explicit discussion of any potential safety or ethical issues,
   such as the implications of the project, the use of the data, the actions the agent is permitted to
   take, and potential applications of your work. Here are some recommendations from
   [ACL's ethics guidelines](https://2021.aclweb.org/ethics/Ethics-FAQ/): "Ethical questions may arise when
   working with a variety of types of computational work with language, including (but not limited to) the
   collection and release of data, inference of information or judgments about individuals, real-world
   impact of the deployment of language technologies, and environmental consequences of large-scale
   computation."
8. **Authorship Statement:** At the end of your paper (after the Acknowledgments section in the template),
   include a brief authorship statement explaining how the individual authors contributed to the project.
   You are free to include whatever information you deem important to convey. For guidance, see the
   second page, right column, of this [guidance for PNAS authors](http://blog.pnas.org/iforc.pdf). We
   require this largely because we think it is a good policy in general. This statement is required even
   for singly-authored papers, because we want to know whether your project is a collaboration with people
   outside of the class. Only in extreme cases, and after discussion with the team, would we consider giving
   separate grades to team members based on this statement.
9. **References**

The Safety & Ethical Considerations, Authorship Statement, and References sections are required but not
separately scored; a missing section will cost points.
