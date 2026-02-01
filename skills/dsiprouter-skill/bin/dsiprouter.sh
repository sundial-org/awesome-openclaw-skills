#!/usr/bin/env bash
set -euo pipefail

: "${DSIP_ADDR:?DSIP_ADDR is required}"
: "${DSIP_TOKEN:?DSIP_TOKEN is required}"

insecure=()
if [[ "${DSIP_INSECURE:-}" == "1" ]]; then insecure=(-k); fi

api() {
  local method="$1"; shift
  local path="$1"; shift
  curl "${insecure[@]}" --silent --show-error --fail-with-body \
    --connect-timeout 5 --max-time 30 \
    -H "Authorization: Bearer ${DSIP_TOKEN}" \
    -H "Content-Type: application/json" \
    -X "${method}" "https://${DSIP_ADDR}:5000${path}" \
    "$@"
}

help() {
  cat << "EOF"
dsiprouter - generated helper CLI from Postman collection

Environment:
  DSIP_ADDR       hostname/IP (no scheme)
  DSIP_TOKEN      bearer token
  DSIP_INSECURE=1 allow self-signed TLS

Generic:
  dsiprouter call <METHOD> <PATH_WITH_QUERY> [<JSON_BODY>]

Generated commands:
  dsiprouter endpointgroups:list [args...]
  dsiprouter endpointgroups:get [args...]
  dsiprouter endpointgroups:create [args...]
  dsiprouter endpointgroups:create_1 [args...]
  dsiprouter endpointgroups:create_2 [args...]
  dsiprouter endpointgroups:create_3 [args...]
  dsiprouter endpointgroups:delete [args...]
  dsiprouter endpointgroups:update [args...]
  dsiprouter kamailio:reload [args...]
  dsiprouter kamailio:list [args...]
  dsiprouter inboundmapping:list [args...]
  dsiprouter inboundmapping:create [args...]
  dsiprouter inboundmapping:update [args...]
  dsiprouter inboundmapping:delete [args...]
  dsiprouter leases:list [args...]
  dsiprouter leases:list_1 [args...]
  dsiprouter leases:revoke [args...]
  dsiprouter carriergroups:list [args...]
  dsiprouter carriergroups:create [args...]
  dsiprouter auth:create [args...]
  dsiprouter auth:update [args...]
  dsiprouter auth:delete [args...]
  dsiprouter auth:list [args...]
  dsiprouter auth:login [args...]
  dsiprouter cdr:get [args...]
  dsiprouter cdr:get_1 [args...]

Notes:
  • If the command has a sample body in Postman, you can pass --sample as the last arg.
  • Otherwise, pass JSON body as the last arg (for POST/PUT).

EOF
}

