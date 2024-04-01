#!/bin/bash
nohup poetry run uvicorn main:petBack --root-path /pet/api > log.log &
