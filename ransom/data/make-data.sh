#!/bin/bash

data_password="6903-EthicalHacking-D@+@P@ssw0rd!_Fall2018_Team:"
key_password="6903-EthicalHacking-K3yP@ssw0rd!_Fall2018_Team:"

chars=36

for team in `seq 2 23`; do 
    echo "----------------------------"
    echo Team: $team
    echo "----------------------------"
    for data in www pfsense workstation dc token; do
       mkdir -p company_data_$data
       proof=`echo -n "$master_password$team$data" | sha512sum | cut -d " " -f1 | cut -c1-$chars` 
       encryption_key=`echo -n "$key_password$team$data" | sha512sum | cut -d " " -f1 | cut -c1-$chars`
       printf "${data}_proof:\t$proof\n"
       printf "${data}_key:\t$encryption_key\n"
       echo "This file has been recovered successfully! Proof: $proof " > company_data_$data/data
       zip -r -P "$encryption_key" $data.data.zip company_data_$data/ >/dev/null 2>&1
    done
    mkdir -p team$team
    mv www.data.zip team$team/pending_transactions.csv
    mv pfsense.data.zip team$team/traffic_audit.psql
    mv workstation.data.zip team$team/q4_finance.xlsx
    mv dc.data.zip team$team/employee_records.dat
    rm token.data.zip 

    rm -rf company_data_*
done

