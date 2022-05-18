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

import collections
import re
import string
import sys

# The buckets we categorize artifacts as
Buckets = collections.namedtuple(
    'Buckets',
    'product version arch os packaging installer is_bin attributes leftover')

# Capture well known version patterns
_VERSION_RE = re.compile(
    r'[-_.]'  # preceed by separator
    r'v?'  # with an optional 'v', which we strip in code
    # classic m.n.p with optional '-alpha-N'
    r'(\d+\.\d+\.\d+-((alpha)|(beta)|(gamma))[.-]?\d+)'
    r'|(\d+\.\d+\.\d+-pre\.\d{8}\.[.\d]+)'   # bazel-5.0.0-pre.20210516.1
    r'|(\d+\.\d+\.\d+(-?rc\.?\d+)?)'         # m.n.p-RCN
    r'|(\d+\.\d+\.\d+[abcdefg]?)'            # 1.2.3a
    r'|(\d+\.\d+[abcdefg])'                  # 1.0a
    r'|(\d+\.\d+(-?rc\d+)?)'                 # m.n-rcN
    )

_PRODUCT_VERSION_RE = re.compile(r'(\w+[-\w]*)[-_.]v?(\d+\.\d+\.\d+[a-z\d]*)[^.\D]?')
#  bazel-toolchains-0dc4917.tar.gz
#  bazel-toolchains-r123456.tar.gz
_PRODUCT_GITHASH_RE = re.compile(r'(\w+[-\w]*)[-_.](([0-9a-f]{7})|(r\d{6}))')

# bazel-5.0.0-pre.20210516.1

_JDK_SPEC_RE = re.compile(r'[^a-z]?(jdk\d*)')

_LINUX_PACKAGE_EXTENSIONS = ['.sh', '.deb', '.rpm', '.zip', '.tar.gz', '.tgz']
_MACOS_PACKAGE_EXTENSIONS = ['.dmg', '.mac', '.osx']
_WINDOWS_PACKAGE_EXTENSIONS = ['.exe']

def Categorize(file_name, default_version=None):
  """Break down file name into buckets that matter."""

  # eat away parts until todo us empty
  todo = file_name
  attributes = []

  # msvc was an odd tag added to early versions
  if todo.find('-msvc') > 0:
    attributes.append('msvc')
    todo = todo.replace('-msvc', '')

  has_unknown, todo = ExtractFeature(todo, ['unknown'])

  arch, todo = ExtractFeature(todo, [
      'x86_64',
      'amd64',
      'arm64',
      'aarch64',
      'pc',
      'unknown',
  ])
  if arch in ['amd64', 'pc']:
    arch = 'x86_64'

  os, todo = ExtractFeature(
      todo, ['dist',
             'linux-gnu', 'pc-windows-gnu', 'windows-gnu',
             'linux', 'gnu',
             'apple-darwin', 'darwin', 'macos', 'osx',
             'windows',
             ])
  if os in ['apple-darwin', 'darwin', 'osx']:
    os = 'macos'
  if os in ['gnu', 'linux-gnu']:
    os = 'linux'
  if os in ['windows-gnu', 'windows']:
    os = 'windows'
  if os == 'dist':
    os = 'any'

  # extract sig before packaging, so .sh and .sha256 are not confused
  is_bin = True
  if todo.endswith('.sig'):
    todo = todo[0:-4]
    attributes.append('sig')
    is_bin = False
  elif todo.endswith('.sha256'):
    todo = todo[0:-7]
    attributes.append('sig')
    is_bin = False

  packaging, todo = ExtractFeature(todo, _LINUX_PACKAGE_EXTENSIONS +
                                   _MACOS_PACKAGE_EXTENSIONS +
                                   _WINDOWS_PACKAGE_EXTENSIONS)
  if packaging and packaging[0] == '.':
    packaging = packaging[1:]
  if packaging in ['tar.gz', 'tgz']:
    if not arch:
      arch = 'src'
    if not os:
      os = 'any'
  if not os:
    if packaging in _LINUX_PACKAGE_EXTENSIONS:
      os = 'linux'
    if packaging in _MACOS_PACKAGE_EXTENSIONS:
      os = 'macos'
    if packaging in _WINDOWS_PACKAGE_EXTENSIONS:
      os = 'windows'

  installer, todo = ExtractFeature(todo, ['installer'])
  installer = 'installer' if installer else 'standalone'

  # How we say things about JDK is a mess
  nojdk, todo = ExtractFeature(todo, ['nojdk', 'without-jdk'])
  jdk = None
  if nojdk:
    jdk = 'nojdk'
  else:
    jdk_match = _JDK_SPEC_RE.search(todo)
    if jdk_match:
      jdk = jdk_match.group(1)
      todo = todo[0:jdk_match.start(1)] + todo[jdk_match.end(1):]
    if jdk:
      attributes.append(jdk)


  # At this point, only the product name and version should be left.
  m = _VERSION_RE.search(todo)
  if m and m.end() == len(todo):
    product = todo[0:m.start()].rstrip('-._')
    if product.endswith('-v'):
      product = product[0:-2]
    version = todo[m.start():m.end()].lstrip('-._')
    todo = ''
  else:
    m = _PRODUCT_VERSION_RE.match(todo)
    if m:
      product = todo[0:m.end(1)]
      version = m.group(2)
      todo = todo[m.end(2):]
    else:
      m = _PRODUCT_GITHASH_RE.match(todo)
      if m:
        product = todo[0:m.end(1)]
        version = m.group(2)
        todo = todo[m.end(2):]
      else:
        # some things are unversioned. e.g. bazelisk-os-arch.
        sep_pos = todo.find('-')
        if sep_pos <= 0:
          # print('Can not find version on:', file_name, file=sys.stderr)
          product = todo
          todo = ''
          version = default_version
        else:
          version = 'head'
          product = todo[0:sep_pos]
          todo = todo[sep_pos:]

  while product.endswith('-') or product.endswith('.'):
    product = product[0:len(product)-1]
  left = re.sub(r'^[- _.]*', '', todo)
  if left:
    left = ' - LEAVES(%s)' % left

  return Buckets(product, version, arch, os, packaging, installer, is_bin,
                 '|'.join(attributes), left)


def ExtractFeature(s, feature_list):
  """Extract a feature from a file name.

  The feature and then redundant punction is removed from the input.

  Returns:
    feature, remainder
  """
  for feature in feature_list:
    pos = s.find(feature)
    if pos < 0:
      pos = s.find(feature.upper())
    if pos >= 0:
      before = s[0:pos]
      after = s[pos+len(feature):]
      if (len(before) and len(after)
          and before[-1] in string.punctuation
          and after[0] in string.punctuation):
        before = before[0:-1]
        # If we are left with after just being the '-', drop it.
        if len(after) == 1:
          after = ''
      elif len(after) == 0 and before[-1] in string.punctuation:
        before = before[0:-1]
      return feature.lower(), before + after
  return None, s
