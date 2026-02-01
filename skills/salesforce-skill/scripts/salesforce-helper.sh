#!/usr/bin/env bash
# salesforce-helper.sh - Common Salesforce operations for Moltbot
# Place in skill folder and reference via {baseDir}/salesforce-helper.sh

set -euo pipefail

COMMAND="${1:-help}"
shift || true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get target org from env or default
TARGET_ORG="${SALESFORCE_TARGET_ORG:-}"
if [[ -n "$TARGET_ORG" ]]; then
    ORG_FLAG="--target-org $TARGET_ORG"
else
    ORG_FLAG=""
fi

case "$COMMAND" in
    # PIPELINE & REPORTING
    pipeline)
        echo -e "${GREEN}📊 Pipeline Summary${NC}"
        sf data query --query "
            SELECT StageName, COUNT(Id) Deals, SUM(Amount) TotalValue
            FROM Opportunity
            WHERE IsClosed = false
            GROUP BY StageName
            ORDER BY StageName
        " $ORG_FLAG --result-format table
        ;;

    pipeline-this-month)
        echo -e "${GREEN}📊 This Month's Pipeline${NC}"
        sf data query --query "
            SELECT StageName, COUNT(Id) Deals, SUM(Amount) TotalValue
            FROM Opportunity
            WHERE IsClosed = false AND CloseDate = THIS_MONTH
            GROUP BY StageName
        " $ORG_FLAG --result-format table
        ;;

    closing-soon)
        DAYS="${1:-14}"
        echo -e "${GREEN}🎯 Opportunities Closing in Next $DAYS Days${NC}"
        sf data query --query "
            SELECT Name, Account.Name, Amount, StageName, CloseDate, Owner.Name
            FROM Opportunity
            WHERE IsClosed = false AND CloseDate = NEXT_N_DAYS:$DAYS
            ORDER BY CloseDate
        " $ORG_FLAG --result-format table
        ;;

    # CONTACTS
    contacts)
        LIMIT="${1:-20}"
        echo -e "${GREEN}👥 Recent Contacts (limit $LIMIT)${NC}"
        sf data query --query "
            SELECT Id, Name, Email, Phone, Account.Name, Title
            FROM Contact
            ORDER BY CreatedDate DESC
            LIMIT $LIMIT
        " $ORG_FLAG --result-format table
        ;;

    search-contacts)
        SEARCH="${1:-}"
        if [[ -z "$SEARCH" ]]; then
            echo -e "${RED}Usage: search-contacts <name or email>${NC}"
            exit 1
        fi
        echo -e "${GREEN}🔍 Searching Contacts: $SEARCH${NC}"
        sf data query --query "
            SELECT Id, Name, Email, Phone, Account.Name
            FROM Contact
            WHERE Name LIKE '%$SEARCH%' OR Email LIKE '%$SEARCH%'
            LIMIT 25
        " $ORG_FLAG --result-format table
        ;;

    create-contact)
        FIRST="${1:-}"
        LAST="${2:-}"
        EMAIL="${3:-}"
        ACCOUNT_ID="${4:-}"

        if [[ -z "$FIRST" || -z "$LAST" ]]; then
            echo -e "${RED}Usage: create-contact <first> <last> [email] [account_id]${NC}"
            exit 1
        fi

        VALUES="FirstName='$FIRST' LastName='$LAST'"
        [[ -n "$EMAIL" ]] && VALUES="$VALUES Email='$EMAIL'"
        [[ -n "$ACCOUNT_ID" ]] && VALUES="$VALUES AccountId='$ACCOUNT_ID'"

        echo -e "${GREEN}➕ Creating Contact: $FIRST $LAST${NC}"
        sf data create record --sobject Contact --values "$VALUES" $ORG_FLAG --json
        ;;

    # ACCOUNTS
    accounts)
        LIMIT="${1:-20}"
        echo -e "${GREEN}🏢 Recent Accounts (limit $LIMIT)${NC}"
        sf data query --query "
            SELECT Id, Name, Industry, Website, Phone, BillingCity
            FROM Account
            ORDER BY CreatedDate DESC
            LIMIT $LIMIT
        " $ORG_FLAG --result-format table
        ;;

    search-accounts)
        SEARCH="${1:-}"
        if [[ -z "$SEARCH" ]]; then
            echo -e "${RED}Usage: search-accounts <name>${NC}"
            exit 1
        fi
        echo -e "${GREEN}🔍 Searching Accounts: $SEARCH${NC}"
        sf data query --query "
            SELECT Id, Name, Industry, Website, (SELECT Name, Email FROM Contacts LIMIT 5)
            FROM Account
            WHERE Name LIKE '%$SEARCH%'
            LIMIT 25
        " $ORG_FLAG --result-format table
        ;;

    # OPPORTUNITIES
    opportunities)
        LIMIT="${1:-20}"
        echo -e "${GREEN}💰 Recent Opportunities (limit $LIMIT)${NC}"
        sf data query --query "
            SELECT Id, Name, Account.Name, Amount, StageName, CloseDate, Probability
            FROM Opportunity
            WHERE IsClosed = false
            ORDER BY CloseDate
            LIMIT $LIMIT
        " $ORG_FLAG --result-format table
        ;;

    update-opp-stage)
        OPP_ID="${1:-}"
        STAGE="${2:-}"

        if [[ -z "$OPP_ID" || -z "$STAGE" ]]; then
            echo -e "${RED}Usage: update-opp-stage <opportunity_id> <stage_name>${NC}"
            echo "Common stages: Prospecting, Qualification, 'Needs Analysis', 'Proposal/Price Quote', 'Negotiation/Review', 'Closed Won', 'Closed Lost'"
            exit 1
        fi

        echo -e "${GREEN}📝 Updating Opportunity $OPP_ID to stage: $STAGE${NC}"
        sf data update record --sobject Opportunity --record-id "$OPP_ID" --values "StageName='$STAGE'" $ORG_FLAG --json
        ;;

    # LEADS
    leads)
        LIMIT="${1:-20}"
        echo -e "${GREEN}🎯 Open Leads (limit $LIMIT)${NC}"
        sf data query --query "
            SELECT Id, Name, Company, Email, Status, LeadSource, CreatedDate
            FROM Lead
            WHERE IsConverted = false
            ORDER BY CreatedDate DESC
            LIMIT $LIMIT
        " $ORG_FLAG --result-format table
        ;;

    stale-leads)
        DAYS="${1:-30}"
        echo -e "${YELLOW}⚠️ Leads Not Touched in $DAYS Days${NC}"
        sf data query --query "
            SELECT Id, Name, Company, Email, Status, LastModifiedDate
            FROM Lead
            WHERE IsConverted = false AND LastModifiedDate < LAST_N_DAYS:$DAYS
            ORDER BY LastModifiedDate
        " $ORG_FLAG --result-format table
        ;;

    create-lead)
        FIRST="${1:-}"
        LAST="${2:-}"
        COMPANY="${3:-}"
        EMAIL="${4:-}"

        if [[ -z "$FIRST" || -z "$LAST" || -z "$COMPANY" ]]; then
            echo -e "${RED}Usage: create-lead <first> <last> <company> [email]${NC}"
            exit 1
        fi

        VALUES="FirstName='$FIRST' LastName='$LAST' Company='$COMPANY' Status='Open - Not Contacted'"
        [[ -n "$EMAIL" ]] && VALUES="$VALUES Email='$EMAIL'"

        echo -e "${GREEN}➕ Creating Lead: $FIRST $LAST at $COMPANY${NC}"
        sf data create record --sobject Lead --values "$VALUES" $ORG_FLAG --json
        ;;

    # CASES
    cases)
        LIMIT="${1:-20}"
        echo -e "${GREEN}📋 Open Cases (limit $LIMIT)${NC}"
        sf data query --query "
            SELECT Id, CaseNumber, Subject, Status, Priority, Account.Name, CreatedDate
            FROM Case
            WHERE IsClosed = false
            ORDER BY Priority, CreatedDate
            LIMIT $LIMIT
        " $ORG_FLAG --result-format table
        ;;

    create-case)
        SUBJECT="${1:-}"
        ACCOUNT_ID="${2:-}"
        PRIORITY="${3:-Medium}"

        if [[ -z "$SUBJECT" ]]; then
            echo -e "${RED}Usage: create-case <subject> [account_id] [priority]${NC}"
            exit 1
        fi

        VALUES="Subject='$SUBJECT' Status='New' Priority='$PRIORITY'"
        [[ -n "$ACCOUNT_ID" ]] && VALUES="$VALUES AccountId='$ACCOUNT_ID'"

        echo -e "${GREEN}➕ Creating Case: $SUBJECT${NC}"
        sf data create record --sobject Case --values "$VALUES" $ORG_FLAG --json
        ;;

    # TASKS & ACTIVITIES
    my-tasks)
        echo -e "${GREEN}✅ My Open Tasks${NC}"
        sf data query --query "
            SELECT Id, Subject, WhoId, WhatId, ActivityDate, Priority, Status
            FROM Task
            WHERE IsClosed = false
            ORDER BY ActivityDate
            LIMIT 25
        " $ORG_FLAG --result-format table
        ;;

    log-call)
        SUBJECT="${1:-}"
        CONTACT_ID="${2:-}"
        NOTES="${3:-}"

        if [[ -z "$SUBJECT" ]]; then
            echo -e "${RED}Usage: log-call <subject> [contact_id] [notes]${NC}"
            exit 1
        fi

        VALUES="Subject='$SUBJECT' Status='Completed' Priority='Normal' ActivityDate='$(date +%Y-%m-%d)' Type='Call'"
        [[ -n "$CONTACT_ID" ]] && VALUES="$VALUES WhoId='$CONTACT_ID'"
        [[ -n "$NOTES" ]] && VALUES="$VALUES Description='$NOTES'"

        echo -e "${GREEN}📞 Logging Call: $SUBJECT${NC}"
        sf data create record --sobject Task --values "$VALUES" $ORG_FLAG --json
        ;;

    # UTILITY
    query)
        SOQL="${1:-}"
        if [[ -z "$SOQL" ]]; then
            echo -e "${RED}Usage: query <SOQL query>${NC}"
            exit 1
        fi
        sf data query --query "$SOQL" $ORG_FLAG --result-format table
        ;;

    query-json)
        SOQL="${1:-}"
        if [[ -z "$SOQL" ]]; then
            echo -e "${RED}Usage: query-json <SOQL query>${NC}"
            exit 1
        fi
        sf data query --query "$SOQL" $ORG_FLAG --result-format json
        ;;

    describe)
        OBJECT="${1:-}"
        if [[ -z "$OBJECT" ]]; then
            echo -e "${RED}Usage: describe <object_name>${NC}"
            echo "Common objects: Account, Contact, Opportunity, Lead, Case, Task"
            exit 1
        fi
        sf sobject describe --sobject "$OBJECT" $ORG_FLAG
        ;;

    fields)
        OBJECT="${1:-}"
        if [[ -z "$OBJECT" ]]; then
            echo -e "${RED}Usage: fields <object_name>${NC}"
            exit 1
        fi
        echo -e "${GREEN}📋 Fields for $OBJECT${NC}"
        sf sobject describe --sobject "$OBJECT" $ORG_FLAG --json | jq -r '.result.fields[] | "\(.name)\t\(.type)\t\(.label)"' | column -t -s $'\t'
        ;;

    orgs)
        echo -e "${GREEN}🔗 Connected Orgs${NC}"
        sf org list
        ;;

    status)
        echo -e "${GREEN}ℹ️ Current Org Status${NC}"
        sf org display $ORG_FLAG
        ;;

    help|*)
        echo -e "${GREEN}Salesforce Helper Commands${NC}"
        echo ""
        echo "PIPELINE & REPORTING:"
        echo "  pipeline              - Show open pipeline by stage"
        echo "  pipeline-this-month   - Pipeline closing this month"
        echo "  closing-soon [days]   - Opportunities closing soon (default: 14 days)"
        echo ""
        echo "CONTACTS:"
        echo "  contacts [limit]      - List recent contacts"
        echo "  search-contacts <q>   - Search contacts by name/email"
        echo "  create-contact <first> <last> [email] [account_id]"
        echo ""
        echo "ACCOUNTS:"
        echo "  accounts [limit]      - List recent accounts"
        echo "  search-accounts <q>   - Search accounts by name"
        echo ""
        echo "OPPORTUNITIES:"
        echo "  opportunities [limit] - List open opportunities"
        echo "  update-opp-stage <id> <stage>"
        echo ""
        echo "LEADS:"
        echo "  leads [limit]         - List open leads"
        echo "  stale-leads [days]    - Leads not touched (default: 30 days)"
        echo "  create-lead <first> <last> <company> [email]"
        echo ""
        echo "CASES:"
        echo "  cases [limit]         - List open cases"
        echo "  create-case <subject> [account_id] [priority]"
        echo ""
        echo "TASKS:"
        echo "  my-tasks              - List my open tasks"
        echo "  log-call <subject> [contact_id] [notes]"
        echo ""
        echo "UTILITY:"
        echo "  query <SOQL>          - Run arbitrary SOQL (table format)"
        echo "  query-json <SOQL>     - Run SOQL (JSON format)"
        echo "  describe <object>     - Describe object schema"
        echo "  fields <object>       - List fields for object"
        echo "  orgs                  - List connected orgs"
        echo "  status                - Show current org status"
        echo ""
        echo "Set SALESFORCE_TARGET_ORG env var to specify default org"
        ;;
esac
