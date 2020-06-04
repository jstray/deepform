#!/bin/bash
# Source this script in order to invoke wandb sweep sweep.yaml and set the var WANDB_SWEEP_ID

export SED_REGEX_EXTRACT='s/^.*Created sweep with ID: \([[:alnum:]]*\).*$/\1/p'
init=$(wandb sweep sweep.yaml 2>&1 | sed -n "$SED_REGEX_EXTRACT")

if [ -z "$init" ]
then
  exit 1
else
  echo $init
  export WANDB_SWEEP_ID="$init"
  wandb agent deepform/deepform/$WANDB_SWEEP_ID
fi
