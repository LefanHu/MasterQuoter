#!/bin/sh
name="tmod"

screen -S $name -X stuff "say Server restarting in 10 seconds"
screen -S $name -X eval "stuff \015"
sleep 5
screen -S $name -X stuff "say Server restarting in 5 seconds"
screen -S $name -X eval "stuff \015"
sleep 1
screen -S $name -X stuff "say Server restarting in 4 seconds"
screen -S $name -X eval "stuff \015"
sleep 1
screen -S $name -X stuff "say Server restarting in 3 seconds"
screen -S $name -X eval "stuff \015"
sleep 1
screen -S $name -X stuff "say Server restarting in 2 seconds"
screen -S $name -X eval "stuff \015"
sleep 1
screen -S $name -X stuff "say Server restarting in 1 second"
screen -S $name -X eval "stuff \015"
sleep 1
screen -S $name -X stuff "say Server is restarting"
screen -S $name -X eval "stuff \015"
sleep 2
screen -S $name -X stuff 'exit'
screen -S $name -X eval "stuff \015"
sleep 30

cd ~/Desktop/terraria_modded
./tmod.sh