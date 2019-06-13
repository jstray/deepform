# Deepform

An experiment to extract information from TV station political advertising disclosure forms using deep learning, and a challenging journalism-relevant dataset for NLP/AI researchers. Orignal data from ProPublica's [Free The Files](https://projects.propublica.org/free-the-files/) project.

This model achieves 90% accuracy extracting total spending from the PDFs in the (held out) test set, which shows that deep learning can generalize surprisingly well to previously unseen form types. I expect it could be made much more accurate through some feature engineering (see below.)

For results and discussion, see [this talk](https://www.youtube.com/watch?v=uNN59kJQ7CA).

Full thanks to my collaborator Nicholas Bardy of Weights & Biases.

## Why?
TV stations are required to disclose their sale of political advertising, but there is no requirement that this disclosure is machine readable. Every election, tens of thousands of PDFs are posted to the FCC Public File, available at [https://publicfiles.fcc.gov/](https://publicfiles.fcc.gov/) in hundreds of different formats. 

In 2012, ProPublica ran the Free The Files project (you can [read how it worked](https://www.niemanlab.org/2012/12/crowdsourcing-campaign-spending-what-propublica-learned-from-free-the-files/)) and hundreds of volunteers hand-entered information for over 17,000 of these forms. That data drove a bunch of campaign finance [coverage](https://www.propublica.org/series/free-the-files) and is now [available](https://www.propublica.org/datastore/dataset/free-the-files-filing-data) from their data store.

Can we replicate this data extraction using modern deep learning techniques? This project aimed to find out, and successfully extracted the easiest of the fields (total amount) at 90% accuracy using a relatively simple network.

## How it works
I settled on a relatively simple design, using a fully connected three-layer network trained on 20 token windows of the data. Each token is hashed to an integer mod 500, then converted to 1-hot representation and embedded into 32 dimensions. This embedding is combined with geometry information (bounding box and page number) and also some hand-crafted "hint" features, such as the number of digit characters in the string. For details, see [the talk](https://www.youtube.com/watch?v=uNN59kJQ7CA).

Although 90% is a good result, it's probably not high enough for production use. However, I believe this approach has lots of room for improvement. The advantage of this type of system is that it can elegantly integrate multiple manual extraction methods — the "hint" features — each of which can be individually crappy. The network actually learns when to trust each method. In ML speak this is "boosting over weak learners." 

So the next steps would be something like:

- Add additional hand-crafted features that signal when a token is the total. These don't have to be individually very accurate.
- Extend the technique to the other fields we wish to extract (advertiser, etc.)

## How to run

If you wish to reproduce this result, there are multple steps in the data preparation:

- The raw data is in `source/ftf-all-filings.tsv`. This file contains the crowdsourced answers and the PDF url.
- `download-pdfs.py` will read this file and download all the PDFs from DocumentCloud. It takes several days. Also, perhaps 10% of these PDFs are no longer on DocumentCloud. In theory they could be re-collected from the FCC.
- `tokenize-pdfs.py` will read each PDF and output a list of tokens and their geometry. Also takes several days to run.
- `create-training-data.py` reads the PDF tokens and matches them against the original data, outputting only documents where the training data is available. Edit this to control which extracted fields appear in the training data. 
- `train.py` loads this data, trains a network, and logs the results using [Weights & Biases](https://www.wandb.com/)
- `baseline.py` is a hand coded total extractor for comparison, which achieves 61% accuracy.

## Training data format
The main training data file is `data/training.csv` but it's too big to post in github, so you can download it [here](https://drive.google.com/drive/folders/1bsV4A-8A9B7KZkzdbsBnCGKLMZftV2fQ?usp=sharing).

There is data from 9018 labelled documents. It's formatted as "tokens plus geometry" like this:

```
slug,page,x0,y0,x1,y1,token,gross_amount
473630-116252-0-13442821773323-_-pdf,0,272.613,438.395,301.525,438.439,$275.00,0.62
473630-116252-0-13442821773323-_-pdf,0,410.146,455.811,437.376,455.865,Totals,0.0
473630-116252-0-13442821773323-_-pdf,0,525.84,454.145,530.288,454.189,6,0.0
473630-116252-0-13442821773323-_-pdf,0,556.892,454.145,592.476,454.189,"$1,170.00",1.0
473630-116252-0-13442821773323-_-pdf,0,18.0,480.478,37.998,480.527,Time,0.0
473630-116252-0-13442821773323-_-pdf,0,40.5,480.478,66.51,480.527,Period,0.0
```

The `slug` is a unique document identifier, ultimately from the source TSV. The page number runs from 0 to 1, and the bounding box is in the original PDF coordinate system. The actual token text is reproduced as `token`. The `gross_amount` represents string similarity to the correct answer in the original `gross_amount` column, from 0 to 1. To add other ground-truth fields, edit `create-training-data.py`.


## A research data set
There is a great deal left to do! For example, we still need to try extracting the other fields such as advertiser and TV station call sign. This will probably be harder than totals as it's harder to identify tokens which "look like" the correct answer.

There is still more data preparation work to do. We discovered that about 30% of the PDFs documents still need OCR, which should increase our training data set from 9k to ~17k documents.

But even in its current form, this is a difficult data set that is very relevant to journalism, and improvements in technique will be immediately useful to campaign finance reporting. 

The general problem is known as "knowledge base construction" in the research community, and the current state of the art is achieved by multimodal systems such as [Fonduer](https://fonduer.readthedocs.io/en/latest/).

I would love to hear from you! Contact me on [twitter](https://twitter.com/jonathanstray) or through my [blog](http://jonathanstray.com).




