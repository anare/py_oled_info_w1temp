#!/usr/bin/env bash

targets="/sys/bus/w1/devices/28-*/resolution"
targetSave="/sys/bus/w1/devices/28-*/eeprom"
for target in $targets; do
  if [ ! -f "$target" ]; then
    echo "Resolution file not found"
    exit 1
  fi
  id=$(echo $target | sed 's/.*devices\/\(.*\)\/resolution/\1/')
# '''
  current=$(cat $targets)
  echo "Current[$id] resolution: $current-bit"
done

if [ "$1" != "" ]; then
  for target in $targets; do
    if [ ! -f "$target" ]; then
      echo "Resolution file not found"
      exit 1
    fi
    targetSave="/sys/bus/w1/devices/$id/eeprom"
    id=$(echo "$target" | sed 's/.*devices\/\(.*\)\/resolution/\1/')
# '''
    echo "Setting resolution for [$id] to $1-bit"
    echo "$1" > "$target"

    current=$(cat "$target")
    echo "Current resolution for [$id]: $current-bit"

    echo "Saving resolution for [$id] to eeprom"
    echo save > "$targetSave"
    echo "Resolution saved for [$id] to eeprom"
  done

fi
