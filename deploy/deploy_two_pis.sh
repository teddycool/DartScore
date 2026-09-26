#!/usr/bin/env bash
# Copy the current camera-free engine and presentation code to separate Pis.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: deploy/deploy_two_pis.sh --engine USER@HOST --presentation USER@HOST [--only engine|presentation] [--dry-run]

Run from any directory on the development computer. The script copies code to
~/dartscore-deploy on each Pi over SSH/rsync. It does not touch runtime data,
the existing ~/DartScore checkout, or running processes. --dry-run prints the
source manifest and destinations without contacting or modifying either Pi.
EOF
}

engine=""
presentation=""
only="both"
dry_run=false
while (($#)); do
    case "$1" in
        --engine|--presentation|--only)
            key="$1"
            if (($# < 2)); then echo "Missing value for $key" >&2; exit 2; fi
            case "$key" in
                --engine) engine="$2" ;;
                --presentation) presentation="$2" ;;
                --only) only="$2" ;;
            esac
            shift 2 ;;
        --dry-run) dry_run=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
    esac
done

if [[ "$only" != "both" && "$only" != "engine" && "$only" != "presentation" ]]; then
    echo "--only must be engine or presentation" >&2; exit 2
fi
if [[ ("$only" == "both" || "$only" == "engine") && -z "$engine" ]] ||
   [[ ("$only" == "both" || "$only" == "presentation") && -z "$presentation" ]]; then
    echo "Missing required Pi SSH destination" >&2; usage >&2; exit 2
fi
for target in "$engine" "$presentation"; do
    if [[ -n "$target" && ! "$target" =~ ^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+$ ]]; then
        echo "Expected USER@HOST (DNS name or IPv4): $target" >&2; exit 2
    fi
done

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
engine_files=(SW/__init__.py SW/DartScoreEngine/__init__.py
              SW/DartScoreEngine/Api/ SW/DartScoreEngine/Game/
              SW/DartScoreEngine/Input/ SW/serve_engine.py SW/simulate_game.py)
presentation_files=(SW/__init__.py SW/Presentation/ SW/serve_presentation.py)

deploy_one() {
    local role="$1" target="$2"
    local -a files
    if [[ "$role" == engine ]]; then files=("${engine_files[@]}")
    else files=("${presentation_files[@]}"); fi
    echo "[$role] $target:~/dartscore-deploy/"
    if [[ "$dry_run" == true ]]; then
        printf '  %s\n' "${files[@]}"
        return
    fi
    ssh -o ConnectTimeout=8 "$target" 'mkdir -p "$HOME/dartscore-deploy"'
    rsync -az --relative --itemize-changes \
        --exclude='__pycache__/' --exclude='*.pyc' \
        -e 'ssh -o ConnectTimeout=8' \
        "${files[@]}" "$target:dartscore-deploy/"
}

if [[ "$only" == "both" || "$only" == "engine" ]]; then deploy_one engine "$engine"; fi
if [[ "$only" == "both" || "$only" == "presentation" ]]; then deploy_one presentation "$presentation"; fi
if [[ "$dry_run" == false ]]; then
    echo "Code copied. Restart each selected process from ~/dartscore-deploy to use it."
fi
