# This file must be used with "source bin/activate.csh" *from csh*.
# Created by Davide Di Blasi <davidedb@gmail.com>
# Ported to Python 3.3 venv by Andrew Svetlov <andrew.svetlov@gmail.com>

# Define constants for better clarity
setenv VIRTUAL_ENV "/Users/abhimehrotra/Dataspell_Projects/Hydrograph_Versus_Seatek_Sensors_Project/clean_env"
setenv VIRTUAL_ENV_PROMPT "(clean_env) "

# Save paths and prompts for later restoration
set OLD_PATH="$PATH"
set OLD_PROMPT="$prompt"

# Update environment variables
setenv PATH "$VIRTUAL_ENV/bin:$PATH"

# Update the shell prompt unless disabled
if (! "$?VIRTUAL_ENV_DISABLE_PROMPT") then
    set prompt = "$VIRTUAL_ENV_PROMPT$prompt"
endif

# Define a helper alias to reset the environment
alias reset_env 'setenv PATH "$OLD_PATH"; unset OLD_PATH; set prompt="$OLD_PROMPT"; unset OLD_PROMPT; unsetenv VIRTUAL_ENV; unsetenv VIRTUAL_ENV_PROMPT'

# Alias deactivate to safely restore the original environment
alias deactivate 'test $?OLD_PATH != 0 && reset_env; rehash; test "\!:*" != "nondestructive" && unalias deactivate'

# Miscellaneous
alias pydoc python -m pydoc
rehash
