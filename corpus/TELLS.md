# Tells: what the model writes that these people did not

Human side: 382 documents, 325,653 words, all published before 2012. AI side: 200 documents, 137,232 words, generated from the same titles at the same lengths.

Ranked by z-scored log-odds with an informative Dirichlet prior, so a phrase has to be both lopsided *and* well evidenced to place. Rates are per 10,000 words. **Docs** is the share of documents on each side containing the term at least once — a tell that is common across many documents is worth more than one a single document repeats. A term must appear in 8 documents to be ranked.

Markdown syntax is stripped before counting: the human corpus was extracted from HTML and lost its formatting, so headings, bold and bullets cannot be compared fairly here.

## The tells worth acting on

Frames rather than words, because a frame survives paraphrase. **Docs** is the share of documents containing it at least once — the number that matters, since a tell you can only see by counting repetitions inside one piece is not much of a tell.

Checked separately against each generating model, so a habit of one model does not get mistaken for a property of machine prose.

| frame | AI docs | human docs | AI /10k | human /10k | opus-5 | sonnet-5 | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| em dash | 98% | 48% | 108.7 | 23.9 | 99% | 97% | the single widest gap; not wrong, but a habit |
| first person (I, my, me) | 44% | 93% | 36.4 | 191.3 | 55% | 34% | INVERSE: people write from experience |
| nobody / no one | 60% | 13% | 16.6 | 2.1 | 70% | 51% | rhetorical straw man |
| actually | 78% | 28% | 26.5 | 4.8 | 72% | 83% | the corrective register |
| worth (…ing/it/doing) | 64% | 15% | 15.8 | 2.5 | 60% | 68% | 'worth noting', 'worth the' |
| isn't / aren't / wasn't | 76% | 31% | 30.1 | 7.8 | 68% | 83% | negation-led contrast |
| rather than | 56% | 15% | 14.7 | 2.7 | 53% | 58% | contrastive framing |
| it's not X (it's Y) | 56% | 24% | 15.4 | 4.5 | 55% | 57% | the defining frame of current machine prose |
| none of this / that | 24% | 1% | 3.9 | 0.2 | 11% | 36% | the pivot-to-conclusion move |
| the ones who / that | 19% | 2% | 4.1 | 0.3 | 11% | 27% | sorting the world into two groups |
| the thing is / that | 11% | 1% | 2.1 | 0.2 | 15% | 7% | false intimacy |
| what people get wrong | 4% | 1% | 0.6 | 0.1 | 4% | 4% | contrarian opener |

## Words

