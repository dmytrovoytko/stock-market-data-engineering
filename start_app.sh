#!/bin/bash
echo
echo '1. STARTING WORKFLOW'
echo

echo '1.1. TERRAFORM?'
bash terraform-setup.sh
sleep 1

echo
echo '1.2. WORKFLOW ORCHESTRATE'
python wf_orchestrate.py --mode=$DATAWAREHOUSE

echo
echo '2. Starting Streamlit app...'
echo
streamlit run dashboard-app.py

sleep 5
