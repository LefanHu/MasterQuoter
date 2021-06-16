#!/bin/sh
name="tmod"

screen -S $name -X stuff "say test"
screen -S $name -X eval "stuff \015"