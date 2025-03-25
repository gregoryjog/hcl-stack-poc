#!/bin/bash
grep -w "environment" ~/.aws/credentials | cut -d '=' -f2 | tr -d ' '