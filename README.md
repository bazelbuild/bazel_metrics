# Bazel github metrics

This project contains various metrics collected from the
[bazelbuild project](http://github.com/bazelbuild).

## Download metrics

This data set contains download counts (from github) of release artifacts
from selected bazelbuild repositories. The intent is that one could use
this data set to analyze usage trends of various rule sets by version.

Notes:
- This can only capture downloads of explicitly declared artifacts. Github
  provides no API for counting downloads of specific commits, nor of the
  auto-created .zip and .tar downloads of of release tags. Rule authors
  who want to be included in this data set are encouraged to make explicit
  releases.
- This data set does not include counts from various mirror sites. As such
  it is only a proxy for general trends and not an absolute usage indicator.

### Raw data

The `downloads/raw` folder contains the raw data. These are simply
captures of file names and cumulative download counts They are divided
into folders by year.

### Processed data

The `downloads/csv` folder contains data in a more convenient to use form.
See [the readme there](downloads/README.md) for a description.
