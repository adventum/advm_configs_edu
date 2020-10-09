#!/usr/bin/env bash
ansible-galaxy role install -r requirements.yml
ansible-playbook ../deploy/pb_deploy.yml --ask-vault-pass -i hosts.ini "$@"