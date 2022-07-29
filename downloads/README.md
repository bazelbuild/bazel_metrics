# Data file description

## Raw download data

The `raw` folder contains files with content of the form:

  *date|hhmm|repository|filename|tag|# artifact downloads|# sha256 downloads|# sig downloads*

Where:

- date: is the date of sample collection
- hhmm: is the hour and minute (UTC) of the collection
- repository: the repository containing this artifact
- filename: is the name of the downloadable artifact
- release: the release name
- # artifact downloads: is the cummulative number of downloads of that artifact
  as of the collection time.
- # sha256 downloads: is the cummulative number of downloads of the sha256
  checksum of the artifact as of the collection time.
- # sig downloads: is the cummulative number of downloads of the signature
  of the artifact as of the collection time.

Sample:

```
2022-03-22|2223|bazelbuild/bazel|bazel-5.0.0-darwin-arm64|5.0.0|869|49|23
2022-03-22|2223|bazelbuild/bazel|bazel-5.0.0-darwin-x86_64|5.0.0|1431|97|28
2022-03-22|2223|bazelbuild/bazel|bazel-5.0.0-dist.zip|5.0.0|2799|55|77
2022-03-22|2223|bazelbuild/bazel|bazel-5.0.0-installer-darwin-arm64.sh|5.0.0|390|30|25
2022-03-22|2223|bazelbuild/bazel|bazel-5.0.0-installer-darwin-x86_64.sh|5.0.0|4421|31|21
2022-03-22|2223|bazelbuild/bazel|bazel-5.0.0-installer-linux-x86_64.sh|5.0.0|15777|48|53
```

## processed data

The files in `csv` categorize the download counts in ways that enable
drill-down.

Format:
  *sample_date,repo,product,version,os,arch,extension,downloads,downloads_total*

Example:

```
2022-03-22,bazelbuild/bazel,bazel,4.2.1,windows,x86_64,exe,147,28719
```

- Product, version, os, arch, and extension are derived from the artifact
  name, the repo, and the release tag.
- downloads_total is the cumulative download count for this artifact
- downlaods is the delta from the previous day


## categorizations.txt

The file `categorizations.txt` contains a mapping of raw file names to
as set of "bins" that might be useful for drill down along important
axis, such as rule set, version, or OS.

  *filename|canonical product name|version|architecture|os|packaging type*

Example:

```
bazel-4.2.0-darwin-arm64|bazel|4.2.0|arm64|macos|None
bazel-4.2.0-darwin-x86_64|bazel|4.2.0|x86_64|macos|None
bazel-4.2.0-dist.zip|bazel|4.2.0|None|any|zip
```
