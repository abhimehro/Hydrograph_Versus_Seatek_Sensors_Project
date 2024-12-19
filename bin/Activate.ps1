# Constants for reused values
$PyVenvConfigFile = 'pyvenv.cfg'
$KeyValueSplitRegex = "\s*=\s*"

# Helper function to determine the prompt
function Get-PromptFromConfigOrDefault {
    param (
        [String] $VenvDir,
        [Hashtable] $PyVenvConfig,
        [String] $Prompt
    )
    if ($Prompt) {
        Write-Verbose "Prompt specified as argument, using '$Prompt'"
        return $Prompt
    }

    if ($PyVenvConfig -and $PyVenvConfig['prompt']) {
        Write-Verbose "Setting Prompt based on pyvenv.cfg: '$($PyVenvConfig['prompt'])'"
        return $PyVenvConfig['prompt']
    }

    # Default to the directory name
    $DefaultPrompt = Split-Path -Path $VenvDir -Leaf
    Write-Verbose "Prompt not specified, defaulting to directory name: '$DefaultPrompt'"
    return $DefaultPrompt
}

# Function to parse pyvenv.cfg
function Get-PyVenvConfig {
    param (
        [String] $ConfigDir,
        [String] $ConfigFileName = $PyVenvConfigFile
    )
    Write-Verbose "Given ConfigDir=$ConfigDir, obtaining values from $ConfigFileName"
    $ConfigPath = Join-Path -Resolve -Path $ConfigDir -ChildPath $ConfigFileName -ErrorAction Continue
    $ConfigMap = @{}

    if ($ConfigPath) {
        Write-Verbose "File exists, parsing key-value pairs"
        Get-Content -Path $ConfigPath | ForEach-Object {
            $KeyValue = $_ -split $KeyValueSplitRegex, 2
            if ($KeyValue[0] -and $KeyValue[1]) {
                $Value = $KeyValue[1].Trim("'""") # Strip quotes
                $ConfigMap[$KeyValue[0]] = $Value
                Write-Verbose "Added Key: '$($KeyValue[0])'='$Value'"
            }
        }
    }
    return $ConfigMap
}

# Main activation script
$VenvExecDir = (Get-Item -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition))
$VenvDir = $VenvDir ? $VenvDir : $VenvExecDir.Parent.FullName.TrimEnd("\\/")
Write-Verbose "Activation script located in '$($VenvExecDir.FullName)', using virtual environment at '$VenvDir'"

# Load pyvenv configuration
$PyVenvConfig = Get-PyVenvConfig -ConfigDir $VenvDir

# Determine prompt
$Prompt = Get-PromptFromConfigOrDefault -VenvDir $VenvDir -PyVenvConfig $PyVenvConfig -Prompt $Prompt
Write-Verbose "Final Prompt: '$Prompt'"

# Deactivate current environment
deactivate -nondestructive
