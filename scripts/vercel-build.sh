#!/usr/bin/env bash
set -euo pipefail

HUGO_VERSION="0.150.0"
DART_SASS_VERSION="1.92.1"
LOCAL_BIN="${HOME}/.local"
VERCEL_BASEURL="${VERCEL_BASEURL:-https://amroelhusseini.vercel.app/}"

mkdir -p "${LOCAL_BIN}/hugo" "${LOCAL_BIN}/dart-sass"

fetch_tar() {
  local url="$1"
  local tmp
  tmp="$(mktemp -d)"
  echo "Downloading: ${url}" >&2
  curl -sL --retry 3 -o "${tmp}/archive.tar.gz" "${url}"
  tar -C "${tmp}" -xzf "${tmp}/archive.tar.gz"
  rm -f "${tmp}/archive.tar.gz"
  echo "${tmp}"
}

if [ ! -x "${LOCAL_BIN}/hugo/hugo" ]; then
  tmp="$(fetch_tar "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz")"
  cp -f "${tmp}/hugo" "${LOCAL_BIN}/hugo/hugo"
  chmod +x "${LOCAL_BIN}/hugo/hugo"
  rm -rf "${tmp}"
fi

if [ ! -x "${LOCAL_BIN}/dart-sass/sass" ]; then
  tmp="$(fetch_tar "https://github.com/sass/dart-sass/releases/download/${DART_SASS_VERSION}/dart-sass-${DART_SASS_VERSION}-linux-x64.tar.gz")"
  cp -rf "${tmp}"/dart-sass/. "${LOCAL_BIN}/dart-sass/"
  chmod +x "${LOCAL_BIN}/dart-sass/sass" "${LOCAL_BIN}/dart-sass/dart-sass" 2>/dev/null || true
  rm -rf "${tmp}"
fi

export PATH="${LOCAL_BIN}/hugo:${LOCAL_BIN}/dart-sass:${PATH}"

if [ ! -e "themes/m10c" ] || [ -z "$(ls -A themes/m10c 2>/dev/null)" ]; then
  echo "Initializing submodule themes/m10c"
  git submodule update --init --recursive 2>/dev/null || \
    git clone --depth 1 "https://github.com/vaga/hugo-theme-m10c.git" themes/m10c
fi

echo "Hugo: $(hugo version)"
echo "Dart Sass: $(sass --version)"

hugo --gc --minify -d docs --baseURL "${VERCEL_BASEURL}"
