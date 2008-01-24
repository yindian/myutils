#!/bin/sh

xset +fp ~/.fonts
xset fp rehash
xrdb -merge ~/.Xdefaults

exec icewm-session
