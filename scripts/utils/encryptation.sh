#!/bin/bash

echo "Key=$(openssl rand -hex 64)"
echo "Key=$(openssl rand -hex 32)"
echo "Key IV=$(openssl rand -hex 16)"