| term | AI /10k | human /10k | AI docs | human docs | z |
| --- | ---: | ---: | ---: | ---: | ---: |
| `a` | 425.1 | 255.33 | 100% | 100% | 30.5 |
| `actually` | 26.5 | 4.79 | 78% | 28% | 17.8 |
| `isn't` | 22.0 | 3.72 | 69% | 19% | 16.4 |
| `it` | 157.1 | 101.03 | 100% | 95% | 15.9 |
| `every` | 28.5 | 8.05 | 80% | 35% | 15.7 |
| `is` | 210.8 | 147.06 | 100% | 97% | 15.4 |
| `the` | 596.9 | 490.00 | 100% | 100% | 15.1 |
| `real` | 20.2 | 4.61 | 68% | 26% | 14.4 |
| `worth` | 15.8 | 2.43 | 64% | 14% | 14.2 |
| `it's` | 52.5 | 25.58 | 88% | 65% | 14.0 |
| `nobody` | 14.4 | 0.80 | 56% | 5% | 14.0 |
| `because` | 38.1 | 16.06 | 78% | 53% | 13.8 |
| `not` | 79.0 | 45.26 | 100% | 79% | 13.8 |
| `what` | 65.2 | 35.96 | 92% | 75% | 13.3 |
| `gets` | 13.0 | 2.06 | 51% | 11% | 12.8 |
| `than` | 42.6 | 20.60 | 88% | 57% | 12.7 |
| `that's` | 22.3 | 7.52 | 69% | 32% | 12.5 |
| `three` | 15.4 | 3.62 | 55% | 19% | 12.5 |
| `whether` | 13.9 | 2.79 | 48% | 17% | 12.5 |
| `rather` | 15.6 | 4.45 | 58% | 22% | 11.5 |
| `question` | 14.5 | 3.93 | 48% | 19% | 11.4 |
| `team` | 14.2 | 3.81 | 44% | 13% | 11.4 |
| `thing` | 18.6 | 6.42 | 62% | 32% | 11.3 |
| `ones` | 10.9 | 2.06 | 42% | 12% | 11.3 |
| `teams` | 11.3 | 2.30 | 33% | 7% | 11.2 |
| `answer` | 11.4 | 2.43 | 40% | 14% | 11.1 |
| `built` | 10.6 | 2.06 | 50% | 11% | 11.0 |
| `wrong` | 12.7 | 3.44 | 44% | 18% | 10.7 |
| `none` | 7.9 | 0.98 | 42% | 8% | 10.3 |
| `founders` | 7.7 | 0.92 | 22% | 3% | 10.2 |
| `where` | 25.6 | 12.13 | 70% | 43% | 10.1 |
| `cost` | 10.9 | 3.10 | 40% | 13% | 9.7 |
| `actual` | 7.9 | 1.41 | 34% | 7% | 9.7 |
| `build` | 12.8 | 4.24 | 50% | 19% | 9.6 |
| `failure` | 6.7 | 0.77 | 32% | 5% | 9.6 |
| `founder` | 6.3 | 0.68 | 20% | 5% | 9.3 |
| `product` | 15.3 | 5.99 | 50% | 20% | 9.3 |
| `matters` | 6.5 | 0.89 | 38% | 6% | 9.2 |
| `genuinely` | 6.9 | 0.25 | 34% | 2% | 9.2 |
| `room` | 7.1 | 1.32 | 29% | 7% | 9.1 |
| `does` | 15.8 | 6.63 | 55% | 31% | 8.9 |
| `never` | 14.1 | 5.59 | 58% | 28% | 8.8 |
| `treat` | 5.5 | 0.43 | 26% | 3% | 8.7 |
| `discipline` | 5.5 | 0.43 | 27% | 3% | 8.7 |
| `ask` | 11.3 | 3.99 | 43% | 19% | 8.6 |

## Two-word phrases

