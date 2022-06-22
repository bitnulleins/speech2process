# Speech*2*Process

Speech*2*Process is a tool to transform natural language (by text oder audio recorded) to BPMN process (incl. EventLog). This tool is part of a research paper.

The following steps is made by the tool:
1. Transcribe audio to text (optional)
2. Extract tasks (events) via NLP tool spaCy
3. Generate simple EventLog for PM4PY
4. Process Mining algorithm for BPMN creation

## Installation

Get project by:

```git clone https://github.com/bitnulleins/speech2process.git```

### Dependencies

You need some python libraries: [requirments.txt](./requirements.txt)

```pip install -r requirments.txt```

### PM4PY

Read the [installation manual](https://pm4py.fit.fraunhofer.de/install) to install PM4PY on your machine. If you've an ARM processor, try [these](https://pm4py.fit.fraunhofer.de/install-page#linux-ARM) manual.

### Install 'flac' libaries

To work with audio files, you've to install *flac* libaries. Try on linux:

```sudo apt-get install -y flac```

On MacOS (via brew)

```brew install flac```

### Install graphviz

To generate BPMN model PNG, it requires:

```sudo apt-get install graphviz```

On MacOS (via brew):

```brew install graphviz```

### spaCy language package

To install specific language package:

```python -m spacy download <package_name>```

For german package:

```python -m spacy download de_core_news_sm```

## Run

### Local

* Production: ```python ./src/wsgi.py```
* Development ```python ./src/app.py```

### Heroku

First download and install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).

Create an app on Heroku, which prepares Heroku to receive your source code:

```heroku create speechtoprocess```

And then

```heroku open```

Then url of the deployed service should be:

https://speechtoprocess.herokuapp.com/

## Research paper

Coming soon...

*Thanks to @ruslanmv for basic Flask project*