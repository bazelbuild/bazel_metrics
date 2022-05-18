#!/usr/bin/env python3
# Copyright 2022 The Bazel Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys

import categorize


def MapRawData(file_names):
  """Recategorize the download files names into bucketable dimensions.

  This is used for regression testing changes to the categorizor.

  For each data files:
    Categorize each entry along the important dimensions
      - gather the oddball stuff into an attribute bag for now
    Re-emit that in a form easy to sort and reduce
  """
  for f in file_names:
    print('Loading:', f, file=sys.stderr)
    with open(f, 'r') as df:
      for line in df:
        line = line.strip()
        (ymd, hm, repo, file_name, release_tag,
         bin_count, sha_count, sig_count) = line.split('|')


        buckets = categorize.Categorize(file_name, default_version=release_tag)
        if buckets:
          print('%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % (
              ymd, hm, file_name, bin_count, sha_count, sig_count,
              buckets.product, buckets.version, buckets.arch, buckets.os,
              buckets.packaging, buckets.installer, buckets.is_bin))
          if buckets.leftover:
            print('WARNING: Could not fully categorize', line,
                  'got', buckets.leftover,
                  out=sys.stderr)
        else:
          print('ERROR: can not categorize', line, out=sys.stderr)
          

def main():
  parser = argparse.ArgumentParser(description='Collect Bazel repo download metrics')
  # Usage:  raw_to_cvs file ...
  parser.add_argument('files', nargs=argparse.REMAINDER, help='raw data files')

  args = parser.parse_args()
  if not args.files:
    parser.print_usage()
    sys.exit(1)
  MapRawData(args.files)


if __name__ == '__main__':
  main()