| term | AI /10k | human /10k | AI docs | human docs | z |
| --- | ---: | ---: | ---: | ---: | ---: |
| `not a` | 14.4 | 2.30 | 52% | 15% | 13.4 |
| `rather than` | 14.7 | 2.67 | 56% | 15% | 13.2 |
| `is the` | 25.7 | 11.12 | 70% | 42% | 11.1 |
| `the thing` | 8.4 | 0.49 | 36% | 3% | 10.7 |
| `because the` | 9.0 | 1.47 | 41% | 10% | 10.5 |
| `none of` | 7.7 | 0.77 | 41% | 6% | 10.3 |
| `the ones` | 7.4 | 0.68 | 28% | 4% | 10.2 |
| `it's the` | 7.5 | 0.95 | 37% | 7% | 10.0 |
| `than a` | 7.8 | 1.38 | 38% | 9% | 9.7 |
| `and it` | 9.8 | 2.61 | 38% | 17% | 9.5 |
| `is a` | 28.9 | 15.17 | 76% | 53% | 9.4 |
| `and the` | 26.6 | 13.79 | 75% | 49% | 9.2 |
| `where the` | 7.6 | 1.72 | 35% | 11% | 8.9 |
| `the one` | 6.2 | 0.95 | 31% | 6% | 8.9 |
| `it's a` | 9.8 | 2.98 | 42% | 18% | 8.8 |
| `is not` | 13.8 | 5.77 | 45% | 27% | 8.3 |
| `a real` | 4.9 | 0.61 | 27% | 4% | 8.1 |
| `that's a` | 5.1 | 0.77 | 26% | 5% | 8.1 |
| `which is` | 8.5 | 2.70 | 42% | 17% | 8.1 |
| `not the` | 7.1 | 1.97 | 36% | 12% | 7.9 |
| `the same` | 16.8 | 8.26 | 62% | 36% | 7.8 |
| `and a` | 12.0 | 5.01 | 47% | 29% | 7.8 |
| `it the` | 5.5 | 1.20 | 28% | 8% | 7.7 |
| `the actual` | 4.3 | 0.64 | 22% | 4% | 7.4 |
| `the room` | 3.9 | 0.34 | 20% | 2% | 7.4 |
| `whether the` | 3.9 | 0.31 | 20% | 3% | 7.4 |
| `that's the` | 4.3 | 0.68 | 24% | 5% | 7.4 |
| `before you` | 4.5 | 0.83 | 22% | 5% | 7.3 |
| `and it's` | 5.1 | 1.20 | 27% | 9% | 7.2 |
| `not just` | 6.0 | 1.69 | 26% | 10% | 7.2 |
| `because it` | 5.9 | 1.66 | 28% | 11% | 7.2 |
| `the wrong` | 3.6 | 0.49 | 18% | 3% | 6.8 |
| `what the` | 5.3 | 1.47 | 29% | 10% | 6.8 |
| `there's a` | 4.7 | 1.20 | 27% | 9% | 6.7 |
| `its own` | 4.0 | 0.80 | 21% | 6% | 6.7 |
| `is worth` | 3.4 | 0.43 | 20% | 3% | 6.7 |
| `the work` | 3.6 | 0.58 | 17% | 5% | 6.7 |
| `not because` | 3.0 | 0.37 | 18% | 3% | 6.3 |
| `looks like` | 3.0 | 0.37 | 16% | 3% | 6.3 |
| `of it` | 5.2 | 1.66 | 28% | 11% | 6.3 |
| `isn't a` | 3.1 | 0.43 | 18% | 3% | 6.3 |
| `is where` | 3.2 | 0.52 | 20% | 4% | 6.3 |
| `that a` | 4.9 | 1.47 | 25% | 9% | 6.3 |
| `it isn't` | 2.9 | 0.37 | 16% | 3% | 6.2 |
| `or a` | 5.3 | 1.75 | 27% | 11% | 6.2 |

## Three-word phrases

