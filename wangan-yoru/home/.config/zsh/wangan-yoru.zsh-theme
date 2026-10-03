# ~/.config/zsh/wangan-yoru.zsh-theme
# Wangan yoru prompt: agnoster's segment chain, standalone (no oh-my-zsh). The
# joins are pills, not the powerline arrow: the chain opens with the left half
# circle (U+E0B6) and every segment ends in the right half circle (U+E0B4),
# drawn in the segment's colour over the next one, so each segment is a capsule
# that overlaps the one after it. Then the prompt character, a small amber ›.
#   status  redline red, only on failure / root / background jobs
#   context raised + amber text, only over SSH or as another user
#   dir     bayside blue + white
#   git     raised pill when clean, amber pill with ± when dirty
# The half circles are Nerd Font glyphs (JetBrains Mono Nerd Font sits behind
# M PLUS 1 Code in fontconfig). They are written as $'\u....' escapes, so this
# file is plain ASCII apart from its comments.
# Hex colours need zsh 5.7+ and a true-colour terminal.

setopt prompt_subst

WANGAN_DEFAULT_USER=${WANGAN_DEFAULT_USER:-$USER}   # hide context on your own box

W_SEL='#1A2029'  W_BLUE='#2A5FC4'  W_ONBLUE='#EEF1F5' W_AMBER='#F2A33A' W_ONAMBER='#0B0D11'
W_TEXT='#EEF1F5' W_RED='#D41F27'   W_ONRED='#FFFFFF'   W_AMBER_T='#F2A33A' W_DIM='#5F6A7C'

WANGAN_HEAD=$'\ue0b6'   # left half circle: opens the first pill
WANGAN_SEP=$'\ue0b4'    # right half circle: closes a pill over the next one
typeset -g WANGAN_BG=NONE

wangan_segment() {
  local bg="%K{$1}" fg="%F{$2}"
  if [[ $WANGAN_BG == NONE ]]; then
    print -n "%{%k%F{$1}%}$WANGAN_HEAD%{$bg$fg%}"
  elif [[ $1 != $WANGAN_BG ]]; then
    print -n "%{$bg%F{$WANGAN_BG}%}$WANGAN_SEP%{$fg%} "
  else
    print -n "%{$bg%}%{$fg%} "
  fi
  WANGAN_BG=$1
  [[ -n $3 ]] && print -n -- "$3"
}

wangan_end() {
  if [[ $WANGAN_BG != NONE ]]; then
    print -n "%{%k%F{$WANGAN_BG}%}$WANGAN_SEP"
  else
    print -n "%{%k%}"
  fi
  print -n "%{%f%}"
  WANGAN_BG=NONE
}

# ~/dotfiles/hypr -> ~/d/hypr
wangan_short_pwd() {
  local p=${(%):-%~}
  local -a parts=("${(@s:/:)p}")
  local i
  for (( i = 1; i < ${#parts}; i++ )); do
    [[ -z ${parts[i]} || ${parts[i]} == '~' ]] && continue
    if [[ ${parts[i]} == .* ]]; then
      parts[i]=${parts[i][1,2]}
    else
      parts[i]=${parts[i][1]}
    fi
  done
  print -rn -- "${(j:/:)parts//\%/%%}"
}

wangan_status() {
  local -a s
  (( WANGAN_RETVAL != 0 )) && s+=$'\u2718'" $WANGAN_RETVAL"
  (( UID == 0 )) && s+=$'\u26a1'
  [[ -n ${jobstates} ]] && s+=$'\u2699'
  (( ${#s} )) && wangan_segment $W_RED $W_ONRED "${(j: :)s}"
}

wangan_context() {
  [[ $USER != $WANGAN_DEFAULT_USER || -n $SSH_CONNECTION ]] &&
    wangan_segment $W_SEL $W_AMBER_T '%n@%m'
}

wangan_dir() {
  wangan_segment $W_BLUE $W_ONBLUE "$(wangan_short_pwd)"
}

wangan_git() {
  command git rev-parse --is-inside-work-tree &>/dev/null || return
  local ref
  ref=$(command git symbolic-ref --short HEAD 2>/dev/null) ||
    ref=$'\u27a6'" $(command git rev-parse --short HEAD 2>/dev/null)"
  ref=${ref//\%/%%}
  if [[ -n $(command git status --porcelain --ignore-submodules=dirty 2>/dev/null | head -n1) ]]; then
    wangan_segment $W_AMBER $W_ONAMBER "$ref "$'\u00b1'
  else
    wangan_segment $W_SEL $W_TEXT "$ref"
  fi
}

wangan_build_prompt() {
  wangan_status
  wangan_context
  wangan_dir
  wangan_git
  wangan_end
}

wangan_precmd() { WANGAN_RETVAL=$? }
autoload -Uz add-zsh-hook
add-zsh-hook precmd wangan_precmd

PROMPT='%{%f%b%k%}$(wangan_build_prompt) %F{'$W_AMBER_T$'}\u203a%f '
RPROMPT="%F{$W_DIM}%*%f"

# ---- completion ------------------------------------------------------
autoload -Uz compinit && compinit
zstyle ':completion:*' menu select
zstyle ':completion:*' list-colors 'ma=48;2;42;95;196;38;2;238;241;245'

# ---- plugins ---------------------------------------------------------
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=$W_DIM"
[[ -r /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh ]] &&
  source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

# zsh-syntax-highlighting must be sourced last, then styled.
if [[ -r /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]]; then
  source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
  ZSH_HIGHLIGHT_STYLES[command]='fg=#EEF1F5'
  ZSH_HIGHLIGHT_STYLES[builtin]='fg=#EEF1F5'
  ZSH_HIGHLIGHT_STYLES[alias]='fg=#EEF1F5'
  ZSH_HIGHLIGHT_STYLES[function]='fg=#EEF1F5'
  ZSH_HIGHLIGHT_STYLES[precommand]='fg=#EEF1F5,underline'
  ZSH_HIGHLIGHT_STYLES[path]='fg=#EEF1F5'
  ZSH_HIGHLIGHT_STYLES[single-hyphen-option]='fg=#5B8DEF'
  ZSH_HIGHLIGHT_STYLES[double-hyphen-option]='fg=#5B8DEF'
  ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#F2A33A'
  ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#F2A33A'
  ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#FF5A5E,underline'
fi

export FZF_DEFAULT_OPTS="--color=bg+:#1A2029,fg:#8C97A8,fg+:#EEF1F5,hl:#5B8DEF,hl+:#F2A33A,pointer:#F2A33A,prompt:#F2A33A,info:#8C97A8,border:#5B8DEF --pointer='●' --border=rounded"