cmd="${1:-help}"; shift || true
case "$cmd" in
  help|-h|--help) help; exit 0 ;;
  call)
    method="${1:?METHOD}"; path="${2:?PATH}"; shift 2 || true
    if [[ "${1:-}" != "" ]]; then api "$method" "$path" --data "${1}"; else api "$method" "$path"; fi
    ;;
  endpointgroups:list)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    path="/api/v1/endpointgroups"
    api "GET" "${path}"
    ;;
  endpointgroups:get)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    set -- "${args[@]}"
    if [[ "$#" -lt 1 ]]; then echo "Error: expected at least 1 path parameter(s) for endpointgroups:get" >&2; exit 2; fi
    path="/api/v1/endpointgroups/${1}"
    path="$(eval echo \"$path\")"
    api "GET" "${path}"
    ;;
  endpointgroups:create)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{
    \"name\": \"FusionPBX PassThru\",
    \"call_settings\": {
        \"limit\": 5,
        \"timeout\": 3600
    },
    
    \"fusionpbx\": {
        \"enabled\": true,
        \"dbhost\": \"fusionpbx.dsiprouter.net\",
        \"dbuser\": \"fusionpbx\",
        \"dbpass\": \"\"
    }
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    path="/api/v1/endpointgroups"
    if [[ "${body}" != "" ]]; then api "POST" "${path}" --data "${body}"; else api "POST" "${path}"; fi
    ;;
  endpointgroups:create_1)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{
    \"name\": \"SIP Trunk In/Out - User/Password\",
    \"call_settings\": {
        \"limit\": 5,
        \"timeout\": 3600
    },
    \"auth\": {
        \"type\": \"userpwd\",
        \"user\": \"18889072085\",
        \"pass\": \"example\",
        \"domain\": \"pbx.example.com\"
    },
    \"strip\": 0,
    \"prefix\": \"\",
    \"notifications\": {
        \"overmaxcalllimit\": \"email@example.com\",
        \"endpointfailure\": \"email@example.com\"
    }
           
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    path="/api/v1/endpointgroups"
    if [[ "${body}" != "" ]]; then api "POST" "${path}" --data "${body}"; else api "POST" "${path}"; fi
    ;;
  endpointgroups:create_2)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{
    \"name\": \"SIP Trunk In/Out - User/Password\",
    \"call_settings\": {
        \"limit\": 5,
        \"timeout\": 3600
    },
    \"auth\": {
        \"type\": \"userpwd\",
        \"user\": \"18889072085\",
        \"pass\": \"example\",
        \"domain\": \"pbx.example.com\"
    },
    \"strip\": 0,
    \"prefix\": \"\",
    \"notifications\": {
        \"overmaxcalllimit\": \"email@example.com\",
        \"endpointfailure\": \"email@example.com\"
    }
           
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    path="/api/v1/endpointgroups"
    if [[ "${body}" != "" ]]; then api "POST" "${path}" --data "${body}"; else api "POST" "${path}"; fi
    ;;
  endpointgroups:create_3)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{
    \"name\": \"SIP Trunk IP Auth\",
    \"call_settings\": {
        \"limit\": 5,
        \"timeout\": 3600
    },
    \"auth\": {
        \"type\": \"ip\"
    },
    \"endpoints\": [
                {
                    \"host\": \"50.192.97.226\",
                    \"port\": 5060,
                    \"signalling\": \"proxy\",
                    \"media\": \"proxy\",
                    \"description\": \"SIP Trunk Endpoint\",
                    \"rweight\": 1
                }
    ],
    \"strip\": 0,
    \"prefix\": \"\",
    \"notifications\": {
        \"overmaxcalllimit\": \"email@example.com\",
        \"endpointfailure\": \"email@example.com\"
    }
           
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    path="/api/v1/endpointgroups"
    if [[ "${body}" != "" ]]; then api "POST" "${path}" --data "${body}"; else api "POST" "${path}"; fi
    ;;
  endpointgroups:delete)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    set -- "${args[@]}"
    if [[ "$#" -lt 1 ]]; then echo "Error: expected at least 1 path parameter(s) for endpointgroups:delete" >&2; exit 2; fi
    path="/api/v1/endpointgroups/${1}"
    path="$(eval echo \"$path\")"
    api "DELETE" "${path}"
    ;;
  endpointgroups:update)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{
    \"name\": \"SIP Trunk IP Auth Update\",
    \"call_settings\": {
        \"limit\": 5,
        \"timeout\": 3600
    },
    \"auth\": {
        \"type\": \"ip\"
    },
    \"endpoints\": [
                {
                    \"host\": \"50.192.97.227\",
                    \"port\": 5060,
                    \"signalling\": \"proxy\",
                    \"media\": \"proxy\",
                    \"description\": \"SIP Trunk Endpoint\",
                    \"rweight\": 1
                }
    ],
    \"strip\": 0,
    \"prefix\": \"\",
    \"notifications\": {
        \"overmaxcalllimit\": \"email@example.com\",
        \"endpointfailure\": \"email@example.com\"
    }
           
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    set -- "${args[@]}"
    if [[ "$#" -lt 1 ]]; then echo "Error: expected at least 1 path parameter(s) for endpointgroups:update" >&2; exit 2; fi
    path="/api/v1/endpointgroups/${1}"
    path="$(eval echo \"$path\")"
    if [[ "${body}" != "" ]]; then api "PUT" "${path}" --data "${body}"; else api "PUT" "${path}"; fi
    ;;
  kamailio:reload)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    path="/api/v1/reload/kamailio"
    api "POST" "${path}"
    ;;
  kamailio:list)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    path="/api/v1/kamailio/stats"
    api "GET" "${path}"
    ;;
  inboundmapping:list)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    path="/api/v1/inboundmapping"
    api "GET" "${path}"
    ;;
  inboundmapping:create)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{ 
    \"did\": \"13132222223\",
    \"servers\": [\"#22\"],
    \"name\": \"Taste Pizzabar\"
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    path="/api/v1/inboundmapping"
    if [[ "${body}" != "" ]]; then api "POST" "${path}" --data "${body}"; else api "POST" "${path}"; fi
    ;;
  inboundmapping:update)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{ 
    \"servers\": [\"#10\"],
    \"name\": \"Flyball\"
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    path="/api/v1/inboundmapping?did=13132222223"
    if [[ "${body}" != "" ]]; then api "PUT" "${path}" --data "${body}"; else api "PUT" "${path}"; fi
    ;;
  inboundmapping:delete)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    path="/api/v1/inboundmapping?did=13132222223"
    api "DELETE" "${path}"
    ;;
  leases:list)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    path="/api/v1/lease/endpoint?email=mack@goflyball.com&ttl=5m"
    api "GET" "${path}"
    ;;
  leases:list_1)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    path="/api/v1/lease/endpoint?email=mack@goflyball.com&ttl=1m&type=ip&auth_ip=172.145.24.2"
    api "GET" "${path}"
    ;;
  leases:revoke)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    set -- "${args[@]}"
    if [[ "$#" -lt 1 ]]; then echo "Error: expected at least 1 path parameter(s) for leases:revoke" >&2; exit 2; fi
    path="/api/v1/lease/endpoint/${1}/revoke"
    path="$(eval echo \"$path\")"
    api "DELETE" "${path}"
    ;;
  carriergroups:list)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    path="/api/v1/carriergroups"
    api "GET" "${path}"
    ;;
  carriergroups:create)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{
    \"name\": \"Test1\",
    \"strip\": \"\",
    \"prefix\": \"\",
    \"auth\": {
        \"type\": \"ip\",
        \"r_username\": \"\",
        \"auth_username\": \"\",
        \"auth_password\": \"\",
        \"auth_domain\": \"\",
        \"auth_proxy\": \"\"
    },
    \"plugin\" : {
        \"name\":\"\",
        \"plugin_prefix\":\"\",
        \"account_sid\": \"\",
        \"account_token\":\"\"
    },
    \"endpoints\":[
        {
            \"name\": \"proxy.detroitpbx.com\",
            \"hostname\": \"proxy.detroitpbx.com\",
            \"strip\": \"\",
            \"prefix\": \"\"
        }
    ]
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    path="/api/v1/carriergroups"
    if [[ "${body}" != "" ]]; then api "POST" "${path}" --data "${body}"; else api "POST" "${path}"; fi
    ;;
  auth:create)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{
    \"username\": \"yahoo2\",
    \"password\": \"123456\",
    \"firstname\": \"First\",
    \"lastname\": \"DeLast\",
    \"roles\": [],
    \"domains\": []
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    path="/api/v1/auth/user"
    if [[ "${body}" != "" ]]; then api "POST" "${path}" --data "${body}"; else api "POST" "${path}"; fi
    ;;
  auth:update)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{
    \"username\": \"de_uzer\",
    \"password\": \"1234567\",
    \"firstname\": \"First\",
    \"lastname\": \"DeLast\",
    \"roles\": [],
    \"domains\": []
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    set -- "${args[@]}"
    if [[ "$#" -lt 1 ]]; then echo "Error: expected at least 1 path parameter(s) for auth:update" >&2; exit 2; fi
    path="/api/v1/auth/user/${1}"
    path="$(eval echo \"$path\")"
    if [[ "${body}" != "" ]]; then api "PUT" "${path}" --data "${body}"; else api "PUT" "${path}"; fi
    ;;
  auth:delete)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    set -- "${args[@]}"
    if [[ "$#" -lt 1 ]]; then echo "Error: expected at least 1 path parameter(s) for auth:delete" >&2; exit 2; fi
    path="/api/v1/auth/user/${1}"
    path="$(eval echo \"$path\")"
    api "DELETE" "${path}"
    ;;
  auth:list)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    path="/api/v1/auth/user"
    api "GET" "${path}"
    ;;
  auth:login)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    body=""
    if [[ $use_sample -eq 1 ]]; then
      body="{
    \"username\": \"yahoo2\",
    \"password\": \"123456\"
}"
    else
      if [[ "${#args[@]}" -gt 0 ]]; then body="${args[-1]}"; unset "args[-1]"; fi
    fi
    path="/api/v1/auth/login"
    if [[ "${body}" != "" ]]; then api "POST" "${path}" --data "${body}"; else api "POST" "${path}"; fi
    ;;
  cdr:get)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    set -- "${args[@]}"
    if [[ "$#" -lt 1 ]]; then echo "Error: expected at least 1 path parameter(s) for cdr:get" >&2; exit 2; fi
    path="/api/v1/cdrs/endpointgroups/${1}?type=csv&dtfilter=2022-09-14&email=True"
    path="$(eval echo \"$path\")"
    api "GET" "${path}"
    ;;
  cdr:get_1)
    args=("$@")
    use_sample=0
    if [[ "${#args[@]}" -gt 0 && "${args[-1]}" == "--sample" ]]; then use_sample=1; unset "args[-1]"; fi
    set -- "${args[@]}"
    if [[ "$#" -lt 1 ]]; then echo "Error: expected at least 1 path parameter(s) for cdr:get_1" >&2; exit 2; fi
    path="/api/v1/cdrs/endpoint/${1}"
    path="$(eval echo \"$path\")"
    api "GET" "${path}"
    ;;
  *) echo "Unknown command: $cmd" >&2; help; exit 2 ;;
esac