| term | AI /10k | human /10k | AI docs | human docs | z |
| --- | ---: | ---: | ---: | ---: | ---: |
| `is not a` | 4.4 | 0.92 | 22% | 7% | 7.0 |
| `none of this` | 3.3 | 0.12 | 21% | 1% | 6.4 |
| `in the room` | 2.4 | 0.21 | 14% | 1% | 5.8 |
| `are the ones` | 2.3 | 0.15 | 12% | 1% | 5.6 |
| `rather than a` | 4.3 | 0.03 | 22% | 0% | 5.6 |
| `this is the` | 3.9 | 1.23 | 22% | 9% | 5.5 |
| `the ones that` | 2.0 | 0.12 | 10% | 1% | 5.3 |
| `the thing that` | 2.0 | 0.12 | 10% | 1% | 5.2 |
| `the ones who` | 1.9 | 0.21 | 10% | 2% | 5.1 |
| `of this is` | 1.9 | 0.21 | 13% | 2% | 5.1 |
| `that's not a` | 1.8 | 0.18 | 12% | 2% | 5.0 |
| `and it is` | 2.0 | 0.34 | 8% | 3% | 5.0 |
| `which is a` | 1.9 | 0.28 | 12% | 2% | 4.9 |
| `it as a` | 1.7 | 0.21 | 11% | 2% | 4.7 |
| `the person who` | 1.5 | 0.15 | 8% | 1% | 4.5 |
| `shows up in` | 1.5 | 0.09 | 9% | 1% | 4.5 |
| `a set of` | 2.0 | 0.52 | 10% | 4% | 4.4 |
| `the shape of` | 1.5 | 0.06 | 10% | 1% | 4.3 |
| `the gap between` | 1.5 | 0.06 | 10% | 1% | 4.3 |
| `is the one` | 1.3 | 0.09 | 9% | 1% | 4.3 |
| `the one that` | 1.4 | 0.06 | 10% | 1% | 4.2 |
| `version of this` | 1.2 | 0.06 | 8% | 1% | 4.1 |
| `no amount of` | 1.1 | 0.09 | 8% | 0% | 3.9 |
| `the cost of` | 2.1 | 0.71 | 11% | 5% | 3.9 |
| `matters more than` | 1.4 | 0.03 | 10% | 0% | 3.8 |
| `this isn't a` | 1.1 | 0.06 | 8% | 1% | 3.8 |
| `none of them` | 1.1 | 0.15 | 6% | 1% | 3.8 |
| `start with the` | 1.0 | 0.09 | 6% | 1% | 3.8 |
| `what happens when` | 1.2 | 0.21 | 7% | 2% | 3.7 |
| `the single most` | 1.0 | 0.15 | 7% | 1% | 3.6 |
| `not just a` | 0.9 | 0.12 | 6% | 1% | 3.6 |
| `used to be` | 1.0 | 0.18 | 5% | 2% | 3.5 |
| `instead of a` | 1.0 | 0.18 | 6% | 1% | 3.5 |
| `every one of` | 0.9 | 0.09 | 5% | 1% | 3.5 |
| `a team that` | 1.0 | 0.03 | 6% | 0% | 3.5 |
| `it is the` | 1.6 | 0.52 | 10% | 4% | 3.4 |
| `rather than the` | 0.9 | 0.15 | 6% | 1% | 3.4 |
| `most of us` | 1.2 | 0.28 | 8% | 2% | 3.4 |
| `the same way` | 1.4 | 0.40 | 8% | 3% | 3.4 |
| `which is exactly` | 0.9 | 0.12 | 6% | 1% | 3.4 |
| `a blog post` | 0.9 | 0.12 | 6% | 1% | 3.4 |
| `the part that` | 0.9 | 0.03 | 6% | 0% | 3.4 |
| `and it's worth` | 0.9 | 0.03 | 6% | 0% | 3.4 |
| `nobody wants to` | 0.8 | 0.06 | 6% | 1% | 3.3 |
| `not just the` | 0.9 | 0.18 | 6% | 2% | 3.3 |

## Four-word phrases

| term | AI /10k | human /10k | AI docs | human docs | z |
| --- | ---: | ---: | ---: | ---: | ---: |
| `none of this is` | 1.8 | 0.03 | 12% | 0% | 4.2 |
| `are the ones that` | 0.7 | 0.03 | 4% | 0% | 2.9 |
| `this is not a` | 0.7 | 0.18 | 5% | 2% | 2.6 |
| `the shape of the` | 0.9 | 0.00 | 6% | 0% | 2.0 |
| `a particular kind of` | 0.9 | 0.00 | 6% | 0% | 2.0 |
| `the honest answer is` | 0.8 | 0.00 | 5% | 0% | 1.8 |
| `is one of the` | 0.9 | 0.46 | 6% | 3% | 1.6 |
| `and it's the one` | 0.7 | 0.00 | 4% | 0% | 1.6 |
| `there's a particular kind` | 0.6 | 0.00 | 4% | 0% | 1.5 |
| `in the first place` | 0.7 | 0.34 | 4% | 3% | 1.5 |
| `in a way that` | 0.8 | 0.49 | 5% | 3% | 1.2 |
