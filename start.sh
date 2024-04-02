#!/bin/bash
nohup poetry run uvicorn main:petBack >> log.log &
