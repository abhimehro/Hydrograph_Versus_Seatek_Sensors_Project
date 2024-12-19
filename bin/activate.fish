# Constants
set -g VIRTUAL_ENV_NAME "(clean_env)"  # Name of the virtual environment

# Function to deactivate virtual environment
function deactivate -d "Exit virtual environment and return to normal shell environment"
    if test -n "$_OLD_VIRTUAL_PATH"
        set -gx PATH $_OLD_VIRTUAL_PATH
        set -e _OLD_VIRTUAL_PATH
    end
    if test -n "$_OLD_VIRTUAL_PYTHONHOME"
        set -gx PYTHONHOME $_OLD_VIRTUAL_PYTHONHOME
        set -e _OLD_VIRTUAL_PYTHONHOME
    end
    if test -n "$_OLD_FISH_PROMPT"
        functions -e fish_prompt
        set -e _OLD_FISH_PROMPT
        functions -c _old_fish_prompt fish_prompt
        functions -e _old_fish_prompt
    end
    set -e VIRTUAL_ENV
    set -e VIRTUAL_ENV_PROMPT
    if test "$argv[1]" != "nondestructive"
        functions -e deactivate
    end
end

# Function to setup the virtual environment prompt
function setup_virtual_prompt
    functions -c fish_prompt _old_fish_prompt
    function fish_prompt
        set -l old_status $status
        printf "%s%s%s" (set_color 4B8BBE) "$VIRTUAL_ENV_NAME " (set_color normal)
        echo "exit $old_status" | .
        _old_fish_prompt
    end
    set -gx _OLD_FISH_PROMPT "$VIRTUAL_ENV"
    set -gx VIRTUAL_ENV_PROMPT "$VIRTUAL_ENV_NAME "
end

# Initialize virtual environment
deactivate nondestructive
set -gx VIRTUAL_ENV "/Users/abhimehrotra/Dataspell_Projects/Hydrograph_Versus_Seatek_Sensors_Project/clean_env"
set -gx _OLD_VIRTUAL_PATH $PATH
set -gx PATH "$VIRTUAL_ENV/bin" $PATH

if set -q PYTHONHOME
    set -gx _OLD_VIRTUAL_PYTHONHOME $PYTHONHOME
    set -e PYTHONHOME
end

if test -z "$VIRTUAL_ENV_DISABLE_PROMPT"
    setup_virtual_prompt
end
