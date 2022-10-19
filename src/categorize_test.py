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
"""Tests for categorize."""

import re
import unittest

import categorize


class CategorizeTest(unittest.TestCase):

  version_re = re.compile(
      r'[-_.]v?(\d+\.\d+\.\d+[a-z\d]*(-rc\d+)?)|(\d+\.\d+[a-z\d]*(-rc\d+)?)')

  def test_samples(self):
    with open('categorize_samples.txt', 'r') as samples:
      for sample in samples:
        # bazel-0.10.0-dist.zip|bazel|0.10.0|None|any|zip|standalone|True|{}
        try:
          (file, product, version, arch, os, packaging, installer, is_bin,
           rest) = sample.strip().split('|')
        except ValueError:
          print('Bad sample:', sample)
          continue
        if not packaging:
          packaging = ''
        with self.subTest(file=file):
          m = self.version_re.search(file)
          # Only use the default version if we can not find the common version
          # pattern in the filename.
          if m:
            buckets = categorize.Categorize(file)
          else:
            buckets = categorize.Categorize(file,
                                            default_version=version)
          self.assertEqual(product, buckets.product, str(buckets))
          self.assertEqual(version, buckets.version, str(buckets))
          self.assertEqual(arch, str(buckets.arch), str(buckets))
          self.assertEqual(os, str(buckets.os), str(buckets))
          self.assertEqual(packaging or '', str(buckets.packaging), str(buckets))
          self.assertEqual(installer, buckets.installer, str(buckets))
          self.assertEqual(is_bin, str(buckets.is_bin), str(buckets))
          self.assertEqual(
              rest,
              '{%s}%s' % (buckets.attributes, buckets.leftover),
              str(buckets))


if __name__ == '__main__':
  unittest.main()
